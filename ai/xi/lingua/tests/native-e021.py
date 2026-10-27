#!/usr/bin/env python3
"""Release exam and same-harness comparisons; never feed answers to the agent."""
import argparse,base64,gzip,hashlib,importlib.util,json,statistics,subprocess,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];REPO=ROOT.parents[2]
spec=importlib.util.spec_from_file_location('language',ROOT/'tests/native-language.py')
lang=importlib.util.module_from_spec(spec);spec.loader.exec_module(lang)
e019,e018,e017=lang.e019,lang.e018,lang.e017
L,U,K,C=lang.L,lang.U,lang.K,lang.C
snapshot,stores=lang.snapshot,lang.stores
Session,decode_result=e017.Session,e017.decode_result
SURFACE=e017.SURFACE
SOCIAL={(int(a),int(l)):t for a,l,t in [x.split('|') for x in (ROOT/'data/surface.psv').read_text().splitlines() if x and not x.startswith('#')]}
CHECKPOINT='BBYQ_E021_Language_Dialogue_ES_EN.rvp'


def percentiles(times):
    return {'median':statistics.median(times),'p95':sorted(times)[max(0,(len(times)*95+99)//100-1)]}


def knowledge(path):return e017.immutable(path)


class Examiner(e018.Examiner):
    def __init__(self,runtime,parent,out):
        super().__init__(runtime,parent,out,expected_parent=lang.PARENT_SHA)
        self.programs['lingua-pattern']=subprocess.check_output(['bash',str(ROOT.parent/'knowledge/link.sh'),'lingua-pattern'],text=True).split('\n',1)[1]

    def check(self,text,expected,language=1,session=None,readonly=True):
        before=knowledge(self.state);ledger=e017.stories.ledger(snapshot(self.state)[1])
        if session:raw,ms=session.request(text,language)
        else:
            started=time.perf_counter_ns();raw=self.run(lang.frame(text,language)+self.programs['conversation']);ms=(time.perf_counter_ns()-started)/1e6
        out=decode_result(raw)
        assert out==expected,(text,out,expected)
        after=knowledge(self.state)
        assert after[0]==self.original[0] and after[2]==self.original[2]
        # Changes within U are allowed only for explicit teaching. The topic
        # cache is ephemeral, excluded by the shared immutable-state helper.
        outside=lambda m:{a:b for a,b in m.items() if not U<=a<U+2**51}
        assert outside(before[1])==outside(after[1]),'earlier knowledge or grammar changed'
        if readonly:
            assert after==before,'a query changed learned knowledge'
            assert ledger==e017.stories.ledger(snapshot(self.state)[1])
        m=snapshot(self.state)[1]
        assert not any(m.get(U+i,0) for i in range(63,512))
        assert not any(m.get(L+i,0) for i in range(16,64))
        assert not any(L+100000<=a<L+118432 for a in m)
        self.checks+=1;self.times.append(ms)
        self.transcript.append({'input':text,'language':language,'output':out,'ms':ms})
        return m


def answer(subject,language,kind='require',why=False):
    tail={'require':('requiere agua.','requires water.'),'other':('requiere energía.','requires energy.'),
          'definition':('es clasea.','is clasea.')}[kind][language-1]
    text=SURFACE[9 if why else 8,language]+' '+subject.capitalize()+' '+tail
    if why:
        edge1='es' if language==1 else 'is';edge2='requiere' if language==1 else 'requires'
        text+=f' [{subject} --{edge1}--> clasea --{edge2}--> '+('agua]' if language==1 else 'water]')
    return text


def exam_prompt(f,s):
    l=f['language'];roles=lang.role_set(f)
    values={'S':s,'P':'requiere' if l==1 else 'requires','O':'agua' if l==1 else 'water'}
    q=f['text'].format(**values)
    if f['intent']==13:expected=SOCIAL[f['act'],l]
    elif f['intent']==3:expected=SURFACE[1,l]
    elif f['intent'] in [8,12]:expected=answer(s,l,'definition')
    else:expected=answer(s,l,why=f['intent']==5)
    return q,expected


def prepare_probe(session,f,s,other):
    if f['intent'] in [9,10,12]:session.request(f'{s} requiere agua?')
    elif f['intent'] in [14,15]:
        session.request(f'{s} requiere agua?');session.request(f'{other} requiere energía?')


def text_transfer(e,binary,learned,dialogs=8):
    before=e.checks;covered=set();timings=[]
    with Session(binary,e.state,e.program) as session:
        for i in range(dialogs):
            s=f'conversa{i:03d}';other=f'alterno{i:03d}'
            e.lesson(f'aprende que {s} es clasea',session=session)
            e.lesson(f'aprende que {other} es claseb',session=session)
            # Every new construction transfers to a new entity and a predicate
            # omitted from all million-example syntax training sequences.
            for f in lang.FORMS:
                prepare_probe(session,f,s,other)
                target=s+(f't{f["id"]}' if f['intent']==3 else '')
                q,expected=exam_prompt(f,target)
                if i%3==1:q=q.upper()
                if f['intent']!=3 and i%2:q+='?'
                e.check(q,expected,f['language'],session=session,readonly=f['intent']!=3)
                timings.append(e.times[-1]);covered.add(f['id'])
                if f['intent']==3:
                    e.check(f'{target} requiere agua?',answer(target,1),session=session)
            if i%2==1:print('E021_TEXT_TRANSFER',i+1,'DIALOGUES',e.checks-before,flush=True)
        metrics=session.metrics()
    assert covered==set(range(1,129))
    e.state.write_bytes(learned)
    return {'dialogues':dialogs,'all_new_constructions_examined':128,'new_form_queries':128*dialogs,
            'checks':e.checks-before,'query_ms':percentiles(timings),'metrics':metrics,
            'held_out':'novel entities and requires predicate; surface construction frames are taught'}


def topic_and_integrity(e,binary,learned):
    before=e.checks
    with Session(binary,e.state,e.program) as s:
        e.check('volvamos a gato',e019.CLARIFY[1],session=s)
        for i in range(10):
            name=f'tema{i:02d}';e.lesson(f'aprende que {name} es clasea',session=s)
            e.check(f'me gustaría saber qué requiere {name}',answer(name,1),session=s)
        # Exactly eight topics; the two oldest are deliberately evicted.
        e.check('volvamos a tema00',e019.CLARIFY[1],session=s)
        e.check('return to the topic of tema02',answer('tema02',2),2,session=s)
        e.check('muchas gracias',SOCIAL[17,1],session=s)
        e.check('y entonces qué requiere',answer('tema02',1),session=s)
        # A resumed topic reruns evidence; it cannot reuse an obsolete answer.
        e.check('olvida que tema02 es clasea',SURFACE[3,1],session=s,readonly=False)
        e.check('volvamos a tema02',SURFACE[4,1],session=s)
        e.check('y entonces qué requiere',e019.CLARIFY[1],session=s)
        e.lesson('aprende que tema02 es clasea',session=s)
        e.check('volvamos a tema02',answer('tema02',1),session=s)
        e.check('confirma si tema02 requiere agua',answer('tema02',1),session=s)
        e.lesson('aprende que tema02 no requiere agua',session=s)
        neg=SURFACE[8,1]+' Tema02 no requiere agua.'
        e.check('retoma el tema de tema02',neg,session=s)
        e.lesson('aprende que tema02 requiere agua',session=s)
        e.check('volvamos a tema02',SURFACE[5,1],session=s)
        # A teaching-like question never writes a new assertion or concept.
        for q in ['te enseño que falso es clasea?','please learn the fact that falseword is clasea?']:
            m=knowledge(e.state);raw,_=s.request(q);assert decode_result(raw)==SURFACE[4,1]
            assert knowledge(e.state)==m
    e.state.write_bytes(learned)
    with Session(binary,e.state,e.program) as s:
        e.lesson('aprende que persiste es clasea',session=s)
        e.check('me gustaría saber qué requiere persiste',answer('persiste',1),session=s)
        e.check('i need to know what gato requires',SURFACE[4,2],2,session=s)
    with Session(binary,e.state,e.program) as s:
        e.check('back to persiste',answer('persiste',2),2,session=s)
        pending=Path(str(e.state)+'.pending');pending.mkdir();before_bytes=e.state.read_bytes()
        try:
            try:s.request('te enseño que falloguardado es clasea');raise AssertionError('failed save accepted')
            except RuntimeError as err:assert 'cannot write state' in str(err)
            assert e.state.read_bytes()==before_bytes
        finally:pending.rmdir()
        e.check('what does that mean',answer('persiste',2,'definition'),2,session=s)
    e.run((ROOT.parent/'stories/reset-episode.xi').read_text())
    with Session(binary,e.state,e.program) as s:
        e.check('back to persiste',e019.CLARIFY[2],2,session=s)
        e.check('y entonces qué requiere',e019.CLARIFY[1],session=s)
    e.state.write_bytes(learned)
    print('E021_TOPIC_EVICTION_RESEARCH_CONFLICT_RESTART_RESET_AND_ROLLBACK_PASS',flush=True)
    return {'checks':e.checks-before,'topics':8,'eviction':True,'fresh_evidence_on_resume':True,'restart_reset_save_rollback':True}


def training_controls(e,binary,learned,unsealed):
    c=lang.Campaign(e.runtime,e.parent,e.out/'training-controls');c.state.write_bytes(unsealed)
    f=lang.FORMS[0];c.lex,c.names=lang.vocabulary(snapshot(c.state)[1])
    # A fully correct row followed by an incorrect label rolls back both rows.
    labels={'S':5,'P':25,'O':110};text=c.render(f,labels);ids=[c.lex[t][0] for t in text.split()]
    bad={**labels,'S':6}
    c.batch(f,[(labels,ids,text),(bad,ids,text)],reject=True)
    # Identical raw demonstrations cannot induce this three-variable frame.
    a=L+10000;c.run(stores([(a+i,0) for i in range(96)]))
    fields=[(U+176,1),(U+177,2),(U+178,0),(U+179,0)]+e017.wide(U+180,5)+e017.wide(U+182,25)+e017.wide(U+184,110)
    for _ in range(4):c.teach('lingua-pattern',fields,'me gustaría saber si gato necesita agua')
    assert snapshot(c.state)[1].get(a+2,0)==0
    c.run((ROOT/'seal.xi').read_text(),reject=True)
    # Sealed grammar cannot be overwritten by a structured syntax lesson.
    c.state.write_bytes(learned);c.teach('lingua-pattern',fields,text,reject=True)
    # Counterfactual experiment: reverse subject/object supervision in one
    # experimental copy. Same XI source and raw phrase, different learned roles.
    c.state.write_bytes(unsealed);m=snapshot(c.state)[1]
    total=lang.u32(m,L+8)-lang.u32(m,a+80);val=lang.u32(m,L+12)-lang.u32(m,a+84)
    put=lambda address,value:[(address+i,(value>>(i*8))&255) for i in range(4)]
    c.run(stores([(a+i,0) for i in range(96)]+put(L+8,total)+put(L+12,val)))
    for s,p,o in [(5,23,40),(110,25,114)]:
        text=c.render(f,{'S':s,'P':p,'O':o})
        fields=[(U+176,1),(U+177,2),(U+178,0),(U+179,0)]+e017.wide(U+180,o)+e017.wide(U+182,p)+e017.wide(U+184,s)
        c.teach('lingua-pattern',fields,text)
    c.train_entities=list(range(40,168));c.train_predicates=[23,25,28,39]
    c.val_entities=list(range(170,190));c.val_predicates=[264,265]
    for validation,n in [(False,1024),(True,64)]:
        buf=[]
        for labels,ids,text in c.observations(f,validation,limit=n):
            labels={**labels,'S':labels['O'],'O':labels['S']};buf.append((labels,ids,text))
            if len(buf)==512:c.batch(f,buf,mode=int(validation));buf=[]
        if buf:c.batch(f,buf,mode=int(validation))
    c.run((ROOT/'seal.xi').read_text());c.run((ROOT/'audit.xi').read_text())
    with Session(binary,c.state,e.program) as s:
        s.request('aprende que cfalfa es clasea')
        raw,_=s.request('me gustaría saber si cfalfa requiere agua')
        assert decode_result(raw)==SURFACE[4,1],decode_result(raw)
    e.state.write_bytes(learned)
    print('E021_ATOMIC_LABEL_REJECTION_REPETITION_AND_COUNTERFACTUAL_ROLES_PASS',flush=True)


FREE_PROMPTS=[
 ('oye dime qué requiere {s}',1,'require'),('me pregunto qué requiere {s}',1,'require'),
 ('puedes hablarme un poco de {s}',1,'definition'),('y hablando de {s} qué requiere',1,'require'),
 ('qué es lo que requiere {s}',1,'require'),('me interesa conocer lo que requiere {s}',1,'require'),
 ('quiero que me cuentes qué requiere {s}',1,'require'),('podrías explicarme un poco sobre {s}',1,'definition'),
 ('would you mind telling me what {s} requires',2,'require'),('i am curious about what {s} requires',2,'require'),
 ('could we discuss what {s} requires',2,'require'),('give me some information about {s}',2,'definition'),
 ('which resources does {s} require',2,'require'),('let me know what {s} requires',2,'require'),
 ('say what {s} requires in other words',2,'require'),('can you tell me a little about {s}',2,'definition')]


def clause_generalization(session,version,transcript):
    session.request('aprende que clausanueva es clasea')
    session.request('aprende que otraentidad es claseb')
    positive=negative=0;times=[]
    for f in json.loads((ROOT/'data/unseen-clause-exam.json').read_text()):
        q=f['text'].format(S='clausanueva',OTHER='otraentidad');l=f['language']
        raw,ms=session.request(q,l);out=decode_result(raw)
        if f['kind']=='require':
            expected=answer('clausanueva',l);ok=out.partition(' [')[0]==expected;positive+=ok;times.append(ms)
        else:
            expected='abstain'
            ok=out in [SURFACE[4,l],SURFACE[11,l],e017.conversation.ACTS[3,l],e019.CLARIFY[l]];negative+=ok
        transcript.append({'version':version,'suite':'unseen_compositional_clauses','kind':f['kind'],'input':q,'output':out,'expected':expected,'pass':ok,'ms':ms})
    return {'unseen_questions':{'correct':positive,'total':12},'abstention_controls':{'correct':negative,'total':12},'query_ms':percentiles(times)}


def comparisons(e,binary,learned):
    # Identical input, ordered setup, examiner oracle, owner runtime and source.
    # The only varying artifact is the decoded learned-state checkpoint.
    versions=[('E017','BBYQ_E017_Open_Dialogue_ES_EN.rvp.gz.b64'),
              ('E018','BBYQ_E018_Concise_Dialogue_ES_EN.rvp.gz.b64'),
              ('E019','BBYQ_E019_Context_Questions_ES_EN.rvp.gz.b64'),
              ('E020','BBYQ_E020_Million_Arithmetic_ES_EN.rvp.gz.b64'),('E021',None)]
    # Discover the exact E017 filename locally without inventing a checkpoint.
    versions[0]=('E017',next((REPO/'ai/checkpoints').glob('BBYQ_E017*.gz.b64')).name)
    results=[];transcript=[]
    for version,name in versions:
        seed=learned if name is None else gzip.decompress(base64.b64decode((REPO/'ai/checkpoints'/name).read_bytes()))
        e.state.write_bytes(seed);mem=snapshot(e.state)[1];correct=0;times=[];math_correct=0;free_correct=0
        with Session(binary,e.state,e.program) as s:
            for f in lang.FORMS:
                # Independent fixture for every probe keeps curricula balanced;
                # a successful new teaching act cannot help a later probe.
                subject=f'sondal{f["id"]:03d}';other=f'otrol{f["id"]:03d}'
                s.request(f'aprende que {subject} es clasea');s.request(f'aprende que {other} es claseb')
                prepare_probe(s,f,subject,other)
                q,expected=exam_prompt(f,subject);raw,ms=s.request(q,f['language']);out=decode_result(raw)
                ok=out==expected or (f['intent']!=5 and out.partition(' [')[0]==expected);correct+=ok;times.append(ms)
                transcript.append({'version':version,'suite':'new_128_forms','form':f['id'],'input':q,'output':out,'expected':expected,'pass':ok,'ms':ms})
            s.request('aprende que libretema es clasea')
            for text,l,kind in FREE_PROMPTS:
                q=text.format(s='libretema');raw,ms=s.request(q,l);out=decode_result(raw);expected=answer('libretema',l,kind)
                ok=out.partition(' [')[0]==expected;free_correct+=ok
                transcript.append({'version':version,'suite':'untrained_paraphrases','input':q,'output':out,'expected':expected,'pass':ok,'ms':ms})
            compositional=clause_generalization(s,version,transcript)
            # The independent old arithmetic diagnostic is identical for all.
            for q,value in [('7 por 2',14),('8 dividido 2',4),('7 resto 2',1),('7 minimo 2',2),('7 maximo 2',7),('7 distancia 2',5)]:
                raw,ms=s.request(q);out=decode_result(raw);word={1:'uno',2:'dos',4:'cuatro',5:'cinco',7:'siete'}.get(value,str(value))
                expected=e017.conversation.ACTS[5,1]+' '+word+'.';ok=out==expected;math_correct+=ok
                transcript.append({'version':version,'suite':'E020_six_operations','input':q,'output':out,'expected':expected,'pass':ok,'ms':ms})
            common_times=[];common_correct=0
            common=[('hola',e017.conversation.ACTS[1,1]),('gato es mamífero?','Un gato es un mamífero.'),
                    ('dos mas tres',e017.conversation.ACTS[5,1]+' cinco.'),('ocho menos tres',e017.conversation.ACTS[5,1]+' cinco.')]
            for _ in range(8):
                for q,expected in common:
                    raw,ms=s.request(q);out=decode_result(raw);common_correct+=out==expected;common_times.append(ms)
            assert common_correct==32,(version,common_correct)
            metrics=s.metrics()
        results.append({'version':version,'checkpoint_sha256':hashlib.sha256(seed).hexdigest(),'checkpoint_bytes':len(seed),
            'constructions':mem.get(U+10,0)+(mem.get(L+4,0) if mem.get(L+3,0)==1 else 0),
            'lexical_registry_entries':e017.u16(mem,K+4)+e017.u16(mem,U+6),
            'new_form_score':{'correct':correct,'total':128},'untrained_paraphrase_score':{'correct':free_correct,'total':len(FREE_PROMPTS)},
            'compositional_clause_exam':compositional,'E020_operation_score':{'correct':math_correct,'total':6},'new_form_ms':percentiles(times),'shared_32_score':{'correct':common_correct,'total':32},'shared_32_query_ms':percentiles(common_times),'metrics':metrics})
        print('E021_COMPARISON',version,'LANGUAGE',correct,'/128','UNTRAINED',free_correct,'/16','NEW_CLAUSES',compositional['unseen_questions']['correct'],'/12',flush=True)
    assert results[-1]['new_form_score']['correct']==128,results[-1]
    assert results[-1]['E020_operation_score']['correct']==6
    assert results[-1]['compositional_clause_exam']['unseen_questions']['correct']==12
    assert results[-1]['compositional_clause_exam']['abstention_controls']['correct']==12
    e.state.write_bytes(learned)
    return {'scope':'128 taught-frame probes with novel entities/predicate; 16 development paraphrases; independent 12 unseen question preambles and 12 abstention controls; not general intelligence',
            'method':'same native owner runtime, source, input, setup and examiner oracle; only learned checkpoint varies; optional unsolicited proof ignored for non-explanation answers',
            'versions':results,'transcript':transcript}


def main():
    p=argparse.ArgumentParser();p.add_argument('runtime');p.add_argument('session_binary');p.add_argument('unsealed');p.add_argument('training')
    p.add_argument('--out',default='evidence/e021');p.add_argument('--smoke',action='store_true');p.add_argument('--dialogs',type=int,default=8)
    a=p.parse_args();out=Path(a.out).resolve();out.mkdir(parents=True,exist_ok=True)
    parent=out/'parent.rvp';parent.write_bytes(gzip.decompress(base64.b64decode((REPO/'ai/checkpoints/BBYQ_E020_Million_Arithmetic_ES_EN.rvp.gz.b64').read_bytes())))
    e=Examiner(a.runtime,parent,out);binary=Path(a.session_binary).resolve()
    unsealed=Path(a.unsealed).read_bytes();e.state.write_bytes(unsealed);training=json.loads(Path(a.training).read_text())
    # A partial pilot may be used only for smoke/debugging, never publication.
    if not a.smoke:assert training['training_examples']==2119224 and training['limit_per_construction'] is None
    e.run((ROOT/'seal.xi').read_text());learned=e.state.read_bytes();(out/CHECKPOINT).write_bytes(learned)
    e017.audit(e);e.run((ROOT/'audit.xi').read_text())
    report={'language_transfer':text_transfer(e,binary,learned,a.dialogs),'topic_integrity':topic_and_integrity(e,binary,learned)}
    if a.smoke:return
    training_controls(e,binary,learned,unsealed)
    compare=comparisons(e,binary,learned)
    report['e019_regression']=e019.novel_dialogues(e,binary,learned,4)
    report['e018_regression']=e018.novel_dialogues(e,binary,learned,20)
    e018.controls(e,binary,learned);e018.interfaces_and_rollback(e,binary,learned);e018.retention(e,binary,learned)
    spec=importlib.util.spec_from_file_location('e020',ROOT.parent/'scale/tests/native-e020.py')
    e020=importlib.util.module_from_spec(spec);spec.loader.exec_module(e020)
    report['e020_arithmetic_regression']=e020.independent_text_exam(e,binary,learned)
    before_controls=e.checks
    e019.controls(e,binary,learned);e019.restart_and_reset(e,binary,learned)
    report['e019_additional_controls']={'checks':e.checks-before_controls,'context_and_bad_lessons':True,'restart_reset':True}
    e.state.write_bytes(learned);e017.audit(e);e.run((ROOT.parent/'scale/audit.xi').read_text());raw=e.run((ROOT/'audit.xi').read_text())
    stats=[json.loads(x) for x in raw.splitlines() if x.startswith('{')]
    report.update({'stage':'E021','parent_sha256':lang.PARENT_SHA,'checkpoint_sha256':hashlib.sha256(learned).hexdigest(),
        'checkpoint_bytes':len(learned),'training':training,'checks':e.checks,'comparison':{x['version']:x['new_form_score'] for x in compare['versions']},
        'new_world_facts_in_release':0,'new_constructions':128,'total_constructions':224,'topic_slots':8,'new_dialogue_acts':8,
        'previous_learned_records_preserved':True,'runtime_commit':'6d4de14a2dfbce4b8a7f1cb50e29d11b9073fe98',
        'mundo_x_commit':'e2778d962af22f6f1a0794058dd4685fc2573966','memory_stats':stats,
        'open_conversation_achieved':False,'limits':{'input_bytes':255,'tokens':15,'topic_slots':8,'search_nodes':64,'proof_nodes':32,'answers':8},
        'intelligence':'XI; original synthetic supervision, no external pretrained model; C++ runtime and Python examiner are infrastructure'})
    for name,data in [('results.json',report),('comparisons.json',compare)]:
        (out/name).write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')
    (out/'raw.jsonl').write_text(''.join(json.dumps(x,ensure_ascii=False)+'\n' for x in e.transcript))
    e.state.write_bytes(learned)
    print(json.dumps(report,ensure_ascii=False,indent=2),flush=True)


if __name__=='__main__':main()
