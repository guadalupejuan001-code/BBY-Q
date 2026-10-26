"""E002: unlabelled regime switches, context recovery, and comparable controls."""
from __future__ import annotations

import copy
import json
import random
import statistics
import time

from .context import context_inspect, contextual_experience
from .experiment import evaluate
from .model import choose_action, experience, new_entity
from .world import RelationalWorld


def _sample(world, seed, n):
    rng = random.Random(seed)
    return [world.observation(rng) for _ in range(n)]


def _train(entity, world, obs, contextual):
    transitions = []
    before = entity['steps']
    for item in obs:
        action = choose_action(entity, item, explore=True)
        result = world.step(item, action)
        if contextual:
            trace = contextual_experience(entity, item, action, result)
            if trace['context_transition']:
                transitions.append({'at': entity['steps'],
                                    'type': trace['context_transition'],
                                    'active': trace['context_active']})
        else:
            experience(entity, item, action, result)
    assert entity['steps'] - before == len(obs)
    return transitions


def one_context_run(seed=42, training=400, testing=240, recovery=36):
    if training < 80 or testing < 50 or recovery < 8:
        raise ValueError('Insufficient training, testing or recovery budget')
    a = RelationalWorld(seed)
    b = RelationalWorld(seed, inverted=True)
    first = _sample(a, seed * 6007 + 71, training)
    alternate = _sample(b, seed * 6007 + 73, training)
    comeback = _sample(a, seed * 6007 + 79, recovery)
    test = _sample(a, seed * 6007 + 83, testing)
    groups = [{(x['signal'], x['pressure']) for x in group}
              for group in (first, alternate, comeback, test)]
    if any(groups[i] & groups[j] for i in range(4) for j in range(i+1, 4)):
        raise AssertionError('Evaluation leakage')
    subject = new_entity(identity=f'context-{seed}')
    baseline = copy.deepcopy(subject)
    _train(subject, a, first, True)
    _train(baseline, a, first, False)
    initial_a = evaluate(subject, a, test)
    switched = _train(subject, b, alternate, True)
    _train(baseline, b, alternate, False)
    adapted_b = evaluate(subject, b, test)
    old_before_return = evaluate(subject, a, test)
    old_baseline_before_return = evaluate(baseline, a, test)
    returned = _train(subject, a, comeback, True)
    _train(baseline, a, comeback, False)
    recovered_a = evaluate(subject, a, test)
    baseline_a = evaluate(baseline, a, test)
    ctx = context_inspect(subject)
    return {
        'seed': seed, 'first_training': training, 'alternate_training': training,
        'return_experiences': recovery, 'holdout_size': testing,
        'first_regime_accuracy': initial_a,
        'inverted_regime_accuracy': adapted_b,
        'original_before_revisit': old_before_return,
        'baseline_original_before_revisit': old_baseline_before_return,
        'recovered_original_accuracy': recovered_a,
        'single_model_recovered_original_accuracy': baseline_a,
        'context_switches': ctx['context_switches'],
        'context_count': ctx['total_contexts'],
        'switch_events': switched + returned,
        'active_context_after_return': ctx['active_context'],
        'total_steps': subject['steps'],
        'serialized_state_bytes': len(json.dumps(subject, separators=(',', ':'),
                                                 sort_keys=True).encode('utf-8')),
    }, subject


def context_campaign(seed=42, runs=5, training=400, testing=240, recovery=36):
    if not 1 <= runs <= 100:
        raise ValueError('runs must be 1..100')
    start = time.perf_counter()
    rows, last = [], None
    for idx in range(runs):
        row, last = one_context_run(seed + idx, training, testing, recovery)
        rows.append(row)
    keys = ('first_regime_accuracy', 'inverted_regime_accuracy',
            'original_before_revisit', 'baseline_original_before_revisit',
            'recovered_original_accuracy', 'single_model_recovered_original_accuracy',
            'context_switches', 'context_count', 'serialized_state_bytes')
    return {
        'experiment': 'BBYQ-E002',
        'algorithm': 'error-evidence context recall over rule-first state, no regime labels',
        'runs': runs, 'training': training, 'testing': testing,
        'recovery': recovery, 'seed': seed,
        'summary_mean': {key: statistics.mean(row[key] for row in rows) for key in keys},
        'per_run': rows,
        'wall_seconds': round(time.perf_counter() - start, 4),
        'native_backend_used_for_campaign': False,
    }, last
