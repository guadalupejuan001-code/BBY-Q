#!/usr/bin/env python3
"""Second training arm after validation regression. The final test stays closed."""
import copy,json
from pathlib import Path
import run as R

def main():
    root=R.OUT;out=root/'qchat-frequency20'
    if out.exists():raise ValueError('Refinement exists; preserve it')
    assert not (root/'FINAL-TEST-OPENED.json').exists()
    plan={'reason':'First-arm validation at epoch 10 retained unknown refusal but reduced known/context accuracy. Refine the codec using training-only token frequencies.',
      'input_frequency_limit':20,'epochs':[5,10,20],'thresholds':R.P['thresholds'],'test_still_closed':True,
      'choice_of_frequency_limit':'Training-only collision audit: limit 15 collapsed labels; limit 20 retained all distinct training labels. No test or validation responses chose token membership.',
      'optimization':'Native XI readout SGD; no host answer selection or lookup at inference'}
    R.atomic(R.ROOT/'integration/balance/refinement.json',plan)
    out.mkdir();(out/'qchat-original.rvp').write_bytes((root/'qchat-original.rvp').read_bytes())
    R.OUT=out;R.P=copy.deepcopy(R.P);R.P['training']['qchat_epochs']=plan['epochs']
    R.qchat(input_frequency_limit=plan['input_frequency_limit'])

if __name__=='__main__':main()
