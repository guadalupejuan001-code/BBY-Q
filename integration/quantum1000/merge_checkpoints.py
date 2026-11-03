#!/usr/bin/env python3
"""Transport both trained agents into a clean connected checkpoint.

Only the new output is written. Historical models stay in their original
files; the combined model has exactly two components of 1000 qubits.
"""
import argparse
import json
from pathlib import Path
from types import SimpleNamespace
from campaign import A, Experiment, sha

p=argparse.ArgumentParser()
p.add_argument('--runtime',required=True)
p.add_argument('--vqc',required=True)
p.add_argument('--qrl',required=True)
p.add_argument('--output',required=True)
args=p.parse_args()
destination=Path(args.output).resolve()
if destination.exists() or destination.with_suffix('.manifest.json').exists():
    p.error('output exists; choose a new checkpoint name')
e=Experiment(SimpleNamespace(runtime=args.runtime,session_binary=None,step_budget=10000000,
    agent='vqc',task='linear',seed=173,episodes=1,eval_size=1,classical=False,
    output=str(destination.parent/'merge-transport'),resume=False))
sources={name:Path(getattr(args,name)).resolve() for name in ['vqc','qrl']}
originals={name:sha(path) for name,path in sources.items()}
payload=[];models={};entanglers=[]
guard=f'load8 r0 {A+1000}\ncmp r0 174\nje connected_model\ndiv r0 0\nlabel connected_model'
for role in ['vqc','qrl']:
    e.args.agent=role
    base=A+(100000 if role=='vqc' else 200000);meta=A+(4000 if role=='vqc' else 5000)
    ranges=[(base,8000),(base+10000,8000),(base+20000,8000),(meta,48)]
    with e.Session(e.binary,sources[role]) as session:
        session.execute(e.source(guard))
        flag,_=session.execute(e.source(f'load64 r0 {A+1008}\nprint r0'))
        entanglers.append(next(x['value'] for x in flag if x['type']=='register'))
        models[role]=e.model_state(session)
        assert models[role]['rotation_parameters_updated']==1000
        assert models[role]['readout_parameters_changed']==1000
        events,_=session.execute(e.source('\n'.join(f'mem_materialize {a} {n}' for a,n in ranges)))
        for row in events:
            if row['type']=='memory_materialization':payload.append((int(row['address']),bytes.fromhex(row['hex'])))
assert entanglers[0]==entanglers[1] and entanglers[0] in [0,1],'cannot merge different circuit architectures'
with e.Session(e.binary,sources['vqc']) as combined:
    combined.execute(e.source(guard))
    transfer='\n'.join(f'store8 {address+i} {byte}' for address,data in payload for i,byte in enumerate(data))
    combined.execute(e.source(transfer))
    for role in ['vqc','qrl']:
        e.args.agent=role
        assert e.model_state(combined)==models[role],'trained parameter bytes changed in transfer'
    combined.execute(e.source(f'store64 {A+272} 0\nfstore {A+296} .1\nstore64 {A+256} 173\ncall vqc_sample\nstore64 {A} 0\ncall select_agent\ncall forward\nstore64 {A} 1\ncall select_agent\ncall forward'))
    events,_=combined.execute(e.source('qmpsinfo 5000\nqmpsinfo 7000\nstats'))
    registers=[x for x in events if x['type']=='mps_register']
    assert len(registers)==2 and all(x['qubits']==1000 and x['nonproduct_bipartitions']==999 for x in registers)
    stats=next(x for x in events if x['type']=='stats')
    assert stats['active_qubits']==2000 and stats['components']==2 and stats['largest_component']==1000
    combined.save(destination);usage=combined.metrics()
for name,path in sources.items():assert sha(path)==originals[name],'input checkpoint overwritten'
result={'ok':True,'source_checkpoints':{n:{'name':path.name,'sha256':originals[n]} for n,path in sources.items()},
    'entangler':'cz' if entanglers[0] else 'cnot',
    'models':models,'connected_registers':registers,'total_active_qubits':2000,
    'qubits_per_agent':1000,'quantum_components':2,'merged_checkpoint':destination.name,
    'merged_checkpoint_sha256':sha(destination),'usage':usage}
destination.with_suffix('.manifest.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2))
