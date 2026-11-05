#!/usr/bin/env python3
"""Exercise the actual native codec; never substitute an analytic encoder."""
import json, random, struct, tempfile
from pathlib import Path
import build as B
import engine as E
from schema import C, ROOT, S, FIELD_WIDTHS

def check(condition, description):
    if not condition:
        raise RuntimeError(description)

def main():
    B.main()
    rng=random.Random(2026110504)
    report={'version':'C1-Sequence-2','checks':[]}
    with tempfile.TemporaryDirectory(prefix='bbyq-c1-codec-') as directory:
        path=Path(directory)/'codec.rvp'; E.birth(path,80)
        with E.Model(path,['<pad>'],['<eos>']) as m:
            total=2048
            for first in range(0,total,32):
                source='';expected=[]
                for index in range(first,min(first+32,total)):
                    fields=[rng.randrange(1<<width) for width in FIELD_WIDTHS]
                    if index==0:fields=[0]*len(FIELD_WIDTHS)
                    if index==1:fields=[(1<<width)-1 for width in FIELD_WIDTHS]
                    expected.append(fields)
                    source+=E.stage64(S['FRAME'],fields)+'call c1_frame\n'
                    source+=f'mem_materialize {C+184} 8\nmem_materialize {S["MEASURED"]} 72\n'
                events=[e for e in m.run(source) if e['type']=='memory_materialization']
                check(len(events)==2*len(expected),'Missing frame evidence')
                for i,fields in enumerate(expected):
                    check(struct.unpack('<q',bytes.fromhex(events[2*i]['hex']))[0]==1,'Native frame rejected')
                    got=list(struct.unpack('<9q',bytes.fromhex(events[2*i+1]['hex'])))
                    check(got==fields,'Measured frame differs from supplied frame')
            report['checks'].append({'name':'native_frame_roundtrip','passed':True,'frames':total,'bits':total*100})
            contrast=[]
            for i in range(40):
                contrast.extend([(f'dato{i}',f'nos{i}'),(f'memoria {i}',f'no memoria {i}'),
                    (f'Neral{i} Orenda{i}',f'Orenda{i} Neral{i}'),(f'valor {i+137}',f'valor {i+138}'),
                    (f'sí año niño {i}',f'si ano nino {i}')])
            for left,right in contrast:
                a=m.prepare(left);n=m.number(40);fa=m.memory(S['F'],n*8)
                b=m.prepare(right);n=m.number(40);fb=m.memory(S['F'],n*8)
                check(fa!=fb,'Contrast lost in measured features')
                check(m.memory(S['RAW'],len(b['raw']))==b['raw'],'Original UTF-8 not retained')
                check(m.codec.words[b['tokens'][0]['id']]==b['tokens'][0]['key'],'Dictionary mismatch')
            report['checks'].append({'name':'native_contrast_discrimination','passed':True,'pairs':len(contrast)})
            for invalid in [[-1]+[0]*8, [1<<20]+[0]*8, [0]*6+[64,0,0]]:
                m.run(E.stage64(S['FRAME'],invalid)+'call c1_frame')
                check(m.number(184)==4,'Out-of-range frame silently accepted')
            report['checks'].append({'name':'frame_boundaries','passed':True,'cases':3})
            for text,previous in [('x '*257,''),('x','x '*65),('x'*16385,'')]:
                try:m.prepare(text,previous)
                except (AssertionError,ValueError):pass
                else:raise RuntimeError('Oversize text silently truncated')
            report['checks'].append({'name':'capacity_rejection','passed':True,'cases':3})
            # Caches may change transport cost, never the measured features.
            m.prepare('no define memoria memoria',previous='define año',cache=S['CACHE'])
            n=m.number(40);original=m.memory(S['F'],n*8)
            m.run(f'store64 {S["F"]} 0\nstore64 {C+128} {S["CACHE"]}\ncall c1_load_input')
            check(original==m.memory(S['F'],n*8),'Cached input differs')
            report['checks'].append({'name':'input_cache_identity','passed':True,'features':n})
            # Two formerly aliased words and a negation must be separately learnable.
            rows=[('dato',1),('nos',2),('memoria',3),('no memoria',4)]
            for i,(prompt,label) in enumerate(rows):m.prepare(prompt,cache=S['CACHE']+i*8192)
            for _ in range(100):
                source=''
                for i,(_,label) in enumerate(rows):
                    source+=m.active([],head=1,cache=S['CACHE']+i*8192)+f'store64 {C+64} {label}\ncall c1_train\n'
                m.run(source)
            check(m.number(232)==400,'Native SGD counter differs')
            for prompt,label in rows:check(m.intent(prompt)['intent']==label,'Formerly colliding prompt not learned')
            saved=Path(directory)/'learned.rvp';m.s.save(saved);saved_vocabulary=list(m.codec.words)
        with E.Model(saved,saved_vocabulary,['<eos>']) as reopened:
            for prompt,label in rows:check(reopened.intent(prompt)['intent']==label,'Saved learner changed')
            report['checks'].append({'name':'native_learning_and_reopen','passed':True,'native_updates':400,'cases':4})
    report['passed']=all(r['passed'] for r in report['checks'])
    output=ROOT/'build/sequence2/codec-checks.json';output.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(report,ensure_ascii=False))

if __name__=='__main__':main()
