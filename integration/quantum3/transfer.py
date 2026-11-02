#!/usr/bin/env python3
"""Zero-shot task/difficulty transfer; parameters remain unchanged."""
import argparse
import json
from pathlib import Path
from types import SimpleNamespace
from campaign import A, Experiment, sha

parser=argparse.ArgumentParser()
parser.add_argument('--runtime',required=True)
parser.add_argument('--session-binary')
parser.add_argument('--vqc-checkpoint',required=True)
parser.add_argument('--qrl-checkpoint',required=True)
parser.add_argument('--output',required=True)
args=parser.parse_args()
out=Path(args.output).resolve();out.parent.mkdir(parents=True,exist_ok=True)
options=SimpleNamespace(runtime=args.runtime,session_binary=args.session_binary,step_budget=100000000,
                        agent='vqc',task='linear',seed=173,episodes=1,eval_size=128,classical=False,
                        analytic=False,joint_mode='independent',initial_checkpoint=None,
                        output=str(out.parent/'transfer-fixture'),resume=False)
e=Experiment(options)
results={}
for task in ['linear','parity','radial','dense']:
    e.args.task=task
    results[task]=e.evaluate(Path(args.vqc_checkpoint).resolve())
    print(json.dumps({'trained_vqc':'linear','evaluation_task':task,'result':results[task]}),flush=True)
e.args.agent='qrl';e.args.eval_size=64
qrl={}
for task in ['line_easy','line_slip']:
    e.args.task=task
    qrl[task]=e.evaluate(Path(args.qrl_checkpoint).resolve(),'ood')
    print(json.dumps({'trained_qrl':'line_easy','evaluation_task':task,'result':qrl[task]}),flush=True)
summary={'no_parameter_updates':True,'vqc_trained_task':'linear','vqc_checkpoint_sha256':sha(args.vqc_checkpoint),
         'vqc_transfer':results,'qrl_trained_task':'line_easy','qrl_checkpoint_sha256':sha(args.qrl_checkpoint),
         'qrl_transfer':qrl}
out.write_text(json.dumps(summary,indent=2)+'\n')
