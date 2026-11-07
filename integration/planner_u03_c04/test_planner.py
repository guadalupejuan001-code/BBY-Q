"""C04 unit contracts: immutable DAG, lazy native owners, hash workers."""
from __future__ import annotations
from contextlib import closing
from concurrent.futures import ThreadPoolExecutor
from hashlib import sha256
from pathlib import Path
import sqlite3
import tempfile
import unittest
from unittest.mock import patch

from integration.unified import session as u02
from integration.unified import quantum as original_quantum
from integration.unified.contracts import RULES
from .planner import make_plan, topological_order
from . import runtime as C04


class PlannerTests(unittest.TestCase):
    def test_original_inference_bytecode_and_bindings_remain_unchanged(self):
        self.assertIs(C04._PLANNED_TURN.__code__, u02.Session.turn.__code__)
        self.assertIsNot(C04._PLANNED_TURN.__globals__, u02.Session.turn.__globals__)
        self.assertIs(C04._PLANNED_TURN.__globals__["Quantum"], C04.LazyReadoutQuantum)
        self.assertIs(u02.Session.turn.__globals__["Quantum"], original_quantum.Quantum)
        self.assertIs(C04.PlannedSession.__mro__[1], C04.CachedSession)

    def test_compound_plan_keeps_native_dependencies_and_is_acyclic(self):
        index = next(i for i, rule in enumerate(RULES, 1)
                     if tuple(x[0] for x in rule.actions) ==
                     ("remember", "observe", "mission"))
        plan = make_plan({"domain": "quantum", "rule": index})
        names = topological_order(plan)
        self.assertEqual(len(names), len(set(names)))
        self.assertEqual(set(plan.banks), {"memory", "v3", "entity", "voice"})
        self.assertFalse(plan.stateful_native_parallelism)
        self.assertTrue(names.index("0.0.memory.write") <
                        names.index("1.0.vqc.sample-and-forward") <
                        names.index("2.0.memory.read"))

    def test_unmatched_and_cancel_have_no_forced_quantum(self):
        self.assertEqual(make_plan(None).banks, ())
        index = next(i for i, rule in enumerate(RULES, 1)
                     if rule.actions[0][0] == "cancel")
        plan = make_plan({"domain": "quantum", "rule": index})
        self.assertEqual(plan.banks, ())
        self.assertEqual(topological_order(plan), ["0.0.metadata.no-write"])

    def test_lazy_bank_only_starts_original_process_on_execute(self):
        opened = []
        class FakeNative:
            def __init__(self, binary, state):
                opened.append(state)
            def execute(self, source): return ([{"type": "ok"}], 1)
            def metrics(self): return {"cpu_ms": 1}
            def save(self, path): return None
            def close(self): opened.append("closed")
        stats = C04._stats()
        token = C04._METRICS.set(stats)
        try:
            with patch.object(C04, "_ORIGINAL_XI_SESSION", FakeNative):
                with C04.LazyNativeBank("native", Path("memory.rvp")) as unused:
                    self.assertEqual(len(opened), 0)
                self.assertEqual(stats["native_bank_processes_avoided"], ["memory"])
                with C04.LazyNativeBank("native", Path("v3.rvp")) as worker:
                    self.assertEqual(len(opened), 0)
                    self.assertEqual(worker.execute("query")[0], [{"type": "ok"}])
                    self.assertEqual(worker.metrics(), {"cpu_ms": 1})
                self.assertEqual(opened, [Path("v3.rvp"), "closed"])
                self.assertEqual(stats["native_bank_processes_started"], ["v3"])
        finally:
            C04._METRICS.reset(token)

    def test_readout_lookup_is_deferred_for_language_task(self):
        class FakeNative: pass
        with patch.object(C04.frozen_common, "integer", return_value=240605) as observed:
            quantum = C04.LazyReadoutQuantum(
                {"v3": FakeNative()}, {}, Path("."), lambda *_: None
            )
            self.assertEqual(quantum.trace, [])
            observed.assert_not_called()
            self.assertEqual(quantum.readout_magic, 240605)
            self.assertTrue(quantum.perception_active)
            self.assertEqual(observed.call_count, 1)

    def test_parallel_hash_is_read_only_and_rejects_tampered_bank(self):
        with closing(sqlite3.connect(":memory:")) as db:
            db.execute("CREATE TABLE unified_banks (name TEXT PRIMARY KEY, snapshot BLOB, sha TEXT)")
            rows = []
            for i in range(7):
                raw = (bytes([65+i]) * 4096)
                rows.append((str(i), raw, sha256(raw).hexdigest()))
            db.executemany("INSERT INTO unified_banks VALUES(?,?,?)", rows)
            owner = object.__new__(C04.PlannedSession)
            owner.db = db
            owner._hash_workers = 4
            metrics = C04._stats()
            token = C04._METRICS.set(metrics)
            try:
                self.assertEqual(owner._banks(), {k: value for k, value, _ in rows})
                self.assertEqual(metrics["immutable_bank_hashes_verified"], 7)
                self.assertEqual(metrics["hash_worker_count"], 4)
                db.execute("UPDATE unified_banks SET snapshot = ? WHERE name='3'", (b"mutated",))
                with self.assertRaisesRegex(ValueError, "Corrupt unified bank: 3"):
                    owner._banks()
            finally:
                C04._METRICS.reset(token)

    def test_parallel_plans_are_context_local(self):
        def run(index):
            stats = C04._stats()
            token = C04._METRICS.set(stats)
            try:
                stats["dependency_plan"] = {"id": index}
                return C04._METRICS.get()["dependency_plan"]["id"]
            finally:
                C04._METRICS.reset(token)
        with ThreadPoolExecutor(max_workers=4) as workers:
            self.assertEqual(list(workers.map(run, range(20))), list(range(20)))
        self.assertIsNone(C04._METRICS.get())


if __name__ == "__main__":
    unittest.main()
