#!/usr/bin/env python3
"""Recover exact CI-trained heads without substitution; no APK credentials.

GitHub credentials are only sent to api.github.com. Artifact-storage redirects
use their signed URLs and must NOT receive a GitHub Authorization header.
"""
from hashlib import sha256
from pathlib import Path
from urllib.parse import urlparse
import io,json,os,urllib.request,zipfile

ROOT=Path(__file__).resolve().parents[2]
REPO='guadalupejuan001-code/BBY-Q'
LOCK={
 'c06':(13578676074,'c06/semantic-trained.rvp','c06/training-report.json',
   'ed0f0067e43fcab74ba81c574bca983d8a497322ae5d7e8218f7a2941aa53018',
   '512692edc23f72bc8a0a340ad748672a047f4deaf5939b1728160eb74b14a65e'),
 'c07':(13579516959,'c07/epistemic-trained.rvp','c07/training-report.json',
   'fd0d68731996771adcfc1bf8bd2a6f634d96dcc042fdb87efbb97103b0e59ecb',
   '409f67613a399bb6d9e4b6a9cc1e802fe32b31390420b068582d85d9115ac132'),
 'c08':(13580822851,'c08/active-trained.rvp','c08/active-report.json',
   '0bb44c4d3da0797934abf1fe51d76354ed54d7f470cb1897c5bae48c8c432448',
   '90e498f1db7a75fe884ca14effaa64efc18d00337fdaf8cac5f94bdcfd93212d'),
}
class ArtifactRedirect(urllib.request.HTTPRedirectHandler):
 def redirect_request(self,req,fp,code,msg,headers,newurl):
  if urlparse(newurl).scheme!='https':raise RuntimeError('Insecure artifact redirect rejected')
  target=super().redirect_request(req,fp,code,msg,headers,newurl)
  if target is not None and urlparse(newurl).hostname!='api.github.com':
   target.remove_header('Authorization')
   target.remove_header('X-github-api-version')
   target.remove_header('Accept')
  return target

def main():
 out=ROOT/'integration/mobile_u03_c16/heads';out.mkdir(parents=True,exist_ok=True)
 token=os.environ.get('GITHUB_TOKEN')
 if not token:raise RuntimeError('Read-only Actions token needed to retrieve original checkpoints')
 opener=urllib.request.build_opener(ArtifactRedirect())
 for cycle,(artifact,checkpoint,report,bank_sha,report_sha) in LOCK.items():
  req=urllib.request.Request(f'https://api.github.com/repos/{REPO}/actions/artifacts/{artifact}/zip',
    headers={'Authorization':'Bearer '+token,'Accept':'application/vnd.github+json','X-GitHub-Api-Version':'2022-11-28'})
  with opener.open(req,timeout=90) as response:blob=response.read()
  with zipfile.ZipFile(io.BytesIO(blob)) as z:raw=z.read(checkpoint);doc=z.read(report)
  if sha256(raw).hexdigest()!=bank_sha or sha256(doc).hexdigest()!=report_sha:
   raise RuntimeError('Original trained checkpoint/report identity mismatch: '+cycle)
  (out/(cycle+'.rvp')).write_bytes(raw);(out/(cycle+'.json')).write_bytes(doc)
  print(json.dumps({'cycle':cycle,'original_artifact':artifact,'checkpoint_sha256':bank_sha,'bytes':len(raw)}))
 (out/'provenance.json').write_text(json.dumps({
  'source':'original validated CI artifacts, byte-identical',
  'promotion':'C06/C07 observational; C08 remains comparison-only',
  'heads':{c:{'artifact':v[0],'checkpoint_sha256':v[3],'report_sha256':v[4]} for c,v in LOCK.items()}
 },indent=2)+'\n')
if __name__=='__main__':main()
