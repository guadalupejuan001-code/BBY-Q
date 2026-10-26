"""BBY Q E002: conditional state recall by evidence from real experiences.

Not a pretrained ensemble and not an oracle regime label. The active hypothesis
is stored once; inactive states are archived rule/delta components in the same
entity snapshot (REVERSE-PC InverseMemory owns the persistent copy).

The method compares predictive log-loss over recent observed consequences,
and only transitions when another archived/cold candidate explains those events
substantially better. It does not copy a hidden world regime identifier.
"""
from __future__ import annotations

import math

from .model import FEATURES, experience, features, predict, validate_entity

WINDOW = 6
MIN_EVIDENCE = 3  # consecutive high-confidence contradictions
SURPRISE_MAX_SUPPORT = 0.18
ARCHIVE_MAX_LOSS = 0.6
MIN_GAIN_NATS = 0.5
MIN_MATURE_UPDATES = 60
MAX_ARCHIVED = 3  # 4 contexts incl. active, bounded; never silently evict expertise.
ZERO = {key: 0.0 for key in FEATURES}


def _support(weights: dict, observation: dict, action: int, outcome: int) -> float:
    f = features(observation, action)
    score = sum(weights[k] * f[k] for k in FEATURES)
    # log P(observation | weights) stable even when score is large.
    value = score if outcome == 1 else -score
    if value >= 0:
        return -math.log1p(math.exp(-value))
    return value - math.log1p(math.exp(value))


def _mean_loss(weights: dict, recent: list[dict]) -> float:
    return -sum(_support(weights, item['input'], item['action'], item['outcome'])
                for item in recent) / len(recent)


def _init(model: dict) -> None:
    """Upgrade legacy in memory on first contextual experience; no replica."""
    model.setdefault('active_context', 0)
    model.setdefault('next_context', 1)
    model.setdefault('active_updates', model['updates'])
    model.setdefault('archived', [])
    model.setdefault('switches', 0)
    model.setdefault('surprise_streak', 0)


def contextual_experience(entity: dict, observation: dict, action: int,
                          outcome: int, learn: bool = True) -> dict:
    """Infer context from feedback; switch atomically before learning from it.

    The consequence is never visible at prediction time. The returned
    pre-feedback prediction is from the original active context (same as
    the inference the agent would have made before the world responded).
    """
    validate_entity(entity)
    before = predict(entity, observation, action)
    if type(outcome) is not int or outcome not in (0, 1):
        raise ValueError('Outcome must be binary')
    if not learn:
        record = experience(entity, observation, action, outcome, learn=False)
        record['context_prior'] = entity['model'].get('active_context', 0)
        record['context_active'] = record['context_prior']
        record['context_transition'] = None
        record['update_suspended'] = False
        return record
    model = entity['model']
    _init(model)
    prior_id = model['active_context']
    switch = None
    # Evidence is a *consecutive surprise run* rather than a moving average
    # of normal + inverted regimes. This avoids mistaking old-regime evidence
    # for evidence against an archived candidate after a change point.
    previous_surprises = model.get('surprise_streak', 0)
    surprising = (math.exp(_support(model['weights'], observation,
                                    action, outcome)) < SURPRISE_MAX_SUPPORT)
    model['surprise_streak'] = min(WINDOW, previous_surprises + 1) if surprising else 0
    if (learn and model['surprise_streak'] >= MIN_EVIDENCE and
            model['active_updates'] >= MIN_MATURE_UPDATES):
        window = entity['recent'][-(MIN_EVIDENCE - 1):] + [
            {'input': dict(observation), 'action': action, 'outcome': outcome}]
        active_loss = _mean_loss(model['weights'], window)
        best = None
        best_loss = math.log(2)   # fresh empty context is an explicit baseline
        for candidate in model['archived']:
            loss = _mean_loss(candidate['weights'], window)
            if loss < ARCHIVE_MAX_LOSS and loss < best_loss:
                best, best_loss = candidate, loss
        chosen = best if best is not None else 'new'
        if chosen != 'new' or len(model['archived']) < MAX_ARCHIVED:
            if active_loss > best_loss + MIN_GAIN_NATS:
                old = {'id': model['active_context'],
                       'weights': model['weights'],
                       'updates': model['active_updates']}
                if chosen == 'new':
                    model['active_context'] = model['next_context']
                    model['next_context'] += 1
                    model['weights'] = dict(ZERO)
                    model['active_updates'] = 0
                    switch = 'created'
                else:
                    model['archived'].remove(chosen)
                    model['active_context'] = chosen['id']
                    model['weights'] = chosen['weights']
                    model['active_updates'] = chosen['updates']
                    switch = 'recalled'
                model['archived'].append(old)
                model['switches'] += 1
                model['surprise_streak'] = 0

    # Protect a mature hypothesis from systematic contradictory feedback.
    # Contradictions remain recorded as evidence for another state; they are
    # not lost just because this update is suspended.
    support = math.exp(_support(model['weights'], observation, action, outcome))
    apply_update = (learn and not (
        model['active_updates'] >= MIN_MATURE_UPDATES and support < 0.2))
    trace = experience(entity, observation, action, outcome, learn=apply_update)
    # The learned context is allowed to change AFTER the feedback. Preserve
    # the actual prediction made before feedback; otherwise the trace leaks
    # the correct answer through the newly recalled context.
    trace['learning_probability_after_selection'] = trace['probability_before_feedback']
    trace['learning_error_after_selection'] = trace['error']
    trace['prediction_before_feedback'] = before['prediction']
    trace['probability_before_feedback'] = round(before['probability_one'], 8)
    trace['error'] = round(outcome - before['probability_one'], 8)
    trace['context_prior'] = prior_id
    trace['context_active'] = model['active_context']
    trace['context_transition'] = switch
    trace['update_suspended'] = learn and not apply_update
    return trace


def context_inspect(entity: dict) -> dict:
    validate_entity(entity)
    model = entity['model']
    return {
        'active_context': model.get('active_context', 0),
        'archived_contexts': [
            {'id': x['id'], 'updates': x['updates'], 'weights': x['weights']}
            for x in model.get('archived', [])],
        'context_switches': model.get('switches', 0),
        'total_contexts': 1 + len(model.get('archived', [])),
        'max_contexts': MAX_ARCHIVED + 1,
        'bound_reached': len(model.get('archived', [])) >= MAX_ARCHIVED,
    }
