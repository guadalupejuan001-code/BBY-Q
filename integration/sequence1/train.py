#!/usr/bin/env python3
"""Prepare data and select candidates; all gradients and predictions run in XI."""
import argparse,collections,gzip,json,math,random,time
from pathlib import Path
from schema import ROOT,C,S
import engine as E
import data as D
import build as B
P=json.loads((ROOT/'integration/sequence1/protocol.json').read_text())
def write(p,value):Path(p).write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n')
def vocabularies():
 text=D.corpus()['train'];intents=D.intentions('train');known=set(D.KEYWORDS)
 for row in text+intents:
  for value in [row['input'],row.get('previous','')]:known.update(E.words(value))
 words=['<pad>']+sorted(known);old=json.loads((ROOT/'integration/balance/release/qchat100/vocabulary.json').read_text());out=list(old)
 for token in sorted({t for row in text for t in E.output_words(row['response'])}):
  if token not in out:out.append(token)
 assert out[0]=='<eos>' and len(out)<=128;return words,out
def evaluate(path,words,out,rows,head):
 result=[]
 with E.Model(path,words,out) as model:
  for row in rows:
   got=model.intent(row['input'],row.get('previous','')) if head else model.generate(row['input'],row.get('previous',''))
   correct=got['intent']==row['intent'] if head else got['tokens']==E.output_words(row['response']) and got['terminated']
   result.append({**row,**got,**({'expected_intent':row['intent']} if head else {}),'correct':correct})
  usage=model.s.metrics()
 groups={}
 for row in result:
  key=str(row['expected_intent']) if head else row.get('kind','known');g=groups.setdefault(key,{'correct':0,'total':0});g['correct']+=int(row['correct']);g['total']+=1
 return {'correct':sum(r['correct'] for r in result),'total':len(rows),'accuracy':sum(r['correct'] for r in result)/len(rows),'groups':groups,'usage':usage,'cases':result}
def fit(folder,words,out,rows,validation,head):
 name='intent' if head else 'text';start=folder/(name+'-initial.rvp');E.birth(start,len(out));rng=random.Random(P['seed']+head);candidates=[]
 with E.Model(start,words,out) as model:
  model.run(f'fstore {C+112} {P["learning"]["learning_rate"]}')
  samples=[];prefixes={};output_ids={w:i for i,w in enumerate(out)}
  for index,row in enumerate(rows):
   cache=S['CACHE']+index*8192;model.prepare(row['input'],row.get('previous',''),cache=cache,retain_bytes=False);prefix=[]
   labels=[row['intent']] if head else [output_ids[w] for w in E.output_words(row['response'])]+[0]
   for label in labels:
    key=(output_ids[prefix[-1]] if prefix else 0,output_ids[prefix[-2]] if len(prefix)>1 else 0,len(prefix))
    if key not in prefixes:
     prefix_cache=C+200000000+len(prefixes)*128;model.run(model.active(prefix,head=head,cache=cache)+f'store64 {C+320} {prefix_cache}\ncall c1_cache_prefix');prefixes[key]=prefix_cache
    samples.append((cache,prefixes[key],label))
    if not head and label:prefix.append(out[label])
   if (index+1)%100==0:print(json.dumps({'head':name,'cached_prompts':index+1}),flush=True)
  write(folder/(name+'-dataset.json'),{'prompts':len(rows),'token_contexts':len(samples),'prefix_frames':len(prefixes)})
  checkpoints=P['learning']['intent_epochs' if head else 'text_epochs']
  for epoch in range(1,max(checkpoints)+1):
   order=list(samples);rng.shuffle(order)
   for first in range(0,len(order),96):
    body=f'store64 {C+56} {head}\n'
    for cache,prefix,label in order[first:first+96]:body+=f'store64 {C+128} {cache}\ncall c1_load_input\nstore64 {C+320} {prefix}\ncall c1_load_prefix\nstore64 {C+64} {label}\ncall c1_train\n'
    model.run(body)
   if epoch%5==0:
    print(json.dumps({'head':name,'epoch':epoch,'native_updates':model.number(224+8*head)}),flush=True)
   if epoch in checkpoints:
    path=folder/(name+f'-epoch-{epoch:03}.rvp');model.s.save(path);measured=evaluate(path,words,out,validation,head);write(folder/(name+f'-validation-{epoch:03}.json'),measured)
    rates=[g['correct']/g['total'] for g in measured['groups'].values()];candidate={'epoch':epoch,'path':path.name,'sha256':E.sha(path),'accuracy':measured['accuracy'],'minimum_group_accuracy':min(rates),'groups':measured['groups'],'updates':model.number(224+8*head)};candidates.append(candidate);write(folder/(name+'-candidates.json'),candidates);print(json.dumps({'validated':name,**candidate}),flush=True)
 best=max(candidates,key=lambda c:(c['minimum_group_accuracy'],c['accuracy']));write(folder/(name+'-selected.json'),best);return best
def main():
 global P
 ap=argparse.ArgumentParser();ap.add_argument('folder',type=Path);ap.add_argument('--head',choices=['text','intent','both'],default='both');ap.add_argument('--protocol',type=Path,default=ROOT/'integration/sequence1/protocol.json');args=ap.parse_args();P=json.loads(args.protocol.read_text());folder=args.folder.resolve();folder.mkdir(parents=True,exist_ok=True);B.main();words,out=vocabularies();write(folder/'vocabulary.json',words);write(folder/'output-vocabulary.json',out);write(folder/'protocol.json',P)
 sources=['ai/xi/sequence1/model.xi.in','ai/xi/qchat100/model.xi','integration/sequence1/build.py','integration/sequence1/schema.py','integration/sequence1/engine.py','integration/sequence1/data.py','integration/sequence1/train.py']
 write(folder/'source-hashes.json',{p:E.sha(ROOT/p) for p in sources});(folder/'model.xi').write_bytes((ROOT/'build/sequence1/model.xi').read_bytes())
 data=D.corpus();selected={}
 if args.head in ['text','both']:selected['text']=fit(folder,words,out,data['train'],data['validation'],0)
 if args.head in ['intent','both']:selected['intent']=fit(folder,words,out,D.intentions('train'),D.intentions('validation'),1)
 write(folder/'selection.json',selected);print(json.dumps({'selected':selected}),flush=True)
if __name__=='__main__':main()
