#!/usr/bin/env python3
"""Scale, session transaction and bounded-work tests; no production learner."""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import statistics
import shutil
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[1]
REPO=ROOT.parents[2]
spec=importlib.util.spec_from_file_location('knowledge_examiner',ROOT/'tests/native-knowledge.py')
exam=importlib.util.module_from_spec(spec);spec.loader.exec_module(exam)
sys.path.insert(0,str(REPO/'ai/native'))
from session_client import Session,decode_result
K=exam.K;D=exam.D


def canonical(path):
    core,memory,bindings=exam.snapshot(path)
    ephemeral={D+3,*range(D+5,D+13),K+3,*range(K+8,K+16),
               *range(K+2100,K+2108),*range(K+2200,K+2232)}
    return core,{a:v for a,v in memory.items() if a not in ephemeral},bindings


def main():
    ap=argparse.ArgumentParser();ap.add_argument('runtime');ap.add_argument('session_binary')
    ap.add_argument('e011');ap.add_argument('e012');ap.add_argument('--out',default='evidence/stress')
    ap.add_argument('--turns',type=int,default=1000);args=ap.parse_args()
    out=Path(args.out).resolve();out.mkdir(parents=True,exist_ok=True)
    runtime=str(Path(args.runtime).resolve());binary=Path(args.session_binary).resolve()
    parent=Path(args.e012).resolve();seed=parent.read_bytes()
    program=out/'combined.xi';program.write_bytes(subprocess.check_output(['bash',str(ROOT/'link.sh'),'combined']))
    e=exam.Examiner(runtime,args.e011,out/'grow');e.state.write_bytes(seed)
    for c,k,l,w in exam.rows('words-v1.psv'):
        e.names.setdefault(int(c),{}).setdefault(int(l),w)
        if w not in e.aliases[int(c)]:e.aliases[int(c)].append(w)
    e.truth={(int(s),int(p),int(o)):int(pol) for s,p,o,pol,_ in exam.rows('facts-v1.psv')}
    stages=[{'name':'base','lexical_entries':374,'facts':185,'path':str(parent),'bytes':len(seed)}]
    for i in range(138):e.word(40,1,1,'zzalias'+chr(97+i//26)+chr(97+i%26))
    e.word(40,1,1,'overflowalias',reject=True)
    tuples=iter((s,29,o) for s in [165,166,167] for o in range(40,198))
    for target in [256,512]:
        while e.preserve().get(K+6,0)+256*e.preserve().get(K+7,0)<target:
            s,p,o=next(tuples);e.fact(s,p,o,source=9)
        e.query('zzaliasfh es organismo?',[(40,23,43)])
        objects=sorted(o for (s,p,o),bits in e.truth.items() if s==165 and p==29 and bits==1)
        e.query('qué transforma bbyq?',[(165,29,o) for o in objects[:8]])
        e.audit()
        path=out/f'facts-{target}.rvp';path.write_bytes(e.state.read_bytes())
        stages.append({'name':f'facts-{target}','lexical_entries':512,'facts':target,
                       'path':str(path),'bytes':path.stat().st_size})
    s,p,o=next(tuples);e.fact(s,p,o,source=9,reject=True)
    print('CAPACITY_AND_ROLLBACK_PASS',flush=True)

    # Wide, unrelated synthetic graph reaches the 64-expansion budget. It is
    # never released as factual knowledge or written over the real checkpoint.
    e.state.write_bytes(seed)
    e.truth={(int(s),int(p),int(o)):int(pol) for s,p,o,pol,_ in exam.rows('facts-v1.psv')}
    for a,b,c in [(180,181,182),(183,184,185)]:
        e.fact(a,29,b,source=9);e.fact(b,29,c,source=9);e.fact(a,29,c,source=9);e.calibrate(29,a,b,c)
    for target in range(40,121):e.fact(165,29,target,source=9)
    reached=e.query('bbyq transforma psicología?',status=0)
    assert reached[K+9]==5
    e.audit()
    print('WIDE_GRAPH_BUDGET_AND_CLEANUP_PASS',flush=True)

    # Exercise the exact proof-depth boundary affected by sparse cleanup.
    e.state.write_bytes(seed)
    e.truth={(int(s),int(p),int(o)):int(pol) for s,p,o,pol,_ in exam.rows('facts-v1.psv')}
    for cid in range(200,233):
        suffix=chr(97+(cid-200)//26)+chr(97+(cid-200)%26)
        e.word(cid,1,1,'nivel'+suffix);e.word(cid,1,2,'depth'+suffix)
    for a,b,c in [(180,181,182),(183,184,185)]:
        e.fact(a,29,b,source=9);e.fact(b,29,c,source=9);e.fact(a,29,c,source=9);e.calibrate(29,a,b,c)
    for cid in range(200,232):e.fact(cid,29,cid+1,source=9)
    boundary=e.query('nivelaa transforma nivelbf?',[(200,29,231)])
    assert boundary[K+15]==31
    e.query('nivelaa transforma nivelbg?',status=0);e.audit()
    print('PROOF_DEPTH_31_AND_32_BOUNDARY_PASS',flush=True)

    # A source edit must invalidate the compiled-source cache. This isolated
    # fixture changes rendering deliberately; it is never a released model.
    copy=out/'cache-fixture';shutil.copytree(REPO/'ai/xi',copy/'xi')
    cached=copy/'state.rvp';cached.write_bytes(seed)
    script=copy/'xi/knowledge/text.sh'
    first=subprocess.run(['bash',str(script),runtime,str(cached),'qué es neurona?','es'],capture_output=True,text=True)
    assert first.returncode==0 and first.stdout=='neurona es célula.\n'
    (copy/'xi/knowledge/respond.xi').write_text('#!reverse-pc-machine-v1\nset r14 79\nprint r14\nhalt\n')
    second=subprocess.run(['bash',str(script),runtime,str(cached),'qué es neurona?','es'],capture_output=True,text=True)
    assert second.returncode==0 and second.stdout=='O\n'
    assert len(list((copy/'.bbyq-xi-cache').glob('*.xi')))==2
    print('SOURCE_CACHE_INVALIDATION_PASS',flush=True)

    working=out/'session.rvp';working.write_bytes(seed);reference=canonical(working)
    timings=[];residents=[];sizes=[]
    cases=[('gato es organismo?','gato es organismo. [gato -> mamífero -> vertebrado -> organismo]'),
           ('qué es neurona?','neurona es célula.'),('dos mas tres','cinco'),
           ('cuarto contiene llave?','cuarto contiene llave (via caja).'),('gato es animal??','?')]
    with Session(binary,working,program) as session:
        for i in range(args.turns):
            text,expected=cases[i%len(cases)];raw,elapsed=session.request(text)
            assert decode_result(raw)==expected;timings.append(elapsed)
            assert canonical(working)==reference  # Saved BEFORE response, not at EOF.
            if i%100==0:
                residents.append({'turn':i,**session.metrics()})
                sizes.append(working.stat().st_size)
        # A second writer must not replace state while this session is alive.
        before=working.read_bytes()
        other=subprocess.run([str(binary),str(working),str(program)],input=b'',capture_output=True)
        assert other.returncode!=0 and b'active writer' in other.stderr
        assert working.read_bytes()==before
        alias=out/'state-alias.rvp';alias.symlink_to(working)
        other=subprocess.run([str(binary),str(alias),str(program)],input=b'',capture_output=True)
        assert other.returncode!=0 and b'active writer' in other.stderr
        assert working.read_bytes()==before
    assert session.process.returncode==0 and not Path(str(working)+'.lock').exists()
    with Session(binary,working,program) as session:
        raw,_=session.request('menos uno');assert decode_result(raw)=='cuatro'
    print('PERSISTENT_TURNS_RESTART_AND_WRITER_LOCK_PASS',flush=True)

    # Saving failure must leave BOTH the file and in-memory context unchanged.
    working.write_bytes(seed)
    with Session(binary,working,program) as session:
        pending=Path(str(working)+'.pending');pending.mkdir()
        before=working.read_bytes()
        try:session.request('dos mas tres');raise AssertionError('save failure not reported')
        except RuntimeError as error:assert 'cannot write state' in str(error)
        assert working.read_bytes()==before;pending.rmdir()
        raw,_=session.request('minus one',2);assert decode_result(raw)=='three'
    # An XI exception must similarly leave the loaded authority untouched.
    failure=out/'failure.xi';body=program.read_text().split('\n',1)[1]
    failure.write_text(f'#!reverse-pc-machine-v1\nload8 r0 {K+17}\ncmp r0 1\njne normal\ndiv r0 0\nlabel normal\n'+body)
    working.write_bytes(seed)
    with Session(binary,working,failure) as session:
        before=working.read_bytes()
        try:session.request('x');raise AssertionError('XI failure not reported')
        except RuntimeError:pass
        assert working.read_bytes()==before
        raw,_=session.request('minus one',2);assert decode_result(raw)=='three'
    corrupt=out/'corrupt.rvp';bad=bytearray(seed);bad[-1]^=1;corrupt.write_bytes(bad)
    failed=subprocess.run([str(binary),str(corrupt),str(program)],input=b'',capture_output=True)
    assert failed.returncode!=0 and not Path(str(corrupt)+'.lock').exists()
    assert corrupt.read_bytes()==bad
    print('TRANSACTION_AND_CORRUPTION_PASS',flush=True)
    report={'parent_sha256':hashlib.sha256(seed).hexdigest(),'stages':stages,
            'overflow_word_513_rejected':True,'overflow_fact_513_rejected':True,
            'wide_graph_budget':64,'wide_graph_stops_without_dirty_scratch':True,
            'proof_depth_31_passes_32_abstains':True,'source_cache_invalidates_after_code_edit':True,
            'persistent_turns':args.turns,'all_turn_outputs_verified':True,'canonical_model_unchanged':True,
            'checkpoint_readable_after_every_reply':True,'writer_lock_and_restart':True,'symlink_uses_same_writer_lock':True,
            'failed_save_keeps_memory_and_file':True,'xi_failure_keeps_memory_and_file':True,
            'corruption_rejected_before_execution':True,'session_median_ms':statistics.median(timings),
            'session_p95_ms':sorted(timings)[int(.95*len(timings))-1],
            'resident_samples':residents,'sampled_checkpoint_bytes':sizes}
    (out/'results.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2))


if __name__=='__main__':main()
