"""C13: isolated-cache safeguards, exact-snapshot parity and fair benchmark math."""
from __future__ import annotations

import inspect
from pathlib import Path
import unittest
from unittest.mock import patch

from integration.unified.common import Legacy

from . import cache
from . import campaign as C


class C13Contracts(unittest.TestCase):
    def test_all_benchmark_cases_new_and_predeclared(self):
        p=C.ensure_separation()
        self.assertTrue(p["independent_of_C11_C12"])
        self.assertEqual(p["unique_cases"],4)
        self.assertEqual(C.DEFAULT_REPEATS,3)
        self.assertEqual({x.position for x in C.CASES},{0,2,4,6})
        self.assertEqual({x.bit for x in C.CASES},{0,1})

    def test_cache_only_immutable_banks_never_turn_sqlite_or_xi(self):
        self.assertTrue(cache.no_unsafe_memoization())
        text=inspect.getsource(cache.authenticated_release_cache)
        for name in ("read_models","router_model","perception_model",
                     "entity_models","source_identity"):
            self.assertIn(name,text)
        self.assertNotIn("session.turn",text)
        self.assertNotIn("sqlite3.connect",text)
        self.assertIn("freeze_assets()",text)
        self.assertIn("finally:",text)

    def test_cache_returns_copies_cleans_up_and_counts_misses_and_hits(self):
        protected={f"historical/{i}":"a"*64 for i in range(159)}
        original=Legacy.read_models
        with patch.object(cache,"freeze_assets",return_value=protected), \
             patch.object(Legacy,"read_models",return_value={"read_only":b"xi"}):
            mocked=Legacy.read_models
            with cache.authenticated_release_cache() as evidence:
                first=Legacy.read_models(Path("frozen"))
                first["read_only"]=b"unauthorized write"
                second=Legacy.read_models(Path("frozen"))
                self.assertEqual(second["read_only"],b"xi")
                self.assertIsNot(first,second)
                self.assertEqual(evidence["cold_authentications"],1)
                self.assertEqual(evidence["cache_hits"],1)
            self.assertIs(Legacy.read_models,mocked)
        self.assertIs(Legacy.read_models,original)

    def test_cache_refuses_mutated_frozen_source_at_scope_exit(self):
        snapshots=[{f"hist/{i}":str(i) for i in range(159)},
                   {f"hist/{i}":str(i) for i in range(159)}]
        snapshots[1]["hist/5"]="changed"
        with patch.object(cache,"freeze_assets",side_effect=snapshots):
            with self.assertRaisesRegex(AssertionError,"protected model identity changed"):
                with cache.authenticated_release_cache():
                    pass

    def test_paired_latency_requires_exact_native_result_and_equal_checkpoint(self):
        r={"source_seed":42,
           "observed":{"native_class":1,"native_rule":0},
           "receipt_sha256":"abc","after_snapshot_sha256":"xyz",
           "phase_ms":{"total_including_new_db":200.0,"total_including_guard":200.0}}
        faster={**r,"phase_ms":{"total_including_new_db":150.0,"total_including_guard":150.0}}
        left=[r]*8;right=[faster]*8
        result=C._paired_report(left,right)
        self.assertEqual(result["pairs"],8)
        self.assertTrue(result["all_native_outputs_and_receipts_byte_equivalent"])
        self.assertEqual(result["observed_median_speedup_percent"],25.0)
        bad={**faster,"receipt_sha256":"not-the-native-original"}
        with self.assertRaises(AssertionError):
            C._paired_report(left,[bad]*8)
        bad_snapshot={**faster,"after_snapshot_sha256":"bad"}
        with self.assertRaises(AssertionError):
            C._paired_report(left,[bad_snapshot]*8)

    def test_native_inference_and_ablations_never_use_teacher(self):
        src=inspect.getsource(C._measure_one)
        self.assertIn("model.turn(",src)
        self.assertIn("no_teacher_labels_entered_native_inference",src)
        self.assertIn("C1_synchronized_with_U02",src)
        self.assertIn("session_startup_authentication",src)
        self.assertIn("original_u02_xi_turn",src)
        self.assertIn("qm_train/publish_angles",src)
        evalsrc=inspect.getsource(C.campaign)
        self.assertIn("training[arm]=_training_arm(",evalsrc)
        self.assertIn("golden=_episode(source,CASES[0])",evalsrc)
        self.assertIn("_identical(a,b)",evalsrc)
        self.assertIn("before_banks[arm][\"hashes\"]!=after_hashes",evalsrc)
        self.assertIn("freeze_assets()!=protected_before",evalsrc)
        self.assertNotIn("torch",evalsrc)
        self.assertNotIn("qiskit",evalsrc)


if __name__=="__main__":
    unittest.main()
