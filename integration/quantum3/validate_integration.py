#!/usr/bin/env python3
"""Execute both coupling modes and the planner, checking model isolation."""
import argparse
import json
from pathlib import Path
from types import SimpleNamespace
from campaign import A, XI, Experiment

parser=argparse.ArgumentParser()
parser.add_argument('--runtime',required=True)
parser.add_argument('--session-binary')
parser.add_argument('--checkpoint',required=True)
parser.add_argument('--output',required=True)
args=parser.parse_args()
out=Path(args.output).resolve();out.parent.mkdir(parents=True,exist_ok=True)
results=[]
for mode in ['frozen','joint']:
    options=SimpleNamespace(runtime=args.runtime,session_binary=args.session_binary,step_budget=100000000,
                            agent='qrl',task='line_easy',seed=173,episodes=3,eval_size=8,
                            classical=False,analytic=False,joint_mode=mode,output=str(out.parent/'coupling-fixture'),
                            resume=False,initial_checkpoint=None)
    e=Experiment(options)
    with e.Session(e.binary,Path(args.checkpoint).resolve()) as session:
        e.args.agent='vqc';before=e.model_state(session);e.args.agent='qrl'
        qbefore=e.model_state(session)
        for ep in range(3):
            events,_=session.execute(e.source('qtrace reset\n'+e.stage('train',ep,training=True)+'\nqtrace report'))
        trace=next(x for x in events if x['type']=='quantum_trace')
        e.args.agent='vqc';after=e.model_state(session);e.args.agent='qrl'
        qafter=e.model_state(session)
        assert trace['distinct_observed_qubits']==trace['distinct_rotated_qubits']==2000
        assert qafter['training_episodes_in_checkpoint']==qbefore['training_episodes_in_checkpoint']+3
        if mode=='frozen':
            assert before==after,'frozen VQC changed during RL training'
        else:
            assert after['training_episodes_in_checkpoint']==before['training_episodes_in_checkpoint']+3
            assert before['parameter_sha256']!=after['parameter_sha256'],'joint VQC did not train'
    results.append({'mode':mode,'before':before,'after':after,'qrl_after':qafter,'trace':trace})

e.args.joint_mode='independent';e.args.agent='qrl'
e.lib='\n'.join((XI/f).read_text() for f in ['common.xi','benchmarks.xi','qrl3-planning.xi','planning.xi'])
with e.Session(e.binary,Path(args.checkpoint).resolve()) as session:
    before=e.model_state(session)
    body=e.stage('ood',0).replace('call qrl_episode',f'store64 {A+320} 4\ncall qrl_episode')
    events,_=session.execute(e.source(body))
    assert before==e.model_state(session),'planning evaluation changed trained parameters'
    assert any(x.get('name')=='success' for x in events)
summary={'ok':True,'coupling_modes':results,'planner_executed_in_xi':True,'planner_preserved_model':True,
         'end_to_end_joint_gradient':False}
out.write_text(json.dumps(summary,indent=2)+'\n')
print(json.dumps(summary))
