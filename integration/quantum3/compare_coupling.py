#!/usr/bin/env python3
"""Matched 32-case evaluations for independent/frozen/alternating QRL."""
import argparse
import json
from pathlib import Path
from types import SimpleNamespace
from campaign import Experiment, sha

parser=argparse.ArgumentParser()
parser.add_argument('--runtime',required=True)
parser.add_argument('--session-binary')
parser.add_argument('--independent',required=True)
parser.add_argument('--frozen',required=True)
parser.add_argument('--joint',required=True)
parser.add_argument('--output',required=True)
args=parser.parse_args();out=Path(args.output).resolve();out.parent.mkdir(parents=True,exist_ok=True)
results=[]
for mode in ['independent','frozen','joint']:
    checkpoint=Path(getattr(args,mode)).resolve()
    options=SimpleNamespace(runtime=args.runtime,session_binary=args.session_binary,step_budget=100000000,
                            agent='qrl',task='line_easy',seed=173,episodes=1,eval_size=32,classical=False,
                            analytic=False,joint_mode=mode,initial_checkpoint=None,
                            output=str(out.parent/'coupling-evaluation-fixture'),resume=False)
    e=Experiment(options)
    with e.Session(e.binary,checkpoint) as session:
        before=e.model_state(session)
    item={'mode':mode,'checkpoint_sha256':sha(checkpoint),'model':before,
          'iid':e.evaluate(checkpoint),'ood':e.evaluate(checkpoint,'ood'),
          'greedy_iid':e.evaluate(checkpoint,greedy=True),'greedy_ood':e.evaluate(checkpoint,'ood',greedy=True)}
    results.append(item)
    print(json.dumps(item),flush=True)
    out.write_text(json.dumps({'examples_per_split':32,'same_evaluation_seeds':True,
                              'training_episodes_per_policy':1000,'results':results},indent=2)+'\n')
