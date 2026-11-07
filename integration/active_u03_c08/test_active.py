"""C08 data nonleakage, active selection, verified receipt and safety."""
from __future__ import annotations

from dataclasses import replace
import unittest

from integration.metacognition_u03_c07.dataset import independent_target, trusted, evidence
from .dataset import (
    acquire_pool, validation, test_reserved, check_separation,
    synthetic_teacher_confirm, Unlabeled, SIZES,
)
from .learner import (
    _profile, ask_for_verification, acquire, _random_control,
    _verify_selected, BUDGET, BUCKET_QUOTAS, _stage_sample,
)


class ActiveLearningContracts(unittest.TestCase):
    def test_dataset_fresh_counts_and_disjoint_identities(self):
        # DO NOT open the test-reserved data here. C08 campaign opens it
        # only after native training + validation selection are frozen.
        pool, val = acquire_pool(), validation()
        self.assertEqual(len(pool), SIZES["pool"])
        self.assertEqual(len(val), SIZES["validation"])
        self.assertEqual(SIZES["test"],180)
        self.assertEqual(len({p.uid for p in pool}),len(pool))
        self.assertEqual(len({p.uid for p in val}),len(val))
        self.assertFalse({p.uid for p in pool} & {p.uid for p in val})
        self.assertFalse({p.query["subject"] for p in pool} &
                         {p.query["subject"] for p in val})

    def test_unlabeled_cases_cannot_expose_training_targets(self):
        pool=acquire_pool()
        self.assertFalse(any(hasattr(c, "label") for c in pool))
        self.assertFalse(any("label" in c.as_dict() for c in pool))
        self.assertTrue(all(c.partition=="pool" for c in pool))
        # Gold labels are requested only from synthetic_teacher_confirm
        # AFTER acquire(); the selector receives no label field.

    def test_selector_does_not_require_teacher_answers(self):
        pool=acquire_pool()
        # Strictly synthetic native-style scores; full XI run is part of CI.
        predictions=[{"predicted":1, "scores":[.3,.5,-.2]} for _ in pool]
        selected, questions=acquire(pool,predictions)
        self.assertEqual(len(selected),BUDGET)
        self.assertEqual(len(questions),BUDGET)
        groups=[_profile(c)[0] for c in selected]
        self.assertEqual({k:groups.count(k) for k in BUCKET_QUOTAS},BUCKET_QUOTAS)
        self.assertTrue(all(q["status"]=="pending-verification" for q in questions))
        self.assertTrue(all(q["does_not_train_until_confirmed"] for q in questions))
        self.assertTrue(all(q["question"].startswith("¿Puedes") or
                            q["question"].startswith("Hay fuentes") for q in questions))
        self.assertFalse(any(hasattr(c,"label") for c in selected))

    def test_teacher_only_verifies_acquired_pool_cases(self):
        pool=acquire_pool()
        selected=pool[:7]
        confirmed, receipts=_verify_selected(selected)
        self.assertEqual(len(confirmed),len(selected))
        self.assertTrue(all(x.partition=="pool" for x in confirmed))
        self.assertTrue(all(x["verifier"].startswith("synthetic closed-world")
                            and x["real_signature_checked"] is False for x in receipts))
        self.assertTrue(all(r.label==independent_target(r.query,r.evidence)
                            for r in confirmed))
        with self.assertRaises(ValueError):
            synthetic_teacher_confirm(replace(selected[0],partition="test"))

    def test_training_packet_contains_teacher_only_after_confirmation(self):
        example=_verify_selected(acquire_pool()[:1])[0][0]
        packet=_stage_sample(example)
        self.assertIn("call c07_train",packet)
        self.assertIn(str(example.label),packet)
        with self.assertRaises(ValueError):
            _stage_sample(replace(example,partition="test"))

    def test_stress_v2_contains_two_additional_signed_but_irrelevant_records(self):
        candidates=acquire_pool()
        for case in candidates:
            external=[x for x in case.evidence if "-external" in x["source"]]
            attribute=[x for x in case.evidence if "-attribute" in x["source"]]
            self.assertEqual(len(external),1)
            self.assertEqual(len(attribute),1)
            self.assertFalse(trusted(external[0],case.query))
            self.assertFalse(trusted(attribute[0],case.query))
            self.assertTrue(external[0]["attested"] and attribute[0]["attested"])

    def test_signed_irrelevant_is_not_a_supported_fact(self):
        query={"subject":"Prisma","predicate":"activo"}
        other=evidence("Otra","activo",1,"laboratorio:unrelated")
        self.assertFalse(trusted(other,query))
        row=Unlabeled("x",query,(other,),"pool")
        self.assertEqual(_profile(row)[0],"insufficient")
        self.assertEqual(independent_target(query,row.evidence),1)
        pred={"predicted":0,"scores":[10.,0.,0.]}
        q=ask_for_verification(row,pred)
        self.assertIn("observación vigente",q["question"])
        self.assertEqual(q["relevant_records"],0)

    def test_requested_clarification_contains_no_fake_answer(self):
        query={"subject":"Nara","predicate":"completo"}
        present=evidence("Nara","completo",1,"registro:test")
        disputed=evidence("Nara","completo",0,"auditor:test")
        missing=Unlabeled("0",query,(),"pool")
        contradictory=Unlabeled("1",query,(present,disputed),"pool")
        supported=Unlabeled("2",query,(present,),"pool")
        for case in (missing,contradictory,supported):
            prompt=ask_for_verification(case,{"predicted":1,"scores":[0.,1.,0.]})
            self.assertEqual(prompt["status"],"pending-verification")
            self.assertNotIn("respuesta_confirmada",prompt)
            self.assertTrue(prompt["does_not_train_until_confirmed"])

    def test_random_baseline_has_equal_budget_and_determinism(self):
        p=acquire_pool()
        a,b=_random_control(p),_random_control(p)
        self.assertEqual(a,b)
        self.assertEqual(len(a),BUDGET)
        self.assertEqual(len({v.uid for v in a}),BUDGET)


if __name__=="__main__":
    unittest.main()
