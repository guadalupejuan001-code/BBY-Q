#!/usr/bin/env python3
"""Same XI learning sequence through CLI checkpoints versus one session."""
import argparse
import json
from pathlib import Path
import statistics
import subprocess
import time
from types import SimpleNamespace
from campaign import Experiment, sha

parser=argparse.ArgumentParser()
parser.add_argument('--runtime',required=True)
parser.add_argument('--session-binary')
parser.add_argument('--checkpoint',required=True)
parser.add_argument('--episodes',type=int,default=30)
parser.add_argument('--output',required=True)
args=parser.parse_args();out=Path(args.output).resolve();out.mkdir(parents=True,exist_ok=True)
options=SimpleNamespace(runtime=args.runtime,session_binary=args.session_binary,step_budget=1000000,
                        agent='vqc',task='linear',seed=173,episodes=args.episodes,eval_size=1,
                        classical=False,analytic=False,joint_mode='independent',initial_checkpoint=None,
                        output=str(out/'fixture'),resume=False)
e=Experiment(options);initial=Path(args.checkpoint).resolve()
sources=[e.source(e.stage('train',i,training=True)) for i in range(args.episodes)]
cli_times=[];state=initial
for i,source in enumerate(sources):
    program=out/f'step-{i:03}.xi';program.write_text(source)
    destination=out/f'cli-{i:03}.rvp'
    started=time.perf_counter_ns()
    subprocess.run([e.cli,'run',program,state,destination],check=True,capture_output=True)
    cli_times.append((time.perf_counter_ns()-started)/1e6);state=destination
with e.Session(e.binary,state) as session:
    cli_model=e.model_state(session)
session_times=[]
with e.Session(e.binary,initial) as session:
    for source in sources:
        _,elapsed=session.execute(source);session_times.append(elapsed)
    persistent_model=e.model_state(session)
    destination=out/'persistent-final.rvp'
    session.save(destination)
    usage=session.metrics()
assert cli_model==persistent_model,'transport optimization changed learning parameters'
same_bytes=sha(state)==sha(destination)
result={'episodes':args.episodes,'same_xi_source_sequence':True,'parameters_identical':True,
        'final_checkpoint_bytes_identical':same_bytes,'parameter_sha256':cli_model['parameter_sha256'],
        'cli_median_ms':statistics.median(cli_times),'persistent_median_ms':statistics.median(session_times),
        'cli_total_ms':sum(cli_times),'persistent_total_ms':sum(session_times),
        'median_speed_ratio':statistics.median(cli_times)/statistics.median(session_times),
        'persistent_usage':usage,'cli_samples_ms':cli_times,'persistent_samples_ms':session_times}
(out/'summary.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result))
