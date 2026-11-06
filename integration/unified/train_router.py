#!/usr/bin/env python3
"""Continue the real native C1 reader for the single unified input route."""
import sys
from pathlib import Path
if __package__ in [None,'']:sys.path.insert(0,str(Path(__file__).resolve().parents[2]))
import argparse,collections,math,random
from integration.unified.common import ROOT,C1,Legacy,encoded,digest,read,write,source_identity
from integration.unified import data

def evaluate(path,words,out,rows):
    cases=[]
    with C1.Model(path,words,out) as model:
        for row in rows:
            result=model.intent(row['input'],row.get('previous',''));cases.append({**row,**result,'expected':row['intent'],'correct':row['intent']==result['intent']})
    groups={}
    for row in cases:
        group=row.get('family','legacy-'+str(row['expected']));g=groups.setdefault(group,{'correct':0,'total':0});g['correct']+=row['correct'];g['total']+=1
    return {'correct':sum(r['correct'] for r in cases),'total':len(cases),'groups':groups,'cases':cases}

def main():
    p=argparse.ArgumentParser();p.add_argument('folder',type=Path);args=p.parse_args();folder=args.folder.resolve();folder.mkdir(parents=True,exist_ok=True)
    print(data.check_splits(),flush=True)
    base=ROOT/'integration/sequence2/release';models=Legacy.read_models(base);words=read(base/'vocabulary.json');out=read(base/'output-vocabulary.json');train=data.rows('train');validation=data.rows('validation')
    extra={w for row in train for value in [row['input'],row.get('previous','')] for w in C1.words(value)}-set(words);words+=sorted(extra)
    semantic=set(read(base/'semantic-vocabulary.json'))|{w for row in train if row['intent']!=0 for w in C1.words(row['input']) if w not in C1.ROUTING_FILLERS}
    for name,value in [('vocabulary.json',words),('output-vocabulary.json',out),('semantic-vocabulary.json',sorted(semantic))]:write(folder/name,value)
    (folder/'model.xi').write_bytes((base/'model.xi').read_bytes());initial=folder/'router-initial.rvp';initial.write_bytes(models['intent'])
    write(folder/'protocol.json',{'seed':2026110701,'epochs':[1,5,10,20],'source':'C1 frozen reader plus declared quantum contracts, native XI SGD and class-balanced rehearsal','selection':'minimum validation capability, no reserved-test feedback','threshold':.9,'quantum_threshold':.95,'apk_built':False})
    write(folder/'source-hashes.json',source_identity());rng=random.Random(2026110701);candidates=[]
    original=data.C1Data.intentions('train');old_semantic=set(read(base/'semantic-vocabulary.json'));added_semantic=semantic-old_semantic
    with C1.Model(initial,words,out) as m:
        m.run(f'fstore {C1.C+112} .1')
        for i,row in enumerate(train):
            address=C1.S['CACHE']+i*8192
            reuse=i<len(original) and row==original[i] and not(set(C1.words(row['input']))&added_semantic)
            if reuse:m.run(f'store64 {C1.C+128} {address}\ncall c1_load_input')
            else:m.prepare(row['input'],row.get('previous',''),cache=address,retain_bytes=False)
            if i%150==0:print({'cached':i,'total':len(train)},flush=True)
        m.prepare(train[0]['input'],cache=C1.S['CACHE']);m.run(m.active([],head=1,cache=C1.S['CACHE'])+f'store64 {C1.C+320} {C1.C+200000000}\ncall c1_cache_prefix')
        grouped=collections.defaultdict(list)
        for i,row in enumerate(train):grouped[row['intent']].append((C1.S['CACHE']+i*8192,row['intent']))
        count=math.ceil(len(train)/len(grouped))
        for epoch in range(1,21):
            samples=[]
            for group in grouped.values():
                shuffled=list(group);rng.shuffle(shuffled);samples.extend(shuffled[i%len(shuffled)] for i in range(count))
            rng.shuffle(samples)
            for first in range(0,len(samples),96):
                body=f'store64 {C1.C+56} 1\n'
                for address,label in samples[first:first+96]:body+=f'store64 {C1.C+128} {address}\ncall c1_load_input\nstore64 {C1.C+320} {C1.C+200000000}\ncall c1_load_prefix\nstore64 {C1.C+64} {label}\ncall c1_train\n'
                m.run(body)
            if epoch in [1,5,10,20]:
                path=folder/f'router-{epoch:03}.rvp';m.s.save(path);result=evaluate(path,words,out,validation);write(folder/f'validation-{epoch:03}.json',result)
                rates=[g['correct']/g['total'] for g in result['groups'].values()];entry={'epoch':epoch,'path':path.name,'sha256':C1.sha(path),'minimum':min(rates),'accuracy':result['correct']/result['total'],'groups':result['groups'],'updates':m.number(232)}
                candidates.append(entry);write(folder/'candidates.json',candidates);print(entry,flush=True)
                quantum=[g['correct']/g['total'] for k,g in result['groups'].items() if not k.startswith('legacy-')]
                if min(rates)>=.9 and min(quantum)>=.95:break
    best=max(candidates,key=lambda row:(row['minimum'],row['accuracy']));write(folder/'selected.json',best)
    print({'selected':best},flush=True)

if __name__=='__main__':main()
