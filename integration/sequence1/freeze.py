#!/usr/bin/env python3
"""Freeze reviewed candidates with dictionary/source binding and honest gates.

This saves an experiment, never promotes a language model or opens the final
task test. Tool execution is a separate engineering stage.
"""
import argparse,gzip,hashlib,json,shutil
from pathlib import Path
import engine as E
from schema import ROOT

def read(p):return json.loads(Path(p).read_text())
def write(p,x):Path(p).write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
def digest(rows):return hashlib.sha256(json.dumps(rows,ensure_ascii=False,separators=(',',':')).encode()).hexdigest()

def main():
 ap=argparse.ArgumentParser();ap.add_argument('campaign',type=Path);ap.add_argument('--destination',type=Path,default=ROOT/'integration/sequence1/experiment');args=ap.parse_args();src=args.campaign.resolve();dest=args.destination.resolve()
 if dest.exists() and any(dest.iterdir()):raise RuntimeError('Refusing to overwrite a frozen experiment')
 sources=read(src/'source-hashes.json')
 for name,sha in sources.items():
  if E.sha(ROOT/name)!=sha:raise RuntimeError('Source changed since campaign started: '+name)
 selection=read(src/'selection.json');protocol=read(src/'protocol.json');dest.mkdir(parents=True,exist_ok=True)
 for name in ['model.xi','vocabulary.json','output-vocabulary.json','source-hashes.json','protocol.json','selection.json','text-dataset.json','intent-dataset.json']:
  shutil.copyfile(src/name,dest/name)
 words=read(dest/'vocabulary.json');out=read(dest/'output-vocabulary.json')
 binding={'wire_version':'C1-Sequence-1','vocabulary_sha256':digest(words),'output_vocabulary_sha256':digest(out),'native_source_sha256':E.sha(dest/'model.xi')};write(dest/'model-binding.json',binding)
 evaluations={};models={}
 for head in ['text','intent']:
  chosen=selection[head];path=src/chosen['path']
  if E.sha(path)!=chosen['sha256']:raise RuntimeError('Selected checkpoint changed')
  data=path.read_bytes();packed=gzip.compress(data,compresslevel=9,mtime=0);file=head+'.rvp.gz';parts=[]
  for offset in range(0,len(packed),131072):
   chunk=packed[offset:offset+131072];name=file+f'.{len(parts)+1:03}';(dest/name).write_bytes(chunk);parts.append({'file':name,'sha256':hashlib.sha256(chunk).hexdigest(),'bytes':len(chunk)})
  models[head]={'file':file,'parts':parts,'checkpoint_sha256':E.sha(path),'gzip_sha256':hashlib.sha256(packed).hexdigest(),'gzip_bytes':len(packed),'native_updates':chosen['updates'],'epoch':chosen['epoch']}
  evaluations[head]=read(src/(head+f'-validation-{chosen["epoch"]:03}.json'))
 # A failed campaign is a useful engineering result, not a release approval.
 v=protocol['validation'];text=evaluations['text'];intent=evaluations['intent'];unknown=text['groups']['unknown']
 gates={'codec':read(ROOT/'build/sequence1/codec-checks.json')['passed'],
        'text_accuracy':text['accuracy']>=v['minimum_text_accuracy'],
        'all_text_groups':all(g['correct']/g['total']>=v['minimum_text_accuracy'] for g in text['groups'].values()),
        'intent_accuracy':intent['accuracy']>=v['minimum_intent_accuracy'],
        'all_intent_groups':all(g['correct']/g['total']>=v['minimum_intent_accuracy'] for g in intent['groups'].values()),
        'unknown_refusal':unknown['correct']/unknown['total']>=v['minimum_unknown_refusal'],
        'natural_tool_adapter':False,'reserved_200_tasks':False}
 write(dest/'validation.json',evaluations)
 manifest={'version':protocol['version'],'stage':'codec and compatible learned readout experiment',
           'active':False,'passed_for_promotion':all(gates.values()),'gates':gates,'models':models,'binding':binding,
           'sources':sources,'validation_sha256':E.sha(dest/'validation.json'),'protocol_sha256':E.sha(dest/'protocol.json'),
           'reserved_test':{'namespace':protocol['final_test']['namespace'],'tasks':200,'opened':False},
           'dependencies':{'reverse_pc':'08c363e6c6855c14026c86046af7183a45f45a98','mundo_x':'e2778d962af22f6f1a0794058dd4685fc2573966','host_xi_session_sha256':E.sha(E.RT/'build/xi_session')},
           'existing_models_modified':False,'general_intelligence_claimed':False,'quantum_advantage_claimed':False}
 write(dest/'manifest.json',manifest)
 print(json.dumps({'frozen':str(dest),'gates':gates,'models':models,'active':False}))

if __name__=='__main__':main()
