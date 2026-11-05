#!/usr/bin/env python3
"""Release and native deployment checks. No model tuning or held-out selection."""
import json
from pathlib import Path
from engine import ROOT,Engine,build,sha
from evaluate import case,checks,FAMILIES
def main():
 release=ROOT/'integration/zero/release';m=json.loads((release/'manifest.json').read_text());r=json.loads((release/'evaluation.json').read_text());assert m['passed'] and not m['general_intelligence_claimed'];done=[]
 assert sha(release/'evaluation.json')==m['evaluation_sha256'];done.append('reserved report identity')
 assert sha(ROOT/'integration/zero/protocol.json')==m['protocol_sha256'];done.append('pre-registered protocol identity')
 for name,digest in m['sources'].items():assert sha(ROOT/name)==digest
 done.append('native inference source identities');build()
 for family in FAMILIES:assert case('zero-deployment-smoke',family,0)['correct'];done.append('new native smoke task: '+family)
 done.extend(checks())
 with Engine() as e:
  assert e.parse('consulta quantum v3 clasifica ['+','.join(['0.1']*1000)+']')['op']==16;done.append('specialist payload stays intact beyond the token window')
 assert r['correct']==r['tasks']==120 and len(r['families'])==6
 result={'ok':True,'version':'BBY Q 0','count':len(done),'reserved_correct':r['correct'],'reserved_tasks':r['tasks'],'checks':done};p=ROOT/'build/zero-release-checks.json';p.parent.mkdir(exist_ok=True);p.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
if __name__=='__main__':main()
