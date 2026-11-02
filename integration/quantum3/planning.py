#!/usr/bin/env python3
"""Evaluate the XI rollout planner; never train or change the supplied model."""
import argparse
import json
from pathlib import Path
import statistics
from types import SimpleNamespace
from campaign import A, XI, Experiment, metrics, sha, wilson

parser=argparse.ArgumentParser()
parser.add_argument('--runtime',required=True)
parser.add_argument('--session-binary')
parser.add_argument('--checkpoint',action='append',required=True)
parser.add_argument('--samples',type=int,default=32)
parser.add_argument('--output',required=True)
args=parser.parse_args()
out=Path(args.output).resolve();out.parent.mkdir(parents=True,exist_ok=True)
options=SimpleNamespace(runtime=args.runtime,session_binary=args.session_binary,step_budget=100000000,
                       agent='qrl',task='line_easy',seed=173,episodes=1,eval_size=args.samples,
                       classical=False,output=str(out.parent/'planner-fixture'),resume=False)
e=Experiment(options)
e.lib='\n'.join((XI/f).read_text() for f in ['common.xi','benchmarks.xi','qrl3-planning.xi','planning.xi'])
results=[]
for checkpoint in args.checkpoint:
    values=[]
    with e.Session(e.binary,Path(checkpoint).resolve()) as session:
        before=e.model_state(session)
        for i in range(args.samples):
            stage=e.stage('ood',i).replace('call qrl_episode',f'store64 {A+320} 4\ncall qrl_episode')
            events,elapsed=session.execute(e.source(stage))
            values.append(dict(metrics(events),transport_ms=elapsed))
        assert before==e.model_state(session),'planner changed learned parameters'
        usage=session.metrics()
    success=sum(x['success'] for x in values)
    item={'checkpoint':str(checkpoint),'checkpoint_sha256':sha(checkpoint),'success_rate':success/args.samples,
          'wilson95':wilson(success,args.samples),'mean_reward':statistics.mean(x['reward'] for x in values),
          'mean_decisions':statistics.mean(x['decisions'] for x in values),
          'median_episode_ms':statistics.median(x['episode_ms'] for x in values),
          'usage':usage,'raw_episodes':values}
    results.append(item)
    print(json.dumps({k:v for k,v in item.items() if k!='raw_episodes'}),flush=True)
    out.write_text(json.dumps({'known_transition_model':True,'learned_dynamics':False,
                              'lookahead_depth':3,'rollouts_per_candidate_action':2,
                              'rollout_policy_qubits':1000,'results':results},indent=2)+'\n')
