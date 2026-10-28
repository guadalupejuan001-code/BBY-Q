#!/usr/bin/env python3
"""Exercise the recovered E025 capsule with the native XI runtime."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
from build import build

parser = argparse.ArgumentParser()
parser.add_argument('runtime')
parser.add_argument('output')
args = parser.parse_args()
runtime = str(Path(args.runtime).resolve())
out = Path(args.output).resolve()
build(runtime, out)
checks = 0


def check(condition, message):
    global checks
    if not condition:
        raise AssertionError(message)
    checks += 1


def run(*items):
    return subprocess.check_output([runtime, *map(str, items)], text=True)


app, state = out / 'BBY-Q.rxe', out / 'live.rvp'
shutil.copy2(out / 'controller.rvp', state)


def ask(text, language='es'):
    return run('app-turn', app, state, state, language, text).strip()


check(ask('hola') == 'Hola. Soy BBY Q.', 'Spanish greeting')
check('BBY Q' in ask('hello', 'en'), 'English greeting')
check('Calculadora es herramienta' in ask('que es calculadora'), 'E025 desktop knowledge')
for i in range(12):
    subject = 'qelora' + chr(ord('a') + i)
    check('Aprendí' in ask('aprende que ' + subject + ' es animal'), 'Teach a new independent concept')
for i in range(12):
    subject = 'qelora' + chr(ord('a') + i)
    answer = ask('que es ' + subject)
    check(subject.capitalize() in answer and 'animal' in answer, 'Retain learned facts across process restarts')

# An observed calculator is a real typed goal for W4u. Read the returned action
# from the candidate's logical memory; no frontend interpretation is involved.
A, M = 8200000000000000000, 8300000000000000000
observation = out / 'observation.xi'
rows = [f'store8 {A+16} 1', f'store8 {A+17} 2', f'store8 {A+18} 1']
for i in range(32):
    rows += [f'store8 {A+32+i} {int(i==2)}', f'store8 {M+640+i} 0',
             f'store8 {M+672+i} 0', f'store8 {M+512+i} 0']
observation.write_text('#!reverse-pc-machine-v1\n' + '\n'.join(rows) + '\nhalt\n')
run('run', observation, state, state)
check(bool(ask('maximiza calculadora')), 'W4u returns a response')
read_action = out / 'read-action.xi'
read_action.write_text(f'#!reverse-pc-machine-v1\nload8 r0 {A+64}\nprint r0\nload8 r1 {A+65}\nprint r1\nhalt\n')
actions = [json.loads(row)['value'] for row in run('run', read_action, state, state).splitlines() if row.startswith('{')]
check(actions == [4, 2], 'W4u requests calculator maximization')

before = state.read_bytes()
failure = subprocess.run([runtime, 'app-turn', str(app), str(state), str(state), 'es', 'x' * 256], capture_output=True)
check(failure.returncode != 0 and state.read_bytes() == before, 'Oversized input is rejected atomically')

# A real write above the former 65,536 override limit checks the expanded native
# memory budget instead of testing only a displayed capacity number.
capacity = out / 'capacity.xi'
capacity.write_text('#!reverse-pc-machine-v1\n' + ''.join(f'store8 {7000000000000000000+i} 7\n' for i in range(70000)) + 'load8 r0 7000000000000069999\nprint r0\nhalt\n')
capacity_output = run('run', capacity, state, out / 'capacity.rvp')
check('"value":7' in capacity_output, 'Native memory retains more than 65,536 overrides')
report = {'checks': checks, 'version': 'E025-Chain-1', 'w4u_version': '0.1',
          'app_sha256': hashlib.sha256(app.read_bytes()).hexdigest(),
          'retained_independent_concepts': 12, 'new_override_writes': 70000,
          'scope': 'Native Linux XI/RXE execution; Android host is tested separately.'}
(out / 'tests.json').write_text(json.dumps(report, indent=2) + '\n')
print(json.dumps(report, indent=2))
