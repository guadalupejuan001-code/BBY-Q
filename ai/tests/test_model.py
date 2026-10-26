import copy
import math
import unittest

from bbyq.model import choose_action, experience, features, new_entity, predict
from bbyq.world import RelationalWorld


class EntityUnitTests(unittest.TestCase):
    def test_identity_steps_and_predictions(self):
        entity = new_entity("known-identity")
        obs = {"signal": 0.6, "pressure": -0.4}
        self.assertEqual(entity["id"], "known-identity")
        self.assertEqual(entity["steps"], 0)
        before = predict(entity, obs, 1)
        self.assertEqual(before["probability_one"], 0.5)
        trace = experience(entity, obs, 1, 0)
        self.assertEqual(trace["prediction_before_feedback"], 1)
        self.assertEqual(trace["outcome"], 0)
        self.assertEqual(entity["steps"], 1)
        self.assertEqual(entity["model"]["updates"], 1)
        self.assertLess(predict(entity, obs, 1)["probability_one"], 0.5)
        self.assertNotEqual(entity["model"]["weights"]["signal"], 0)

    def test_frozen_control_and_history_bounds(self):
        obs = {"signal": -0.5, "pressure": 0.5}
        frozen = new_entity()
        for i in range(65):
            experience(frozen, obs, -1, i % 2, learn=False)
        self.assertEqual(frozen["steps"], 65)
        self.assertEqual(frozen["model"]["updates"], 0)
        self.assertEqual(len(frozen["recent"]), 32)
        self.assertEqual(frozen["recent"][0]["step"], 34)
        self.assertTrue(all(weight == 0 for weight in frozen["model"]["weights"].values()))

    def test_reject_invalid_inputs_without_state_change(self):
        entity = new_entity()
        original = copy.deepcopy(entity)
        for obs, action, outcome in [
            ({"signal": float("nan"), "pressure": 0.2}, 1, 0),
            ({"signal": 2, "pressure": 0.2}, 1, 0),
            ({"signal": 0, "pressure": 0}, 0, 0),
            ({"signal": 0, "pressure": 0}, 1, 2),
        ]:
            with self.assertRaises(ValueError):
                experience(entity, obs, action, outcome)
            self.assertEqual(entity, original)

    def test_exploration_and_world_separation(self):
        agent = new_entity()
        obs = {"signal": 0.1, "pressure": -0.8}
        world = RelationalWorld(19)
        first_action = choose_action(agent, obs, explore=True)
        self.assertEqual(first_action, -1)
        outcome = world.step(obs, first_action)
        experience(agent, obs, first_action, outcome)
        self.assertEqual(choose_action(agent, obs, explore=True), 1)
        self.assertTrue(0 <= predict(agent, obs, 1)["probability_one"] <= 1)


if __name__ == "__main__":
    unittest.main()
