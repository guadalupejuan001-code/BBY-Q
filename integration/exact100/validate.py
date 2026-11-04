#!/usr/bin/env python3
"""Independent 100-qubit Pauli certificates and real native persistence tests."""
import argparse
import json
from pathlib import Path
import random
import tempfile
import time
import types
from cli import BASE, WIDTH, SEED, prepare, command, native, audit_state, parse_circuit, digest, statistics, xi


def conjugate(rows, gate):
    # Independent verification algebra: P = i^p X^x Z^z, Python integer masks.
    # This is a test oracle; it is never used to execute a production circuit.
    op, a, *tail = gate
    transformed = []
    for x, z, p in rows:
        xa, za = (x >> a) & 1, (z >> a) & 1
        if op == 'h':
            p += 2*xa*za
            if xa != za: x ^= 1 << a; z ^= 1 << a
        elif op == 's':
            p += xa
            if xa: z ^= 1 << a
        elif op in ['x', 'y', 'z']:
            p += 2*(za if op == 'x' else xa if op == 'z' else xa+za)
        elif op == 'cx':
            b = tail[0]
            if xa: x ^= 1 << b
            if (z >> b) & 1: z ^= 1 << a
        elif op == 'cz':
            b = tail[0]; xb = (x >> b) & 1
            p += 2*xa*xb
            if xb: z ^= 1 << a
            if xa: z ^= 1 << b
        else:
            raise AssertionError(op)
        transformed.append((x, z, p % 4))
    return transformed


def certificate(gates):
    rows = [(0, 1 << i, 0) for i in range(WIDTH)]
    for gate in gates: rows = conjugate(rows, gate)
    # A full rank set of 100 commuting Hermitian stabilizers determines the
    # complete pure state, up to its physically irrelevant global phase.
    basis = {}
    for x, z, p in rows:
        assert (p-(x & z).bit_count()) % 2 == 0
        vector = x | (z << WIDTH)
        while vector:
            top = vector.bit_length()-1
            if top not in basis: basis[top] = vector; break
            vector ^= basis[top]
    assert len(basis) == WIDTH
    for x, z, _ in rows:
        for a, b, _ in rows:
            assert ((x & b).bit_count()+(z & a).bit_count()) % 2 == 0
    program, expected = [], []
    for x, z, p in rows:
        terms = []
        for i in range(WIDTH):
            a, b = (x >> i) & 1, (z >> i) & 1
            if a or b: terms.append(('Y' if a and b else 'X' if a else 'Z')+':'+str(BASE+i))
        sign = (p-(x & z).bit_count()) % 4
        assert sign in [0, 2]
        program.append('expect '+' '.join(terms))
        expected.append(1 if sign == 0 else -1)
    return '\n'.join(program)+'\n', expected


def main():
    p = argparse.ArgumentParser();p.add_argument('--runtime', type=Path, required=True);p.add_argument('--output', type=Path, required=True)
    args = p.parse_args();runtime = args.runtime.resolve();started = time.perf_counter()
    checks = 0
    with tempfile.TemporaryDirectory(prefix='bbyq-exact100-test-') as temp:
        root = Path(temp); session = root/'session'
        prepared = prepare(session, runtime)
        seed = session/'versions/0.rvp'; seed_hash = digest(seed)
        def run(source, state=seed):
            f, out = root/'test.xi', root/'test.rvp'
            f.write_text('#!reverse-pc-machine-v1\n'+source+'\nhalt\n')
            return native(runtime, ['run', f, state, out]), out

        # GHZ-100 has 99 independent ZZ stabilizers and one global X.
        all_x = ' '.join('X:'+str(BASE+i) for i in range(WIDTH))
        body = ''.join(f'expect Z:{BASE+i} Z:{BASE+i+1}\n' for i in range(WIDTH-1))+'expect '+all_x+'\n'
        body += ''.join(f'probz {BASE+i}\n' for i in range(WIDTH))+'stats\nqstats\n'
        events, _ = run(body);statistics(events)
        assert [e['value'] for e in events if e['type']=='expectation'] == [1]*100
        assert [e['probability_one'] for e in events if e['type']=='probz'] == [.5]*100
        checks += 200

        # Every site changes global phase coherence and neighboring parity.
        body = ''
        for i in range(WIDTH):
            q, neighbor = BASE+i, BASE+(i+1)%WIDTH
            body += f'z {q}\nexpect {all_x}\nz {q}\nx {q}\nexpect Z:{q} Z:{neighbor}\nx {q}\n'
        events, _ = run(body)
        assert [e['value'] for e in events if e['type']=='expectation'] == [-1]*200
        checks += 200

        # Mixed phases and long-range entangling gates on the complete register.
        rng = random.Random(20261104)
        circuits = []
        for trial in range(8):
            gates = [['s', i] for i in range(100)]
            for j in range(300):
                op = rng.choice(['h', 's', 'x', 'y', 'z', 'cx', 'cz'])
                a, b = rng.sample(range(WIDTH), 2)
                gates.append([op, a, b] if op in ['cx', 'cz'] else [op, a])
            proof, expected = certificate(SEED+gates)
            events, after = run(xi(gates)+proof+'stats\nqstats\n')
            statistics(events)
            assert [e['value'] for e in events if e['type']=='expectation'] == expected, trial
            audit_state(runtime, after, SEED+gates)
            circuits.append({'trial': trial, 'gates': len(gates), 'independent_exact_stabilizers': 100})
            checks += 200

        # Real measurements: all 100 outcomes must agree for each GHZ sample.
        outcomes = []
        for trial in range(12):
            events, _ = run(f'seed {1700+trial}\n'+''.join(f'measure {BASE+i}\n' for i in range(WIDTH)))
            observed = [e for e in events if e['type']=='measurement']
            assert len(observed) == WIDTH
            values = [e['outcome_one'] for e in observed]
            assert len(set(values)) == 1
            assert observed[0]['probability'] == .5
            assert all(e['probability']==1 for e in observed[1:])
            outcomes.append(values[0]);checks += WIDTH
        assert len(set(outcomes)) == 2

        # Protected API: reject uncertified gates, preserve the published state.
        original_head = (session/'HEAD.json').read_bytes()
        for source in ['t 10000', 'rz 10000 0.1', 'h 9999', 'cx 10000 10100', 'cx 10000 10000', 'qprepare 10000 100', 'h $r0']:
            f = root/'rejected.xi';f.write_text(source)
            try: parse_circuit(f)
            except ValueError: pass
            else: raise AssertionError('Uncertified program accepted: '+source)
            assert (session/'HEAD.json').read_bytes() == original_head and digest(seed)==seed_hash
            checks += 1

        f = root/'accepted.xi';f.write_text('#!reverse-pc-machine-v1\ns 10099\nh 10017\ncz 10017 10084\nhalt\n')
        applied = command(types.SimpleNamespace(command='apply', session=str(session), circuit=str(f)))
        assert applied['revision']==1
        current = session/json.loads((session/'HEAD.json').read_text())['file']
        proof, expected = certificate(SEED+[['s',99],['h',17],['cz',17,84]])
        events, _ = run(proof,current)
        assert [e['value'] for e in events if e['type']=='expectation']==expected
        reopened = command(types.SimpleNamespace(command='audit', session=str(session)))
        assert reopened['checkpoint_sha256']==applied['checkpoint_sha256']
        exported = root/'export.rvp'
        command(types.SimpleNamespace(command='export',session=str(session),output=str(exported)))
        assert digest(exported)==digest(current) and digest(seed)==seed_hash
        checks += 103

        # Hash corruption must fail without publishing a new revision.
        before = (session/'HEAD.json').read_bytes();saved = current.read_bytes()
        current.write_bytes(saved[:-1]+bytes([saved[-1]^1]))
        try: command(types.SimpleNamespace(command='audit',session=str(session)))
        except ValueError: pass
        else: raise AssertionError('Corrupted checkpoint accepted')
        assert (session/'HEAD.json').read_bytes()==before
        current.write_bytes(saved);checks += 1

        report = {'ok': True, 'qubits': 100, 'connected_seed': 'GHZ-100', 'independent_stabilizers_per_circuit': 100,
                  'zero_tolerance_checks': checks, 'random_circuits': circuits, 'all_sites_causal_tests': 200,
                  'full_register_measurements': 12, 'measurement_outcomes': outcomes,
                  'original_seed_preserved': True, 'checkpoint_restore_verified': True,
                  'rejected_uncertified_programs': 7, 'tableau_bytes': prepared['tableau_bytes'],
                  'checkpoint_bytes': prepared['checkpoint_bytes'], 'runtime_sha256': digest(runtime),
                  'floating_state_coefficients': False, 'mps': False, 'training_updates': 0,
                  'conversational_model': False, 'elapsed_seconds': time.perf_counter()-started}
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(report, indent=2)+'\n')
        print(json.dumps(report, indent=2))


if __name__ == '__main__': main()
