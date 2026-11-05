#!/usr/bin/env python3
"""Cycle-wise E02 campaign with validation selection and a locked final test."""
import argparse,gzip,json,shutil,time
from pathlib import Path
import engine as N
def atomic(p,v):
 p=Path(p);t=p.with_suffix(p.suffix+'.pending');t.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n');t.replace(p)
def brief(v):return {k:x for k,x in v.items() if k!='cases'}
def main():
 p=argparse.ArgumentParser();p.add_argument('--output',type=Path,default=N.ROOT/'build/entity-e02');p.add_argument('--refine-from',type=Path);args=p.parse_args();out=args.output.resolve()
 if out.exists():raise ValueError('Use a fresh campaign directory')
 out.mkdir(parents=True);atomic(out/'protocol-pinned.json',N.P)
 initial=out/'initial';candidates=[]
 if args.refine_from:
  shutil.copytree(args.refine_from,initial);last=252;cycles=[504,504];voice_epochs=[60,180]
  atomic(out/'refinement-pinned.json',json.loads((N.ROOT/'integration/entity/refinement.json').read_text()))
 else:
  N.boot(initial);last=0;cycles=N.P['training']['cycles'];voice_epochs=N.P['training']['voice_epochs']
 atomic(out/'source-pinned.json',{str(p.relative_to(N.ROOT)):N.sha(p) for p in [Path(__file__),N.ROOT/'integration/entity/engine.py',*sorted((N.ROOT/'ai/xi/entity').glob('*.xi'))]})
 current=initial
 for cycle_number,(end,epochs) in enumerate(zip(cycles,voice_epochs)):
  print(json.dumps({'phase':'cycle','episodes':end,'voice_epochs':epochs}),flush=True)
  with N.Entity(current) as entity:
   before=entity.identities();updates=entity.voice_train(epochs)
   rows=[]
   for i in range(last,end):
    rows.append(entity.episode('train',i,train=True,gate=False))
    if (i+1)%42==0:print(json.dumps({'phase':'training','episodes':i+1,'joint_correct_recent':sum(r['joint_success'] for r in rows[-42:])}),flush=True)
   after=entity.identities();candidate=out/f'cycle-{end:04d}-{cycle_number}';entity.save(candidate)
  validation=N.evaluate(candidate,'validation',N.P['validation']['episodes'])
  eligible=validation['joint_accuracy']>=.85 and validation['voice_accuracy']>=.95 and validation['missing_refusal']==1.
  result={'episodes':end,'voice_epochs_this_cycle':epochs,'voice_updates_this_cycle':updates,'folder':candidate.name,'before':before,'after':after,'changed':{k:before[k]!=after[k] for k in before},'validation':validation,'eligible':eligible}
  candidates.append(result);atomic(out/'candidates.json',candidates)
  print(json.dumps({'phase':'validated','episodes':end,'changed':result['changed'],'eligible':eligible,**brief(validation)}),flush=True)
  current=candidate;last=end
  if args.refine_from and eligible:break
 accepted=[c for c in candidates if c['eligible']]
 if not accepted:
  atomic(out/'status.json',{'status':'no-eligible-candidate','candidates':len(candidates)});return
 selected=max(accepted,key=lambda c:(c['validation']['joint_accuracy'],-c['validation']['mean_brier']))
 atomic(out/'selection.json',selected)
 atomic(out/'FINAL-TEST-OPENED.json',{'selection_sha256':N.sha(out/'selection.json'),'protocol_sha256':N.sha(out/'protocol-pinned.json')})
 chosen=out/selected['folder'];test=N.evaluate(chosen,'test',N.P['test']['episodes'])
 controls={}
 for control in ['memory-erased','vqc-ablated','qrl-random','voice-ablated']:
  print(json.dumps({'phase':'control','control':control}),flush=True)
  controls[control]=N.evaluate(chosen,'test',N.P['test']['episodes'],control)
 # Freeze the shared learner while retaining the same selected experts.
 frozen=out/'frozen-controller';frozen.mkdir()
 for name in ['v3','memory','voice']:shutil.copy2(chosen/(name+'.rvp'),frozen/(name+'.rvp'))
 shutil.copy2(initial/'entity.rvp',frozen/'entity.rvp')
 controls['frozen-common-learning']=N.evaluate(frozen,'test',N.P['test']['episodes'])
 passed=test['joint_accuracy']>=.85 and test['voice_accuracy']>=.95 and test['missing_refusal']==1.
 report={'version':N.P['version'],'protocol':N.P,'selected':selected,'source_hashes':json.loads((out/'source-pinned.json').read_text()),'refinement':json.loads((out/'refinement-pinned.json').read_text()) if args.refine_from else None,'test':test,'controls':controls,'passed':passed,'e01_originals_preserved':True,'limits':['The joint task uses a fixed rule, binary memory and a seven-position environment.','The learned voice maps four action symbols to short sentences, using the existing exact Clifford encoder.','Specialists have separate parameters, common task evidence, verified credit and atomic persistence. This is not joint differentiation or general intelligence.','Quantum circuits are simulated; no quantum advantage is claimed.']}
 atomic(out/'report.json',report);print(json.dumps({'phase':'complete','passed':passed,**brief(test)}),flush=True)
 if not passed:return
 release=N.ROOT/'integration/entity/release';release.mkdir(parents=True,exist_ok=True)
 manifests={}
 for name in ['v3','memory','voice','entity']:
  raw=(chosen/(name+'.rvp')).read_bytes();file=release/(name+'.rvp.gz');file.write_bytes(gzip.compress(raw,compresslevel=9,mtime=0))
  manifests[name]={'file':file.name,'checkpoint_sha256':__import__('hashlib').sha256(raw).hexdigest(),'gzip_sha256':N.sha(file),'gzip_bytes':file.stat().st_size}
 with N.Entity(chosen) as entity:
  counters={'vqc':int.from_bytes(N.material(entity.sessions['v3'],N.A+4000,8),'little'),'qrl':int.from_bytes(N.material(entity.sessions['v3'],N.A+5000,8),'little'),'voice':int.from_bytes(N.material(entity.sessions['voice'],N.Q+24,8),'little'),'memory':int.from_bytes(N.material(entity.sessions['memory'],N.M+24,8),'little'),'shared':int.from_bytes(N.material(entity.sessions['entity'],N.E+128,8),'little')}
 atomic(release/'vocabulary.json',N.VOCAB);atomic(release/'evaluation.json',report)
 atomic(release/'manifest.json',{'schema':1,'version':'E02','passed':True,'models':manifests,'training_counters':counters,'protocol_sha256':N.sha(out/'protocol-pinned.json'),'evaluation_sha256':N.sha(release/'evaluation.json'),'vocabulary_sha256':N.sha(release/'vocabulary.json'),'runtime':'08c363e6c6855c14026c86046af7183a45f45a98','ether':'e2778d962af22f6f1a0794058dd4685fc2573966','native_source_sha256':{str(p.relative_to(N.ROOT)):N.sha(p) for p in sorted((N.ROOT/'ai/xi/entity').glob('*.xi'))}})
if __name__=='__main__':main()
