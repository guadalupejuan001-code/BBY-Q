"""C10: DAG constraints, typed premises and fail-closed provenance, no XI runner."""
from __future__ import annotations

from copy import deepcopy
import unittest

from integration.memory_u03_c09.view import external_claim
from .engine import check_plan
from .planner import Goal, steps, ordered, original_native_prompt


def audited():
    return {
        "schema":"BBYQ-U03-C09-read-only-memory-v1",
        "read_only":True,
        "new_memory_authorities":0,
        "C1_synchronized_with_U02":True,
        "view_sha256":"consistent-checkpoint", "revision":7,
        "stale_projections":[],
        "bank_sha256":{"v3":"sha-v3","memory":"sha-memory"},
        "facts":[
            {"kind":"vqc_observation","subject":"observación nara",
             "predicate":"input_sha256","value":"sample-sha"},
            {"kind":"vqc_projection","subject":"observación nara",
             "predicate":"clase","value":0,"status":"current",
             "bank_sha256":"sha-v3","input_sha256":"sample-sha"},
            {"kind":"qmemory_association","subject":"faro azul",
             "predicate":"valor","value":1,"status":"recorded",
             "provenance":"explicit-user-supervision"},
        ],
    }


class PlannerContractTests(unittest.TestCase):
    def test_two_native_goals_are_original_and_nonmutating(self):
        for goal in (
            Goal("prove_alert","Nara"),
            Goal("plan_mission","Nara","Faro Azul",3),
        ):
            graph=steps(goal)
            order=ordered(graph)
            self.assertEqual(len(order),len(graph))
            self.assertEqual(order,[node["id"] for node in graph])
            self.assertTrue(all(not node["may_mutate_original_checkpoint"]
                                for node in graph))
            self.assertEqual(sum(node["runs_native_XI"] for node in graph),1)
            self.assertTrue(all(node["execution"]=="serial" for node in graph))
            self.assertEqual(graph[-3]["bank"],"original-XI")
        self.assertEqual(original_native_prompt(Goal("prove_alert","Nara")),
                         "dime si observación Nara es alerta")
        self.assertEqual(original_native_prompt(Goal("plan_mission","Nara","Faro Azul",3)),
                         "resuelve Nara usando la regla Faro Azul desde 3")

    def test_invalid_goals_never_get_dispatched(self):
        for x in (
            Goal("invent_agility","Nara"), Goal("prove_alert","Nara!",None),
            Goal("prove_alert","Nara","Faro Azul"),
            Goal("plan_mission","Nara",None),
            Goal("plan_mission","Nara","Faro Azul",True),
            Goal("plan_mission","Nara","Faro Azul",7),
            Goal("prove_alert","a"*80),
        ):
            with self.subTest(x=x),self.assertRaises(ValueError):
                x.validate()

    def test_unknown_edge_and_cycle_are_rejected(self):
        goal=Goal("prove_alert","Nara")
        graph=steps(goal)
        duplicate=deepcopy(graph);duplicate.append(deepcopy(duplicate[0]))
        with self.assertRaisesRegex(ValueError,"duplicate"):
            ordered(duplicate)
        invalid=deepcopy(graph)
        invalid[1]["dependencies"]=("some-unknown-node",)
        with self.assertRaisesRegex(ValueError,"unknown"):
            ordered(invalid)
        cycle=deepcopy(graph)
        cycle[0]["dependencies"]=(cycle[-1]["id"],)
        with self.assertRaisesRegex(ValueError,"cyclic"):
            ordered(cycle)

    def test_current_unchanged_native_premises_are_only_ready_not_true(self):
        memory=audited()
        before=deepcopy(memory)
        for goal in (
            Goal("prove_alert","Nara"),
            Goal("plan_mission","Nara","Faro Azul",3),
        ):
            proof=check_plan(goal,memory)
            self.assertEqual(proof["status"],"ready_for_native")
            self.assertIsNone(proof["native"])
            self.assertFalse(proof["conclusions_are_real_world_truth"])
            self.assertEqual(proof["original_database_writes"],0)
        self.assertEqual(memory,before)

    def test_stale_projections_block_even_if_native_class_binary(self):
        memory=audited()
        projection=next(x for x in memory["facts"] if x["kind"]=="vqc_projection")
        projection["status"]="stale"
        result=check_plan(Goal("prove_alert","Nara"),memory)
        self.assertEqual(result["status"],"blocked_stale_VQC_projection")
        projection["status"]="current"
        memory["stale_projections"]=["observación nara"]
        result=check_plan(Goal("plan_mission","Nara","Faro Azul"),memory)
        self.assertEqual(result["status"],"blocked_stale_VQC_projection")

    def test_missing_authorized_premise_never_uses_unverified_overlay(self):
        memory=audited()
        memory["facts"]=[r for r in memory["facts"]
                         if r["kind"]!="qmemory_association"]
        counter=external_claim("Faro Azul","valor",1,"anonymous:anybody")
        result=check_plan(Goal("plan_mission","Nara","Faro Azul"),memory,
                          overlay=[counter])
        self.assertEqual(result["status"],"blocked_missing_QMemory")
        memory["facts"]=[r for r in memory["facts"]
                         if r["kind"]!="vqc_observation"]
        self.assertEqual(check_plan(Goal("prove_alert","Nara"),memory)["status"],
                         "blocked_missing_VQC_observation")

    def test_legacy_sync_required_before_all_reasoning(self):
        memory=audited()
        memory["C1_synchronized_with_U02"]=False
        self.assertEqual(check_plan(Goal("prove_alert","Nara"),memory)["status"],
                         "blocked_legacy_desynchronization")

    def test_conflicting_external_hash_is_detected_not_auto_accepted(self):
        goal=Goal("plan_mission","Nara","Faro Azul",3)
        mismatch=external_claim("Faro Azul","valor",0,"web:unsigned")
        result=check_plan(goal,audited(),overlay=(mismatch,))
        self.assertEqual(result["status"],"blocked_unverified_disagreement")
        self.assertEqual(result["unverified_overlay_count"],1)
        self.assertEqual(result["original_database_writes"],0)
        agreeing=external_claim("Faro Azul","valor",1,"web:unsigned")
        ok=check_plan(goal,audited(),overlay=(agreeing,))
        self.assertEqual(ok["status"],"ready_for_native")
        forged=dict(mismatch,content_sha256="0"*64)
        with self.assertRaises(ValueError):
            check_plan(goal,audited(),overlay=(forged,))

    def test_class_conflict_blocks_native_proof(self):
        overlay=external_claim("observación Nara","clase",1,
                               "source:unverified")
        result=check_plan(Goal("prove_alert","Nara"),audited(),overlay=(overlay,))
        self.assertEqual(result["status"],"blocked_unverified_disagreement")

    def test_all_new_authorities_and_malformed_views_rejected(self):
        memory=audited()
        memory["new_memory_authorities"]=1
        with self.assertRaisesRegex(ValueError,"authorities"):
            check_plan(Goal("prove_alert","Nara"),memory)
        memory["new_memory_authorities"]=0
        memory["schema"]="faked"
        with self.assertRaisesRegex(ValueError,"C09"):
            check_plan(Goal("prove_alert","Nara"),memory)
        with self.assertRaises(ValueError):
            check_plan(Goal("prove_alert","Nara"),audited(),overlay=[{}]*13)


if __name__=="__main__":
    unittest.main()
