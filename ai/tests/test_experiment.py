import unittest
from bbyq.experiment import campaign, evaluate, one_run
from bbyq.model import new_entity
from bbyq.world import RelationalWorld


class ExperimentTests(unittest.TestCase):
    def test_evaluation_only_reads(self):
        entity = new_entity()
        world = RelationalWorld(42)
        observations = [{"signal": 0.1, "pressure": 0.2},
                        {"signal": -0.8, "pressure": 0.9}]
        original_steps = entity["steps"]
        self.assertTrue(0 <= evaluate(entity, world, observations) <= 1)
        self.assertEqual(entity["steps"], original_steps)

    def test_real_train_holdout_and_negative_control(self):
        row, entity = one_run(42, training=400, testing=240)
        self.assertEqual(row["identical_train_test_inputs"], 0)
        self.assertGreater(row["accuracy_after_learning"], 0.80)
        self.assertGreater(row["accuracy_after_learning"], row["accuracy_frozen_no_learning"])
        self.assertLess(row["negative_parity_accuracy"], 0.7)
        self.assertEqual(entity["steps"], 400)  # the inverted-regime test uses an isolated copy
        self.assertLess(row["old_regime_after_adaptation_retention"], 0.2)

    def test_reproducible_accuracy(self):
        # Timing/RAM are platform-dependent, outcome accuracy should not be.
        a, _ = one_run(43, training=150, testing=100)
        b, _ = one_run(43, training=150, testing=100)
        for key in ("accuracy_after_learning", "accuracy_frozen_no_learning",
                    "negative_parity_accuracy", "new_regime_after_adaptation"):
            self.assertEqual(a[key], b[key])

    def test_campaign_has_unfiltered_failing_results(self):
        report, _ = campaign(seed=42, runs=3, training=100, testing=70)
        self.assertEqual(len(report["per_run"]), 3)
        self.assertIn("old_regime_after_adaptation_retention", report["summary_mean"])
        self.assertFalse(report["native_backend_used_for_campaign"])


if __name__ == "__main__":
    unittest.main()
