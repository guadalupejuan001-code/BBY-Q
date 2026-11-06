#!/usr/bin/env python3
"""Freeze real Python/native codec results for Android parity checks."""
import json,random,tempfile
from pathlib import Path
import build as B
import engine as E
from schema import C,S,ROOT,FIELD_WIDTHS

def main():
 B.main();rng=random.Random(2026110504)
 prompts=['dato','nos','memoria','no memoria','sí si año ano niño nino','Neral Blanco y Orenda Verde',
          '137 + 24 = 161','50,25 / 2','café cafe\u0301','🙂 👩\u200d🔬','árbol\nárbol\tárbol','１２٣ 137',
          'İΣ ΑΣ','☀︎ \u0085 fin','no\u001cno','']
 prompts+= [f'{"no " if i%2 else ""}Neral{i} Orenda{i} {137+i} + {24+i}. año sí niño' for i in range(112)]
 words=['<pad>'];rows=[]
 with tempfile.TemporaryDirectory(prefix='c1-android-') as directory:
  path=Path(directory)/'state.rvp';E.birth(path,80)
  with E.Model(path,words,['<eos>']) as model:
   for i,prompt in enumerate(prompts):
    previous='define memoria' if i%3==0 else '';text=model.prepare(prompt,previous)
    count=model.number(40)
    rows.append({'prompt':prompt,'previous':previous,'tokens':text['tokens'],'raw_hex':text['raw'].hex(),'feature_count':count,'features_hex':model.memory(S['F'],count*8).hex()})
 frames=[[0]*9,[(1<<width)-1 for width in FIELD_WIDTHS]]+[[rng.randrange(1<<width) for width in FIELD_WIDTHS] for _ in range(62)]
 result={'version':'C1-Sequence-1','vocabulary':words,'codec_cases':rows,'frames':frames}
 out=ROOT/'android-personal/app/src/androidTest/assets/sequence1-codec.json';out.parent.mkdir(parents=True,exist_ok=True);out.write_text(json.dumps(result,ensure_ascii=False)+'\n')
 print(json.dumps({'android_codec_cases':len(rows),'frames':len(frames),'bytes':out.stat().st_size}))
if __name__=='__main__':main()
