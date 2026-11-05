#!/usr/bin/env python3
"""Freeze compatible native readers before end-to-end validation or reserved tasks."""
import argparse,gzip,json,shutil
from pathlib import Path
import engine as E
from schema import ROOT
from workspace import digest,encoded

def read(path):return json.loads(Path(path).read_text())
def write(path,value):Path(path).write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n')

def main():
    p=argparse.ArgumentParser();p.add_argument('campaign',type=Path);p.add_argument('--intent-campaign',type=Path);p.add_argument('--destination',type=Path,default=ROOT/'integration/sequence2/release');args=p.parse_args()
    text=args.campaign.resolve();intent=(args.intent_campaign or args.campaign).resolve();dest=args.destination.resolve()
    if dest.exists() and any(dest.iterdir()):raise ValueError('Cannot overwrite a frozen candidate')
    for campaign in [text,intent]:
        for name,sha in read(campaign/'source-hashes.json').items():
            if E.sha(ROOT/name)!=sha:raise ValueError('Source changed after training: '+name)
    for name in ['model.xi','vocabulary.json','output-vocabulary.json','semantic-vocabulary.json','protocol.json']:
        if (text/name).read_bytes()!=(intent/name).read_bytes():raise ValueError('Readers have different source/dictionary/protocol identities')
    selected={};evaluation={};models={};dest.mkdir(parents=True,exist_ok=True)
    for name in ['model.xi','vocabulary.json','output-vocabulary.json','semantic-vocabulary.json','protocol.json']:
        shutil.copyfile(text/name,dest/name)
    for head,campaign in [('text',text),('intent',intent)]:
        candidates=read(campaign/(head+'-candidates.json'))
        # An unchanged warm seed is a measured baseline candidate. A continued
        # checkpoint must improve validation to replace it.
        baseline=campaign/(head+'-baseline-candidate.json')
        if baseline.exists():candidates.append(read(baseline))
        entry=max(candidates,key=lambda c:(c['minimum_group_accuracy'],c['accuracy']))
        selected[head]=entry;source=campaign/entry['path'];raw=source.read_bytes()
        if digest(raw)!=entry['sha256']:raise ValueError('Selected checkpoint changed')
        packed=gzip.compress(raw,compresslevel=9,mtime=0);parts=[]
        for offset in range(0,len(packed),131072):
            chunk=packed[offset:offset+131072];name=head+f'.rvp.gz.{len(parts)+1:03}';(dest/name).write_bytes(chunk)
            parts.append({'file':name,'bytes':len(chunk),'sha256':digest(chunk)})
        models[head]={'parts':parts,'gzip_sha256':digest(packed),'gzip_bytes':len(packed),
                      'checkpoint_sha256':digest(raw),'native_updates':entry['updates'],'epoch':entry['epoch']}
        evaluation[head]=read(campaign/(head+f'-validation-{entry["epoch"]:03}.json'))
        write(dest/(head+'-candidates.json'),candidates)
    write(dest/'selection.json',selected);write(dest/'validation.json',evaluation)
    words=read(dest/'vocabulary.json');output=read(dest/'output-vocabulary.json')
    binding={'wire_version':'C1-Sequence-1','readout_version':'C1-Sequence-2',
             'vocabulary_sha256':digest(encoded(words)),'output_vocabulary_sha256':digest(encoded(output)),
             'semantic_vocabulary_sha256':digest(encoded(read(dest/'semantic-vocabulary.json'))),
             'native_source_sha256':E.sha(dest/'model.xi')}
    write(dest/'model-binding.json',binding)
    sources={}
    for directory in ['integration/sequence2','ai/xi/sequence2']:
        for path in (ROOT/directory).glob('*'):
            if path.is_file() and path.suffix in ['.py','.json','.in']:sources[str(path.relative_to(ROOT))]=E.sha(path)
    for name in ['ai/personal/zero/core.xi.in','ai/personal/zero/model.mjs','ai/personal/zero/schema.mjs']:
        sources[name]=E.sha(ROOT/name)
    for directory in ['integration/sequence2/seed','integration/sequence2/intent-seed']:
        for path in (ROOT/directory).iterdir():
            if path.is_file():sources[str(path.relative_to(ROOT))]=E.sha(path)
    for name in ['bbyq.mjs','.github/workflows/bbyq-c1-native.yml','.github/workflows/bbyq-personal-android.yml']:
        sources[name]=E.sha(ROOT/name)
    text_eval=evaluation['text'];intent_eval=evaluation['intent']
    gates={'text_accuracy':text_eval['accuracy']>=.9,'every_text_group':all(v['correct']/v['total']>=.9 for v in text_eval['groups'].values()),
           'intent_accuracy':intent_eval['accuracy']>=.9,'every_intent_group':all(v['correct']/v['total']>=.9 for v in intent_eval['groups'].values()),
           'codec':read(ROOT/'build/sequence2/codec-checks.json')['passed'],
           'native_tools':read(ROOT/'build/sequence2/tool-checks.json')['passed'],
           'transactions':False,'complete_tasks':False}
    manifest={'version':'BBYQ-C1-Sequence-2','stage':'frozen candidate; complete-task validation pending',
              'models':models,'binding':binding,'sources':sources,'validation_sha256':E.sha(dest/'validation.json'),
              'protocol_sha256':E.sha(dest/'protocol.json'),'validation_gates':gates,
              'reserved_test':{'namespace':'c1-repaired-reserved-1','tasks':200,'opened':False},
              'active_in_android':False,'apk_built':False,'existing_models_modified':False,
              'general_intelligence_claimed':False,'quantum_advantage_claimed':False,
              'dependencies':{'reverse_pc':'08c363e6c6855c14026c86046af7183a45f45a98','mundo_x':'e2778d962af22f6f1a0794058dd4685fc2573966'}}
    write(dest/'manifest.json',manifest);print(json.dumps({'frozen':str(dest),'validation_gates':gates,'selected':selected}))

if __name__=='__main__':main()
