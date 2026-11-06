#!/usr/bin/env python3
"""Run a frozen experimental C1 head with its exact matching dictionary."""
import argparse,gzip,json,tempfile
from pathlib import Path
import engine as E
from schema import ROOT
from artifacts import model_bytes

def main():
 ap=argparse.ArgumentParser();ap.add_argument('text');ap.add_argument('--previous',default='');ap.add_argument('--head',choices=['text','intent'],default='text');ap.add_argument('--model',type=Path,default=ROOT/'integration/sequence1/experiment');a=ap.parse_args();folder=a.model.resolve();manifest=json.loads((folder/'manifest.json').read_text());entry=manifest['models'][a.head]
 words=json.loads((folder/'vocabulary.json').read_text());out=json.loads((folder/'output-vocabulary.json').read_text());packed=model_bytes(folder,entry)
 with tempfile.TemporaryDirectory(prefix='bbyq-c1-run-') as temporary:
  local=Path(temporary)
  for name in ['model.xi','model-binding.json']:(local/name).write_bytes((folder/name).read_bytes())
  checkpoint=local/'model.rvp';checkpoint.write_bytes(gzip.decompress(packed))
  if E.sha(checkpoint)!=entry['checkpoint_sha256']:raise RuntimeError('Checkpoint identity mismatch')
  with E.Model(checkpoint,words,out) as model:
   result=model.generate(a.text,a.previous) if a.head=='text' else model.intent(a.text,a.previous)
   print(json.dumps({'version':manifest['version'],'experimental':not manifest['active'],'head':a.head,**result},ensure_ascii=False))
if __name__=='__main__':main()
