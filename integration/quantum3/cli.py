#!/usr/bin/env python3
"""Usable model interface: input/JSON/checkpoint transport only."""
import argparse
import json
import math
from pathlib import Path
import sys
from types import SimpleNamespace
from campaign import A, XI, Experiment, metrics, sha

parser=argparse.ArgumentParser(description='VQC3/QRL3 native XI models, 1000 functional qubits each')
parser.add_argument('--runtime',required=True)
parser.add_argument('--session-binary')
parser.add_argument('--state',required=True)
parser.add_argument('--seed',type=int,default=173)
commands=parser.add_subparsers(dest='command',required=True)
commands.add_parser('info')
classify=commands.add_parser('classify')
classify.add_argument('--inputs',required=True,help='JSON array of 1000 normalized numbers, or - for stdin')
train=commands.add_parser('learn-class')
train.add_argument('--inputs',required=True)
train.add_argument('--label',type=int,choices=[0,1],required=True)
train.add_argument('--output',required=True)
act=commands.add_parser('act')
act.add_argument('--position',type=int,choices=range(7),required=True)
act.add_argument('--goal',type=int,choices=range(7),required=True)
act.add_argument('--greedy',action='store_true')
episode=commands.add_parser('learn-episode')
episode.add_argument('--slip',type=float,default=.15)
episode.add_argument('--horizon',type=int,default=12)
episode.add_argument('--output',required=True)
args=parser.parse_args()
if not 0<=args.seed<2147483648:
    parser.error('seed must be 0..2147483647')
if args.command=='learn-episode' and (not math.isfinite(args.slip) or not 0<=args.slip<=1 or args.horizon<1):
    parser.error('slip must be a probability and horizon must be positive')
if getattr(args,'output',None) and Path(args.output).exists():
    parser.error('output already exists; previous checkpoints are preserved')
state=Path(args.state).resolve();original=sha(state)
options=SimpleNamespace(runtime=args.runtime,session_binary=args.session_binary,step_budget=100000000,
                        agent='vqc',task='linear',seed=args.seed,episodes=1,eval_size=1,classical=False,
                        analytic=False,joint_mode='independent',initial_checkpoint=None,
                        output=str(state.parent/'cli-transport'),resume=False)
e=Experiment(options)
e.lib+='\n'+(XI/'encode-input.xi').read_text()
prefix=f'''load8 r0 {A+1000}
cmp r0 173
je valid_v3_checkpoint
div r0 0
label valid_v3_checkpoint
store64 {A+256} {args.seed}
store64 {A+280} 0
'''
with e.Session(e.binary,state) as session:
    if args.command=='info':
        session.execute(e.source(prefix))
        data={}
        for agent in ['vqc','qrl']:
            e.args.agent=agent;data[agent]=e.model_state(session)
        data['runtime']=session.metrics()
    else:
        if args.command in ['classify','learn-class']:
            raw=sys.stdin.read() if args.inputs=='-' else Path(args.inputs).read_text()
            values=json.loads(raw)
            if not isinstance(values,list) or len(values)!=1000 or any(isinstance(v,bool) or
                not isinstance(v,(int,float)) or not math.isfinite(v) for v in values):
                parser.error('inputs must be exactly 1000 finite numeric values')
            prefix+='\n'.join(f'fstore {A+300000+8*i} {float(v):.17g}' for i,v in enumerate(values))+'\ncall encode_external_input\n'
            if args.command=='classify':
                body=(XI/'vqc3-infer.xi').read_text().split('\n',1)[1]
            else:
                body=f'store64 {A} 0\nfstore {A+128} {args.label}\ncall supervised_update'
        elif args.command=='act':
            prefix+=f'''store64 {A+344} {args.position}
store64 {A+352} {args.goal}
store64 {A+360} 0
store64 {A+312} 12
store64 {A+320} {2 if args.greedy else 1}
call qrl_observe
'''
            body=(XI/'qrl3-act.xi').read_text().split('\n',1)[1]
        else:
            body=f'''fstore {A+304} {args.slip:.17g}
store64 {A+312} {args.horizon}
store64 {A+320} 0
store64 {A+328} 0
store64 {A+336} 0
call qrl_episode'''
        events,elapsed=session.execute(e.source(prefix+'\n'+body))
        data=dict(metrics(events),elapsed_ms=elapsed,qubits_used_by_agent=1000)
        if getattr(args,'output',None):
            session.save(args.output)
            data.update(checkpoint=str(Path(args.output).resolve()),checkpoint_sha256=sha(args.output))
assert sha(state)==original,'input checkpoint changed'
print(json.dumps(data,ensure_ascii=False,indent=2))
