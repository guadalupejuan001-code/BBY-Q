#!/usr/bin/env python3
"""Serial, alternating-order inference timing with the same frozen parameters.

This is a forward-only latency test. Full training is measured independently by
compare_topologies.py; the forward timings must not be called full-agent speed.
"""
import argparse
from datetime import datetime, timezone
from pathlib import Path
import statistics
import subprocess
from types import SimpleNamespace
import os
from compare_topologies import A, VARIANTS, experiment, publish, sha

p=argparse.ArgumentParser()
p.add_argument('--runtime',required=True)
p.add_argument('--output',required=True)
p.add_argument('--cpu',type=int,default=0)
p.add_argument('--rounds',type=int,default=5)
p.add_argument('--forwards',type=int,default=40)
args=p.parse_args()
os.sched_setaffinity(0,{args.cpu})
out=Path(args.output).resolve();out.mkdir(parents=True,exist_ok=True)
assert not (out/'benchmark.json').exists()
states={};experiments={};trials={v:[] for v in VARIANTS}
initials={}
for variant in VARIANTS:
    settings=SimpleNamespace(runtime=args.runtime,output=str(out/variant),variant=variant,
        agent='vqc',task='linear',seed=173,episodes=1,samples=1)
    m,e,birth=experiment(settings)
    empty=out/f'{variant}-empty.rvp'
    subprocess.run([str(e.cli),'init',str(empty)],check=True,capture_output=True)
    state=out/f'{variant}-frozen.rvp'
    with e.Session(e.binary,empty) as s:
        s.execute(birth+'\n'+e.lib)
        fixture=[]
        for q in range(1000):
            fixture += [f'fstore {A+300000+8*q} {0.71+0.003*(q%17):.17g}',
                        f'fstore {A+110000+8*q} {0.1+0.001*(q%7):.17g}']
        s.execute(e.source('\n'.join(fixture)+f'\nstore64 {A} 0\ncall select_agent'))
        initials[variant]=e.model_state(s)['parameter_sha256']
        s.save(state)
    states[variant]=state;experiments[variant]=e
assert len(set(initials.values()))==1
for repeat in range(args.rounds):
    order=VARIANTS[repeat%3:]+VARIANTS[:repeat%3]
    for variant in order:
        e=experiments[variant]
        before_hash=sha(states[variant])
        with e.Session(e.binary,states[variant]) as s:
            body=e.source('call forward\nfemit score f20')
            for _ in range(5):s.execute(body)
            before=s.metrics();times=[]
            for _ in range(args.forwards):
                events,elapsed=s.execute(body);times.append(elapsed)
            after=s.metrics()
        assert sha(states[variant])==before_hash
        trials[variant].append({'round':repeat,'forwards':args.forwards,
            'median_transport_ms':statistics.median(times),
            'cpu_ms_per_forward':(after['cpu_ms']-before['cpu_ms'])/args.forwards,
            'peak_rss_kib':after['peak_rss_kib'],'transport_ms':times})
summary={v:{'median_cpu_ms_per_forward':statistics.median(x['cpu_ms_per_forward'] for x in rows),
    'median_transport_ms':statistics.median(x['median_transport_ms'] for x in rows),
    'median_peak_rss_kib':statistics.median(x['peak_rss_kib'] for x in rows)} for v,rows in trials.items()}
report={'scope':'frozen single-agent forward only; not training or a complete QRL episode',
    'runtime_binary_sha256':sha(experiments['connected1000'].binary),'cpu_affinity':[args.cpu],
    'rounds':args.rounds,'forwards_per_round':args.forwards,'warmup_forwards_per_round':5,
    'identical_learned_parameters':initials,'alternating_variant_order':True,
    'trials':trials,'summary':summary,'completed_utc':datetime.now(timezone.utc).isoformat()}
publish(out/'benchmark.json',report)
print(__import__('json').dumps(summary,indent=2))
