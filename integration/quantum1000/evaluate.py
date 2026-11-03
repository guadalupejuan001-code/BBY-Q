#!/usr/bin/env python3
"""Fresh evaluation seeds after architecture selection; no model updates."""
import argparse
import json
from pathlib import Path
from types import SimpleNamespace
from campaign import A, Experiment, sample_seed, sha

p=argparse.ArgumentParser()
p.add_argument('--runtime',required=True)
p.add_argument('--trained',required=True)
p.add_argument('--initial',required=True)
p.add_argument('--agent',choices=['vqc','qrl'],required=True)
p.add_argument('--task',required=True)
p.add_argument('--samples',type=int,default=64)
p.add_argument('--seed',type=int,default=20261103)
p.add_argument('--training-seed',type=int,default=173)
p.add_argument('--training-episodes',type=int,default=1000)
p.add_argument('--output',required=True)
args=p.parse_args()
out=Path(args.output).resolve()
if out.exists():p.error('output exists; retain the previous evaluation')
train={sample_seed(args.training_seed,'train',i) for i in range(args.training_episodes)}
test={sample_seed(args.seed,split,i) for split in ['iid','ood'] for i in range(args.samples)}
assert not train & test,'train/test seed overlap'
e=Experiment(SimpleNamespace(runtime=args.runtime,session_binary=None,step_budget=10000000,
    agent=args.agent,task=args.task,seed=args.seed,episodes=1,eval_size=args.samples,
    classical=False,output=str(out.parent/'evaluation-transport'),resume=False))
paths={name:Path(getattr(args,name)).resolve() for name in ['trained','initial']}
originals={name:sha(path) for name,path in paths.items()}
flags=[]
for path in paths.values():
    with e.Session(e.binary,path) as s:
        events,_=s.execute(e.source(f'load8 r0 {A+1000}\ncmp r0 174\nje connected_evaluation\ndiv r0 0\nlabel connected_evaluation\nload64 r0 {A+1008}\nprint r0'))
        flags.append(next(x['value'] for x in events if x['type']=='register'))
assert flags[0]==flags[1] and flags[0] in [0,1]
result={'agent':args.agent,'task':args.task,'samples_per_split':args.samples,
    'entangler':'cz' if flags[0] else 'cnot',
    'evaluation_seed':args.seed,'training_seed':args.training_seed,
    'training_seed_overlap':False,'model_update':False,
    'source_checkpoints':{name:{'name':path.name,'sha256':originals[name]} for name,path in paths.items()}}
for name,path in paths.items():
    result[name]={'iid':e.evaluate(path),'ood':e.evaluate(path,'ood')}
result['observations_zeroed']={'iid':e.evaluate(paths['trained'],ablate=True),'ood':e.evaluate(paths['trained'],'ood',ablate=True)}
if args.agent=='qrl':
    result['random_policy']={'iid':e.evaluate(paths['initial'],random=True),'ood':e.evaluate(paths['initial'],'ood',random=True)}
    result['greedy_policy']={'iid':e.evaluate(paths['trained'],greedy=True),'ood':e.evaluate(paths['trained'],'ood',greedy=True)}
for name,path in paths.items():assert sha(path)==originals[name],'evaluation changed checkpoint'
out.parent.mkdir(parents=True,exist_ok=True)
out.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
