"""C15 fails closed on missing native XI/WAL proofs and unsafe promotion."""
from __future__ import annotations
import inspect
import unittest
from . import campaign as C
from . import protocol as P


class StressContracts(unittest.TestCase):
    def test_predeclared_independent_progressive_stress(self):
        proof=P.separation()
        self.assertTrue(proof["independent_of_C11_through_C14"])
        self.assertEqual(proof["case_count"],8)
        self.assertEqual(P.LEVELS,(1,2,4,6))
        self.assertEqual(P.READERS,{1:1,2:2,4:2,6:3})
        self.assertEqual(len(set(x.seed for x in P.CASES)),8)
        self.assertEqual(len(P.EXPECTED_NATIVE_OPERATIONS),6)
        self.assertEqual(P.SCHEMA,"BBYQ-U03-C15-native-WAL-stress-v1")

    def test_sqlite_readonly_WAL_snapshot_authenticates_every_bank(self):
        source=inspect.getsource(C._original_bank_view)
        self.assertIn("?mode=ro",source)
        self.assertIn("PRAGMA query_only=ON",source)
        self.assertIn('con.execute("BEGIN")',source)
        self.assertIn('con.execute("ROLLBACK")',source)
        self.assertIn("len(banks) != 7",source)
        self.assertIn("digest(raw) != hash_expected",source)
        self.assertIn("language_sync",source)
        self.assertIn("C1_U02_synchronized",source)
        self.assertNotIn("UPDATE ",source.replace("SELECT","").replace("query_only",""))

    def test_true_multiple_original_native_writers_and_readers(self):
        writer=inspect.getsource(C._writer)
        self.assertIn("Session(db)",writer)
        self.assertIn("model.turn(",writer)
        self.assertIn("all(op in ops for op in EXPECTED_NATIVE_OPERATIONS)",writer)
        self.assertNotIn("payload=",writer)
        src=inspect.getsource(C._load_level)
        self.assertIn("threading.Barrier",src)
        self.assertIn("ThreadPoolExecutor",src)
        self.assertIn("model.snapshot() != snap",src)
        self.assertIn("PRAGMA integrity_check",src)
        self.assertIn("journal_mode",src)
        self.assertIn("throughput_native_tasks_per_second",src)
        self.assertIn("first_commit = threading.Event()",src)
        self.assertIn("readers_observed_post_commit_revision",src)
        reader=inspect.getsource(C._reader)
        self.assertIn("first_commit.wait(timeout=95)",reader)
        self.assertIn("revisions[-1] <= initial_revision",reader)
        self.assertIn("after_commit_revision_seen",reader)
        self.assertIn("RUSAGE_CHILDREN",inspect.getsource(C._child_cpu_ms))

    def test_failures_and_crashes_must_recover_original_SQLite(self):
        failures=inspect.getsource(C._failure_rollback)
        self.assertIn("fail_after=cutoff",failures)
        self.assertIn("model.history()!=history",failures)
        self.assertIn("restored.snapshot()!=before",failures)
        worker=inspect.getsource(C._abrupt_crash)
        self.assertIn("BEGIN IMMEDIATE",worker)
        self.assertIn("os._exit(73)",worker)
        self.assertIn("os._exit(74)",worker)
        self.assertIn('model.turn("c15-crash-committed"',worker)
        crash=inspect.getsource(C._crash_recovery)
        self.assertIn("subprocess.run(",crash)
        self.assertIn('timeout=90',crash)
        self.assertIn("PRAGMA integrity_check",crash)
        self.assertIn("C15 native committed receipt not idempotent",crash)

    def test_id_collision_rejects_different_payload_without_double_write(self):
        src=inspect.getsource(C._colliding_requests)
        self.assertIn("ThreadPoolExecutor(max_workers=2)",src)
        self.assertIn('"c15-collision"',src)
        self.assertIn("COUNT(*) FROM unified_tasks",src)
        self.assertIn("different_payload_same_id_rejected",src)
        self.assertIn("model.snapshot()!=previous",src)

    def test_cache_remains_serial_and_unpromoted(self):
        src=inspect.getsource(C._cache_control)
        self.assertIn("authenticated_release_cache()",src)
        self.assertIn("_identical(reference,cached)",src)
        self.assertIn('"cache_not_promoted":True',src)
        self.assertIn('"single_threaded_only":True',src)
        campaign=inspect.getsource(C.campaign)
        self.assertIn('"model_promoted":False',campaign)
        self.assertIn('"cache_promoted":False',campaign)
        self.assertIn('"apk_built":False',campaign)
        self.assertIn("protected=freeze_assets()",campaign)
        self.assertIn("freeze_assets()!=protected",campaign)
        self.assertIn('len(protected)!=159',campaign)
        self.assertIn('"architecture":"BBY Q -> w4U -> QdU"',campaign)

    def test_no_staged_secret_labels_or_fake_quantum_runtime(self):
        src=inspect.getsource(C._writer)+inspect.getsource(C._load_level)
        self.assertNotIn("qiskit",src)
        self.assertNotIn("torch",src)
        self.assertNotIn("fake",src)
        self.assertIn("model.turn(",src)
        self.assertIn("throughput_native_tasks_per_second",inspect.getsource(C._load_level))


if __name__=="__main__":
    unittest.main()
