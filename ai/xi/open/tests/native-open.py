#!/usr/bin/env python3
"""Train the E017 extension on the authentic E016 checkpoint and examine it.

The examiner supplies labeled demonstrations and independent expected results.
Only text and language enter the agent's resident native inference process.
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
U=7800000000000000000
PARENT_SHA='55992a06df9ec9cad6889f3dabbdbc179d2626cfd32667efec1f74b78660e732'
spec=importlib.util.spec_from_file_location('conversation',ROOT.parent/'conversation/tests/native-conversation.py')
conversation=importlib.util.module_from_spec(spec);spec.loader.exec_module(conversation)
stories=conversation.stories
snapshot,frame,stores=conversation.snapshot,conversation.frame,conversation.stores
Session,decode_result=conversation.Session,conversation.decode_result
K,C,D,W=conversation.K,conversation.C,conversation.D,conversation.W


def rows(name):
    return [line.split('|') for line in (ROOT/'data'/name).read_text().splitlines() if line and not line.startswith('#')]


def wide(address,value):return [(address,value%256),(address+1,value//256)]
def u16(memory,address):return memory.get(address,0)+256*memory.get(address+1,0)


def lexicon(memory):
    result={}
    for i in range(u16(memory,U+6)):
        a=U+100000+i*40
        text=bytes(memory.get(a+5+j,0) for j in range(memory.get(a+4,0))).decode()
        assert text not in result,('duplicate surface entry',text)
        result[text]=(u16(memory,a),memory[a+2],memory[a+3])
    return result


def immutable(path):
    core,memory,bindings=conversation.immutable(path)
    return core,{a:b for a,b in memory.items() if not (U+12<=a<U+20 or 8000000000000000128<=a<8000000000000000256)},bindings


def base_immutable(path):
    core,memory,bindings=conversation.immutable(path)
    return core,{a:b for a,b in memory.items() if not U<=a<U+2**51},bindings


SURFACE={(int(a),int(l)):t for a,l,t in rows('surface-v1.psv')}
PREFIX=SURFACE[8,1]+' '


def names(e):return {text:cid for text,(cid,_,_) in lexicon(snapshot(e.state)[1]).items()}


def audit(e):
    for path in ['ai/xi/e008/audit-organism.xi','ai/xi/language/audit.xi','ai/xi/school/audit.xi',
                 'ai/xi/dialogue/audit.xi','ai/xi/knowledge/audit.xi','ai/xi/stories/audit.xi',
                 'ai/xi/grammar/audit.xi','ai/xi/conversation/audit.xi','ai/xi/open/audit.xi']:
        before=e.state.read_bytes();e.run((REPO/path).read_text());assert e.state.read_bytes()==before
    lexicon(snapshot(e.state)[1])


class Examiner(stories.Examiner):
    def __init__(self,runtime,parent,out,*,expected_parent=PARENT_SHA):
        self.runtime=str(Path(runtime).resolve());self.parent=Path(parent).resolve()
        assert hashlib.sha256(self.parent.read_bytes()).hexdigest()==expected_parent
        self.original=snapshot(self.parent);self.out=Path(out).resolve();self.out.mkdir(parents=True,exist_ok=True)
        self.state,self.next=self.out/'state.rvp',self.out/'next.rvp';self.event=self.out/'event.xi'
        self.state.write_bytes(self.parent.read_bytes());self.checks=0;self.times=[];self.transcript=[]
        self.programs={m:subprocess.check_output(['bash',str(ROOT.parent/'knowledge/link.sh'),m],text=True).split('\n',1)[1]
                       for m in ['open-word','open-pattern','open-utterance','open-calibrate','open-base','conversation','combined']}
        self.program=self.out/'conversation.xi';self.program.write_text('#!reverse-pc-machine-v1\n'+self.programs['conversation'])
        self.compact=self.out/'compact.xi';self.compact.write_text('#!reverse-pc-machine-v1\n'+self.programs['combined'])

    def teach(self,mode,fields,text='',language=1,reject=False):
        self.run(frame(text,language)+stores(fields).split('\n',1)[1]+self.programs[mode],reject=reject)

    def word(self,cid,kind,language,text,reject=False):
        self.teach('open-word',wide(U+160,cid)+[(U+162,kind),(U+163,language),(U+164,0)],text,language,reject)

    def pattern(self,pid,intent,s,p,o,alias,language,text,reject=False):
        self.teach('open-pattern',[(U+176,pid),(U+177,intent),(U+178,alias)]+wide(U+180,s)+wide(U+182,p)+wide(U+184,o),text,language,reject)

    def calibrate(self,p,s,a,o,reject=False):
        self.teach('open-calibrate',wide(U+280,p)+wide(U+282,s)+wide(U+284,a)+wide(U+286,o),reject=reject)

    def check(self,text,expected,language=1,session=None,readonly=True):
        before=immutable(self.state)
        before_ledger=stories.ledger(snapshot(self.state)[1])
        if session:raw,elapsed=session.request(text,language)
        else:
            started=time.perf_counter_ns();raw=self.run(frame(text,language)+self.programs['conversation'])
            elapsed=(time.perf_counter_ns()-started)/1e6
        spoken=decode_result(raw)
        assert spoken==expected,(text,spoken,expected)
        core,memory,bindings=snapshot(self.state)
        assert core==self.original[0] and bindings==self.original[2]
        assert base_immutable(self.state)==base_immutable(self.parent),'earlier learned bytes changed'
        if readonly:
            assert immutable(self.state)==before,'a query changed learned knowledge'
            assert stories.ledger(memory)==before_ledger,'a question changed episode accounts'
        assert not any(memory.get(U+i,0) for i in [*range(63,512),*range(1024,1084),*range(2048,2108)])
        assert not any(U+8000000<=a<U+8400000 for a in memory),'reasoning scratch leaked'
        assert not any(memory.get(C+i,0) for i in range(16,256))
        self.transcript.append({'input':text,'language':language,'output':spoken,'ms':elapsed})
        self.times.append(elapsed);self.checks+=1
        return memory

    def lesson(self,text,language=1,session=None):
        ledger=stories.ledger(snapshot(self.state)[1])
        result=self.check(text,SURFACE[1,language],language,session=session,readonly=False)
        assert stories.ledger(result)==ledger
        return result


def train(e,binary):
    started=time.perf_counter()
    e.run((ROOT/'birth.xi').read_text())
    for cid,kind,language,text in rows('lexicon-v1.psv'):e.word(int(cid),int(kind),int(language),text)
    for act,language,text in rows('surface-v1.psv'):
        e.teach('open-utterance',[(U+304,int(act))],text,int(language))
    for predicate,text in rows('bases-v1.psv'):
        e.teach('open-base',wide(U+312,int(predicate)),text,2)
    for pid,intent,s,p,o,alias,language,text in rows('constructions-v1.psv'):
        e.pattern(*map(int,(pid,intent,s,p,o,alias,language)),text)
    m=snapshot(e.state)[1]
    count=max(int(r[0]) for r in rows('constructions-v1.psv'))
    assert m[U+10]==count
    for i in range(count):assert m.get(U+10000+i*96+2,0)==1,('pattern not enabled',i+1)
    print('LEARNED_CONSTRUCTIONS_PASS',count,flush=True)
    with Session(binary,e.state,e.program) as session:
        for (text,) in rows('reasoning-v1.psv'):
            e.lesson(text,session=session)
    words=lexicon(snapshot(e.state)[1])
    for p,s,a,o in [(264,'dida','clasea','agua'),(264,'dibe','claseb','energía'),
                    (265,'rutauno','rutados','rutatres'),(265,'pasosuno','pasosdos','pasostres')]:
        ids={name:words[name][0] for name in words}
        ids.update({'agua':110,'energía':114})
        e.calibrate(p,ids[s],ids[a],ids[o])
    # Restore every parent display/context byte. Publish no examination input,
    # new test facts, aliases or conversation references as the released model.
    old=e.original[1]
    fields=[(K+3,old.get(K+3,0))]+[(a,old.get(a,0)) for a in [*range(K+8,K+16),*range(K+2100,K+2108),*range(K+2200,K+2232),*range(C+4,C+16)]]
    fields += [(U+i,0) for i in range(12,20)]
    e.run(stores(fields))
    return e.state.read_bytes(),time.perf_counter()-started


def learning_controls(e,binary,learned):
    e.state.write_bytes(learned)
    # Duplicate and insufficiently varied syntax demonstrations do not promote.
    # Record 12 is the teaching construction: erase only this experimental copy.
    a=U+10000+11*96;e.run(stores([(a+i,0) for i in range(96)]))
    for _ in range(5):e.pattern(12,3,5,23,40,0,1,'aprende que gato es mamífero')
    assert not snapshot(e.state)[1].get(a+2,0)
    with Session(binary,e.state,e.program) as session:
        e.check('aprende que novato es mamífero',conversation.ACTS[3,1],session=session)
    assert 'novato' not in names(e)
    e.pattern(12,3,110,25,114,0,2,'learn that water needs energy')
    assert snapshot(e.state)[1][a+2]==1
    # A literal "is" in a prefix is not the predicate variable. Both examples
    # are needed to resolve the ambiguous masks, even with two copies of "is".
    e.state.write_bytes(learned);a=U+10000+24*96
    e.run(stores([(a+i,0) for i in range(96)]))
    e.pattern(25,2,5,23,40,0,1,'es cierto que gato es mamífero')
    assert not snapshot(e.state)[1].get(a+2,0)
    e.pattern(25,2,110,25,114,0,1,'es cierto que agua necesita energía')
    m=snapshot(e.state)[1]
    assert m[a+2]==1 and m[a+16]==16 and m[a+16+4*4]==2
    # A conflicting lesson cannot silently overwrite a learned construction.
    e.pattern(25,2,110,25,114,0,1,'gato es cierto que agua necesita energía',reject=True)
    e.state.write_bytes(learned)
    e.word(5,1,1,'perro',reject=True)
    e.teach('open-utterance',[(U+304,1)],'a conflicting surface',reject=True)
    print('DISTINCT_SYNTAX_LITERAL_DISAMBIGUATION_AND_BAD_LESSONS_PASS',flush=True)


def novel_dialogues(e,binary,learned,cases):
    e.state.write_bytes(learned);timings=[]
    with Session(binary,e.state,e.program) as session:
        for i in range(cases):
            stem=f'criatura{i:03d}'
            # New subjects and properties never appear in the syntax examples.
            e.lesson(f'aprende que {stem} es clasea',session=session)
            q=[f'{stem} requiere agua?',f'¿es cierto que {stem} requiere agua?',
               f'por qué {stem} requiere agua?',f'explain why {stem} requires water',
               f'why does the {stem} require water?'][i%5]
            explanation=i%5>=2
            expected=(SURFACE[9,1] if explanation else SURFACE[8,1])+f' {stem.capitalize()} requiere agua. [{stem} --es--> clasea --requiere--> agua]'
            e.check(q,expected,session=session);timings.append(e.times[-1])
            e.check('por qué?',SURFACE[9,1]+f' {stem.capitalize()} requiere agua. [{stem} --es--> clasea --requiere--> agua]',session=session)
            # Productive wh-answer: this exact inherited consequence was never
            # supplied by the examiner as a statement or an inference answer.
            e.check(f'what does {stem} require?',SURFACE[8,2]+f' {stem.capitalize()} requires water. [{stem} --is--> clasea --requires--> water]',2,session=session)
            alias=f'being{i:03d}'
            e.check(f'{alias} means {stem}',SURFACE[2,2],2,session=session,readonly=False)
            e.check(f'is it true that {alias} requires water?',SURFACE[8,2]+f' {alias.capitalize()} requires water. [{alias} --is--> clasea --requires--> water]',2,session=session)
            e.check(f'recuerda que {stem} no es ave',SURFACE[1,1],session=session,readonly=False)
            e.check(f'{alias} is bird?',SURFACE[8,2]+f' {alias.capitalize()} is not a bird.',2,session=session)
            if i%20==0:print('NOVEL_OPEN_DIALOGUE_PROGRESS',i+1,flush=True)
        metrics=session.metrics()
    audit(e)
    # The two languages share one new concept ID, with canonical names chosen
    # from the requested output language instead of duplicating the concept.
    words=lexicon(snapshot(e.state)[1]);assert all(words[f'criatura{i:03d}'][0]==words[f'being{i:03d}'][0] for i in range(cases))
    e.state.write_bytes(learned)
    print('NOVEL_DIALOGUES_PASS',cases,cases*8,flush=True)
    return {'novel_dialogues':cases,'novel_dialogue_turns':cases*8,'new_reasoning_ms':{
        'median':statistics.median(timings),'p95':sorted(timings)[max(0,(len(timings)*95+99)//100-1)]},'session_metrics':metrics}


def safety_and_corrections(e,binary,learned):
    e.state.write_bytes(learned)
    with Session(binary,e.state,e.program) as session:
        before=e.state.read_bytes();count=u16(snapshot(e.state)[1],U+6)
        for q in ['qué es desconocido?', 'desconocido requiere agua?', 'how does infinity think?',
                  'aprende que falso es mamífero?', '¿recuerda que falso es mamífero',
                  '¿olvida que dida es clasea?', 'alias nuevo gato?', 'aprende que termino termino agua']:
            expected=SURFACE[11,1] if q.endswith('termino termino agua') else (
                SURFACE[4,1] if q.startswith(('aprende que falso','¿recuerda','¿olvida','alias nuevo')) else conversation.ACTS[3,1])
            # Unknown old-style queries retain the old surface; syntactically
            # recognized new terms use the extension's evidence message.
            if q=='desconocido requiere agua?':expected=SURFACE[4,1]
            e.check(q,expected,session=session)
            assert u16(snapshot(e.state)[1],U+6)==count and 'falso' not in names(e)
        e.check('gato significa perro',SURFACE[12,1],session=session)
        e.check('por qué?',SURFACE[6,1],session=session)
        e.lesson('aprende que duda es mamífero',session=session)
        e.lesson('aprende que duda no es ave',session=session)
        e.lesson('aprende que duda es ave',session=session)
        e.check('duda es ave?',SURFACE[5,1],session=session)
        e.check('why',SURFACE[6,2],2,session=session)
        e.check('olvida que duda es ave',SURFACE[3,1],session=session,readonly=False)
        e.check('duda es ave?',SURFACE[4,1],session=session)
        e.lesson('aprende que duda no es ave',session=session)
        e.check('duda es ave?',SURFACE[8,1]+' Duda no es un ave.',session=session)
    # Contradicting a preexisting fact blocks both surfaces while preserving
    # every old evidence byte. Retraction restores the original evidence.
    e.state.write_bytes(learned)
    with Session(binary,e.state,e.program) as session:
        e.lesson('aprende que gato no es mamífero',session=session)
        e.check('gato es mamífero?',SURFACE[5,1],session=session)
    with Session(binary,e.state,e.compact) as session:e.check('gato es mamífero?','?',session=session)
    with Session(binary,e.state,e.program) as session:
        e.check('olvida que gato es mamífero',SURFACE[3,1],session=session,readonly=False)
        e.check('gato es mamífero?',SURFACE[8,1]+' Un gato es un mamífero.',session=session)
    with Session(binary,e.state,e.compact) as session:e.check('gato es mamífero?','gato es mamífero.',session=session)
    # Explicit exceptions block inherited conclusions for both yes/no and wh.
    e.state.write_bytes(learned)
    with Session(binary,e.state,e.program) as session:
        e.lesson('aprende que claseconflicto requiere agua',session=session)
        e.lesson('aprende que excepcion es claseconflicto',session=session)
        e.lesson('aprende que claseconflicto no requiere agua',session=session)
        e.check('excepcion requiere agua?',SURFACE[5,1],session=session)
        e.check('qué requiere excepcion?',SURFACE[5,1],session=session)
    e.state.write_bytes(learned)
    with Session(binary,e.state,e.program) as session:
        e.lesson('aprende que clasec es clasea',session=session)
        e.lesson('aprende que clasec no requiere agua',session=session)
        e.lesson('aprende que impedido es clasec',session=session)
        e.check('impedido requiere agua?',SURFACE[4,1],session=session)
        e.check('qué requiere impedido?',SURFACE[4,1],session=session)
        e.lesson('aprende que negativo no requiere agua',session=session)
        e.check('negativo requires water?',SURFACE[8,2]+' Negativo does not require water.',2,session=session)
        e.lesson('learn that signed observes water',2,session=session)
        e.check('observe means observes',SURFACE[2,2],2,session=session,readonly=False)
        e.lesson('learn that signed does not observe water',2,session=session)
        e.check('signed observes water?',SURFACE[5,2],2,session=session)
        e.check('forget that signed observes water',SURFACE[3,2],2,session=session,readonly=False)
        e.lesson('learn that signed does not observe water',2,session=session)
        e.check('signed observes water?',SURFACE[8,2]+' It is false that Signed observes water.',2,session=session)
    audit(e);e.state.write_bytes(learned)
    print('UNKNOWN_QUERIES_DONT_LEARN_NEGATION_CONFLICT_CORRECTION_PASS',flush=True)


def rule_controls(e,binary,learned):
    e.state.write_bytes(learned)
    # No arbitrary new predicate inherits a rule merely because it is a verb.
    with Session(binary,e.state,e.program) as session:
        e.lesson('aprende que primero observa segundo',session=session)
        e.lesson('aprende que segundo observa tercero',session=session)
        e.check('primero observa tercero?',SURFACE[4,1],session=session)
        e.lesson('aprende que crece es clasea',session=session)
        e.check('crece requiere agua?',SURFACE[8,1]+' Crece requiere agua. [crece --es--> clasea --requiere--> agua]',session=session)
        e.check('olvida que dida requiere agua',SURFACE[3,1],session=session,readonly=False)
        e.check('crece requiere agua?',SURFACE[4,1],session=session)
        e.lesson('aprende que dida requiere agua',session=session)
        e.check('crece requiere agua?',SURFACE[8,1]+' Crece requiere agua. [crece --es--> clasea --requiere--> agua]',session=session)
    e.state.write_bytes(learned)
    # Same spelling "requiere", same interpreter, different consequence
    # witnesses: learn transitivity instead of inheritance in a control copy.
    e.run(stores([(U+2000000+264*64+i,0) for i in range(64)]))
    with Session(binary,e.state,e.program) as session:
        for a,b,c in [('cxuno','cxdos','cxtres'),('cyuno','cydos','cytres')]:
            for text in [f'aprende que {a} requiere {b}',f'aprende que {b} requiere {c}',f'aprende que {a} requiere {c}']:
                e.lesson(text,session=session)
        e.lesson('aprende que fuerauno requiere fuerados',session=session)
        e.lesson('aprende que fuerados requiere fueratres',session=session)
    ids=names(e);e.calibrate(264,ids['cxuno'],ids['cxdos'],ids['cxtres'])
    for _ in range(3):e.calibrate(264,ids['cxuno'],ids['cxdos'],ids['cxtres'])
    assert snapshot(e.state)[1][U+2000000+264*64]==1
    with Session(binary,e.state,e.program) as session:e.check('fuerauno requiere fueratres?',SURFACE[4,1],session=session)
    e.calibrate(264,ids['cyuno'],ids['cydos'],ids['cytres'])
    with Session(binary,e.state,e.program) as session:
        e.check('fuerauno requiere fueratres?',SURFACE[8,1]+' Fuerauno requiere fueratres. [fuerauno --requiere--> fuerados --requiere--> fueratres]',session=session)
        e.lesson('aprende que otro es clasea',session=session)
        e.check('otro requiere agua?',SURFACE[4,1],session=session)
    # A contradictory family lesson is atomic, and stale closures cannot keep
    # the counterfactual transitive model enabled.
    ids=names(e);e.calibrate(264,ids['dida'],ids['clasea'],110,reject=True)
    audit(e);e.state.write_bytes(learned)
    print('REPEATED_WITNESSES_REVALIDATION_AND_REVERSED_REASONING_PASS',flush=True)


def scale_and_budgets(e,binary,learned,terms):
    e.state.write_bytes(learned)
    with Session(binary,e.state,e.program) as session:
        for i in range(terms):
            e.lesson(f'aprende que entidad{i:03d} es mamífero',session=session)
        memory=snapshot(e.state)[1];words=lexicon(memory)
        assert 471+u16(memory,U+6)>512 and max(cid for cid,_,_ in words.values())>512
        assert u16(memory,K+4)==471
        for i in range(0,terms,max(1,terms//20)):
            s=f'entidad{i:03d}'
            e.check(f'{s} es organismo?',SURFACE[8,1]+f' {s.capitalize()} es un organismo. [{s} --es--> mamífero --es--> vertebrado --es--> organismo]',session=session)
        metrics=session.metrics()
    audit(e)
    count=u16(snapshot(e.state)[1],U+6)
    # Reload the same grown graph and resolve its widest entity ID after exit.
    with Session(binary,e.state,e.program) as session:
        s=f'entidad{terms-1:03d}'
        e.check(f'qué es {s}?',SURFACE[8,1]+f' {s.capitalize()} es un mamífero; {s} es un vertebrado; {s} es un animal; {s} es un organismo.',session=session)
    e.state.write_bytes(learned)
    # Bounded deep search returns a limit, not an invented negative answer.
    with Session(binary,e.state,e.program) as session:
        for i in range(34):e.lesson(f'aprende que tramo{i:02d} alcanza tramo{i+1:02d}',session=session)
        e.check('tramo00 alcanza tramo34?',SURFACE[7,1],session=session)
        e.lesson('aprende que mismo es mismo',session=session)
        e.check('mismo es mismo?',SURFACE[8,1]+' Mismo es mismo.',session=session)
    audit(e);e.state.write_bytes(learned)
    print('U16_CONCEPTS_GROWN_LEXICON_RESTART_AND_SEARCH_LIMITS_PASS',terms,flush=True)
    return {'growth_terms':terms,'grown_extension_lexical_entries':count,'grown_total_lexical_entries':471+count,'growth_metrics':metrics}


def retention(e,binary,learned):
    e.state.write_bytes(learned)
    # All old byte-exact compact and all E016 realized factual answers on NEW
    # E017, before users add new assertions that deliberately affect them.
    for program,polished in [(e.compact,False),(e.program,True)]:
        with Session(binary,e.state,program) as session:
            for text,answer,language in stories.retained_curriculum():
                e.check(text,conversation.factual_answer(answer,language) if polished else answer,language,session=session)
    e.state.write_bytes(learned)
    with Session(binary,e.state,e.program) as session:
        e.check('ana tiene dos manzanas','Ana tiene dos manzanas.',session=session,readonly=False)
        e.check('ella recibe tres más','Ana tiene cinco manzanas.',session=session,readonly=False)
        e.check('how many does she have?','Ana has five apples.',2,session=session)
        e.check('¿qué es un gato?','Un gato es un mamífero.',session=session)
        e.check('¿y un perro?','Un perro es un mamífero.',session=session)
        e.check('hola',conversation.ACTS[1,1],session=session)
        e.check('un más dos',conversation.ACTS[5,1]+' tres.',session=session,readonly=False)
    audit(e);e.state.write_bytes(learned)
    print('ALL_1522_OLD_CASES_IN_BOTH_SURFACES_AND_E016_DIALOGUE_PASS',flush=True)


def transaction_controls(e,binary,learned):
    e.state.write_bytes(learned)
    answer=SURFACE[9,1]+' Baseuno es un organismo. [baseuno --es--> mamífero --es--> vertebrado --es--> organismo]'
    with Session(binary,e.state,e.program) as session:
        e.lesson('aprende que baseuno es mamífero',session=session)
        e.check('baseuno es organismo?',answer.replace(SURFACE[9,1],SURFACE[8,1]),session=session)
        pending=Path(str(e.state)+'.pending');pending.mkdir();before=e.state.read_bytes()
        try:
            try:session.request('aprende que falloguardado es clasea');raise AssertionError('save failure acknowledged')
            except RuntimeError as error:assert 'cannot write state' in str(error),error
            assert e.state.read_bytes()==before and 'falloguardado' not in names(e)
        finally:pending.rmdir()
        e.check('por qué?',answer,session=session)
    count=u16(snapshot(e.state)[1],U+6)
    body=e.program.read_text();end='\nlabel finish\nhalt\n';assert body.count(end)==1
    injected=e.out/'failure-after-learning.xi'
    injected.write_text(body.replace(end,f'\nlabel finish\nload8 r0 {U+6}\nload8 r1 {U+7}\nmul r1 256\nadd r0 r1\ncmp r0 {count}\nje finish_ok\ndiv r0 0\nlabel finish_ok\nhalt\n'))
    with Session(binary,e.state,injected) as session:
        before=e.state.read_bytes()
        try:session.request('aprende que falloexcepcion es clasea');raise AssertionError('post-learning XI error acknowledged')
        except RuntimeError:pass
        assert e.state.read_bytes()==before and 'falloexcepcion' not in names(e)
        e.check('por qué?',answer,session=session)
    e.state.write_bytes(learned)
    print('ATOMIC_NEW_VOCABULARY_FACTS_AND_EXPLANATION_CACHE_ROLLBACK_PASS',flush=True)


def interfaces(e,binary,learned):
    e.state.write_bytes(learned)
    with Session(binary,e.state,e.program) as session:
        e.lesson('aprende que persistente es mamífero',session=session)
        e.check('persistente es organismo?',SURFACE[8,1]+' Persistente es un organismo. [persistente --es--> mamífero --es--> vertebrado --es--> organismo]',session=session)
    with Session(binary,e.state,e.program) as session:
        e.check('por qué?',SURFACE[9,1]+' Persistente es un organismo. [persistente --es--> mamífero --es--> vertebrado --es--> organismo]',session=session)
    before=immutable(e.state);e.run((ROOT.parent/'stories/reset-episode.xi').read_text())
    assert immutable(e.state)==before
    with Session(binary,e.state,e.program) as session:e.check('why',SURFACE[6,2],2,session=session)
    fixture=e.out/'cache-fixture';shutil.copytree(REPO/'ai/xi',fixture/'xi')
    state=fixture/'state.rvp';state.write_bytes(learned)
    cli=['bash',str(fixture/'xi/knowledge/text.sh'),e.runtime,str(state)]
    assert subprocess.check_output(cli+['aprende que cliuno es mamífero','es'],text=True)==SURFACE[1,1]+'\n'
    expected=SURFACE[8,1]+' Cliuno es un organismo. [cliuno --es--> mamífero --es--> vertebrado --es--> organismo]'
    assert subprocess.check_output(cli+['cliuno es organismo?','es'],text=True)==expected+'\n'
    assert subprocess.check_output(cli+['cliuno es organismo?','es','--compact'],text=True)=='cliuno es organismo. [cliuno --es--> mamífero --es--> vertebrado --es--> organismo]\n'
    assert len(list((fixture/'.bbyq-xi-cache').glob('*.xi')))==2
    name=fixture/'xi/open/name.xi';name.write_text(name.read_text().replace('\n','\nset r14 33\nprint r14\n',1))
    actual=subprocess.check_output(cli+['cliuno es organismo?','es'],text=True)
    assert actual!=expected+'\n' and '!' in actual
    assert len(list((fixture/'.bbyq-xi-cache').glob('*.xi')))==3
    client=[sys.executable,str(REPO/'ai/native/session_client.py'),str(binary),str(e.state)]
    value=subprocess.check_output(client,input='aprende que cliente es mamífero\ncliente es organismo?\n',text=True)
    assert value==SURFACE[1,1]+'\n'+SURFACE[8,1]+' Cliente es un organismo. [cliente --es--> mamífero --es--> vertebrado --es--> organismo]\n'
    # Fatal startup is reported with the native diagnostic; closing a broken
    # pipe must not mask it or erase a writer lock owned by another process.
    lock=Path(str(e.state)+'.lock');lock.mkdir()
    try:
        with Session(binary,e.state,e.program) as blocked:
            deadline=time.perf_counter()+5
            while time.perf_counter()<deadline:
                blocked.stderr.seek(0)
                if b'active writer' in blocked.stderr.read():break
                time.sleep(.01)
            try:blocked.request('hola');raise AssertionError('blocked writer accepted')
            except RuntimeError as error:assert 'active writer' in str(error),error
        assert lock.is_dir()
    finally:lock.rmdir()
    e.state.write_bytes(learned)
    print('RESIDENT_AND_CLI_CLIENTS_SOURCE_CACHE_AND_RESET_PASS',flush=True)


def diagnostic(e,binary,learned):
    source=ROOT/'data/diagnostic-before-v1.json'
    original=json.loads(source.read_text());e.state.write_bytes(learned);result=[]
    with Session(binary,e.state,e.program) as session:
        for row in original:
            raw,ms=session.request(row['input']);result.append({**row,'before':row['output'],'output':decode_result(raw),'ms':ms})
    e.state.write_bytes(learned)
    return result


def main():
    ap=argparse.ArgumentParser();ap.add_argument('runtime');ap.add_argument('session_binary');ap.add_argument('parent')
    ap.add_argument('--out',default='evidence/e017');ap.add_argument('--smoke',action='store_true')
    ap.add_argument('--cases',type=int,default=80);ap.add_argument('--terms',type=int,default=280);args=ap.parse_args()
    e=Examiner(args.runtime,args.parent,args.out);binary=Path(args.session_binary).resolve()
    learned,seconds=train(e,binary);release=e.out/'BBYQ_E017_Open_Learning_ES_EN.rvp';release.write_bytes(learned)
    print('TRAINED',hashlib.sha256(learned).hexdigest(),len(learned),'SECONDS',seconds,flush=True)
    with Session(binary,e.state,e.program) as session:
        checks=[('explícame qué es un gato','Un gato es un mamífero.',1),
                ('aprende que neral es mamífero','Aprendí esa afirmación del diálogo.',1),
                ('qué es neral?','Según lo aprendido: Neral es un mamífero; neral es un vertebrado; neral es un animal; neral es un organismo.',1),
                ('neral es organismo?','Según lo aprendido: Neral es un organismo. [neral --es--> mamífero --es--> vertebrado --es--> organismo]',1),
                ('por qué?','La evidencia guardada es: Neral es un organismo. [neral --es--> mamífero --es--> vertebrado --es--> organismo]',1),
                ('michi significa gato','Aprendí ese nombre para el mismo concepto.',1),
                ('qué es michi?','Un gato es un mamífero.',1),
                ('aprende que silu es clasea','Aprendí esa afirmación del diálogo.',1),
                ('silu requiere agua?','Según lo aprendido: Silu requiere agua. [silu --es--> clasea --requiere--> agua]',1),
                ('learn that silu is not bird','I learned that statement from this dialogue.',2),
                ('silu is bird?','From the taught statements: Silu is not a bird.',2)]
        for text,answer,language in checks:
            changes=text.startswith(('aprende','learn','michi significa'))
            e.check(text,answer,language,session=session,readonly=not changes);print('OPEN_PASS',text,'->',answer,flush=True)
    e.state.write_bytes(learned)
    if args.smoke:return
    core,memory,bindings=snapshot(e.state)
    assert core==e.original[0] and bindings==e.original[2]
    assert {a:b for a,b in memory.items() if not U<=a<U+2**51}==e.original[1]
    assert u16(memory,K+4)==471 and u16(memory,K+6)==185
    audit(e);learning_controls(e,binary,learned)
    report=novel_dialogues(e,binary,learned,args.cases)
    safety_and_corrections(e,binary,learned)
    rule_controls(e,binary,learned)
    report.update(scale_and_budgets(e,binary,learned,args.terms))
    transaction_controls(e,binary,learned)
    interfaces(e,binary,learned)
    retention(e,binary,learned)
    diag=diagnostic(e,binary,learned)
    audit(e)
    m=snapshot(e.state)[1]
    report.update({'stage':'E017','parent_sha256':PARENT_SHA,'learned_sha256':hashlib.sha256(learned).hexdigest(),
        'checkpoint_bytes':len(learned),'training_seconds':seconds,'learned_constructions':m[U+10],
        'construction_presentations':len(rows('constructions-v1.psv')),'extension_lexical_entries':u16(m,U+6),
        'legacy_lexical_entries_unchanged':471,'total_lexical_entries':471+u16(m,U+6),
        'new_concepts_next_id':u16(m,U+4),'registered_dialogue_assertions_in_release':u16(m,U+8),
        'legacy_facts_unchanged':185,'reasoning_families':['witnessed transitivity','witnessed class-property inheritance'],
        'fixed_surface_lessons':len(rows('surface-v1.psv')),'base_form_lessons':len(rows('bases-v1.psv')),
        'parent_memory_preserved_exactly':True,'unknown_queries_never_allocate':True,
        'atomic_learning_and_explanation_cache_rollback':True,'old_subject_conflicts_seen_in_both_surfaces':True,
        'prior_cases_per_surface':1522,'checks':e.checks,'old_training_replayed':False,
        'limits':{'extended_words':2048,'extended_assertions':1024,'constructions':64,'tokens':15,'input_bytes':255,
                  'search_nodes':64,'proof_nodes':32,'answers':8,'open_conversation_achieved':False},
        'platform':sys.platform,'intelligence':'XI only; unchanged pinned REVERSE-PC and Mundo X; one RVPC2',
        'no_reverse_os_integration':True})
    e.state.write_bytes(learned)
    (e.out/'results.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    (e.out/'raw.jsonl').write_text(''.join(json.dumps(x,ensure_ascii=False)+'\n' for x in e.transcript))
    if diag:(e.out/'diagnostic.json').write_text(json.dumps(diag,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(report,ensure_ascii=False,indent=2),flush=True)


if __name__=='__main__':main()
