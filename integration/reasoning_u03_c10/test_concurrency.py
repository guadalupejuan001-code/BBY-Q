"""C10 race guards: deterministic injected concurrent checkpoint updates.

These are negative boundary unit tests. The positive native proof is
separately demonstrated by conformance.py against real REVERSE-PC XI.
"""
from copy import deepcopy
from types import SimpleNamespace
import unittest
from unittest.mock import patch

from .engine import Reasoner
from .planner import Goal
from .test_planner import audited


class Cursor:
    def fetchone(self):
        return None


class SourceDB:
    in_transaction=False
    def backup(self, target):
        # The mock is a controlled test of C10's revision barriers, not a
        # substitute for the real SQLite WAL tests in C09.
        pass


class FakeClone:
    def __init__(self, *args):
        self.db=SimpleNamespace(execute=lambda *a,**k:Cursor())
        self.invocations=0
    def __enter__(self):
        return self
    def __exit__(self, *args):
        pass
    def turn(self, identifier, prompt):
        self.invocations+=1
        return {
            "ok":True,
            "results":[{"kind":"query","status":1,"proof":[1234]}],
            "trace":[{"operation":"c1_encode_input/c1_next"}],
        }


class ChangedStateTests(unittest.TestCase):
    def plan(self, original, clone_snapshot, later_snapshot):
        s=SimpleNamespace(db=SourceDB())
        planner=Reasoner(s)
        values=[original,later_snapshot]
        planner.view=SimpleNamespace(snapshot=lambda:values.pop(0))
        fake=FakeClone()
        with patch("integration.reasoning_u03_c10.engine.Session",return_value=fake):
            with patch("integration.reasoning_u03_c10.engine.UnifiedMemoryView",
                       return_value=SimpleNamespace(snapshot=lambda:clone_snapshot)):
                report=planner.plan(Goal("prove_alert","Nara"))
        return report,fake.invocations

    def test_changed_during_backup_aborts_before_native(self):
        original=audited()
        other=deepcopy(original);other["view_sha256"]="other-checkpoint"
        status, count=self.plan(original,other,original)
        self.assertEqual(status["status"],"blocked_concurrent_change")
        self.assertEqual(status["blocked_at"],"verify_C09_copy_is_same_revision")
        self.assertEqual(count,0)
        self.assertIsNone(status["native"])
        self.assertFalse(status["native_goal_executed_in_disposable_copy"])
        self.assertFalse(status["source_unchanged_at_last_check"])

    def test_changed_after_native_proof_discards_result_not_sandbox_trace(self):
        original=audited()
        changed=deepcopy(original);changed["view_sha256"]="updated-checkpoint"
        status,count=self.plan(original,original,changed)
        self.assertEqual(status["status"],"blocked_concurrent_change")
        self.assertEqual(status["blocked_at"],"reverify_source_unchanged")
        self.assertEqual(count,1)
        self.assertIsNone(status["native"])
        self.assertTrue(status["native_goal_executed_in_disposable_copy"])
        self.assertFalse(status["source_unchanged_at_last_check"])
        self.assertEqual(status["original_database_writes"],0)

    def test_unchanged_source_delivers_traced_native_proof(self):
        original=audited()
        result,count=self.plan(original,original,original)
        self.assertEqual(count,1)
        self.assertEqual(result["status"],"native_proof")
        self.assertEqual(result["native"]["symbolic_proof_ids"],[1234])
        self.assertTrue(result["source_unchanged_at_last_check"])


if __name__=="__main__":
    unittest.main()
