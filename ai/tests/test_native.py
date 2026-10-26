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
