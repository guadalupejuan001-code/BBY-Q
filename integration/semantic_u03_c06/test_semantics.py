"""C06 input/label separation, novel templates and feature-ablation contracts."""
from __future__ import annotations

import re
import tempfile
import unittest
from pathlib import Path

from .dataset import LABELS, TEMPLATES, split, verify_disjoint
from .features import features, FEATURES


class DatasetSemanticsTests(unittest.TestCase):
    def test_train_validation_heldout_entities_templates_disjoint(self):
        proof = verify_disjoint()
        self.assertTrue(proof["disjoint_templates"])
        self.assertTrue(proof["disjoint_entities"])
        self.assertTrue(proof["disjoint_prompts"])
        self.assertEqual(proof["counts"], {"train": 360, "validation": 90, "test": 120})
        self.assertEqual(len(LABELS), 3)

    def test_label_origin_is_independent_of_c05_inference(self):
        # The independently authored reference label is not read by features.
        corpus = split("train")
        for row in corpus[:30]:
            self.assertEqual(len(features(row.prompt)), FEATURES)
            self.assertEqual(len(features(row.prompt, mode="bag")), FEATURES)
            self.assertEqual(len(features(row.prompt, mode="no-order")), FEATURES)
            self.assertTrue(all(isinstance(x, float) for x in features(row.prompt)))

    def test_unseen_holdout_has_distinct_negation_scope(self):
        for group in ("train", "validation", "test"):
            for row in split(group):
                sem = features(row.prompt)
                if row.label == 0:
                    self.assertEqual(sem[3], 1., row.prompt)
                    self.assertEqual(sem[4], 0., row.prompt)
                elif row.label == 1:
                    self.assertEqual(sem[3], 0., row.prompt)
                    self.assertEqual(sem[4], 1., row.prompt)
                else:
                    self.assertEqual(sem[2], 0., row.prompt)
        # Paired inputs share the same bag-level presence of action and "no",
        # but differ in whether negation binds the action or a later topic.
        prohibit = features("no definas Memoria")
        exclude = features("define Memoria no Datos")
        self.assertNotEqual(prohibit[3:5], exclude[3:5])
        self.assertEqual(prohibit[3:5], (1.,0.))
        self.assertEqual(exclude[3:5], (0.,1.))

    def test_removing_order_removes_only_semantic_relations(self):
        for row in split("test")[:25]:
            original = features(row.prompt)
            cut = features(row.prompt, mode="no-order")
            self.assertEqual(original[:3], cut[:3])
            self.assertEqual(original[6:], cut[6:])
            self.assertEqual(cut[3:6], (0., 0., 0.))
            if original[3] or original[4]:
                self.assertNotEqual(original, cut)

    def test_deterministic_generation(self):
        first = split("test")
        second = split("test")
        self.assertEqual(first, second)
        self.assertEqual(len({row.uid for row in first}), 120)

    def test_templates_are_not_labels_in_source_record(self):
        for name in TEMPLATES:
            for text, target in TEMPLATES[name]:
                self.assertIn("{a}", text)
                self.assertIn(target, (0,1,2))
                self.assertNotIn("prohibit_action", text)
                self.assertNotIn("exclude_topic", text)
                self.assertNotIn("affirm_action", text)

    def test_feature_modes_fail_closed(self):
        with self.assertRaises(ValueError):
            features("define memoria", mode="unknown")


if __name__ == "__main__":
    unittest.main()
