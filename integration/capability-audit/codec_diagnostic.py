#!/usr/bin/env python3
"""Trace the frozen QChat input codec; no model tuning or product mutation."""
import argparse,collections,gzip,hashlib,importlib.util,itertools,json,random,statistics,sys,time,zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];RELEASE=ROOT/'integration/balance/release/qchat100';OUT=ROOT/'build/codec-diagnostic';OUT.mkdir(parents=True,exist_ok=True)
def module(name,path):
 s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
Q=module('codec_qchat',ROOT/'integration/qchat100/engine.py');D=module('codec_curriculum',ROOT/'integration/balance/data.py')
LEX=set(json.loads((RELEASE/'input-vocabulary.json').read_text()));HISTORY=set(json.loads((RELEASE/'history-vocabulary.json').read_text()));VOCAB=json.loads((RELEASE/'vocabulary.json').read_text());RT=ROOT/'deps/reverse-pc';SEED=2026110503
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def textbits(bits):return ''.join(map(str,bits))
def encode(prompt,prefix=(),previous='',filtered=True):return Q.bits(prompt,list(prefix),previous,LEX if filtered else None,HISTORY if filtered else None)
def features(raw):return list(raw)+[raw[i]*raw[88+j] for i in range(64) for j in range(12)]
def fixtures():
 rng=random.Random(SEED);manual=['memoria','no memoria','memoria no circuito','circuito no memoria','mi nave se llama Neral','mi nave se llama Orenda','calcula 137 por 24','calcula 999 por 51','sí','si','año','ano','memoria memoria memoria','define memoria','no definas memoria','¡Hola, X!','¿qué es un cúbit?','medición e interferencia']
 rows=[{'prompt':p,'previous':'','prefix':[]} for p in manual]
 while len(rows)<128:
  words=sorted(LEX)+['no','nunca','137','24','neral','orenda','si','sí','año','ano','+','*']
  rows.append({'prompt':' '.join(rng.choices(words,k=rng.randint(1,16))),'previous':' '.join(rng.choices(words,k=rng.randint(0,12))),'prefix':rng.choices(VOCAB[1:],k=rng.randint(0,16))})
 for row in rows:row['bits']=textbits(encode(row['prompt'],row['prefix'],row['previous']))
 raw=[[0]*100,[1]*100]+[[int(i==j) for i in range(100)] for j in range(100)]+[[rng.randrange(2) for _ in range(100)] for _ in range(16)]
 result={'version':'QChatCodecDiagnostic-1','seed':SEED,'base_commit':'6a6a66b301ab6efe1208791f675a18358179e2d6','input_vocabulary_sha256':sha(RELEASE/'input-vocabulary.json'),'history_vocabulary_sha256':sha(RELEASE/'history-vocabulary.json'),'codec_cases':rows,'native_vectors':[textbits(r) for r in raw]}
 p=ROOT/'android-personal/app/src/androidTest/assets/qchat-codec-diagnostic.json';p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(result,ensure_ascii=False,separators=(',',':'))+'\n');return result,p
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--fixtures-only',action='store_true');args=ap.parse_args();f,path=fixtures();print(json.dumps({'fixtures':str(path),'python_android_cases':128,'native_vectors':118}),flush=True)
 if args.fixtures_only:return
 result={'scope':'Frozen QChat100 codec, native transport and feature map; Android parity follows in CI.','base_commit':f['base_commit'],'seed':SEED,'input_vocabulary_count':len(LEX),'history_vocabulary_count':len(HISTORY),'output_vocabulary_count':len(VOCAB),'input_partitions':{'prompt_unordered_presence':48,'previous_unordered_presence':16,'last_output_token_hash':16,'second_last_output_token_hash':8,'clipped_output_position':12},'sources':{str(p.relative_to(ROOT)):sha(p) for p in [ROOT/'integration/qchat100/engine.py',ROOT/'ai/xi/qchat100/model.xi',RELEASE/'input-vocabulary.json',RELEASE/'history-vocabulary.json',RELEASE/'vocabulary.json',RELEASE/'manifest.json']}}
 pairs=[('define memoria','no definas memoria'),('memoria no circuito','circuito no memoria'),('mi nave se llama Neral','mi nave se llama Orenda'),('calcula 137 por 24','calcula 999 por 51'),('sí','si'),('año','ano'),('memoria','memoria memoria memoria')]
 result['semantic_pairs']=[{'a':a,'b':b,'normalized_a':Q.normalize(a),'normalized_b':Q.normalize(b),'tokens_a':Q.words(Q.normalize(a)),'tokens_b':Q.words(Q.normalize(b)),'kept_a':[w for w in Q.words(Q.normalize(a)) if w in LEX],'kept_b':[w for w in Q.words(Q.normalize(b)) if w in LEX],'filtered_equal':encode(a)==encode(b),'unfiltered_equal':encode(a,filtered=False)==encode(b,filtered=False),'bits':textbits(encode(a))} for a,b in pairs]
 result['critical_terms']={w:w in LEX for w in ['no','nunca','sin','137','24','neral','orenda','memoria','circuito']}
 def collisions(items,region):
  buckets=collections.defaultdict(list)
  for item in items:
   prompt=item if isinstance(item,str) else ' '.join(item);buckets[textbits(encode(prompt)[region])].append(item)
  groups=[v for v in buckets.values() if len(v)>1];return {'inputs':len(items),'distinct_codes':len(buckets),'ambiguous_code_groups':len(groups),'examples':groups[:8]}
 result['single_term_hash_collisions']=collisions(sorted(LEX),slice(0,48));result['two_term_hash_collisions']=collisions(list(itertools.combinations(sorted(LEX),2)),slice(0,48))
 rng=random.Random(SEED);terms=sorted(LEX);rng.shuffle(terms);result['saturation']=[{'unique_known_terms':n,'prompt_bits_set':sum(encode(' '.join(terms[:n]))[:48]),'previous_bits_set':sum(encode('repitelo',previous=' '.join(terms[:n]))[48:64])} for n in [1,2,5,10,20,40,80,106]]
 result['output_position_clipping']={'eleven_vs_twelve_repeated_tokens_identical':encode('hola',['memoria']*11)==encode('hola',['memoria']*12),'maximum_generated_tokens':16}
 corpus=D.build();all_rows=[dict(r,split=split) for split in ['train','validation','test'] for r in corpus[split]];groups=collections.defaultdict(list)
 for row in all_rows:groups[textbits(encode(row['input'],previous=row.get('previous','')))].append(row)
 conflicts=[v for v in groups.values() if len({tuple(Q.words(r['response'])) for r in v})>1]
 result['curriculum_encoding']={'examples':len(all_rows),'distinct_prompt_context_codes':len(groups),'incompatible_label_code_groups':len(conflicts),'examples_of_conflict':conflicts[:5],'scope':'Only the bounded E01 topic curriculum, not an open-language benchmark'}
 descriptor=json.loads((RELEASE/'manifest.json').read_text());raw=gzip.decompress((RELEASE/descriptor['file']).read_bytes());assert hashlib.sha256(raw).hexdigest()==descriptor['checkpoint_sha256'];state=OUT/'qchat.rvp';state.write_bytes(raw);original=sha(state)
 stats={'vectors':0,'stage_bytes_checked':0,'native_feature_bytes_checked':0,'native_vs_analytic_vectors':0,'basis_vectors':100,'failures':[]}
 with Q.Native(RT,state) as model:
  for idx,bits in enumerate(f['native_vectors']):
   raw=[int(c) for c in bits];events,_=model.execute(Q.stage(raw)+f'store64 {Q.A+80} 0\ncall qchat_encode\nmem_materialize {Q.A+1000} 100\nmem_materialize {Q.A+2000} 868')
   chunks=[bytes.fromhex(e['hex']) for e in events if e['type']=='memory_materialization'];assert chunks[0]==bytes(raw),(idx,'stage');assert chunks[1]==bytes(features(raw)),(idx,'native feature map')
   events,_=model.execute(f'store64 {Q.A+80} 2\ncall qchat_encode\nmem_materialize {Q.A+2000} 868');control=next(bytes.fromhex(e['hex']) for e in events if e['type']=='memory_materialization');assert control==chunks[1],(idx,'analytic control')
   stats['vectors']+=1;stats['stage_bytes_checked']+=100;stats['native_feature_bytes_checked']+=868;stats['native_vs_analytic_vectors']+=1
  result['native_transport_and_features']=stats;result['runtime_usage']=model.s.metrics()
  generated=[]
  for row in result['semantic_pairs'][:4]:
   a=model.generate(row['a'],VOCAB,input_vocabulary=LEX,history_vocabulary=HISTORY);b=model.generate(row['b'],VOCAB,input_vocabulary=LEX,history_vocabulary=HISTORY)
   assert a['text']==b['text'];generated.append({'a':row['a'],'b':row['b'],'response_a':a['text'],'response_b':b['text'],'identical_response':a['text']==b['text']})
  result['native_generated_aliases']=generated
 assert sha(state)==original;result['checkpoint_sha256']=original;result['released_checkpoint_unchanged']=sha(RELEASE/descriptor['file'])==descriptor['gzip_sha256']
 evidence=ROOT/'build/capability-audit/android-capability-audit.json'
 if evidence.exists():
  rows=json.loads(evidence.read_text())['cases'];open_rows=[r for r in rows if r['group']=='open-language'];result['prior_android_open_request_routes']={'requests':len(open_rows),'engines':dict(collections.Counter(r.get('engine','exception before a result') for r in open_rows)),'warning':'Open-language failures are not all caused by QChat. Most reach the preserved route or fail in the Zero parser before the generator is selected.','cases':[{'id':r['id'],'input':r['input'],'engine':r.get('engine'),'exception':r.get('exception')} for r in open_rows]}
 target=OUT/'native-report.json';target.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n');print(json.dumps({'report':str(target),'transport_vectors':stats['vectors'],'native_feature_bytes_checked':stats['native_feature_bytes_checked'],'single_term_collision_groups':result['single_term_hash_collisions']['ambiguous_code_groups'],'two_term_collision_groups':result['two_term_hash_collisions']['ambiguous_code_groups']},ensure_ascii=False),flush=True)
if __name__=='__main__':main()
