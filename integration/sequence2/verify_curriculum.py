#!/usr/bin/env python3
"""Check intended task labels and split boundaries before expensive training."""
import json
from collections import Counter
import data as D

def main():
 corpus=D.corpus();topics=dict(D.TOPICS);sets={};counts={}
 for split,rows in corpus.items():
  keys={};counts[split]=dict(Counter(r.get('kind','known') for r in rows))
  for row in rows:
   key=(row['input'],row.get('previous',''))
   if key in keys and keys[key]!=row['response']:raise RuntimeError('Contradictory text labels')
   keys[key]=row['response']
   if row.get('kind')=='order':
    tokens=row['input'].split()
    if len(tokens)!=4 or tokens[0]!='define' or tokens[2]!='no' or tokens[1] not in topics or tokens[3] not in topics or tokens[1]==tokens[3]:raise RuntimeError('Malformed order curriculum')
    if topics[tokens[1]]!=row['response']:raise RuntimeError('Order target is not first topic')
  sets[split]=set(keys)
 for a,b in [('train','validation'),('train','test'),('validation','test')]:
  if sets[a]&sets[b]:raise RuntimeError('Text split overlap')
 intents={}
 for split in sets:
  rows=D.intentions(split);intents[split]={(r['input'],r.get('previous','')) for r in rows}
  if len(intents[split])!=len(rows):raise RuntimeError('Duplicated intent examples inflate scores')
 for a,b in [('train','validation'),('train','test'),('validation','test')]:
  if intents[a]&intents[b]:raise RuntimeError('Intent split overlap')
 print(json.dumps({'curriculum_integrity':True,'text_groups':counts,'intent_unique_examples':{k:len(v) for k,v in intents.items()}}))
if __name__=='__main__':main()
