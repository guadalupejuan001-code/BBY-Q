#!/usr/bin/env python3
"""Measured readout controls on open validation cases, never a reserved retune."""
import argparse,json,tempfile
from pathlib import Path
import engine as E
from schema import ROOT,C,S,FEATURE_STRIDE
from workspace import read_models

class Controlled(E.Model):
    mode='full'
    def active(self,*args,**kwargs):
        if self.mode=='erase_all':kwargs['ablate']=True
        source=super().active(*args,**kwargs)
        if self.mode!='drop_order':return source
        return source+f'''load64 r8 {C+48}
set r7 0
set r9 0
label c2_control_filter
cmp r7 r8
jge c2_control_done
mov r0 r7
mul r0 8
add r0 {S['G']}
load64 r1 $r0
mov r6 r1
div r6 {FEATURE_STRIDE}
cmp r6 10
je c2_control_next
cmp r6 6
jge c2_control_keep
mod r6 3
cmp r6 0
jne c2_control_next
label c2_control_keep
mov r0 r9
mul r0 8
add r0 {S['G']}
store64 $r0 r1
add r9 1
label c2_control_next
add r7 1
jmp c2_control_filter
label c2_control_done
store64 {C+48} r9
'''

def main():
    p=argparse.ArgumentParser();p.add_argument('--readers',type=Path,default=ROOT/'integration/sequence2/release');args=p.parse_args();f=args.readers
    rows=[r for r in json.loads((f/'validation.json').read_text())['text']['cases'] if r.get('kind')=='order']
    words=json.loads((f/'vocabulary.json').read_text());out=json.loads((f/'output-vocabulary.json').read_text());raw=read_models(f)['text'];controls={}
    with tempfile.TemporaryDirectory(prefix='c1-controls-') as temporary:
        local=Path(temporary);state=local/'text.rvp';state.write_bytes(raw);(local/'model.xi').write_bytes((f/'model.xi').read_bytes())
        if (f/'semantic-vocabulary.json').exists():(local/'semantic-vocabulary.json').write_bytes((f/'semantic-vocabulary.json').read_bytes())
        for mode in ['full','drop_order','erase_all']:
            cases=[]
            with Controlled(state,words,out) as m:
                m.mode=mode
                for row in rows:
                    got=m.generate(row['input'],row.get('previous',''));correct=got['terminated'] and got['tokens']==E.output_words(row['response'])
                    cases.append({'input':row['input'],'expected':row['response'],'correct':correct,**got})
            controls[mode]={'correct':sum(r['correct'] for r in cases),'total':len(cases),'cases':cases}
    report={'split':'open validation, not reserved tasks','controls':controls,
            'interpretation':'Dependence on measured ordered/scope features in a learned classical readout; no quantum advantage or circuit speedup claim.'}
    path=ROOT/'build/sequence2/controls.json';path.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');print(json.dumps({k:{a:b for a,b in v.items() if a!='cases'} for k,v in controls.items()}))

if __name__=='__main__':main()
