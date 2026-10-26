"""E002 control, recall, safety and no oracle context labels."""
import copy
import math
import unittest

from bbyq.context import MAX_ARCHIVED, context_inspect, contextual_experience
from bbyq.context_experiment import context_campaign, one_context_run
from bbyq.experiment import evaluate
from bbyq.model import FEATURES, experience, new_entity, predict, validate_entity
from bbyq.world import RelationalWorld


class ContextTests(unittest.TestCase):
    def test_recall_is_real_not_a_new_learner_and_exceeds_baseline(self):
        for seed in range(42, 47):
            with self.subTest(seed=seed):
                row, agent = one_context_run(seed)
                self.assertGreater(row['first_regime_accuracy'], .84)
                self.assertGreater(row['inverted_regime_accuracy'], .84)
                self.assertGreater(row['recovered_original_accuracy'], .84)
                self.assertGreater(row['recovered_original_accuracy'],
                                   row['single_model_recovered_original_accuracy'])
                self.assertEqual(row['context_count'], 2)
                self.assertEqual(row['context_switches'], 2)
                self.assertEqual([x['type'] for x in row['switch_events']],
                                 ['created', 'recalled'])
                self.assertEqual(agent['steps'], 400*2+36)
                validate_entity(agent)

    def test_feedback_never_masquerades_as_prior_prediction(self):
        entity = new_entity('test-trace')
        # Create a mature predictor that confidently expects success.
        entity['model']['weights']['bias'] = 10.0
        entity['model']['updates'] = 100
        entity['model']['active_updates'] = 100
        obs = {'signal': 0, 'pressure': 0}
        for _ in range(2):
            contextual_experience(entity, obs, 1, 0)
        prior = predict(entity, obs, 1)
        self.assertEqual(prior['prediction'], 1)
        record = contextual_experience(entity, obs, 1, 0)
        self.assertEqual(record['context_transition'], 'created')
        self.assertEqual(record['prediction_before_feedback'], 1)
        self.assertAlmostEqual(record['probability_before_feedback'],
                               prior['probability_one'], places=7)
        self.assertNotEqual(record['probability_before_feedback'],
                            record['learning_probability_after_selection'])
        self.assertEqual(record['context_prior'], 0)
        self.assertEqual(record['context_active'], 1)
        self.assertAlmostEqual(record['learning_probability_after_selection'], .5)
        self.assertEqual(context_inspect(entity)['total_contexts'], 2)

    def test_no_external_label_and_immutable_holdout(self):
        entity = new_entity('immutable-evaluation')
        world = RelationalWorld(19)
        for i in range(150):
            obs = world.observation(__import__('random').Random(i))
            action = -1 if i % 2 else 1
            contextual_experience(entity, obs, action, world.step(obs, action))
        original = copy.deepcopy(entity)
        evaluate(entity, world, [{'signal': -.3, 'pressure': .7},
                                 {'signal': .2, 'pressure': -.8}])
        self.assertEqual(entity, original)
        self.assertEqual(context_inspect(entity)['total_contexts'], 1)

    def test_context_budget_rejects_creation_without_evicting(self):
        entity = new_entity('bounded')
        model = entity['model']
        model['weights']['bias'] = 10.0
        model['updates'] = model['active_updates'] = 100
        model['archived'] = [
            {'id': i, 'weights': dict(model['weights']), 'updates': 60}
            for i in range(1, MAX_ARCHIVED + 1)]
        model['next_context'] = 4
        for _ in range(5):
            contextual_experience(entity, {'signal': 0.0, 'pressure': 0.0}, 1, 0)
        self.assertEqual(context_inspect(entity)['total_contexts'], 4)
        self.assertTrue(context_inspect(entity)['bound_reached'])
        self.assertEqual(entity['model']['switches'], 0)
        self.assertEqual(entity['model']['active_context'], 0)

    def test_validation_rejects_malformed_archive_and_nan(self):
        entity = new_entity('safety')
        original = copy.deepcopy(entity)
        with self.assertRaises(ValueError):
            contextual_experience(entity, {'signal': float('nan'), 'pressure': 0}, 1, 1)
        self.assertEqual(entity, original)
        entity['model']['archived'].append({'id': 0, 'updates': 0,
                                             'weights': {k: 0. for k in FEATURES}})
        with self.assertRaises(ValueError):
            validate_entity(entity)

    def test_legacy_v1_model_migrates_on_next_contextual_step(self):
        entity = new_entity('legacy-compatible')
        for name in ('active_context', 'next_context', 'active_updates',
                     'archived', 'switches', 'surprise_streak'):
            entity['model'].pop(name)
        for _ in range(80):
            experience(entity, {'signal': .2, 'pressure': .1}, 1, 1)
        trace = contextual_experience(entity, {'signal': .2, 'pressure': .1}, 1, 1)
        self.assertEqual(trace['context_prior'], 0)
        self.assertEqual(entity['model']['active_updates'], 81)
        self.assertEqual(entity['model']['updates'], 81)
        validate_entity(entity)

    def test_campaign_reproducible_predictions(self):
        a, _ = context_campaign(seed=41, runs=2, training=150, testing=80, recovery=24)
        b, _ = context_campaign(seed=41, runs=2, training=150, testing=80, recovery=24)
        for x, y in zip(a['per_run'], b['per_run']):
            for key in ('first_regime_accuracy', 'inverted_regime_accuracy',
                        'recovered_original_accuracy', 'context_count', 'context_switches'):
                self.assertEqual(x[key], y[key])
        self.assertFalse(a['native_backend_used_for_campaign'])


if __name__ == '__main__':
    unittest.main()
