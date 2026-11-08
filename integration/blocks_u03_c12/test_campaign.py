"""C12 no-label leakage, independent splits, native origin and promotion tests."""
from __future__ import annotations
import inspect
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from . import protocol as P
from . import campaign as C


class CrossBlockContracts(unittest.TestCase):
    def test_new_precommitted_harder_matrix(self):
        proof = P.separate()
        self.assertTrue(proof["c11_names_seeds_prompts_disjoint"])
        self.assertTrue(proof["evaluation_contains_both_rules_and_seven_positions"])
        self.assertEqual(proof["counts"],
                         {"training": 2, "validation": 4, "test": 6, "load": 6})
        self.assertEqual(len(P.OPERATIONS), 6)
        self.assertEqual(P.MODES, ("frozen", "joint-verified"))
        self.assertEqual(P.REVISIT[0], P.REVISIT[2])
        self.assertNotEqual(P.REVISIT[0], P.REVISIT[1])

    def test_original_native_engine_only(self):
        source = inspect.getsource(C._timed_episode)
        self.assertIn("_episode(source, case, control=control)", source)
        training = inspect.getsource(C._training_arm)
        self.assertIn("model.turn(", training)
        self.assertIn("aprende de la última tarea", training)
        self.assertIn("independent-labels", training)
        self.assertNotIn("torch", training)
        self.assertNotIn("qiskit", training)
        trajectory = inspect.getsource(C._trajectory)
        self.assertIn("bank_weight_hashes(model._banks())", trajectory)
        self.assertIn("UnifiedMemoryView(model).snapshot()", trajectory)
        self.assertIn("model.turn(", trajectory)

    def test_test_label_is_opened_after_validation_only_selection(self):
        source = inspect.getsource(C.campaign)
        self.assertLess(source.index("validation = _evaluate("),
                        source.index("eligible = _eligible("))
        self.assertLess(source.index("candidate_before_test ="),
                        source.index("test_cases = heldout_test()"))
        evaluation = inspect.getsource(C._evaluate)
        self.assertLess(evaluation.index("observations ="),
                        evaluation.index("teachers ="))
        self.assertLess(evaluation.index("_timed_episode("),
                        evaluation.index("native_sample_teacher("))

    def test_no_invented_accuracy_or_reward(self):
        source = inspect.getsource(C.campaign)
        self.assertIn('"candidate_promoted_to_production": False', source)
        self.assertIn('"real_quantum_hardware_used": False', source)
        self.assertIn('if freeze_assets() != original_protected', source)
        self.assertEqual(P.SCHEMA, "BBYQ-U03-C12-native-cross-block-v1")

    def test_trajectory_oracle_revealed_after_both_arms(self):
        source = inspect.getsource(C.campaign)
        self.assertLess(source.index('capacity = {mode: _trajectory('),
                        source.index('_score_trajectory(capacity'))
        self.assertLess(source.index('interference = {mode: _trajectory('),
                        source.index('_score_trajectory(interference'))
        val=[x.seed for x in P.VALIDATION]
        test=[x.seed for x in P.TEST]
        self.assertTrue(set(val).isdisjoint(test))


if __name__ == "__main__":
    unittest.main()
