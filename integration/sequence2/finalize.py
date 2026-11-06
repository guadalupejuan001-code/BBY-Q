#!/usr/bin/env python3
"""Attach the once-opened reserved evidence to the unchanged native candidate."""
import argparse,json,shutil
from pathlib import Path
from schema import ROOT
import engine as E

def main():
    p=argparse.ArgumentParser();p.add_argument('--readers',type=Path,default=ROOT/'integration/sequence2/release');p.add_argument('--report',type=Path,default=ROOT/'build/sequence2/reserved.json');args=p.parse_args();dest=args.readers
    m=json.loads((dest/'manifest.json').read_text());r=json.loads(args.report.read_text())
    if not all(m['validation_gates'].values()):raise ValueError('An unqualified candidate cannot be finalized')
    if r['identity']['manifest_sha256']!=E.sha(dest/'manifest.json'):raise ValueError('Candidate changed after reserved opening')
    if r['identity']['evaluation_source_sha256']!=E.sha(ROOT/'integration/sequence2/evaluate.py'):raise ValueError('Evaluation code changed after opening')
    if not r['reserved'] or r['total']!=200 or r['namespace']!=m['reserved_test']['namespace']:raise ValueError('Wrong reserved task set')
    for name,sha in m['sources'].items():
        if E.sha(ROOT/name)!=sha:raise ValueError('Frozen source changed: '+name)
    passed=all(v['correct']/v['total']>=.9 for v in r['families'].values())
    shutil.copyfile(args.report,dest/'reserved.json')
    record={'ready_for_native_review':passed,'candidate_manifest_sha256':E.sha(dest/'manifest.json'),
            'reserved_sha256':E.sha(dest/'reserved.json'),'reserved_opened':True,'reserved_correct':r['correct'],
            'reserved_tasks':r['total'],'families':r['families'],'apk_built':False,'active_in_android':False,
            'scope':'Source/native correction only; the installed Android application is not replaced.'}
    (dest/'promotion.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n');print(json.dumps(record,ensure_ascii=False))
    if not passed:raise SystemExit(1)

if __name__=='__main__':main()
