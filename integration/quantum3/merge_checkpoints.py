#!/usr/bin/env python3
"""Transport validated V3 parameter bytes onto a preserved legacy checkpoint."""
import argparse
import json
from pathlib import Path
from types import SimpleNamespace
from campaign import A, XI, Experiment, sha

parser=argparse.ArgumentParser()
parser.add_argument('--runtime',required=True)
parser.add_argument('--session-binary')
parser.add_argument('--legacy',required=True)
parser.add_argument('--vqc',required=True)
parser.add_argument('--qrl',required=True)
parser.add_argument('--output',required=True)
args=parser.parse_args()
destination=Path(args.output).resolve()
if destination.exists(): parser.error('output exists; choose a new checkpoint name')
options=SimpleNamespace(runtime=args.runtime,session_binary=args.session_binary,step_budget=10000000,
                        agent='vqc',task='linear',seed=173,episodes=1,eval_size=1,classical=False,
                        analytic=False,joint_mode='independent',initial_checkpoint=None,
                        output=str(destination.parent/'merge-transport'),resume=False)
e=Experiment(options)
sources={name:Path(getattr(args,name)).resolve() for name in ['legacy','vqc','qrl']}
originals={name:sha(path) for name,path in sources.items()}
payload=[];models={}
for role in ['vqc','qrl']:
    e.args.agent=role
    base=A+(100000 if role=='vqc' else 200000)
    meta=A+(4000 if role=='vqc' else 5000)
    ranges=[(base,8000),(base+10000,8000),(base+20000,8000),(meta,48)]
    with e.Session(e.binary,sources[role]) as session:
        models[role]=e.model_state(session)
        assert models[role]['rotation_parameters_updated']==1000
        assert models[role]['readout_parameters_changed']==1000
        events,_=session.execute(e.source('\n'.join(f'mem_materialize {a} {n}' for a,n in ranges)))
        for row in events:
            if row['type']=='memory_materialization':
                payload.append((int(row['address']),bytes.fromhex(row['hex'])))
with e.Session(e.binary,sources['legacy']) as combined:
    combined.execute((XI/'birth.xi').read_text()+'\n'+e.lib)
    transfer='\n'.join(f'store8 {address+i} {byte}' for address,data in payload for i,byte in enumerate(data))
    combined.execute(e.source(transfer))
    for role in ['vqc','qrl']:
        e.args.agent=role
        assert e.model_state(combined)==models[role],'parameter transfer changed trained bytes'
    old_program=Path(__file__).resolve().parents[2]/'ai/xi/qml_qrl/agents1000-audit.xi'
    events,_=combined.execute(old_program.read_text())
    assert [x['value'] for x in events if x['type']=='register']==[800,800]
    assert next(x for x in events if x['type']=='stats')['active_qubits']==4000
    combined.save(destination)
    usage=combined.metrics()
for name,path in sources.items(): assert sha(path)==originals[name],'input checkpoint was overwritten'
result={'ok':True,'source_checkpoints':{n:{'name':p.name,'sha256':originals[n]} for n,p in sources.items()},
        'models':models,'legacy_training_preserved':[800,800],
        'qubits_per_v3_agent':1000,'legacy_qubits':2000,'total_active_qubits':4000,
        'merged_checkpoint':destination.name,'merged_checkpoint_sha256':sha(destination),'usage':usage}
destination.with_suffix('.manifest.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result))
