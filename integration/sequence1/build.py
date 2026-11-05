#!/usr/bin/env python3
"""Resolve data addresses and fixed frame widths; no host inference."""
import json
from schema import ROOT,C,S,FIELD_WIDTHS,FEATURE_STRIDE,NODE_STRIDE,HEAD_STRIDE,LIMITS,expand

def source():
 text=(ROOT/'ai/xi/sequence1/model.xi.in').read_text()
 frame=[];offset=0
 for field,width in enumerate(FIELD_WIDTHS):
  frame.extend([f'load64 r1 {S["FRAME"]+8*field}','cmp r1 0','jlt c1_bad_frame',f'set r2 {offset}',f'set r3 {width}',f'label c1_pack_{field}','mov r0 r2',f'add r0 {S["BITS"]}','mov r4 r1','mod r4 2','store8 $r0 r4','div r1 2','add r2 1','sub r3 1','cmp r3 0',f'jgt c1_pack_{field}','cmp r1 0','jne c1_bad_frame'])
  offset+=width
 frame+= [f'store64 {S["QM"]+80} 0','call qchat_encode']
 offset=0
 for field,width in enumerate(FIELD_WIDTHS):
  frame.extend(['set r1 0','set r4 1',f'set r2 {offset}',f'set r3 {width}',f'label c1_unpack_{field}','mov r0 r2',f'add r0 {S["OBS"]}','load8 r5 $r0','cmp r5 0','jlt c1_bad_frame','cmp r5 1','jgt c1_bad_frame','mul r5 r4','add r1 r5','mul r4 2','add r2 1','sub r3 1','cmp r3 0',f'jgt c1_unpack_{field}',f'store64 {S["MEASURED"]+field*8} r1',f'load64 r0 {S["FRAME"]+field*8}','cmp r0 r1','jne c1_bad_frame'])
  offset+=width
 frame+= [f'store64 {C+184} 1',f'load64 r0 {C+256}','add r0 1',f'store64 {C+256} r0','ret','label c1_bad_frame',f'store64 {C+184} 4','ret']
 text=text.replace('# FRAME_IMPLEMENTATION','\n'.join(frame)).replace('%FEATURE_STRIDE%',str(FEATURE_STRIDE)).replace('%NODE_STRIDE%',str(NODE_STRIDE)).replace('%HEAD_STRIDE%',str(HEAD_STRIDE))
 text=expand(text)
 assert '@' not in text and '%FEATURE' not in text
 return text+'\n'+(ROOT/'ai/xi/qchat100/model.xi').read_text()

def main():
 out=ROOT/'build/sequence1';out.mkdir(parents=True,exist_ok=True);(out/'model.xi').write_text(source());(out/'schema.json').write_text(json.dumps({'version':'C1-Sequence-1','base':C,'addresses':S,'field_widths':FIELD_WIDTHS,'feature_stride':FEATURE_STRIDE,'node_stride':NODE_STRIDE,'head_stride':HEAD_STRIDE,'limits':LIMITS},indent=2)+'\n')
if __name__=='__main__':main()
