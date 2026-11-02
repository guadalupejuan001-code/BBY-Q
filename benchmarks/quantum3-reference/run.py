#!/usr/bin/env python3
"""Same-machine circuit comparison against qsim; no product model is replaced.

The external reference is qsim Basic/CPU/binary64, manually factorized into
250 independent four-wire states per register. This adapter is new benchmark
code, not evidence of a historical qsim 1000-qubit RL agent. Timings compare
frozen circuit inference, not complete learning campaigns or different papers.
"""
import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import platform
import random
import statistics
import struct
import subprocess
import sys
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'integration/quantum3'))
from campaign import A, XI, Experiment, metrics, sha

QSIM_COMMIT = '50cac4b3fa331450b70387735479a00e223b8d25'


def unpack(events, count):
    return [struct.unpack('<' + 'd' * count, bytes.fromhex(row['hex']))
            for row in events if row['type'] == 'memory_materialization']


def maximum_error(left, right):
    return max(abs(a-b) for a, b in zip(left, right, strict=True))


def git_head(path):
    return subprocess.check_output(['git', '-C', str(path), 'rev-parse', 'HEAD'], text=True).strip()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--runtime', required=True)
    parser.add_argument('--mundo-x', required=True)
    parser.add_argument('--qsim', required=True)
    parser.add_argument('--checkpoint', help='Optional delivered model; otherwise reproducible nonzero test parameters')
    parser.add_argument('--output', required=True)
    parser.add_argument('--samples-per-agent', type=int, default=8)
    parser.add_argument('--repetitions', type=int, default=20)
    args = parser.parse_args()
    if args.samples_per_agent < 2 or args.repetitions < 2:
        parser.error('at least two samples and repetitions are required')
    out = Path(args.output).resolve()
    out.mkdir(parents=True, exist_ok=True)
    if (out/'summary.json').exists():
        parser.error('output contains an existing result; choose another directory')
    runtime, qsim = Path(args.runtime).resolve(), Path(args.qsim).resolve()
    ether = Path(args.mundo_x).resolve()
    assert git_head(qsim) == QSIM_COMMIT, 'use the pinned qsim source'
    affinity = None
    if hasattr(os, 'sched_getaffinity'):
        affinity = min(os.sched_getaffinity(0))
        os.sched_setaffinity(0, {affinity})
    reference = out/'qsim_reference'
    compiler = ['g++', '-std=c++17', '-O2', '-pthread', '-I'+str(qsim),
                str(Path(__file__).with_name('qsim_reference.cpp')), '-o', str(reference)]
    built = subprocess.run(compiler, capture_output=True, text=True)
    (out/'compile.log').write_text(built.stdout+built.stderr)
    if built.returncode:
        raise RuntimeError(built.stderr)
    measured_xi = out/'xi_session_memory_probe'
    xi_command = ['g++', '-std=c++17', '-O2', '-pthread',
        '-DREVERSE_PC_HAVE_BOUNDED_PRODUCT_IMPORT=1',
        '-DBBYQ_XI_SOURCE='+json.dumps(str(runtime/'src/xi_session.cpp')),
        '-I'+str(runtime/'build/ether-compat'), '-I'+str(ether/'native/include'), '-I'+str(runtime/'src'),
        str(Path(__file__).with_name('xi_memory_probe.cpp')), '-o', str(measured_xi)]
    if not (runtime/'build/ether-compat/mundo_x/quantum_runtime.hpp').exists():
        parser.error('compile pinned Ether/REVERSE-PC with build-xi-session.sh first')
    built = subprocess.run(xi_command, capture_output=True, text=True)
    (out/'xi-memory-probe-compile.log').write_text(built.stdout+built.stderr)
    if built.returncode:
        raise RuntimeError(built.stderr)
    options = SimpleNamespace(runtime=str(runtime), session_binary=str(measured_xi), step_budget=10000000,
        agent='vqc', task='linear', seed=173, episodes=1, eval_size=1, classical=False,
        analytic=False, joint_mode='independent', initial_checkpoint=None,
        output=str(out/'transport'), resume=False)
    e = Experiment(options)
    empty, initial = out/'empty.rvp', out/'initial.rvp'
    subprocess.run([e.cli, 'init', empty], check=True, capture_output=True)
    with e.Session(e.binary, empty) as session:
        session.execute((XI/'birth.xi').read_text()+'\n'+e.lib)
        session.save(initial)
    checkpoint = Path(args.checkpoint).resolve() if args.checkpoint else None
    checkpoint_hash = sha(checkpoint) if checkpoint else None
    models = {}
    if checkpoint:
        with e.Session(e.binary, checkpoint) as session:
            for role in [0, 1]:
                base = A+(100000 if role == 0 else 200000)
                meta = A+(4000 if role == 0 else 5000)
                events, _ = session.execute(e.source(
                    f'mem_materialize {base} 8000\nmem_materialize {base+10000} 8000'))
                theta, weights = unpack(events, 1000)
                events, _ = session.execute(e.source(f'mem_materialize {meta+16} 8'))
                models[role] = (theta, weights, unpack(events, 1)[0][0])
    else:
        rng = random.Random(20261102)
        for role in [0, 1]:
            models[role] = ([rng.uniform(-.8, .8) for _ in range(1000)],
                            [rng.uniform(-.3, .3) for _ in range(1000)], .07)
    fixtures = []
    with e.Session(e.binary, initial) as session:
        for role in [0, 1]:
            for i in range(args.samples_per_agent):
                if role == 0:
                    e.args.task = ['linear', 'parity', 'dense'][i % 3]
                    body = e.stage('iid' if i % 2 else 'ood', i).split('call select_agent')[0]
                else:
                    body = (f'store64 {A+344} {i%7}\nstore64 {A+352} {6 if i%2 else 0}\n'
                            f'store64 {A+360} {i%5}\nstore64 {A+312} 12\ncall qrl_observe\nfstore {A+128} 0')
                events, _ = session.execute(e.source(body+f'\nmem_materialize {A+300000} 8000'))
                values = unpack(events, 1000)[0]
                events, _ = session.execute(e.source(f'mem_materialize {A+128} 8'))
                label = unpack(events, 1)[0][0]
                theta, weights, bias = models[role]
                fixtures.append(dict(role=role, block=249 if i == 0 else (37*i)%250,
                    x=values, theta=theta, weights=weights, bias=bias, label=label))
    warmups = 2
    fixture_file = out/'fixtures.txt'
    with fixture_file.open('w') as file:
        file.write(f'{len(fixtures)} {args.repetitions} {warmups}\n')
        for f in fixtures:
            file.write(f'{f["role"]} {f["block"]} {f["bias"]:.17g} {f["label"]:.17g}\n')
            for key in ['x', 'theta', 'weights']:
                file.write(' '.join(format(v, '.17g') for v in f[key])+'\n')

    def run_qsim(round_id):
        result = subprocess.run([reference, fixture_file], check=True, capture_output=True, text=True)
        (out/f'qsim-round-{round_id}.jsonl').write_text(result.stdout)
        return [json.loads(line) for line in result.stdout.splitlines()]

    def run_xi(round_id):
        rows = []
        with e.Session(e.binary, initial) as session:
            for case_id, f in enumerate(fixtures):
                base = A+(100000 if f['role'] == 0 else 200000)
                meta = A+(4000 if f['role'] == 0 else 5000)
                body = [f'store64 {A} {f["role"]}', f'store64 {A+280} 0',
                        f'fstore {meta+16} {f["bias"]:.17g}', f'store64 {meta} {f["block"]}',
                        f'fstore {A+128} {f["label"]:.17g}']
                for key, address in [('x', A+300000), ('theta', base), ('weights', base+10000)]:
                    body.extend(f'fstore {address+8*i} {value:.17g}' for i, value in enumerate(f[key]))
                body += ['call select_agent', 'qtrace reset']
                session.execute(e.source('\n'.join(body)))
                # XI scratch registers are local to each EXEC; select the
                # persistent model again inside every independently timed call.
                timed = e.source('call select_agent\nqtrace reset\nclock f28\ncall forward\nclock f29\nfsub f29 f28\n'
                                 'femit forward_ms f29\nfemit probability f21\nfemit score f20\nqtrace report')
                times, transport = [], []
                for j in range(args.repetitions+warmups):
                    events, elapsed = session.execute(timed)
                    if j >= warmups:
                        times.append(metrics(events)['forward_ms'])
                        transport.append(elapsed)
                values = metrics(events)
                trace = next(row for row in events if row['type'] == 'quantum_trace')
                assert trace['distinct_observed_qubits'] == trace['distinct_rotated_qubits'] == 1000
                assert trace['active_qubits'] == 2000, (case_id, trace)
                assert trace['rotations'] == 2000
                assert trace['observations'] == 1000 and trace['gates'] == 750
                events, _ = session.execute(e.source(f'mem_materialize {A+310000} 8000'))
                observations = unpack(events, 1000)[0]
                events, _ = session.execute(e.source(f'call select_agent\nset r9 {4*f["block"]}\ncall selected_gradients\n'
                    f'mem_materialize {A+130000+32*f["block"]} 32'))
                row = dict(case=case_id, role=f['role'], native_ms=times, transport_ms=transport,
                           observations=observations, gradients=unpack(events, 4)[0], trace=trace,
                           score=values['score'], probability=values['probability'])
                if f['role'] == 0:
                    events, _ = session.execute(e.source('call supervised_update\n'+
                        f'mem_materialize {base} 8000\nmem_materialize {base+10000} 8000'))
                    row['sgd_theta'], row['sgd_weights'] = unpack(events, 1000)
                    events, _ = session.execute(e.source(f'mem_materialize {meta+16} 8'))
                    row['sgd_bias'] = unpack(events, 1)[0][0]
                row['usage'] = session.metrics()
                rows.append(row)
        (out/f'xi-round-{round_id}.jsonl').write_text(''.join(json.dumps(r)+'\n' for r in rows))
        return rows

    # AB/BA order prevents treating one backend's warm/cold order as an advantage.
    references, natives = [], []
    references.append(run_qsim(0)); natives.append(run_xi(0))
    natives.append(run_xi(1)); references.append(run_qsim(1))
    errors = dict(observations=0., score=0., probability=0., gradients=0., sgd_parameters=0.)
    for qr, xr in zip(references, natives, strict=True):
        assert len(qr) == len(xr) == len(fixtures)
        for q, x in zip(qr, xr, strict=True):
            assert q['case'] == x['case']
            for name in ['observations', 'gradients']:
                errors[name] = max(errors[name], maximum_error(q[name], x[name]))
            for name in ['score', 'probability']:
                errors[name] = max(errors[name], abs(q[name]-x[name]))
            if x['role'] == 0:
                for name in ['sgd_theta', 'sgd_weights']:
                    errors['sgd_parameters'] = max(errors['sgd_parameters'], maximum_error(q[name], x[name]))
                errors['sgd_parameters'] = max(errors['sgd_parameters'], abs(q['sgd_bias']-x['sgd_bias']))
    assert max(errors.values()) < 1e-10, errors
    if checkpoint:
        assert sha(checkpoint) == checkpoint_hash, 'input model changed'
    comparisons = []
    for role, name in [(0, 'vqc'), (1, 'qrl')]:
        xx = [row for run in natives for row in run if row['role'] == role]
        qq = [row for run in references for row in run if fixtures[row['case']]['role'] == role]
        xi_time = statistics.median(t for row in xx for t in row['native_ms'])
        qsim_time = statistics.median(t for row in qq for t in row['native_ms'])
        comparisons.append(dict(agent=name, qubits_evaluated_per_forward=1000,
            xi_median_native_ms=xi_time, qsim_median_native_ms=qsim_time,
            xi_median_transport_ms=statistics.median(t for row in xx for t in row['transport_ms']),
            xi_over_qsim_native_time=xi_time/qsim_time,
            xi_peak_native_rss_mib=max(row['usage']['peak_rss_kib'] for row in xx)/1024,
            qsim_peak_native_rss_mib=max(row['peak_rss_kib'] for row in qq)/1024))
    summary = dict(ok=True, verified_utc=datetime.now(timezone.utc).isoformat(),
        comparison='Identical frozen 1000-wire local circuit inference; not complete RL training',
        qsim_adapter_is_new_reference_not_historical_rl_agent=True,
        qsim_backend='SimulatorBasic<SequentialFor,double>; explicit 250 independent four-wire states per agent',
        simultaneous_allocated_qubits=2000, samples_per_agent=args.samples_per_agent,
        repetitions_per_case_per_round=args.repetitions, rounds=2, order='qsim,XI,XI,qsim',
        cpu_affinity=affinity, platform=platform.platform(),
        memory_measurement='Linux /proc/self/status VmHWM after exec for both native workers; measurement-only XI wrapper',
        qsim_commit=QSIM_COMMIT, reverse_commit=git_head(runtime), ether_commit=git_head(ether),
        fixture_sha256=sha(fixture_file), delivered_model_sha256=checkpoint_hash,
        instrumented_xi_session_sha256=sha(e.binary),
        original_xi_session_sha256=sha(runtime/'build/xi_session'),
        xi_instrumentation='Only RSS reporting uses Linux VmHWM; original XI translation unit included unchanged',
        qsim_reference_sha256=sha(reference),
        numerical_max_absolute_errors=errors,
        observations_compared=2*len(fixtures)*1000,
        sgd_parameter_comparisons=2*args.samples_per_agent*2001,
        comparisons=comparisons,
        limits=['Measures native worker RSS, excludes Python orchestration for both backends',
                'XI timings include VM instructions, generic storage and exact quantum execution; qsim adapter is compiled C++',
                'Does not reproduce the different circuits, data or reported hardware of the QCNN or Quantum Mario papers',
                'No claim of a global speed, memory, qubit-count or historical-priority record'])
    (out/'summary.json').write_text(json.dumps(summary, indent=2)+'\n')
    print(json.dumps(summary), flush=True)


if __name__ == '__main__':
    main()
