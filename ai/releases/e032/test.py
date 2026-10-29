#!/usr/bin/env python3
"""Independent oracle; role-labeled examples enter native XI, never templates/answers."""
import argparse,base64,gzip,hashlib,importlib.util,json,random,shutil,subprocess
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('runtime');p.add_argument('prior');p.add_argument('out');a=p.parse_args()
runtime=str(Path(a.runtime).resolve());prior=Path(a.prior).resolve()/'dictionary';out=Path(a.out).resolve();out.mkdir(parents=True,exist_ok=True)
app=out/'temporal.rxe';parent=prior/'dictionary.rxe';state=out/'live.rvp';state.write_bytes(gzip.decompress(base64.b64decode(Path('ai/checkpoints/e030/preserved-patterns.rvp.gz.b64').read_text())))
N=8650000000000000000;U=7400000000000000000;checks=0;turns=[];lessons=[]
sha=lambda f:hashlib.sha256(Path(f).read_bytes()).hexdigest()
fixed_hash=sha(app)
spec=importlib.util.spec_from_file_location('snapshot',Path('ai/xi/knowledge/tests/native-knowledge.py'));m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);snapshot=m.snapshot
def eq(x,y,label):
 global checks
 assert x==y,(label,x,y)
 checks+=1
def ok(x,label):eq(bool(x),True,label)
def memory():return snapshot(state)
def without_new(s):return s[0],{k:v for k,v in s[1].items() if not N<=k<N+86016 and v},s[2]
def rules(s):return bytes(s[1].get(N+4096+i,0) for i in range(64*256))
def events(s):return bytes(s[1].get(N+65536+i,0) for i in range(256*80))
def ask(q,lang='es',used=app,live=state):
 answer=subprocess.check_output([runtime,'app-turn',str(used),str(live),str(live),lang,q],text=True).rstrip()
 turns.append({'input':q,'language':lang,'output':answer,'app_sha256':sha(used)});return answer
forms=json.loads(Path('ai/releases/e032/examples.json').read_text())
def lesson(f,s,o,reject=False):
 q=f['text'].replace('{S}',s).replace('{O}',o)
 fields=[(N+16,f['id']),(N+17,1 if f['language']=='es' else 2),(N+18,f['intent']),(N+19,f['time']),(N+20,f['polarity']),(N+21,len(q.encode())),(N+22,len(s)),(N+23,len(o))]
 fields += [(N+128+i,b) for i,b in enumerate(q.encode())]+[(N+512+i,b) for i,b in enumerate(s.encode())]+[(N+544+i,b) for i,b in enumerate(o.encode())]
 code='#!reverse-pc-machine-v1\n'+''.join('store8 %d %d\n'%x for x in fields)+Path('ai/releases/e032/learn.xi').read_text().split('\n',1)[1]
 file=out/'lesson.xi';file.write_text(code);dest=out/'next.rvp';dest.unlink(missing_ok=True);before=state.read_bytes()
 r=subprocess.run([runtime,'run',str(file),str(state),str(dest)],text=True,capture_output=True)
 lessons.append({'frame':f['id'],'subject':s,'object':o,'text':q,'labels':[f['intent'],f['time'],f['polarity']],'rejected':reject,'returncode':r.returncode})
 if reject:ok(r.returncode!=0 and not dest.exists() and state.read_bytes()==before,'rejected lesson atomic')
 else:
  ok(r.returncode==0,('native teaching failed',f['id'],r.stderr));dest.replace(state)
# Same candidate code before/after grammar teaching.
baseline=ask('¿lucia tenía piano?')
ok(baseline!='No tengo evidencia para ese momento.','untrained grammar does not claim new temporal interpretation')
before=memory()
for f in forms:
 s,o=('maria','agua') if f['language']=='es' else ('mary','water')
 lesson(f,s,o)
 lesson(f,s,o) if f['id']==1 else None
 eq(memory()[1].get(N+4096+(f['id']-1)*256),1,'single or duplicate witness disabled')
 s,o=('pedro','pan') if f['language']=='es' else ('peter','bread')
 lesson(f,s,o)
 eq(memory()[1].get(N+4096+(f['id']-1)*256),2,'two varied roles enabled')
eq(without_new(before),without_new(memory()),'teaching changes only declared temporal region')
eq(sha(app),fixed_hash,'same code before and after teaching')
lesson(forms[0],'otra','sal',reject=True)
model=memory();shutil.copy2(state,out/'learned-temporal-checkpoint.rvp')
packed=base64.b64encode(gzip.compress(state.read_bytes(),mtime=0)).decode()
(out/'checkpoint.rvp.gz.b64').write_text(packed+'\n')
# Reopen exact compressed checkpoint: no re-teaching during examination.
state.write_bytes(gzip.decompress(base64.b64decode(packed)))
model_hash=sha(state)
unknown={'es':'No tengo evidencia para ese momento.','en':'I have no evidence for that time.'}
ack={('es',1):'Registrado en pasado.',('es',2):'Registrado en presente.',('es',3):'Registrado como previsión futura.',('en',1):'Recorded in the past.',('en',2):'Recorded in the present.',('en',3):'Recorded as a future projection.'}
def question(s,o,t,l,relative=False):
 if l=='es':
  v=['tenía','tiene','tendrá'][t-1];tail=[' ayer',' ahora',' mañana'][t-1] if relative else ''
  return '¿'+s+' '+v+' '+o+tail+'?'
 return ['did '+s+' have '+o,'does '+s+' have '+o,'will '+s+' have '+o][t-1]+([' yesterday',' now',' tomorrow'][t-1] if relative else '')+'?'
def statement(s,o,t,l,negative=False,relative=False):
 verb=(['no tenía','no tiene','no tendrá'] if negative else ['tenía','tiene','tendrá'])[t-1] if l=='es' else (['did not have','does not have','will not have'] if negative else ['had','has','will have'])[t-1]
 cue=(['ayer','hoy','mañana'] if l=='es' else ['yesterday','today','tomorrow'])[t-1]+' ' if relative else ''
 return cue+s+' '+verb+' '+o
def answer(t,l,neg=False):
 if t==3:return ('Previsto que no; todavía no está confirmado.' if neg else 'Previsto que sí; todavía no está confirmado.') if l=='es' else ('Projected no; it is not yet confirmed.' if neg else 'Projected yes; it is not yet confirmed.')
 return ('Según lo registrado: '+('no' if neg else 'sí')+' ('+('pasado' if t==1 else 'presente')+').') if l=='es' else ('According to the record: '+('no' if neg else 'yes')+' ('+('past' if t==1 else 'present')+').')
correct=0;isolation=0;ablation=0
old_state=out/'parent-ablation.rvp'
# Facts taught on 24 subjects and four objects absent from grammar examples.
for i in range(24):
 s='tempor'+chr(97+i);o=['piano','radio','taxi','hotel'][i%4]
 eq(ask(statement(s,o,1,'es',relative=i%2==0)),ack[('es',1)],'record past')
 # Past evidence cannot answer a present or future question.
 for l in ['es','en']:
  eq(ask(question(s,o,2,l),l),unknown[l],'past does not imply present');isolation+=1
  eq(ask(question(s,o,3,l),l),unknown[l],'past does not imply future');isolation+=1
 eq(ask(statement(s,o,2,'en',negative=True,relative=i%2==0),'en'),ack[('en',2)],'record negative present')
 eq(ask(statement(s,o,3,'es',relative=i%2==1)),ack[('es',3)],'record future projection')
 shutil.copy2(state,old_state)
 for t in [1,2,3]:
  for l in ['es','en']:
   eq(ask(question(s,o,t,l,relative=i%2==1),l),answer(t,l,t==2),'reserved temporal query')
   correct+=1
   ablation+=int(ask(question(s,o,t,l,relative=i%2==1),l,parent,old_state)==answer(t,l,t==2))
eq(ablation,0,'previous code does not supply new temporal answers on same memory')
eq(correct,144,'reserved exact temporal questions')
# Questioning never writes new events or adapts frames.
pre_events=events(memory());pre_rules=rules(memory())
for l in ['es','en']:eq(ask(question('ausente','piano',2,l),l),unknown[l],'unknown entity')
eq(events(memory()),pre_events,'queries do not publish facts')
eq(rules(memory()),pre_rules,'queries do not adapt learned grammar')
# Same-time contradiction does not invalidate other time buckets.
eq(ask(statement('tempora','piano',2,'es')),ack[('es',2)],'conflicting present assertion')
eq(ask(question('tempora','piano',2,'es')),'Hay afirmaciones contradictorias para ese momento.','contradiction abstention')
eq(ask(question('tempora','piano',1,'en'),'en'),answer(1,'en'),'past survives present conflict')
eq(ask(question('tempora','piano',3,'es')),answer(3,'es'),'future remains projected')
# A future assertion alone cannot become a current fact.
eq(ask(statement('futura','robot',3,'en'),'en'),ack[('en',3)],'future-only event')
eq(ask(question('futura','robot',2,'es')),unknown['es'],'future is not present')
eq(ask(question('futura','robot',1,'en'),'en'),unknown['en'],'future is not past')
for t,subject in [(1,'negpast'),(3,'negfuture')]:
 eq(ask(statement(subject,'laser',t,'en',negative=True),'en'),ack[('en',t)],'negative tense record')
 eq(ask(question(subject,'laser',t,'es')),answer(t,'es',True),'negative temporal answer')
for q in ['ayer futura tiene robot','futura tenía robot mañana','futura will have robot yesterday']:
 pre=events(memory());ask(q);eq(events(memory()),pre,'unsupported conflicting cues do not add events')
# E030 learned forms still operate after native temporal learning.
eq(ask('nueva es orbe.'),'Registré esa afirmación.','E029 preserved')
eq(ask('nueva requiere luz.'),'Registré esa afirmación.','E029 second relation')
eq(ask('dime de nueva su clase y su requisito'),'nueva es orbe [#000]. nueva requiere luz [#001].','E030 learned form retained')
eq(ask('hola'),'Hola. Soy BBY Q.','original greeting')
eq(rules(memory()),rules(model),'rule model retained across all conversations')
eq(sha(app),fixed_hash,'candidate executable unchanged throughout')
# Reuse existing dictionary transport against new temporal capsule, no dictionary reimport.
smoke=out/'dictionary-smoke';smoke.mkdir()
shutil.copy2(app,smoke/'dictionary.rxe')
(smoke/'banks').symlink_to(prior/'banks',target_is_directory=True)
for lang,word in [('es','perro'),('en','dog')]:
 raw=subprocess.check_output(['python3','ai/releases/e031/query.py',runtime,str(smoke),str(state),lang,word],text=True)
 data=json.loads(raw);eq(data['word'],word,'dictionary word retained');ok(bool(data['senses']),'dictionary senses retained')
report={'version':'E032-Temporal-1-dev','checks':checks,'learned_frames':len(forms),'labeled_examples':2*len(forms),'reserved_subjects':24,
 'exact_temporal_queries':correct,'total_temporal_queries':144,'cross_time_isolation_controls':isolation,
 'previous_code_exact':ablation,'future_assertions_marked_unconfirmed':True,'same_time_conflict_abstains':True,
 'candidate_sha256_before':fixed_hash,'candidate_sha256_after':sha(app),
 'learned_checkpoint_sha256':model_hash,'parent_checkpoint_sha256':'18030f0c4e7098a0d19d07c3b3a93507d982caa1ae70e047bd9c2d118e9a3d4b',
 'learning_region':{'base_address':str(N),'length':86016},'old_memory_unchanged_by_teaching':True,
 'scope':'Learned two-role possession frames, three relative tense buckets, single-token entity/object, explicit supervised time labels. Same surface referents across languages; no general translation/date/aspect/mood mastery.',
 'native_process_per_turn':True,'production_deployed':False}
(out/'results.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
(out/'transcripts.jsonl').write_text(''.join(json.dumps(x,ensure_ascii=False)+'\n' for x in turns))
(out/'teaching.json').write_text(json.dumps(lessons,ensure_ascii=False,indent=2)+'\n')
print('TEMPORAL_BUNDLE_JSON='+json.dumps({'report':report,'checkpoint_gzip_base64':packed}),flush=True)
