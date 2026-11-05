#!/usr/bin/env python3
"""A content-focused input codec, with all response learning still in native XI."""
import copy
import run as R

FUNCTION_WORDS='a al algo acerca ayúdame ayuda ayudarme comprender concepto conocer cuenta cuéntalo de del decir define definición dime el en entender es esa ese eso estos explica explícame explicarlo favor forma gustaría háblame interesa la las lo los me mi necesito para por podrías puedes puedo qué que querer quiero quisiera representa significado sobre saber si su te termino término tu tus un una unos veces vez otra más mas manera modo cómo como'

def main():
    root=R.OUT;out=root/'qchat-content'
    if out.exists():raise ValueError('Content refinement already exists')
    assert not (root/'FINAL-TEST-OPENED.json').exists()
    excluded={t for s in FUNCTION_WORDS.split() for t in R.QE.words(R.QE.normalize(s))}
    plan={'reason':'Validation diagnostics showed unrelated prefixes and function words changing otherwise learned-topic replies. Remove generic function words from the existing binary input codec.',
      'excluded_tokens':sorted(excluded),'epochs':[5,10,20],'thresholds':R.P['thresholds'],'test_still_closed':True,
      'learning':'Native XI SGD on the same curated training set; no host generation, semantic answer table or test examples used in training'}
    R.atomic(R.ROOT/'integration/balance/refinement-content.json',plan)
    out.mkdir();(out/'qchat-original.rvp').write_bytes((root/'qchat-original.rvp').read_bytes())
    R.OUT=out;R.P=copy.deepcopy(R.P);R.P['training']['qchat_epochs']=plan['epochs']
    R.qchat(excluded_tokens=excluded)

if __name__=='__main__':main()
