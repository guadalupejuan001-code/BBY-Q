#!/usr/bin/env python3
"""Independent examiner and byte transport; all learning and inference run in XI."""
import argparse, hashlib, importlib.util, json, shutil, subprocess
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('runtime');p.add_argument('build');p.add_argument('output');a=p.parse_args()
runtime=str(Path(a.runtime).resolve());root=Path(a.build).resolve();out=Path(a.output).resolve();out.mkdir(parents=True,exist_ok=True)
spec=importlib.util.spec_from_file_location('knowledge_exam',Path('ai/xi/knowledge/tests/native-knowledge.py'))
knowledge=importlib.util.module_from_spec(spec);spec.loader.exec_module(knowledge)
snapshot=knowledge.snapshot
T=9200000000000000000
app=root/'learned.rxe';parent=root/'e029-baseline.rxe';state=out/'state.rvp'
shutil.copy2(root/'controller.rvp',state)
sha=lambda f:hashlib.sha256(Path(f).read_bytes()).hexdigest()
fixed_hash=sha(app);checks=0;transcript=[];training=[]
def check(v,label):
 global checks
 assert v,label
 checks+=1
def eq(x,y,label):check(x==y,(label,x,y))
def ask(q,lang='es',used=app,live=state):
 result=subprocess.check_output([runtime,'app-turn',str(used),str(live),str(live),lang,q],text=True).rstrip()
 transcript.append({'input':q,'language':lang,'app_sha256':sha(used),'output':result})
 return result
def memento():return snapshot(state)
def learned_memory(snap):return {k:v for k,v in snap[1].items() if T<=k<T+3072 and v}
def outside(snap):return snap[0],{k:v for k,v in snap[1].items() if not T<=k<T+3072 and v},snap[2]
def teach(rule,lang,subject,q,reject=False):
 # The tutor supplies observations and roles, not prefix/suffix, masks or answers.
 fields=[(T+16,1 if lang=='es' else 2),(T+17,len(q.encode())),(T+18,len(subject)),(T+19,rule),(T+20,1)]
 fields += [(T+128+i,b) for i,b in enumerate(q.encode())]+[(T+400+i,b) for i,b in enumerate(subject.encode())]
 program=out/'lesson.xi'
 source=Path('ai/releases/e030/learn.xi').read_text().split('\n',1)[1]
 program.write_text('#!reverse-pc-machine-v1\n'+''.join('store8 %d %d\n'%pair for pair in fields)+source)
 before=state.read_bytes();destination=out/'next.rvp';destination.unlink(missing_ok=True)
 result=subprocess.run([runtime,'run',str(program),str(state),str(destination)],capture_output=True,text=True)
 training.append({'rule':rule,'language':lang,'subject_role':subject,'query':q,'rejected':reject,
  'returncode':result.returncode,'stderr':result.stderr[-1000:]})
 if reject:
  check(result.returncode!=0 and not destination.exists() and state.read_bytes()==before,'rejected lesson atomic')
 else:
  check(result.returncode==0,('XI lesson failed',result.stderr))
  destination.replace(state)
def form(subject,lang):
 return ('dime de '+subject+' su clase y su requisito' if lang=='es' else
         'outline for '+subject+' its class and its requirement')
def canonical(subject,lang):
 return 'que es '+subject+' y que requiere' if lang=='es' else 'what is '+subject+' and what does it need'
def expected(subject,klass,need,n,lang):
 return (subject+' es '+klass+' [#%03d]. '%n+subject+' requiere '+need+' [#%03d].'%(n+1) if lang=='es' else
  subject+' is '+klass+' [#%03d]. '%n+subject+' needs '+need+' [#%03d].'%(n+1))
rows=[]
# Facts for the examination are learned normally, before any syntax demonstration.
# All 24 subjects are disjoint from the two labeled grammar subjects.
for i in range(24):
 s='reserva'+chr(97+i);cl='clase'+str(i);need='recurso'+str(i)
 eq(ask(s+' es '+cl+'.'),'Registré esa afirmación.','E029 acquisition')
 eq(ask(s+' requiere '+need+'.'),'Registré esa afirmación.','E029 second fact')
 rows.append((s,cl,need,2*i))
check('Aprendí' in ask('aprende que legado es animal'),'prior E025 teaching')
shutil.copy2(state,out/'before-learning.rvp')
baseline=0
for s,cl,need,n in rows:
 for lang in ['es','en']:
  baseline+=int(ask(form(s,lang),lang)==expected(s,cl,need,n,lang))
eq(baseline,0,'unsupported forms before learning')
pre=memento()
# One witness and a duplicate may not license the variable.
teach(1,'es','tutora',form('tutora','es'))
teach(1,'es','tutora',form('tutora','es'))
eq(memento()[1].get(T+1024),1,'duplicate cannot enable pattern')
check(ask(form(rows[0][0],'es'))!=expected(*rows[0],'es'),'one witness remains inactive')
# Deliberately incompatible demonstration must not alter even a pending rule.
teach(1,'es','tutorb','dime de tutorb otra clase y otro requisito',reject=True)
# Capture immediately around teaching so normal conversational focus is not confused with learning writes.
before_teach=memento()
teach(1,'es','tutorb',form('tutorb','es'))
teach(2,'en','tutora',form('tutora','en'))
teach(2,'en','tutorb',form('tutorb','en'))
after_teach=memento()
eq(outside(before_teach),outside(after_teach),'only declared learned region changes during native teaching')
eq(after_teach[1].get(T+1024),2,'Spanish enabled from distinct witnesses')
eq(after_teach[1].get(T+1280),2,'English enabled from distinct witnesses')
check(all(after_teach[1].get(T+i,0)==0 for i in range(16,1024)),'teacher mailbox and scratch clean')
# Active records are sealed against accidental replacement.
teach(1,'es','tutorc',form('tutorc','es'),reject=True)
shutil.copy2(state,out/'learned-checkpoint.rvp')
learned_model=learned_memory(memento())
score=0;old_code_score=0
ablation=out/'ablation.rvp';shutil.copy2(state,ablation)
for s,cl,need,n in rows:
 for lang in ['es','en']:
  answer=ask(form(s,lang),lang)
  eq(answer,expected(s,cl,need,n,lang),'reserved subject with learned frame')
  eq(answer,ask(canonical(s,lang),lang),'canonical old capability retained')
  score+=1
  old_code_score+=int(ask(form(s,lang),lang,parent,ablation)==expected(s,cl,need,n,lang))
eq(old_code_score,0,'E029 code ignores new model records: ablation')
eq(sha(app),fixed_hash,'fixed capsule before and after learning')
eq(learned_memory(memento()),learned_model,'evaluation does not adapt learned descriptors')
eq(ask(form('ausente','es')),'Falta evidencia para combinar ambas propiedades.','unknown subject abstains')
eq(ask('negra es animal.'),'Registré esa afirmación.','negative-control subject')
eq(ask('negra requiere agua.'),'Registré esa afirmación.','negative-control property')
eq(ask('negra no requiere agua.'),'Registré esa afirmación.','negative evidence')
eq(ask(form('negra','es')),'Evidencia negativa o contradictoria; no puedo afirmar esa propiedad.','learned frame keeps negative evidence policy')
for q in [form('reserva a','es'),form('reservaa','es')+' extra',
          'no '+form('reservaa','es'),form('reservaa y reservab','es'),
          form('x'*32,'es')]:
 answer=ask(q)
 check(answer!=expected(*rows[0],'es'),'near-match/mixed/overlong does not reuse positive answer')
eq(ask('@ctx get 0'),'#000 reservaa es clase0','original archive remains inspectable')
eq(ask('@ctx clear'),'CTX vaciado.','archive clear')
check('animal' in ask('que es legado'),'E025 fact retained')
eq(learned_memory(memento()),learned_model,'clearing context preserves learned patterns')
eq(ask('nueva es orbe.'),'Registré esa afirmación.','new post-clear fact')
eq(ask('nueva requiere luz.'),'Registré esa afirmación.','new post-clear need')
eq(ask(form('nueva','en'),'en'),expected('nueva','orbe','luz',0,'en'),'pattern survives clear and process restart')
check(all(memento()[1].get(T+i,0)==0 for i in range(16,1024)),'inference scratch clean')
# Persist final state separately; the saved learned checkpoint remains available.
shutil.copy2(state,out/'after-evaluation.rvp')
eq(sha(root/'controller.rvp'),'ce058a65092dd9892b6fd55276a17287b764a16bc526ccbfa0085154baef9631','authentic seed unchanged')
report={'version':'E030-Learned-Frames-1-dev','checks':checks,
 'reserved_subjects':24,'grammar_training_subjects':['tutora','tutorb'],
 'scores':{'before_learning':baseline,'after_learning':score,'e029_code_on_learned_memory':old_code_score,'total':48},
 'app_sha256_before':fixed_hash,'app_sha256_after':sha(app),
 'learned_checkpoint_sha256':sha(out/'learned-checkpoint.rvp'),
 'before_checkpoint_sha256':sha(out/'before-learning.rvp'),
 'seed_sha256':sha(root/'controller.rvp'),'learned_memory_region':[T,T+3072],
 'outside_region_unchanged_during_teaching':True,
 'process_restart_per_turn':True,'evaluation_adapts_patterns':False,
 'scope':'Supervised one-subject byte frames with fixed dual-relation intent. Literal sides induced from two examples; not open grammar or new reasoning.',
 'production_deployed':False}
(out/'results.json').write_text(json.dumps(report,indent=2)+'\n')
(out/'transcripts.jsonl').write_text(''.join(json.dumps(x,ensure_ascii=False)+'\n' for x in transcript))
(out/'teaching.json').write_text(json.dumps(training,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(report,indent=2),flush=True)
