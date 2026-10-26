"""Paired A/B experiment: BQL2 versus uncompressed JSON in identical XI runtime.

No external database or AI; both conditions use the same REVERSE-PC executable,
Inverse Ether Memory, initial entity and interactions. Trials are interleaved.
"""
from __future__ import annotations

import copy
import json
import os
from pathlib import Path
import platform
import statistics
import tempfile
import time

from bbyq.model import experience, new_entity, validate_entity
from bbyq.store import MAX_PAYLOAD, NativeStore


class RawSnapshotStore(NativeStore):
    @staticmethod
    def _encode(entity: dict) -> bytes:
        validate_entity(entity)
        payload = json.dumps(entity, separators=(',', ':'), sort_keys=True,
                             allow_nan=False, ensure_ascii=True).encode('utf-8')
        if len(payload) > MAX_PAYLOAD:
            raise ValueError('Raw control exceeds the experimental budget')
        return len(payload).to_bytes(4, 'little') + payload


def trial(path: Path, initial: dict, condition: str) -> tuple[dict, dict]:
    store = NativeStore(path) if condition == 'bql2' else RawSnapshotStore(path)
    store.initialize(copy.deepcopy(initial))
    # Normalize trial start: both codecs have already stored the same initial
    # entity in their respective physical representation before timing begins.
    store.transact(lambda entity: None)
    samples = []
    for i in range(24):
        observation = {'signal': ((i*7 % 21)-10)/10,
                       'pressure': ((i*11 % 21)-10)/10}
        start = time.perf_counter_ns()
        store.transact(lambda entity: experience(
            entity, observation, -1 if i%2==0 else 1, int(i%3 == 0)))
        samples.append((time.perf_counter_ns()-start)/1e6)
    final = store.read()
    stats = store.stats()
    types = {entry['type']: entry for entry in stats['native']}
    if types['stats']['active_qubits'] or types['memory_stats']['quantum_bindings']:
        raise AssertionError('Unexpected simulated quantum allocation')
    return {
        'condition': condition,
        'median_ms': statistics.median(samples),
        'p95_nearest_rank_ms': sorted(samples)[22],
        'samples_ms': samples,
        'rvpc2_bytes': stats['rvpc2_bytes'],
        'logical_overrides': types['memory_stats']['overrides'],
        'active_qubits': types['stats']['active_qubits'],
    }, final


def main() -> None:
    initial = new_entity('paired-codec-identical-entity')
    data = []
    with tempfile.TemporaryDirectory(prefix='bbyq-codec-AB-') as root:
        for cycle in range(7):
            conditions = ['json', 'bql2'] if cycle%2==0 else ['bql2', 'json']
            expected = None
            for condition in conditions:
                row, final = trial(Path(root)/f'{cycle}-{condition}.rvp',
                                   initial, condition)
                row['cycle'] = cycle
                if expected is None:
                    expected = final
                elif final != expected:
                    raise AssertionError('Codecs changed logical outcome')
                data.append(row)
    grouped = {name: [x for x in data if x['condition']==name]
               for name in ('json','bql2')}
    median_runs = {name: statistics.median(x['median_ms'] for x in rows)
                   for name, rows in grouped.items()}
    med_bytes = {name: statistics.median(x['rvpc2_bytes'] for x in rows)
                 for name, rows in grouped.items()}
    report = {
        'experiment': 'BBYQ-CODEC-AB01',
        'paired_cycles': 7,
        'experiences_per_trial': 24,
        'order': 'alternating AB/BA on same GitHub runner and same XI executable',
        'benchmark_median_of_trial_medians_ms': median_runs,
        'benchmark_median_rvpc2_bytes': med_bytes,
        'runtime_state_identical_per_cycle': True,
        'qubits_allocated': 0,
        'per_trial': data,
        'platform': platform.platform(),
        'notes': 'Includes Python encoding, process launch, XI transport and RVPC2 commits. '
                 'Not an isolated compression CPU benchmark; uncompressed JSON is a control '
                 'inside the same REVERSE-PC technology, not an external implementation.',
    }
    target = Path(os.environ.get('BBYQ_CODEC_BENCH_OUTPUT','codec-comparison.json'))
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(report,indent=2,sort_keys=True)+'\n')
    print(json.dumps(report,indent=2,sort_keys=True))


if __name__ == '__main__':
    main()
