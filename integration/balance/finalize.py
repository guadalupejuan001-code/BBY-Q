#!/usr/bin/env python3
"""Open the final test only after selection, package accepted native checkpoints."""
import gzip,hashlib,json,statistics,sys,struct,zipfile
from pathlib import Path
import run as R

ROOT=R.ROOT;OUT=R.OUT;RT=R.RT;P=R.P
def selected(name):
    report=json.loads((OUT/(name+'-selection.json')).read_text());c=report['selected']
    return report,OUT/(c['checkpoint'] if c else report['original'])
def compressed(source,destination):destination.write_bytes(gzip.compress(source.read_bytes(),compresslevel=9,mtime=0))
def write_bytes(session,address,data):
    body='\n'.join(f'store8 {address+i} {v}' for i,v in enumerate(data));R.execute(session,body)
def clean_chat(source,destination,rows):
    with R.QE.Native(RT,source) as model:
      for first in range(0,rows,96):
        body=''
        for i in range(first,min(rows,first+96)):
          start=R.QE.BANK+i*R.QE.STRIDE;end=start+R.QE.FEATURES+1
          body+=f'set r5 {start}\nset r6 {end}\nlabel clear_{i}\nstore8 $r5 0\nadd r5 1\ncmp r5 r6\njlt clear_{i}\n'
        model.execute(body)
      model.save(destination)
def combine_v3(vqc,qrl,destination):
    with R.XiSession(RT/'build/xi_session',vqc) as v,R.XiSession(RT/'build/xi_session',qrl) as q,R.XiSession(RT/'build/xi_session',OUT/'v3-original.rvp') as target:
      for session,agent,offset in [(v,'vqc',100000),(q,'qrl',200000)]:
        params=R.parameters(session,agent)
        for address,data in [(R.A+offset,params['theta']),(R.A+offset+10000,params['weights']),(R.A+offset+20000,params['visits']),(R.A+(4000 if agent=='vqc' else 5000),params['metadata'])]:write_bytes(target,address,data)
      R.execute(target,f'store64 {R.A+560} 0');target.save(destination)
def qrl_varied(path,repeats=2):
    rows=[]
    with R.XiSession(RT/'build/xi_session',path) as model:
      for i in range(42*repeats):
        body=f'store64 {R.A+256} {R.seed("qrl","test-varied",i)}\nstore64 {R.A+280} 0\nstore64 {R.A+560} 1\nstore64 {R.A+568} {i%42}\nfstore {R.A+304} .15\nstore64 {R.A+312} 12\nstore64 {R.A+320} 2\nstore64 {R.A+328} 0\nstore64 {R.A+336} 0\ncall qrl_episode'
        rows.append(R.metrics(R.execute(model,body)))
    k=sum(int(x['success']) for x in rows);return {'successes':k,'examples':len(rows),'success_rate':k/len(rows),'mean_reward':statistics.mean(r['reward'] for r in rows),'scope':'Fresh stochastic trajectories for the 42 practiced position/goal pairs; supplementary evaluation, not unseen states'}
def main():
    reports={};paths={}
    for name in ['vqc','qrl','qchat','qmemory']:reports[name],paths[name]=selected(name)
    if (OUT/'FINAL-TEST-OPENED.json').exists():raise ValueError('Final test already opened; reuse the saved result, never tune on it')
    R.atomic(OUT/'FINAL-TEST-OPENED.json',{'selection_sha256':{name:R.sha(OUT/(name+'-selection.json')) for name in reports},'protocol_sha256':R.sha(ROOT/'integration/balance/protocol.json')})
    result={'protocol':P,'base_commit':P['base_commit'],'selection':reports,'test':{},'limitations':[
      'Different tests measure different capabilities; no combined intelligence percentage is calculated.',
      'All circuits run as classical software simulations. These tests do not demonstrate quantum advantage.',
      'VQC remains a synthetic linear classifier; QRL practices finite line-navigation states; QChat100 remains a small learned-topic generator; QMemory stores binary associations.']}
    for name in ['vqc','qrl']:
      R.log('final',stage='testing',component_under_test=name)
      if name=='vqc':
        n=P['test']['numeric_examples_per_split'];before={k:R.vqc_eval(OUT/'v3-original.rvp','test-'+k,n) for k in ['iid','ood']};after={k:R.vqc_eval(paths[name],'test-'+k,n) for k in ['iid','ood']}
        ok=all(v['accuracy']>=.90 and v['brier']<=.08 and v['accuracy']>=before[k]['accuracy']-.02 for k,v in after.items())
      else:
        n=P['test']['qrl_episode_examples_per_split'];before=R.qrl_eval(OUT/'v3-original.rvp','test',n);after=R.qrl_eval(paths[name],'test',n)
        before['varied_goal_rollouts']=qrl_varied(OUT/'v3-original.rvp');after['varied_goal_rollouts']=qrl_varied(paths[name])
        ok=after['pairs_correct']>=40 and all(r['success_rate']>=.90 for r in after['original_environments'].values())
      result['test'][name]={'before':before,'after':after,'criterion_passed':ok};R.atomic(OUT/'final-partial.json',result)
    data=R.build();codec=json.loads((OUT/'qchat-codec.json').read_text());vocab=codec['vocabulary'];lex=set(codec['input_vocabulary']);history=set(codec['history_vocabulary']);release=ROOT/'integration/qchat100/release'
    oldlex=set(json.loads((release/'input-vocabulary.json').read_text()));oldhist=set(json.loads((release/'history-vocabulary.json').read_text()))
    R.log('final',stage='testing',component_under_test='qchat')
    before=R.chat_eval(OUT/'qchat-original.rvp',data['test'],vocab,oldlex,oldhist);after=R.chat_eval(paths['qchat'],data['test'],vocab,lex,history)
    retention=R.chat_eval(paths['qchat'],data['original_retention'],vocab,lex,history)
    known=[r for r,c in zip(after['cases'],data['test']) if c['kind']!='unknown'];known_accuracy=sum(r['correct'] for r in known)/len(known)
    unknown=after['groups']['unknown']['accuracy'];ok=known_accuracy>=.85 and unknown>=.85 and retention['exact_response_accuracy']>=.90
    seen={tuple(R.QE.bits(r['input'],[],r.get('previous',''),lex,history)) for r in data['train']}
    fresh=[(r,c) for r,c in zip(after['cases'],data['test']) if tuple(R.QE.bits(c['input'],[],c.get('previous',''),lex,history)) not in seen]
    analytic=R.chat_eval(paths['qchat'],data['test'],vocab,lex,history,mode=2);ablated=R.chat_eval(paths['qchat'],data['test'],vocab,lex,history,mode=1)
    assert [r['tokens'] for r in analytic['cases']]==[r['tokens'] for r in after['cases']]
    result['test']['qchat']={'before':before,'after':after,'known_accuracy':known_accuracy,'unknown_refusal':unknown,'retention':retention,
      'unseen_feature_vectors':{'correct':sum(r['correct'] for r,c in fresh),'examples':len(fresh),'accuracy':sum(r['correct'] for r,c in fresh)/len(fresh) if fresh else None},
      'analytic_control_identical':True,'observables_ablated':ablated,'criterion_passed':ok};R.atomic(OUT/'final-partial.json',result)
    R.log('final',stage='testing',component_under_test='qmemory')
    before=R.memory_eval(OUT/'qmemory-original.rvp','test',4);after=R.memory_eval(paths['qmemory'],'test',4)
    erased=R.QM.evaluate(RT,paths['qmemory'],250,P['seed'],'test',repeats=4,delays=(2,8,12),reset=True)
    # Give the existing classical control the same continued training budget/data.
    with R.QM.Engine(RT,OUT/'qmemory-original.rvp') as model:
      updates=reports['qmemory']['selected']['updates'] if reports['qmemory']['selected'] else 0
      for i in range(updates):model.episode(1,R.QM.seed(P['seed'],'train',i),i%13,train=True)
      model.s.save(OUT/'qmemory-matched-control.rvp')
    classical=R.QM.evaluate(RT,OUT/'qmemory-matched-control.rvp',250,P['seed'],'test',repeats=4,delays=(2,8,12),role=1)
    result['test']['qmemory']={'before':before,'after':after,'memory_erased':erased,'matched_classical_control':classical,'criterion_passed':after['accuracy']>=.99 and after['mse']<=.01}
    result['balanced']=all(v['criterion_passed'] for v in result['test'].values())
    result['originals_preserved']=all(R.sha(OUT/(name+'-original.rvp'))==expected for name,expected in P['original_sha256'].items())
    assert result['originals_preserved']
    R.atomic(OUT/'final-report.json',result);R.log('final',stage='completed',balanced=result['balanced'])
    if not result['balanced']:return
    target=ROOT/'integration/balance/release'
    if target.exists():raise ValueError('Release already exists; never replace a published model')
    target.mkdir(parents=True)
    combined=OUT/'v3-balanced.rvp';combine_v3(paths['vqc'],paths['qrl'],combined)
    cleaned=OUT/'qchat-balanced.rvp';clean_chat(paths['qchat'],cleaned,reports['qchat']['token_contexts'])
    # Cleaning cache rows must leave independently generated responses unchanged.
    check=R.chat_eval(cleaned,data['test'][:8],vocab,lex,history)
    expected=result['test']['qchat']['after']['cases'][:8];assert [r['tokens'] for r in check['cases']]==[r['tokens'] for r in expected]
    components={}
    for name,checkpoint,source_release in [('v3',combined,ROOT/'integration/quantum3/release'),('qchat100',cleaned,ROOT/'integration/qchat100/release'),('qmemory',paths['qmemory'],ROOT/'integration/qmemory/release')]:
      folder=target/name;folder.mkdir();m=json.loads((source_release/'manifest.json').read_text());file=folder/m['file'];compressed(checkpoint,file)
      m.update({'checkpoint_sha256':R.sha(checkpoint),'gzip_sha256':R.sha(file),'gzip_bytes':file.stat().st_size,'checkpoint_bytes':checkpoint.stat().st_size,'balanced_release':'E01','original_checkpoint_sha256':json.loads((source_release/'manifest.json').read_text())['checkpoint_sha256']})
      component_report={'selection':reports['qchat' if name=='qchat100' else name] if name!='v3' else {'vqc':reports['vqc'],'qrl':reports['qrl']},'test':result['test']['qchat' if name=='qchat100' else name] if name!='v3' else {'vqc':result['test']['vqc'],'qrl':result['test']['qrl']}}
      R.atomic(folder/'training-report.json',component_report);m['training_report_sha256']=R.sha(folder/'training-report.json')
      if name=='qchat100':
        for key,values in [('vocabulary',vocab),('input-vocabulary',sorted(lex)),('history-vocabulary',sorted(history))]:
          f=folder/(key+'.json');f.write_text(json.dumps(values,ensure_ascii=False)+'\n');m[key.replace('-','_')+'_sha256']=R.sha(f)
        m['training_updates']=reports['qchat']['selected']['total_updates']
      if name=='v3':
        m['training_episodes']={'vqc':reports['vqc']['selected']['episodes'] if reports['vqc']['selected'] else 10000,'qrl':reports['qrl']['selected']['episodes'] if reports['qrl']['selected'] else 10000}
        m.pop('training_episodes_per_agent',None);m['training']='E01 continued native XI SGD and REINFORCE; validation-selected checkpoints'
        m['source_sha256']={str(p.relative_to(ROOT)):R.sha(p) for p in [ROOT/'ai/xi/quantum3/common.xi',ROOT/'ai/xi/quantum3/benchmarks.xi',ROOT/'ai/xi/balance/qrl3-curriculum.xi',ROOT/'ai/xi/quantum3/step.xi']}
      if name=='qmemory':
        m['continued_updates']=reports['qmemory']['selected']['updates'] if reports['qmemory']['selected'] else 0
        with R.QM.Engine(RT,checkpoint) as model:counts=model.parameters()
        m.pop('updates_per_model',None);m['quantum_updates']=counts['quantum_updates'];m['classical_updates_in_checkpoint']=counts['classical_updates'];m['continuation_seed']=P['seed']
      R.atomic(folder/'manifest.json',m);components[name]={'directory':name,'manifest_sha256':R.sha(folder/'manifest.json')}
    R.atomic(target/'evaluation.json',result)
    R.atomic(target/'active.json',{'schema':1,'version':'E01','balanced':True,'protocol_sha256':R.sha(ROOT/'integration/balance/protocol.json'),'evaluation_sha256':R.sha(target/'evaluation.json'),'components':components})
    R.log('release',stage='packaged',components=list(components))

if __name__=='__main__':main()
