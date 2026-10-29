#!/usr/bin/env python3
"""Complete source ingestion and exact byte transport. Matching/answers run in XI."""
import argparse,base64,collections,gzip,hashlib,importlib.util,json,random,shutil,struct,subprocess,time
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('runtime');p.add_argument('omw');p.add_argument('out');a=p.parse_args()
runtime=str(Path(a.runtime).resolve());source=Path(a.omw);out=Path(a.out).resolve();out.mkdir(parents=True,exist_ok=True)
subprocess.run(['node','ai/releases/e030/build.mjs',runtime,str(out)],check=True)
base_app=out/'learned.rxe'
prep=Path('ai/releases/e031/request.xi').read_text()
linked=prep.replace('print r0\nhalt','jmp lex_lookup').replace('label lex_delegate\ndiv r0 0','label lex_delegate\njmp lex_parent_entry')
linked+=Path('ai/releases/e031/lookup.xi').read_text()
linked+=(out/'learned-linked.xi').read_text().replace('#!reverse-pc-machine-v1','label lex_parent_entry',1)
(out/'dictionary-linked.xi').write_text(linked)
subprocess.run([runtime,'compile',str(out/'dictionary-linked.xi'),str(out/'dictionary-code.rxe'),'BBY Q bilingual dictionary XI'],check=True,capture_output=True)
subprocess.run([runtime,'pack-app',str(out/'dictionary-code.rxe'),str(out/'controller.rvp'),str(out/'dictionary.rxe'),'org.reverse.bbyq','BBY Q','E031-Dictionary-1-dev','d9440d5300900b0418c8f14b4713b882c7f375dc'],check=True,capture_output=True)
sha=lambda f:hashlib.sha256(Path(f).read_bytes()).hexdigest()
raws={'en':source/'wns/eng/wn-data-eng.tab','es':source/'wns/mcr/wn-data-spa.tab'}
lemmas=collections.defaultdict(lambda:collections.defaultdict(set));defs=collections.defaultdict(lambda:collections.defaultdict(list))
words={'en':collections.defaultdict(set),'es':collections.defaultdict(set)};counts={}
fold=lambda w:w.translate(str.maketrans('ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz')).replace('_',' ')
for lang,file in raws.items():
 n=0;types=collections.Counter()
 for line in file.read_text().splitlines():
  if not line or line.startswith('#'):continue
  cols=line.split('\t');types[cols[1]]+=1;n+=1
  sid,typ=cols[:2]
  if typ.rsplit(':',1)[-1]=='lemma':
   forms=[cols[2]]+([v.strip() for v in cols[3].split(',')] if len(cols)>3 else [])
   for w in forms:
    if w in ('GAP!','PSEUDOGAP!') or not w:continue
    w=fold(w);words[lang][w].add(sid);lemmas[sid][lang].add(w)
  elif typ.rsplit(':',1)[-1]=='def':defs[sid][lang].append(cols[-1])
 counts[lang]={'source_records':n,'types':dict(types),'unique_forms':len(words[lang]),'sha256':sha(file)}
 assert words[lang],('Empty source',file)
# English OMW supplies lemmas only; import original Princeton glosses as data.
wn=Path('deps/wordnet/wn/data/wordnet-3.0');wn_hashes={}
for name in ('noun','verb','adj','adv'):
 file=wn/('data.'+name);wn_hashes[file.name]=sha(file)
 for line in file.read_text().splitlines():
  if not line or not line[0].isdigit():continue
  head,gloss=line.split('|',1);cols=head.split();pos=cols[2]
  if pos=='s':pos='a'
  sid=cols[0]+'-'+pos
  defs[sid]['en'].append(gloss.strip())
shutil.copy2(wn/'LICENSE',out/'LICENSE-Princeton-WordNet.txt')
print('SOURCE_COUNTS='+json.dumps(counts),flush=True)
# Parse ALL entries without truncating senses, definitions or translations.
pages=collections.defaultdict(bytearray);expected={};entries=0
def bucket(word,lang):
 h=0
 for c in word.encode():h=(h*131+c)%65536
 return h+(0 if lang=='es' else 65536)
for lang in ('es','en'):
 for word,sids in sorted(words[lang].items()):
  senses=[{'id':sid,'definition_en':defs[sid].get('en',[]),'definition_es':defs[sid].get('es',[]),
   'es':sorted(lemmas[sid].get('es',[])),'en':sorted(lemmas[sid].get('en',[]))} for sid in sorted(sids)]
  payload=json.dumps({'word':word,'language':lang,'senses':senses},ensure_ascii=False,separators=(',',':')).encode()
  key=bucket(word,lang);w=word.encode()
  pages[key]+=struct.pack('<HI',len(w),len(payload))+w+payload;entries+=1
  expected[(lang,word)]=payload.decode()
bankdir=out/'banks';bankdir.mkdir()
for k,data in pages.items():(bankdir/(str(k)+'.bin')).write_bytes(data)
maxpage=max(map(len,pages.values()))
assert maxpage<400000,('Page exceeds configured override budget',maxpage)
for lang,file in [('en',source/'wns/eng/LICENSE'),('es',source/'wns/mcr/LICENSE')]:
 shutil.copy2(file,out/('LICENSE-'+lang+'.txt'))
# Deterministic, portable complete dictionary; not a pretrained model.
with gzip.open(out/'dictionary-pages.jsonl.gz','wt',encoding='utf8') as f:
 for k,data in sorted(pages.items()):f.write(json.dumps({'page':k,'bytes':base64.b64encode(data).decode()})+'\n')
U=7400000000000000000;B=8700000000000000000
state=out/'state.rvp'
state.write_bytes(gzip.decompress(base64.b64decode(Path('ai/checkpoints/e030/preserved-patterns.rvp.gz.b64').read_text())))
seed_state=out/'before-dictionary.rvp';shutil.copy2(state,seed_state)
shutil.copy2(state,out/'dictionary-checkpoint.rvp')
spec=importlib.util.spec_from_file_location('snapshot',Path('ai/xi/knowledge/tests/native-knowledge.py'));m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
snapshot=m.snapshot
original=snapshot(state);oldhash=sha(seed_state);cached=-1;last=0;transcript=[];checks=0
def run(program):
 file=out/'transport.xi';file.write_text(program)
 return subprocess.check_output([runtime,'run',str(file),str(state),str(state)],text=True)
def query(word,lang):
 global cached,last,checks
 q=('@lex '+word).encode();assert len(q)<=255
 fields=[(U+16,1),(U+17,len(q)),(U+3,1 if lang=='es' else 2)]+[(U+128+i,v) for i,v in enumerate(q)]
 text='#!reverse-pc-machine-v1\n'+''.join('store8 %d %d\n'%x for x in fields)+prep.split('\n',1)[1]
 values=[json.loads(x)['value'] for x in run(text).splitlines() if x.startswith('{')]
 key=values[-1];assert key==bucket(fold(word),lang),'XI page selection differs'
 if cached!=key:
  data=pages.get(key,b'')
  program='#!reverse-pc-machine-v1\nset r0 0\nlabel clear\ncmp r0 %d\njge copied\nset r7 %d\nadd r7 r0\nstore8 $r7 0\nadd r0 1\njmp clear\nlabel copied\n'%(last,B+1024)
  fields=[(B+1024+i,v) for i,v in enumerate(data)]+[(B+16+i,(len(data)>>(8*i))&255) for i in range(3)]+[(B+8+i,(key>>(8*i))&255) for i in range(3)]
  program+=''.join('store8 %d %d\n'%x for x in fields)+'halt\n';run(program);cached=key;last=len(data)
 answer=subprocess.check_output([runtime,'app-turn',str(out/'dictionary.rxe'),str(state),str(state),lang,q.decode()],text=True).rstrip()
 transcript.append({'query':word,'language':lang,'page_selected_by_XI':key,'output':answer})
 return answer
# Subjects selected after ingest, absent from program source; no answer labels enter XI.
rng=random.Random(20261029);correct=0;baseline=0;unicode_cases=0;multi=0;samples=[]
for lang in ('es','en'):
 population=[w for w in words[lang] if len(w.encode())<=250]
 sample=rng.sample(sorted(population),64)
 # Include accented and multiword cases to exercise real UTF-8 transport.
 sample+=rng.sample(sorted(w for w in population if not w.isascii()),min(8,sum(not w.isascii() for w in population)))
 sample+=rng.sample(sorted(w for w in population if ' ' in w),8)
 for word in dict.fromkeys(sample):
  actual=query(word,lang);assert actual==expected[(lang,word)],(lang,word,actual[:100]);correct+=1;checks+=1
  unicode_cases+=int(not word.isascii());multi+=int(' ' in word)
  samples.append((lang,word))
for lang in ('es','en'):
 assert query('zzznopalabraqvxyz',lang)=='No consta en este diccionario.';checks+=1
assert subprocess.check_output([runtime,'app-turn',str(out/'dictionary.rxe'),str(state),str(state),'es','hola'],text=True).strip()=='Hola. Soy BBY Q.';checks+=1
current=snapshot(state)
# Only dictionary bank, UI transient and pre-existing conversation transient regions
# may change during queries; preserve the exact previously learned pattern block.
T=9200000000000000000
assert bytes(original[1].get(T+i,0) for i in range(3072))==bytes(current[1].get(T+i,0) for i in range(3072));checks+=1
assert original[0]==current[0] and original[2]==current[2];checks+=1
assert sha(seed_state)==oldhash;checks+=1
manifest={'source_repository':'omwn/omw-data','source_commit':'406bf83b3c507a3d1f26e88252d5d66893fd36bf',
 'wordnet_data_repository':'nltk/wordnet','wordnet_data_commit':'ce91915ae38a341ae845be4d825ef6003cddf395','wordnet_data_sha256':wn_hashes,
 'languages':counts,'entries':entries,'pages':len(pages),'max_page_bytes':maxpage,'stored_bytes':sum(map(len,pages.values())),
 'dictionary_gzip_sha256':sha(out/'dictionary-pages.jsonl.gz'),
 'dictionary_gzip_bytes':(out/'dictionary-pages.jsonl.gz').stat().st_size,
 'scope':'All lemma records/variants and senses supplied by the pinned Spanish and English Wordnets. Not every word of either language; dictionary reference acquisition, not demonstrated general understanding.'}
report={'version':'E031-Dictionary-1-dev','checks':checks,'native_exact_queries':correct,'unicode_cases':unicode_cases,'multiword_cases':multi,
 'unknown_controls':2,'candidate_sha256':sha(out/'dictionary.rxe'),'prior_checkpoint_sha256':oldhash,
 'prior_patterns_preserved':True,'same_RVPC2_agent':True,'source':manifest,
 'execution':'XI hashes full query, chooses page ID, compares full UTF-8 lemma, reads senses and emits data. Host transports complete pages without selecting answers.',
 'limitations':['Explicit @lex lookup transport required; not automatically incorporated into general conversation or old 512-entry grammar','Definitions may only be supplied in English; missing Spanish glosses remain missing','No new general reasoning demonstrated']}
(out/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
(out/'results.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
(out/'transcripts.jsonl').write_text(''.join(json.dumps(x,ensure_ascii=False)+'\n' for x in transcript))
print('DICTIONARY_RESULT_JSON='+json.dumps(report,ensure_ascii=False),flush=True)
