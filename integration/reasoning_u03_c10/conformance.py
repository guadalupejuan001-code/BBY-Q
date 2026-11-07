#!/usr/bin/env python3
"""C10: require genuine U02 XI proof/mission on disposable original bank clones.

Compare original U02 vs C10 opt-in, preserve all historical byte-identical
snapshots and receipts. Explicitly prove missing source / stale projection /
conflict never produces a native proof. No apk and no model re-training.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import tempfile

from integration.audit_u03_c00.profile import ROOT, MISSION, freeze_assets, apk_files
from integration.memory_u03_c09.view import UnifiedMemoryView, external_claim
from integration.unified.session import Session
from integration.unified.common import key
from .planner import Goal
from .engine import Reasoner
from .session import ReasoningSession


def without_clock(v):
    if isinstance(v,dict):
        return {k: without_clock(x) for k,x in v.items() if k!="elapsed_ms"}
    if isinstance(v,list):
        return [without_clock(x) for x in v]
    return v


def native_trial(klass):
    with tempfile.TemporaryDirectory(prefix="bbyq-c10-sandboxed-original-xi-") as tmp:
        path=Path(tmp)/"single-entity.sqlite"
        outcomes=[]
        with klass(path) as entity:
            planner=entity.reasoning if isinstance(entity,ReasoningSession) else Reasoner(entity)
            def call(identifier,prompt,**kwargs):
                receipt=entity.turn(identifier,prompt,**kwargs)
                if not receipt["ok"]:
                    raise AssertionError("Original XI U02 task failed: "+identifier)
                outcomes.append(without_clock(receipt))
                return receipt
            first=UnifiedMemoryView(entity).snapshot()
            blocked=planner.plan(Goal("prove_alert","Nara"))
            if blocked["status"]!="blocked_missing_VQC_observation":
                raise AssertionError("C10 inferred without a recorded sample")
            if entity.snapshot()["revision"]!=first["revision"]:
                raise AssertionError("C10 mutated source during absence test")

            task=call("mission",MISSION)
            original=entity.snapshot()
            memory=UnifiedMemoryView(entity).snapshot()
            if any(row["kind"]=="vqc_projection" and row["status"]!="current"
                   for row in memory["facts"]):
                raise AssertionError("Original VQC projection not current before training")

            unknown_rule=planner.plan(Goal("plan_mission","Nara","Desconocida",3))
            if unknown_rule["status"]!="blocked_missing_QMemory":
                raise AssertionError("C10 invented an unknown supervised rule")
            conflict=planner.plan(
                Goal("plan_mission","Nara","Faro Azul",3),
                overlay=[external_claim("Faro Azul","valor",0,"unsigned:third-party")])
            if conflict["status"]!="blocked_unverified_disagreement" or conflict["native"] is not None:
                raise AssertionError("C10 auto-accepted a contradictory third-party statement")

            # The original C1 native reasoner is queried without a proof rule.
            # A recognized tool contract is not evidence by itself.
            not_proven=planner.plan(Goal("prove_alert","Nara"))
            if not_proven["status"]!="native_unproven":
                raise AssertionError("C10 fabricated a proof without a native XI rule")
            call("bridge-rule","si alguien es clase cero entonces es alerta")

            before=entity.snapshot()
            history=without_clock(entity.history())
            proved=planner.plan(Goal("prove_alert","Nara"))
            if proved["status"]!="native_proof":
                raise AssertionError("C10 did not authenticate the existing XI Zero proof: "
                                     + str(proved["status"]))
            if not proved["native"]["symbolic_proof_ids"]:
                raise AssertionError("C10 reported a positive native proof with no proof IDs")
            plan=planner.plan(Goal("plan_mission","Nara","Faro Azul",3))
            if plan["status"]!="native_plan":
                raise AssertionError("C10 did not obtain complete QMemory/VQC/QRL/voice native plan")
            if plan["native"]["policy_action"] not in (0,1,2):
                raise AssertionError("C10 native policy action not a bounded XI value")
            if any(x["original_database_writes"] or x["conclusions_are_real_world_truth"]
                   or x["user_actions_executed"] for x in (proved,plan)):
                raise AssertionError("C10 promoted a sandbox result to factual/external action")
            if entity.snapshot()!=before or without_clock(entity.history())!=history:
                raise AssertionError("C10 native sandbox published original database changes")

            call("feedback","aprende de la última tarea")
            stale=planner.plan(Goal("prove_alert","Nara"))
            if stale["status"]!="blocked_stale_VQC_projection" or stale["native"] is not None:
                raise AssertionError("C10 did not reject the obsolete VQC premise")
            if entity.snapshot()["banks"]["memory"] is None:
                raise AssertionError("Original native memory unexpectedly unavailable")
            # Verified original U02 refreshes the VQC projection through XI.
            # No C10 shortcuts are permitted during this step.
            call("original-refresh","dime si observación Nara es alerta")
            after_refresh=UnifiedMemoryView(entity).snapshot()
            proj=next(x for x in after_refresh["facts"]
                      if x["kind"]=="vqc_projection"
                      and x["subject"]==key("observación Nara"))
            if proj["status"]!="current":
                raise AssertionError("U02 native refresh did not restore VQC derivation")
            repaired=planner.plan(Goal("prove_alert","Nara"))
            if repaired["status"] not in ("native_proof","native_unproven"):
                raise AssertionError("C10 skipped native XI after U02 refreshed the premise")

            before_failure=entity.snapshot()
            try:
                entity.turn(
                    "abort",
                    "guarda la regla Otra con valor 0 observa Brisa con muestra 122121 y resuelve desde 3",
                    fail_after=2,
                )
            except RuntimeError:
                pass
            else:
                raise AssertionError("C10 changed original rollback behaviour")
            if entity.snapshot()!=before_failure:
                raise AssertionError("C10 leaked a native partial checkpoint")

            replay=entity.turn("mission",MISSION)
            if without_clock(replay)!=outcomes[0] or entity.snapshot()!=before_failure:
                raise AssertionError("C10 changed original idempotent receipt")
            final=entity.snapshot()
            final_history=without_clock(entity.history())
            summary={
                "receipts":outcomes,
                "starting_sha256":first["view_sha256"],
                "native_proof":proved,
                "native_mission":plan,
                "missing_status":blocked["status"],
                "missing_rule_status":unknown_rule["status"],
                "missing_XI_rule":not_proven["status"],
                "overlay_status":conflict["status"],
                "obsolete_status":stale["status"],
                "refresh_status":repaired["status"],
                "final_snapshot":final,
                "history":final_history,
            }
        with Session(path) as reader:
            if reader.snapshot()!=final or without_clock(reader.history())!=final_history:
                raise AssertionError("Original U02 cannot reload C10 native trace / banks")
        return summary


def main():
    before, apks=freeze_assets(),apk_files()
    original=native_trial(Session)
    candidate=native_trial(ReasoningSession)
    if original!=candidate:
        changed=[k for k in original if original[k]!=candidate.get(k)]
        raise AssertionError("C10 original XI vs planned XI differs: "+str(changed))
    if freeze_assets()!=before or apk_files()!=apks:
        raise AssertionError("C10 changed frozen checkpoints or compiled APK")
    result={
        "passed":True,
        "same_U02_C10_original_receipts_and_native_banks":True,
        "native_C1_Zero_symbolic_proof_present":True,
        "native_QMemory_VQC_Entity_QRL_QChat_plan_present":True,
        "missing_native_proof_rejected":True,
        "missing_user_rule_rejected":True,
        "unverified_conflict_blocked":True,
        "stale_VQC_projection_blocked_until_native_refresh":True,
        "replay_rollback_and_original_restart_identical":True,
        "native_inference_only_inside_disposable_SQLite_copy":True,
        "original_checkpoint_writes":0,
        "frozen_asset_count":len(before),
        "frozen_assets_unchanged":True,
        "apk_built":False,
        "reference_sha256":hashlib.sha256(
            json.dumps(original,ensure_ascii=False,sort_keys=True).encode()
        ).hexdigest(),
        "native_proof_ids":len(original["native_proof"]["native"]["symbolic_proof_ids"]),
        "native_mission_operation_count":len(original["native_mission"]["native"]["XI_operations"]),
    }
    target=ROOT/"build/c10/conformance.json"
    target.parent.mkdir(parents=True,exist_ok=True)
    target.write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n")
    print(json.dumps(result,ensure_ascii=False))


if __name__=="__main__":
    main()
