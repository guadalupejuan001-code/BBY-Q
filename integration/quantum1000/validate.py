#!/usr/bin/env python3
"""Connected registers, exact measured gradients, updates, rollback and resume."""
import argparse
import json
from pathlib import Path
import struct
import subprocess
from types import SimpleNamespace
from campaign import A, XI, Experiment, metrics, sha

p=argparse.ArgumentParser()
p.add_argument('--runtime',required=True)
p.add_argument('--output',required=True)
args=p.parse_args()
out=Path(args.output).resolve();out.mkdir(parents=True,exist_ok=True)
e=Experiment(SimpleNamespace(runtime=args.runtime,session_binary=None,step_budget=10000000,
    agent='vqc',task='linear',seed=173,episodes=12,eval_size=8,classical=False,
    output=str(out/'transport'),resume=False))
empty=out/'empty.rvp'
if not empty.exists():subprocess.run([e.cli,'init',empty],check=True,capture_output=True)
checks=[]
def require(ok,name):
    if not ok:raise AssertionError(name)
    checks.append(name)
def materialize(s,address,count,code=''):
    events,_=s.execute(e.source(code+f'\nmem_materialize {address} {8*count}'))
    raw=bytes.fromhex(next(x['hex'] for x in events if x['type']=='memory_materialization'))
    return struct.unpack('<'+'d'*count,raw)

base=out/'birth.rvp'
with e.Session(e.binary,empty) as s:
    s.execute((XI/'birth.xi').read_text()+'\n'+e.lib)
    s.save(base)
    stage=[]
    for q in range(1000):
        stage += [f'fstore {A+300000+8*q} {.008+.00001*(q%11):.17g}',
                  f'fstore {A+110000+8*q} {.4+.013*(q%7):.17g}']
    s.execute(e.source('\n'.join(stage)))
    code='store64 '+str(A)+' 0\ncall select_agent\ncall forward'
    gradients=materialize(s,A+130000,1000,code)
    require(all(abs(g)>1e-6 for g in gradients),'all 1000 angle derivatives affect the learned score')
    errors=[]
    for q in [0,3,4,7,8,127,499,500,998,999]:
        values=[]
        for delta in [1e-5,-1e-5]:
            events,_=s.execute(e.source(f'fstore {A+100000+8*q} {.31+delta:.17g}\n'+code+'\nfemit score f20'))
            values.append(metrics(events)['score'])
        s.execute(e.source(f'fstore {A+100000+8*q} .31'))
        error=abs((values[0]-values[1])/2e-5-gradients[q]);errors.append(error)
        require(error<1e-7,f'full-score finite-difference gradient at wire {q}')
    # A feature at the first wire changes a measurement at the last wire.
    remote=[]
    for value in [.008,.108]:
        events,_=s.execute(e.source(f'fstore {A+300000} {value}\n'+code+'\nfexpect f0 Z:5999\nfemit remote f0'))
        remote.append(metrics(events)['remote'])
    require(abs(remote[0]-remote[1])>1e-4,'causal influence from wire 0 to wire 999')
    clipped=materialize(s,A+130000,1000,f'fstore {A+4016} 100\n'+code)
    require(all(g==0 for g in clipped),'saturated logit clamp has zero angle derivatives')
    s.execute(e.source(f'fstore {A+4016} 0'))
    events,_=s.execute(e.source('qtrace reset\n'+code+'\nstore64 '+str(A)+' 1\ncall select_agent\ncall forward\nqtrace report\nqmpsinfo 5000\nqmpsinfo 7000\nstats'))
    trace=next(x for x in events if x['type']=='quantum_trace')
    registers=[x for x in events if x['type']=='mps_register']
    stats=next(x for x in events if x['type']=='stats')
    require(trace['preparations']==2 and trace['max_prepared_block']==1000,'two complete register preparations, with no 4-wire resets')
    require(trace['distinct_rotated_qubits']==trace['distinct_observed_qubits']==2000,'all 1000 wires in each agent rotate and are observed')
    require(trace['distinct_two_qubit_edges']==1998,'999 distinct neighbour connections per agent')
    require(stats['components']==2 and stats['largest_component']==1000,'one quantum component per agent')
    require(all(r['nonproduct_bipartitions']==999 for r in registers),'both registers entangled across all 999 cuts')
    unchanged=out/'entangled.rvp';s.save(unchanged)
    before=e.model_state(s)
    for bad in ['fstore '+str(A+110000)+' 99\ndiv r0 0','qmps 5000 4']:
        try:s.execute(e.source(bad))
        except RuntimeError:pass
        else:raise AssertionError('invalid operation unexpectedly accepted')
        require(e.model_state(s)==before,'failed update or partial reset cannot change learned parameters')
    probs=[]
    for label in [0,1]:
        events,_=s.execute(e.source(f'fstore {A+128} {label}\n'+code+'\nfemit probability f21'))
        probs.append(metrics(events)['probability'])
    require(probs[0]==probs[1],'hidden labels do not influence inference')

with e.Session(e.binary,unchanged) as s:
    events,_=s.execute(e.source('qmpsinfo 5000\nqmpsinfo 7000'))
    restored=[x for x in events if x['type']=='mps_register']
    require(restored==registers,'entangled MPS states round-trip exactly through Ether checkpoint')

trained={}
for agent,task in [('vqc','linear'),('qrl','line_easy')]:
    e.args.agent=agent;e.args.task=task;digests=[]
    for resume in [False,True]:
        state=base
        for start,end in ([(0,12)] if not resume else [(0,6),(6,12)]):
            with e.Session(e.binary,state) as s:
                episodes=[]
                for i in range(start,end):
                    events,_=s.execute(e.source(e.stage('train',i,training=True)))
                    episodes.append(metrics(events))
                model=e.model_state(s)
                if resume and end==6:
                    state=out/f'{agent}-resume-at-6.rvp';s.save(state)
                else:digests.append(model['parameter_sha256'])
    require(digests[0]==digests[1],f'{agent} uninterrupted and resumed learning have identical parameters')
    require(model['training_episodes_in_checkpoint']==12,f'{agent} executed twelve real training episodes')
    require(model['rotation_parameters_changed']==model['readout_parameters_changed']==1000,f'{agent} trained all 1000 angles and all 1000 readout weights')
    if agent=='qrl':
        require(all(3<=r['decisions']<=8 for r in episodes),'QRL uses sequential decisions with terminal rewards')
        require(all(abs(r['reward']-(r['success']-.02*r['decisions']))<1e-12 for r in episodes),'QRL rewards agree with actual trajectories')
    trained[agent]=model

report={'ok':True,'checks':checks,'max_finite_difference_error':max(errors),
    'first_to_last_observation_change':abs(remote[0]-remote[1]),'trace':trace,
    'registers':registers,'trained':trained,'runtime_sha256':sha(e.binary),
    'classical_simulation':True,'truncation':False}
(out/'validation.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({'ok':True,'checks':len(checks),'maximum_gradient_error':max(errors),'trained':trained},indent=2))
