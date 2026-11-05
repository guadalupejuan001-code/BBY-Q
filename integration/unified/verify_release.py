#!/usr/bin/env python3
"""Check the exact deployed router, source bindings and retained evidence."""
import gzip,json
from .common import ROOT,C1,Legacy,encoded,digest,read,entity_models
from .session import router_model,perception_model

def main():
    folder=ROOT/'integration/unified/release';manifest=read(folder/'manifest.json');raw=router_model(folder)
    assert manifest['passed'] and manifest['apk_built'] is False
    assert digest(b''.join((folder/p['file']).read_bytes() for p in manifest['router']['parts']))==manifest['router']['gzip_sha256']
    for name,sha in manifest['evidence'].items():assert C1.sha(folder/name)==sha,name
    for name,sha in read(folder/'training-source-hashes.json').items():assert C1.sha(ROOT/name)==sha,name
    assert {name:digest(value) for name,value in Legacy.read_models(ROOT/'integration/sequence2/release').items()}==manifest['base_models']
    assert set(entity_models())=={'v3','memory','voice','entity'}
    validation=read(folder/'validation.json');assert validation['correct']==488 and validation['total']==490
    assert all(g['correct']==g['total'] for family,g in validation['groups'].items() if not family.startswith('legacy-'))
    reserved=json.loads(gzip.decompress((folder/'reserved.json.gz').read_bytes()));assert reserved['integration_passed'] and reserved['tasks']==200 and reserved['all_stages_executed']==200
    assert sum(row['correct'] for row in reserved['cases'])==reserved['correct']==manifest['prediction_correct']
    assert manifest['prediction_errors']==200-reserved['correct']
    assert manifest['prediction_perfect']==reserved['passed']==(reserved['correct']==200)
    assert perception_model(folder) is not None
    assert all(row['causal_effect'] for row in reserved['controls'][1:])
    assert len({row['seed'] for row in reserved['cases']})==200
    assert read(folder/'integration-checks.json')['passed']
    print(json.dumps({'passed':True,'version':'U01','router_sha256':digest(raw),'reader_validation':[488,490],'quantum_contracts':[139,139],'reserved_all_stages':[200,200],'reserved_correct':[reserved['correct'],200],'prediction_errors':200-reserved['correct'],'apk_built':False}))

if __name__=='__main__':main()
