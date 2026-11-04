"""Text codec, native XI transport and measurements. No host optimizer/model."""
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys
import unicodedata

ROOT=Path(__file__).resolve().parents[2]
A=8160000000000000000
BANK=A+1000000
STRIDE=1024
FEATURES=868

def words(s):
    return re.findall(r'\w+|[.!?,]',s.lower(),re.UNICODE)

def normalize(s):
    return ''.join(c for c in unicodedata.normalize('NFD',s.lower()) if unicodedata.category(c)!='Mn')

def fnv(s, seed=2166136261):
    n=seed
    for b in s.encode(): n=((n^b)*16777619)&0xffffffff
    return n

def bits(prompt,prefix,previous='',input_vocabulary=None,history_vocabulary=None):
    value=[0]*100
    for token in words(normalize(prompt)):
        if input_vocabulary is not None and token not in input_vocabulary:continue
        for salt in ['a','b','c']: value[fnv(salt+token)%48]=1
    for token in words(normalize(previous)):
        if input_vocabulary is not None and token not in input_vocabulary:continue
        if history_vocabulary is not None and token not in history_vocabulary:continue
        for salt in ['p','q','r']: value[48+fnv(salt+token)%16]=1
    last=prefix[-1] if prefix else '<bos>'
    before=prefix[-2] if len(prefix)>1 else '<bos>'
    h=fnv(last)
    for i in range(16): value[64+i]=(h>>i)&1
    h=fnv(before)
    for i in range(8): value[80+i]=(h>>i)&1
    n=len(prefix)
    value[88+min(n,11)]=1
    return value

def detokenize(tokens):
    proper={'x':'X','bby':'BBY','q':'Q','xi':'XI','ether':'Ether'}
    result=' '.join(proper.get(t,t) for t in tokens)
    result=re.sub(r'\s+([.!?,])',r'\1',result)
    return result[:1].upper()+result[1:]

def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def library(): return (ROOT/'ai/xi/qchat100/model.xi').read_text()

def source(body): return '#!reverse-pc-machine-v1\nbudget 50000000\n'+body+'\nhalt\n'+library()

def stage(raw):
    assert len(raw)==100 and all(type(x)is int and x in [0,1] for x in raw)
    return '\n'.join(f'store8 {A+1000+i} {b}' for i,b in enumerate(raw))+'\n'

def metric(events,name): return next(e['value'] for e in events if e.get('type')=='metric' and e['name']==name)

class Native:
    def __init__(self,runtime,state):
        self.runtime=Path(runtime).resolve()
        sys.path.insert(0,str(self.runtime/'scripts'))
        from xi_session_client import XiSession
        self.s=XiSession(self.runtime/'build/xi_session',state)
    def execute(self,body): return self.s.execute(source(body))
    def save(self,p): return self.s.save(p)
    def close(self): self.s.close()
    def __enter__(self): return self
    def __exit__(self,*args): self.close()
    def generate(self,prompt,vocab,previous='',mode=0,max_tokens=16,input_vocabulary=None,history_vocabulary=None):
        prefix=[]; probability=0.;elapsed=0.
        for _ in range(max_tokens):
            events,ms=self.execute(stage(bits(prompt,prefix,previous,input_vocabulary,history_vocabulary))+f'store64 {A+80} {mode}\ncall qchat_encode\ncall qchat_next')
            token=next(e['value'] for e in events if e.get('type')=='register' and e.get('register')=='r12')
            elapsed+=ms;probability+=metric(events,'log_probability')
            if token==0: return {'text':detokenize(prefix),'tokens':prefix,'terminated':True,'log_probability':probability,'elapsed_ms':elapsed}
            if not 0<=token<len(vocab):raise ValueError('Native model produced an invalid vocabulary entry')
            prefix.append(vocab[token])
        return {'text':detokenize(prefix),'tokens':prefix,'terminated':False,'log_probability':probability,'elapsed_ms':elapsed}

def examples(records,vocab,input_vocabulary=None,history_vocabulary=None):
    ids={token:i for i,token in enumerate(vocab)}
    result=[];seen=set()
    for record in records:
        prefix=[]
        for target in [*words(record['response']),'<eos>']:
            raw=bits(record['input'],prefix,record.get('previous',''),input_vocabulary,history_vocabulary)
            label=ids[target];key=(tuple(raw),label)
            if key not in seen:result.append((raw,label));seen.add(key)
            prefix.append(target)
    return result

def evaluate(runtime,state,records,vocab,mode=0,input_vocabulary=None,history_vocabulary=None):
    rows=[]
    with Native(runtime,state) as model:
        for record in records:
            prediction=model.generate(record['input'],vocab,record.get('previous',''),mode,input_vocabulary=input_vocabulary,history_vocabulary=history_vocabulary)
            rows.append({'input':record['input'],'previous':record.get('previous',''),'expected':detokenize(words(record['response'])),
                         **prediction,'correct':prediction['tokens']==words(record['response'])})
        usage=model.s.metrics()
    return {'examples':len(rows),'exact_responses':sum(r['correct'] for r in rows),'exact_response_accuracy':sum(r['correct'] for r in rows)/len(rows) if rows else None,
            'terminated':sum(r['terminated'] for r in rows),'mean_response_ms':sum(r['elapsed_ms'] for r in rows)/len(rows) if rows else None,
            'peak_rss_kib':usage['peak_rss_kib'],'cases':rows}
