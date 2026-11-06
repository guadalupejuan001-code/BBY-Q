#!/usr/bin/env python3
"""Bind complete-task and transaction evidence without changing frozen weights."""
import argparse,json,shutil
from pathlib import Path
from schema import ROOT
import engine as E

def main():
    p=argparse.ArgumentParser();p.add_argument('--readers',type=Path,default=ROOT/'integration/sequence2/release');args=p.parse_args();dest=args.readers
    m=json.loads((dest/'manifest.json').read_text())
    for source,sha in m['sources'].items():
        if E.sha(ROOT/source)!=sha:raise ValueError('Frozen source changed: '+source)
    documents={}
    for name in ['codec-checks.json','tool-checks.json','workspace-checks.json','tasks-validation.json']:
        path=ROOT/'build/sequence2'/name;document=json.loads(path.read_text());shutil.copyfile(path,dest/name);documents[name]=document
    gates=m['validation_gates'];gates['transactions']=documents['workspace-checks.json']['passed']
    report=documents['tasks-validation.json'];gates['complete_tasks']=all(v['correct']/v['total']>=.9 for v in report['families'].values()) and report['total']>=20
    m['validation_reports']={name:E.sha(dest/name) for name in documents}
    m['stage']='qualified frozen candidate; reserved test remains unopened' if all(gates.values()) else 'blocked by validation'
    (dest/'manifest.json').write_text(json.dumps(m,ensure_ascii=False,indent=2)+'\n');print(json.dumps({'stage':m['stage'],'gates':gates}))
    if not all(gates.values()):raise SystemExit(1)

if __name__=='__main__':main()
