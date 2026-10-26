"""BBY Q E003: blind holdout, native spatial state updates, no Python AI engine."""
from __future__ import annotations

import json
import os
from pathlib import Path
import random
import statistics
import subprocess
import tempfile
import time

from bbyq.world import RelationalWorld

BINARY = os.environ.get('BBYQ_SPATIAL_BINARY')

def run(*args, payload=None):
    proc = subprocess.run([BINARY, *map(str, args)], input=payload,
                          text=True, capture_output=True, check=True, timeout=60)
    return proc.stdout

def one(seed, train, test, negative=False):
    world = RelationalWorld(seed, mode='parity' if negative else 'linear')
    rng_training = random.Random(seed * 4099 + 31)
    rng_holdout = random.Random(seed * 4099 + 97)
    inputs = [world.observation(rng_training) for _ in range(train)]
    holdout = [world.observation(rng_holdout) for _ in range(test)]
    assert {(x['signal'], x['pressure']) for x in inputs}.isdisjoint(
        {(x['signal'], x['pressure']) for x in holdout})
    with tempfile.TemporaryDirectory() as directory:
        state = Path(directory) / 'entity.rvp'
        run('new', state)
        actions = [-1 if i % 2 == 0 else 1 for i in range(train)]
        lines = [f'L {x["signal"]:.17g} {x["pressure"]:.17g} {a} {world.step(x,a)}'
                 for x, a in zip(inputs, actions)]
        start = time.perf_counter()
        online = [json.loads(x) for x in
                  run('session', state, payload='\n'.join(lines) + '\n').splitlines()]
        elapsed = time.perf_counter() - start
        correct_online = sum(t['prediction_before_feedback'] == t['outcome']
                             for t in online)
        before = state.read_bytes()
        test_actions = [-1 if i % 2 == 0 else 1 for i in range(test)]
        queries = [f'P {x["signal"]:.17g} {x["pressure"]:.17g} {a}'
                   for x, a in zip(holdout, test_actions)]
        predicted = [json.loads(x)['prediction'] for x in
                     run('session', state, payload='\n'.join(queries) + '\n').splitlines()]
        assert before == state.read_bytes(), 'holdout modified the learned state'
        answers = [world.step(x, a) for x, a in zip(holdout, test_actions)]
        learned = sum(v == y for v, y in zip(predicted, answers)) / test
        frozen = sum(1 == y for y in answers) / test  # all-zero state
        info = json.loads(run('inspect', state))
        assert info['steps'] == train and info['active_qubits'] == 0
        return {
            'seed': seed, 'negative_control': negative,
            'holdout_accuracy': learned, 'frozen_accuracy': frozen,
            'online_accuracy': correct_online / train,
            'train_seconds_including_native_commit': elapsed,
            'rvpc2_bytes': len(before),
            'logical_overrides': info['logical_overrides'],
            'active_qubits': info['active_qubits'],
            'quantum_bindings': info['quantum_bindings'],
            'relation_weights': info['relations'],
        }

def campaign(seed=42, runs=5, train=400, test=240):
    if not BINARY or not Path(BINARY).is_file():
        raise RuntimeError('BBYQ_SPATIAL_BINARY must be the compiled Ether learner')
    rows = [one(seed + i, train, test) for i in range(runs)]
    negative = [one(seed + i, train, test, negative=True) for i in range(runs)]
    report = {
        'experiment': 'BBYQ-E003',
        'source_of_learned_state': 'XI/InverseEtherMemory',
        'native_learner': True, 'train_per_run': train,
        'test_per_run': test, 'runs': runs,
        'observations_train_holdout_disjoint': True,
        'summary': {
            'learned_mean_accuracy': statistics.mean(x['holdout_accuracy'] for x in rows),
            'frozen_mean_accuracy': statistics.mean(x['frozen_accuracy'] for x in rows),
            'negative_parity_mean_accuracy': statistics.mean(x['holdout_accuracy'] for x in negative),
            'median_rvpc2_bytes': statistics.median(x['rvpc2_bytes'] for x in rows),
            'median_native_train_seconds': statistics.median(
                x['train_seconds_including_native_commit'] for x in rows),
        }, 'per_run': rows, 'negative_runs': negative,
    }
    if report['summary']['learned_mean_accuracy'] <= report['summary']['frozen_mean_accuracy']:
        raise AssertionError('E003 failed to improve over its no-learning baseline')
    return report

if __name__ == '__main__':
    result = campaign()
    path = os.environ.get('BBYQ_SPATIAL_EVIDENCE', 'spatial-campaign.json')
    Path(path).write_text(json.dumps(result, indent=2, sort_keys=True) + '\n')
    print(json.dumps(result['summary'], indent=2))
