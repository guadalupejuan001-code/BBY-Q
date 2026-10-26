#!/usr/bin/env python3
"""Continue the authentic E015 learner. Python teaches and independently exams;
only bytes and language enter the XI conversation program during inference.
"""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import random
import shutil
import statistics
import subprocess
import sys
import time

ROOT=Path(__file__).resolve().parents[1]
REPO=ROOT.parents[2]
C=7700000000000000000
PARENT_SHA='b32e95d54b866230adfa020d4c706e36d25a4b1ceb66ede7e63b795fd03dd0b1'
spec=importlib.util.spec_from_file_location('grammar',ROOT.parent/'grammar/tests/native-grammar.py')
grammar=importlib.util.module_from_spec(spec);spec.loader.exec_module(grammar)
stories=grammar.stories
snapshot,frame,stores=grammar.snapshot,grammar.frame,grammar.stores
Session,decode_result=grammar.Session,grammar.decode_result
K,D,W=grammar.K,stories.D,grammar.W


def rows(name):
    return [line.split('|') for line in (ROOT/'data'/name).read_text().splitlines()
            if line and not line.startswith('#')]


def immutable(path):
    core,memory,bindings=stories.immutable(path)
    return core,{a:b for a,b in memory.items() if not C+4<=a<C+16 and not D<=a<D+16},bindings


class Examiner(stories.Examiner):
    def __init__(self,runtime,parent,out):
        self.runtime=str(Path(runtime).resolve());self.parent=Path(parent).resolve()
        assert hashlib.sha256(self.parent.read_bytes()).hexdigest()==PARENT_SHA
        self.original=snapshot(self.parent)
        self.out=Path(out).resolve();self.out.mkdir(parents=True,exist_ok=True)
        self.state,self.next=self.out/'state.rvp',self.out/'next.rvp'
        self.event=self.out/'event.xi';self.state.write_bytes(self.parent.read_bytes())
        self.programs={m:subprocess.check_output(['bash',str(ROOT.parent/'knowledge/link.sh'),m],text=True).split('\n',1)[1]
                       for m in ['word','utterance','config','role','nominal','order','combined','conversation']}
        self.word_program=self.programs['word'];self.combined=self.programs['conversation']
        self.program=self.out/'conversation.xi';self.program.write_text('#!reverse-pc-machine-v1\n'+self.combined)
        self.compact=self.out/'compact.xi';self.compact.write_text('#!reverse-pc-machine-v1\n'+self.programs['combined'])
        self.transcript,self.times,self.checks=[],[],0

    def teach(self,mode,fields,text='',language=1,reject=False):
        self.run(frame(text,language)+stores(fields).split('\n',1)[1]+self.programs[mode],reject=reject)

    def utterance(self,act,language,text,reject=False):
        self.teach('utterance',[(C+16,1),(C+17,act)],text,language,reject)

    def order(self,language,actor,item,verb,quantity,text,reject=False):
        self.teach('order',[(C+16,2),(C+17,actor),(C+18,item),(C+19,verb),(C+20,quantity)],text,language,reject)

    def nominal(self,noun,mode,language,text,reject=False):
        self.teach('nominal',[(C+16,3),(C+17,noun),(C+18,mode)],text,language,reject)

    def check(self,text,expected,language=1,session=None,reference=None,ledger=None):
        before=immutable(self.state)
        if session:
            raw,elapsed=session.request(text,language)
        else:
            started=time.perf_counter_ns();raw=self.run(frame(text,language)+self.combined)
            elapsed=(time.perf_counter_ns()-started)/1e6
        spoken=decode_result(raw)
        assert spoken==expected,(text,spoken,expected)
        core,memory,bindings=snapshot(self.state)
        assert core==self.original[0] and bindings==self.original[2]
        assert not any(memory.get(C+i,0) for i in range(16,256))
        assert not any(memory.get(K+i,0) for i in [*range(16,2048),*range(3000,4500)])
        assert not any(memory.get(W+i,0) for i in [*range(16,64),*range(2000,2216)])
        assert immutable(self.state)==(reference if reference is not None else before),'inference changed learned state'
        if ledger is not None:assert stories.ledger(memory)==ledger,(text,stories.ledger(memory),ledger)
        self.transcript.append({'input':text if isinstance(text,str) else repr(text),'language':language,'output':spoken,'ms':elapsed,
                                'topic':memory.get(C+10,0),'actor':memory.get(C+5,0),'item':memory.get(C+6,0)})
        self.times.append(elapsed);self.checks+=1
        return memory


def train(e):
    e.run((ROOT/'birth.xi').read_text())
    for cid,kind,language,text in rows('words-v1.psv'):
        e.word(int(cid),int(kind),int(language),text)
    for role,cid in rows('functions-v1.psv'):
        e.teach('config',[(C+16,5),(C+17,int(role)),(C+18,int(cid))])
    for cid,kind,gender in rows('roles-v1.psv'):
        e.teach('role',[(C+16,4),(C+17,int(cid)),(C+18,int(kind)),(C+19,int(gender))])
    for act,language,text in rows('utterances-v1.psv'):
        e.utterance(int(act),int(language),text)
    for noun,mode,language,text in rows('nominals-v1.psv'):
        e.nominal(int(noun),int(mode),int(language),text)
    for language,actor,item,verb,num,text in rows('orders-v1.psv'):
        e.order(*map(int,(language,actor,item,verb,num)),text)
    # Restore the authentic parent's display descriptors and publish no exam
    # accounts or conversation references as lessons.
    old=e.original[1]
    fields=[(K+3,old.get(K+3,0))]+[(C+i,0) for i in range(4,16)]
    e.run(stores(fields))
    return e.state.read_bytes()


PEOPLE=[('ana',204,2),('luis',205,1),('eva',206,2),('tom',207,1)]
ITEMS=[(208,'manzana','manzanas','apple','apples','una'),
       (209,'pera','peras','pear','pears','una'),
       (210,'libro','libros','book','books','un'),
       (211,'pelota','pelotas','ball','balls','una')]
ACTS={(int(a),int(l)):t for a,l,t in rows('utterances-v1.psv')}


def sentence(person,item,quantity,language):
    _,es,esp,en,enp,one=item
    noun=(es if quantity==1 else esp) if language==1 else (en if quantity==1 else enp)
    num=one if quantity==1 and language==1 else stories.number(quantity,language)
    return f'{person.capitalize()} {"tiene" if language==1 else "has"} {num} {noun}.'


def factual_answer(compact,language):
    """Independent realization oracle from the old semantic examiner, not input
    to XI. Learned surface forms are test data; facts still come from E012.
    """
    negative=compact.startswith('no: ')
    if negative:compact=compact[4:]
    body,sep,proof=compact.partition(' [')
    articles={}
    for _,mode,lang,text in rows('nominals-v1.psv'):
        if mode=='3' and int(lang)==language:
            article,noun=text.split(' ',1);articles[noun]=article
    result=[]
    for triple in body.removesuffix('.').split('; '):
        subject,predicate,obj=triple.split()
        if predicate==('es' if language==1 else 'is'):
            subject=(articles[subject]+' '+subject) if subject in articles else subject
            obj=(articles[obj]+' '+obj) if obj in articles else obj
        result.append(f'{subject} {predicate} {obj}'.replace('_',' '))
    text='; '.join(result)+'.'
    if negative:text=ACTS[7,language]+' '+text
    else:text=text[0].upper()+text[1:]
    if sep:text+=' ['+proof.replace('_',' ')
    return text


def audit(e):
    e.audit()
    e.run((ROOT.parent/'grammar/audit.xi').read_text())
    before=e.state.read_bytes();e.run((ROOT/'audit.xi').read_text());assert e.state.read_bytes()==before


def learning_controls(e,binary,learned):
    e.state.write_bytes(learned)
    e.utterance(3,1,'a contradictory replacement',reject=True)
    e.teach('config',[(C+16,5),(C+17,1),(C+18,221)],reject=True)
    e.nominal(210,2,1,'tres libro',reject=True)
    e.order(1,204,208,24,14,'tiene ana una manzana',reject=True)
    e.order(1,204,208,24,14,'ana tiene una ana',reject=True)
    # Repeated evidence, or varying only a subset of referents, is insufficient.
    e.run(stores([(C+1000+i,0) for i in range(32)]))
    for _ in range(5):e.order(1,204,208,24,14,'ana tiene una manzana')
    e.order(1,205,208,24,16,'luis tiene tres manzanas')
    assert snapshot(e.state)[1][C+1001]==1
    with Session(binary,e.state,e.program) as session:
        e.check('eva tiene siete libros',ACTS[6,1]+' siete.',session=session)
    e.order(1,205,209,24,16,'luis tiene tres peras')
    assert snapshot(e.state)[1][C+1001]==2
    e.state.write_bytes(learned)
    # Same XI, different demonstrated ordering -> different composed sentence.
    e.run(stores([(C+1000+i,0) for i in range(32)]))
    e.order(1,204,208,24,14,'tiene ana una manzana')
    e.order(1,205,209,24,16,'tiene luis tres peras')
    with Session(binary,e.state,e.program) as session:
        e.check('eva tiene siete libros','Tiene Eva siete libros.',session=session)
    e.state.write_bytes(learned)
    # Plural forms require two distinct quantities; repetition cannot add it.
    mask=C+100000+210*224+101
    e.run(stores([(mask,0)]))
    e.nominal(210,2,1,'dos libros');e.nominal(210,2,1,'dos libros')
    assert snapshot(e.state)[1][mask]==1
    with Session(binary,e.state,e.program) as session:
        e.check('eva tiene siete libros',ACTS[6,1]+' siete.',session=session)
    e.nominal(210,2,1,'tres libros')
    assert snapshot(e.state)[1][mask]==3
    with Session(binary,e.state,e.program) as session:
        e.check('cuántos libros tiene eva?',sentence('eva',ITEMS[2],7,1),session=session)
    e.state.write_bytes(learned)
    # Read-only audit detects corrupt learned structure.
    e.run(stores([(C+1008,9)]));e.run((ROOT/'audit.xi').read_text(),reject=True)
    e.state.write_bytes(learned)
    print('DISTINCT_EVIDENCE_REVERSED_ORDER_AND_INFLECTION_CONTROLS_PASS',flush=True)


def interfaces(e,binary,learned,reference):
    e.state.write_bytes(learned)
    with Session(binary,e.state,e.program) as session:
        e.check('ana tiene cinco manzanas',sentence('ana',ITEMS[0],5,1),session=session,reference=reference)
        e.check('qué es una neurona?',factual_answer('neurona es célula.',1),session=session,reference=reference)
    e.run((ROOT.parent/'stories/reset-episode.xi').read_text())
    memory=snapshot(e.state)[1]
    assert not stories.ledger(memory) and not any(memory.get(C+i,0) for i in range(4,16))
    assert immutable(e.state)==reference
    with Session(binary,e.state,e.program) as session:
        e.check('¿y las peras?',ACTS[4,1],session=session,reference=reference)
    e.state.write_bytes(learned)
    fixture=e.out/'cache-fixture';shutil.copytree(REPO/'ai/xi',fixture/'xi')
    state=fixture/'state.rvp';state.write_bytes(learned)
    cli=['bash',str(fixture/'xi/knowledge/text.sh'),e.runtime,str(state)]
    assert subprocess.check_output(cli+['ana tiene dos manzanas','es'],text=True)=='Ana tiene dos manzanas.\n'
    assert subprocess.check_output(cli+['cuántas manzanas tiene ana?','es','--compact'],text=True)=='dos\n'
    assert len(list((fixture/'.bbyq-xi-cache').glob('*.xi')))==2
    emitter=fixture/'xi/conversation/emit.xi'
    emitter.write_text(emitter.read_text().replace('label done\n','label done\nset r14 33\nprint r14\n',1))
    assert subprocess.check_output(cli+['ana tiene dos manzanas','es'],text=True)=='Ana! tiene! dos! manzanas!.\n'
    assert len(list((fixture/'.bbyq-xi-cache').glob('*.xi')))==3
    # Public resident client defaults to speech and can request the old API.
    client=[sys.executable,str(REPO/'ai/native/session_client.py'),str(binary),str(state)]
    assert subprocess.check_output(client,input='cuántas manzanas tiene ana?\n',text=True)=='Ana tiene dos manzanas.\n'
    assert subprocess.check_output(client+['--compact'],input='cuántas manzanas tiene ana?\n',text=True)=='dos\n'
    # Old authentic E015 state on the new default client keeps old exact output.
    old_state=e.out/'old-model.rvp';old_state.write_bytes(e.parent.read_bytes())
    old_client=[sys.executable,str(REPO/'ai/native/session_client.py'),str(binary),str(old_state)]
    assert subprocess.check_output(old_client,input='dos mas tres\n',text=True)=='cinco\n'
    assert not any(C<=a<C+160000 for a in snapshot(old_state)[1])
    e.state.write_bytes(learned)
    print('EPISODE_RESET_PUBLIC_CLIENTS_COMPACT_AND_SOURCE_CACHE_PASS',flush=True)


def transaction_controls(e,binary,learned,reference):
    e.state.write_bytes(learned)
    with Session(binary,e.state,e.program) as session:
        e.check('ana tiene cinco manzanas',sentence('ana',ITEMS[0],5,1),session=session,reference=reference)
        pending=Path(str(e.state)+'.pending');pending.mkdir();before=e.state.read_bytes()
        try:
            try:session.request('luis tiene tres peras');raise AssertionError('save failure acknowledged')
            except RuntimeError as error:assert 'cannot write state' in str(error),error
            assert e.state.read_bytes()==before
        finally:pending.rmdir()
        e.check('ella recibe una manzana',sentence('ana',ITEMS[0],6,1),session=session,reference=reference,
                ledger={(204,208):6})
    e.state.write_bytes(learned)
    with Session(binary,e.state,e.program) as session:
        e.check('ana tiene cinco manzanas',sentence('ana',ITEMS[0],5,1),session=session,reference=reference)
    body=e.program.read_text();end='\nlabel finish\nhalt\n';assert body.count(end)==1
    failure=e.out/'failure-after-context.xi'
    failure.write_text(body.replace(end,f'\nlabel finish\nload8 r0 {C+5}\ncmp r0 205\njne finish_ok\ndiv r0 0\nlabel finish_ok\nhalt\n'))
    with Session(binary,e.state,failure) as session:
        before=e.state.read_bytes()
        try:session.request('luis tiene tres peras');raise AssertionError('post-update XI failure acknowledged')
        except RuntimeError:pass
        assert e.state.read_bytes()==before
        e.check('how many does she have?',sentence('ana',ITEMS[0],5,2),2,session=session,reference=reference,
                ledger={(204,208):5})
    e.state.write_bytes(learned)
    print('SAVE_AND_POST_UPDATE_CONTEXT_ROLLBACK_PASS',flush=True)


def full_exam(e,binary,learned,reference,dialogs):
    rng=random.Random(160627);dialogue_turns=0;heldout_times=[]
    # Frame teaching used Ana/Luis and apples/pears. Compositional dialogues use
    # Eva/Tom and books/balls. Lexical morphology is taught separately for all.
    for i in range(dialogs):
        e.state.write_bytes(learned)
        person,aid,gender=PEOPLE[2+i%2];other,oid,_=PEOPLE[3-i%2]
        item=ITEMS[2+(i//2)%2];second=ITEMS[3-(i//2)%2]
        amount=rng.randint(1,60000);gain=rng.randint(1,100);other_amount=rng.randint(1,60000)
        language=1+i%2;pronoun=('ella' if gender==2 else 'él') if language==1 else ('she' if gender==2 else 'he')
        with Session(binary,e.state,e.program) as session:
            e.check('hola' if language==1 else 'hello',ACTS[1,language],language,session=session,reference=reference)
            e.check(f'{person} tiene {amount} {item[2]}',sentence(person,item,amount,language),language,session=session,reference=reference)
            text=f'{pronoun} recibe {gain} más' if language==1 else f'{pronoun} receives {gain} more'
            e.check(text,sentence(person,item,amount+gain,language),language,session=session,reference=reference)
            heldout_times.append(e.times[-1])
        # Restart with a stored discourse referent before resolving a pronoun.
        with Session(binary,e.state,e.program) as session:
            q='¿cuántas tiene ella?' if gender==2 else 'how many does he have?'
            e.check(q,sentence(person,item,amount+gain,3-language),3-language,session=session,reference=reference)
            e.check(f'{other} tiene {other_amount} {item[2]}',sentence(other,item,other_amount,1),session=session,reference=reference)
            e.check('¿y '+person+'?',sentence(person,item,amount+gain,1),session=session,reference=reference)
            e.check(f'{person} tiene una {second[1]}',sentence(person,second,1,1),session=session,reference=reference)
            e.check('and the '+item[4]+'?',sentence(person,item,amount+gain,2),2,session=session,reference=reference)
            assert stories.ledger(snapshot(e.state)[1])=={(aid,item[0]):amount+gain,(oid,item[0]):other_amount,(aid,second[0]):1}
        dialogue_turns+=8
        if i%30==0:print('NOVEL_DIALOGUE_PROGRESS',i+1,flush=True)
    e.state.write_bytes(learned)
    print('COMPOSITIONAL_DIALOGUES_AND_CONTEXT_RESTART_PASS',dialogs,dialogue_turns,flush=True)

    # Singular/plural and quantities around boundaries, not response examples.
    quantity_cases=0
    with Session(binary,e.state,e.program) as session:
        for item in ITEMS:
            for person,aid,_ in PEOPLE:
                for amount in (0,1,2,9,10,65535):
                    for language in (1,2):
                        e.check(f'{person} tiene {amount} {item[2]}.',sentence(person,item,amount,language),language,
                                session=session,reference=reference)
                        q=f'cuántas {item[2]} tiene {person}?' if language==1 else f'how many {item[4]} does {person} have?'
                        e.check(q,sentence(person,item,amount,language),language,session=session,reference=reference)
                        quantity_cases+=2
        before=stories.ledger(snapshot(e.state)[1]);assert len(before)==16
        e.check('gato tiene tres roca',ACTS[3,1],session=session,reference=reference,ledger=before)
        e.check('ana tiene 65535 manzanas y recibe una manzana',ACTS[3,1],session=session,reference=reference,ledger=before)
    e.state.write_bytes(learned)
    print('INFLECTION_BOUNDARIES_AND_16_ACCOUNTS_PASS',quantity_cases,flush=True)

    # Polished factual realization of the old examiner's exact semantic oracle.
    old_cases=stories.retained_curriculum();assert len(old_cases)==1522
    with Session(binary,e.state,e.program) as session:
        for text,answer,language in old_cases:
            e.check(text,factual_answer(answer,language),language,session=session,reference=reference)
        examples=[('háblame de un gato',factual_answer('gato es mamífero.',1),1),
                  ('tell me about a neuron',factual_answer('neuron is cell.',2),2)]
        for text,answer,language in examples:e.check(text,answer,language,session=session,reference=reference)
        e.check('¿y un perro?',factual_answer('perro es mamífero.',1),session=session,reference=reference)
        e.check('¿cómo estás?',ACTS[8,1],session=session,reference=reference)
        e.check('how are you?',ACTS[8,2],2,session=session,reference=reference)
        e.check('what is your name?',ACTS[2,2],2,session=session,reference=reference)
        e.check('qué sabes?',ACTS[2,1],session=session,reference=reference)
        e.check('un más dos',ACTS[5,1]+' tres.',session=session,reference=reference)
    e.state.write_bytes(learned)
    # Compact API preserves all prior exact outputs on the NEW learned model.
    with Session(binary,e.state,e.compact) as session:
        for text,answer,language in old_cases:
            e.check(text,answer,language,session=session,reference=reference)
    e.state.write_bytes(learned)
    print('ALL_1522_FACTUAL_CONVERSATIONAL_AND_COMPACT_RETENTION_PASS',flush=True)

    # Each failure starts from the same valid quantity context, so a previous
    # failure's explicit context invalidation cannot mask a later error.
    failures=[('how many books does he have?',4),('ella tiene dos manzanas??',3),
              ('ella recibe tres más?',3),('ella no recibe dos',3),
              ('ana recibe dos manzanas y ella recibe una manzana',4),
              ('what is a unicorn?',3),('cuántas tiene desconocido?',3),
              ('y unicornio?',3),('how many books does she not have?',3),
              ('she receives 65536 more',3),('tiene dos más',3),
              ('ana tiene dos más',3),('how many books does eva have extra?',3),
              (b'how many books does eva have\xc3',3),('gato es animal??',3)]
    for text,act in failures:
        e.state.write_bytes(learned)
        with Session(binary,e.state,e.program) as session:
            e.check('eva tiene cinco libros',sentence('eva',ITEMS[2],5,1),session=session,reference=reference)
            e.check(text,ACTS[act,1],session=session,reference=reference,ledger={(206,210):5})
    e.state.write_bytes(learned)
    with Session(binary,e.state,e.program) as session:
        for text in ['ella recibe dos más','¿y las peras?','¿cuántas tiene?']:
            e.check(text,ACTS[4,1],session=session,reference=reference,ledger={})
        e.check('gato es mamífero?',factual_answer('gato es mamífero.',1),session=session,reference=reference)
        e.check('ella recibe dos más',ACTS[4,1],session=session,reference=reference,ledger={})
        e.check('ana tiene cinco manzanas',sentence('ana',ITEMS[0],5,1),session=session,reference=reference)
        e.check('luis recibe tres peras',ACTS[3,1],session=session,reference=reference,ledger={(204,208):5})
        e.check('ella recibe dos más',ACTS[4,1],session=session,reference=reference,ledger={(204,208):5})
    e.state.write_bytes(learned)
    print('UNKNOWN_AMBIGUOUS_PRONOUNS_AND_QUESTION_SAFETY_PASS',flush=True)
    return {'dialogs':dialogs,'dialogue_turns':dialogue_turns,'quantity_cases':quantity_cases,
            'factual_conversational_cases':len(old_cases),'compact_retention_cases':len(old_cases),
            'failure_controls':len(failures),'dialogue_action_ms':{
                'median':statistics.median(heldout_times),'p95':sorted(heldout_times)[max(0,(len(heldout_times)*95+99)//100-1)]}}


def main():
    ap=argparse.ArgumentParser();ap.add_argument('runtime');ap.add_argument('session_binary');ap.add_argument('parent')
    ap.add_argument('--out',default='evidence/e016');ap.add_argument('--dialogs',type=int,default=120)
    ap.add_argument('--smoke',action='store_true');args=ap.parse_args()
    e=Examiner(args.runtime,args.parent,args.out);binary=Path(args.session_binary).resolve()
    started=time.perf_counter();learned=train(e);training_seconds=time.perf_counter()-started;reference=immutable(e.state)
    release=e.out/'BBYQ_E016_Conversation_ES_EN.rvp';release.write_bytes(learned)
    assert not stories.ledger(snapshot(e.state)[1])
    with Session(binary,e.state,e.program) as session:
        for text,expected,language in [
            ('hola','Hola. Soy BBY Q.',1),
            ('who are you?','I am BBY Q. I can answer from learned knowledge and track simple quantities.',2),
            ('ana tiene dos manzanas.','Ana tiene dos manzanas.',1),
            ('ella recibe tres más','Ana tiene cinco manzanas.',1),
            ('how many apples does she have?','Ana has five apples.',2),
            ('ana tiene una pera','Ana tiene una pera.',1),
            ('¿y las manzanas?','Ana tiene cinco manzanas.',1),
            ('what is a cat?','A cat is a mammal.',2),
            ('¿y un perro?','Un perro es un mamífero.',1),
            ('qué es una neurona?','Una neurona es una célula.',1),
            ('dos mas tres','El resultado es cinco.',1),
            ('minus one','The result is four.',2),
        ]:
            e.check(text,expected,language,session=session,reference=reference)
            print('CONVERSATION_PASS',text,'->',expected,flush=True)
    e.state.write_bytes(learned)
    print('TRAINED',hashlib.sha256(learned).hexdigest(),len(learned),flush=True)
    if args.smoke:return
    # The complete parent state, core and bindings are retained; new lexical
    # entries are appended without replacing a single existing learned byte.
    core,memory,bindings=snapshot(e.state);old=e.original[1]
    old_count=stories.u16(old,K+4);new_count=stories.u16(memory,K+4)
    assert new_count==old_count+len(rows('words-v1.psv'))
    excluded={K+4,K+5}|set(range(K+10000+old_count*40,K+10000+new_count*40))|{
        K+6000+int(r[0]) for r in rows('words-v1.psv') if K+6000+int(r[0]) not in old}
    assert core==e.original[0] and bindings==e.original[2]
    assert {a:b for a,b in memory.items() if not C<=a<C+160000 and a not in excluded}=={
        a:b for a,b in old.items() if a not in excluded},'a prior learned byte was replaced'
    audit(e)
    learning_controls(e,binary,learned)
    report=full_exam(e,binary,learned,reference,args.dialogs)
    transaction_controls(e,binary,learned,reference)
    interfaces(e,binary,learned,reference)
    audit(e)
    report.update({'stage':'E016','parent_sha256':PARENT_SHA,'learned_sha256':hashlib.sha256(learned).hexdigest(),
                   'checkpoint_bytes':len(learned),'training_seconds':training_seconds,
                   'new_lexical_entries':len(rows('words-v1.psv')),'total_lexical_entries':new_count,
                   'response_order_demonstrations':len(rows('orders-v1.psv')),
                   'nominal_demonstrations':len(rows('nominals-v1.psv')),
                   'fixed_dialogue_act_lessons':len(rows('utterances-v1.psv')),
                   'programmed_function_labels':len(rows('functions-v1.psv')),
                   'supervised_entity_role_labels':len(rows('roles-v1.psv')),
                   'old_training_replayed':False,'old_knowledge_unchanged':True,
                   'saved_context_restart':True,'save_and_post_update_context_rollback':True,
                   'repeated_evidence_does_not_promote':True,'reversed_order_control':True,
                   'two_quantity_inflection_gate':True,'public_clients_default_to_speech':True,
                   'compact_protocol_preserved':True,'old_checkpoint_default_compatible':True,
                   'source_cache_covers_conversation':True,'episode_reset_clears_context':True,
                   'checks':e.checks,'intelligence':'XI only; same pinned runtime and E014 authority',
                   'platform':sys.platform,'no_reverse_os_integration':True})
    e.state.write_bytes(learned)
    (e.out/'results.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    (e.out/'raw.jsonl').write_text(''.join(json.dumps(x,ensure_ascii=False)+'\n' for x in e.transcript))
    print(json.dumps(report,ensure_ascii=False,indent=2),flush=True)


if __name__=='__main__':main()
