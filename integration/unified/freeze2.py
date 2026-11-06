#!/usr/bin/env python3
"""Publish U02 only after predictive, native and upgrade qualification."""
import argparse,gzip,json,shutil,tempfile
from pathlib import Path
from .common import ROOT,C1,encoded,digest,read,write,source_identity,entity_models
from .session import router_model
from .freeze import DEPENDENCIES
from . import perception as P
from .train_head import seed as training_seed

def load_report(path):
    path=Path(path)
    return json.loads(gzip.decompress(path.read_bytes())) if path.suffix=='.gz' else read(path)

def gzip_report(path,value):path.write_bytes(gzip.compress(encoded(value),mtime=0))

def main():
    parser=argparse.ArgumentParser();parser.add_argument('training',type=Path);args=parser.parse_args();training=args.training;folder=ROOT/'integration/unified/release';build=ROOT/'build/unified'
    selected=read(training/'selection.json');validation=read(training/f'validation-{selected["epoch"]:03}.json')
    if not selected['eligible'] or validation['validation-iid']['correct']!=validation['validation-iid']['total']:raise ValueError('U02 requires an eligible model with no IID validation errors')
    if validation['validation-ood']['accuracy']<.99:raise ValueError('OOD validation did not qualify')
    regression=read(build/'regression.json');reserved=read(build/'reserved.json');opened=read(build/'opened-regression.json');classification=read(build/'classification-test.json')
    for name,report in [('regression',regression),('reserved',reserved),('opened-regression',opened)]:
        if not report['passed'] or report['tasks']!=200 or report['correct']!=200 or report['all_stages_executed']!=200:raise ValueError(name+' did not pass all 200 predictive tasks')
        assert report['perception_parameter_sha256']==selected['parameter_sha256'],'Evaluation used another readout'
    if not classification['passed'] or classification['total']!=1024:raise ValueError('Independent 1024-case classification test did not qualify')
    assert classification['parameter_identity']['readout']==selected['parameter_sha256']
    assert regression['reserved_seed']==2026110705 and opened['reserved_seed']==2026110602 and reserved['reserved_seed']==2026110603
    assert classification['namespace']==2026110603
    protocol=read(training/'protocol.json')
    learning_seeds={training_seed('train',i) for i in range(protocol['training_examples'])}|{training_seed(split,i) for split in protocol['validation_splits'] for i in range(protocol['validation_examples_per_split'])}
    assert not learning_seeds&{row['seed'] for report in (regression,opened,reserved) for row in report['cases']}
    checks={name:read(build/name) for name in ['integration-checks.json','perception-checks.json','upgrade-checks.json']}
    if not all(report['passed'] for report in checks.values()):raise ValueError('Native invariants, gradients or data-preserving migration failed')
    previous=read(build/'u01-release-manifest.json')
    baseline=load_report(folder/'u01-reserved.json.gz') if (folder/'u01-reserved.json.gz').exists() else load_report(folder/'reserved.json.gz')
    failures=[row for row in baseline['cases'] if not row['correct']]
    assert len(failures)==9 and baseline['reserved_seed']==regression['reserved_seed']
    after={row['index']:row for row in regression['cases']};fixed=[]
    for row in failures:
        current=after[row['index']];assert current['seed']==row['seed'] and current['correct']
        fixed.append({'index':row['index'],'seed':row['seed'],'expected_class':row['expected_class'],'before':row['result']['results'][-1],'after':current['result']['results'][-1]})
    # The router and all original quantum weights remain the existing models.
    actual_router=gzip.decompress(b''.join((folder/part['file']).read_bytes() for part in previous['router']['parts']))
    assert digest(actual_router)==previous['router']['sha256']
    raw=(training/selected['path']).read_bytes();assert digest(raw)==selected['sha256']
    with tempfile.TemporaryDirectory(prefix='bbyq-u02-package-') as temporary:
        source=Path(temporary)/'selected.rvp';source.write_bytes(raw)
        with C1.XiSession(C1.RT/'build/xi_session',source) as native:
            before=P.parameter_identity(native)
            P.run(native,f'fstore {P.B+96} 0\nstore64 {P.B+104} 0\nstore64 {P.B+112} 0\nfstore {P.B+64} 0\nfstore {P.B+72} 0\nfstore {P.B+80} 0\nfstore {P.B+88} 0')
            assert P.parameter_identity(native)==before
            destination=Path(temporary)/'deployment.rvp';native.save(destination);raw=destination.read_bytes()
    packed=gzip.compress(raw,mtime=0);(folder/'v3.rvp.gz').write_bytes(packed)
    write(folder/'u01-manifest.json',previous);gzip_report(folder/'u01-reserved.json.gz',baseline)
    gzip_report(folder/'regression.json.gz',regression);gzip_report(folder/'reserved.json.gz',reserved);gzip_report(folder/'classification-test.json.gz',classification)
    gzip_report(folder/'opened-regression.json.gz',opened)
    first=read(build/'first-reserved.json');assert first['correct']==199 and first['reserved_seed']==2026110602
    gzip_report(folder/'first-reserved.json.gz',first);gzip_report(folder/'first-classification-test.json.gz',read(build/'first-classification-test.json'))
    errors=[row for row in first['cases'] if not row['correct']];assert len(errors)==1
    corrected={row['index']:row for row in opened['cases']}
    write(folder/'boundary-failure-corrected.json',{'passed':True,'corrected':1,'before':errors[0],'after':corrected[errors[0]['index']]})
    write(folder/'known-failures-corrected.json',{'passed':True,'corrected':9,'total':9,'cases':fixed})
    write(folder/'reserved-summary.json',{k:v for k,v in reserved.items() if k!='cases'})
    write(folder/'regression-summary.json',{k:v for k,v in regression.items() if k!='cases'})
    write(folder/'opened-regression-summary.json',{k:v for k,v in opened.items() if k!='cases'})
    write(folder/'classification-summary.json',{k:v for k,v in classification.items() if k!='cases'})
    for name,report in checks.items():write(folder/name,report)
    for source,target in [('protocol.json','readout-training-protocol.json'),('configuration.json','readout-configuration.json'),('selection.json','readout-selection.json'),('candidates.json','readout-candidates.json'),('baseline.json','readout-baseline.json')]:shutil.copyfile(training/source,folder/target)
    write(folder/'readout-validation.json',validation)
    for path in training.glob('warmup-*.json'):shutil.copyfile(path,folder/('readout-'+path.name))
    shutil.copyfile(build/'u02-evaluation-plan.json',folder/'evaluation-plan.json')
    training_sources=[]
    for name,sha in read(training/'training-sources.json').items():
        source=training/'sources'/name
        if not source.exists():source=ROOT/name
        assert C1.sha(source)==sha,'Training source was not preserved: '+name
        target=folder/'training-sources'/name;target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(source,target)
        training_sources.append({'path':name,'snapshot':str(target.relative_to(folder)),'sha256':sha})
    write(folder/'readout-training-sources.json',training_sources)
    previous_identity=read(build/'u01-upgrade-fixture.json')['identity']
    sources=source_identity()
    for name in DEPENDENCIES:sources[name]=C1.sha(ROOT/name)
    evidence=[path for path in folder.glob('*.json') if path.name!='manifest.json']+list(folder.glob('*.json.gz'))+list((folder/'training-sources').rglob('*.py'))+list((folder/'training-sources').rglob('*.xi.in'))
    manifest={**previous,'version':'U02','passed':True,'prediction_scope':'the independently reserved 200 cooperative tasks','prediction_perfect':True,'prediction_errors':0,'integration_tasks':200,'prediction_correct':200,'regression_correct':200,'opened_regression_correct':200,'known_errors_corrected':9,'boundary_error_corrected':1,
              'classification_test':{'correct':classification['correct'],'total':1024,'errors':1024-classification['correct'],'accuracy':classification['accuracy'],'seed':classification['namespace']},
              'perception':{'file':'v3.rvp.gz','sha256':digest(raw),'gzip_sha256':digest(packed),'readout_magic':P.MAGIC,'readout_parameter_sha256':before,'original_parameters_preserved':selected['preserved_original_parameters']},
              'migrations':[{'identity':previous_identity,'identity_sha256':digest(encoded(previous_identity))}],
              'sources':sources,'evidence':{str(path.relative_to(folder)):C1.sha(path) for path in evidence},
              'limits':'Nine known classifier errors corrected and strict 200-case regression plus 200 new cooperative tasks passed. Independent 1024-case classification accuracy is reported separately. Bounded synthetic task on the existing native quantum backend; no claim of arbitrary error-free classification or quantum advantage. Android integration and APK builds remain disabled.','apk_built':False}
    write(folder/'manifest.json',manifest);print({'version':'U02','regression_correct':200,'new_tasks_correct':200,'known_errors_corrected':9,'classification_correct':classification['correct'],'classification_total':1024,'apk_built':False})

if __name__=='__main__':main()
