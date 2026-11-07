"""C11 regression: no teacher leakage, real model identity and fair ablations."""
from __future__ import annotations

import inspect
import unittest

from .campaign import _eligible, score_runs, _episode, evaluate, _learn_one
from .protocol import (
    Heldout, SCHEMA, MODES, CONTROLS, TRAINING_MISSION,
    TRAINED_SEEDS, validation, heldout_test, separation, controls_must_be_existing,
)
from .native import HEADS


class JointContracts(unittest.TestCase):
    def test_only_original_qualified_XI_modes_and_training_splits(self):
        self.assertTrue(controls_must_be_existing())
        self.assertEqual(len(MODES),3)
        self.assertEqual(len(CONTROLS),5)
        self.assertEqual(len(HEADS),6)
        self.assertEqual(len(validation()),3)
        self.assertEqual(len(heldout_test()),4)
        report=separation((TRAINING_MISSION,),validation(),heldout_test())
        self.assertTrue(report["training_validation_test_seeds_disjoint"])
        self.assertTrue(report["training_validation_test_names_disjoint"])
        self.assertEqual([report["splits"][s]["count"]
                          for s in ("training","validation","test")],[1,3,4])
        self.assertFalse(any(x.seed in TRAINED_SEEDS for x in validation()))

    def test_goal_controls_fail_closed(self):
        from unittest.mock import Mock
        case=Heldout("test","Aurora","Eco Claro",99999)
        with self.assertRaises(ValueError):
            _episode(None,case,control="skip-native-math")
        with self.assertRaises(ValueError):
            _episode(None,case,control="unsafe-teacher-leak")

    def test_source_never_stages_training_labels_during_heldout_inference(self):
        text=inspect.getsource(_episode)
        self.assertIn("model.turn(",text)
        self.assertNotIn("payload=",text)
        self.assertNotIn("labels=",text)
        self.assertNotIn("aprende de la última tarea",text)
        self.assertIn("has_teacher_in_trace",text)
        protocol=inspect.getsource(evaluate)
        self.assertLess(protocol.index("for mode,source in arms.items():"),
                        protocol.index("teachers={"))
        self.assertIn("native_sample_teacher",protocol)
        self.assertEqual(SCHEMA,"BBYQ-U03-C11-coordinated-XI-joint-learning-v1")

    def test_selection_requires_strict_gain_plus_weight_change(self):
        baseline={
            "class_correct":2,"rule_correct":3,
            "supported_faithful":3,"native_receipt_ok":3,
        }
        improved={**baseline,"class_correct":3}
        changes=dict.fromkeys(HEADS,False)
        self.assertFalse(_eligible(baseline,improved,changes))
        changes["entity_weights"]=True
        self.assertTrue(_eligible(baseline,improved,changes))
        self.assertFalse(_eligible(baseline,baseline,changes))
        too_risky={**improved,"supported_faithful":2}
        self.assertFalse(_eligible(baseline,too_risky,changes))

    def test_scoring_retains_failures_and_never_claims_real_world_truth(self):
        cases=(Heldout("validation","Vela","Sol Claro",11111,bit=1),)
        prediction={
            "source_seed":11111,"name":"Vela","control":"normal",
            "receipt_ok":False, "native_class":1,"native_rule":1,
            "native_action":1,"native_goal":6,
            "native_supported":False,
            "native_voice_faithful":False,"native_voice_terminated":False,
            "no_teacher_labels_entered_native_inference":True,
        }
        score=score_runs([prediction],{11111:0},cases)
        self.assertEqual(score["total"],1)
        self.assertEqual(score["class_correct"],0)
        self.assertEqual(score["rule_correct"],1)
        self.assertEqual(score["native_receipt_ok"],0)
        self.assertEqual(score["supported_faithful"],0)
        self.assertFalse(score["raw"][0]["class_correct"])
        self.assertTrue(score["all_inference_without_teacher"])

    def test_feedback_parity_is_native_u02_not_python_weights(self):
        source=inspect.getsource(_learn_one)
        self.assertIn("model.turn(",source)
        self.assertIn("independent-labels",source)
        self.assertIn("explicit-user-result",source)
        self.assertIn("bank_weight_hashes",inspect.getsource(__import__(
            "integration.joint_u03_c11.campaign",
            fromlist=["_read_weights"])._read_weights))
        self.assertNotIn("torch",source)
        self.assertNotIn("qiskit",source)


if __name__=="__main__":
    unittest.main()
