#!/usr/bin/env python3
"""Deployment checks on accepted E02 models; no optimization or test selection."""
import gzip,json,tempfile
from pathlib import Path
import engine as N
def main():
 root=N.ROOT/'integration/entity/release';m=json.loads((root/'manifest.json').read_text());assert m['passed'] and m['version']=='E02'
 checks=[]
 assert N.sha(root/'evaluation.json')==m['evaluation_sha256'];checks.append('accepted report hash')
 for source,digest in m['native_source_sha256'].items():assert N.sha(N.ROOT/source)==digest
 checks.append('native workspace and credit source hashes')
 report=json.loads((root/'evaluation.json').read_text());assert report['passed']
 with tempfile.TemporaryDirectory(prefix='bbyq-e02-') as tmp:
  folder=Path(tmp)
  for name,model in m['models'].items():
   data=(root/model['file']).read_bytes();assert N.sha(root/model['file'])==model['gzip_sha256'];raw=gzip.decompress(data);assert __import__('hashlib').sha256(raw).hexdigest()==model['checkpoint_sha256'];(folder/(name+'.rvp')).write_bytes(raw);checks.append(name+' checkpoint')
  selected=[];seen=set()
  for row in report['test']['cases']:
   if row['joint_success']!=1:continue
   signature=(int(row['action']),bool(row['memory_present'] and row['sensor_present']))
   if signature in seen:continue
   selected.append(row);seen.add(signature)
  assert all(any(int(r['action'])==a for r in selected) for a in [-1,0,1,2])
  with N.Entity(folder) as e:
   before=e.identities()
   for row in selected:
    actual=e.episode('test',row['index']);assert actual['joint_success']==1 and actual['voice']==row['voice'];checks.append('cross-model action '+str(row['action']))
   assert before==e.identities();checks.append('inference preserves every trained parameter')
   s=e.sessions['entity'];base={8:1,16:1,24:3,40:.999,48:.9}
   a=N.metrics(N.run(s,N.workspace({**base,264:0,272:0})+'call entity_infer\n'+N.emit_int(N.E+72,'goal')))
   b=N.metrics(N.run(s,N.workspace({**base,264:1,272:1})+'call entity_infer\n'+N.emit_int(N.E+72,'goal')));assert a==b
   checks.append('withheld teachers cannot alter inference')
   row=next(r for r in selected if int(r['action']) in [0,1]);original=e.episode('test',row['index']);prior=e.identities()
   # A separate throwaway feedback experiment checks causal use of learning.
   # It changes no released checkpoint and is not a candidate-selection input.
   N.run(s,f'fstore {N.E+96} 0\nset r15 0\nlabel feedback_stress\ncall entity_learn\nadd r15 1\ncmp r15 100\njlt feedback_stress')
   changed=e.episode('test',row['index']);assert original['action']!=-1 and changed['action']==-1
   after=e.identities();assert prior['entity']!=after['entity'] and all(prior[k]==after[k] for k in ['vqc','qrl','memory','voice'])
   checks.append('common verified feedback changes a subsequent decision')
 result={'ok':True,'version':'E02','count':len(checks),'checks':checks};out=N.ROOT/'build/entity-release-checks.json';out.parent.mkdir(exist_ok=True);out.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
if __name__=='__main__':main()
