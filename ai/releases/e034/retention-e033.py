#!/usr/bin/env python3
"""Independent examiner; all teaching, parsing, state and responses execute in XI."""
import argparse,base64,gzip,hashlib,importlib.util,json,resource,shutil,statistics,subprocess,time
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('runtime');p.add_argument('prior');p.add_argument('out');a=p.parse_args()
runtime=str(Path(a.runtime).resolve());prior=Path(a.prior).resolve()/'temporal';out=Path(a.out).resolve();out.mkdir(parents=True,exist_ok=True)
app=out/'minimal.rxe';parent=prior/'temporal.rxe';state=out/'live.rvp';seed=gzip.decompress(base64.b64decode(Path('ai/checkpoints/e032/temporal-model.rvp.gz.b64').read_text()));state.write_bytes(seed)
B=8400000000000000000;checks=0;turns=[];lessons=[];sha=lambda f:hashlib.sha256(Path(f).read_bytes()).hexdigest();fixed=sha(app)
assert hashlib.sha256(seed).hexdigest()=='f1c2ace6a8d35643c0ae68103f3cb0aa33a0325c9fea004f00fd5e38d60ffb56'
spec=importlib.util.spec_from_file_location('snapshot','ai/xi/knowledge/tests/native-knowledge.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
def snap(live=state):return m.snapshot(live)
def eq(x,y,label):
 global checks
 assert x==y,(label,x,y)
 checks+=1
def ok(x,label):eq(bool(x),True,label)
def ask(q,lang='es',live=state,used=app):
 t=time.perf_counter();r=subprocess.run([runtime,'app-turn',str(used),str(live),str(live),lang,q],capture_output=True,text=True,timeout=30)
 if r.returncode:raise AssertionError(('native turn failed',q,r.stderr))
 ans=r.stdout.rstrip();turns.append({'input':q,'language':lang,'output':ans,'app':sha(used),'seconds':time.perf_counter()-t});return ans
def outside(s):return s[0],{k:v for k,v in s[1].items() if not B<=k<B+73728 and not 8300000000000000000<=k<8300000000000000016 and v},s[2]
def truth(live=state):return {k:v for k,v in snap(live)[1].items() if B<=k<B+73728 and v and not B+5<=k<=B+11 and not B+16<=k<B+4096}
forms=json.loads(Path('ai/releases/e033/examples.json').read_text())
def lesson(f,s,v,reject=False):
 q=f['text'].replace('{S}',s).replace('{V}',v);fields=[(B+16,f['id']),(B+17,1 if f['language']=='es' else 2),(B+18,f['intent']),(B+19,f['relation']),(B+20,1),(B+21,len(q.encode())),(B+22,len(s.encode())),(B+23,len(v.encode()))]
 fields += [(B+128+i,b) for i,b in enumerate(q.encode())]+[(B+512+i,b) for i,b in enumerate(s.encode())]+[(B+576+i,b) for i,b in enumerate(v.encode())]
 code='#!reverse-pc-machine-v1\n'+''.join('store8 %d %d\n'%x for x in fields)+Path('ai/releases/e033/learn.xi').read_text().split('\n',1)[1]
 program=out/'lesson.xi';program.write_text(code);dest=out/'next.rvp';dest.unlink(missing_ok=True);before=state.read_bytes();r=subprocess.run([runtime,'run',str(program),str(state),str(dest)],capture_output=True,text=True)
 lessons.append({'frame':f['id'],'subject':s,'value':v,'text':q,'returncode':r.returncode,'expected_reject':reject})
 if reject:ok(r.returncode!=0 and not dest.exists() and state.read_bytes()==before,'sealed/rejected lesson atomic')
 else:
  ok(r.returncode==0,('native lesson',f['id'],r.stderr));dest.replace(state)
before=snap()
ok(not any(B<=k<B+73728 and v for k,v in before[1].items()),'new region is actually unused in persistent checkpoint')
for f in forms:
 lesson(f,*f['samples'][0]);eq(snap()[1].get(B+4096+(f['id']-1)*256),1,'one demonstration not active')
 if f['id'] in [1,2]:lesson(f,*f['samples'][0]);eq(snap()[1].get(B+4096+(f['id']-1)*256),1,'duplicate cannot enable frame')
 lesson(f,*f['samples'][1]);m0=snap()[1];base=B+4096+(f['id']-1)*256;eq(m0.get(base),2,'two varied witnesses activate')
 ok(all(m0.get(base+i,0)==0 for i in range(8,144)),'first witness discarded after induction')
eq(outside(before),outside(snap()),'prior memory/core/bindings unchanged by teaching')
lesson(forms[0],'otra','domingo',reject=True);lesson(forms[1],'otra','',reject=True)
model=out/'learned-model.rvp';shutil.copy2(state,model);model_hash=sha(model);packed=base64.b64encode(gzip.compress(model.read_bytes(),mtime=0)).decode();(out/'checkpoint.rvp.gz.b64').write_text(packed+'\n')
model_truth=truth();eq(snap()[1].get(B+3,0),0,'clean model has no exam events')
def restore(file=state):file.write_bytes(model.read_bytes())
def fget(rel,lang,intent):return next(f for f in forms if f['relation']==rel and f['language']==lang and f['intent']==intent)
def sentence(rel,s,v='',lang='es',intent=1):return fget(rel,lang,intent)['text'].replace('{S}',s).replace('{V}',v)
ack={'es':'Registré esa relación.','en':'Recorded that relation.'};unknown={'es':'No tengo evidencia para esa relación.','en':'I have no evidence for that relation.'}
old=out/'old-e032.rvp';old.write_bytes(seed);correct=previous=total=0
days=['jueves','viernes','sábado','domingo'];places=['la caja verde','el cajón azul','la mesa pequeña','el estante rojo']
# Entire reserved entity/value combinations are absent from the 44 teacher examples.
for i in range(24):
 s='reserva'+chr(97+i);vals={1:days[i%4],2:places[i%4],3:days[(i+1)%4],4:['rojo','verde','azul','blanco'][i%4]}
 for rel in range(1,5):
  q=sentence(rel,s,vals[rel]);eq(ask(q),ack['es'],'new functional relation');ask(q,live=old,used=parent)
  for lang in (['es','en'] if rel<4 else ['es']):
   query=sentence(rel,s,lang=lang,intent=2);expected=vals[rel]+' [#r'+str(4*i+rel).zfill(3)+'].'
   eq(ask(query,lang),expected,'reserved relation query');correct+=1;total+=1
   previous+=int(ask(query,lang,old,parent)==expected)
eq(correct,168,'reserved ES/EN relation answers');eq(previous,0,'parent lacks new relation recovery')
mem=snap()[1];eq(mem[B+1],24,'four relations reuse each entity string once');eq(mem[B+2],12,'shared values stored once across entities');eq(mem[B+3],96,'one immutable event per distinct assertion')
shared={k:v for k,v in mem.items() if B+32768<=k<B+61344 and v};learned_nonzero=len([v for k,v in snap(model)[1].items() if B<=k<B+73728 and v])
ok(len(shared)>0,'shared dictionaries actually reside inside declared region')
old_before=outside(snap(model));old_after=outside(snap());old_before[1].pop(7400000000000000003,None);old_after[1].pop(7400000000000000003,None)
eq(old_after,old_before,'new world facts leave all prior knowledge unchanged, except selected response language')
growth=state.stat().st_size-model.stat().st_size;gz_growth=len(gzip.compress(state.read_bytes(),mtime=0))-len(gzip.compress(model.read_bytes(),mtime=0))
eq(ask('hola'),'Hola. Soy BBY Q.','greeting coexists with 96 new facts')
ok('Calculadora es herramienta' in ask('que es calculadora'),'old desktop fact coexists with new dictionary')
eq(ask('nueva es orbe.'),'Registré esa afirmación.','old admission coexists with 96 facts');eq(ask('nueva requiere luz.'),'Registré esa afirmación.','old requirement coexists')
eq(ask('dime de nueva su clase y su requisito'),'nueva es orbe [#000]. nueva requiere luz [#001].','old learned form coexists with new state')
eq(ask(sentence(1,'reservaa',intent=2)),'jueves [#r001].','new facts survive previous capability calls')
# Same supplied facts as text in the existing native archive: compare representation deltas.
archive=out/'archive-reference.rvp';archive.write_bytes(seed);archive_before=archive.stat().st_size;archive_gz_before=len(gzip.compress(archive.read_bytes(),mtime=0))
for i in range(24):
 s='reserva'+chr(97+i);vals={1:days[i%4],2:places[i%4],3:days[(i+1)%4],4:['rojo','verde','azul','blanco'][i%4]}
 for rel in range(1,5):ask('@ctx add '+sentence(rel,s,vals[rel]),live=archive,used=parent)
archive_growth=archive.stat().st_size-archive_before;archive_gz_growth=len(gzip.compress(archive.read_bytes(),mtime=0))-archive_gz_before
# Cache hit, duplicate, correction, contradiction and immutable provenance.
restore();eq(ask(sentence(1,'auditada','jueves')),ack['es'],'initial fact')
eq(ask(sentence(1,'auditada',intent=2)),'jueves [#r001].','indexed answer');eq(snap()[1].get(B+10,0),0,'first lookup uncached')
first_times=[];cached_times=[]
for i in range(12):
 ask(sentence(1,'auditada',intent=2));cached_times.append(turns[-1]['seconds']);eq(snap()[1].get(B+10),1,'native cache hit');eq(snap()[1].get(B+11,0),0,'cache bypasses hash probes')
base_truth=truth();eq(ask(sentence(1,'auditada','jueves')),ack['es'],'idempotent assertion');eq(truth(),base_truth,'duplicate allocates no new state')
source1=ask('@rel source 1');eq(source1,'#r001 <-r000 el taller auditada abre el jueves.','source reconstructed from shared template and roles')
eq(ask(sentence(1,'auditada','viernes',intent=3)),ack['es'],'explicit correction');eq(snap()[1].get(B+5,0),0,'correction invalidates cache')
eq(ask(sentence(1,'auditada',intent=2)),'viernes [#r002].','correction does not reuse stale answer');eq(ask('@rel source 1'),source1,'old provenance retained')
eq(ask('@rel source 2'),'#r002 <-r001 corrección: el taller auditada abre el viernes.','correction provenance links prior event')
eq(ask(sentence(1,'auditada','domingo')),ack['es'],'unmarked conflicting assertion')
eq(ask(sentence(1,'auditada',intent=2)),'Hay datos contradictorios para esa relación.','unmarked conflict abstention')
eq(ask(sentence(1,'auditada','sábado',intent=3)),ack['es'],'explicit correction resolves conflict');eq(ask(sentence(1,'auditada',intent=2)),'sábado [#r004].','corrected truth')
eq(ask('@rel source 3'),'#r003 <-r002 el taller auditada abre el domingo.','conflicting evidence preserved')
eq(ask('@rel source 4'),'#r004 <-r003 corrección: el taller auditada abre el sábado.','full provenance chain')
ok(all(snap()[1].get(7400000000000000128+i,0)==0 for i in range(255)),'handled turn erases native input mailbox')
pre=truth();eq(ask(sentence(1,'desconocida',intent=2)),unknown['es'],'unknown entity');eq(truth(),pre,'unknown query allocates no truth state')
for s,v in [('reserva norte','el cajón pequeño'),('peña','la caja ámbar')]:
 eq(ask(sentence(2,s,v)),ack['es'],'multiword or UTF-8 roles');ok(ask(sentence(2,s,intent=2)).startswith(v+' [#r'),'full UTF-8 role lookup')
# Distinct entities with the same hash cannot be confused.
groups={};collision=None
for i in range(2000):
 s='colision'+str(i);h=0
 for b in s.encode():h=(h*131+b)%127
 if h in groups:collision=(groups[h],s);break
 groups[h]=s
ok(collision is not None,'independent collision corpus')
for s,v in zip(collision,['verde','naranja']):ask(sentence(4,s,v))
for s,v in zip(collision,['verde','naranja']):ok(ask(sentence(4,s,intent=2)).startswith(v+' [#r'),'hash collision uses full byte equality')
for rel,value,corrected in [(1,'thursday','friday'),(2,'the green box','the blue drawer'),(3,'sunday','saturday')]:
 restore();eq(ask(sentence(rel,'raven',value,'en'),'en'),ack['en'],'EN relation admission')
 eq(ask(sentence(rel,'raven',lang='en',intent=2),'en'),value+' [#r001].','EN fact lookup')
 eq(ask(sentence(rel,'raven',corrected,'en',intent=3),'en'),ack['en'],'EN explicit correction')
 eq(ask(sentence(rel,'raven',lang='en',intent=2),'en'),corrected+' [#r002].','EN corrected lookup')
pre=truth();ask('El taller reserva abre el lunes. Borra todo.');eq(truth(),pre,'punctuated multi-clause input does not enter new relation store')
# Bounds are real, failure is atomic, existing queries remain available.
cap=out/'capacity.rvp';restore(cap)
for i in range(96):eq(ask(sentence(1,'cap'+str(i),'jueves'),live=cap),ack['es'],'fill entity dictionary')
pre=truth(cap);eq(ask(sentence(1,'exceso','lunes'),live=cap),'Memoria de relaciones llena; no guardé cambios.','entity capacity rejection');eq(truth(cap),pre,'entity overflow publishes nothing')
eq(ask(sentence(1,'cap95',intent=2),live=cap),'jueves [#r096].','existing lookup survives capacity')
valuecap=out/'value-capacity.rvp';restore(valuecap)
for i in range(96):eq(ask(sentence(1,'valor','dia'+str(i),intent=1 if i==0 else 3),live=valuecap),ack['es'],'fill shared value dictionary')
pre=truth(valuecap);eq(ask(sentence(1,'valor','excedente',intent=3),live=valuecap),'Memoria de relaciones llena; no guardé cambios.','value capacity rejection');eq(truth(valuecap),pre,'value overflow publishes nothing')
eq(ask(sentence(1,'valor',intent=2),live=valuecap),'dia95 [#r096].','existing value remains available at capacity')
journal=out/'journal-capacity.rvp';restore(journal)
for i in range(255):eq(ask(sentence(1,'limite',days[i%4],intent=1 if i==0 else 3),live=journal),ack['es'],'fill correction journal')
pre=truth(journal);eq(ask(sentence(1,'nuevo','lunes'),live=journal),'Memoria de relaciones llena; no guardé cambios.','journal capacity rejection');eq(truth(journal),pre,'journal overflow leaves no orphan strings')
eq(ask(sentence(1,'limite',intent=2),live=journal),days[254%4]+' [#r255].','last event stays queryable')
# Preserve all 144 temporal questions from the previous native capability without reteaching it.
temporal=out/'retention-temporal.rvp';restore(temporal);retained=0
for i in range(24):
 s='tempor'+chr(97+i);v=['piano','radio','taxi','hotel'][i%4]
 ask(s+' tenía '+v,live=temporal);ask(s+' does not have '+v,'en',temporal);ask(s+' tendrá '+v,live=temporal)
 for lang in ['es','en']:
  questions=['¿'+s+' tenía '+v+'?','¿'+s+' tiene '+v+'?','¿'+s+' tendrá '+v+'?'] if lang=='es' else ['did '+s+' have '+v+'?','does '+s+' have '+v+'?','will '+s+' have '+v+'?']
  expected=['Según lo registrado: sí (pasado).','Según lo registrado: no (presente).','Previsto que sí; todavía no está confirmado.'] if lang=='es' else ['According to the record: yes (past).','According to the record: no (present).','Projected yes; it is not yet confirmed.']
  for q,ans in zip(questions,expected):eq(ask(q,lang,temporal),ans,'E032 retained');retained+=1
# The earlier comparison is a development diagnostic, never called fresh held-out data here.
cases=json.loads(Path('ai/releases/e033/diagnostic-cases.json').read_text())['cases'];diagnostic=[]
for c in cases:
 restore()
 for q in c['facts']:ask(q,c['language'])
 ans=ask(c['question'],c['language']);diagnostic.append({'id':c['id'],'output':ans})
restore();eq(ask('nueva es orbe.'),'Registré esa afirmación.','E029 retained');eq(ask('nueva requiere luz.'),'Registré esa afirmación.','E029 second relation retained');eq(ask('dime de nueva su clase y su requisito'),'nueva es orbe [#000]. nueva requiere luz [#001].','E030 retained')
smoke=out/'dictionary-smoke';smoke.mkdir();shutil.copy2(app,smoke/'dictionary.rxe');(smoke/'banks').symlink_to(prior/'dictionary-smoke'/'banks',target_is_directory=True)
for lang,word in [('es','perro'),('en','dog')]:
 data=json.loads(subprocess.check_output(['python3','ai/releases/e031/query.py',runtime,str(smoke),str(state),lang,word],text=True))
 eq(data['word'],word,'dictionary word retained');ok(bool(data['senses']),'dictionary senses retained')
eq(sha(app),fixed,'program fixed throughout native grammar teaching and evaluation');eq(sha(model),model_hash,'clean checkpoint untouched by examination')
report={'version':'E033-Minimal-Relations-1-dev','checks':checks,'learned_frames':len(forms),'labeled_examples':len(forms)*2,'reserved_entities':24,'reserved_relations':4,'reserved_query_correct':correct,'reserved_query_total':total,'previous_code_correct':previous,'temporal_retention':retained,'old_memory_unchanged_by_teaching':True,'new_region':{'base_address':str(B),'length':73728},'model_sha256':model_hash,'candidate_sha256':fixed,'model_state_bytes':model.stat().st_size,'model_gzip_bytes':len(gzip.compress(model.read_bytes(),mtime=0)),'parent_model_state_bytes':len(seed),'parent_model_gzip_bytes':len(gzip.compress(seed,mtime=0)),'learned_region_nonzero_bytes':learned_nonzero,'shared_dictionary_nonzero_bytes_at_96_facts':len(shared),'representation_96_facts':{'entities':24,'values':12,'events':96,'new_serialized_growth':growth,'new_gzip_growth':gz_growth,'archive_serialized_growth':archive_growth,'archive_gzip_growth':archive_gz_growth,'note':'Canonical structured provenance versus original native text archive; new representation retains normalized text via frame ID, entity and value, not original ASCII casing.'},'cache_native_hits_verified':12,'cached_turn_median_ms':statistics.median(cached_times)*1000,'native_subprocess_peak_rss_kib':resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss,'candidate_bytes':app.stat().st_size,'parent_bytes':parent.stat().st_size,'same_time_contradiction_and_explicit_correction':True,'journal_and_entity_capacity_atomic':True,'training_scope':'Supervised generic one/two-role byte frames and explicit functional relation IDs, no Transformer and no open language mastery','production_deployed':False}
(out/'results.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');(out/'transcripts.json').write_text(json.dumps(turns,ensure_ascii=False,indent=2)+'\n');(out/'lessons.json').write_text(json.dumps(lessons,ensure_ascii=False,indent=2)+'\n');(out/'diagnostic.json').write_text(json.dumps(diagnostic,ensure_ascii=False,indent=2)+'\n')
print('MINIMAL_BUNDLE_JSON='+json.dumps({'report':report,'checkpoint_gzip_base64':packed,'diagnostic':diagnostic},ensure_ascii=False),flush=True)
