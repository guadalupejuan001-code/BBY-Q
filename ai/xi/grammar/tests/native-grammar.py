#!/usr/bin/env python3
"""Continue E014 from labeled language examples; examine withheld referents.

Python supplies demonstrations and an independent oracle. BBY Q receives only
raw question bytes at inference; XI induces and matches every structural slot.
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

ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT.parents[2]
G, K, W = 7600000000000000000, 7400000000000000000, 7500000000000000000
PARENT_SHA = 'c3b732c4d704c21d1d0f99b0f774840de1ab66281813c5664a920d580fdf27b5'
spec = importlib.util.spec_from_file_location('stories', ROOT.parent/'stories/tests/native-stories.py')
stories = importlib.util.module_from_spec(spec)
spec.loader.exec_module(stories)
snapshot, frame, stores = stories.snapshot, stories.frame, stories.stores
Session, decode_result = stories.Session, stories.decode_result


def rows(name):
    return [line.split('|') for line in (ROOT/'data'/name).read_text().splitlines()
            if line and not line.startswith('#')]


class Examiner(stories.Examiner):
    def __init__(self, runtime, parent, out):
        self.runtime = str(Path(runtime).resolve())
        self.parent = Path(parent).resolve()
        assert hashlib.sha256(self.parent.read_bytes()).hexdigest() == PARENT_SHA
        self.original = snapshot(self.parent)
        self.out = Path(out).resolve()
        self.out.mkdir(parents=True, exist_ok=True)
        self.state, self.next = self.out/'state.rvp', self.out/'next.rvp'
        self.event = self.out/'event.xi'
        self.state.write_bytes(self.parent.read_bytes())
        def linked(mode):
            return subprocess.check_output(['bash', str(ROOT.parent/'knowledge/link.sh'), mode], text=True).split('\n', 1)[1]
        self.combined, self.word_program, self.teach_program = [linked(m) for m in ('combined', 'word', 'pattern')]
        self.program = self.out/'combined.xi'
        self.program.write_text('#!reverse-pc-machine-v1\n'+self.combined)
        self.transcript, self.times, self.checks = [], [], 0

    def grammar(self, name, reject=False):
        return self.run((ROOT/name).read_text(), reject=reject)

    def teach(self, actor, item, verb, text, reject=False):
        fields = [(G+16, 1), (G+17, actor), (G+18, item), (G+19, verb)]
        self.run(frame(text)+stores(fields).split('\n', 1)[1]+self.teach_program, reject=reject)

    def unsupported(self, text, session):
        # Unrecognized language retains E011's preexisting behavior: an
        # arithmetic fallback failure invalidates the old numeric continuation.
        # Learned arithmetic bytes and every episode account must still survive.
        def fixed():
            core, memory, bindings = stories.immutable(self.state)
            return core, {a:b for a,b in memory.items() if not stories.D <= a < stories.D+16}, bindings
        before = fixed(), stories.ledger(snapshot(self.state)[1])
        raw, elapsed = session.request(text)
        assert decode_result(raw) == '?', (text, decode_result(raw))
        assert (fixed(), stories.ledger(snapshot(self.state)[1])) == before
        memory = snapshot(self.state)[1]
        assert not any(memory.get(G+i,0) for i in range(4,192))
        self.transcript.append({'input':text if isinstance(text,str) else repr(text), 'output':'?', 'ms':elapsed})
        self.checks += 1


TEMPLATES = [
    'how many {item} does {actor} have?', 'how many {item} has {actor}?',
    'how many {item} does {actor} have now?', 'how many {item} has {actor} now?',
    '{actor} has how many {item}?', '{actor} tiene cuántas {item}?',
    'cuántas {item} le quedan a {actor}?', 'cuántas {item} tiene ahora {actor}?',
    'cuántas {item} tiene {actor} ahora?',
]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('runtime'); ap.add_argument('session_binary'); ap.add_argument('parent')
    ap.add_argument('--out', default='evidence/e015'); ap.add_argument('--cases', type=int, default=720)
    args = ap.parse_args()
    binary = Path(args.session_binary).resolve()
    e = Examiner(args.runtime, args.parent, args.out)
    # Same code, no new lexicon or grammar: all new held-out formulations fail.
    baseline = []
    with Session(binary, e.state, e.program) as session:
        e.check('ana tiene cinco manzanas', 'cinco', session=session)
        for template in TEMPLATES:
            text = template.format(actor='ana', item='manzanas' if 'cuántas' in template else 'apples')
            raw, _ = session.request(text)
            baseline.append({'input': text, 'output': decode_result(raw)})
    assert all(x['output'] == '?' for x in baseline)
    e.state.write_bytes(e.parent.read_bytes())
    e.grammar('birth.xi')
    e.grammar('birth.xi', reject=True)
    for cid, kind, lang, word in rows('words-v1.psv'):
        e.word(int(cid), int(kind), int(lang), word)
    untrained = e.state.read_bytes()
    # Lexicon alone cannot answer the new structures.
    with Session(binary, e.state, e.program) as session:
        e.check('eva tiene siete libros', 'siete', session=session)
        for template in TEMPLATES:
            text = template.format(actor='eva', item='libros' if 'cuántas' in template else 'books')
            e.unsupported(text, session)
    e.state.write_bytes(untrained)
    demos = [(int(a), int(i), int(v), t) for a, i, v, t in rows('demonstrations-v1.psv')]
    for _ in range(5):
        e.teach(*demos[0])
    memory = snapshot(e.state)[1]
    assert memory.get(G+3, 0) == 1 and not memory.get(G+1001, 0)
    # A second example with the same object still fails the variation gate.
    e.teach(205, 208, 24, 'how many apples does luis have?')
    assert not snapshot(e.state)[1].get(G+1001, 0)
    with Session(binary, e.state, e.program) as session:
        e.check('eva tiene siete libros', 'siete', session=session)
        e.unsupported('how many books does eva have?', session)
    # Restore the clean untrained state: exam accounts are never published.
    e.state.write_bytes(untrained)
    for demo in demos:
        e.teach(*demo)
    learned = e.state.read_bytes()
    release = e.out/'BBYQ_E015_Grammar_ES_EN.rvp'
    release.write_bytes(learned)
    reference = stories.immutable(e.state)
    core, memory, bindings = snapshot(e.state)
    assert core == e.original[0] and bindings == e.original[2]
    assert memory[G+3] == len(TEMPLATES)
    assert all(memory[G+1001+i*64] == 1 for i in range(len(TEMPLATES)))
    assert not stories.ledger(memory)
    # Exact retention outside the new region and appended lexical records.
    old = e.original[1]
    count_before = stories.u16(old, K+4)
    count_after = stories.u16(memory, K+4)
    assert count_after == count_before+len(rows('words-v1.psv'))
    mutable = {K+4, K+5}
    appended = set(range(K+10000+count_before*40, K+10000+count_after*40))
    roles = {K+6000+int(r[0]) for r in rows('words-v1.psv') if K+6000+int(r[0]) not in old}
    exclude = mutable | appended | roles
    assert {a:b for a,b in memory.items() if not G <= a < G+2024 and a not in exclude} == {
        a:b for a,b in old.items() if a not in exclude}, 'earlier learned byte changed'
    e.audit(); e.grammar('audit.xi')
    print('GRAMMAR_INDUCTION_VARIATION_GATE_AND_EXACT_RETENTION_PASS', flush=True)

    # No example uses Eva, Tom, books, balls or gato/roca. The oracle selects
    # independent episode counts. Neither counts nor expected answers enter
    # the pattern teacher. 720 fresh questions span all nine structures.
    rng = random.Random(150627)
    times = []
    queries = []
    people = [('eva',206), ('tom',207)]
    objects = [('libros','books',210), ('pelotas','balls',211)]
    with Session(binary, e.state, e.program) as session:
        for actor, aid in people:
            for es, en, iid in objects:
                n = rng.randint(10, 60000)
                e.check(f'{actor} tiene {n} {es}', str(n), session=session, reference=reference)
        for i in range(args.cases):
            actor, aid = rng.choice(people)
            es, en, iid = rng.choice(objects)
            n = rng.randint(0,65535)
            e.check(f'{actor} tiene {n} {es}', stories.number(n,1), session=session, reference=reference)
            template = TEMPLATES[i % len(TEMPLATES)]
            text = template.format(actor=actor, item=rng.choice([es,en]))
            if i % 3 == 0:
                text = ' \t '.join(text.split()).upper()
            if i % 7 == 0:
                text = '¿'+text
            language = rng.choice([1,2])
            before = stories.ledger(snapshot(e.state)[1])
            e.check(text, stories.number(n,language), language, session=session, reference=reference)
            assert stories.ledger(snapshot(e.state)[1]) == before
            times.append(e.times[-1]); queries.append(text)
        rss = session.metrics()
    assert len(set(queries)) >= min(args.cases, 60)
    print('WITHHELD_REFERENTS_AND_NEW_FORMULATIONS_PASS', args.cases, flush=True)

    # Continued learning from language must leave actions, unknowns and
    # arithmetic context safe. Interrogatives never create an unknown account.
    failures = ['how many apples does ana have?', 'how many books does eva lose?',
                'how many books does unknown have?', 'how many spaceships does eva have?',
                'how books many does eva have?', 'how many books does eva have extra?',
                'how many books does eva have now now?', 'how many books does eva not have?',
                'how many books does eva have??', 'how many books does seven have?',
                'cuántas libros le quedan a desconocido?', 'cuántas libros no tiene eva?',
                'cuántas libros le quedan a eva extra?', 'cuántas libros recibe eva ahora?',
                'cuántas libros tiene 7 ahora?', 'how many books do eva have?',
                'how many books does eva have and tom has two balls?',
                'how many books does eva have and receives two books',
                b'how many books does eva have\xc3', b'\xffhow many books does eva have?']
    with Session(binary, e.state, e.program) as session:
        before = stories.ledger(snapshot(e.state)[1])
        for text in failures:
            e.unsupported(text, session)
            assert stories.ledger(snapshot(e.state)[1]) == before
    # Restore only the numeric conversation descriptors for the following
    # isolation checks; this is examiner setup, not learning or inference.
    e.run(stores([(stories.D+i,e.original[1].get(stories.D+i,0)) for i in range(16)]))
    with Session(binary, e.state, e.program) as session:
        e.check('gato tiene dos roca y recibe tres roca', 'cinco', session=session, reference=reference)
        e.check('how many roca does gato have?', 'five', 2, session=session, reference=reference)
        e.check('cuántos roca tiene gato ahora?', 'cinco', session=session, reference=reference)
        # Genuine follow-up to new actions and process restart.
        e.check('eva tiene ocho libros y pierde tres libros', 'cinco', session=session, reference=reference)
    with Session(binary, e.state, e.program) as session:
        e.check('how many books does eva have now?', 'five', 2, session=session, reference=reference)
        e.check('cuántos libros le quedan a eva?', 'cinco', session=session, reference=reference)
    e.audit(); e.grammar('audit.xi')
    print('UNKNOWN_NEGATION_MALFORMED_ACTIONS_AND_RESTART_PASS', flush=True)

    # The same code abstains when the grammar region is not learned. Also
    # conflicting learned interpretations must abstain, never pick a template.
    e.state.write_bytes(learned)
    e.teach(204, 204, 24, 'how many apples does ana have?', reject=True)
    e.teach(204, 208, 198, 'how many apples does ana have?', reject=True)
    e.teach(204, 208, 24, 'how many unknown does ana have?', reject=True)
    e.teach(204, 208, 24, 'how many apples does ana have ana?', reject=True)
    # Deliberately teach the inverted semantic labeling in another copy; two
    # structural patterns now both match but disagree on the pair to retrieve.
    e.teach(208, 204, 24, demos[0][3])
    e.teach(209, 205, 24, demos[1][3])
    with Session(binary, e.state, e.program) as session:
        e.check('eva tiene cinco libros', 'cinco', session=session)
        e.unsupported('how many books does eva have?', session)
        assert stories.ledger(snapshot(e.state)[1]) == {(206,210):5}
    e.state.write_bytes(learned)
    print('INVALID_TEACHING_AND_AMBIGUOUS_STRUCTURES_ABSTAIN_PASS', flush=True)

    # Read-only audit rejects a corrupt slot; file and loaded state unchanged.
    e.run(stores([(G+1008, 9)]))
    e.grammar('audit.xi', reject=True)
    e.state.write_bytes(learned)
    # E014's transactional failure controls also run through the E015 matcher.
    with Session(binary, e.state, e.program) as session:
        e.check('ana tiene cinco manzanas', 'cinco', session=session, reference=reference)
    stories.transaction_controls(e, binary, reference)
    e.state.write_bytes(learned)
    print('POST_UPDATE_SAVE_AND_XI_FAILURE_ROLLBACK_PASS', flush=True)

    # Exact legacy curriculum, factual/relational routing and arithmetic on the
    # NEW learner, without replaying any old teaching.
    with Session(binary, e.state, e.program) as session:
        for text, answer, lang in stories.retained_curriculum():
            e.check(text, answer, lang, session=session, reference=reference)
        for text, answer in [('cuarto contiene llave?', 'cuarto contiene llave (via caja).'),
                             ('luz toca bolsa?', 'no: luz toca bolsa.'),
                             ('bbyq tiene conciencia?', '?')]:
            e.check(text, answer, session=session, reference=reference)
        assert decode_result(session.request('dos mas tres')[0]) == 'cinco'
        e.check('ana tiene dos manzanas y recibe tres manzanas', 'cinco', session=session)
        e.check('how many apples does ana have?', 'cinco', session=session)
        assert decode_result(session.request('minus one',2)[0]) == 'four'
    e.audit(); e.grammar('audit.xi')
    print('FULL_1522_CURRICULUM_AND_ARITHMETIC_CONTINUITY_PASS', flush=True)

    # CLI source cache includes the newly added grammar.
    fixture = e.out/'cache-fixture'
    shutil.copytree(REPO/'ai/xi', fixture/'xi')
    state = fixture/'state.rvp';state.write_bytes(learned)
    cli = ['bash',str(fixture/'xi/knowledge/text.sh'), e.runtime,str(state)]
    assert subprocess.check_output(cli+['ana tiene cinco manzanas','es'],text=True) == 'cinco\n'
    assert subprocess.check_output(cli+['how many apples does ana have?','es'],text=True) == 'cinco\n'
    matcher = fixture/'xi/grammar/match.xi'
    matcher.write_text('#!reverse-pc-machine-v1\nhalt\n')
    assert subprocess.check_output(cli+['how many apples does ana have?','es'],text=True) == '?\n'
    assert len(list((fixture/'.bbyq-xi-cache').glob('*.xi'))) == 2
    e.state.write_bytes(learned)
    report = {
        'stage':'E015','parent_sha256':PARENT_SHA,
        'learned_sha256':hashlib.sha256(learned).hexdigest(),'checkpoint_bytes':len(learned),
        'new_lexical_entries':len(rows('words-v1.psv')),'total_lexical_entries':count_after,
        'distinct_demonstrations':len(demos),'enabled_patterns':len(TEMPLATES),
        'baseline_new_formulations_correct':0,'baseline_new_formulations_total':len(TEMPLATES),
        'baseline':baseline,'novel_questions':args.cases,'distinct_question_texts':len(set(queries)),
        'fresh_quantity_contexts':args.cases,'question_seed':150627,
        'training_referents':{'actors':['ana','luis'],'items':['manzanas/apples','peras/pears']},
        'exam_referents':{'actors':['eva','tom'],'items':['libros/books','pelotas/balls']},
        'question_ms':{'median':statistics.median(times),'p95':sorted(times)[max(0,(len(times)*95+99)//100-1)]},
        'session_metrics':rss,'prior_curriculum_questions_on_new_checkpoint':1522,
        'failure_controls':len(failures),'old_knowledge_unchanged':True,
        'repeated_examples_do_not_promote':True,'lexicon_without_grammar_abstains':True,
        'both_referents_must_vary':True,'conflicting_structures_abstain':True,
        'invalid_teaching_rejected':True,'grammar_source_cache_invalidated':True,
        'save_and_post_update_xi_failure_rollback':True,'checks':e.checks,
        'empty_episode_ledger_in_release':True,'old_training_replayed':False,
        'intelligence':'XI only, same E014 ledger and E011 arithmetic/speaker',
        'limits':{'patterns':16,'tokens':15,'input_bytes':255,'open_grammar':False},
        'platform':sys.platform,'no_reverse_os_integration':True,
    }
    (e.out/'results.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    (e.out/'raw.jsonl').write_text(''.join(json.dumps(x,ensure_ascii=False)+'\n' for x in e.transcript))
    print(json.dumps(report,ensure_ascii=False,indent=2),flush=True)


if __name__ == '__main__':
    main()
