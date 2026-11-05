#!/usr/bin/env python3
"""Training orchestration and independent scoring; all model updates run in XI."""
import argparse,concurrent.futures,gzip,hashlib,importlib.util,json,math,random,statistics,struct,sys,time
from pathlib import Path
from data import build,ABSTAIN
ROOT=Path(__file__).resolve().parents[2]
RT=ROOT/'deps/reverse-pc'
sys.path.insert(0,str(RT/'scripts'))
from xi_session_client import XiSession

def module(name,file):
    spec=importlib.util.spec_from_file_location(name,file);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
QE=module('balance_qchat_engine',ROOT/'integration/qchat100/engine.py')
QM=module('balance_qmemory_controller',ROOT/'integration/qmemory/controller.py')
A=8140000000000000000;M=8170000000000000000
P=json.loads((ROOT/'integration/balance/protocol.json').read_text())
OUT=ROOT/'build/balance-e01'

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def atomic(p,value):
    temporary=p.with_suffix(p.suffix+'.pending');temporary.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n');temporary.replace(p)
def log(component,**fields):
    value={'component':component,'time':time.time(),**fields};atomic(OUT/(component+'-status.json'),value)
    print(json.dumps(value,ensure_ascii=False),flush=True)
def seed(component,split,index):return int.from_bytes(hashlib.sha256(f"E01:{P['seed']}:{component}:{split}:{index}".encode()).digest()[:4],'little')&0x7fffffff
def metrics(events):return {e['name']:e['value'] for e in events if e.get('type')=='metric'}
def wilson(k,n):
    z=1.95996398454;p=k/n;d=1+z*z/n;c=(p+z*z/(2*n))/d;h=z*math.sqrt(p*(1-p)/n+z*z/(4*n*n))/d;return [c-h,c+h]
def library(qrl=True):
    names=[ROOT/'ai/xi/quantum3/common.xi',ROOT/'ai/xi/quantum3/benchmarks.xi',ROOT/'ai/xi/balance/qrl3-curriculum.xi',ROOT/'ai/xi/quantum3/step.xi']
    return '\n'.join(p.read_text() for p in names)
LIB=library()
def source(body):return '#!reverse-pc-machine-v1\nbudget 100000000\n'+body+'\nhalt\n'+LIB
def execute(s,body):return s.execute(source(body))[0]
def count(s,agent):
    ev=execute(s,f'load64 r0 {A+(4000 if agent=="vqc" else 5000)}\nprint r0')
    return next(e['value'] for e in ev if e.get('type')=='register')
def parameters(s,agent):
    t=A+(100000 if agent=='vqc' else 200000);meta=A+(4000 if agent=='vqc' else 5000)
    ev=execute(s,'\n'.join(f'mem_materialize {a} {n}' for a,n in [(t,8000),(t+10000,8000),(t+20000,8000),(meta,48)]))
    chunks=[bytes.fromhex(e['hex']) for e in ev if e.get('type')=='memory_materialization']
    return {'sha256':hashlib.sha256(b''.join(chunks)).hexdigest(),'episodes':struct.unpack('<q',chunks[3][:8])[0],
      'theta':chunks[0],'weights':chunks[1],'visits':chunks[2],'metadata':chunks[3]}
def vqc_eval(path,split,n):
    result=[]
    with XiSession(RT/'build/xi_session',path) as s:
      before=parameters(s,'vqc')['sha256']
      for i in range(n):
        noise=.6 if split.endswith('ood') else .1
        body=f'store64 {A+256} {seed("vqc",split,i)}\nstore64 {A+280} 0\nstore64 {A+272} 0\nfstore {A+296} {noise}\ncall vqc_sample\nstore64 {A} 0\ncall select_agent\ncall forward\nfemit probability f21\nfload f0 {A+128}\nfemit label f0'
        result.append(metrics(execute(s,body)))
      assert parameters(s,'vqc')['sha256']==before
      usage=s.metrics()
    k=sum((r['probability']>=.5)==bool(r['label']) for r in result)
    return {'correct':k,'examples':n,'accuracy':k/n,'brier':statistics.mean((r['probability']-r['label'])**2 for r in result),'wilson95':wilson(k,n),'peak_rss_kib':usage['peak_rss_kib']}
def vqc():
    original=OUT/'v3-original.rvp';n=P['validation']['numeric_examples_per_split']
    baseline={split:vqc_eval(original,'validation-'+split,n) for split in ['iid','ood']};log('vqc',stage='baseline',validation=baseline)
    candidates=[];last=0
    with XiSession(RT/'build/xi_session',original) as learner:
      initial=parameters(learner,'vqc');execute(learner,f'fstore {A+4024} {P["training"]["vqc_readout_lr"]}')
      for end in P['training']['vqc_cycles']:
        for i in range(last,end):
          execute(learner,f'store64 {A+256} {seed("vqc","train",i)}\nstore64 {A+280} 0\nstore64 {A+272} 0\nfstore {A+296} {.6 if i%4==0 else .1}\ncall vqc_sample\nstore64 {A} 0\ncall supervised_update')
          if (i+1)%100==0:log('vqc',stage='training',updates=i+1)
        checkpoint=OUT/f'vqc-{end:04}.rvp';learner.save(checkpoint);state=parameters(learner,'vqc');assert state['sha256']!=initial['sha256']
        values={split:vqc_eval(checkpoint,'validation-'+split,n) for split in ['iid','ood']}
        eligible=all(v['accuracy']>=.90 and v['brier']<=.08 and v['accuracy']>=baseline[k]['accuracy']-.02 for k,v in values.items())
        item={'updates':end,'checkpoint':checkpoint.name,'sha256':sha(checkpoint),'parameters':state['sha256'],'episodes':state['episodes'],'validation':values,'eligible':eligible,
              'objective':min(v['accuracy'] for v in values.values())-.5*statistics.mean(v['brier'] for v in values.values())}
        candidates.append(item);atomic(OUT/'vqc-candidates.json',candidates);log('vqc',stage='validated',candidate=item);last=end
    accepted=[c for c in candidates if c['eligible']];selected=max(accepted,key=lambda c:c['objective']) if accepted else None
    report={'original':str(original.name),'baseline_validation':baseline,'candidates':candidates,'selected':selected}
    atomic(OUT/'vqc-selection.json',report);log('vqc',stage='selected',candidate=selected['checkpoint'] if selected else 'original');return report

def qrl_eval(path,split,n):
    pairs=[];episodes={}
    with XiSession(RT/'build/xi_session',path) as s:
      before=parameters(s,'qrl')['sha256']
      for pos in range(7):
        for goal in range(7):
          if pos==goal:continue
          body=f'store64 {A+344} {pos}\nstore64 {A+352} {goal}\nstore64 {A+360} 0\nstore64 {A+312} 12\nstore64 {A+320} 2\nstore64 {A+280} 0\ncall qrl_step'
          r=metrics(execute(s,body));pairs.append({'position':pos,'goal':goal,'action':int(r['action']),'correct':int(r['action'])==int(goal>pos)})
      for environment in ['iid','ood']:
        rows=[]
        for i in range(n):
          body=f'store64 {A+256} {seed("qrl",split+"-"+environment,i)}\nstore64 {A+280} 0\nstore64 {A+560} 0\nfstore {A+304} .15\nstore64 {A+312} 12\nstore64 {A+320} 2\nstore64 {A+328} {int(environment=="ood")}\nstore64 {A+336} {int(environment=="ood")}\ncall qrl_episode'
          rows.append(metrics(execute(s,body)))
        k=sum(int(r['success']) for r in rows);episodes[environment]={'successes':k,'examples':n,'success_rate':k/n,'mean_reward':statistics.mean(r['reward'] for r in rows),'wilson95':wilson(k,n)}
      assert parameters(s,'qrl')['sha256']==before;usage=s.metrics()
    return {'pairs_correct':sum(r['correct'] for r in pairs),'pairs_total':42,'pairs':pairs,'original_environments':episodes,'peak_rss_kib':usage['peak_rss_kib']}
def qrl():
    original=OUT/'v3-original.rvp';n=P['validation']['qrl_episode_examples_per_split']
    baseline=qrl_eval(original,'validation',n);log('qrl',stage='baseline',validation={k:v for k,v in baseline.items() if k!='pairs'})
    candidates=[];last=0
    with XiSession(RT/'build/xi_session',original) as learner:
      initial=parameters(learner,'qrl');execute(learner,f'fstore {A+5024} {P["training"]["qrl_readout_lr"]}')
      for end in P['training']['qrl_cycles']:
        for i in range(last,end):
          # Environment covers all 42 pairs; actions still come from the trained circuit.
          body=f'store64 {A+256} {seed("qrl","train",i)}\nstore64 {A+280} 0\nstore64 {A+560} 1\nstore64 {A+568} {i%42}\nfstore {A+304} .15\nstore64 {A+312} 12\nstore64 {A+320} 0\nstore64 {A+328} 0\nstore64 {A+336} 0\ncall qrl_episode'
          execute(learner,body)
          if (i+1)%84==0:log('qrl',stage='training',updates=i+1)
        checkpoint=OUT/f'qrl-{end:04}.rvp';learner.save(checkpoint);state=parameters(learner,'qrl');assert state['sha256']!=initial['sha256']
        values=qrl_eval(checkpoint,'validation',n)
        eligible=values['pairs_correct']>=40 and all(r['success_rate']>=.90 for r in values['original_environments'].values())
        item={'updates':end,'checkpoint':checkpoint.name,'sha256':sha(checkpoint),'parameters':state['sha256'],'episodes':state['episodes'],'validation':values,'eligible':eligible,
              'objective':values['pairs_correct']/42+statistics.mean(r['mean_reward'] for r in values['original_environments'].values())*.1}
        candidates.append(item);atomic(OUT/'qrl-candidates.json',candidates);log('qrl',stage='validated',pairs_correct=values['pairs_correct'],eligible=eligible);last=end
    accepted=[c for c in candidates if c['eligible']];selected=max(accepted,key=lambda c:c['objective']) if accepted else None
    report={'original':original.name,'baseline_validation':baseline,'candidates':candidates,'selected':selected};atomic(OUT/'qrl-selection.json',report);log('qrl',stage='selected',candidate=selected['checkpoint'] if selected else 'original');return report

def chat_eval(path,rows,vocab,lex,history,mode=0):
    result=QE.evaluate(RT,path,rows,vocab,mode=mode,input_vocabulary=lex,history_vocabulary=history)
    grouped={}
    for kind in ['known','context','unknown']:
      subset=[r for r,case in zip(result['cases'],rows) if case.get('kind','known')==kind]
      if subset:grouped[kind]={'correct':sum(r['correct'] for r in subset),'examples':len(subset),'accuracy':sum(r['correct'] for r in subset)/len(subset)}
    result['groups']=grouped;return result
def compact_eval(r):return {k:v for k,v in r.items() if k!='cases'}
def qchat():
    data=build();atomic(OUT/'qchat-corpus.json',data)
    release=ROOT/'integration/qchat100/release';vocab=json.loads((release/'vocabulary.json').read_text())
    lex=set(json.loads((release/'input-vocabulary.json').read_text()));history=set(json.loads((release/'history-vocabulary.json').read_text()))
    original=OUT/'qchat-original.rvp';baseline=chat_eval(original,data['validation'],vocab,lex,history)
    log('qchat',stage='baseline',validation=compact_eval(baseline))
    lex|={t for r in data['train'] for s in [r['input'],r.get('previous','')] for t in QE.words(QE.normalize(s))};history=set(lex)
    rows=QE.examples(data['train'],vocab,lex,history);atomic(OUT/'qchat-codec.json',{'vocabulary':vocab,'input_vocabulary':sorted(lex),'history_vocabulary':sorted(history)})
    # Identical encoded prompts with contradictory labels are reported, never hidden.
    signatures={};collisions=[]
    for r in data['train']:
      key=tuple(QE.bits(r['input'],[],r.get('previous',''),lex,history));target=tuple(QE.words(r['response']))
      if key in signatures and signatures[key]!=target:collisions.append(r['input'])
      signatures[key]=target
    atomic(OUT/'qchat-collisions.json',{'count':len(collisions),'inputs':collisions})
    candidates=[];rng=random.Random(P['seed'])
    with QE.Native(RT,original) as learner:
      ev,_=learner.execute(f'load64 r0 {QE.A+24}\nprint r0');initial_updates=next(e['value'] for e in ev if e.get('type')=='register')
      learner.execute(f'fstore {QE.A+32} {P["training"]["qchat_learning_rate"]}\nstore64 {QE.A+80} 0')
      for first in range(0,len(rows),24):
        body=''
        for i,(raw,label) in enumerate(rows[first:first+24],first):body+=QE.stage(raw)+f'store64 {QE.A+48} {label}\nstore64 {QE.A+72} {QE.BANK+i*QE.STRIDE}\ncall qchat_encode\ncall qchat_cache\n'
        learner.execute(body)
      log('qchat',stage='cached',token_contexts=len(rows),conversations=len(data['train']))
      for epoch in range(1,max(P['training']['qchat_epochs'])+1):
        order=list(range(len(rows)));rng.shuffle(order)
        for first in range(0,len(order),96):learner.execute(''.join(f'store64 {QE.A+72} {QE.BANK+i*QE.STRIDE}\ncall qchat_load_case\ncall qchat_train\n' for i in order[first:first+96]))
        if epoch%5==0:log('qchat',stage='training',epoch=epoch,new_updates=epoch*len(rows))
        if epoch in P['training']['qchat_epochs']:
          checkpoint=OUT/f'qchat-epoch-{epoch:03}.rvp';learner.save(checkpoint)
          validation=chat_eval(checkpoint,data['validation'],vocab,lex,history);retention=chat_eval(checkpoint,data['original_retention'],vocab,lex,history)
          known=[r for r,c in zip(validation['cases'],data['validation']) if c['kind']!='unknown'];known_accuracy=sum(r['correct'] for r in known)/len(known)
          unknown=validation['groups']['unknown']['accuracy'];retained=retention['exact_response_accuracy']
          eligible=known_accuracy>=.85 and unknown>=.85 and retained>=.90
          item={'epoch':epoch,'new_updates':epoch*len(rows),'total_updates':initial_updates+epoch*len(rows),'checkpoint':checkpoint.name,'sha256':sha(checkpoint),'validation':compact_eval(validation),'retention':compact_eval(retention),'known_accuracy':known_accuracy,'unknown_refusal':unknown,'eligible':eligible,'objective':min(known_accuracy,unknown,retained)}
          candidates.append(item);atomic(OUT/'qchat-candidates.json',candidates);log('qchat',stage='validated',candidate=item)
      usage=learner.s.metrics()
    accepted=[c for c in candidates if c['eligible']];selected=max(accepted,key=lambda c:(c['objective'],c['known_accuracy'])) if accepted else None
    report={'original':original.name,'baseline_validation':baseline,'candidates':candidates,'selected':selected,'training_conversations':len(data['train']),'token_contexts':len(rows),'native_usage':usage,'encoding_label_collisions':len(collisions)}
    atomic(OUT/'qchat-selection.json',report);log('qchat',stage='selected',candidate=selected['checkpoint'] if selected else 'original');return report

def memory_eval(path,split,repeats):
    return QM.evaluate(RT,path,250,P['seed'],split,repeats=repeats,delays=(2,8,12))
def qmemory():
    original=OUT/'qmemory-original.rvp';baseline=memory_eval(original,'validation',2);log('qmemory',stage='baseline',accuracy=baseline['accuracy'],mse=baseline['mse'])
    candidates=[];last=0
    with QM.Engine(RT,original) as learner:
      before=learner.parameters()
      for end in P['training']['qmemory_cycles']:
        for i in range(last,end):learner.episode(0,QM.seed(P['seed'],'train',i),i%13,train=True)
        checkpoint=OUT/f'qmemory-{end:03}.rvp';learner.s.save(checkpoint);after=learner.parameters()
        validation=memory_eval(checkpoint,'validation',2);eligible=validation['accuracy']>=.99 and validation['mse']<=.01
        item={'updates':end,'checkpoint':checkpoint.name,'sha256':sha(checkpoint),'parameters_before':before,'parameters_after':after,'validation':validation,'eligible':eligible,'objective':validation['accuracy']-validation['mse']}
        candidates.append(item);atomic(OUT/'qmemory-candidates.json',candidates);log('qmemory',stage='validated',updates=end,accuracy=validation['accuracy'],mse=validation['mse']);last=end
    accepted=[c for c in candidates if c['eligible'] and c['validation']['mse']<=baseline['mse']];selected=max(accepted,key=lambda c:c['objective']) if accepted else None
    report={'original':original.name,'baseline_validation':baseline,'candidates':candidates,'selected':selected};atomic(OUT/'qmemory-selection.json',report);log('qmemory',stage='selected',candidate=selected['checkpoint'] if selected else 'original');return report

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--components',default='qrl,qchat,vqc,qmemory');a=parser.parse_args()
    assert sha(ROOT/'integration/balance/protocol.json')==sha(OUT/'protocol-pinned.json'),'Protocol changed after registration'
    jobs={'qrl':qrl,'qchat':qchat,'vqc':vqc,'qmemory':qmemory}
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
      pending={pool.submit(jobs[name]):name for name in a.components.split(',')}
      for future in concurrent.futures.as_completed(pending):
        name=pending[future]
        try:future.result()
        except Exception as error:log(name,stage='failed',error=str(error));raise
    log('campaign',stage='training_and_selection_completed',test_opened=False)

if __name__=='__main__':main()
