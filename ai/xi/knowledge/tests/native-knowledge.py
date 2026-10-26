#!/usr/bin/env python3
"""Examiner and data transport only. No knowledge inference for the agent.

Expected answers and oracle graphs remain in this process; each XI query is
given ONLY raw UTF-8 bytes and output preference. Native proofs are checked
edge by edge against teaching evidence. No external language model is used.
"""
import argparse
from collections import defaultdict, deque
import hashlib
import json
from pathlib import Path
import random
import struct
import subprocess
import time

K=7400000000000000000
D=7300000000000000000
ROOT=Path(__file__).resolve().parents[1]
REPO=ROOT.parents[2]
SOURCE_SHA='efe5585761d4745b868c83e55cc1c6356291f396649458c03814ca27b2f6b453'


def rows(name):
    return [line.split('|') for line in (ROOT/'data'/name).read_text().splitlines()
            if line and not line.startswith('#')]


def snapshot(path):
    raw=Path(path).read_bytes()
    assert raw[:5]==b'RVPC2'
    nc,nm,_=struct.unpack_from('<QQQ',raw,5)
    assert len(raw)==29+nc+nm
    core=raw[29:29+nc]
    lines=raw[29+nc:].decode().splitlines()
    assert lines[0].startswith('MXIM2 ') and lines[1]=='MXIM1 0'
    memory={};bindings=[]
    for line in lines[2:]:
        kind,address,value=line.split()
        if kind=='O':memory[int(address)]=int(value)
        else:bindings.append(line)
    return core,memory,bindings


class Examiner:
    def __init__(self,runtime,checkpoint,out):
        self.runtime=str(Path(runtime).resolve());self.original=Path(checkpoint).resolve()
        assert hashlib.sha256(self.original.read_bytes()).hexdigest()==SOURCE_SHA
        self.core,self.old,self.bindings=snapshot(self.original)
        self.out=Path(out).resolve();self.out.mkdir(parents=True,exist_ok=True)
        self.state=self.out/'state.rvp';self.event=self.out/'event.xi';self.next=self.out/'next.rvp'
        self.linked={mode:subprocess.check_output(['bash',str(ROOT/'link.sh'),mode],text=True).split('\n',1)[1]
                     for mode in ['word','query','combined']}
        self.checks=0;self.transcript=[];self.latencies=[]
        self.names={};self.aliases=defaultdict(list);self.truth={}
        for i,line in enumerate((ROOT.parent/'school/data/observations-v1.psv').read_text().splitlines()):
            if not line or line.startswith('#'):continue
            _,_,_,_,es,en=line.split('|');cid=len(self.names)+1
            self.names[cid]={1:es,2:en};self.aliases[cid]+=[es,en]
        self.run((ROOT/'birth.xi').read_text(),source=self.original)

    def preserve(self,arithmetic=False):
        core,mem,bindings=snapshot(self.state)
        assert core==self.core and bindings==self.bindings
        old={a:v for a,v in mem.items() if not K<=a<K+70_000_000}
        reference=self.old
        if arithmetic:
            mutable={D+3,*range(D+5,D+13)}
            old={a:v for a,v in old.items() if a not in mutable}
            reference={a:v for a,v in self.old.items() if a not in mutable}
        assert old==reference,'Earlier knowledge changed'
        self.checks+=1
        return mem

    def run(self,program,source=None,reject=False,arithmetic=False):
        self.event.write_text(program);self.next.unlink(missing_ok=True)
        before=self.state.read_bytes() if self.state.exists() else None
        started=time.perf_counter()
        p=subprocess.run([self.runtime,'run',str(self.event),str(source or self.state),str(self.next)],
                         capture_output=True,text=True,timeout=30)
        if reject:
            assert p.returncode!=0,'Invalid lesson accepted'
            assert not self.next.exists() and self.state.read_bytes()==before
            self.checks+=1;return ''
        assert p.returncode==0,p.stderr
        self.next.replace(self.state);self.preserve(arithmetic)
        self.latencies.append((time.perf_counter()-started)*1000)
        return p.stdout

    def frame(self,text='',lang=1,fields=()):
        data=text.encode() if isinstance(text,str) else text
        assert len(data)<=255
        stores=[(K+16,1),(K+17,len(data)),(K+3,lang)]
        stores.extend((K+128+i,b) for i,b in enumerate(data))
        stores.extend((K+offset,value) for offset,value in fields)
        return '#!reverse-pc-machine-v1\n'+''.join(f'store8 {a} {v}\n' for a,v in stores)

    def word(self,cid,kind,lang,word,reject=False):
        self.run(self.frame(word,fields=[(24,1),(25,cid),(26,kind),(27,lang)])+self.linked['word'],reject=reject)
        if not reject:
            self.names.setdefault(cid,{}).setdefault(lang,word)
            if word not in self.aliases[cid]:self.aliases[cid].append(word)

    def fact(self,s,p,o,pol=1,source=10,reject=False):
        self.run(self.frame(fields=[(24,2),(25,s),(26,p),(27,o),(28,pol),(29,source)])+
                 (ROOT/'learn-fact.xi').read_text().split('\n',1)[1],reject=reject)
        if not reject:
            key=(s,p,o);bits=self.truth.get(key,0)
            self.truth[key]=bits|pol if pol in (1,2) else bits&~(1 if pol==3 else 2)

    def calibrate(self,p,a,b,c,reject=False):
        self.run(self.frame(fields=[(24,3),(25,p),(26,a),(27,b),(28,c)])+
                 (ROOT/'calibrate.xi').read_text().split('\n',1)[1],reject=reject)

    def query(self,text,triples=(),status=1,lang=1,arithmetic=False,expected=None):
        before=snapshot(self.state)[1]
        output=self.run(self.frame(text,lang=lang)+self.linked['combined' if arithmetic else 'query'],arithmetic=arithmetic)
        regs=[json.loads(row) for row in output.splitlines() if row.startswith('{')]
        spoken=bytes(row['value'] for row in regs if row.get('register')=='r14').decode('utf-8')
        mem=self.preserve(arithmetic)
        assert {a:v for a,v in mem.items() if K+6000<=a<K+70_000_000}=={
               a:v for a,v in before.items() if K+6000<=a<K+70_000_000},'Query trained on its answer'
        assert not any(mem.get(K+i,0) for i in [*range(16,2048),*range(3000,4500)])
        if expected is None:
            expected='?' if status==0 else ('no: ' if status==2 else '')+'; '.join(
                ' '.join(self.names[cid][lang] for cid in triple) for triple in triples)+'.'
            depth=mem.get(K+15,0)
            if depth>1:
                assert len(triples)==1 and status==1
                path=[mem.get(K+2200+i,0) for i in range(depth+1)][::-1]
                s,p,o=triples[0]
                assert path[0]==s and path[-1]==o and len(path)==len(set(path))
                assert all(self.truth.get((a,p,b))==1 for a,b in zip(path,path[1:])), 'Unfounded proof edge'
                expected+=' ['+' -> '.join(self.names[cid][lang] for cid in path)+']'
            assert mem.get(K+8,0)==status, (repr(text), spoken, {i:mem.get(K+i,0) for i in range(8,16)})
        assert spoken==expected,f'{text!r}: {spoken!r} != {expected!r}'
        self.transcript.append({'input':text if isinstance(text,str) else repr(text),'output':spoken,
                                'language':lang,'proof_steps':mem.get(K+15,0),'reason':mem.get(K+9,0)})
        self.checks+=1
        return mem

    def audit(self):
        for file in ['ai/xi/e008/audit-organism.xi','ai/xi/language/audit.xi','ai/xi/school/audit.xi',
                     'ai/xi/dialogue/audit.xi','ai/xi/knowledge/audit.xi']:
            before=self.state.read_bytes();self.run((REPO/file).read_text())
            assert self.state.read_bytes()==before;self.checks+=1


def main():
    ap=argparse.ArgumentParser();ap.add_argument('runtime');ap.add_argument('checkpoint')
    ap.add_argument('--out',default='evidence/e012');ap.add_argument('--random-cases',type=int,default=200)
    ap.add_argument('--seeds',type=int,nargs='+',default=[170627,270629,370631])
    args=ap.parse_args();e=Examiner(args.runtime,args.checkpoint,args.out);started=time.time()
    e.query('gato es organismo?',status=0)
    for cid,kind,lang,word in rows('words-v1.psv'):e.word(int(cid),int(kind),int(lang),word)
    for s,p,o,pol,src in rows('facts-v1.psv'):e.fact(*map(int,(s,p,o,pol,src)))
    e.query('gato es organismo?',status=0)  # No rule before evidence.
    e.calibrate(23,40,41,42)
    for _ in range(3):e.calibrate(23,40,41,42)
    e.query('gato es organismo?',status=0)  # Repetition cannot stand for two closures.
    e.calibrate(23,41,42,43)
    e.calibrate(30,13,14,15);e.calibrate(30,14,15,16)
    e.word(150,1,1,'gato',reject=True)
    e.word(40,2,1,'mamífero',reject=True)
    e.fact(5,40,43,reject=True)  # An entity cannot silently become a predicate.
    e.fact(5,23,43,source=0,reject=True)
    e.calibrate(23,5,40,43,reject=True)  # Held-out conclusion absent from teaching.
    e.audit();(e.out/'learned-before-exam.rvp').write_bytes(e.state.read_bytes())
    print('LEARNING_AND_GUARDS_PASS',flush=True)
    learned=dict(e.truth);direct=0
    for (s,p,o),truth in learned.items():
        for lang in (1,2):
            question=' '.join(e.names[cid][lang] for cid in (s,p,o))+'?'
            e.query(question,[(s,p,o)],status=truth,lang=lang);direct+=1
    print('DIRECT_RETRIEVAL_PASS',direct,flush=True)
    edges=defaultdict(list)
    for (s,p,o),truth in learned.items():
        if p==23 and truth==1:edges[s].append(o)
    inferred=[]
    for subject in sorted(edges):
        queue=deque([(subject,0)]);visited={subject}
        while queue:
            node,depth=queue.popleft()
            for target in sorted(edges[node]):
                if target in visited:continue
                visited.add(target);queue.append((target,depth+1))
                if depth+1>=2 and (subject,23,target) not in learned:inferred.append((subject,23,target))
    for s,p,o in inferred:
        for lang in (1,2):e.query(' '.join(e.names[cid][lang] for cid in (s,p,o))+'?',[(s,p,o)],lang=lang)
    print('UNSEEN_INFERENCE_PASS',2*len(inferred),flush=True)
    groups=defaultdict(list)
    for (s,p,o),truth in learned.items():
        if truth==1:groups[(s,p)].append(o)
    for (s,p),objects in groups.items():
        for lang in (1,2):
            e.query(f'{e.names[250][lang]} {e.names[p][lang]} {e.names[s][lang]}?',
                    [(s,p,o) for o in sorted(objects)[:8]],lang=lang)
    print('OBJECT_QUESTIONS_PASS',2*len(groups),flush=True)
    # New formulations and cross-language combinations without retraining.
    for seed in args.seeds:
        rng=random.Random(seed)
        for _ in range(args.random_cases):
            s,p,o=rng.choice(inferred)
            tokens=[rng.choice(e.aliases[cid]) for cid in (s,p,o)]
            text=' \t '.join(tokens).upper()+'?'
            if rng.choice((0,1)):text='¿'+text
            e.query(text,[(s,p,o)],lang=rng.choice((1,2)))
        print('MIXED_LANGUAGE_PASS',seed,args.random_cases,flush=True)
    for text in ['bbyq tiene conciencia?','software es organismo?','conciencia es inteligencia?',
                 'cero sigue tres?','gato necesita oxígeno?','fantasma es organismo?',
                 '¿qué es fantasma?', 'qué necesita software?', 'qué es', 'gato es animal ahora?',
                 'gato es animal??', 'gato, es animal?', b'\xc3']:
        e.query(text,status=0)
    print('UNKNOWNS_PASS',flush=True)
    # Contradiction blocks both direct certainty and traversal through its edge.
    e.fact(5,23,40,2);e.query('gato es mamífero?',status=0);e.query('gato es organismo?',status=0)
    e.fact(5,23,40,4);e.query('gato es organismo?',[(5,23,43)])
    e.fact(40,23,42,2);e.query('gato es organismo?',status=0)
    e.fact(40,23,42,4);e.query('gato es organismo?',[(5,23,43)])
    e.query('cero sigue dos?',[(13,30,15)],status=2)
    e.audit()
    stable=e.state.read_bytes();saved_truth=dict(e.truth)
    e.run(f'#!reverse-pc-machine-v1\nstore8 {K+2} 2\n')
    e.fact(5,23,40,reject=True)
    e.calibrate(23,40,41,42,reject=True)
    e.state.write_bytes(stable)

    # Same algorithms, unfamiliar names and a completely separate relation.
    for cid in range(200,216):
        e.word(cid,1,1,'nodo'+chr(97+cid-200));e.word(cid,1,2,'node'+chr(97+cid-200))
    e.word(220,2,1,'enlaza');e.word(220,2,2,'links')
    for a,b,c in [(210,211,212),(213,214,215)]:
        e.fact(a,220,b);e.fact(b,220,c);e.fact(a,220,c);e.calibrate(220,a,b,c)
    for cid in range(200,208):e.fact(cid,220,cid+1)
    e.fact(208,220,200)  # Cycle must terminate.
    long=e.query('nodoa enlaza nodoi?',[(200,220,208)])
    assert long[K+15]==8
    e.query('nodoa enlaza kelvin?',status=0)
    e.audit();(e.out/'unfamiliar-graph-control.rvp').write_bytes(e.state.read_bytes())
    e.state.write_bytes(stable);e.truth=saved_truth
    # One native text entry point retains the existing E011 arithmetic program.
    e.query('¿dos mas tres?',arithmetic=True,expected='cinco')
    e.query('minus one',arithmetic=True,lang=2,expected='four')
    e.preserve()  # The final arithmetic referent equals the original E011 state.
    e.query('¿QUÉ ES NEURONA?',[(78,23,77)])
    e.query('qué estudia filosofía?',[(195,39,103),(195,39,180)])
    e.audit()
    final=e.out/'BBYQ_E012_Knowledge_ES_EN.rvp';final.write_bytes(e.state.read_bytes())
    mem=e.preserve();count=lambda offset:mem.get(K+offset,0)+256*mem.get(K+offset+1,0)
    report={'parent_checkpoint_sha256':SOURCE_SHA,'old_training_replayed':False,
            'new_lexical_entries':count(4),'new_symbolic_concepts':len({int(r[0]) for r in rows('words-v1.psv')}),
            'inherited_grounded_concepts':22,'taught_propositions':count(6),
            'direct_retrieval_questions':direct,'unseen_inferred_questions':2*len(inferred),
            'object_questions':2*len(groups),'mixed_language_unseen_questions':args.random_cases*len(args.seeds),'mixed_test_seeds':args.seeds,
            'eight_hop_unfamiliar_graph_control':True,'cycle_termination':True,'invalid_schema_rejected_transactionally':True,
            'rule_retraction_and_restoration':True,'conflict_abstention':True,
            'original_core_and_all_previous_knowledge_unchanged':True,
            'all_previous_logical_bytes_equal_at_completion':True,'five_audits_read_only':True,
            'checks':e.checks,'final_state_bytes':final.stat().st_size,
            'final_state_sha256':hashlib.sha256(final.read_bytes()).hexdigest(),
            'elapsed_seconds':time.time()-started,
            'limits':['symbolic teacher-provided concepts, not real perception','3-token question grammar',
                      'Latin-1 Spanish UTF-8 and ASCII only','512 new lexical entries','512 registered facts',
                      '8 answers per object query','8 calibration witnesses per predicate',
                      '64 BFS expansions and 31 proof steps','no general conversation','no subjective-experience claim']}
    (e.out/'results.json').write_text(json.dumps(report,indent=2)+'\n')
    (e.out/'transcript.jsonl').write_text(''.join(json.dumps(x,ensure_ascii=False)+'\n' for x in e.transcript))
    e.event.unlink(missing_ok=True);e.next.unlink(missing_ok=True)
    print(json.dumps(report,indent=2))


if __name__=='__main__':main()
