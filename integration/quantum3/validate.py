#!/usr/bin/env python3
"""Run the real XI agents; check gradients, causal width and resume identity."""
import argparse
import hashlib
import json
from pathlib import Path
import struct
import subprocess
import sys
from types import SimpleNamespace

from campaign import A, XI, Experiment, metrics, sha

parser=argparse.ArgumentParser()
parser.add_argument('--runtime',required=True)
parser.add_argument('--session-binary')
parser.add_argument('--output',required=True)
parser.add_argument('--legacy-checkpoint')
args=parser.parse_args()
out=Path(args.output).resolve();out.mkdir(parents=True,exist_ok=True)
options=SimpleNamespace(runtime=args.runtime,session_binary=args.session_binary,step_budget=10000000,
                        agent='vqc',task='linear',seed=173,episodes=20,eval_size=8,
                        classical=False,output=str(out/'fixture'),resume=False)
experiment=Experiment(options)
empty=out/'empty.rvp'
if not empty.exists(): subprocess.run([experiment.cli,'init',empty],check=True)
checks=0
grad_errors=[]

def require(condition, message):
    global checks
    assert condition,message
    checks+=1

with experiment.Session(experiment.binary,empty) as session:
    events,_=session.execute((XI/'birth.xi').read_text()+'\n'+experiment.lib)
    require(next(x for x in events if x['type']=='stats')['active_qubits']==2000,'both registers initialized')
    base=out/'birth.rvp'
    if base.exists(): base.unlink()
    session.save(base)
    # Stage independent nonzero readout weights and angles as test inputs.
    stage=[]
    for q in range(1000):
        stage += [f'fstore {A+300000+8*q} {.6+.017*(q%31):.17g}',
                  f'fstore {A+110000+8*q} {.02+.013*(q%7):.17g}']
    session.execute(experiment.source('\n'.join(stage)))
    source=f'store64 {A} 0\ncall select_agent\nset r9 0\ncall selected_gradients\nmem_materialize {A+130000} 32'
    events,_=session.execute(experiment.source(source))
    calculated=struct.unpack('<4d',bytes.fromhex(next(x['hex'] for x in events if x['type']=='memory_materialization')))
    for q,g in enumerate(calculated):
        observed=[]
        for shift in [1e-5,-1e-5]:
            source=f'fstore {A+100000+8*q} {.31+shift:.17g}\ncall select_agent\ncall forward\nfemit score f20'
            events,_=session.execute(experiment.source(source));observed.append(metrics(events)['score'])
        session.execute(experiment.source(f'fstore {A+100000+8*q} 0.31'))
        finite=(observed[0]-observed[1])/2e-5
        error=abs(g-finite);grad_errors.append(error)
        require(error<1e-7,'XI exact local parameter shift matches independent full-score finite difference')
        require(abs(g)>1e-6,'selected rotation affects classifier output')
    events,_=session.execute(experiment.source(f'qtrace reset\nstore64 {A} 0\ncall select_agent\ncall forward\nstore64 {A} 1\ncall select_agent\ncall forward\nqtrace report'))
    trace=next(x for x in events if x['type']=='quantum_trace')
    require(trace['distinct_observed_qubits']==trace['distinct_rotated_qubits']==trace['active_qubits']==2000,'all wires participate')
    before=experiment.model_state(session)
    try:
        session.execute(experiment.source(f'fstore {A+110000} 99\ndiv r0 0'))
        raise AssertionError('bad update committed')
    except RuntimeError:
        pass
    require(before==experiment.model_state(session),'failed update leaves learned parameters unchanged')

# Identical data order, uninterrupted versus save/restore, excludes timing
# scratch bytes from the SHA. This verifies actual parameter/optimizer state.
digests=[]
for resumed in [False,True]:
    current=base
    for start,end in ([(0,10)] if not resumed else [(0,5),(5,10)]):
        with experiment.Session(experiment.binary,current) as session:
            for ep in range(start,end):
                session.execute(experiment.source(experiment.stage('train',ep,training=True)))
            final=experiment.model_state(session)
            if resumed and end==5:
                current=out/'resume-at-5.rvp'
                if current.exists(): current.unlink()
                session.save(current)
            else:
                digests.append(final['parameter_sha256'])
require(digests[0]==digests[1],'checkpoint resume is bit-identical for VQC parameters and optimizer state')
require(final['readout_parameters_changed']==1000,'all VQC readout weights actually updated')
require(final['rotation_parameters_updated']>0,'VQC continuous rotations actually trained')

# Native multi-step RL with terminal return and quantum-dependent actions.
experiment.args.agent='qrl';experiment.args.task='line_easy'
with experiment.Session(experiment.binary,base) as session:
    episodes=[]
    for ep in range(12):
        events,_=session.execute(experiment.source(experiment.stage('train',ep,training=True)))
        episodes.append(metrics(events))
    state=experiment.model_state(session)
    require(state['training_episodes_in_checkpoint']==12,'twelve real RL episodes')
    require(state['training_decisions_in_checkpoint']>=36,'sequential decisions, not a contextual one-step bandit')
    require(state['readout_parameters_changed']==1000,'RL measured features change all readout weights')
    require(state['rotation_parameters_updated']>0,'RL return updates continuous circuit parameters')
    require(all(3<=r['decisions']<=8 for r in episodes),'observable environment episodes obey horizon')
    require(all(abs(r['reward']-(r['success']-.02*r['decisions']))<1e-12 for r in episodes),'terminal returns agree with trajectories')

legacy=None
if args.legacy_checkpoint:
    original=Path(args.legacy_checkpoint).resolve();digest=sha(original)
    with experiment.Session(experiment.binary,original) as session:
        session.execute((XI/'birth.xi').read_text()+'\n'+experiment.lib)
        old=Path(__file__).resolve().parents[2]/'ai/xi/qml_qrl/agents1000-audit.xi'
        events,_=session.execute(old.read_text())
        counts=[x['value'] for x in events if x['type']=='register']
        require(counts==[800,800],'older GHZ training remains 800/800')
        require(next(x for x in events if x['type']=='stats')['active_qubits']==4000,'old and new registers coexist')
        legacy=out/'legacy-plus-v3.rvp'
        if legacy.exists(): legacy.unlink()
        session.save(legacy)
    require(sha(original)==digest,'original trained checkpoint bytes preserved')
    legacy={'input_sha256':digest,'combined_sha256':sha(legacy),'active_qubits':4000}
summary={'ok':True,'checks':checks,'parameter_shift_max_absolute_error':max(grad_errors),
         'trace':trace,'resume_parameter_sha256':digests[0],'qrl_test':state,'legacy':legacy}
(out/'summary.json').write_text(json.dumps(summary,indent=2)+'\n')
print(json.dumps(summary))
