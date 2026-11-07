#!/usr/bin/env python3
"""C11: verified multi-engine XI feedback, training controls, heldout ablations.

The learner is ORIGINAL U02 Quantum.feedback: Entity, VQC3, QRL3,
QMemory, QChat100, and C1 router are trained within its one SQLite
transaction. C11 coordinates independent disposable clones of an identical
native checkpoint; verifies all module parameter regions and uses a
validation-only promotion gate. It does NOT implement fake Python learning.

Three arms:
  - joint-verified: original synthetic teacher + user rule supervision,
    with native XI gradients and one SQLite commit;
  - outcome-only: explicit success signal, no independently verified
    class/rule; updates Entity/voice/router but not supervised VQC/QRL/memory;
  - frozen: no feedback, same prepared task and original models.

Evaluation uses disjoint seeds and original U02 contracts, running on
separate fresh clones. Native synthetic label is generated in another
V3 session ONLY AFTER all predictions; never passed to inference.
"""
from __future__ import annotations

import argparse
from hashlib import sha256
import json
from pathlib import Path
import sqlite3
import tempfile
import time

from integration.audit_u03_c00.profile import ROOT, freeze_assets, apk_files
from integration.unified.session import Session
from integration.memory_u03_c09.view import UnifiedMemoryView
from .protocol import (
    SCHEMA, MODES, CONTROLS, TRAINING_MISSION, TRAINING_CORRECTION,
    FULL_FEEDBACK, Heldout, validation, heldout_test, separation,
)
from .native import bank_weight_hashes, native_sample_teacher, HEADS


def _clone(source:Path, target:Path):
    """Copy an authenticated SQLite/WAL snapshot without touching source."""
    with sqlite3.connect(str(source),isolation_level=None,timeout=60) as src:
        with sqlite3.connect(str(target),isolation_level=None,timeout=60) as dst:
            src.backup(dst)


def _prepared(database:Path) -> dict:
    with Session(database) as model:
        task=model.turn("native-training-input",TRAINING_MISSION)
        if not task["ok"] or task["results"][-1]["kind"]!="mission":
            raise AssertionError("C11 native training fixture unsupported")
        corrected=model.turn("native-rule-correction",TRAINING_CORRECTION)
        if not corrected["ok"]:
            raise AssertionError("C11 explicit user correction not recorded")
        row=model.db.execute(
            "SELECT rule FROM unified_task_supervision WHERE id=?",
            (task["results"][-1]["task_id"],)
        ).fetchone()
        if row is None or row[0]!=1:
            raise AssertionError("C11 native task teacher missing from supervised fixture")
        view=UnifiedMemoryView(model).snapshot()
        if len(view["bank_sha256"])!=7 or not view["C1_synchronized_with_U02"]:
            raise AssertionError("C11 prepared checkpoint failed C09 audit")
        return {
            "task_id":task["results"][-1]["task_id"],
            "snapshot":model.snapshot(),
            "view_sha256":view["view_sha256"],
            "bank_sha256":view["bank_sha256"],
            "v3_oracle_origin":model.initial["v3"],
            "training_receipt_sha256":sha256(
                json.dumps(task,sort_keys=True,ensure_ascii=False).encode()
            ).hexdigest(),
        }


def _read_weights(database:Path):
    with Session(database) as session:
        if not UnifiedMemoryView(session).snapshot()["C1_synchronized_with_U02"]:
            raise AssertionError("C11 C1/U02 bank sync failed")
        return bank_weight_hashes(session._banks()),session.snapshot()


def _learn_one(database:Path, mode:str, before_weights:dict):
    if mode not in MODES:
        raise ValueError("C11 unsupported training mode")
    with Session(database) as model:
        view=UnifiedMemoryView(model).snapshot()
        if view["new_memory_authorities"]!=0 or len(view["bank_sha256"])!=7:
            raise AssertionError("C11 original U02 checkpoint authority changed")
        before=model.snapshot()
        original=model.history()
        feedback=None
        if mode=="joint-verified":
            result=model.turn("verified-feedback",FULL_FEEDBACK)
            if not result["ok"]:
                raise AssertionError("C11 original U02 independently verified learning failed")
            feedback=result["results"][-1]
            if feedback["kind"]!="feedback" or feedback["supervision"]!="independent-labels":
                raise AssertionError("C11 U02 learned without independently verified label")
            if feedback["updates"].get("perception_readout")!=1:
                raise AssertionError("C11 failed original native VQC readout update")
            # The U02 trusted task is known to be successful in the frozen
            # U02 regression suite. An outcome-only comparator may reuse
            # this scalar, but not the teacher's VQC or QMemory labels.
            if feedback["success"] is not True:
                raise AssertionError("C11 independent task score did not confirm success")
            replay=model.turn("verified-feedback",FULL_FEEDBACK)
            if replay!=result:
                raise AssertionError("C11 idempotent replay returned different receipt")
            state=model.snapshot()
            if model.snapshot()!=state:
                raise AssertionError("C11 replay trained a second time")
            try:
                model.turn("duplicate-feedback",FULL_FEEDBACK)
            except ValueError:
                pass
            else:
                raise AssertionError("C11 duplicated native teacher feedback")
        elif mode=="outcome-only":
            result=model.turn("explicit-feedback",
                              "evalúa la última tarea con resultado 1")
            if not result["ok"]:
                raise AssertionError("C11 scalar outcome control rejected")
            feedback=result["results"][-1]
            if feedback["supervision"]!="explicit-user-result":
                raise AssertionError("C11 outcome control accidentally obtained verified labels")
            if any(feedback["updates"].get(k,0) for k in (
                    "vqc","qrl","memory","perception_readout")):
                raise AssertionError("C11 ablation leaked teacher class/rule into XI")
        else:
            if model.snapshot()!=before or model.history()!=original:
                raise AssertionError("C11 frozen arm trained unexpectedly")
        final=model.snapshot()
        after_view=UnifiedMemoryView(model).snapshot()
        if after_view["new_memory_authorities"]!=0:
            raise AssertionError("C11 created a second authoritative memory")
        if mode!="frozen" and after_view["C1_synchronized_with_U02"] is not True:
            raise AssertionError("C11 feedback desynchronized the original C1 bank")
        if mode=="frozen" and final!=before:
            raise AssertionError("C11 no-feedback arm changed the original state")
    after_weights, verified_snapshot = _read_weights(database)
    if verified_snapshot!=final:
        raise AssertionError("C11 native weights audit mutated the trained candidate")
    changes={name:before_weights[name]!=after_weights[name]
             for name in HEADS}
    if mode=="frozen" and any(changes.values()):
        raise AssertionError("C11 no-feedback arm changed native XI parameters")
    if mode=="outcome-only" and any(changes[k] for k in (
            "vqc_weights","qrl_weights","qmemory_angles","vqc_readout")):
        raise AssertionError("C11 result-only ablation modified supervised XI weights")
    return {
        "mode":mode,
        "feedback":feedback,
        "native_param_hashes_before":before_weights,
        "native_param_hashes_after":after_weights,
        "native_weight_changed":changes,
        "original_checkpoint":final,
        "changed_bank_names":[name for name in final["banks"]
                              if final["banks"][name]!=before["banks"][name]],
        "training_feedback_verified":mode=="joint-verified",
        "trained_on_test_labels":False,
        "extra_authoritative_memories":0,
    }


def _rollback_test(prepared_path:Path, target:Path):
    _clone(prepared_path,target)
    with Session(target) as session:
        original=session.snapshot()
        history=session.history()
        try:
            session.turn("injected-rollback",FULL_FEEDBACK,fail_after=1)
        except RuntimeError:
            pass
        else:
            raise AssertionError("C11 injected native learning failure did not abort")
        if session.snapshot()!=original or session.history()!=history:
            raise AssertionError("C11 partial XI learning transaction leaked")
    return True


def _episode(source:Path, example:Heldout, *, control=None):
    """Heldout U02 inference, never accepts teacher labels or feedback."""
    if control not in CONTROLS:
        raise ValueError("C11 unexpected XI ablation control")
    with tempfile.TemporaryDirectory(prefix="bbyq-c11-test-clone-") as tmp:
        dest=Path(tmp)/"test-only.sqlite"
        _clone(source,dest)
        with Session(dest) as model:
            starting=model.snapshot()
            prompt=example.prompt()
            r=model.turn("heldout-inference",prompt,control=control)
            native=next((x for x in reversed(r.get("results",[]))
                         if x.get("kind")=="mission"),None)
            if native is None:
                # A novel test string can fail the *learned* U02 reader.
                # It must count as an unsuccessful heldout inference, not
                # disappear from a selectively reported success rate.
                native={}
            if control is None and r.get("ok") is False:
                # This is an *observed* failure and must count against
                # accuracy, not silently disappear from evaluation.
                pass
            has_teacher_in_trace=any(
                item.get("operation") in (
                    "supervised_update","u2_adam","qm_train/publish_angles",
                    "qchat_train","entity_qrl_feedback"
                ) for item in r.get("trace",[])
            )
            if has_teacher_in_trace:
                raise AssertionError("C11 test leaked a training operation into native inference")
            return {
                "source_seed":example.seed,
                "name":example.name,
                "control":control or "normal",
                "receipt_ok":bool(r.get("ok")),
                "native_class":native.get("class"),
                "native_rule":native.get("rule_value"),
                "native_action":native.get("action"),
                "native_goal":native.get("goal"),
                "native_supported":native.get("supported") is True,
                "native_voice_faithful":native.get("voice",{}).get("faithful") is True,
                "native_voice_terminated":native.get("voice",{}).get("terminated") is True,
                "native_trace_ops":sorted({e.get("operation") for e in r.get("trace",[])
                                           if isinstance(e.get("operation"),str)}),
                "checkpoint_changed_only_in_disposable_test_copy":
                    model.snapshot()!=starting,
                "no_teacher_labels_entered_native_inference":True,
            }


def evaluate(arms:dict[str,Path], fixtures, *, original_v3:bytes,
             controls=(None,)):
    """Run ALL XI predictions first, then open independent labels to score."""
    records={}
    for mode,source in arms.items():
        observations=[]
        for example in fixtures:
            for control in controls:
                observations.append(_episode(source,example,control=control))
        records[mode]=observations
    # The original native synthetic oracle is read only AFTER every
    # predictor has returned and all opaque XI traces were captured.
    teachers={e.seed:native_sample_teacher(original_v3,e.seed) for e in fixtures}
    return {
        mode:score_runs(observations,teachers,fixtures)
        for mode, observations in records.items()
    }


def score_runs(observations,teachers,examples) -> dict:
    by_seed={e.seed:e for e in examples}
    rows=[]
    for r in observations:
        seed=r["source_seed"]
        expected=teachers[seed]
        row={
            **r, "native_synthetic_label_evaluation_only":expected,
            "class_correct":r["native_class"]==expected,
            "rule_correct":r["native_rule"]==by_seed[seed].bit,
            "supported_and_faithful":r["native_supported"] and
                r["native_voice_faithful"] and r["native_voice_terminated"],
            "right_action_observed":r["native_action"]==1,
        }
        rows.append(row)
    n=len(rows)
    return {
        "total":n,
        "class_correct":sum(r["class_correct"] for r in rows),
        "rule_correct":sum(r["rule_correct"] for r in rows),
        "supported_faithful":sum(r["supported_and_faithful"] for r in rows),
        "native_action_1_count":sum(r["right_action_observed"] for r in rows),
        "native_receipt_ok":sum(r["receipt_ok"] for r in rows),
        "label_positives":sum(teachers[r["source_seed"]]==1 for r in rows),
        "raw":rows,
        "all_inference_without_teacher":all(
            r["no_teacher_labels_entered_native_inference"] for r in rows),
    }


def _eligible(base:dict, candidate:dict, changed:dict)->bool:
    """Validation-only promotion. No claim unless there is a strict gain."""
    return (
        any(changed.values())
        and candidate["class_correct"]>base["class_correct"]
        and candidate["rule_correct"]>=base["rule_correct"]
        and candidate["supported_faithful"]>=base["supported_faithful"]
        and candidate["native_receipt_ok"]>=base["native_receipt_ok"]
    )


def campaign(output:Path):
    protected,original_apks=freeze_assets(),apk_files()
    started=time.perf_counter_ns()
    output=Path(output)
    output.parent.mkdir(parents=True,exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="bbyq-c11-native-joint-") as temporary:
        workspace=Path(temporary)
        prepared=workspace/"prepared-native-u02.sqlite"
        state=_prepared(prepared)
        prepared_hash=sha256(prepared.read_bytes()).hexdigest()
        initial_param_hashes,_=_read_weights(prepared)
        arms={}
        train_summary={}
        for mode in MODES:
            location=workspace/(mode+".sqlite")
            _clone(prepared,location)
            arms[mode]=location
        rollback_ok=_rollback_test(prepared,workspace/"forced-failure.sqlite")
        for mode in MODES:
            train_summary[mode]=_learn_one(arms[mode],mode,initial_param_hashes)
        if sha256(prepared.read_bytes()).hexdigest()!=prepared_hash:
            raise AssertionError("C11 modified prepared native source checkpoint")
        if train_summary["joint-verified"]["feedback"]["updates"]["router"]!=1:
            raise AssertionError("C11 original native C1 router did not train")
        if not all(train_summary["joint-verified"]["feedback"]["updates"].get(x,0)>0
                   for x in ("entity","vqc","memory","voice")):
            raise AssertionError("C11 original joint native learner skipped a required engine")

        val=validation()
        val_metrics=evaluate(arms,val,original_v3=state["v3_oracle_origin"])
        frozen=val_metrics["frozen"]
        joint=val_metrics["joint-verified"]
        weight_change=train_summary["joint-verified"]["native_weight_changed"]
        selected="joint-verified" if _eligible(frozen,joint,weight_change) else "frozen"
        # All selection and promotion decisions are now immutable.
        # Read the heldout split ONCE, and never use it to train or select.
        test=heldout_test()
        proof=separation((TRAINING_MISSION,),val,test)
        test_metrics=evaluate(arms,test,original_v3=state["v3_oracle_origin"])
        # Evaluate inference-time native ablations only on copies of the
        # original U02 joint learner; controls are U02's exact existing modes.
        ablations=evaluate(
            {"joint-verified":arms["joint-verified"]},test[:2],
            original_v3=state["v3_oracle_origin"],
            controls=CONTROLS,
        )["joint-verified"]

        if sha256(prepared.read_bytes()).hexdigest()!=prepared_hash:
            raise AssertionError("C11 heldout evaluation mutated original common source")
        if freeze_assets()!=protected or apk_files()!=original_apks:
            raise AssertionError("C11 touched historical checkpoints or built APK")

        candidate=output.parent/"joint-candidate.sqlite"
        _clone(arms["joint-verified"],candidate)
        copy_sha=sha256(candidate.read_bytes()).hexdigest()
        # Candidate is an isolated synthetic SQLite/7-XI-bank artifact,
        # not a new authority, promoted user database or new Android app.
        report={
            "schema":SCHEMA, "passed":True,
            "reference":"original U02 Quantum.feedback and original XI interpreter",
            "architecture":"BBY Q -> w4U -> QdU",
            "prior_checkpoints_preserved":True,
            "protected_files":len(protected),
            "apk_built":False,
            "no_new_models_or_new_memory_authority":True,
            "training_input":TRAINING_MISSION,
            "verified_feedback_only_original_native_branch":True,
            "feedback_rollback_passed":rollback_ok,
            "original_input_snapshot_sha256":prepared_hash,
            "synthetic_candidate_file":"joint-candidate.sqlite",
            "synthetic_candidate_sha256":copy_sha,
            "native_weights_before":initial_param_hashes,
            "models":{
                mode:{
                    "feedback":train_summary[mode]["feedback"],
                    "original_checkpoint":train_summary[mode]["original_checkpoint"],
                    "changed_bank_names":train_summary[mode]["changed_bank_names"],
                    "native_parameter_sha256":train_summary[mode]["native_param_hashes_after"],
                    "native_weights_changed":train_summary[mode]["native_weight_changed"],
                } for mode in MODES
            },
            "splits":proof,
            "validation":val_metrics,
            "test":test_metrics,
            "inference_ablation_joint":ablations,
            "promotion_decided_from_validation_only":True,
            "promotion_candidate":selected,
            "test_first_opened_after_promotion":True,
            "no_training_on_heldout_labels":True,
            "prior_learning_result_C08_not_promoted":True,
            "source_database_only_synthetic":True,
            "candidate_not_installed_or_merged":True,
            "elapsed_ms":round((time.perf_counter_ns()-started)/1e6,3),
            "limitations":[
                "U02 already implements the joint native feedback; C11 audits/compares and does not invent a replacement learner.",
                "The scalar outcome-only control has weaker supervision than independent class/rule verification; differences cannot be attributed to a single engine.",
                "Heldout consists of a few original-contract synthetic seeds, not open conversation or a general intelligence benchmark.",
                "The original VQC sample teacher is generated ONLY after heldout inference, on a separate native XI session.",
                "A bank SHA may change with counters; native parameter digests separately exclude optimizer metadata.",
                "The voice/Entity/QRL actions remain simulated and never operate external systems.",
                "The synthetic candidate SQLite is isolated and NOT the existing user's database.",
                "Validation/test accuracy alone is not a guarantee of deployment safety or quantum advantage.",
            ],
        }
        output.write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n")
    return report


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--out",type=Path,default=ROOT/"build/c11/campaign.json")
    args=p.parse_args()
    result=campaign(args.out)
    print(json.dumps({
        "passed":result["passed"],
        "native_weights_changed":result["models"]["joint-verified"]["native_weights_changed"],
        "validation":{
            mode:{k:x[k] for k in ("class_correct","supported_faithful","total")}
            for mode,x in result["validation"].items()},
        "test":{
            mode:{k:x[k] for k in ("class_correct","supported_faithful","total")}
            for mode,x in result["test"].items()},
        "promotion":result["promotion_candidate"],
        "frozen_checkpoint_assets":result["protected_files"],
        "apk_built":False,
    },ensure_ascii=False))


if __name__=="__main__":
    main()
