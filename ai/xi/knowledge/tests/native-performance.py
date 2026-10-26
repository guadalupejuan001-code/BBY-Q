#!/usr/bin/env python3
"""Reproducible timing/verification only. Never selects an agent answer.

Times complete captured child processes and records child CPU deltas.
Native session metrics report their own RSS; launcher RSS is cumulative.
Native programs get only request bytes. Oracle comparisons run after timing.
"""
import argparse
import hashlib
import json
import math
import os
from pathlib import Path
import platform
import random
import resource
import statistics
import subprocess
import sys
import time

K=7400000000000000000
CASES=[
 ('direct','¿qué es neurona?','neurona es célula.'),
 ('inferred','gato es organismo?','gato es organismo. [gato -> mamífero -> vertebrado -> organismo]'),
 ('objects','qué estudia filosofía?','filosofía estudia conciencia; filosofía estudia conocimiento.'),
 ('unknown','bbyq tiene conciencia?','?'),
 ('late_word','metro mide longitud?','metro mide longitud.'),
 ('arithmetic','nueve mas nueve menos uno','17'),
 ('legacy','cuarto contiene llave?','cuarto contiene llave (via caja).'),
 ('malformed','gato es animal??','?'),
]


def frame(text):
    data=text.encode('utf-8')
    stores=[(K+16,1),(K+17,len(data)),(K+3,1)]
    stores += [(K+128+i,v) for i,v in enumerate(data)]
    return '#!reverse-pc-machine-v1\n'+''.join(f'store8 {a} {v}\n' for a,v in stores)


def summarize(samples):
    walls=sorted(x['ms'] for x in samples)
    return {'n':len(samples),'median_ms':statistics.median(walls),
            'p95_ms':walls[max(0,math.ceil(.95*len(walls))-1)],
            'p99_ms':walls[max(0,math.ceil(.99*len(walls))-1)],
            'cpu_ms_median':statistics.median(x['cpu_ms'] for x in samples if x['cpu_ms'] is not None) if any(x['cpu_ms'] is not None for x in samples) else None,
            'campaign_peak_child_rss_kib':max(x['rss_kib'] for x in samples if x['rss_kib'] is not None) if any(x['rss_kib'] is not None for x in samples) else None,
            'serial_queries_per_second':1000*len(walls)/sum(walls)}


def child(command,out):
    # communicate waits for captured pipe output as well as process completion;
    # never reuse a mutable stdout file as the measurement synchronization.
    before=resource.getrusage(resource.RUSAGE_CHILDREN)
    started=time.perf_counter_ns()
    p=subprocess.run(command,capture_output=True,timeout=30)
    elapsed=(time.perf_counter_ns()-started)/1e6
    usage=resource.getrusage(resource.RUSAGE_CHILDREN)
    (out/'stdout').write_bytes(p.stdout);(out/'stderr').write_bytes(p.stderr)
    assert p.returncode==0,(command,p.stderr.decode())
    return {'ms':elapsed,'cpu_ms':1000*(usage.ru_utime+usage.ru_stime-before.ru_utime-before.ru_stime),
            'rss_kib':usage.ru_maxrss}


def decode(path):
    result=[]
    for row in path.read_text().splitlines():
        if not row.startswith('{'):continue
        item=json.loads(row)
        if item.get('register') in ('r14','r9'):result.append(item['value'])
    return bytes(result).decode('utf-8')


def profile(runtime,root,state,out,repeats):
    """Isolate each native phase on its actual input; matched no-op exposes
    reload/parse/save overhead. Phase medians are not additive latency claims.
    """
    out.mkdir(parents=True,exist_ok=True);incoming=out/'incoming.rvp';incoming.write_bytes(state.read_bytes())
    raw=out/'raw.xi';raw.write_text(frame('gato es organismo?'))
    child([runtime,'run',str(raw),str(incoming),str(out/'staged.rvp')],out)
    incoming.write_bytes((out/'staged.rvp').read_bytes())
    noop=out/'noop.xi';noop.write_text('#!reverse-pc-machine-v1\nhalt\n')
    results={}
    for name in ['read','resolve','parse-question','rule-check','ask','respond','clean']:
        samples=[];reference=[];program=root/'ai/xi/knowledge'/f'{name}.xi'
        for _ in range(repeats):
            reference.append(child([runtime,'run',str(noop),str(incoming),str(out/'noop.rvp')],out))
            samples.append(child([runtime,'run',str(program),str(incoming),str(out/'next.rvp')],out))
        results[name]={'phase':summarize(samples),'matched_noop':summarize(reference)}
        incoming.write_bytes((out/'next.rvp').read_bytes())
    return results


def main():
    ap=argparse.ArgumentParser();ap.add_argument('runtime');ap.add_argument('baseline_root');ap.add_argument('baseline_state')
    ap.add_argument('--candidate-root');ap.add_argument('--candidate-state');ap.add_argument('--out',default='evidence/performance')
    ap.add_argument('--native-repeats',type=int,default=30);ap.add_argument('--ui-repeats',type=int,default=8)
    ap.add_argument('--profile',action='store_true');ap.add_argument('--session-binary');args=ap.parse_args()
    runtime=str(Path(args.runtime).resolve());out=Path(args.out).resolve();out.mkdir(parents=True,exist_ok=True)
    variants={'baseline':(Path(args.baseline_root).resolve(),Path(args.baseline_state).resolve())}
    if args.candidate_root:
        variants['candidate']=(Path(args.candidate_root).resolve(),Path(args.candidate_state).resolve())
    linked={};programs={};samples={};cold={};warmup={};raw=[]
    for label,(root,state) in variants.items():
        folder=out/label;folder.mkdir(exist_ok=True)
        linked[label]=subprocess.check_output(['bash',str(root/'ai/xi/knowledge/link.sh'),'combined'],text=True).split('\n',1)[1]
        samples[label]={'native':{},'ui_warm':{}};cold[label]={};warmup[label]={}
        for name,text,expected in CASES:
            p=folder/f'{name}.xi';p.write_text(frame(text)+linked[label]);programs[label,name]=p
            samples[label]['native'][name]=[];samples[label]['ui_warm'][name]=[]
            # First UI request includes source linkage/cache construction.
            working=folder/f'first-{name}.rvp';working.write_bytes(state.read_bytes())
            m=child(['bash',str(root/'ai/xi/knowledge/text.sh'),runtime,str(working),text,'es'],folder)
            assert (folder/'stdout').read_text().rstrip('\n')==expected
            cold[label][name]=m
    rng=random.Random(170213)
    for mode,repeats in [('native',args.native_repeats),('ui_warm',args.ui_repeats)]:
        for iteration in range(repeats):
            pairs=[(label,case) for label in variants for case in CASES];rng.shuffle(pairs)
            for label,(name,text,expected) in pairs:
                root,state=variants[label];folder=out/label
                if mode=='native':
                    command=[runtime,'run',str(programs[label,name]),str(state),str(folder/'next.rvp')]
                else:
                    working=folder/f'work-{iteration}-{name}.rvp';working.write_bytes(state.read_bytes())
                    command=['bash',str(root/'ai/xi/knowledge/text.sh'),runtime,str(working),text,'es']
                result=child(command,folder)
                if mode=='ui_warm':assert not Path(str(working)+'.lock').exists()
                actual=decode(folder/'stdout') if mode=='native' else (folder/'stdout').read_text().rstrip('\n')
                assert actual==expected,(label,mode,name,actual,expected)
                samples[label][mode][name].append(result)
                raw.append({'variant':label,'mode':mode,'case':name,'iteration':iteration,**result})
            if iteration%10==0:print(mode,iteration,flush=True)
    summary={'platform':{'system':platform.system(),'machine':platform.machine(),'logical_cpus':os.cpu_count()},
             'method':'interleaved deterministic random order; one request per process; captured pipe completion; child CPU deltas; RSS is campaign cumulative peak; oracle outside timing',
             'program_sha256':{k:hashlib.sha256(v.encode()).hexdigest() for k,v in linked.items()},
             'states':{k:{'bytes':s.stat().st_size,'sha256':hashlib.sha256(s.read_bytes()).hexdigest()} for k,(_,s) in variants.items()},
             'results':{k:{mode:{case:summarize(v) for case,v in cases.items()} for mode,cases in modes.items()} for k,modes in samples.items()},
             'first_ui_requests':cold}
    if args.session_binary:
        sys.path.insert(0,str(Path(__file__).resolve().parents[3]/'native'))
        from session_client import Session,decode_result
        summary['sessions']={};active={};timings={};first={}
        try:
            for label,(root,state) in variants.items():
                folder=out/label
                program=folder/'session.xi';program.write_text('#!reverse-pc-machine-v1\n'+linked[label])
                working=folder/'session.rvp';working.write_bytes(state.read_bytes())
                active[label]=Session(Path(args.session_binary).resolve(),working,program)
                value,first[label]=active[label].request(CASES[0][1]);assert decode_result(value)==CASES[0][2]
                timings[label]={name:[] for name,_,_ in CASES}
            for iteration in range(args.native_repeats):
                order=[(label,case) for label in variants for case in CASES];rng.shuffle(order)
                for label,(name,text,expected) in order:
                    value,ms=active[label].request(text)
                    assert decode_result(value)==expected
                    timings[label][name].append({'ms':ms,'cpu_ms':None,'rss_kib':None})
            for label,session in active.items():
                native_metrics=session.metrics()
                session.close()
                summary['sessions'][label]={'first_request_ms':first[label],'native_metrics':native_metrics,
                    'results':{name:summarize(v) for name,v in timings[label].items()},
                    'checkpoint_committed_before_every_reply':True,'variants_interleaved':True}
        finally:
            for session in active.values():session.close()
    if args.profile:summary['baseline_phases']=profile(runtime,variants['baseline'][0],variants['baseline'][1],out/'phase',12)
    (out/'results.json').write_text(json.dumps(summary,indent=2)+'\n')
    (out/'raw.jsonl').write_text(''.join(json.dumps(x)+'\n' for x in raw))
    print(json.dumps(summary['results'],indent=2))


if __name__=='__main__':main()
