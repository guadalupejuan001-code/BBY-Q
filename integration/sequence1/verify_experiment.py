#!/usr/bin/env python3
"""Verify frozen identities, gates and real reloaded native predictions."""
import gzip,json,tempfile
from pathlib import Path
import engine as E
from schema import ROOT
from artifacts import model_bytes

def read(p):return json.loads(Path(p).read_text())
def check(ok,message):
 if not ok:raise RuntimeError(message)

def main():
 folder=ROOT/'integration/sequence1/experiment';m=read(folder/'manifest.json');evaluation=read(folder/'validation.json')
 check(m['active'] is False and not m['general_intelligence_claimed'] and not m['quantum_advantage_claimed'],'Unsupported promotion or intelligence claim')
 check(m['reserved_test']['opened'] is False,'Reserved tasks were opened without promotion')
 check(E.sha(folder/'validation.json')==m['validation_sha256'],'Validation identity')
 check(E.sha(folder/'protocol.json')==m['protocol_sha256'],'Protocol identity')
 for name,sha in m['sources'].items():check(E.sha(ROOT/name)==sha,'Native/training source changed: '+name)
 check(E.sha(folder/'model.xi')==m['binding']['native_source_sha256'],'Native model identity')
 check(read(folder/'model-binding.json')==m['binding'],'Binding metadata changed')
 if 'controls_sha256' in m:check(E.sha(folder/'controls.json')==m['controls_sha256'],'Controls identity')
 protocol=read(folder/'protocol.json');v=protocol['validation'];text=evaluation['text'];intent=evaluation['intent'];unknown=text['groups']['unknown']
 expected={'codec':read(ROOT/'build/sequence1/codec-checks.json')['passed'],'text_accuracy':text['accuracy']>=v['minimum_text_accuracy'],'all_text_groups':all(g['correct']/g['total']>=v['minimum_text_accuracy'] for g in text['groups'].values()),'intent_accuracy':intent['accuracy']>=v['minimum_intent_accuracy'],'all_intent_groups':all(g['correct']/g['total']>=v['minimum_intent_accuracy'] for g in intent['groups'].values()),'unknown_refusal':unknown['correct']/unknown['total']>=v['minimum_unknown_refusal'],'natural_tool_adapter':False,'reserved_200_tasks':False}
 check(expected==m['gates'] and m['passed_for_promotion']==all(expected.values()),'A failed capability gate was overridden')
 words=read(folder/'vocabulary.json');out=read(folder/'output-vocabulary.json');checked={}
 with tempfile.TemporaryDirectory(prefix='c1-frozen-') as temporary:
  local=Path(temporary)
  for name in ['model.xi','model-binding.json']:(local/name).write_bytes((folder/name).read_bytes())
  for head,headid in [('text',0),('intent',1)]:
   entry=m['models'][head];packed=model_bytes(folder,entry)
   path=local/(head+'.rvp');path.write_bytes(gzip.decompress(packed));check(E.sha(path)==entry['checkpoint_sha256'],'Checkpoint identity')
   with E.Model(path,words,out) as model:
    check(model.number(224+headid*8)==entry['native_updates'],'Training counter changed')
    # One case per true group, including failures: this checks transport and
    # reload identity without laundering a failed capability as a pass.
    seen=set()
    for row in evaluation[head]['cases']:
     group=row['expected_intent'] if headid else row.get('kind','known')
     if group in seen:continue
     seen.add(group)
     if headid:check(model.intent(row['input'],row.get('previous',''))['intent']==row['intent'],'Reloaded intent differs')
     else:
      got=model.generate(row['input'],row.get('previous',''));check(got['tokens']==row['tokens'] and got['terminated']==row['terminated'],'Reloaded text differs')
    checked[head]=len(seen)
   try:E.Model(path,words+['incompatible-dictionary'],out)
   except ValueError:pass
   else:raise RuntimeError('Mismatched dictionary accepted')
 report={'integrity_passed':True,'active':False,'promotion_gates':m['gates'],'native_reloaded_cases':checked}
 (ROOT/'build/sequence1/experiment-checks.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report))

if __name__=='__main__':main()
