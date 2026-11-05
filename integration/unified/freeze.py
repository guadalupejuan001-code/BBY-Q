#!/usr/bin/env python3
"""Freeze validated native parameters and the integration's real evidence."""
import argparse,gzip,shutil
from pathlib import Path
from .common import ROOT,C1,Legacy,encoded,digest,read,write,source_identity

DEPENDENCIES=['bbyq','.github/workflows/bbyq-unified.yml','integration/entity/engine.py','integration/qchat100/engine.py',
 'ai/xi/quantum3/common.xi','ai/xi/quantum3/benchmarks.xi','ai/xi/balance/qrl3-curriculum.xi','ai/xi/quantum3/step.xi',
 'ai/xi/qchat100/model.xi','ai/xi/qmemory/model.xi','ai/xi/entity/workspace.xi','ai/xi/entity/credit.xi','ai/xi/entity/feedback.xi']

def main():
    parser=argparse.ArgumentParser();parser.add_argument('training',type=Path);args=parser.parse_args();training=args.training
    chosen=read(training/'selected.json');validation=read(training/f'validation-{chosen["epoch"]:03}.json')
    integration=read(ROOT/'build/unified/integration-checks.json');reserved=read(ROOT/'build/unified/reserved.json')
    if not integration['passed'] or not reserved['integration_passed'] or reserved['tasks']!=200:raise ValueError('Full integration and execution of all engines in 200 reserved tasks must pass before freezing')
    if chosen['minimum']<.9:raise ValueError('Reader validation threshold failed')
    if any(g['correct']!=g['total'] for family,g in chosen['groups'].items() if not family.startswith('legacy-')):raise ValueError('A quantum language capability failed validation')
    for name,sha in read(training/'source-hashes.json').items():
        if C1.sha(ROOT/name)!=sha:raise ValueError('Training source identity changed: '+name)
    folder=ROOT/'integration/unified/release';folder.mkdir(parents=True,exist_ok=True)
    binding={}
    for name in ['model.xi','vocabulary.json','output-vocabulary.json','semantic-vocabulary.json']:
        shutil.copyfile(training/name,folder/name);binding[name]=C1.sha(folder/name)
    raw=(training/chosen['path']).read_bytes()
    if digest(raw)!=chosen['sha256']:raise ValueError('Selected reader changed')
    packed=gzip.compress(raw,mtime=0);parts=[]
    for i,start in enumerate(range(0,len(packed),131072),1):
        piece=packed[start:start+131072];name=f'router.rvp.gz.{i:03}';(folder/name).write_bytes(piece);parts.append({'file':name,'sha256':digest(piece),'bytes':len(piece)})
    write(folder/'validation.json',validation);write(folder/'selection.json',chosen);write(folder/'training-protocol.json',read(training/'protocol.json'));write(folder/'training-source-hashes.json',read(training/'source-hashes.json'));write(folder/'candidates.json',read(training/'candidates.json'))
    write(folder/'integration-checks.json',integration);write(folder/'reserved-summary.json',{k:v for k,v in reserved.items() if k!='cases'})
    (folder/'reserved.json.gz').write_bytes(gzip.compress(encoded(reserved),mtime=0))
    before=read(ROOT/'build/unified/reserved-before-perception.json');(folder/'diagnostic-before.json.gz').write_bytes(gzip.compress(encoded(before),mtime=0))
    perception=read(training/'perception-selected.json');v3=(training/perception['path']).read_bytes()
    if digest(v3)!=perception['sha256']:raise ValueError('Perception selection changed')
    v3_packed=gzip.compress(v3,mtime=0);(folder/'v3.rvp.gz').write_bytes(v3_packed)
    for name in ['perception-protocol.json','perception-baseline.json','perception-candidates.json','perception-selected.json']:
        shutil.copyfile(training/name,folder/name)
    if perception['updates']:shutil.copyfile(training/f'perception-validation-{perception["updates"]:04}.json',folder/'perception-validation.json')
    else:shutil.copyfile(training/'perception-baseline.json',folder/'perception-validation.json')
    sources=source_identity()
    for name in DEPENDENCIES:sources[name]=C1.sha(ROOT/name)
    evidence=['validation.json','selection.json','training-protocol.json','training-source-hashes.json','candidates.json','integration-checks.json','reserved-summary.json','reserved.json.gz','diagnostic-before.json.gz','perception-protocol.json','perception-baseline.json','perception-candidates.json','perception-selected.json','perception-validation.json']
    manifest={'version':'U01','passed':True,'prediction_perfect':reserved['passed'],'prediction_errors':reserved['tasks']-reserved['correct'],'integration_tasks':reserved['tasks'],'prediction_correct':reserved['correct'],'perception':{'file':'v3.rvp.gz','sha256':digest(v3),'gzip_sha256':digest(v3_packed)},'router':{'sha256':digest(raw),'gzip_sha256':digest(packed),'parts':parts},'binding':binding,'sources':sources,'evidence':{name:C1.sha(folder/name) for name in evidence},'base_models':{name:digest(raw) for name,raw in Legacy.read_models(ROOT/'integration/sequence2/release').items()},'runtime_revisions':{'REVERSE-PC':'08c363e6c6855c14026c86046af7183a45f45a98','mundo-X':'e2778d962af22f6f1a0794058dd4685fc2573966'},'apk_built':False,'limits':'Integration checks pass; predictive accuracy is reported separately with every error retained. Supported contracts and bounded cooperative tasks on the native quantum simulator; no joint end-to-end gradient, general conversation guarantee or demonstrated quantum advantage. Android packaging is not activated.'}
    write(folder/'manifest.json',manifest);print({'version':'U01','parts':len(parts),'reserved':reserved['correct'],'apk_built':False})

if __name__=='__main__':main()
