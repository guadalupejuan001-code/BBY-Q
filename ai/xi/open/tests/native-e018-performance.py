#!/usr/bin/env python3
"""Interleaved measured native sessions; display changes never replace search."""
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
U=7800000000000000000
PREFIX='Según lo aprendido: '
WHY='La evidencia guardada es: Neral es un organismo. [neral --es--> mamífero --es--> vertebrado --es--> organismo]'
CASES=[
    ('direct','qué es neurona?','Una neurona es una célula.','Una neurona es una célula.'),
    ('old_inference','gato es organismo?','Un gato es un organismo. [gato -> mamífero -> vertebrado -> organismo]','Un gato es un organismo.'),
    ('multiple','qué estudia filosofía?','Filosofía estudia conciencia; filosofía estudia conocimiento.','Filosofía estudia conciencia y conocimiento.'),
    ('new_definition','qué es neral?',PREFIX+'Neral es un mamífero; neral es un vertebrado; neral es un animal; neral es un organismo.',PREFIX+'Neral es un mamífero, un vertebrado, un animal y un organismo.'),
    ('new_inference','neral es organismo?',PREFIX+'Neral es un organismo. [neral --es--> mamífero --es--> vertebrado --es--> organismo]',PREFIX+'Neral es un organismo.'),
    ('explicit_why','por qué neral es organismo?',WHY,WHY),
    ('unknown','qué es algoquenoexiste?','No tengo información suficiente para responder.','No tengo información suficiente para responder.'),
    ('arithmetic','dos mas tres','El resultado es cinco.','El resultado es cinco.'),
]


def summary(values):
    return {'n':len(values),'median_ms':statistics.median(values),
            'p95_ms':sorted(values)[max(0,(len(values)*95+99)//100-1)]}


def main():
    ap=argparse.ArgumentParser();ap.add_argument('runtime');ap.add_argument('binary')
    ap.add_argument('baseline_root');ap.add_argument('checkpoint');ap.add_argument('--out',default='evidence/e018-performance')
    ap.add_argument('--repeats',type=int,default=40);args=ap.parse_args()
    out=Path(args.out).resolve();out.mkdir(parents=True,exist_ok=True)
    seed=Path(args.checkpoint).read_bytes();runtime=Path(args.runtime).resolve();binary=Path(args.binary).resolve()
    variants={'e017_full':(Path(args.baseline_root).resolve(),1,2),'e018_full':(REPO,0,2),'e018_brief':(REPO,1,3)}
    active={};times={};raw=[];hashes={}
    try:
        for label,(root,preference,index) in variants.items():
            state=out/(label+'.rvp');state.write_bytes(seed)
            if label=='e018_full':
                style=out/'preference.xi';target=out/'preferred.rvp'
                code=subprocess.check_output(['bash',str(REPO/'ai/xi/knowledge/link.sh'),'open-style'],text=True).split('\n',1)[1]
                style.write_text(f'#!reverse-pc-machine-v1\nstore8 {U+316} {preference}\n'+code)
                subprocess.run([str(runtime),'run',str(style),str(state),str(target)],check=True,capture_output=True)
                target.replace(state)
            program=out/(label+'.xi')
            program.write_bytes(subprocess.check_output(['bash',str(root/'ai/xi/knowledge/link.sh'),'conversation']))
            hashes[label]=hashlib.sha256(program.read_bytes()).hexdigest()
            session=Session(binary,state,program);active[label]=session
            answer,_=session.request('aprende que neral es mamífero')
            assert decode_result(answer)=='Aprendí esa afirmación del diálogo.'
            times[label]={case[0]:[] for case in CASES}
            for case in CASES:
                result,_=session.request(case[1]);assert decode_result(result)==case[index]
        rng=random.Random(180627)
        for iteration in range(args.repeats):
            order=[(label,case) for label in variants for case in CASES];rng.shuffle(order)
            for label,case in order:
                value,ms=active[label].request(case[1]);spoken=decode_result(value)
                assert spoken==case[variants[label][2]],(label,case[0],spoken)
                times[label][case[0]].append(ms)
                raw.append({'variant':label,'case':case[0],'iteration':iteration,'ms':ms,'response_utf8_bytes':len(spoken.encode())})
        result={'method':'native resident sessions; same E018 checkpoint; E018 full differs only in explicit display preference; randomized interleaving seed 180627; save before ACK; expected answers outside native inference',
                'checkpoint_sha256':hashlib.sha256(seed).hexdigest(),'checkpoint_bytes':len(seed),
                'program_sha256':hashes,'platform':sys.platform,
                'results':{label:{name:summary(values) for name,values in cases.items()} for label,cases in times.items()},
                'response_utf8_bytes':{case[0]:{'full':len(case[2].encode()),'brief':len(case[3].encode())} for case in CASES},
                'metrics':{label:session.metrics() for label,session in active.items()}}
        (out/'results.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
        (out/'raw.jsonl').write_text(''.join(json.dumps(row)+'\n' for row in raw))
        print(json.dumps(result,ensure_ascii=False,indent=2))
    finally:
        for session in active.values():session.close()


if __name__=='__main__':main()
