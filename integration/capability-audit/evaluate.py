#!/usr/bin/env python3
"""Frozen-model capability measurements. Python transports and scores; XI infers."""
import collections,gzip,hashlib,importlib.util,json,math,statistics,sys,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];HERE=Path(__file__).resolve().parent;OUT=ROOT/'build/capability-audit';OUT.mkdir(parents=True,exist_ok=True)
P=json.loads((HERE/'protocol.json').read_text());NS=P['namespace'];RT=ROOT/'deps/reverse-pc'
def load(name,path):
 s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def save(name,v):
 p=OUT/(name+'.json');p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n');print(json.dumps({'completed':name,'file':str(p)},ensure_ascii=False),flush=True)
def compact(v):return {k:w for k,w in v.items() if k not in ['cases','pairs','rows']}
def summary(rows):
 k=sum(int(r.get('passed',False)) for r in rows);return {'passed':k,'total':len(rows),'cases':rows}
def main():
 source_files=[p for folder in [ROOT/'ai',ROOT/'integration/balance/release',ROOT/'integration/entity/release',ROOT/'integration/zero/release'] for p in folder.rglob('*') if p.is_file() and '__pycache__' not in p.parts]
 before={str(p.relative_to(ROOT)):sha(p) for p in source_files};save('source-identity-before',before)
 Z=load('audit_zero',ROOT/'integration/zero/engine.py');sys.modules['engine']=Z;ZE=load('audit_zero_evaluate',ROOT/'integration/zero/evaluate.py');Z.build()
 rows=[ZE.case(NS,f,i) for f in ZE.FAMILIES for i in range(20)];symbolic={'correct':sum(r['correct'] for r in rows),'tasks':len(rows),'families':{f:{'correct':sum(r['correct'] for r in rows if r['family']==f),'total':20} for f in ZE.FAMILIES},'cases':rows};save('symbolic',symbolic)
 projections=[]
 with Z.Engine() as e:
  for probability in [0.0,.49,.5,.51,1.0]:
   e.parse('observa senal muestra 1');e.stage(192,[15]);e.stage(216,[1]);e.raw(f'fstore {Z.Z+208} {probability}');e.call(5);a=e.numbers(16384,4);projection_status=e.integer(16)
   e.facts=[a];r=e.run('¿senal es clase1?');projections.append({'probability':probability,'projection_status':projection_status,'atom':a,'query_status':r['status'],'uncertain_band':.4<=probability<=.6})
  missing=e.run('¿dato es desconocido?\ncalcula 2+3');safe=e.run('aprende regla: si $x es humana entonces $y es mortal');budget=e.run('resuelve:\na es inicio\nsi $x es inicio entonces $x es fin\n¿a es fin?',budget=1)
 save('symbolic-probes',{'near_threshold_predictions_become_assertions':projections,'unknown_goal_then_valid_tool':missing['status'],'unsafe_rule_rejected':safe['status']==4,'budget_status':budget['status'],'scope':'Programmed grammar and native typed projections, not the entire Android transaction harness'})
 sys.path.insert(0,str(ROOT/'integration/balance'));R=load('audit_balanced',ROOT/'integration/balance/run.py');N=load('audit_entity',ROOT/'integration/entity/engine.py')
 states=OUT/'states';states.mkdir(exist_ok=True);m=json.loads((ROOT/'integration/entity/release/manifest.json').read_text())
 for name,desc in m['models'].items():
  raw=gzip.decompress((ROOT/'integration/entity/release'/desc['file']).read_bytes());assert hashlib.sha256(raw).hexdigest()==desc['checkpoint_sha256'];(states/(name+'.rvp')).write_bytes(raw)
 qmanifest=json.loads((ROOT/'integration/balance/release/qchat100/manifest.json').read_text());qstate=states/'qchat.rvp';qstate.write_bytes(gzip.decompress((ROOT/'integration/balance/release/qchat100'/qmanifest['file']).read_bytes()));assert sha(qstate)==qmanifest['checkpoint_sha256']
 numeric={s:R.vqc_eval(states/'v3.rvp',NS+'-'+s,64) for s in ['iid','ood']}
 ablated=[]
 with R.XiSession(RT/'build/xi_session',states/'v3.rvp') as session:
  initial=R.parameters(session,'vqc')['sha256']
  for i in range(64):
   ev=R.execute(session,f'store64 {R.A+256} {R.seed("vqc",NS+"-iid",i)}\nstore64 {R.A+280} 1\nstore64 {R.A+272} 0\nfstore {R.A+296} .1\ncall vqc_sample\nstore64 {R.A} 0\ncall select_agent\ncall forward\nfemit probability f21\nfload f0 {R.A+128}\nfemit label f0');ablated.append(R.metrics(ev))
  assert R.parameters(session,'vqc')['sha256']==initial
 numeric['ablated_iid']={'correct':sum((r['probability']>=.5)==bool(r['label']) for r in ablated),'examples':64,'brier':statistics.mean((r['probability']-r['label'])**2 for r in ablated),'cases':ablated};save('vqc',numeric)
 policy=R.qrl_eval(states/'v3.rvp',NS,32);save('qrl',policy)
 memory=R.QM.evaluate(RT,states/'memory.rvp',250,P['seed'],NS,repeats=4,delays=(2,8,12));save('memory',memory)
 cooperation={arm:N.evaluate(states,NS,84,control=None if arm=='intact' else arm) for arm in P['native']['entity_arms']};save('entity',cooperation)
 vocab=json.loads((ROOT/'integration/balance/release/qchat100/vocabulary.json').read_text());lex=set(json.loads((ROOT/'integration/balance/release/qchat100/input-vocabulary.json').read_text()));history=set(json.loads((ROOT/'integration/balance/release/qchat100/history-vocabulary.json').read_text()))
 topics=[('memoria','la memoria conserva información .'),('dato','un dato representa información .'),('algoritmo','un algoritmo es una serie de instrucciones .'),('circuito','un circuito aplica puertas a los cúbits .'),('cúbit','un cúbit es una unidad de información cuántica .'),('entrelazamiento','el entrelazamiento crea correlaciones cuánticas .'),('medición','medir produce un resultado según el estado .'),('interferencia','la interferencia combina amplitudes .'),('xi','xi es nuestro lenguaje de instrucciones .'),('ether','ether ejecuta nuestro núcleo cuántico .')]
 language=[{'input':form.format(topic),'response':answer,'kind':'known'} for topic,answer in topics for form in ['puedes contarme qué significa {}','para entenderlo, necesito que definas {}']]
 language +=[{'input':form.format(topic),'response':'necesito más ejemplos para aprender .','kind':'unknown'} for topic in ['quasar','mitocondria','resonancia','ionosfera','fulereno','barión'] for form in ['qué significa {}','puedes definir {}']]
 language +=[{'input':'repítelo !','previous':'aprendamos acerca de '+topic,'response':answer,'kind':'context'} for topic,answer in topics]
 assert len(language)==42
 chat=R.QE.evaluate(RT,qstate,language,vocab,input_vocabulary=lex,history_vocabulary=history)
 chat['groups']={kind:{'correct':sum(r['correct'] for r,c in zip(chat['cases'],language) if c['kind']==kind),'total':sum(c['kind']==kind for c in language)} for kind in ['known','unknown','context']}
 pairs=[('ana requiere energia','energia requiere ana'),('alda no ayuda a bea','bea no ayuda a alda'),('primero calcula despues recuerda','primero recuerda despues calcula')];chat['order_probes']=[{'a':a,'b':b,'identical_encoded_bits':R.QE.bits(a,[],input_vocabulary=lex)==R.QE.bits(b,[],input_vocabulary=lex)} for a,b in pairs];save('language',chat)
 errors=[r for r in cooperation['intact']['cases'] if not r['joint_success']];conf={'wrong_decisions':len(errors),'wrong_with_confidence_ge_90':sum(r['confidence']>=.90 for r in errors),'wrong_confidence_range':[min(r['confidence'] for r in errors),max(r['confidence'] for r in errors)] if errors else [],'cases':errors};save('confidence',conf)
 after={str(p.relative_to(ROOT)):sha(p) for p in source_files};assert before==after;save('source-identity-after',after)
 result={'protocol':P,'base_commit':P['base_commit'],'native_runtime_sha256':sha(RT/'build/xi_session'),'symbolic':compact(symbolic),'vqc':{k:compact(v) for k,v in numeric.items()},'qrl':compact(policy),'memory':compact(memory),'entity':{k:compact(v) for k,v in cooperation.items()},'language':compact(chat),'confidence':compact(conf),'released_sources_and_models_unchanged':True,'scope':'Fresh native evaluations on copies; Android end-to-end results are collected separately. No overall intelligence score.'};save('summary',result)
if __name__=='__main__':main()
