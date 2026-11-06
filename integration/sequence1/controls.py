#!/usr/bin/env python3
"""Native feature ablations on the already-open validation contrasts."""
import gzip,json,tempfile
from pathlib import Path
import engine as E
from schema import C,S,FEATURE_STRIDE,ROOT
from artifacts import model_bytes

class ControlledModel(E.Model):
 mode='full'
 def active(self,*args,**kwargs):
  if self.mode=='erase_all':kwargs['ablate']=True
  text=super().active(*args,**kwargs)
  if self.mode!='drop_order':return text
  # All filtering and prediction remain native. Input bytes and dictionary
  # stay identical; only pair/position families are removed from the readout.
  return text+f'''load64 r8 {C+48}
set r7 0
set r9 0
label control_filter
cmp r7 r8
jge control_done
mov r0 r7
mul r0 8
add r0 {S['G']}
load64 r1 $r0
mov r6 r1
div r6 {FEATURE_STRIDE}
cmp r6 6
jge control_keep
mod r6 3
cmp r6 0
jne control_next
label control_keep
mov r0 r9
mul r0 8
add r0 {S['G']}
store64 $r0 r1
add r9 1
label control_next
add r7 1
jmp control_filter
label control_done
store64 {C+48} r9
'''

def main():
 folder=ROOT/'integration/sequence1/experiment';read=lambda p:json.loads(Path(p).read_text());manifest=read(folder/'manifest.json');data=read(folder/'validation.json');words=read(folder/'vocabulary.json');out=read(folder/'output-vocabulary.json');rows=[r for r in data['text']['cases'] if r['kind']=='order'];report={'split':'already-open validation; not final test','cases':len(rows),'controls':{}}
 with tempfile.TemporaryDirectory(prefix='c1-control-') as temporary:
  local=Path(temporary)
  for name in ['model.xi','model-binding.json']:(local/name).write_bytes((folder/name).read_bytes())
  checkpoint=local/'text.rvp';checkpoint.write_bytes(gzip.decompress(model_bytes(folder,manifest['models']['text'])))
  for mode in ['full','drop_order','erase_all']:
   correct=0;cases=[]
   with ControlledModel(checkpoint,words,out) as model:
    model.mode=mode
    for row in rows:
     got=model.generate(row['input'],row.get('previous',''));ok=got['terminated'] and got['tokens']==E.output_words(row['response']);correct+=ok;cases.append({'input':row['input'],'expected':row['response'],**got,'correct':ok})
   report['controls'][mode]={'correct':correct,'total':len(rows),'accuracy':correct/len(rows),'cases':cases}
 (folder/'controls.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');manifest['controls_sha256']=E.sha(folder/'controls.json');(folder/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n');print(json.dumps({k:{a:b for a,b in v.items() if a!='cases'} for k,v in report['controls'].items()}))
if __name__=='__main__':main()
