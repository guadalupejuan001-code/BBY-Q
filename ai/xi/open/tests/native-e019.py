#!/usr/bin/env python3
"""Continue E018 with query paraphrases and bounded factual discourse.

The examiner owns demonstrations and expected answers. The resident native
process receives only text and output language; all interpretation stays XI.
"""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import statistics
import time

ROOT=Path(__file__).resolve().parents[1]
REPO=ROOT.parents[2]
PARENT_SHA='df074a27d284025ccd033373c92f116c5c3237455e9f51891fcfa0392828aaec'
spec=importlib.util.spec_from_file_location('e018',ROOT/'tests/native-e018.py')
e018=importlib.util.module_from_spec(spec);spec.loader.exec_module(e018)
e017=e018.e017
Session,decode_result=e017.Session,e017.decode_result
snapshot,stores=e017.snapshot,e017.stores
U,K,C=e017.U,e017.K,e017.C
SURFACE=e017.SURFACE
CLARIFY={int(language):text for _,language,text in e017.rows('e019-surface.psv')}
CHECKPOINT='BBYQ_E019_Context_Questions_ES_EN.rvp'


class Examiner(e018.Examiner):
    def __init__(self,runtime,parent,out):
        super().__init__(runtime,parent,out,expected_parent=PARENT_SHA)


def train(e):
    started=time.perf_counter()
    for cid,kind,language,text in e017.rows('e019-words.psv'):
        e.word(int(cid),int(kind),int(language),text)
    for act,language,text in e017.rows('e019-surface.psv'):
        e.teach('open-utterance',[(U+304,int(act))],text,int(language))
    for row in e017.rows('e019-constructions.psv'):
        e.pattern(*map(int,row[:7]),row[7])
    e018.restore_context(e)
    core,memory,bindings=snapshot(e.state)
    assert core==e.original[0] and bindings==e.original[2]
    changed={U+4,U+5,U+6,U+7,U+10}
    assert all(memory.get(a,0)==b for a,b in e.original[1].items() if a not in changed)
    old_count=e017.u16(e.original[1],U+6);new_count=e017.u16(memory,U+6)
    old_next=e017.u16(e.original[1],U+4);new_next=e017.u16(memory,U+4)
    def declared(a):
        return (a in changed or U+10000+64*96<=a<U+10000+96*96 or
                U+20000+old_next<=a<U+20000+new_next or
                U+100000+old_count*40<=a<U+100000+new_count*40 or
                U+507680<=a<U+508192)
    assert all(declared(a) for a,b in memory.items() if b!=e.original[1].get(a,0))
    assert memory[U+10]==96 and memory[U+3]==1
    assert e017.u16(memory,U+8)==12
    for i in range(96):assert memory.get(U+10000+i*96+2,0)==1,('not enabled',i+1)
    # All added constructions end before the existing concept-kind region.
    assert 10000+96*96<20000
    e017.audit(e)
    return e.state.read_bytes(),time.perf_counter()-started


def spoken(s,language,kind='require',other=None):
    name=s.capitalize()
    if kind=='definition':tail='es clasea.' if language==1 else 'is clasea.'
    elif kind=='require':tail='requiere agua.' if language==1 else 'requires water.'
    elif kind=='other':tail='requiere energía.' if language==1 else 'requires energy.'
    elif kind=='reach':tail=('alcanza ' if language==1 else 'reaches ')+other+'.'
    else:raise AssertionError(kind)
    return SURFACE[8,language]+' '+name+' '+tail


def forms(s,other):
    # Held-out entities AND predicates: requiere was absent from syntax lessons.
    # Context-subject questions carry forward the previous predicate, not its
    # object; each must search for this new subject's own answer.
    return [
        (65,f'sabes qué requiere {s}',1,'require',s),
        (66,f'sabes qué requiere el {s}',1,'require',s),
        (67,f'sabes si {s} requiere agua',1,'require',s),
        (68,f'do you know what {s} requires',2,'require',s),
        (69,f'do you know if {s} requires water',2,'require',s),
        (70,f'es {s} clasea',1,'definition',s),
        (71,f'is the {s} a clasea',2,'definition',s),
        (72,f'does {s} require water',2,'require',s),
        (73,'y qué requiere',1,'require',s),
        (74,'qué requiere eso',1,'require',s),
        (75,'what does it require',2,'require',s),
        (76,'and what does it require',2,'require',s),
        (77,'y requiere agua',1,'require',s),
        (78,'eso requiere agua',1,'require',s),
        (79,'does it require water',2,'require',s),
        (80,'and does it require water',2,'require',s),
        (81,f'y {other}',1,'other',other),
        (82,f'y el {other}',1,'other',other),
        (83,f'what about {other}',2,'other',other),
        (84,f'and {other}',2,'other',other),
        (85,'y qué es',1,'definition',s),
        (86,'qué es eso',1,'definition',s),
        (87,'what is it',2,'definition',s),
        (88,'and what is it',2,'definition',s),
        (89,f'me explicas qué requiere {s}',1,'require',s),
        (90,f'please explain what {s} requires',2,'require',s),
        (91,f'me dices si {s} requiere agua',1,'require',s),
        (92,f'please tell me whether {s} requires water',2,'require',s),
        (93,'entonces qué requiere',1,'require',s),
        (94,'then what does it require',2,'require',s),
        (95,'entonces requiere agua',1,'require',s),
        (96,'then does it require water',2,'require',s),
    ]


CONTEXT_IDS=set(range(73,89))|set(range(93,97))


def smoke(e,binary,learned):
    with Session(binary,e.state,e.program) as session:
        e.lesson('aprende que neral es clasea',session=session)
        for q,lang,kind in [('sabes qué requiere neral',1,'require'),
                            ('y qué requiere',1,'require'),
                            ('what is it',2,'definition')]:
            answer=spoken('neral',lang,kind)
            e.check(q,answer,lang,session=session)
            print('E019_PASS',q,'->',answer,flush=True)
        e.check('hola',e017.conversation.ACTS[1,1],session=session)
        # Native dialogue context was invalidated by this unrelated turn.
        e.check('y qué requiere',CLARIFY[1],session=session)
    e.state.write_bytes(learned)


def controls(e,binary,learned):
    # No promotion from repeated identical predicate-only demonstrations.
    a=U+10000+72*96
    e.run(stores([(a+i,0) for i in range(96)]))
    for _ in range(4):e.pattern(73,9,0,25,0,0,1,'y qué necesita')
    assert snapshot(e.state)[1].get(a+2,0)==0
    e.pattern(73,9,0,28,0,0,1,'y qué utiliza')
    assert snapshot(e.state)[1][a+2]==1
    e.state.write_bytes(learned)
    e.pattern(97,1,5,23,0,0,1,'qué es gato',reject=True)
    e.pattern(96,13,0,25,110,0,2,'then does it need water',reject=True)
    with Session(binary,e.state,e.program) as session:
        e.check('what does it require?',CLARIFY[2],2,session=session)
        e.check('sabes si noexiste requiere agua?',SURFACE[4,1],session=session)
        e.check('entonces qué requiere?',CLARIFY[1],session=session)
        e.check('aprende que noborrar es mamífero?',SURFACE[4,1],session=session)
        assert 'noborrar' not in e017.names(e)
        # An unanswered delegated old query cannot leave a usable referent.
        e.check('gato utiliza filosofía?',e017.conversation.ACTS[3,1],session=session)
        e.check('y qué requiere?',CLARIFY[1],session=session)
        # Read-only evidence search distinguishes negative from missing truth.
        e.lesson('aprende que neral es clasea',session=session)
        e.lesson('aprende que neral no es ave',session=session)
        e.check('neral es ave?',SURFACE[8,1]+' Neral no es un ave.',session=session)
        e.check('y qué requiere?',spoken('neral',1),session=session)
        e.lesson('aprende que neral no requiere agua',session=session)
        # An explicit exception blocks a general inherited consequence.
        e.check('sabes si neral requiere agua?',SURFACE[8,1]+' Neral no requiere agua.',session=session)
        e.lesson('aprende que neral requiere agua',session=session)
        e.check('sabes si neral requiere agua?',SURFACE[5,1],session=session)
        e.check('what is it?',CLARIFY[2],2,session=session)
        e.check('olvida que neral requiere agua',SURFACE[3,1],session=session,readonly=False)
        e.check('neral requiere agua?',spoken('neral',1),session=session)
        # An ambiguous multi-referent form is never reduced to one name.
        e.check('y neral y gato',e017.conversation.ACTS[3,1],session=session)
        e.check('qué es eso?',CLARIFY[1],session=session)
    e.state.write_bytes(learned)
    # Previous number/account continuations retain their established owner.
    with Session(binary,e.state,e.program) as session:
        for q,a in [('ana tiene dos manzanas','Ana tiene dos manzanas.'),
                    ('luis tiene tres manzanas','Luis tiene tres manzanas.'),
                    ('ella recibe dos más',e017.conversation.ACTS[4,1]),
                    ('cuántas manzanas tiene ana','Ana tiene dos manzanas.'),
                    ('y luis','Luis tiene tres manzanas.')]:
            e.check(q,a,session=session,readonly=False)
    e.state.write_bytes(learned)
    print('E019_QUERY_INTENT_TOPIC_CHANGES_AMBIGUITY_AND_BOUNDS_PASS',flush=True)


def novel_dialogues(e,binary,learned,cases):
    before=e.checks;timings=[];covered=set()
    with Session(binary,e.state,e.program) as session:
        for i in range(cases):
            s=f'foco{i:03d}';other=f'cambio{i:03d}';goal=f'meta{i:03d}'
            e.lesson(f'aprende que {s} es clasea',session=session)
            e.lesson(f'aprende que {other} es claseb',session=session)
            for pid,q,language,kind,subject in forms(s,other):
                if pid in CONTEXT_IDS:
                    e.check(s+' requiere agua?',spoken(s,1),session=session)
                e.check(q,spoken(subject,language,kind),language,session=session)
                timings.append(e.times[-1]);covered.add(pid)
            # A continuous conversation changes both subject and relation,
            # with no explicit complete question between its continuations.
            e.check(s+' requiere agua?',spoken(s,1),session=session)
            e.check('y '+other,spoken(other,1,'other'),session=session)
            e.check('what is it',SURFACE[8,2]+f' {other.capitalize()} is claseb.',2,session=session)
            e.check('what about '+s,spoken(s,2,'definition'),2,session=session)
            e.check('entonces qué requiere',spoken(s,1),session=session)
            # Transitivity uses freshly supplied edges, not a supplied result.
            e.lesson(f'aprende que {s} alcanza {other}',session=session)
            e.lesson(f'aprende que {other} alcanza {goal}',session=session)
            e.check(f'do you know if {s} reaches {goal}',spoken(s,2,'reach',goal),2,session=session)
            e.check(f'and does it reach {goal}',spoken(s,2,'reach',goal),2,session=session)
            why=SURFACE[9,2]+f' {s.capitalize()} reaches {goal}. [{s} --reaches--> {other} --reaches--> {goal}]'
            e.check('why?',why,2,session=session)
            e.check('then what does it reach',SURFACE[8,2]+f' {s.capitalize()} reaches {other} and {goal}.',2,session=session)
            # A question with a teaching marker is still a question.
            e.check(f'aprende que {s} requiere energía?',SURFACE[4,1],session=session)
            e.check('then what does it require?',CLARIFY[2],2,session=session)
            if i%8==0:print('E019_NOVEL_PROGRESS',i+1,flush=True)
        metrics=session.metrics();rss=session.rss_kib()
    assert covered==set(range(65,97)),covered
    e017.audit(e);e.state.write_bytes(learned)
    print('E019_ALL_32_NEW_CONSTRUCTIONS_TRANSFER_PASS',cases,flush=True)
    return {'novel_dialogues':cases,'new_query_problems':32*cases,
            'novel_dialogue_checks':e.checks-before,'new_constructions_examined':sorted(covered),
            'native_query_ms':{'median':statistics.median(timings),
                'p95':sorted(timings)[max(0,(len(timings)*95+99)//100-1)]},
            'novel_session_metrics':metrics,'resident_rss_kib':rss}


def restart_and_reset(e,binary,learned):
    with Session(binary,e.state,e.program) as session:
        e.lesson('aprende que retenta901 es clasea',session=session)
        e.check('sabes qué requiere retenta901',spoken('retenta901',1),session=session)
    with Session(binary,e.state,e.program) as session:
        e.check('then what does it require',spoken('retenta901',2),2,session=session)
        e.check('what is it',spoken('retenta901',2,'definition'),2,session=session)
    e.run((ROOT.parent/'stories/reset-episode.xi').read_text())
    with Session(binary,e.state,e.program) as session:
        e.check('qué es eso',CLARIFY[1],session=session)
        e.check('sabes qué requiere retenta901',spoken('retenta901',1),session=session)
    e.state.write_bytes(learned)
    print('E019_CONTEXT_RESTART_AND_RESET_PASS',flush=True)


def diagnostic(e,binary,learned):
    transcript=[];score={}
    for stage,seed in [('before',e.parent.read_bytes()),('after',learned)]:
        e.state.write_bytes(seed);correct=0
        with Session(binary,e.state,e.program) as session:
            session.request('aprende que sondera es clasea')
            session.request('aprende que alterna es claseb')
            for pid,q,language,kind,subject in forms('sondera','alterna'):
                if pid in CONTEXT_IDS:session.request('sondera requiere agua?')
                raw,ms=session.request(q,language);out=decode_result(raw)
                expected=spoken(subject,language,kind);passed=out==expected;correct+=passed
                transcript.append({'stage':stage,'construction':pid,'input':q,'language':language,
                                   'output':out,'expected':expected,'pass':passed,'ms':ms})
        score[stage]={'correct':correct,'total':32}
    e.state.write_bytes(learned)
    return {'scope':'32 fixed probes; unseen entities and require predicate; not a general-language score',
            'score':score,'transcript':transcript}


def main():
    p=argparse.ArgumentParser();p.add_argument('runtime');p.add_argument('session_binary');p.add_argument('parent')
    p.add_argument('--out',default='evidence/e019');p.add_argument('--smoke',action='store_true')
    p.add_argument('--dialogs',type=int,default=32);args=p.parse_args()
    e=Examiner(args.runtime,args.parent,args.out);binary=Path(args.session_binary).resolve()
    learned,seconds=train(e);(e.out/CHECKPOINT).write_bytes(learned)
    print('TRAINED_E019',hashlib.sha256(learned).hexdigest(),len(learned),'SECONDS',seconds,flush=True)
    smoke(e,binary,learned)
    if args.smoke:return
    controls(e,binary,learned)
    report=novel_dialogues(e,binary,learned,args.dialogs)
    restart_and_reset(e,binary,learned)
    # Reuse the complete E018 prior semantic exams, clients, persistence and
    # rollback checks against the newly continued checkpoint.
    e018.controls(e,binary,learned)
    report['e018_novel_regression']=e018.novel_dialogues(e,binary,learned,20)
    e018.interfaces_and_rollback(e,binary,learned)
    e018.retention(e,binary,learned)
    diag=diagnostic(e,binary,learned);e017.audit(e)
    memory=snapshot(e.state)[1]
    report.update({'stage':'E019','parent_sha256':PARENT_SHA,
        'learned_sha256':hashlib.sha256(learned).hexdigest(),'checkpoint_bytes':len(learned),
        'training_seconds':seconds,'checks':e.checks,'total_constructions':96,
        'new_constructions':32,'syntax_presentations':len(e017.rows('e019-constructions.psv')),
        'new_lexical_entries':len(e017.rows('e019-words.psv')),
        'total_lexical_entries':471+e017.u16(memory,U+6),'new_world_assertions_in_release':0,
        'inherited_didactic_assertions':e017.u16(memory,U+8),'old_training_replayed':False,
        'previous_learned_records_unchanged':True,'declared_header_updates_only':True,
        'old_1522_cases_both_surfaces':True,'diagnostic_score':diag['score'],
        'context':'one supported factual subject/predicate; explicit subject switching; no general coreference',
        'limits':{'constructions':96,'tokens':15,'input_bytes':255,'search_nodes':64,'proof_nodes':32,'answers':8},
        'intelligence':'XI only; same RVPC2 and unchanged pinned owner runtime',
        'open_conversation_achieved':False,'no_reverse_os_integration':True})
    for name,data in [('results.json',report),('diagnostic.json',diag)]:
        (e.out/name).write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')
    (e.out/'raw.jsonl').write_text(''.join(json.dumps(row,ensure_ascii=False)+'\n' for row in e.transcript))
    print(json.dumps(report,ensure_ascii=False,indent=2),flush=True)


if __name__=='__main__':main()
