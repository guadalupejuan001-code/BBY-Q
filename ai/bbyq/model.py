"""BBY Q's first learnable representation: an inspectable relation/weight graph.

No weights, labels, model, or tokenizer are imported from another AI. This is
an experimental online logistic rule, not a claim of general intelligence.
"""
from __future__ import annotations

import math
import uuid
from datetime import datetime, timezone

SCHEMA = "bbyq-state-v1"
FEATURES = ("bias", "signal", "pressure", "action", "signal_x_action")
LEARNING_RATE = 0.24
MAX_RECENT = 32


def new_entity(identity: str | None = None) -> dict:
    return {
        "schema": SCHEMA,
        "id": identity or str(uuid.uuid4()),
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "steps": 0,
        "model": {"weights": {key: 0.0 for key in FEATURES}, "updates": 0,
                  "active_context": 0, "next_context": 1, "active_updates": 0,
                  "archived": [], "switches": 0, "surprise_streak": 0},
        "recent": [],
    }


def validate_entity(entity: dict) -> None:
    if not isinstance(entity, dict) or entity.get("schema") != SCHEMA:
        raise ValueError("Unsupported BBY Q state schema")
    if not isinstance(entity.get("id"), str) or not entity["id"]:
        raise ValueError("Missing entity identity")
    if type(entity.get("steps")) is not int or entity["steps"] < 0:
        raise ValueError("Invalid step count")
    model = entity.get("model")
    if not isinstance(model, dict) or type(model.get("updates")) is not int:
        raise ValueError("Invalid learning model")
    weights = model.get("weights")
    if not isinstance(weights, dict) or set(weights) != set(FEATURES):
        raise ValueError("Invalid hypothesis coordinates")
    if any(not isinstance(value, (int, float)) or not math.isfinite(value)
           for value in weights.values()):
        raise ValueError("Non-finite hypothesis")
    if 'archived' in model:
        archived = model['archived']
        if type(archived) is not list or len(archived) > 3:
            raise ValueError('Invalid archived context budget')
        for name in ('active_context', 'next_context', 'active_updates',
                     'switches', 'surprise_streak'):
            if type(model.get(name)) is not int or model[name] < 0:
                raise ValueError(f'Invalid context metadata: {name}')
        if model['next_context'] <= model['active_context']:
            raise ValueError('Invalid context id sequence')
        if model['active_updates'] > model['updates']:
            raise ValueError('Context updates exceed entity updates')
        ids = {model['active_context']}
        for entry in archived:
            if (type(entry) is not dict or type(entry.get('id')) is not int or
                    entry['id'] < 0 or entry['id'] >= model['next_context'] or
                    entry['id'] in ids or type(entry.get('updates')) is not int or
                    not 0 <= entry['updates'] <= model['updates']):
                raise ValueError('Invalid archived context')
            archived_weights = entry.get('weights')
            if (type(archived_weights) is not dict or
                    set(archived_weights) != set(FEATURES) or
                    any(type(value) not in (float, int) or not math.isfinite(value)
                        for value in archived_weights.values())):
                raise ValueError('Invalid archived context weights')
            ids.add(entry['id'])
    if not isinstance(entity.get("recent"), list) or len(entity["recent"]) > MAX_RECENT:
        raise ValueError("Invalid experience history")


def features(observation: dict, action: int) -> dict[str, float]:
    if type(action) is not int or action not in (-1, 1):
        raise ValueError("Action must be -1 or 1")
    if not isinstance(observation, dict) or set(observation) != {"signal", "pressure"}:
        raise ValueError("Observation requires signal and pressure")
    signal, pressure = observation["signal"], observation["pressure"]
    if any(not isinstance(x, (int, float)) or not math.isfinite(x) or abs(x) > 1.0
           for x in (signal, pressure)):
        raise ValueError("Sensors must be finite values between -1 and 1")
    return {"bias": 1.0, "signal": float(signal), "pressure": float(pressure),
            "action": float(action), "signal_x_action": float(signal * action)}


def predict(entity: dict, observation: dict, action: int) -> dict:
    feat = features(observation, action)
    weights = entity["model"]["weights"]
    relations = {name: weights[name] * value for name, value in feat.items()}
    score = sum(relations.values())
    # Numerically stable sigmoid for large scores.
    probability = (1.0 / (1.0 + math.exp(-score))) if score >= 0 else (
        math.exp(score) / (1.0 + math.exp(score)))
    return {"prediction": int(probability >= 0.5),
            "probability_one": probability, "score": score,
            "relations": relations}


def choose_action(entity: dict, observation: dict, explore: bool = False) -> int:
    """Policy is explicit. Exploration covers both actions; exploitation predicts reward."""
    if explore:
        return -1 if entity["steps"] % 2 == 0 else 1
    return max((-1, 1), key=lambda action: predict(entity, observation, action)["probability_one"])


def experience(entity: dict, observation: dict, action: int,
               outcome: int, learn: bool = True) -> dict:
    """Observe a consequence, keep a trace, and modify relational hypotheses."""
    if type(outcome) is not int or outcome not in (0, 1):
        raise ValueError("Outcome must be binary 0 or 1")
    validate_entity(entity)
    before = predict(entity, observation, action)
    feat = features(observation, action)
    error = outcome - before["probability_one"]
    changes = {}
    if learn:
        for key in FEATURES:
            changes[key] = LEARNING_RATE * error * feat[key]
            entity["model"]["weights"][key] += changes[key]
        entity["model"]["updates"] += 1
        if 'active_updates' in entity['model']:
            entity['model']['active_updates'] += 1
    entity["steps"] += 1
    record = {"step": entity["steps"], "input": dict(observation), "action": action,
              "prediction_before_feedback": before["prediction"],
              "probability_before_feedback": round(before["probability_one"], 8),
              "outcome": outcome, "error": round(error, 8),
              "weight_delta": {key: round(value, 8) for key, value in changes.items()}}
    entity["recent"].append(record)
    entity["recent"] = entity["recent"][-MAX_RECENT:]
    return record
