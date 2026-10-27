#!/usr/bin/env python3
"""Continue authentic E017; syntax teaching and expected answers stay outside XI.

The native resident learner receives only text and output language per turn.
E018 configures presentation separately from inference and teaches 25 further
constructions, without replaying earlier lessons or changing their evidence.
"""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import shutil
import statistics
import subprocess
import sys
import time

ROOT=Path(__file__).resolve().parents[1]
REPO=ROOT.parents[2]
PARENT_SHA='5ae5283a213a84c78ae9fc1eac0ff5972b018feed3c677f0a4e7d38f8aed7c4c'
spec=importlib.util.spec_from_file_location('e017',ROOT/'tests/native-open.py')
e017=importlib.util.module_from_spec(spec);spec.loader.exec_module(e017)
Session,decode_result=e017.Session,e017.decode_result
snapshot,stores,frame=e017.snapshot,e017.stores,e017.frame
U,K,C=e017.U,e017.K,e017.C
SURFACE=e017.SURFACE


class Examiner(e017.Examiner):
    def __init__(self,runtime,parent,out):
        super().__init__(runtime,parent,out,expected_parent=PARENT_SHA)
        self.programs['open-style']=subprocess.check_output(['bash',str(ROOT.parent/'knowledge/link.sh'),'open-style'],text=True).split('\n',1)[1]

    def style(self,preference,reject=False):
        self.teach('open-style',[(U+316,preference)],reject=reject)


def restore_context(e):
    old=e.original[1]
    mutable=[K+3,*range(K+8,K+16),*range(K+2100,K+2108),*range(K+2200,K+2232),*range(C+4,C+16),*range(U+12,U+20)]
    e.run(stores([(a,old.get(a,0)) for a in mutable]))


def train(e):
    started=time.perf_counter()
    # Preference cannot be enabled until its required fragments exist.
    e.style(1,reject=True)
    for cid,kind,language,text in e017.rows('e018-words.psv'):
        e.word(int(cid),int(kind),int(language),text)
    for act,language,text in e017.rows('e018-surface.psv'):
        e.teach('open-utterance',[(U+304,int(act))],text,int(language))
    for pid,intent,s,p,o,alias,language,text in e017.rows('e018-constructions.psv'):
        e.pattern(*map(int,(pid,intent,s,p,o,alias,language)),text)
    for (preference,) in e017.rows('e018-style.psv'):e.style(int(preference))
    restore_context(e)
    core,memory,bindings=snapshot(e.state)
    assert core==e.original[0] and bindings==e.original[2]
    changed={U+3,U+4,U+5,U+6,U+7,U+10}
    assert {a:b for a,b in e.original[1].items() if a not in changed}=={a:memory.get(a,0) for a in e.original[1] if a not in changed},'existing learned byte changed'
    assert {a:b for a,b in memory.items() if not U<=a<U+2**51}=={a:b for a,b in e.original[1].items() if not U<=a<U+2**51}
    old_count=e017.u16(e.original[1],U+6);new_count=e017.u16(memory,U+6)
    old_next=e017.u16(e.original[1],U+4);new_next=e017.u16(memory,U+4)
    def declared(a):
        return a in changed or U+10000+39*96<=a<U+10000+64*96 or U+20000+old_next<=a<U+20000+new_next or U+100000+old_count*40<=a<U+100000+new_count*40 or U+507168<=a<U+507680
    assert all(declared(a) for a,b in memory.items() if b!=e.original[1].get(a,0)),'undeclared memory addition'
    assert memory[U+3]==1 and memory[U+10]==64
    assert e017.u16(memory,U+8)==12
    for i in range(64):assert memory.get(U+10000+i*96+2,0)==1,('construction not enabled',i+1)
    e017.audit(e)
    return e.state.read_bytes(),time.perf_counter()-started


def smoke(e,binary,learned):
    with Session(binary,e.state,e.program) as session:
        checks=[
            ('gato es organismo?','Un gato es un organismo.',1,True),
            ('por qué?',SURFACE[9,1]+' Un gato es un organismo. [gato --es--> mamífero --es--> vertebrado --es--> organismo]',1,True),
            ('aprende que el neral es un mamífero',SURFACE[1,1],1,False),
            ('háblame de neral',SURFACE[8,1]+' Neral es un mamífero, un vertebrado, un animal y un organismo.',1,True),
            ('neral es organismo?',SURFACE[8,1]+' Neral es un organismo.',1,True),
            ('por qué?',SURFACE[9,1]+' Neral es un organismo. [neral --es--> mamífero --es--> vertebrado --es--> organismo]',1,True),
            ('tell me if neral is organism',SURFACE[8,2]+' Neral is an organism.',2,True),
            ('learn that the neral is not a bird',SURFACE[1,2],2,False),
            ('neral is bird?',SURFACE[8,2]+' Neral is not a bird.',2,True),
            ('qué estudia filosofía?','Filosofía estudia conciencia y conocimiento.',1,True),
            ('qué es algoquenoexiste?',e017.conversation.ACTS[3,1],1,True),
        ]
        for q,a,l,readonly in checks:
            e.check(q,a,l,session=session,readonly=readonly)
            print('E018_PASS',q,'->',a,flush=True)
    e.state.write_bytes(learned)


def query_forms(s):
    """Independent exam prompts; novel subjects and derived consequences."""
    return [
        (40,f'qué significa {s}',1,'definition'),
        (41,f'qué significa un {s}',1,'definition'),
        (42,f'what is the meaning of {s}',2,'definition'),
        (43,f'tell me about {s}',2,'definition'),
        (44,f'háblame de {s}',1,'definition'),
        (45,f'háblame de un {s}',1,'definition'),
        (46,f'me puedes decir qué es {s}',1,'definition'),
        (47,f'puedes decirme qué es un {s}',1,'definition'),
        (48,f'can you explain what {s} requires',2,'require'),
        (49,f'could you tell me what {s} requires',2,'require'),
        (50,f'dime si {s} es organismo',1,'organism'),
        (51,f'tell me if {s} is organism',2,'organism'),
        (52,f'puedes decirme si el {s} es organismo',1,'organism'),
        (53,f'can you tell me if {s} requires water',2,'require'),
        (54,f'why is {s} organism',2,'why-organism'),
        (55,f'por qué el {s} es un organismo',1,'why-organism'),
        (56,f'why is the {s} a vertebrate',2,'why-vertebrate'),
        (57,f'qué es {s} por favor',1,'definition'),
        (58,f'what does {s} require please',2,'require'),
    ]


def expected(s,language,kind):
    name=s.capitalize()
    if kind=='definition':
        tail='es un mamífero, un vertebrado, un animal y un organismo.' if language==1 else 'is a mammal, a vertebrate, an animal and an organism.'
    elif kind=='require':tail='requiere agua.' if language==1 else 'requires water.'
    elif kind=='why-vertebrate':tail='is a vertebrate.'
    else:tail='es un organismo.' if language==1 else 'is an organism.'
    act=9 if kind.startswith('why-') else 8
    answer=SURFACE[act,language]+' '+name+' '+tail
    if kind.startswith('why-'):
        if language==1:path=f'{s} --es--> mamífero --es--> vertebrado --es--> organismo'
        elif kind=='why-vertebrate':path=f'{s} --is--> mammal --is--> vertebrate'
        else:path=f'{s} --is--> mammal --is--> vertebrate --is--> organism'
        answer+=' ['+path+']'
    return answer


def novel_dialogues(e,binary,learned,dialogs):
    e.state.write_bytes(learned);covered=set();before=e.checks
    with Session(binary,e.state,e.program) as session:
        # A held-out assumption supplies a new use of the calibrated rule;
        # no tested entity or derived consequence is supplied as a lesson.
        e.lesson('aprende que mamífero requiere agua',session=session)
        for i in range(dialogs):
            s=f'criatura{i:03d}';alias=f'being{i:03d}';language=1+i%2
            q=f'aprende que el {s} es un mamífero' if language==1 else f'learn that the {s} is a mammal'
            e.lesson(q,language,session=session);covered.add(58+language)
            pid,q,lang,kind=query_forms(s)[i%19]
            e.check(q,expected(s,lang,kind),lang,session=session);covered.add(pid)
            e.check(s+' es organismo?',expected(s,1,'organism'),session=session)
            e.check('por qué?',expected(s,1,'why-organism'),session=session)
            e.check(f'{alias} means {s}',SURFACE[2,2],2,session=session,readonly=False)
            # An alias does not replace the first taught name in that language.
            english_name=alias if language==1 else s
            e.check(f'tell me whether {alias} is organism',expected(english_name,2,'organism'),2,session=session)
            q=f'aprende que el {s} no es un ave' if language==1 else f'learn that the {s} is not a bird'
            e.lesson(q,language,session=session);covered.add(60+language)
            e.check(f'{alias} is bird?',SURFACE[8,2]+f' {english_name.capitalize()} is not a bird.',2,session=session)
            count=e017.u16(snapshot(e.state)[1],U+6)
            e.check(f'can you tell me if {alias} requires unknownobject',SURFACE[4,2],2,session=session)
            assert e017.u16(snapshot(e.state)[1],U+6)==count
            e.check('why',SURFACE[6,2],2,session=session)
            q=f'olvida que el {s} es un mamífero' if language==1 else f'forget that the {s} is a mammal'
            e.check(q,SURFACE[3,language],language,session=session,readonly=False);covered.add(62+language)
            e.check(f'{s} es organismo?',SURFACE[4,1],session=session)
            if i%20==0:print('E018_NOVEL_DIALOGUES_PROGRESS',i+1,flush=True)
        metrics=session.metrics()
    assert covered==set(range(40,65)),covered
    names=e017.lexicon(snapshot(e.state)[1])
    assert all(names[f'criatura{i:03d}'][0]==names[f'being{i:03d}'][0] for i in range(dialogs))
    e017.audit(e);e.state.write_bytes(learned)
    print('E018_ALL_25_CONSTRUCTIONS_TRANSFER_TO_NOVEL_DIALOGUES_PASS',dialogs,flush=True)
    return {'novel_dialogues':dialogs,'novel_dialogue_turns':dialogs*12,'heldout_background_lessons':1,
            'new_constructions_examined':sorted(covered),'novel_session_metrics':metrics,'novel_checks':e.checks-before}


def brief_fact(compact,language):
    """Realization oracle over the independent old semantic exam, not XI input."""
    negative=compact.startswith('no: ')
    if negative:compact=compact[4:]
    body=compact.partition(' [')[0].removesuffix('.')
    triples=[t.split() for t in body.split('; ')]
    s,p,_=triples[0];assert all(t[:2]==[s,p] for t in triples)
    articles={}
    for _,mode,lang,text in e017.conversation.rows('nominals-v1.psv'):
        if mode=='3' and int(lang)==language:
            article,noun=text.split(' ',1);articles[noun]=article
    def noun(n):
        result=(articles[n]+' '+n) if p in ('es','is') and n in articles else n
        return result.replace('_',' ')
    objects=[noun(t[2]) for t in triples]
    obj=objects[0] if len(objects)==1 else ', '.join(objects[:-1])+(' y ' if language==1 else ' and ')+objects[-1]
    text=f'{noun(s)} {p.replace("_"," ")} {obj}.'
    return e017.conversation.ACTS[7,language]+' '+text if negative else text[0].upper()+text[1:]


def retention(e,binary,learned):
    cases=e017.stories.retained_curriculum()
    for mode in ['conversation','combined']:
        e.state.write_bytes(learned)
        program=e.program if mode=='conversation' else e.compact
        with Session(binary,e.state,program) as session:
            for index,(q,compact,language) in enumerate(cases):
                answer=brief_fact(compact,language) if mode=='conversation' else compact
                e.check(q,answer,language,session=session)
                if index%500==499:print('E018_RETENTION_PROGRESS',mode,index+1,flush=True)
    e.state.write_bytes(learned)
    with Session(binary,e.state,e.program) as session:
        e.check('ana tiene dos manzanas','Ana tiene dos manzanas.',session=session,readonly=False)
        e.check('ella recibe tres más','Ana tiene cinco manzanas.',session=session,readonly=False)
        e.check('how many does she have?','Ana has five apples.',2,session=session)
        e.check('hola',e017.conversation.ACTS[1,1],session=session)
        e.check('dos mas tres',e017.conversation.ACTS[5,1]+' cinco.',session=session,readonly=False)
    e.state.write_bytes(learned)
    print('E018_ALL_1522_FACTS_BRIEF_AND_EXACT_COMPACT_RETENTION_PASS',flush=True)


def controls(e,binary,learned):
    e.state.write_bytes(learned)
    # Repetition and changes that fail to identify a subject do not promote.
    a=U+10000+39*96;e.run(stores([(a+i,0) for i in range(96)]))
    for _ in range(4):e.pattern(40,8,5,0,0,0,1,'qué significa gato')
    assert snapshot(e.state)[1].get(a+2,0)==0
    e.pattern(40,8,6,0,0,0,1,'qué significa perro');assert snapshot(e.state)[1][a+2]==1
    e.state.write_bytes(learned)
    # A concrete wh-prefix wins over the broad "alias means target" frame.
    with Session(binary,e.state,e.program) as session:
        e.check('qué significa gato','Un gato es un mamífero.',session=session)
        e.check('qué es el significado de gato','Un gato es un mamífero.',session=session)
        e.check('michi significa gato',SURFACE[2,1],session=session,readonly=False)
        e.check('qué significa michi','Un gato es un mamífero.',session=session)
    e.state.write_bytes(learned)
    # Equally specific conflicting interpretations still require clarification.
    a=U+10000+63*96;e.run(stores([(a+i,0) for i in range(96)]))
    e.pattern(64,2,6,23,5,0,1,'gato es perro')
    e.pattern(64,2,40,23,6,0,1,'perro es mamífero')
    with Session(binary,e.state,e.program) as session:
        e.check('gato es perro',SURFACE[11,1],session=session)
    e.state.write_bytes(learned)
    e.style(2,reject=True)
    e.run(stores([(U+3,2)]));e.run((ROOT/'audit.xi').read_text(),reject=True)
    e.state.write_bytes(learned)
    # Changing display preference retains the same facts and inference.
    e.style(0)
    with Session(binary,e.state,e.program) as session:
        e.check('gato es organismo?','Un gato es un organismo. [gato -> mamífero -> vertebrado -> organismo]',session=session)
        e.check('qué estudia filosofía?','Filosofía estudia conciencia; filosofía estudia conocimiento.',session=session)
    e.style(1)
    with Session(binary,e.state,e.program) as session:
        e.check('gato es organismo?','Un gato es un organismo.',session=session)
        e.check('por qué?',SURFACE[9,1]+' Un gato es un organismo. [gato --es--> mamífero --es--> vertebrado --es--> organismo]',session=session)
        for q in ['qué es desconocidofalso?','aprende que el falso es un mamífero?',
                  'learn that the falseword is not a bird?', 'olvida que el gato es un mamífero?',
                  'forget that the cat is a mammal?', 'tell me if unknownsubject is mammal']:
            before=e017.immutable(e.state)
            raw,_=session.request(q);answer=decode_result(raw)
            assert answer in [e017.conversation.ACTS[3,1],SURFACE[4,1]],(q,answer)
            assert e017.immutable(e.state)==before,'an unknown question taught or deleted a fact'
            assert 'falseword' not in e017.names(e) and 'falso' not in e017.names(e)
        e.lesson('aprende que el gato no es un mamífero',session=session)
        e.check('dime si gato es mamífero',SURFACE[5,1],session=session)
        e.check('forget that the cat is a mammal',SURFACE[3,2],2,session=session,readonly=False)
        e.check('dime si gato es mamífero',SURFACE[8,1]+' Un gato es un mamífero.',session=session)
    e.state.write_bytes(learned)
    print('E018_PREFERENCE_REPETITION_UNCERTAINTY_AND_CONTRADICTION_PASS',flush=True)


def interfaces_and_rollback(e,binary,learned):
    e.state.write_bytes(learned)
    why=SURFACE[9,1]+' Persistente es un organismo. [persistente --es--> mamífero --es--> vertebrado --es--> organismo]'
    with Session(binary,e.state,e.program) as session:
        e.lesson('aprende que el persistente es un mamífero',session=session)
        e.check('dime si persistente es organismo',SURFACE[8,1]+' Persistente es un organismo.',session=session)
        pending=Path(str(e.state)+'.pending');pending.mkdir();before=e.state.read_bytes()
        try:
            try:session.request('learn that the failedsave is a mammal');raise AssertionError('failed save accepted')
            except RuntimeError as error:assert 'cannot write state' in str(error)
            assert e.state.read_bytes()==before
        finally:pending.rmdir()
        e.check('por qué?',why,session=session)
    with Session(binary,e.state,e.program) as session:e.check('por qué?',why,session=session)
    before=e017.immutable(e.state);e.run((ROOT.parent/'stories/reset-episode.xi').read_text())
    assert e017.immutable(e.state)==before and snapshot(e.state)[1][U+3]==1
    with Session(binary,e.state,e.program) as session:e.check('why',SURFACE[6,2],2,session=session)
    e.state.write_bytes(learned)
    client=[sys.executable,str(REPO/'ai/native/session_client.py'),str(binary),str(e.state)]
    assert subprocess.check_output(client,input='gato es organismo?\npor qué?\n',text=True)=='Un gato es un organismo.\n'+SURFACE[9,1]+' Un gato es un organismo. [gato --es--> mamífero --es--> vertebrado --es--> organismo]\n'
    cli=['bash',str(ROOT.parent/'knowledge/text.sh'),e.runtime,str(e.state)]
    assert subprocess.check_output(cli+['gato es organismo?','es'],text=True)=='Un gato es un organismo.\n'
    assert subprocess.check_output(cli+['gato es organismo?','es','--compact'],text=True)=='gato es organismo. [gato -> mamífero -> vertebrado -> organismo]\n'
    e.state.write_bytes(learned)
    print('E018_RESTART_RESET_CLIENTS_AND_LEARNING_ROLLBACK_PASS',flush=True)


def diagnostic(e,binary,learned):
    result=[]
    for label,seed in [('before',e.parent.read_bytes()),('after',learned)]:
        e.state.write_bytes(seed)
        with Session(binary,e.state,e.program) as session:
            session.request('aprende que sondera es mamífero')
            for pid,q,language,kind in query_forms('sondera'):
                raw,ms=session.request(q,language)
                result.append({'stage':label,'construction':pid,'input':q,'language':language,'output':decode_result(raw),'ms':ms})
            for q in ['gato es organismo?','por qué?','qué es desconocidofalso?']:
                raw,ms=session.request(q);result.append({'stage':label,'input':q,'language':1,'output':decode_result(raw),'ms':ms})
    e.state.write_bytes(learned)
    return result


def main():
    p=argparse.ArgumentParser();p.add_argument('runtime');p.add_argument('session_binary');p.add_argument('parent')
    p.add_argument('--out',default='evidence/e018');p.add_argument('--smoke',action='store_true')
    p.add_argument('--dialogs',type=int,default=60);args=p.parse_args()
    e=Examiner(args.runtime,args.parent,args.out);binary=Path(args.session_binary).resolve()
    learned,seconds=train(e);(e.out/'BBYQ_E018_Concise_Dialogue_ES_EN.rvp').write_bytes(learned)
    print('TRAINED_E018',hashlib.sha256(learned).hexdigest(),len(learned),'SECONDS',seconds,flush=True)
    smoke(e,binary,learned)
    if args.smoke:return
    controls(e,binary,learned)
    report=novel_dialogues(e,binary,learned,args.dialogs)
    interfaces_and_rollback(e,binary,learned)
    retention(e,binary,learned)
    diag=diagnostic(e,binary,learned);e017.audit(e)
    memory=snapshot(e.state)[1]
    report.update({'stage':'E018','parent_sha256':PARENT_SHA,'learned_sha256':hashlib.sha256(learned).hexdigest(),
        'checkpoint_bytes':len(learned),'training_seconds':seconds,'checks':e.checks,
        'new_syntax_presentations':len(e017.rows('e018-constructions.psv')),'total_constructions':64,
        'new_lexical_entries':len(e017.rows('e018-words.psv')),'total_lexical_entries':471+e017.u16(memory,U+6),
        'new_world_assertions_in_release':0,'inherited_didactic_assertions':e017.u16(memory,U+8),
        'new_surface_lessons':len(e017.rows('e018-surface.psv')),'old_training_replayed':False,
        'previous_learned_records_unchanged':True,'declared_header_updates_only':True,
        'uncertainty_texts_unchanged':True,'proofs_preserved_on_explicit_request':True,
        'compact_semantics_and_output_unchanged':True,'all_1522_prior_cases_per_surface':True,
        'briefness_is_explicit_configuration':True,'open_conversation_achieved':False,
        'limits':{'tokens':15,'input_bytes':255,'constructions':64,'search_nodes':64,'proof_nodes':32,'answers':8},
        'intelligence':'XI only; same RVPC2 and unchanged pinned owner runtime','platform':sys.platform,
        'no_reverse_os_integration':True})
    e.state.write_bytes(learned)
    for name,content in [('results.json',report),('diagnostic.json',diag)]:
        (e.out/name).write_text(json.dumps(content,ensure_ascii=False,indent=2)+'\n')
    (e.out/'raw.jsonl').write_text(''.join(json.dumps(row,ensure_ascii=False)+'\n' for row in e.transcript))
    print(json.dumps(report,ensure_ascii=False,indent=2),flush=True)


if __name__=='__main__':main()
