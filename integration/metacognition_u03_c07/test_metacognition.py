"""C07 tests: provenance, epistemic risk, split isolation, calibration.

These contracts do NOT claim that a real-world source is trustworthy.
"""
from __future__ import annotations

from copy import deepcopy
from math import isfinite
import unittest

from .dataset import (
    DAY, LABELS, PREDICATES, evidence, independent_target, split, trusted,
    unfamiliar_cases, verify_disjoint,
)
from .features import evidence_features, is_unsupported, MODES
from .train import (
    probabilities, quality, selective_quality, select_temperature,
    select_threshold, guarded_action,
)


class MetaEpistemicTests(unittest.TestCase):
    def test_split_reproducibility_and_no_cross_split_leak(self):
        info=verify_disjoint()
        self.assertEqual(info["counts"], {"train":540,"validation":135,"test":180,"challenge":180})
        self.assertTrue(info["subject_source_scenario_disjoint"])
        for name in ("train","validation","test","challenge"):
            a,b=split(name),split(name)
            self.assertEqual(a,b)
            self.assertEqual(len({x.uid for x in a}),len(a))
            self.assertEqual([sum(x.label==i for x in a) for i in range(3)],
                             [len(a)//3]*3)

    def test_independent_scenarios_respect_predeclared_policy(self):
        for name in ("train","validation","test"):
            for row in split(name):
                self.assertEqual(independent_target(row.query,row.evidence),row.label)
                x=evidence_features(row.query,row.evidence)
                self.assertEqual(len(x),10)
                self.assertTrue(all(isfinite(v) for v in x))
                self.assertEqual(x[0],1.0)

    def test_verified_false_is_answerable_not_a_hallucination(self):
        query={"subject":"prueba","predicate":"activo"}
        no=evidence("prueba","activo",0,"registro:1")
        self.assertTrue(trusted(no,query))
        self.assertEqual(independent_target(query,(no,)),0)
        self.assertEqual(evidence_features(query,(no,))[2],.5)

    def test_conflicts_require_two_authorized_matching_opposites(self):
        query={"subject":"A","predicate":"activo"}
        yes=evidence("A","activo",1,"laboratorio:1")
        no=evidence("A","activo",0,"auditor:2")
        unsigned=evidence("A","activo",0,"auditor:3",attested=False)
        stale=evidence("A","activo",0,"auditor:4",age=100,ttl=30)
        mismatched=evidence("A","completo",0,"auditor:5")
        self.assertEqual(independent_target(query,(yes,no)),2)
        self.assertEqual(independent_target(query,(yes,unsigned)),0)
        self.assertEqual(independent_target(query,(yes,stale)),0)
        self.assertEqual(independent_target(query,(yes,mismatched)),0)
        self.assertEqual(evidence_features(query,(yes,no))[3],1.0)
        self.assertEqual(evidence_features(query,(yes,unsigned))[3],0.0)

    def test_reject_tamper_and_untrusted_source(self):
        query={"subject":"A","predicate":"operativo"}
        signed=evidence("A","operativo",1,"laboratorio:1")
        tampered=deepcopy(signed)
        tampered["value"]=0
        self.assertFalse(trusted(tampered,query))
        self.assertFalse(trusted(evidence("A","operativo",1,"unknown:fake"),query))
        self.assertFalse(trusted(evidence("A","operativo",1,"registro:1",age=60,ttl=30),query))
        self.assertFalse(trusted(evidence("B","operativo",1,"registro:1"),query))
        self.assertEqual(independent_target(query,(tampered,)),1)
        self.assertEqual(independent_target(query,()),1)

    def test_no_ablation_receives_label(self):
        q={"subject":"A","predicate":"activo"}
        rows=(evidence("A","activo",1,"laboratorio:1"),)
        for mode in MODES:
            values=evidence_features(q,rows,mode=mode)
            self.assertEqual(len(values),10)
            self.assertTrue(all(type(v) is float for v in values))
        base=evidence_features(q,rows)
        no_contrast=evidence_features(q,rows,mode="no-contrast")
        self.assertEqual(no_contrast[3],0)
        self.assertEqual(base[0:3],no_contrast[0:3])
        with self.assertRaises(ValueError):
            evidence_features(q,rows,mode="unknown")

    def test_ood_predicate_and_malformed_rows_fail_closed(self):
        for query,rows in unfamiliar_cases():
            if query["predicate"] not in PREDICATES:
                self.assertTrue(is_unsupported(query,rows))
            else:
                self.assertEqual(independent_target(query,tuple(rows)),1)
        self.assertTrue(is_unsupported({"subject":"","predicate":"activo"},[]))
        self.assertTrue(is_unsupported({"subject":"A","predicate":"activo"},[None]))
        with self.assertRaises(ValueError):
            evidence_features({"subject":"A","predicate":"activo"},[{}]*25)

    def test_temperature_softmax_and_calibration_nonleakage(self):
        self.assertAlmostEqual(sum(probabilities([-3.0,0.1,1.0],.5)),1.0)
        self.assertGreater(probabilities([20.,-10.,-10.],.5)[0],.99)
        v=split("validation")[:9]
        p=[{"predicted":i%3,"scores":[4.,0.,0.]} for i in range(9)]
        report=quality(v,p,1.)
        self.assertEqual(report["total"],len(v))
        self.assertTrue(0<=report["brier_multiclass"]<=2)
        self.assertTrue(0<=report["ECE_10_bins"]<=1)
        t=select_temperature(v,p)
        self.assertTrue(t>0)
        threshold=select_threshold(v,p,t)
        self.assertTrue(.4<=threshold<=.99)

    def test_unsupported_rejected_despite_overconfidence(self):
        query={"subject":"Alien","predicate":"predice_el_futuro"}
        row=type("Row",(),{"query":query,"evidence":()})()
        prediction={"predicted":0,"scores":[100.,0.,0.]}
        self.assertEqual(guarded_action(row,prediction,.5,.5),1)

    def test_unjustified_abstentions_counted_separately_from_safe_refusals(self):
        examples=split("validation")[:9]
        predictions=[{"predicted":1,"scores":[0.,10.,0.]} for _ in examples]
        result=selective_quality(examples,predictions,1.,.55)
        self.assertEqual(result["answered"],0)
        self.assertEqual(result["unsafe_answers"],0)
        self.assertEqual(result["unjustified_abstentions"],
                         sum(x.label==0 for x in examples))
        self.assertIsNone(result["risk_among_answered"])


if __name__=="__main__":
    unittest.main()
