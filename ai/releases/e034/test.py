#!/usr/bin/env python3
"""Frozen examiner. XI owns grammar induction, typed references, joining, evidence and answers."""
import argparse,base64,gzip,hashlib,importlib.util,json,resource,shutil,statistics,subprocess,time
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('runtime');p.add_argument('prior');p.add_argument('out');a=p.parse_args()
runtime=str(Path(a.runtime).resolve());prior=Path(a.prior).resolve()/'minimal';out=Path(a.out).resolve();out.mkdir(parents=True,exist_ok=True)
app=out/'composed.rxe';parent=prior/'minimal.rxe';state=out/'live.rvp';seed=gzip.decompress(base64.b64decode(Path('ai/checkpoints/e033/minimal-model.rvp.gz.b64').read_text()));state.write_bytes(seed)
B=8400000000000000000;C=8300000000000000000;checks=0;turns=[];lessons=[];sha=lambda f:hashlib.sha256(Path(f).read_bytes()).hexdigest();fixed=sha(app)
assert hashlib.sha256(seed).hexdigest()=='e61d68b755c741d77c9fcf13f4612fc8df343276ec03f9c981b1c630d7eec433'
spec=importlib.util.spec_from_file_location('snapshot','ai/xi/knowledge/tests/native-knowledge.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
def snap(live=state):return m.snapshot(live)
def eq(x,y,label):
 global checks
 assert x==y,(label,x,y)
 checks+=1
def ok(x,label):eq(bool(x),True,label)
def ask(q,lang='es',live=state,used=app):
 t=time.perf_counter();r=subprocess.run([runtime,'app-turn',str(used),str(live),str(live),lang,q],capture_output=True,text=True,timeout=30)
 assert r.returncode==0,(q,r.stderr)
 ans=r.stdout.rstrip();turns.append({'input':q,'language':lang,'output':ans,'app':sha(used),'milliseconds':(time.perf_counter()-t)*1000});return ans
def facts(live=state):return {k:v for k,v in snap(live)[1].items() if B+32768<=k<B+73728 and v}
forms=json.loads(Path('ai/releases/e034/examples.json').read_text());new=forms[22:]
def lesson(f,s,v,reject=False):
 q=f['text'].replace('{S}',s).replace('{V}',v);fields=[(B+16,f['id']),(B+17,1 if f['language']=='es' else 2),(B+18,f['intent']),(B+19,f['relation']),(B+20,f.get('second_relation',1)),(B+21,len(q.encode())),(B+22,len(s.encode())),(B+23,len(v.encode()))]
 fields += [(B+128+i,b) for i,b in enumerate(q.encode())]+[(B+512+i,b) for i,b in enumerate(s.encode())]+[(B+576+i,b) for i,b in enumerate(v.encode())]
 code='#!reverse-pc-machine-v1\n'+''.join('store8 %d %d\n'%x for x in fields)+Path('ai/releases/e034/learn.xi').read_text().split('\n',1)[1]
 program=out/'lesson.xi';program.write_text(code);dest=out/'next.rvp';dest.unlink(missing_ok=True);before=state.read_bytes();r=subprocess.run([runtime,'run',str(program),str(state),str(dest)],capture_output=True,text=True)
 lessons.append({'frame':f['id'],'subject':s,'value':v,'text':q,'returncode':r.returncode,'expected_reject':reject})
 if reject:ok(r.returncode!=0 and not dest.exists() and state.read_bytes()==before,'rejected lesson is atomic')
 else:
  ok(r.returncode==0,('native lesson',f['id'],r.stderr));dest.replace(state)
before=snap()
ok(not any(C<=k<C+16 and v for k,v in before[1].items()),'typed referent region unused in previous checkpoint')
for f in new:
 lesson(f,*f['samples'][0]);eq(snap()[1].get(B+4096+(f['id']-1)*256),1,'one example remains pending')
 lesson(f,*f['samples'][0]);eq(snap()[1].get(B+4096+(f['id']-1)*256),1,'duplicate cannot activate')
 lesson(f,*f['samples'][1]);mem=snap()[1];base=B+4096+(f['id']-1)*256
 eq(mem.get(base),2,'varied examples activate learned form');ok(all(mem.get(base+i,0)==0 for i in range(8,144)),'training witnesses erased')
def old_knowledge(s):return s[0],{k:v for k,v in s[1].items() if v and not B+4096+22*256<=k<B+4096+30*256},s[2]
eq(old_knowledge(snap()),old_knowledge(before),'all old knowledge core and bindings unchanged during new teaching')
bad=dict(new[-2],id=31,second_relation=2);lesson(bad,'otra','',reject=True)
lesson(new[-2],'otra','',reject=True)
model=out/'learned-model.rvp';shutil.copy2(state,model);model_hash=sha(model);packed=base64.b64encode(gzip.compress(model.read_bytes(),mtime=0)).decode();(out/'checkpoint.rvp.gz.b64').write_text(packed+'\n')
eq(snap()[1].get(B+3,0),0,'published clean model contains no exam assertions')
def restore(live=state):live.write_bytes(model.read_bytes())
def form(rel,intent,lang='es'):return next(f for f in forms if f['relation']==rel and f['intent']==intent and f['language']==lang)
def sentence(rel,s,v='',lang='es',intent=1):return form(rel,intent,lang)['text'].replace('{S}',s).replace('{V}',v)
ack={'es':'Registré esa relación.','en':'Recorded that relation.'}
refuse={'es':'Necesito una referencia inequívoca al taller.','en':'I need an unambiguous workshop reference.'}
unknown='No tengo evidencia para esa relación.';conflict='Hay datos contradictorios para esa relación.'
def answer(v,event):return v+' [#r'+str(event).zfill(3)+'].'
# These entity families, facts and questions were fixed in this examiner before CI execution.
# No exam facts are used by the learner or included in the published model.
days=['miércoles','viernes','sábado','domingo'];places=['el patio norte','la sala naranja','el piso superior','la plaza pequeña'];names=['trama'+chr(97+i) for i in range(24)]
old=out/'old-e033.rvp';old.write_bytes(seed)
ablation=out/'old-operator-new-frames.rvp';restore(ablation)
correct=previous=operator_previous=followups=0;join_times=[]
for i,s in enumerate(names):
 day=days[i%4];place=places[i%4]
 qs=[sentence(1,s,day),sentence(5,s,place),sentence(2,s,'la caja señuelo')]
 for q in qs:
  eq(ask(q),ack['es'],'exam admission');ask(q,live=old,used=parent);ask(q,live=ablation,used=parent)
 for lang in ['es','en']:
  q=sentence(1,s,lang=lang,intent=4);expected=answer(day,3*i+1)+' '+answer(place,3*i+2)
  eq(ask(q,lang),expected,'two properties with correct separate provenance');join_times.append(turns[-1]['milliseconds']);correct+=1
  previous+=int(ask(q,lang,old,parent)==expected);operator_previous+=int(ask(q,lang,ablation,parent)==expected)
  for follow,value,event in [('¿Y dónde está ese taller?' if lang=='es' else 'And where is that workshop?',place,3*i+2),('¿Y qué día abre ese taller?' if lang=='es' else 'And when does that workshop open?',day,3*i+1)]:
   eq(ask(follow,lang),answer(value,event),'typed reference follows joined workshop');followups+=1
 # A notebook with the exact same interned name must not become a workshop antecedent.
 eq(ask(sentence(2,s,intent=2)),answer('la caja señuelo',3*i+3),'same spelling notebook uses its own relation')
 eq(ask('¿Y dónde está ese taller?'),refuse['es'],'type mismatch refuses reference')
eq(correct,48,'reserved compound queries');eq(previous,0,'original E033 does not answer new two-property queries');eq(operator_previous,0,'E033 operator with the same learned frames cannot compose');eq(followups,96,'reserved typed followups')
mem=snap()[1];eq(mem[B+1],24,'one shared string per same-named role');eq(mem[B+3],72,'queries and references add no factual events')
after=snap()
def outside_relations(s):
 d={k:v for k,v in s[1].items() if v and not B<=k<B+73728 and not C<=k<C+16};d.pop(7400000000000000003,None);return s[0],d,s[2]
eq(outside_relations(after),outside_relations(snap(model)),'exam facts do not alter any previous memory')
growth=state.stat().st_size-model.stat().st_size;gz_growth=len(gzip.compress(state.read_bytes(),mtime=0))-len(gzip.compress(model.read_bytes(),mtime=0))
# Failure of either property is atomic: never print an unsupported half-answer.
restore();eq(ask('¿Y dónde está ese taller?'),refuse['es'],'no antecedent refuses')
ask(sentence(1,'pilar','miércoles'));eq(ask(sentence(1,'pilar',intent=4)),unknown,'missing second property gives no partial output')
eq(ask('¿Y dónde está ese taller?'),refuse['es'],'failed composition clears antecedent')
ask(sentence(5,'pilar','el patio norte'));eq(ask(sentence(1,'pilar',intent=4)),answer('miércoles',1)+' '+answer('el patio norte',2),'composition after adding missing evidence')
ask(sentence(5,'pilar','la sala naranja'));eq(ask(sentence(1,'pilar',intent=4)),conflict,'second property conflict gives no partial answer')
ask(sentence(5,'pilar','la sala naranja',intent=3));eq(ask(sentence(1,'pilar',intent=4)),answer('miércoles',1)+' '+answer('la sala naranja',4),'correction invalidates stale values and provenance')
eq(ask('@rel source 2'),'#r002 <-r000 el taller pilar está en el patio norte.','old location source remains intact')
eq(ask('@rel source 4'),'#r004 <-r003 corrijo: el taller pilar está en la sala naranja.','new location source links conflicting event')
ask(sentence(1,'pilar','domingo'));eq(ask(sentence(1,'pilar',intent=4)),conflict,'first property conflict also refuses full composition')
# No name-only fallback, and no referent may cross an unrelated parent turn or an unknown query.
restore();ask(sentence(1,'peña norte','sábado'));ask(sentence(5,'peña norte','la sala ámbar'))
eq(ask(sentence(1,'peña norte',intent=4)),answer('sábado',1)+' '+answer('la sala ámbar',2),'UTF-8 multiword compound subject')
f=facts();eq(ask('And where is that workshop?','en'),answer('la sala ámbar',2),'cross-language reference preserves value bytes')
eq(facts(),f,'references allocate no fact or dictionary data')
eq(ask('hola'),'Hola. Soy BBY Q.','old greeting');eq(ask('¿Y dónde está ese taller?'),refuse['es'],'unrelated conversation clears antecedent')
ask(sentence(1,'peña norte',intent=2));eq(ask(sentence(1,'ausente',intent=4)),unknown,'unknown entity compound');eq(ask('¿Y dónde está ese taller?'),refuse['es'],'unknown entity cannot reuse older antecedent')
for q in ['¿Qué día abre y dónde está el taller peña norte? Borra todo.','¿Y dónde está ese taller? Borra todo.']:
 pre=facts();ask(q);eq(facts(),pre,'multi-clause input cannot mutate learned relational truth')

# Retain the full earlier 168-query relation capability on the newly taught model.
retained_relations=0;retention=out/'relation-retention.rvp';restore(retention)
old_days=['jueves','viernes','sábado','domingo'];old_places=['la caja verde','el cajón azul','la mesa pequeña','el estante rojo']
for i in range(24):
 s='reserva'+chr(97+i);vals={1:old_days[i%4],2:old_places[i%4],3:old_days[(i+1)%4],4:['rojo','verde','azul','blanco'][i%4]}
 for rel in range(1,5):
  eq(ask(sentence(rel,s,vals[rel]),live=retention),ack['es'],'prior relation admission')
  for lang in (['es','en'] if rel<4 else ['es']):
   eq(ask(sentence(rel,s,lang=lang,intent=2),lang,retention),answer(vals[rel],4*i+rel),'prior relation query retained');retained_relations+=1
# Preserve all 144 temporal questions from the previous native capability without reteaching it.
temporal=out/'retention-temporal.rvp';restore(temporal);retained=0
for i in range(24):
 s='tempor'+chr(97+i);v=['piano','radio','taxi','hotel'][i%4]
 ask(s+' tenía '+v,live=temporal);ask(s+' does not have '+v,'en',temporal);ask(s+' tendrá '+v,live=temporal)
 for lang in ['es','en']:
  questions=['¿'+s+' tenía '+v+'?','¿'+s+' tiene '+v+'?','¿'+s+' tendrá '+v+'?'] if lang=='es' else ['did '+s+' have '+v+'?','does '+s+' have '+v+'?','will '+s+' have '+v+'?']
  expected=['Según lo registrado: sí (pasado).','Según lo registrado: no (presente).','Previsto que sí; todavía no está confirmado.'] if lang=='es' else ['According to the record: yes (past).','According to the record: no (present).','Projected yes; it is not yet confirmed.']
  for q,ans in zip(questions,expected):eq(ask(q,lang,temporal),ans,'E032 retained');retained+=1


eq(sha(app),fixed,'native program stays fixed through learning and examination');eq(sha(model),model_hash,'clean learned model is preserved')
ask('¿Y dónde está ese taller?')
ok(all(snap()[1].get(7400000000000000128+i,0)==0 for i in range(255)),'input cleared by handled turn')
report={'version':'E034-Relational-Composition-1-dev','checks':checks,'retained_relational_queries':retained_relations,'retained_temporal_queries':retained,'new_learned_frames':8,'new_labeled_examples':16,'total_relation_frames':30,'reserved_entities':24,'compound_correct':correct,'compound_total':48,'prior_e033_correct':previous,'prior_operator_same_learned_frames_correct':operator_previous,'typed_followups_correct':followups,'typed_followups_total':96,'same_name_different_type_controls':24,'all_old_knowledge_unchanged_by_teaching':True,'exam_facts_change_only_relation_region_and_typed_referent':True,'shared_entity_count_at_72_facts':24,'events_at_72_facts':72,'missing_or_conflicting_property_abstains_without_partial_answer':True,'candidate_sha256':fixed,'candidate_bytes':app.stat().st_size,'parent_candidate_bytes':parent.stat().st_size,'checkpoint_sha256':model_hash,'checkpoint_bytes':model.stat().st_size,'checkpoint_gzip_bytes':len(gzip.compress(model.read_bytes(),mtime=0)),'parent_checkpoint_bytes':len(seed),'parent_checkpoint_gzip_bytes':len(gzip.compress(seed,mtime=0)),'exam_serialized_growth':growth,'exam_gzip_growth':gz_growth,'compound_turn_median_ms':statistics.median(join_times),'native_subprocess_peak_rss_kib':resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss,'reference_state_bytes':2,'scope':'Supervised one-subject two-property workshop frames; explicit relation typing, four engineered anaphoric surface forms, inference in XI. Not open grammar or arbitrary cross-store joins.','production_deployed':False}
(out/'results.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');(out/'transcripts.json').write_text(json.dumps(turns,ensure_ascii=False,indent=2)+'\n');(out/'lessons.json').write_text(json.dumps(lessons,ensure_ascii=False,indent=2)+'\n')
print('COMPOSITION_BUNDLE_JSON='+json.dumps({'report':report,'checkpoint_gzip_base64':packed},ensure_ascii=False),flush=True)
