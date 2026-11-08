#!/usr/bin/env python3
"""Retain the actual historical C06-C08 checkpoints, not new training substitutes.

Input directories come from pinned GitHub Actions artifacts. The returned APK
contains these bytes and their complete original reports; no network on device.
"""
from pathlib import Path
from hashlib import sha256
import json,shutil
ROOT=Path(__file__).resolve().parents[2]
ITEMS={
 'c06':('semantic-trained.rvp','training-report.json','ed0f0067e43fcab74ba81c574bca983d8a497322ae5d7e8218f7a2941aa53018',42383154492,13578676074),
 'c07':('epistemic-trained.rvp','training-report.json','fd0d68731996771adcfc1bf8bd2a6f634d96dcc042fdb87efbb97103b0e59ecb',42386450584,13579516959),
 'c08':('active-trained.rvp','active-report.json','0bb44c4d3da0797934abf1fe51d76354ed54d7f470cb1897c5bae48c8c432448',42389307671,13580822851),
}
def main():
 out=ROOT/'integration/mobile_candidates';out.mkdir(parents=True,exist_ok=True)
 index={'schema':'BBYQ-Android-original-candidates-v1','models':{},'automatic_promotion':False}
 for cycle,(model,report,expected,run,artifact) in ITEMS.items():
  source=ROOT/'build/mobile-candidates'/cycle/cycle
  raw=(source/model).read_bytes();report_bytes=(source/report).read_bytes();meta=json.loads(report_bytes)
  assert sha256(raw).hexdigest()==expected,(cycle,'wrong historical candidate')
  assert meta.get('passed') is True
  assert meta.get('trained_checkpoint_sha256',meta.get('active_model_sha256'))==expected
  if cycle=='c08':assert meta['source_model_sha256']==ITEMS['c07'][2]
  target=out/cycle;target.mkdir(parents=True,exist_ok=True)
  (target/model).write_bytes(raw);(target/report).write_bytes(report_bytes)
  index['models'][cycle]={'model':cycle+'/'+model,'report':cycle+'/'+report,
   'model_sha256':expected,'report_sha256':sha256(report_bytes).hexdigest(),
   'original_run':run,'original_artifact':artifact,'promoted':False}
 (out/'index.json').write_text(json.dumps(index,indent=2)+'\n')
 print(json.dumps({'candidate_sources_retained':list(index['models']),'all_original_sha256':True,'trained_again':False}))
if __name__=='__main__':main()
