#!/usr/bin/env python3
"""Interleaved native session timing with the same authentic checkpoint for all.

Compact variants have identical outputs. Conversation does extra realization;
its timings describe the new task and are not advertised as a speedup.
"""
import argparse
import hashlib
import json
from pathlib import Path
import random
import statistics
import subprocess
import sys

REPO=Path(__file__).resolve().parents[4]
sys.path.insert(0,str(REPO/'ai/native'))
from session_client import Session,decode_result

CASES=[
    ('direct','qué es neurona?','neurona es célula.','Una neurona es una célula.'),
    ('inferred','gato es organismo?','gato es organismo. [gato -> mamífero -> vertebrado -> organismo]',
     'Un gato es un organismo. [gato -> mamífero -> vertebrado -> organismo]'),
    ('quantity','cuántas manzanas tiene ana?','cinco','Ana tiene cinco manzanas.'),
    ('arithmetic','dos mas tres','cinco','El resultado es cinco.'),
    ('unknown','bbyq tiene conciencia?','?','No tengo información suficiente para responder.'),
]


def summary(values):
    return {'n':len(values),'median_ms':statistics.median(values),
            'p95_ms':sorted(values)[max(0,(len(values)*95+99)//100-1)]}


def main():
    ap=argparse.ArgumentParser();ap.add_argument('binary');ap.add_argument('baseline_root');ap.add_argument('checkpoint')
    ap.add_argument('--out',default='evidence/e016-performance');ap.add_argument('--repeats',type=int,default=40)
    ap.add_argument('--baseline-name',default='e015_compact')
    ap.add_argument('--candidate-name',default='e016_compact')
    ap.add_argument('--conversation-name',default='e016_conversation')
    args=ap.parse_args();out=Path(args.out).resolve();out.mkdir(parents=True,exist_ok=True)
    checkpoint=Path(args.checkpoint).read_bytes();binary=Path(args.binary).resolve()
    variants={args.baseline_name:(Path(args.baseline_root).resolve(),'combined',2),
              args.candidate_name:(REPO,'combined',2),args.conversation_name:(REPO,'conversation',3)}
    active={};times={};raw=[];program_hashes={}
    try:
        for label,(root,mode,index) in variants.items():
            state=out/(label+'.rvp');state.write_bytes(checkpoint)
            program=out/(label+'.xi');program.write_bytes(subprocess.check_output(['bash',str(root/'ai/xi/knowledge/link.sh'),mode]))
            program_hashes[label]=hashlib.sha256(program.read_bytes()).hexdigest()
            active[label]=Session(binary,state,program);times[label]={case[0]:[] for case in CASES}
            value,_=active[label].request('ana tiene cinco manzanas')
            assert decode_result(value)==('Ana tiene cinco manzanas.' if index==3 else 'cinco')
            for _ in range(3):active[label].request(CASES[0][1])
        rng=random.Random(160629)
        for iteration in range(args.repeats):
            order=[(label,case) for label in variants for case in CASES];rng.shuffle(order)
            for label,case in order:
                value,ms=active[label].request(case[1]);assert decode_result(value)==case[variants[label][2]]
                times[label][case[0]].append(ms);raw.append({'variant':label,'case':case[0],'iteration':iteration,'ms':ms})
        result={'method':'native resident sessions; same checkpoint; randomized interleaving seed 160629; commit before ACK; oracle outside timing',
                'checkpoint_sha256':hashlib.sha256(checkpoint).hexdigest(),'checkpoint_bytes':len(checkpoint),
                'program_sha256':program_hashes,
                'results':{label:{name:summary(values) for name,values in cases.items()} for label,cases in times.items()},
                'metrics':{label:session.metrics() for label,session in active.items()},'platform':sys.platform}
        (out/'results.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
        (out/'raw.jsonl').write_text(''.join(json.dumps(x)+'\n' for x in raw))
        print(json.dumps(result,ensure_ascii=False,indent=2))
    finally:
        for session in active.values():session.close()


if __name__=='__main__':main()
