#!/usr/bin/env python3
"""Independent examiner ONLY, never imported or executed by BBY Q.

Transports raw bytes to native XI, supplies teacher consequences, generates
unseen questions, computes oracle answers and compares persistent snapshots.
It does not tokenize a question, choose a model operation or produce AI output.
"""
import argparse
import hashlib
import json
from pathlib import Path
import random
import struct
import subprocess
import time

B = 7300000000000000000
ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT.parents[2]
SOURCE_SHA = 'de1a02a77c93cab6f2671858a2543dd65c7bf2d2858917290808ae1ae3c5ff1f'


def snapshot(path):
    raw = Path(path).read_bytes()
    assert raw[:5] == b'RVPC2'
    nc, nm, _ = struct.unpack_from('<QQQ', raw, 5)
    assert len(raw) == 29 + nc + nm
    core = raw[29:29+nc]
    lines = raw[29+nc:].decode('ascii').splitlines()
    assert lines[0].startswith('MXIM2 ') and lines[1] == 'MXIM1 0'
    memory = {}
    bindings = []
    for line in lines[2:]:
        kind, address, value = line.split()
        if kind == 'O':
            memory[int(address)] = int(value)
        else:
            bindings.append(line)
    return core, memory, bindings


class Examiner:
    def __init__(self, runtime, checkpoint, out):
        self.runtime = str(Path(runtime).resolve())
        self.out = Path(out).resolve()
        self.out.mkdir(parents=True, exist_ok=True)
        self.original = Path(checkpoint).resolve()
        assert hashlib.sha256(self.original.read_bytes()).hexdigest() == SOURCE_SHA
        self.old_core, self.old_memory, self.old_bindings = snapshot(self.original)
        self.state = self.out / 'state.rvp'
        self.program = self.out / 'event.xi'
        self.next = self.out / 'next.rvp'
        self.linked = {
            mode: subprocess.check_output(['bash', str(ROOT/'link.sh'), mode], text=True).split('\n', 1)[1]
            for mode in ('query', 'teach')
        }
        self.checks = 0
        self.latencies = []
        self.transcript = []
        self.run((ROOT/'birth.xi').read_text(), source=self.original)

    def preserve(self):
        core, memory, bindings = snapshot(self.state)
        assert core == self.old_core, 'Original Ether core changed'
        assert bindings == self.old_bindings, 'Quantum bindings changed'
        old = {a: v for a, v in memory.items() if not B <= a < B+2048}
        assert old == self.old_memory, 'Pre-E011 memory changed or new authority appeared'
        self.checks += 1
        return memory

    def run(self, program, source=None, reject=False):
        self.program.write_text(program)
        self.next.unlink(missing_ok=True)
        before = self.state.read_bytes() if self.state.exists() else None
        start = time.perf_counter()
        result = subprocess.run([self.runtime, 'run', str(self.program),
                                 str(source or self.state), str(self.next)], capture_output=True, text=True)
        if reject:
            assert result.returncode != 0, 'Contradictory/ambiguous lesson was accepted'
            assert not self.next.exists(), 'Failed transaction published a state'
            assert self.state.read_bytes() == before
            self.checks += 1
            return ''
        assert result.returncode == 0, result.stderr
        self.next.replace(self.state)
        self.preserve()
        self.latencies.append((time.perf_counter()-start)*1000)
        return result.stdout

    def frame(self, text, lang=1, consequence=None):
        data = text.encode('utf-8')
        assert len(data) <= 255
        stores = [(B+16, 1), (B+17, len(data)), (B+3, lang)]
        stores += [(B+128+i, value) for i, value in enumerate(data)]
        if consequence is not None:
            stores += [(B+24, 1), (B+25, consequence % 256), (B+26, consequence // 256)]
        return '#!reverse-pc-machine-v1\n' + ''.join(f'store8 {a} {v}\n' for a, v in stores)

    def teach(self, text, consequence, reject=False):
        self.run(self.frame(text, consequence=consequence)+self.linked['teach'], reject=reject)

    def query(self, text, expected, lang=1, record=True):
        output = self.run(self.frame(text, lang=lang)+self.linked['query'])
        rows = [json.loads(row) for row in output.splitlines() if row.startswith('{')]
        spoken = ''.join(chr(row['value']) for row in rows if row.get('register') == 'r14')
        assert spoken == expected, f'{text!r}: got {spoken!r}, expected {expected!r}'
        memory = self.preserve()
        assert memory.get(B+8, 0) == int(expected != '?')
        assert not any(memory.get(B+i, 0) for i in range(16, 864)), 'Raw text or feedback leaked'
        if record:
            self.transcript.append({'input': text, 'language': 'es' if lang == 1 else 'en',
                                    'output': spoken, 'reason': memory.get(B+9, 0)})
        self.checks += 1
        return memory

    def audit(self):
        for file in ('ai/xi/e008/audit-organism.xi', 'ai/xi/language/audit.xi',
                     'ai/xi/school/audit.xi', 'ai/xi/dialogue/audit.xi'):
            before = self.state.read_bytes()
            self.run((REPO/file).read_text())
            assert self.state.read_bytes() == before, f'Audit mutated state: {file}'
            self.checks += 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('runtime')
    ap.add_argument('checkpoint')
    ap.add_argument('--out', default='evidence/e011')
    ap.add_argument('--cases-per-seed', type=int, default=200)
    ap.add_argument('--seeds', type=int, nargs='+', default=[19, 42, 91])
    args = ap.parse_args()
    e = Examiner(args.runtime, args.checkpoint, args.out)
    started = time.time()
    e.query('dos mas uno', '?')
    e.teach('dos mas uno', 3)
    for _ in range(3):
        e.teach('dos mas uno', 3)
    e.query('dos mas uno', '?')
    assert e.preserve()[B+1018] == 1, 'Duplicate evidence falsely promoted a word'
    e.teach('cuatro mas dos', 6)
    e.query('tres mas dos', 'cinco')
    for row in (ROOT/'data/teaching-v1.psv').read_text().splitlines():
        if row and not row.startswith('#'):
            text, answer = row.split('|')
            e.teach(text, int(answer))
    e.teach('tres mas dos', 1, reject=True)
    e.teach('dos dos uno', 3, reject=True)
    e.teach('dos dudoso cero', 2, reject=True)
    e.teach('dos falso uno', 9, reject=True)
    e.audit()
    (e.out/'learned-before-exam.rvp').write_bytes(e.state.read_bytes())

    # Independent oracle words come from teaching DATA, never native source.
    names = {}
    for row in (ROOT.parent/'school/data/observations-v1.psv').read_text().splitlines():
        if row and not row.startswith('#'):
            domain, number, _, _, es, en = row.split('|')
            if domain == '4':
                names[int(number)] = (es, en)
    def answer(value, lang):
        return names[value][lang-1] if 0 <= value <= 9 else str(value)

    focused = [
        ('  TRES\tMAS   DOS?  ', 5, 1), ('Two plus three?', 5, 2),
        ('nueve mas nueve menos uno', 17, 1), ('65535 menos 65530', 5, 2),
        ('0 mas 0', 0, 1), ('65535 plus 0', 65535, 2),
        ('1 plus 1 plus 1 plus 1 plus 1 plus 1 plus 1 plus 1', 8, 2),
        ('00009 mas 00001', 10, 1), ('nueve zeta dos omega tres', 8, 1),
        ('dos mas tres', 5, 1), ('menos uno', 4, 1), ('plus two', 6, 2),
    ]
    for text, value, lang in focused:
        e.query(text, answer(value, lang), lang)
    invalid = ['', '?', 'dos? mas tres', 'dos ??', 'dos, mas tres', '1a mas dos',
               'desconocido mas dos', '65536 mas uno', '65535 mas uno',
               'cero menos uno mas dos', 'dos mas', 'dos tres', 'dos mas mas tres',
               'dos dividido uno', 'á mas uno', 'abcdefghijklmnopq',
               '1 plus 1 plus 1 plus 1 plus 1 plus 1 plus 1 plus 1 plus 1']
    for text in invalid:
        e.query(text, '?')
    e.query('mas dos', '?')  # Unknown turn must not retain an old reference.
    assert e.preserve()[B+9] == 3

    systematic = 0
    for lang in (1, 2):
        for left in range(10):
            for right in range(10):
                # These ordered operands were never teaching demonstrations.
                if (left, right) in ((2, 1), (4, 2), (6, 2), (7, 3)):
                    continue
                for positive in (True, False):
                    operation = ('mas', 'plus')[lang-1] if positive else ('menos', 'minus')[lang-1]
                    text = f'{names[left][lang-1]} {operation} {names[right][lang-1]}'
                    value = left+right if positive else left-right
                    e.query(text, answer(value, lang) if value >= 0 else '?', lang)
                    systematic += 1
    campaign = []
    for seed in args.seeds:
        rng = random.Random(seed)
        supported = abstentions = 0
        for case in range(args.cases_per_seed):
            lang = rng.choice((1, 2))
            current = rng.randrange(65536)
            tokens = [str(current)]
            valid = True
            for _ in range(rng.randrange(1, 8)):
                amount = rng.randrange(12000)
                positive = rng.choice((True, False))
                op = rng.choice(('mas', 'plus', 'juntar', 'y', 'and', 'zeta') if positive else
                                ('menos', 'minus', 'quitar', 'omega'))
                numeral = names[amount][rng.randrange(2)] if amount in names else str(amount)
                tokens += [op, numeral]
                current += amount if positive else -amount
                valid &= 0 <= current <= 65535
            question = ' '.join(tokens)
            e.query(question, answer(current, lang) if valid else '?', lang)
            supported += int(valid)
            abstentions += int(not valid)
        campaign.append({'seed': seed, 'cases': args.cases_per_seed,
                         'supported_correct': supported, 'appropriate_abstentions': abstentions})
        print(json.dumps(campaign[-1]), flush=True)

    # Learned spellings must follow EVIDENCE even when meanings are reversed.
    main_state = e.state.read_bytes()
    e.state.unlink()
    e.run((ROOT/'birth.xi').read_text(), source=e.original)
    e.query('cinco zeta dos', '?')
    for text, observed in [('seis zeta dos', 4), ('siete zeta tres', 4),
                           ('dos omega uno', 3), ('cuatro omega dos', 6)]:
        e.teach(text, observed)
    e.query('cinco zeta dos', 'tres')
    e.query('cinco omega dos', 'siete')
    e.audit()
    (e.out/'reversed-spelling-control.rvp').write_bytes(e.state.read_bytes())
    # Bound exhaustion must reject transactionally, preserving accepted words.
    e.state.unlink()
    e.run((ROOT/'birth.xi').read_text(), source=e.original)
    for index in range(32):
        word = 'op' + chr(97+index//26) + chr(97+index%26)
        e.teach(f'dos {word} uno', 3)
        e.teach(f'cuatro {word} dos', 6)
    e.query('tres opaa dos', 'cinco')
    e.teach('dos overflow uno', 3, reject=True)
    e.query('tres opbf dos', 'cinco')
    e.audit()
    # A damaged model header must fail without publishing an output file.
    e.run(f'#!reverse-pc-machine-v1\nstore8 {B+4} 33\n')
    e.run(e.frame('dos opaa uno')+e.linked['query'], reject=True)
    e.state.write_bytes(main_state)
    e.query('dos mas tres', 'five', 2)
    e.query('menos uno', 'four', 2)  # A fresh process restores the context.
    e.audit()
    final = e.out/'BBYQ_E011_Compositional_ES_EN.rvp'
    final.write_bytes(e.state.read_bytes())
    e.program.unlink(missing_ok=True)
    e.next.unlink(missing_ok=True)
    data = final.read_bytes()
    latencies = sorted(e.latencies)
    report = {'base_commit': '1d621ba9875435fd46bdbc13b7459c8c62faef9b',
              'e010_source_sha256': SOURCE_SHA, 'replayed_old_training': False,
              'learning_language': 'XI', 'new_operator_spellings': 10,
              'campaign': campaign, 'systematic_unseen_bilingual_questions': systematic, 'checks': e.checks,
              'original_core_and_all_previous_logical_bytes_unchanged': True,
              'duplicate_witness_not_promoted': True, 'contradictory_lessons_rolled_back': 4,
              'reversed_spelling_control': 'passed', 'operator_capacity_and_corruption_guards': 'passed',
              'final_state_bytes': len(data), 'final_state_sha256': hashlib.sha256(data).hexdigest(),
              'native_transaction_ms_median': latencies[len(latencies)//2],
              'native_transaction_ms_p95': latencies[int(len(latencies)*.95)],
              'wall_seconds': time.time()-started,
              'limits': ['ASCII', '255 input bytes', '15 tokens of at most 16 bytes',
                         '32 operator spellings', 'designed left-to-right grammar',
                         '0..65535 at each step', 'no open-domain conversation',
                         'no comparison against large language models']}
    (e.out/'results.json').write_text(json.dumps(report, indent=2)+'\n')
    (e.out/'transcript.jsonl').write_text(''.join(json.dumps(x, ensure_ascii=False)+'\n' for x in e.transcript))
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
