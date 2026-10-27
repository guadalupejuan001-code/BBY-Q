#!/usr/bin/env python3
"""Original supervised synthetic language campaign, entirely induced in XI.

Host: curriculum generation, lexical encoding, transport, independent scoring.
XI: tokenization of priming/text exams, construction induction, every training
sequence/label check, evidence reasoning, topic retrieval and reply selection.
The million-example stream is concept-token encoded; it is not raw web prose.
"""
import argparse,base64,gzip,hashlib,importlib.util,json,struct,subprocess,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];REPO=ROOT.parents[2]
L=8000000000000000000
PARENT_SHA='9fdf0b3f5300ea63607f6c0656d09c3ad1bfb7dbf96a167e775c48c35ae4fafc'
spec=importlib.util.spec_from_file_location('e019',ROOT.parent/'open/tests/native-e019.py')
e019=importlib.util.module_from_spec(spec);spec.loader.exec_module(e019)
e018=e019.e018;e017=e019.e017
snapshot,stores,frame=e017.snapshot,e017.stores,e017.frame
U,K,C=e017.U,e017.K,e017.C
FORMS=json.loads((ROOT/'data/constructions.json').read_text())


def u32(m,a):return sum(m.get(a+i,0)<<(8*i) for i in range(4))


def vocabulary(m):
    lex={};names={}
    for i in range(22):
        a=7200000000000001000+i*32
        for language,off in [(1,5),(2,14)]:
            t=bytes(m.get(a+off+1+j,0) for j in range(m.get(a+off,0))).decode()
            if t:lex[t]=(i+1,1,language);names[i+1,language]=t
    for i in range(e017.u16(m,K+4)):
        a=K+10000+i*40;t=bytes(m.get(a+4+j,0) for j in range(m.get(a+3,0))).decode()
        cid,kind,lang=m[a],m[a+1],m[a+2]
        lex[t]=(cid,kind,lang);names.setdefault((cid,lang),t)
    for t,(cid,kind,lang) in e017.lexicon(m).items():
        assert t not in lex or lex[t][:2]==(cid,kind),(t,lex.get(t),(cid,kind))
        lex[t]=(cid,kind,lang);names.setdefault((cid,lang),t)
    return lex,names


def role_set(f):return [x for x in ['S','P','O'] if '{'+x+'}' in f['text']]


class Campaign(e018.Examiner):
    def __init__(self,runtime,parent,out):
        super().__init__(runtime,parent,out,expected_parent=PARENT_SHA)
        self.programs['lingua-pattern']=subprocess.check_output(['bash',str(ROOT.parent/'knowledge/link.sh'),'lingua-pattern'],text=True).split('\n',1)[1]
        self.programs['lingua-cue']=subprocess.check_output(['bash',str(ROOT.parent/'knowledge/link.sh'),'lingua-cue'],text=True).split('\n',1)[1]
        self.batch_code=(ROOT/'learn-batch.xi').read_text().split('\n',1)[1]
        self.processed=0;self.validated=0;self.batches=0;self.digest=hashlib.sha256();self.raw_digest=hashlib.sha256()

    def prepare(self):
        self.run((ROOT/'birth.xi').read_text())
        lex,_=vocabulary(snapshot(self.state)[1]);next_id=e017.u16(snapshot(self.state)[1],U+4)
        added=[]
        for f in FORMS:
            for t in f['text'].split():
                if t.startswith('{') or t in lex:continue
                self.word(next_id,3,f['language'],t);lex[t]=(next_id,3,f['language'])
                added.append((next_id,3,f['language'],t));next_id+=1
        for line in (ROOT/'data/surface.psv').read_text().splitlines():
            if not line or line.startswith('#'):continue
            a,l,t=line.split('|');self.teach('open-utterance',[(U+304,int(a))],t,int(l))
        self.lex,self.names=vocabulary(snapshot(self.state)[1])
        entities=sorted(cid for cid in {v[0] for v in self.lex.values() if v[1]==1}
                        if cid not in range(13,23) and (cid,1) in self.names and (cid,2) in self.names)
        assert len(entities)>=144,len(entities)
        self.train_entities=entities[:128];self.val_entities=entities[128:]
        self.train_predicates=[23,25,28,39];self.val_predicates=[264,265]
        for line in (ROOT/'data/cues.psv').read_text().splitlines():
            if line and not line.startswith('#'):
                kind,language,text=line.split('|');self.teach('lingua-cue',[(L+48,int(kind))],text,int(language))
        for f in FORMS:
            for s,p,o in [(5,23,40),(110,25,114)]:
                labels={x:cid for x,cid in zip(['S','P','O'],[s,p,o]) if x in role_set(f)}
                text=self.render(f,labels)
                self.teach('lingua-pattern',[(U+176,f['id']),(U+177,f['intent']),(U+178,0),(U+179,f['act'])]
                           +e017.wide(U+180,labels.get('S',0))+e017.wide(U+182,labels.get('P',0))+e017.wide(U+184,labels.get('O',0)),text,f['language'])
            a=L+10000+(f['id']-1)*96
            assert snapshot(self.state)[1].get(a+2)==1,('not induced',f)
        e018.restore_context(self)
        self.training_base=snapshot(self.state)
        (self.out/'primed.rvp').write_bytes(self.state.read_bytes())
        (self.out/'words.json').write_text(json.dumps(added,ensure_ascii=False,indent=2)+'\n')
        return added

    def render(self,f,labels):
        return f['text'].format(**{r:self.names[cid,f['language']] for r,cid in labels.items()})

    def observations(self,f,validation=False,limit=None):
        roles=role_set(f)
        if validation:
            n=64 if len(roles)>1 else (16 if roles==['S'] else (2 if roles==['P'] else 1))
            ss,ps,oo=self.val_entities,self.val_predicates,list(reversed(self.val_entities))
        else:
            n=1
            for x in roles:n*=4 if x=='P' else 128
            ss=oo=self.train_entities;ps=self.train_predicates
        if limit is not None:n=min(n,limit)
        for i in range(n):
            labels={};v=i
            for r in reversed(roles):
                pool=ps if r=='P' else (ss if r=='S' else oo)
                labels[r]=pool[v%len(pool)];v//=len(pool)
            text=self.render(f,labels)
            ids=[self.lex[t][0] for t in text.split()]
            yield labels,ids,text

    def batch(self,f,rows,mode=0,reject=False):
        packed=b''.join(struct.pack('<'+'H'*(3+len(ids)),labels.get('S',0),labels.get('P',0),labels.get('O',0),*ids)
                        for labels,ids,_ in rows)
        fields=[(L+16,mode),(L+17,f['id']),(L+18,len(rows)%256),(L+19,len(rows)//256)]
        code=stores(fields)+''.join(f'store8 {L+100000+i} {b}\n' for i,b in enumerate(packed))+self.batch_code
        self.run(code,reject=reject)
        if reject:return
        self.batches+=1
        if mode:self.validated+=len(rows)
        else:
            self.processed+=len(rows)
            for labels,ids,text in rows:
                self.digest.update(bytes([f['id'],f['intent'],f['language']])+struct.pack('<'+'H'*(3+len(ids)),labels.get('S',0),labels.get('P',0),labels.get('O',0),*ids))
                self.raw_digest.update(bytes([f['id']])+text.encode()+b'\n')

    def preserve(self):
        core,m,bindings=snapshot(self.state)
        assert core==self.training_base[0] and bindings==self.training_base[2]
        outside=lambda mem:{a:b for a,b in mem.items() if not L<=a<L+200000}
        assert outside(m)==outside(self.training_base[1])
        assert not any(L+100000<=a<L+118432 for a in m)
        assert not any(m.get(L+i,0) for i in range(16,64))
        assert u32(m,L+8)==self.processed
        assert u32(m,L+12)==self.validated
        return m


def main():
    p=argparse.ArgumentParser();p.add_argument('runtime');p.add_argument('--out',default='evidence/e021-training')
    p.add_argument('--limit',type=int);p.add_argument('--batch',type=int,default=512)
    a=p.parse_args();assert 1<=a.batch<=512
    out=Path(a.out).resolve();out.mkdir(parents=True,exist_ok=True)
    parent=out/'parent.rvp';parent.write_bytes(gzip.decompress(base64.b64decode((REPO/'ai/checkpoints/BBYQ_E020_Million_Arithmetic_ES_EN.rvp.gz.b64').read_bytes())))
    e=Campaign(a.runtime,parent,out);start=time.perf_counter();added=e.prepare();priming=time.perf_counter()-start
    start=time.perf_counter()
    for f in FORMS:
        buffer=[]
        for row in e.observations(f,limit=a.limit):
            buffer.append(row)
            if len(buffer)==a.batch:e.batch(f,buffer);buffer=[]
        if buffer:e.batch(f,buffer)
        e.preserve()
        if f['id']%8==0:print('E021_LANGUAGE_TRAINED',f['id'],'ROWS',e.processed,'SECONDS',round(time.perf_counter()-start,2),flush=True)
    seconds=time.perf_counter()-start
    for f in FORMS:e.batch(f,list(e.observations(f,True)),mode=1)
    m=e.preserve()
    old=e.original[1]
    assert all(m.get(a,0)==b for a,b in old.items() if a not in {U+4,U+5,U+6,U+7})
    (e.out/'unsealed.rvp').write_bytes(e.state.read_bytes())
    report={'stage':'E021','parent_sha256':PARENT_SHA,'training_examples':e.processed,
        'distinct_concept_token_training_examples':e.processed,'validation_examples':e.validated,'held_out_binding_validation_examples':e.validated-24,'literal_form_rechecks':24,
        'batches':e.batches,'training_seconds':seconds,'priming_seconds':priming,'examples_per_second':e.processed/seconds,
        'concept_token_corpus_sha256':e.digest.hexdigest(),'surface_corpus_sha256':e.raw_digest.hexdigest(),
        'raw_construction_priming_presentations':2*len(FORMS),'cue_presentations':10,'new_constructions':len(FORMS),'total_constructions':96+len(FORMS),
        'new_lexical_entries':len(added),'total_lexical_entries':e017.u16(m,K+4)+e017.u16(m,U+6),'unique_surface_forms_including_E010':len(e.lex),'new_dialogue_acts':8,'topic_slots':8,
        'previous_learned_bytes_preserved':True,'checkpoint_bytes_before':len(e.parent.read_bytes()),
        'checkpoint_bytes_unsealed':e.state.stat().st_size,'input_representation':'full concept-token sequences and S/P/O labels; raw text priming and independent inference exams',
        'data':'original synthetic supervised syntax; no downloaded conversation corpus or external pretrained component',
        'new_world_facts':0,'open_conversation_achieved':False,'limit_per_construction':a.limit}
    (e.out/'training.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(report,ensure_ascii=False,indent=2),flush=True)


if __name__=='__main__':main()
