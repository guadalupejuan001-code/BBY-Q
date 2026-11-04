#!/usr/bin/env python3
"""Transport and proof boundary for the user's exact Clifford XI register."""
import argparse
import contextlib
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import uuid

ROOT = Path(__file__).resolve().parents[2]
WIDTH, BASE, MAX_GATES = 100, 10000, 4096
OPS = {'h': 1, 's': 1, 'x': 1, 'y': 1, 'z': 1, 'cx': 2, 'cz': 2}
SEED = [['h', 0]] + [['cx', i, i+1] for i in range(WIDTH-1)]


def require(value, message):
    if not value:
        raise ValueError(message)


def digest(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def source_pins():
    return {p: digest(ROOT/p) for p in ['ai/xi/exact100/birth.xi', 'integration/exact100/cli.py']}


def atomic_json(p, value):
    pending = p.with_name(p.name+'.'+uuid.uuid4().hex+'.pending')
    try:
        with pending.open('x') as out:
            os.chmod(pending, 0o600)
            out.write(json.dumps(value, indent=2)+'\n')
            out.flush()
            os.fsync(out.fileno())
        os.replace(pending, p)
    finally:
        pending.unlink(missing_ok=True)


def native(runtime, args):
    p = subprocess.run([str(runtime), *map(str, args)], text=True,
                       capture_output=True, timeout=60, check=True)
    return [json.loads(line) for line in p.stdout.splitlines() if line.startswith('{')]


def validate_gates(gates):
    require(isinstance(gates, list) and len(gates) <= MAX_GATES, 'Circuit exceeds 4096 exact gates')
    for gate in gates:
        require(isinstance(gate, list) and gate and isinstance(gate[0], str), 'Invalid gate')
        require(gate[0] in OPS and len(gate) == OPS[gate[0]]+1, 'Unsupported exact gate')
        require(all(type(q) is int and 0 <= q < WIDTH for q in gate[1:]), 'Qubit outside the 100-qubit register')
        if len(gate) == 3:
            require(gate[1] != gate[2], 'Two-qubit gate requires distinct qubits')
    return gates


def parse_circuit(p):
    require(p.stat().st_size <= 128*1024, 'XI circuit exceeds 128 KiB')
    lines = [line.split('#', 1)[0].strip() for line in p.read_text().splitlines()]
    lines = [line for line in lines if line]
    if lines and lines[-1] == 'halt':
        lines.pop()
    gates = []
    for line in lines:
        tokens = line.split()
        require(tokens[0] in OPS, 'Exact100 permits only H/S/X/Y/Z/CX/CZ; continuous rotations and T are not certified')
        require(all(x.isascii() and x.isdecimal() for x in tokens[1:]), 'Use literal XI addresses 10000..10099')
        gates.append([tokens[0], *[int(x)-BASE for x in tokens[1:]]])
    require(gates, 'Empty circuit')
    return validate_gates(gates)


def xi(gates):
    return ''.join(op+' '+ ' '.join(str(BASE+q) for q in qs)+'\n' for op, *qs in gates)


def inverse(gates):
    return [g for gate in reversed(gates) for g in ([gate]*3 if gate[0] == 's' else [gate])]


def statistics(events):
    state = next((e for e in events if e['type'] == 'stats'), {})
    quantum = next((e for e in events if e['type'] == 'quantum_stats'), {})
    require(state.get('active_qubits') == WIDTH and state.get('components') == 1 and state.get('largest_component') == WIDTH,
            'State is not one 100-qubit component')
    require(state.get('background') == 'zero' and state.get('ether_rules') == 0, 'Unexpected core background or frame')
    require(quantum.get('clifford_components') == 1 and quantum.get('adaptive_components') == 0 and quantum.get('reduced_components') == 0,
            'Non-Clifford state is outside this exact profile')
    require(quantum.get('coefficients') == 0 and quantum.get('factor_amplitudes') == 0 and quantum.get('T_instructions') == 0,
            'Floating coefficients are outside this exact profile')
    require(quantum.get('norm') == 1 and quantum.get('payload_bytes') == state.get('tableau_bytes'), 'Invalid exact state payload')
    return state, quantum


def audit_state(runtime, state, gates):
    """The full inverse must restore every Z_i to +1, with no tolerance."""
    validate_gates(gates)
    original = digest(state)
    with tempfile.TemporaryDirectory(prefix='bbyq-exact100-proof-') as temp:
        p, out = Path(temp)/'proof.xi', Path(temp)/'proof.rvp'
        p.write_text('#!reverse-pc-machine-v1\nstats\nqstats\n'+xi(inverse(gates))+
                     ''.join(f'expect Z:{BASE+i}\nprobz {BASE+i}\n' for i in range(WIDTH))+'halt\n')
        events = native(runtime, ['run', p, state, out])
    s, q = statistics(events)
    observed = [e['value'] for e in events if e['type'] == 'expectation']
    probabilities = [e['probability_one'] for e in events if e['type'] == 'probz']
    require(observed == [1]*WIDTH and probabilities == [0]*WIDTH,
            'Full 100-qubit inverse certificate failed')
    require(digest(state) == original, 'Read-only proof changed the checkpoint')
    return {'registered_qubits': WIDTH, 'components': 1, 'tableau_bytes': s['tableau_bytes'],
            'checkpoint_bytes': state.stat().st_size, 'checkpoint_sha256': original,
            'representation': 'original CompactCore Clifford stabilizer; integer/sign algebra',
            'mps': False, 'floating_state_coefficients': False, 'inverse_z_certificates': WIDTH,
            'comparison_tolerance': 0, 'known_circuit_gates': len(gates),
            'training_updates': 0, 'conversational_model': False}


def load(session):
    config = json.loads((session/'profile.json').read_text())
    require(config.get('schema') == 1 and config.get('qubits') == WIDTH and config.get('profile') == 'exact100-clifford', 'Wrong profile')
    runtime = Path(config['runtime'])
    require(digest(runtime) == config['runtime_sha256'], 'Runtime changed; preserve this session and prepare another')
    require(source_pins() == config['source_sha256'], 'Profile implementation changed')
    head = json.loads((session/'HEAD.json').read_text())
    require(type(head.get('revision')) is int and head['revision'] >= 0, 'Invalid revision')
    file = head.get('file', '')
    require(file.startswith('versions/') and Path(file).name == file.removeprefix('versions/') and file.endswith('.rvp'), 'Invalid checkpoint path')
    state = session/file
    require(digest(state) == head['sha256'], 'Checkpoint hash mismatch')
    validate_gates(head['circuit'])
    return config, head, runtime, state


@contextlib.contextmanager
def locked(session):
    lock = session/'.write-lock'
    fd = os.open(lock, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    try:
        yield
    finally:
        os.close(fd)
        lock.unlink()


def prepare(session, runtime):
    require(not session.exists(), 'Choose a new directory; existing models are preserved')
    runtime = runtime.resolve()
    require(runtime.is_file(), 'Provide the compiled reverse_pc executable')
    session.parent.mkdir(parents=True, exist_ok=True)
    staging = Path(tempfile.mkdtemp(prefix='.bbyq-exact100-', dir=session.parent))
    try:
        (staging/'versions').mkdir()
        empty, state = staging/'empty.rvp', staging/'versions/0.rvp'
        native(runtime, ['init', empty])
        statistics(native(runtime, ['run', ROOT/'ai/xi/exact100/birth.xi', empty, state]))
        report = audit_state(runtime, state, SEED)
        empty.unlink()
        atomic_json(staging/'profile.json', {'schema': 1, 'profile': 'exact100-clifford', 'qubits': WIDTH,
                    'runtime': str(runtime), 'runtime_sha256': digest(runtime), 'source_sha256': source_pins()})
        atomic_json(staging/'HEAD.json', {'revision': 0, 'file': 'versions/0.rvp', 'sha256': report['checkpoint_sha256'], 'circuit': SEED})
        require(not session.exists(), 'Destination appeared; refusing overwrite')
        staging.rename(session)
        return {'ok': True, 'action': 'prepare-exact100', 'session': str(session), 'revision': 0, **report}
    finally:
        if staging.exists():
            shutil.rmtree(staging)


def command(args):
    session = Path(args.session).resolve()
    if args.command == 'prepare':
        return prepare(session, Path(args.runtime))
    if args.command == 'apply':
        gates = parse_circuit(Path(args.circuit))
        with locked(session):
            config, head, runtime, state = load(session)
            all_gates = validate_gates(head['circuit']+gates)
            name = f"versions/{head['revision']+1}-{uuid.uuid4().hex}.rvp"
            target = session/name
            try:
                with tempfile.TemporaryDirectory(prefix='bbyq-exact100-apply-') as temp:
                    source = Path(temp)/'apply.xi'
                    source.write_text('#!reverse-pc-machine-v1\n'+xi(gates)+'stats\nqstats\nhalt\n')
                    statistics(native(runtime, ['run', source, state, target]))
                report = audit_state(runtime, target, all_gates)
                require(digest(state) == head['sha256'], 'Prior checkpoint changed')
                atomic_json(session/'HEAD.json', {'revision': head['revision']+1, 'file': name, 'sha256': report['checkpoint_sha256'], 'circuit': all_gates})
                return {'ok': True, 'action': 'apply-exact100', 'revision': head['revision']+1, **report}
            except BaseException:
                # A process interruption may arrive after HEAD was published.
                # Keep immutable candidates; an orphan is safer than deleting
                # the newly committed checkpoint behind a valid HEAD.
                raise
    config, head, runtime, state = load(session)
    report = audit_state(runtime, state, head['circuit'])
    if args.command == 'export':
        target = Path(args.output).resolve()
        with target.open('xb') as out, state.open('rb') as src:
            shutil.copyfileobj(src, out)
        require(digest(target) == report['checkpoint_sha256'], 'Export hash mismatch')
        report['file'] = str(target)
    return {'ok': True, 'action': args.command+'-exact100', 'revision': head['revision'], **report}


def main():
    parser = argparse.ArgumentParser(description='100 exact simulated Clifford qubits in XI/Ether')
    sub = parser.add_subparsers(dest='command', required=True)
    p = sub.add_parser('prepare'); p.add_argument('session'); p.add_argument('--runtime', required=True)
    for name in ['audit', 'status']:
        sub.add_parser(name).add_argument('session')
    p = sub.add_parser('apply'); p.add_argument('session'); p.add_argument('circuit')
    p = sub.add_parser('export'); p.add_argument('session'); p.add_argument('output')
    try:
        print(json.dumps(command(parser.parse_args()), indent=2))
    except (ValueError, OSError, subprocess.SubprocessError, KeyError) as error:
        print(json.dumps({'ok': False, 'error': str(error)}))
        raise SystemExit(1)


if __name__ == '__main__':
    main()
