#!/usr/bin/env python3
"""Teach observed consequences; independently examine novel fictional stories.

Only raw text and language reach query XI. All expected counts/answers live
here, outside the learner. Python never chooses an answer for BBY Q.
"""
import argparse
from collections import defaultdict, deque
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

ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT.parents[2]
K, D, W = 7400000000000000000, 7300000000000000000, 7500000000000000000
PARENT_SHA = '8961833bb7140d7b63494dbd96ff02136559fd25eeca5a51f65fe3148131844f'
spec = importlib.util.spec_from_file_location('knowledge', ROOT.parent/'knowledge/tests/native-knowledge.py')
knowledge = importlib.util.module_from_spec(spec)
spec.loader.exec_module(knowledge)
snapshot = knowledge.snapshot
sys.path.insert(0, str(REPO/'ai/native'))
from session_client import Session, decode_result


def rows(name):
    return [x.split('|') for x in (ROOT/'data'/name).read_text().splitlines()
            if x and not x.startswith('#')]


def stores(fields):
    return '#!reverse-pc-machine-v1\n' + ''.join(f'store8 {a} {b}\n' for a, b in fields)


def frame(text, language=1):
    raw = text.encode() if isinstance(text, str) else text
    assert len(raw) <= 255
    return stores([(K+16, 1), (K+17, len(raw)), (K+3, language)] +
                  [(K+128+i, b) for i, b in enumerate(raw)])


def u16(memory, address):
    return memory.get(address, 0) + 256*memory.get(address+1, 0)


def ledger(memory):
    result = {}
    for i in range(memory.get(W+6, 0)):
        a = W+1000+i*8
        key = memory.get(a, 0), memory.get(a+1, 0)
        assert all(key) and key not in result
        result[key] = u16(memory, a+2)
        assert not any(memory.get(a+j, 0) for j in range(4, 8))
    return result


def immutable(path):
    core, memory, bindings = snapshot(path)
    transient = {K+3, *range(K+8, K+16), *range(K+2100, K+2108),
                 *range(K+2200, K+2232), *range(W+8, W+16), W+6,
                 *range(W+1000, W+1128)}
    return core, {a: b for a, b in memory.items() if a not in transient}, bindings


class Examiner:
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
        self.combined = subprocess.check_output(['bash', str(ROOT.parent/'knowledge/link.sh'), 'combined'], text=True).split('\n', 1)[1]
        self.word_program = subprocess.check_output(['bash', str(ROOT.parent/'knowledge/link.sh'), 'word'], text=True).split('\n', 1)[1]
        self.program = self.out/'combined.xi'
        self.program.write_text('#!reverse-pc-machine-v1\n'+self.combined)
        self.transcript, self.times = [], []
        self.checks = 0

    def run(self, program, reject=False):
        self.event.write_text(program)
        self.next.unlink(missing_ok=True)
        before = self.state.read_bytes()
        p = subprocess.run([self.runtime, 'run', str(self.event), str(self.state), str(self.next)],
                           capture_output=True, text=True, timeout=30)
        if reject:
            assert p.returncode != 0, 'invalid lesson accepted'
            assert not self.next.exists() and self.state.read_bytes() == before
            self.checks += 1
            return ''
        assert p.returncode == 0, p.stderr
        self.next.replace(self.state)
        self.checks += 1
        return p.stdout

    def module(self, name):
        return (ROOT/name).read_text().split('\n', 1)[1]

    def word(self, cid, kind, language, text):
        self.run(frame(text, language) + stores([(K+24, 1), (K+25, cid), (K+26, kind), (K+27, language)]).split('\n', 1)[1] + self.word_program)

    def effect(self, verb, before, amount, after, reject=False):
        fields = [(W+16, 1), (W+17, verb)]
        for i, n in enumerate((before, amount, after)):
            fields += [(W+18+2*i, n % 256), (W+19+2*i, n // 256)]
        self.run(stores(fields)+self.module('learn-effect.xi'), reject=reject)

    def marker(self, role, concept, reject=False):
        self.run(stores([(W+16, 2), (W+17, role), (W+18, concept)])+
                 self.module('learn-marker.xi'), reject=reject)

    def check(self, text, expected, language=1, session=None, reference=None):
        old = snapshot(self.state)[1]
        arithmetic_before = {a: b for a, b in old.items() if D <= a < D+10_000}
        started = time.perf_counter_ns()
        if session:
            raw, elapsed = session.request(text, language)
        else:
            raw = self.run(frame(text, language)+self.combined)
            elapsed = (time.perf_counter_ns()-started)/1e6
        spoken = decode_result(raw)
        assert spoken == expected, (text, spoken, expected)
        core, memory, bindings = snapshot(self.state)
        assert core == self.original[0] and bindings == self.original[2]
        assert not any(memory.get(K+i, 0) for i in [*range(16, 2048), *range(3000, 4500)])
        assert not any(memory.get(W+i, 0) for i in [*range(16, 64), *range(2000, 2216)])
        arithmetic_after = {a: b for a, b in memory.items() if D <= a < D+10_000}
        assert arithmetic_after == arithmetic_before, 'story changed prior arithmetic context'
        if reference is not None:
            assert immutable(self.state) == reference, 'query changed learned knowledge'
        self.transcript.append({'input': text if isinstance(text, str) else repr(text),
                                'language': language, 'output': spoken, 'ms': elapsed,
                                'mode': memory.get(K+13, 0), 'story_reason': memory.get(W+9, 0)})
        self.times.append(elapsed)
        self.checks += 1
        return memory

    def audit(self):
        for name in ['ai/xi/e008/audit-organism.xi', 'ai/xi/language/audit.xi',
                     'ai/xi/school/audit.xi', 'ai/xi/dialogue/audit.xi',
                     'ai/xi/knowledge/audit.xi', 'ai/xi/stories/audit.xi']:
            before = self.state.read_bytes()
            self.run((REPO/name).read_text())
            assert self.state.read_bytes() == before


ES = ['cero', 'uno', 'dos', 'tres', 'cuatro', 'cinco', 'seis', 'siete', 'ocho', 'nueve']
EN = ['zero', 'one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine']


def number(n, language):
    return (ES if language == 1 else EN)[n] if n < 10 else str(n)


def retained_curriculum():
    """Independent old-curriculum oracle, applied to the NEW checkpoint."""
    names, aliases = {}, defaultdict(list)
    for line in (ROOT.parent/'school/data/observations-v1.psv').read_text().splitlines():
        if not line or line.startswith('#'):
            continue
        *_, es, en = line.split('|')
        cid = len(names)+1
        names[cid] = {1: es, 2: en}
        aliases[cid] += [es, en]
    for cid, _, lang, word in knowledge.rows('words-v1.psv'):
        cid, lang = int(cid), int(lang)
        names.setdefault(cid, {}).setdefault(lang, word)
        aliases[cid].append(word)
    facts = {tuple(map(int, r[:3])): int(r[3]) for r in knowledge.rows('facts-v1.psv')}
    cases = []
    for (s, p, o), polarity in facts.items():
        for lang in (1, 2):
            triple = ' '.join(names[c][lang] for c in (s, p, o))
            cases.append((triple+'?', ('no: ' if polarity == 2 else '')+triple+'.', lang))
    edges, groups = defaultdict(list), defaultdict(list)
    for (s, p, o), polarity in facts.items():
        if polarity == 1:
            groups[s, p].append(o)
            if p == 23:
                edges[s].append(o)
    inferred = []
    for subject in sorted(edges):
        queue = deque([[subject]])
        visited = {subject}
        while queue:
            path = queue.popleft()
            for target in sorted(edges[path[-1]]):
                if target in visited:
                    continue
                visited.add(target)
                next_path = path+[target]
                queue.append(next_path)
                if len(next_path) >= 3 and (subject, 23, target) not in facts:
                    inferred.append((subject, 23, target, next_path))
    def answer(s, p, o, path, language):
        return ' '.join(names[c][language] for c in (s, p, o))+'. ['+' -> '.join(names[c][language] for c in path)+']'
    for s, p, o, path in inferred:
        for lang in (1, 2):
            cases.append((' '.join(names[c][lang] for c in (s, p, o))+'?', answer(s, p, o, path, lang), lang))
    for (s, p), objects in groups.items():
        for lang in (1, 2):
            question = f'{names[250][lang]} {names[p][lang]} {names[s][lang]}?'
            result = '; '.join(' '.join(names[c][lang] for c in (s, p, o)) for o in sorted(objects)[:8])+'.'
            cases.append((question, result, lang))
    for seed in (170627, 270629, 370631):
        rng = random.Random(seed)
        for _ in range(200):
            s, p, o, path = rng.choice(inferred)
            text = ' \t '.join(rng.choice(aliases[c]) for c in (s, p, o)).upper()+'?'
            if rng.choice((False, True)):
                text = '¿'+text
            lang = rng.choice((1, 2))
            cases.append((text, answer(s, p, o, path, lang), lang))
    assert len(cases) == 1522
    return cases


def transaction_controls(e, binary, reference):
    """Fail after candidate episode changes; recover the old loaded authority."""
    count = ledger(snapshot(e.state)[1])[204, 208]
    expected = number(count, 1)
    with Session(binary, e.state, e.program) as session:
        pending = Path(str(e.state)+'.pending')
        pending.mkdir()
        before = e.state.read_bytes()
        try:
            try:
                session.request('ana recibe siete manzanas y luis tiene tres peras')
                raise AssertionError('failed save was acknowledged')
            except RuntimeError as error:
                assert 'cannot write state' in str(error), error
            assert e.state.read_bytes() == before
        finally:
            pending.rmdir()
        e.check('cuántas manzanas tiene ana?', expected, session=session, reference=reference)
        assert ledger(snapshot(e.state)[1]) == {(204, 208): count}
    # Inject an exception after the full normal program, including its episode
    # update and cleanup. The exception is triggered only by the changed count.
    body = e.program.read_text()
    end = '\nlabel finish\nhalt\n'
    assert body.count(end) == 1
    failure = e.out/'failure-after-episode.xi'
    failure.write_text(body.replace(end, f'\nlabel finish\nload8 r0 {W+12}\ncmp r0 {(count+7)%256}\njne finish_ok\ndiv r0 0\nlabel finish_ok\nhalt\n'))
    with Session(binary, e.state, failure) as session:
        before = e.state.read_bytes()
        try:
            session.request('ana recibe siete manzanas')
            raise AssertionError('XI exception was acknowledged')
        except RuntimeError:
            pass
        assert e.state.read_bytes() == before
        e.check('cuántas manzanas tiene ana?', expected, session=session, reference=reference)
        assert ledger(snapshot(e.state)[1]) == {(204, 208): count}
    print('STORY_SAVE_AND_POST_UPDATE_XI_FAILURE_ROLLBACK_PASS', flush=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('runtime'); ap.add_argument('session_binary'); ap.add_argument('parent')
    ap.add_argument('--out', default='evidence/e014'); ap.add_argument('--stories', type=int, default=600)
    ap.add_argument('--turns', type=int, default=1000)
    args = ap.parse_args()
    e = Examiner(args.runtime, args.parent, args.out)
    e.run('#!reverse-pc-machine-v1\n'+e.module('birth.xi'))
    e.run('#!reverse-pc-machine-v1\n'+e.module('birth.xi'), reject=True)
    for cid, kind, language, text in rows('words-v1.psv'):
        e.word(int(cid), int(kind), int(language), text)
    e.marker(1, 212); e.marker(2, 213)
    e.marker(1, 213, reject=True); e.marker(0, 212, reject=True)
    e.marker(2, 208, reject=True)
    lessons = [tuple(map(int, r)) for r in rows('effects-v1.psv')]
    for _ in range(5):
        e.effect(*lessons[0])
    memory = snapshot(e.state)[1]
    assert memory[W+10000+24*24+1] == 1
    assert memory.get(W+10000+24*24+2, 0) == 0
    e.check('ana tiene dos manzanas', '?')
    for lesson in lessons[1:]:
        e.effect(*lesson)
    e.effect(198, 4, 3, 1, reject=True)
    e.effect(208, 4, 3, 7, reject=True)
    e.effect(0, 4, 3, 7, reject=True)
    # Release only taught capabilities. Do not ship fictional exam episodes or
    # their answers as learned facts. Restore the parent's output descriptors.
    parent_memory = e.original[1]
    output_fields = [K+3, *range(K+8, K+16), *range(K+2100, K+2108), *range(K+2200, K+2232)]
    e.run(stores([(a, parent_memory.get(a, 0)) for a in output_fields] + [(W+i, 0) for i in range(8, 16)]))
    learned = e.state.read_bytes()
    release = e.out/'BBYQ_E014_Quantity_Stories_ES_EN.rvp'
    release.write_bytes(learned)
    reference = immutable(e.state)
    core, memory, bindings = snapshot(e.state)
    # Earlier lexicon records, facts, evidence, operators, all core and bindings
    # must be unchanged. Only append lexical entries/roles and E014 memory.
    mutable = {K+4, K+5}
    appended = set(range(K+10000+374*40, K+10000+(374+len(rows('words-v1.psv')))*40))
    new_roles = {K+6000+int(r[0]) for r in rows('words-v1.psv')}
    assert {a: b for a, b in memory.items() if not W <= a < W+20_000 and a not in mutable|appended|new_roles} == {
        a: b for a, b in parent_memory.items() if a not in mutable|appended|new_roles}
    assert not ledger(memory)
    e.audit()
    print('LEARNING_DISTINCT_WITNESSES_AND_PARENT_RETENTION_PASS', flush=True)

    actors = [204, 205, 206, 207]
    items = [208, 209, 210, 211]
    aliases = {}
    for cid, _, lang, text in rows('words-v1.psv'):
        aliases.setdefault(int(cid), {}).setdefault(int(lang), []).append(text)
    aliases[24] = {1: ['tiene'], 2: ['has']}
    effects = {24: 'set', 198: 'add', 199: 'sub', 200: 'add', 201: 'sub', 202: 'add', 203: 'sub'}
    rng = random.Random(140627)
    expected_ledger = {}
    for i in range(args.stories):
        actor, item = rng.choice(actors), rng.choice(items)
        pair = actor, item
        parts = []
        for clause in range(rng.randint(1, 3)):
            verb = 24 if clause == 0 else rng.choice(list(effects))
            operation = effects[verb]
            old = expected_ledger.get(pair, 0)
            maximum = old if operation == 'sub' else min(65535-old, 999) if operation == 'add' else 65535
            amount = rng.randint(0, maximum)
            if rng.random() < .5:
                amount = min(amount, rng.randint(0, 9))
            new = amount if operation == 'set' else old+amount if operation == 'add' else old-amount
            words = []
            if clause:
                words += [rng.choice(['y', 'and'])]
            if clause == 0 or rng.choice([False, True]):
                words += [rng.choice(aliases[actor][rng.choice([1, 2])])]
            words += [rng.choice(aliases[verb][rng.choice([1, 2])]),
                      number(amount, rng.choice([1, 2])) if rng.choice([False, True]) else str(amount),
                      rng.choice(aliases[item][rng.choice([1, 2])])]
            parts += words
            expected_ledger[pair] = new
        language = rng.choice([1, 2])
        text = (' \t ' if i % 3 == 0 else ' ').join(parts)
        if i % 5 == 0:
            text = text.upper()
        memory = e.check(text, number(new, language), language, reference=reference)
        assert ledger(memory) == expected_ledger
        assert memory[K+13] == 4 and memory[W+14] == (len([x for x in parts if x in ['y', 'and']])+1)
        question = f'{rng.choice(aliases[212][language])} {rng.choice(aliases[item][language])} {aliases[24][language][0]} {aliases[actor][language][0]}?'
        if language == 1:
            question = '¿'+question
        memory = e.check(question, number(new, language), language, reference=reference)
        assert ledger(memory) == expected_ledger and memory.get(W+14, 0) == 0
        if i % 100 == 0:
            print('NOVEL_STORIES_PROGRESS', i+1, flush=True)
    print('NOVEL_STORIES_AND_REFERENTS_PASS', args.stories, flush=True)

    # Reach actual episode capacity even in a short smoke run.
    for actor in actors:
        for item in items:
            if (actor, item) not in ledger(snapshot(e.state)[1]):
                e.check(f'{aliases[actor][1][0]} tiene uno {aliases[item][1][0]}', 'uno', reference=reference)
    before = ledger(snapshot(e.state)[1])
    assert len(before) == 16
    failures = ['ana pierde 65535 manzanas y pierde 1 manzana',
                'ana tiene 65535 manzanas y recibe una manzana',
                'ana tiene dos manzanas y recibe tres palabras_desconocidas',
                'ana tiene dos manzanas and receives three apples trailing',
                'ana tiene dos manzanas y', 'ana tiene dos manzanas recibe tres manzanas',
                'ana recibe manzanas tres', 'ana tiene infinito manzanas',
                'ana tiene 65536 manzanas', 'ana tiene 999999999999999999 manzanas',
                'ana tiene dos uno', 'uno tiene dos manzanas',
                'cuántas manzanas recibe ana?', 'cuántas manzanas tiene desconocido?',
                'cuántas manzanas tiene gato?', 'gato recibe tres roca',
                'gato tiene tres roca', 'ana tiene dos manzanas??',
                'ana tiene dos manzanas?', 'ana recibe dos manzanas?',
                '¿ana tiene dos manzanas', 'ana no tiene dos manzanas',
                'ana tiene dos manzanas y luis tiene tres peras y eva tiene cuatro libros extra']
    for text in failures:
        memory = e.check(text, '?', reference=reference)
        assert ledger(memory) == before, ('partial/invalid story published', text)
    # Failed second/third clauses cannot publish an earlier valid assignment.
    text = 'ana tiene dos manzanas y recibe tres manzanas y pierde seis manzanas'
    memory = e.check(text, '?', reference=reference)
    assert ledger(memory) == before
    e.audit()
    print('ATOMIC_FAILURE_RANGE_GRAMMAR_AND_CAPACITY_PASS', flush=True)

    e.run('#!reverse-pc-machine-v1\n'+e.module('reset-episode.xi'))
    assert not ledger(snapshot(e.state)[1]) and immutable(e.state) == reference
    e.check('ana tiene dos manzanas y luis tiene tres manzanas y recibe cuatro manzanas', 'siete', reference=reference)
    assert ledger(snapshot(e.state)[1]) == {(204, 208): 2, (205, 208): 7}
    e.check('ana recibe una manzana', 'tres', reference=reference)
    e.check('cuántas manzanas tiene luis?', 'siete', reference=reference)
    e.check('ana tiene ocho peras y pierde tres peras', 'cinco', reference=reference)
    assert ledger(snapshot(e.state)[1]) == {(204, 208): 3, (205, 208): 7, (204, 209): 5}
    print('MULTI_ACTOR_ITEM_ISOLATION_AND_NEW_EPISODE_PASS', flush=True)

    # Control: exactly the same spelling/input has a different effect only when
    # the observed consequences in an isolated learner differ.
    e.state.write_bytes(learned)
    e.check('ana tiene ocho manzanas y zorp tres manzanas', 'cinco', reference=reference)
    e.run(stores([(W+10000+203*24+j, 0) for j in range(24)]))
    e.effect(203, 6, 2, 8); e.effect(203, 8, 3, 11)
    control_reference = immutable(e.state)
    e.check('ana tiene ocho manzanas y zorp tres manzanas', '11', reference=control_reference)
    e.state.write_bytes(learned)
    # Reuse existing E012 identities as actors/items without new role lessons.
    e.check('gato tiene dos roca y recibe tres roca', 'cinco', reference=reference)
    e.check('cuántas roca tiene gato?', 'cinco', reference=reference)
    e.audit()
    print('REVERSED_TEACHING_AND_OLD_CONCEPT_TRANSFER_PASS', flush=True)

    # Ambiguous zero-change observations cannot promote a verb, even with two
    # distinct witnesses. A later informative consequence resolves the family.
    e.state.write_bytes(learned)
    e.run(stores([(W+10000+203*24+j, 0) for j in range(24)]))
    e.effect(203, 5, 0, 5); e.effect(203, 8, 0, 8)
    ambiguous = snapshot(e.state)[1]
    assert ambiguous[W+10000+203*24] == 6
    assert ambiguous[W+10000+203*24+1] == 2
    assert ambiguous.get(W+10000+203*24+2, 0) == 0
    e.effect(203, 6, 2, 8)
    assert snapshot(e.state)[1][W+10000+203*24+2] == 2
    e.state.write_bytes(learned)
    print('AMBIGUOUS_CONSEQUENCES_REQUIRE_INFORMATIVE_EVIDENCE_PASS', flush=True)

    # Nonzero arithmetic continuation survives story success and failure.
    e.run(frame('dos mas tres')+e.combined)
    arithmetic_context = snapshot(e.state)[1]
    story_reference = immutable(e.state)
    e.check('ana tiene dos manzanas y recibe tres manzanas', 'cinco', reference=story_reference)
    e.check('ana tiene dos manzanas y pierde tres manzanas', '?', reference=story_reference)
    output = decode_result(e.run(frame('minus one', 2)+e.combined))
    assert output == 'four'
    assert u16(arithmetic_context, D+6) == 5
    e.state.write_bytes(learned)
    print('ARITHMETIC_CONTEXT_ISOLATION_PASS', flush=True)

    # The CLI source cache must include the new XI modules, not just E012.
    fixture = e.out/'cache-fixture'
    shutil.copytree(REPO/'ai/xi', fixture/'xi')
    cached = fixture/'state.rvp'; cached.write_bytes(learned)
    command = ['bash', str(fixture/'xi/knowledge/text.sh'), e.runtime, str(cached), 'ana tiene dos manzanas', 'es']
    p = subprocess.run(command, capture_output=True, text=True, timeout=30)
    assert p.returncode == 0 and p.stdout == 'dos\n', p.stderr
    renderer = fixture/'xi/stories/finish.xi'
    renderer.write_text(renderer.read_text().removesuffix('halt\n')+
                        f'store8 {D+10} 7\nstore8 {D+11} 0\nhalt\n')
    p = subprocess.run(command, capture_output=True, text=True, timeout=30)
    assert p.returncode == 0 and p.stdout == 'siete\n', (p.stdout, p.stderr)
    assert len(list((fixture/'.bbyq-xi-cache').glob('*.xi'))) == 2
    print('STORY_SOURCE_CACHE_INVALIDATION_PASS', flush=True)

    # Persist every turn before ACK, then restart and query the same episode.
    binary = Path(args.session_binary).resolve()
    residents = []
    session_times = []
    with Session(binary, e.state, e.program) as session:
        e.check('ana tiene 1000 manzanas', '1000', session=session, reference=reference)
        for i in range(args.turns):
            text, expected = ('ana recibe una manzana', '1001') if i % 2 == 0 else ('ana pierde una manzana', '1000')
            memory = e.check(text, expected, session=session, reference=reference)
            assert ledger(memory) == {(204, 208): int(expected)}
            session_times.append(e.times[-1])
            if i % 100 == 0:
                residents.append({'turn': i, **session.metrics()})
        final_metrics = session.metrics()
    with Session(binary, e.state, e.program) as session:
        expected = '1001' if args.turns % 2 else '1000'
        e.check('cuántas manzanas tiene ana?', expected, session=session, reference=reference)
        e.check('luis recibe una manzana', '?', session=session, reference=reference)
    e.audit()
    print('PERSISTENT_SAVED_TURNS_AND_RESTART_PASS', args.turns, flush=True)
    transaction_controls(e, binary, reference)
    e.state.write_bytes(learned)
    old_questions = [('gato es organismo?', 'gato es organismo. [gato -> mamífero -> vertebrado -> organismo]'),
                     ('qué es neurona?', 'neurona es célula.'),
                     ('qué estudia filosofía?', 'filosofía estudia conciencia; filosofía estudia conocimiento.'),
                     ('cuarto contiene llave?', 'cuarto contiene llave (via caja).'),
                     ('luz toca bolsa?', 'no: luz toca bolsa.'), ('bbyq tiene conciencia?', '?')]
    retained_times = []
    with Session(binary, e.state, e.program) as session:
        for text, answer, language in retained_curriculum():
            e.check(text, answer, language, session=session, reference=reference)
        for _ in range(30):
            for text, answer in old_questions:
                e.check(text, answer, session=session, reference=reference)
                retained_times.append(e.times[-1])
    e.audit()
    print('FULL_1522_CURRICULUM_ON_NEW_CHECKPOINT_PASS', flush=True)
    report = {
        'stage': 'E014', 'parent_sha256': PARENT_SHA,
        'learned_sha256': hashlib.sha256(learned).hexdigest(), 'checkpoint_bytes': len(learned),
        'new_lexical_entries': len(rows('words-v1.psv')), 'total_lexical_entries': 374+len(rows('words-v1.psv')),
        'trained_verb_concepts': len({x[0] for x in lessons}), 'distinct_consequence_lessons': len(lessons),
        'novel_stories': args.stories, 'followup_questions': args.stories,
        'failure_controls': len(failures)+1, 'persisted_action_turns': args.turns,
        'session_ms': {'median': statistics.median(session_times), 'p95': sorted(session_times)[max(0, (len(session_times)*95+99)//100-1)]},
        'retained_questions_session_ms': {'median': statistics.median(retained_times)},
        'resident_samples': residents, 'session_final_metrics': final_metrics,
        'old_knowledge_unchanged': True, 'empty_episode_ledger_in_release': True,
        'reverse_teaching_control': True, 'same_arithmetic_interpreter_and_speaker': True,
        'arithmetic_context_isolated': True, 'checks': e.checks,
        'prior_curriculum_questions_on_new_checkpoint': 1522,
        'multi_actor_item_isolation': True, 'reset_episode_preserves_lessons': True,
        'source_cache_includes_story_modules': True,
        'story_save_failure_keeps_episode_and_context': True,
        'story_post_update_xi_failure_keeps_episode_and_context': True,
        'limits': {'entities_per_episode': 16, 'tokens': 15, 'input_bytes': 255, 'quantity': [0, 65535]},
        'platform': sys.platform, 'no_reverse_os_integration': True,
    }
    (e.out/'results.json').write_text(json.dumps(report, ensure_ascii=False, indent=2)+'\n')
    (e.out/'raw.jsonl').write_text(''.join(json.dumps(x, ensure_ascii=False)+'\n' for x in e.transcript))
    print(json.dumps(report, ensure_ascii=False, indent=2), flush=True)


if __name__ == '__main__':
    main()
