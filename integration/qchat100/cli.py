#!/usr/bin/env python3
"""Explicit trained QChat100 sessions. No old conversational engine fallback."""
import argparse
import contextlib
import gzip
import json
import os
from pathlib import Path
import shutil
import tempfile
import uuid
from engine import A,BANK,STRIDE,ROOT,Native,examples,words,normalize,sha

def require(ok,message):
    if not ok:raise ValueError(message)

def atomic(p,value):
    temp=p.with_name(p.name+'.'+uuid.uuid4().hex+'.pending')
    try:
        with temp.open('x') as f:
            os.chmod(temp,0o600);f.write(json.dumps(value,ensure_ascii=False,indent=2)+'\n');f.flush();os.fsync(f.fileno())
        os.replace(temp,p)
    finally:temp.unlink(missing_ok=True)

def pins():return {name:sha(ROOT/name) for name in ['ai/xi/qchat100/model.xi','integration/qchat100/engine.py','integration/qchat100/cli.py']}

def info(runtime,state,vocab):
    with Native(runtime,state) as n:
        events,_=n.execute(f'load64 r0 {A}\nprint r0\nload64 r0 {A+8}\nprint r0\nload64 r0 {A+24}\nprint r0\nstats\nqstats')
    regs=[e['value'] for e in events if e.get('type')=='register']
    s=next(e for e in events if e['type']=='stats');q=next(e for e in events if e['type']=='quantum_stats')
    require(regs[0]==100 and regs[1]==len(vocab) and regs[2]>0,'Untrained or incompatible language checkpoint')
    require(s['active_qubits']==100 and s['largest_component']==100 and s['components']==1,'Checkpoint does not own one 100-qubit register')
    require(q['clifford_components']==1 and q['adaptive_components']==0 and q['reduced_components']==0 and q['norm']==1,'Exact Clifford state profile required')
    return {'qubits':100,'training_updates':regs[2],'vocabulary':len(vocab),'quantum_payload_bytes':q['payload_bytes'],
            'quantum_state':'exact Clifford','learned_readout':'native XI binary64 hierarchical softmax','mps':False}

def prepare(session,runtime,release):
    require(not session.exists(),'Choose a new session; existing models are preserved')
    m=json.loads((release/'manifest.json').read_text())
    require(m['schema']==1 and m['qubits']==100,'Unsupported model release')
    require(Path(m['file']).name==m['file'],'Invalid model file name')
    compressed=release/m['file'];require(compressed.stat().st_size<=5*1024*1024,'Model archive exceeds 5 MiB')
    require(sha(compressed)==m['gzip_sha256'],'Model archive hash mismatch')
    with gzip.open(compressed,'rb') as f:raw=f.read(24*1024*1024+1)
    require(len(raw)<=24*1024*1024,'Checkpoint exceeds 24 MiB')
    require(__import__('hashlib').sha256(raw).hexdigest()==m['checkpoint_sha256'],'Checkpoint hash mismatch')
    vocab=json.loads((release/'vocabulary.json').read_text());lex=json.loads((release/'input-vocabulary.json').read_text())
    history=json.loads((release/'history-vocabulary.json').read_text())
    require(sha(release/'vocabulary.json')==m['vocabulary_sha256'] and sha(release/'input-vocabulary.json')==m['input_vocabulary_sha256'],'Vocabulary hash mismatch')
    require(sha(release/'history-vocabulary.json')==m['history_vocabulary_sha256'],'History vocabulary hash mismatch')
    require(3<=len(vocab)<=128 and len(set(vocab))==len(vocab),'Invalid output vocabulary')
    require(all(type(t)is str for t in lex) and len(lex)<=4096,'Invalid input vocabulary')
    session.parent.mkdir(parents=True,exist_ok=True)
    staging=Path(tempfile.mkdtemp(prefix='.bbyq-qchat100-',dir=session.parent))
    try:
        (staging/'versions').mkdir();state=staging/'versions/0.rvp';state.write_bytes(raw)
        report=info(runtime,state,vocab)
        atomic(staging/'profile.json',{'schema':1,'profile':'qchat100','runtime':str(runtime),'runtime_sha256':sha(runtime/'build/xi_session'),'source_sha256':pins()})
        atomic(staging/'HEAD.json',{'revision':0,'file':'versions/0.rvp','sha256':sha(state),'vocabulary':vocab,'input_vocabulary':lex,'history_vocabulary':history,'receipts':{}})
        atomic(staging/'conversation.json',{'messages':[],'receipts':{}})
        require(not session.exists(),'Destination appeared; refusing overwrite');staging.rename(session)
        return {'ok':True,'action':'prepare-qchat100','session':str(session),**report}
    finally:
        if staging.exists():shutil.rmtree(staging)

def load(session):
    profile=json.loads((session/'profile.json').read_text());head=json.loads((session/'HEAD.json').read_text())
    require(profile['schema']==1 and profile['profile']=='qchat100','Wrong session profile')
    runtime=Path(profile['runtime']);require(sha(runtime/'build/xi_session')==profile['runtime_sha256'],'Runtime changed')
    require(pins()==profile['source_sha256'],'Model implementation changed; preserve this session')
    f=head['file'];require(f.startswith('versions/') and Path(f).name==f[9:] and f.endswith('.rvp'),'Invalid version path')
    state=session/f;require(sha(state)==head['sha256'],'Model checkpoint hash mismatch')
    return head,runtime,state

@contextlib.contextmanager
def locked(session):
    p=session/'.write-lock';fd=os.open(p,os.O_CREAT|os.O_EXCL|os.O_WRONLY,0o600)
    try:yield
    finally:os.close(fd);p.unlink()

def reference_previous(prompt,messages):
    if not set(words(normalize(prompt))) & {'eso','mas','otra','repetirlo','repitelo','explicalo','repite'}:return ''
    return next((x['text'] for x in reversed(messages) if x['role']=='user' and not set(words(normalize(x['text']))) & {'eso','mas','repetirlo','explicalo'}),'')

def chat(head,runtime,state,message,previous=''):
    require(0<len(message.encode())<=4096,'Message must contain 1..4096 UTF-8 bytes')
    with Native(runtime,state) as n:result=n.generate(message,head['vocabulary'],previous,input_vocabulary=set(head['input_vocabulary']),history_vocabulary=set(head['history_vocabulary']))
    require(sha(state)==head['sha256'],'Read-only inference changed the checkpoint')
    return {'ok':True,'revision':head['revision'],'qubits':100,**result}

def run(args):
    session=Path(args.session).resolve()
    if args.command=='prepare':return prepare(session,Path(args.runtime).resolve(),Path(args.model).resolve())
    if args.command=='turn':
        require(args.id.replace('-','').replace('_','').isalnum() and len(args.id)<=96,'Use a stable request ID')
        with locked(session):
            head,runtime,state=load(session);c=json.loads((session/'conversation.json').read_text())
            previous=reference_previous(args.message,c['messages'])
            if args.id in c['receipts']:
                old=c['receipts'][args.id];require(old['input']==args.message,'Request ID already belongs to another message');return old['result']
            result=chat(head,runtime,state,args.message,previous)
            c['messages']=(c['messages']+[{'role':'user','text':args.message},{'role':'assistant','text':result['text']}])[-64:]
            c['receipts'][args.id]={'input':args.message,'result':result}
            require(len(c['receipts'])<=2048,'Session request limit reached; export and start a new conversation')
            atomic(session/'conversation.json',c);return result
    head,runtime,state=load(session)
    if args.command=='ask':return chat(head,runtime,state,args.message,args.previous)
    if args.command=='status':return {'ok':True,'revision':head['revision'],'checkpoint_sha256':head['sha256'],**info(runtime,state,head['vocabulary'])}
    if args.command=='export':
        target=Path(args.output).resolve()
        with target.open('xb') as out,state.open('rb') as src:shutil.copyfileobj(src,out)
        require(sha(target)==head['sha256'],'Export mismatch')
        return {'ok':True,'file':str(target),'sha256':head['sha256'],'vocabulary':head['vocabulary'],'input_vocabulary':head['input_vocabulary'],'history_vocabulary':head['history_vocabulary']}
    raise ValueError('Unknown language command')

def main():
    p=argparse.ArgumentParser(description='Trained native XI 100-qubit Spanish starter generator')
    sub=p.add_subparsers(dest='command',required=True)
    s=sub.add_parser('prepare');s.add_argument('session');s.add_argument('--runtime',required=True);s.add_argument('--model',default=str(ROOT/'integration/qchat100/release'))
    s=sub.add_parser('ask');s.add_argument('session');s.add_argument('message');s.add_argument('--previous',default='')
    s=sub.add_parser('turn');s.add_argument('session');s.add_argument('id');s.add_argument('message')
    s=sub.add_parser('status');s.add_argument('session')
    s=sub.add_parser('export');s.add_argument('session');s.add_argument('output')
    try:print(json.dumps(run(p.parse_args()),ensure_ascii=False,indent=2))
    except (ValueError,OSError,KeyError,RuntimeError) as e:print(json.dumps({'ok':False,'error':str(e)},ensure_ascii=False));raise SystemExit(1)

if __name__=='__main__':main()
