#!/usr/bin/env python3
"""Verify the blocked control before comparing learning or speed."""
import argparse
import json
from pathlib import Path
import struct
import subprocess
from types import SimpleNamespace
from compare_topologies import A, VARIANTS, experiment, publish, sha, structure_probe

p = argparse.ArgumentParser()
p.add_argument('--runtime', required=True)
p.add_argument('--output', required=True)
args = p.parse_args()
out = Path(args.output).resolve()
out.mkdir(parents=True, exist_ok=True)
checks, errors, outputs, initials = [], {}, {}, {}
for variant in VARIANTS:
    settings = SimpleNamespace(runtime=args.runtime, output=str(out/variant), variant=variant,
        agent='vqc', task='linear', seed=173, episodes=2, samples=4)
    m, e, birth = experiment(settings)
    empty = out/f'{variant}-empty.rvp'
    subprocess.run([str(e.cli),'init',str(empty)],check=True,capture_output=True)
    base = out/f'{variant}-base.rvp'
    with e.Session(e.binary,empty) as s:
        s.execute(birth+'\n'+e.lib)
        initials[variant] = e.model_state(s)['parameter_sha256']
        s.save(base)
    structural = structure_probe(e, base, variant)
    checks.append(variant+': all 2,000 wires, component counts and edge counts verified')
    with e.Session(e.binary,base) as s:
        fixture = []
        for q in range(1000):
            fixture += [f'fstore {A+300000+8*q} {0.71+0.003*(q%17):.17g}',
                        f'fstore {A+110000+8*q} {0.1+0.001*(q%7):.17g}']
        s.execute(e.source('\n'.join(fixture)))
        code = f'store64 {A} 0\ncall select_agent\ncall forward'
        if variant != 'historical4':
            events,_=s.execute(e.source(code+f'\nmem_materialize {A+130000} 8000'))
            raw=bytes.fromhex(next(x['hex'] for x in events if x['type']=='memory_materialization'))
            gradients=struct.unpack('<1000d',raw)
            assert all(abs(x)>1e-8 for x in gradients)
            deltas=[]
            for q in [0,3,4,499,500,998,999]:
                values=[]
                for delta in [1e-5,-1e-5]:
                    events,_=s.execute(e.source(f'fstore {A+100000+8*q} {.31+delta:.17g}\n'+code+'\nfemit score f20'))
                    values.append(m.metrics(events)['score'])
                s.execute(e.source(f'fstore {A+100000+8*q} .31'))
                deltas.append(abs((values[0]-values[1])/2e-5-gradients[q]))
            assert max(deltas)<1e-7
            errors[variant]=max(deltas)
            checks.append(variant+': all 1,000 score gradients nonzero; boundary/interior finite differences agree')
        # With CNOT selected, the new blocked control must reproduce the actual
        # historical model's 1,000 observations and probability, not merely fit.
        if variant in ['historical4','blocked4']:
            if variant=='blocked4':
                s.execute(e.source(f'store64 {A+1008} 0'))
            events,_=s.execute(e.source(code+f'\nfemit score f20\nmem_materialize {A+310000} 8000'))
            raw=bytes.fromhex(next(x['hex'] for x in events if x['type']=='memory_materialization'))
            outputs[variant]={'score':m.metrics(events)['score'],'observations':struct.unpack('<1000d',raw)}
    # Use disjoint unsaved sessions to verify the control itself resumes exactly.
    if variant=='blocked4':
        end_hashes=[]
        for split in [False,True]:
            state=base
            for start,end in ([(0,2)] if not split else [(0,1),(1,2)]):
                with e.Session(e.binary,state) as s:
                    for i in range(start,end):s.execute(e.source(e.stage('train',i,training=True)))
                    if split and end==1:
                        state=out/'blocked4-resume-at-1.rvp';s.save(state)
                    else:end_hashes.append(e.model_state(s)['parameter_sha256'])
        assert end_hashes[0]==end_hashes[1]
        checks.append('blocked4: uninterrupted and resumed native learning have identical parameters')

assert len(set(initials.values()))==1
checks.append('all three variants have identical initial learned parameters and optimizer metadata')
max_observation_error=max(abs(x-y) for x,y in zip(outputs['historical4']['observations'],outputs['blocked4']['observations']))
score_error=abs(outputs['historical4']['score']-outputs['blocked4']['score'])
assert max_observation_error<1e-12 and score_error<1e-12
checks.append('blocked4/CNOT reproduces the historical 1,000 observables and score')
result={'ok':True,'checks':checks,'maximum_gradient_errors':errors,
    'historical_cnot_observation_error':max_observation_error,'historical_cnot_score_error':score_error,
    'initial_parameter_hashes':initials,'runtime_binary_sha256':sha(e.binary)}
publish(out/'validation.json',result)
print(json.dumps(result,indent=2))
