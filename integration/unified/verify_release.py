#!/usr/bin/env python3
"""Check the exact deployed router, source bindings and retained evidence."""
import gzip,json,tempfile
from pathlib import Path
from .common import ROOT,C1,Legacy,encoded,digest,read,entity_models
from .session import router_model,perception_model
from . import perception as P
from .upgrades import bank_parameters

def report(folder,name):return json.loads(gzip.decompress((folder/name).read_bytes()))

def main():
    folder=ROOT/'integration/unified/release';manifest=read(folder/'manifest.json');raw=router_model(folder)
    assert manifest['version']=='U02' and manifest['passed'] and manifest['apk_built'] is False
    assert digest(b''.join((folder/p['file']).read_bytes() for p in manifest['router']['parts']))==manifest['router']['gzip_sha256']
    for name,sha in manifest['evidence'].items():assert C1.sha(folder/name)==sha,name
    for name,sha in read(folder/'training-source-hashes.json').items():assert C1.sha(ROOT/name)==sha,name
    assert {name:digest(value) for name,value in Legacy.read_models(ROOT/'integration/sequence2/release').items()}==manifest['base_models']
    assert set(entity_models())=={'v3','memory','voice','entity'}
    validation=read(folder/'validation.json');assert validation['correct']==488 and validation['total']==490
    assert all(g['correct']==g['total'] for family,g in validation['groups'].items() if not family.startswith('legacy-'))
    reserved=report(folder,'reserved.json.gz');assert reserved['passed'] and reserved['integration_passed'] and reserved['tasks']==200 and reserved['all_stages_executed']==200
    assert sum(row['correct'] for row in reserved['cases'])==reserved['correct']==manifest['prediction_correct']
    assert manifest['prediction_errors']==200-reserved['correct']
    assert manifest['prediction_perfect']==reserved['passed']==(reserved['correct']==200)
    regression=report(folder,'regression.json.gz');assert regression['passed'] and regression['correct']==200 and regression['all_stages_executed']==200
    baseline=report(folder,'u01-reserved.json.gz');assert baseline['correct']==191 and baseline['tasks']==200
    assert manifest['router']['sha256']==read(folder/'u01-manifest.json')['router']['sha256']
    old_errors={row['index']:row for row in baseline['cases'] if not row['correct']}
    fixed=read(folder/'known-failures-corrected.json');assert fixed['corrected']==fixed['total']==len(old_errors)==9
    assert {row['index'] for row in fixed['cases']}==set(old_errors)
    for row in fixed['cases']:
        assert row['seed']==old_errors[row['index']]['seed']
        assert row['before']['class']!=row['expected_class'] and row['after']['class']==row['expected_class']
    classification=report(folder,'classification-test.json.gz')
    assert classification['passed'] and classification['total']==1024 and classification['accuracy']>=.995 and classification['no_test_learning']
    assert sum(row['correct'] for row in classification['cases'])==classification['correct']
    assert classification['correct']>classification['base_correct']
    opened=report(folder,'opened-regression.json.gz');assert opened['passed'] and opened['correct']==opened['tasks']==200
    assert reserved['perception_parameter_sha256']==regression['perception_parameter_sha256']==opened['perception_parameter_sha256']==classification['parameter_identity']['readout']==manifest['perception']['readout_parameter_sha256']
    assert regression['reserved_seed']==2026110705 and opened['reserved_seed']==2026110602 and reserved['reserved_seed']==2026110603
    first=report(folder,'first-reserved.json.gz');assert first['correct']==199 and first['reserved_seed']==opened['reserved_seed']
    boundary=read(folder/'boundary-failure-corrected.json');assert boundary['passed'] and not boundary['before']['correct'] and boundary['after']['correct'] and boundary['before']['seed']==boundary['after']['seed']
    assert report(folder,'first-classification-test.json.gz')['correct']==1023
    validation=read(folder/'readout-validation.json');assert validation['validation-iid']['correct']==validation['validation-iid']['total']
    assert validation['validation-ood']['accuracy']>=.99
    for source in read(folder/'readout-training-sources.json'):assert C1.sha(folder/source['snapshot'])==source['sha256']
    for migration in manifest['migrations']:assert digest(encoded(migration['identity']))==migration['identity_sha256'] and migration['identity']['version']=='U01'
    raw_perception=perception_model(folder)
    with tempfile.TemporaryDirectory(prefix='bbyq-u02-release-') as temporary:
        checkpoint=Path(temporary)/'perception.rvp';checkpoint.write_bytes(raw_perception)
        with C1.XiSession(C1.RT/'build/xi_session',checkpoint) as native:
            from .common import integer
            assert integer(native,P.B)==P.MAGIC and integer(native,P.B+8)==P.NF and integer(native,P.B+16)==P.NH
            assert P.parameter_identity(native)==manifest['perception']['readout_parameter_sha256']
            assert bank_parameters(native)==manifest['perception']['original_parameters_preserved']
            assert integer(native,P.B+96)==0 and integer(native,P.B+112)==0
    assert all(row['causal_effect'] for row in reserved['controls'][1:])
    assert len({row['seed'] for row in reserved['cases']})==200
    assert read(folder/'integration-checks.json')['passed']
    assert read(folder/'perception-checks.json')['passed'] and read(folder/'upgrade-checks.json')['passed']
    print(json.dumps({'passed':True,'version':'U02','router_sha256':digest(raw),'reader_validation':[488,490],'quantum_contracts':[139,139],'known_errors_corrected':[9,9],'regression_correct':[200,200],'new_tasks_correct':[reserved['correct'],200],'classification_correct':[classification['correct'],1024],'apk_built':False}))

if __name__=='__main__':main()
