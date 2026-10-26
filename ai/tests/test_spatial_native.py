"""E003: native REVERSE-PC state authority tests, no mocked backend."""
import json
import os
from pathlib import Path
import subprocess
import tempfile
import unittest

SPACE = 7_000_000_000_000_000_000
BINARY = os.environ.get('BBYQ_SPATIAL_BINARY')
RUNTIME = os.environ.get('BBYQ_REVERSE_PC')
REQUIRED = os.environ.get('BBYQ_SPATIAL_REQUIRED') == '1'

@unittest.skipUnless(BINARY or REQUIRED, 'native spatial executable not configured')
class SpatialNativeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not BINARY or not Path(BINARY).is_file():
            raise AssertionError('BBYQ_SPATIAL_BINARY requires compiled native Ether learner')
        if REQUIRED and (not RUNTIME or not Path(RUNTIME).is_file()):
            raise AssertionError('Original REVERSE-PC CLI required for interop')

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.path = Path(self.tmp.name) / 'single-authority.rvp'

    def run_space(self, *args, payload=None, success=True):
        result = subprocess.run([BINARY, *map(str, args)], text=True,
                                input=payload, capture_output=True, timeout=30)
        if success:
            self.assertEqual(result.returncode, 0, result.stderr)
        else:
            self.assertNotEqual(result.returncode, 0)
        return result

    def birth(self):
        return json.loads(self.run_space('new', self.path).stdout)

    def test_native_birth_uses_implicit_space_not_qubits(self):
        state = self.birth()
        self.assertEqual(state['schema'], 'BBYQ-SPACE-3')
        self.assertEqual(state['steps'], 0)
        self.assertEqual(state['active_qubits'], 0)
        self.assertEqual(state['quantum_bindings'], 0)
        self.assertEqual(state['logical_overrides'], 3)
        self.assertEqual(set(state['relations']),
                         {'bias', 'signal', 'pressure', 'action', 'signal_action'})
        before = self.path.read_bytes()
        self.run_space('new', self.path, success=False)
        self.assertEqual(before, self.path.read_bytes())

    def test_relation_updates_and_process_restart(self):
        self.birth()
        prior = json.loads(self.run_space('predict', self.path, .3, -.2, 1).stdout)
        self.assertEqual(prior['prediction'], 1)
        trace = json.loads(self.run_space('learn', self.path, .3, -.2, 1, 0).stdout)
        self.assertEqual(trace['prediction_before_feedback'], 1)
        self.assertEqual(trace['outcome'], 0)
        state = json.loads(self.run_space('inspect', self.path).stdout)
        self.assertEqual(state['steps'], 1)
        self.assertLessEqual(state['logical_overrides'], 12)
        self.assertLess(state['rvpc2_bytes'], 4096)
        self.assertNotEqual(state['relations']['bias'], 0)
        self.run_space('learn', self.path, -.8, .8, -1, 1)
        self.assertEqual(json.loads(self.run_space('inspect', self.path).stdout)['steps'], 2)

    def test_failed_session_rolls_back_all_effects_and_stdout(self):
        self.birth()
        before = self.path.read_bytes()
        bad = self.run_space('session', self.path,
                             payload='L 0.3 -0.2 1 0\nL 1.8 0.4 -1 1\n', success=False)
        self.assertIn('BBYQ_SPACE_FAIL', bad.stderr)
        self.assertEqual(bad.stdout, '')
        self.assertEqual(before, self.path.read_bytes())
        bad2 = self.run_space('learn', self.path, 0, 0, 1, 3, success=False)
        self.assertEqual(bad2.stdout, '')
        self.assertEqual(before, self.path.read_bytes())

    def test_session_predict_is_read_only_and_feedback_cannot_leak(self):
        self.birth()
        old = self.path.read_bytes()
        output = [json.loads(x) for x in self.run_space('session', self.path,
                 payload='P 0.5 0.4 1\nP -0.5 0.2 -1\n').stdout.splitlines()]
        self.assertEqual(len(output), 2)
        self.assertEqual(old, self.path.read_bytes())
        output = [json.loads(x) for x in self.run_space('session', self.path,
                 payload='P 0.5 0.4 1\nL 0.5 0.4 1 0\n').stdout.splitlines()]
        self.assertEqual(output[0]['prediction'], output[1]['prediction_before_feedback'])
        self.assertEqual(output[1]['steps'], 1)

    def test_detects_corruption_without_rewriting(self):
        self.birth()
        data = bytearray(self.path.read_bytes())
        data[-1] ^= 1
        self.path.write_bytes(data)
        before = self.path.read_bytes()
        self.run_space('inspect', self.path, success=False)
        self.assertEqual(before, self.path.read_bytes())

    def test_reverse_pc_can_read_same_memory_authority(self):
        if not RUNTIME:
            self.skipTest('REVERSE-PC CLI unavailable')
        self.birth()
        self.run_space('learn', self.path, .8, -.2, 1, 0)
        program = Path(self.tmp.name) / 'inspect.xi'
        program.write_text(f'mem_read {SPACE}\nmem_read {SPACE+64}\nmem_stats\nstats\n')
        output = Path(self.tmp.name) / 'original-cli-output.rvp'
        p = subprocess.run([RUNTIME, 'run', str(program), str(self.path), str(output)],
                           text=True, capture_output=True, timeout=30)
        self.assertEqual(p.returncode, 0, p.stderr)
        records = [json.loads(x) for x in p.stdout.splitlines()]
        self.assertEqual(records[0]['value'], 66)
        state = json.loads(self.run_space('inspect', self.path).stdout)
        self.assertEqual(records[1]['value'], state['relations']['bias'] % 256)
        self.assertEqual(records[2]['overrides'], state['logical_overrides'])
        self.assertEqual(records[3]['active_qubits'], 0)
        self.assertEqual(self.path.read_bytes(), output.read_bytes())

if __name__ == '__main__':
    unittest.main()
