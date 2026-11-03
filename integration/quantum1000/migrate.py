#!/usr/bin/env python3
"""Preserve trained coefficients; create connected states in a new checkpoint.

The original input is immutable. New-topology training counters start at zero;
historical counts and coefficient hashes are recorded in the migration report.
"""
import argparse
import json
from pathlib import Path
import struct
from types import SimpleNamespace
from campaign import A, Experiment, sha

p=argparse.ArgumentParser()
p.add_argument('--runtime',required=True)
p.add_argument('--input',required=True)
p.add_argument('--output',required=True)
p.add_argument('--report',required=True)
args=p.parse_args()
source=Path(args.input).resolve();target=Path(args.output).resolve();report=Path(args.report).resolve()
if target.exists() or report.exists():p.error('choose new output paths; existing files are preserved')
digest=sha(source)
e=Experiment(SimpleNamespace(runtime=args.runtime,session_binary=None,step_budget=10000000,
    agent='vqc',task='linear',seed=173,episodes=1,eval_size=1,classical=False,
    output=str(target.parent/'migration-transport'),resume=False))
before={};after={}
def coefficients(s,role):
    addresses=[A+(100000 if role==0 else 200000),A+(110000 if role==0 else 210000),A+(4016 if role==0 else 5016)]
    events,_=s.execute(e.source('\n'.join(f'mem_materialize {x} {8000 if i<2 else 8}' for i,x in enumerate(addresses))))
    import hashlib
    return hashlib.sha256(b''.join(bytes.fromhex(x['hex']) for x in events if x['type']=='memory_materialization')).hexdigest()
with e.Session(e.binary,source) as s:
    s.execute(e.source(f'load8 r0 {A+1000}\ncmp r0 173\nje valid_legacy_v3\ndiv r0 0\nlabel valid_legacy_v3'))
    for role,name in [(0,'vqc'),(1,'qrl')]:
        e.args.agent=name;before[name]={'model':e.model_state(s),'coefficient_sha256':coefficients(s,role)}
    lines=['qmps 5000 1000','qmps 7000 1000',f'store8 {A+1000} 174']
    for role in [0,1]:
        meta=A+(4000 if role==0 else 5000);visits=A+(120000 if role==0 else 220000)
        lines += [f'store64 {meta} 0',f'store64 {meta+8} 0']
        lines += [f'store64 {visits+8*q} 0' for q in range(1000)]
    s.execute(e.source('\n'.join(lines)))
    for role,name in [(0,'vqc'),(1,'qrl')]:
        e.args.agent=name;after[name]={'model':e.model_state(s),'coefficient_sha256':coefficients(s,role)}
        assert before[name]['coefficient_sha256']==after[name]['coefficient_sha256']
        assert after[name]['model']['training_episodes_in_checkpoint']==0
    s.save(target)
assert sha(source)==digest,'original checkpoint modified'
report.parent.mkdir(parents=True,exist_ok=True)
report.write_text(json.dumps({'input':source.name,'input_sha256':digest,'output':target.name,
    'output_sha256':sha(target),'before':before,'after':after,
    'note':'Coefficients preserved; initial quantum states re-prepared. Learning on the new connected topology is not yet established by migration.'},indent=2)+'\n')
print(report.read_text())
