"""Real REVERSE-PC / XI integration. CI sets BBYQ_REQUIRE_NATIVE=1."""
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from bbyq.model import experience, new_entity, predict
from bbyq.store import NativeStore

RUNTIME = os.environ.get("BBYQ_REVERSE_PC")
REQUIRED = os.environ.get("BBYQ_REQUIRE_NATIVE") == "1"
if REQUIRED and not RUNTIME:
    raise RuntimeError("CI requires real REVERSE-PC; native test must not silently skip")


@unittest.skipUnless(RUNTIME, "Set BBYQ_REVERSE_PC to compiled, pinned REVERSE-PC CLI")
class NativeIntegrationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.filename = Path(self.temp.name) / "entity.rvp"
        self.store = NativeStore(self.filename, RUNTIME)
        self.store.initialize(new_entity("pinned-reverse-pc-session"))

    def test_birth_and_restart_and_provenance(self):
        prior = self.store.read()
        self.assertEqual(prior["steps"], 0)
        payload, record = self.store.transact(lambda entity: experience(
            entity, {"signal": .45, "pressure": -.2}, -1, 1))
        self.assertEqual(record["step"], 1)
        reopened = NativeStore(self.filename, RUNTIME).read()
        self.assertEqual(reopened, payload)
        self.assertEqual(reopened["id"], prior["id"])
        stats = self.store.stats()
        kinds = {item["type"]: item for item in stats["native"]}
        self.assertEqual(kinds["stats"]["active_qubits"], 0)
        self.assertEqual(kinds["memory_stats"]["quantum_bindings"], 0)
        self.assertGreater(kinds["memory_stats"]["overrides"], 0)
        self.assertLess(stats["rvpc2_bytes"], 32768)

    def test_xi_atomic_failure_unchanged_file(self):
        original = self.filename.read_bytes()
        with self.assertRaises(RuntimeError):
            self.store._run("mem_store 999 53\nmem_store 998 999\n", readonly=False)
        self.assertEqual(original, self.filename.read_bytes())
        self.assertEqual(self.store.read()["steps"], 0)

    def test_corrupted_snapshot_rejected(self):
        raw = self.filename.read_bytes()
        damaged = bytearray(raw)
        damaged[-3] ^= 2
        self.filename.write_bytes(damaged)
        with self.assertRaises(RuntimeError):
            self.store.read()
        self.filename.write_bytes(raw)
        self.assertEqual(self.store.read()["steps"], 0)

    def test_recreation_fails_not_overwritten(self):
        original = self.filename.read_bytes()
        with self.assertRaises(FileExistsError):
            self.store.initialize(new_entity("wrong-id"))
        self.assertEqual(original, self.filename.read_bytes())

    def test_legacy_snapshot_roundtrip_and_compact_migration(self):
        from bbyq.store import BASE_ADDRESS, COMPACT_FLAG
        legacy = new_entity('old-json-state')
        for name in ('active_context', 'next_context', 'active_updates',
                     'archived', 'switches', 'surprise_streak'):
            legacy['model'].pop(name)
        new_payload = json.dumps(legacy, separators=(',', ':'), sort_keys=True,
                                 ensure_ascii=True, allow_nan=False).encode()
        new_wire = len(new_payload).to_bytes(4, 'little') + new_payload
        with self.store._lock():
            _, old_wire = self.store._load_unlocked()
            commands = [f'mem_store {BASE_ADDRESS+i} {new_wire[i] if i < len(new_wire) else 0}'
                        for i in range(max(len(old_wire), len(new_wire)))
                        if (new_wire[i] if i < len(new_wire) else 0) !=
                           (old_wire[i] if i < len(old_wire) else 0)]
            self.store._run('\n'.join(commands) + '\n', readonly=False)
            self.assertFalse(int.from_bytes(self.store._materialize(4), 'little') & COMPACT_FLAG)
        self.assertEqual(self.store.read(), legacy)
        self.store.transact(lambda entity: experience(
            entity, {'signal': .2, 'pressure': .1}, 1, 1))
        self.assertEqual(self.store.read()['steps'], 1)
        with self.store._lock():
            self.assertTrue(int.from_bytes(self.store._materialize(4), 'little') & COMPACT_FLAG)

    def test_failed_birth_never_publishes_broken_state(self):
        bad = new_entity('invalid-size')
        bad['extra_padding'] = 'X' * 30000
        failed_path = Path(self.temp.name) / 'birth-failed.rvp'
        store = NativeStore(failed_path, RUNTIME)
        with self.assertRaises(ValueError):
            store.initialize(bad)
        self.assertFalse(failed_path.exists())
        store.initialize(new_entity('recovered'))
        self.assertEqual(store.read()['id'], 'recovered')

    def test_persist_context_and_recall_after_restart(self):
        from bbyq.context import contextual_experience
        model = self.store.read()['model']
        def mature(entity):
            entity['model']['weights']['bias'] = 10.0
            entity['model']['updates'] = 100
            entity['model']['active_updates'] = 100
        self.store.transact(mature)
        for _ in range(3):
            self.store.transact(lambda state: contextual_experience(
                state, {'signal': 0.0, 'pressure': 0.0}, 1, 0))
        cold = NativeStore(self.filename, RUNTIME).read()
        self.assertEqual(cold['model']['active_context'], 1)
        self.assertEqual(len(cold['model']['archived']), 1)
        self.assertEqual(cold['model']['archived'][0]['id'], 0)
        self.assertEqual(cold['model']['archived'][0]['weights']['bias'], 10.0)

    def test_new_process_can_observe_continuity(self):
        self.store.transact(lambda entity: experience(entity,
                            {"signal": 0.2, "pressure": 0.1}, 1, 0))
        env = os.environ.copy()
        env["PYTHONPATH"] = str(Path(__file__).resolve().parents[1])
        completed = subprocess.run(
            [sys.executable, "-m", "bbyq", "--state", str(self.filename),
             "--reverse-pc", RUNTIME, "inspect"], env=env, text=True,
            capture_output=True, check=True)
        payload = json.loads(completed.stdout)
        self.assertEqual(payload["entity"]["steps"], 1)
        self.assertEqual(payload["entity"]["id"], "pinned-reverse-pc-session")


if __name__ == "__main__":
    unittest.main()
