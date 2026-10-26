"""Reproducible Stage 2 hypothesis test; independent environment and agent.

Predictions are evaluated against held-out, newly generated observations.
No evaluation feedback updates the learner. Include a non-linear negative test.
"""
from __future__ import annotations

import copy
import json
import random
import statistics
import time
import tracemalloc

from .model import choose_action, experience, new_entity, predict
from .world import RelationalWorld


def evaluate(entity: dict, world: RelationalWorld, observations: list[dict]) -> float:
    before = json.dumps(entity, sort_keys=True, allow_nan=False)
    right = 0
    for i, obs in enumerate(observations):
        action = -1 if i % 2 == 0 else 1
        right += int(predict(entity, obs, action)["prediction"] == world.step(obs, action))
    if json.dumps(entity, sort_keys=True, allow_nan=False) != before:
        raise AssertionError("Evaluation contaminated the learned state")
    return right / len(observations)


def _observations(world: RelationalWorld, seed: int, count: int) -> list[dict]:
    rng = random.Random(seed)
    return [world.observation(rng) for _ in range(count)]


def one_run(seed: int, training: int = 400, testing: int = 240) -> tuple[dict, dict]:
    if training < 50 or testing < 50:
        raise ValueError("Require at least 50 training and 50 holdout examples")
    world = RelationalWorld(seed)
    train_obs = _observations(world, seed * 4099 + 31, training)
    test_obs = _observations(world, seed * 4099 + 97, testing)
    train_keys = {(v["signal"], v["pressure"]) for v in train_obs}
    test_keys = {(v["signal"], v["pressure"]) for v in test_obs}
    assert train_keys.isdisjoint(test_keys), "Train/test observation leakage"

    agent = new_entity(identity=f"experiment-seed-{seed}")
    control = copy.deepcopy(agent)
    initial_accuracy = evaluate(agent, world, test_obs)
    correct_by_quartile = [0, 0, 0, 0]
    count_by_quartile = [0, 0, 0, 0]
    outcomes = []
    training_cpu_ns = 0
    prediction_cpu_ns = 0
    tracemalloc.start()
    try:
        for i, obs in enumerate(train_obs):
            action = choose_action(agent, obs, explore=True)
            outcome = world.step(obs, action)
            outcomes.append(outcome)
            t0 = time.perf_counter_ns()
            pred = predict(agent, obs, action)
            prediction_cpu_ns += time.perf_counter_ns() - t0
            quarter = min(3, i * 4 // training)
            correct_by_quartile[quarter] += int(pred["prediction"] == outcome)
            count_by_quartile[quarter] += 1
            t1 = time.perf_counter_ns()
            experience(agent, obs, action, outcome, learn=True)
            training_cpu_ns += time.perf_counter_ns() - t1
            experience(control, obs, action, outcome, learn=False)
        peak_tracemalloc = tracemalloc.get_traced_memory()[1]
    finally:
        tracemalloc.stop()

    actual = evaluate(agent, world, test_obs)
    serial_bytes_after_first_task = len(json.dumps(agent, sort_keys=True).encode("utf-8"))
    first_task_weights = {k: round(v, 5) for k, v in agent["model"]["weights"].items()}
    frozen = evaluate(control, world, test_obs)
    majority = int(sum(outcomes) * 2 >= len(outcomes))
    majority_accuracy = sum(int(world.step(v, -1 if i % 2 == 0 else 1) == majority)
                            for i, v in enumerate(test_obs)) / testing

    negative = RelationalWorld(seed, mode="parity")
    neg_agent = new_entity(identity=f"negative-seed-{seed}")
    for obs in train_obs:
        action = choose_action(neg_agent, obs, explore=True)
        experience(neg_agent, obs, action, negative.step(obs, action))
    negative_accuracy = evaluate(neg_agent, negative, test_obs)

    learned_entity = copy.deepcopy(agent)  # Preserve the proven first-task policy.
    adaptation_entity = copy.deepcopy(agent)  # Isolated branch; negative transfer cannot corrupt it.
    switched = RelationalWorld(seed, inverted=True)
    post_switch_before = evaluate(adaptation_entity, switched, test_obs)
    adaptation_obs = _observations(switched, seed * 4099 + 211, training)
    for obs in adaptation_obs:
        action = choose_action(adaptation_entity, obs, explore=True)
        experience(adaptation_entity, obs, action, switched.step(obs, action))
    adaptation_after = evaluate(adaptation_entity, switched, test_obs)
    original_after_switch = evaluate(adaptation_entity, world, test_obs)
    metrics = {
        "seed": seed,
        "training_experiences": training,
        "holdout_cases": testing,
        "identical_train_test_inputs": 0,
        "accuracy_before_learning": initial_accuracy,
        "accuracy_frozen_no_learning": frozen,
        "accuracy_train_majority_baseline": majority_accuracy,
        "accuracy_after_learning": actual,
        "prequential_train_accuracy_by_quarter": [correct_by_quartile[i] / count_by_quartile[i]
                                                 for i in range(4)],
        "negative_parity_accuracy": negative_accuracy,
        "new_regime_before_adaptation": post_switch_before,
        "new_regime_after_adaptation": adaptation_after,
        "old_regime_after_adaptation_retention": original_after_switch,
        "learning_microseconds_per_experience": training_cpu_ns / (training * 1000),
        "predict_microseconds_per_case": prediction_cpu_ns / (training * 1000),
        "python_tracemalloc_peak_bytes": peak_tracemalloc,
        "serialized_state_bytes_before_switch": serial_bytes_after_first_task,
        "hypothesis_weights_after_first_task": first_task_weights,
    }
    # Return evolved entity for optional persistence; the report is not state authority.
    return metrics, learned_entity


def campaign(seed: int = 42, runs: int = 5, training: int = 400,
             testing: int = 240) -> tuple[dict, dict]:
    if runs < 1 or runs > 100:
        raise ValueError("runs must be 1..100")
    t0 = time.perf_counter()
    per_run, agent_last = [], None
    for offset in range(runs):
        row, agent_last = one_run(seed + offset, training, testing)
        per_run.append(row)
    numeric = ("accuracy_before_learning", "accuracy_frozen_no_learning",
               "accuracy_train_majority_baseline", "accuracy_after_learning",
               "negative_parity_accuracy", "new_regime_before_adaptation",
               "new_regime_after_adaptation", "old_regime_after_adaptation_retention",
               "learning_microseconds_per_experience", "predict_microseconds_per_case",
               "python_tracemalloc_peak_bytes")
    report = {
        "experiment": "BBYQ-E001",
        "algorithm": "online relation-weight logistic gradient, no pretraining",
        "world": "seeded hidden relational threshold; separate parity negative control",
        "environment_seed_start": seed,
        "runs": runs,
        "training_per_run": training,
        "holdout_per_run": testing,
        "summary_mean": {key: statistics.mean(row[key] for row in per_run) for key in numeric},
        "per_run": per_run,
        "wall_seconds": round(time.perf_counter() - t0, 4),
        "native_backend_used_for_campaign": False,
        "interpretation": "Small learnability experiment, not proof of general intelligence",
    }
    return report, agent_last
