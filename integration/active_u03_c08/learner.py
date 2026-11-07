"""Native C08 active learning with a VERIFIED feedback gate and equal-budget control.

The acquisition selector consumes *unlabeled* cases, XI scores and typed
observations. Only AFTER selection is there a synthetic teacher confirmation.
Real-world evidence cannot be authenticated by this toy content-hash policy.

No C07 CHALLENGE sample or label enters acquisition, native training,
validation selection or hyperparameter tuning. A NEW C08 test is generated
only after all three variant policies and checkpoints have been frozen.
"""
from __future__ import annotations

import argparse
from dataclasses import dataclass
from hashlib import sha256
import json
from pathlib import Path
import random
import shutil
import struct
import tempfile
import time

from integration.audit_u03_c00.profile import ROOT, freeze_assets, apk_files
from integration.unified.common import C1
from integration.metacognition_u03_c07.dataset import trusted
from integration.metacognition_u03_c07.features import evidence_features
from integration.metacognition_u03_c07.train import (
    BASE, NATIVE, infer, quality, selective_quality,
    select_temperature, select_threshold, native_validation,
)
from .dataset import (
    Unlabeled, Labeled, acquire_pool, validation, test_reserved,
    synthetic_teacher_confirm, check_separation, SIZES, PROTOCOL,
)

BUDGET = 96
ROUNDS = 2
NATIVE_STEPS_BUDGET = BUDGET * ROUNDS
BUCKET_QUOTAS = {"supported": 52, "conflicting": 22, "insufficient": 22}


def native_weight_digest(file: Path) -> str:
    """Hash ONLY the 30 learned XI coefficients; exclude training counters.

    A different RVPC2 SHA can merely mean that a counter advanced.
    Real native parameter learning is proven only by this independent hash.
    """
    with C1.Model(file, ["<pad>"], ["<eos>"]) as model:
        model.library += "\n" + NATIVE.read_text()
        weights = model.memory(BASE + 1024, 3 * 10 * 8)
        return sha256(weights).hexdigest()


def _profile(case: Unlabeled) -> tuple[str, int, int]:
    qualified = [row for row in case.evidence if trusted(row, case.query)]
    values = {row["value"] for row in qualified}
    bucket = (
        "insufficient" if not values
        else "conflicting" if len(values) == 2
        else "supported"
    )
    relevant = sum(
        row.get("subject") == case.query["subject"]
        and row.get("predicate") == case.query["predicate"]
        for row in case.evidence
    )
    distractors = len(case.evidence) - relevant
    return bucket, len(qualified), distractors


def _margin(prediction) -> float:
    sorted_scores = sorted(prediction["scores"], reverse=True)
    return float(sorted_scores[0] - sorted_scores[1])


def ask_for_verification(case: Unlabeled, prediction: dict) -> dict:
    """Question for a *future* authorized teacher; no auto ingestion."""
    bucket, qualified, distractors = _profile(case)
    q = case.query
    if bucket == "insufficient":
        text = (f"¿Puedes aportar una observación vigente y verificable sobre "
                f"«{q['subject']} — {q['predicate']}», con su procedencia?")
    elif bucket == "conflicting":
        text = (f"Hay fuentes pertinentes opuestas acerca de "
                f"«{q['subject']} — {q['predicate']}». "
                "¿Qué comprobación independiente puede resolver el conflicto?")
    else:
        text = (f"¿Puedes confirmar la relación entre la evidencia pertinente "
                f"y «{q['subject']} — {q['predicate']}», "
                "descartando las observaciones de otras entidades?")
    return {
        "uid": case.uid, "question": text,
        "source": "synthetic acquisition only",
        "proposed_action": bucket,
        "native_prediction": int(prediction["predicted"]),
        "relevant_records": qualified, "distractors": distractors,
        "status": "pending-verification",
        "does_not_train_until_confirmed": True,
    }


def acquire(candidates: list[Unlabeled], prediction: list[dict],
            budget=BUDGET) -> tuple[list[Unlabeled], list[dict]]:
    """Acquisition does not take or inspect a supervised target label.

    More coverage is allocated to supported-but-distracted observations,
    C07's documented weakness, with explicit exploration quotas for
    missing/conflicting situations so safety behavior does not vanish.
    """
    if len(candidates) != len(prediction) or budget != sum(BUCKET_QUOTAS.values()):
        raise ValueError("C08 candidate and budget mismatch")
    grouped = {name: [] for name in BUCKET_QUOTAS}
    for case, pred in zip(candidates, prediction):
        bucket, support, distractors = _profile(case)
        if pred["predicted"] not in (0, 1, 2):
            raise ValueError("C08 invalid XI prediction")
        margin = _margin(pred)
        # This priority uses only the native prediction and observable
        # provenance/distractors, NEVER the reference training target.
        uncertain = 1/(1+margin)
        probable_false_abstention = int(
            bucket == "supported" and pred["predicted"] == 1
        )
        score = (probable_false_abstention * 100
                 + 10*uncertain
                 + 2*min(distractors,4)
                 + int(pred["predicted"]==1)
                 + min(support,3)/10)
        grouped[bucket].append((score, case.uid, case, pred))
    chosen = []
    records = []
    for bucket, count in BUCKET_QUOTAS.items():
        options = sorted(grouped[bucket], key=lambda row: (-row[0], row[1]))
        if len(options) < count:
            raise ValueError("C08 insufficient unlabeled candidates in "+bucket)
        for score, _, case, pred in options[:count]:
            chosen.append(case)
            records.append({
                **ask_for_verification(case, pred),
                "priority": round(score, 6),
            })
    if len(chosen) != budget or len({c.uid for c in chosen}) != budget:
        raise AssertionError("C08 acquisition reused a candidate")
    return chosen, records


def _random_control(candidates: list[Unlabeled], budget=BUDGET):
    """Same unlabeled pool, number of verified labels and native updates."""
    return random.Random(2026110808).sample(candidates, budget)


def _verify_selected(selected: list[Unlabeled]) -> tuple[list[Labeled], list[dict]]:
    verified = []
    receipts = []
    for case in selected:
        # This is the ONLY point where the independent synthetic oracle
        # creates a class label, after the selection is immutable.
        receipt = synthetic_teacher_confirm(case)
        if receipt["real_signature_checked"] is not False:
            raise AssertionError("C08 falsely claimed a real cryptographic signature")
        verified.append(Labeled(case.uid, case.query, case.evidence,
                                receipt["label"], "pool"))
        receipts.append(receipt)
    return verified, receipts


def _train_rounds(start: Path, cases: list[Labeled],
                  folder: Path, name: str, validation_data: list[Labeled],
                  rounds: int = ROUNDS) -> dict:
    outputs = []
    with C1.Model(start, ["<pad>"], ["<eos>"]) as model:
        model.library += "\n" + NATIVE.read_text()
        pre = struct.unpack("<q", model.memory(BASE,8))[0]
        mistakes_before = struct.unpack("<q", model.memory(BASE+24,8))[0]
        for epoch in range(1,rounds+1):
            examples = list(cases)
            random.Random(2026110809+epoch).shuffle(examples)
            for index in range(0,len(examples),32):
                program = "".join(
                    _stage_sample(case) for case in examples[index:index+32]
                )
                model.run(program)
            now = struct.unpack("<q",model.memory(BASE,8))[0]
            if now-pre != epoch*len(cases):
                raise AssertionError("C08 did not train each verified sample in native XI")
            candidate = folder / f"{name}-round-{epoch}.rvp"
            model.s.save(candidate)
            mistake_now = struct.unpack("<q",model.memory(BASE+24,8))[0]
            outputs.append((candidate, now, mistake_now-mistakes_before))
    # Original XI weights are reopened in distinct native processes.
    scores = []
    for epoch,(file, count, corrected) in enumerate(outputs,1):
        observations = native_validation(file, validation_data, "provenance")
        temp = select_temperature(validation_data, observations)
        threshold = select_threshold(validation_data, observations, temp)
        raw = quality(validation_data, observations, temp)
        selective = selective_quality(validation_data, observations, temp, threshold)
        # Model selection by fresh validation only:
        # maximize correct actions then coverage; penalize missed conflicts
        # and unsafe answers. Do not favor a candidate based on heldout.
        rank = (
            -selective["unsafe_answers"],
            -selective["conflicts_missed"],
            selective["correct_actions"],
            selective["correct_answered"],
            -selective["unjustified_abstentions"],
            -raw["brier_multiclass"],
        )
        scores.append({
            "round": epoch, "path": file, "rank": rank, "seen":count,
            "native_weight_corrections": corrected,
            "validation":raw, "selective":selective,
            "temperature":temp, "threshold":threshold,
        })
    chosen = max(scores,key=lambda v:v["rank"])
    final = folder / (name+"-chosen.rvp")
    shutil.copyfile(chosen["path"], final)
    return {
        "mode":name, "file":final,
        "selected_round":chosen["round"],
        "native_weight_corrections":chosen["native_weight_corrections"],
        "training_updates":len(cases)*chosen["round"],
        "full_training_updates":len(cases)*rounds,
        "verified_labels":len(cases),
        "temperature":chosen["temperature"],
        "answer_threshold":chosen["threshold"],
        "validation":chosen["validation"],
        "validation_selective":chosen["selective"],
        "checkpoints_evaluated":[
            {k:v for k,v in item.items() if k not in ("path","rank")}
            for item in scores
        ],
        "sha256":sha256(final.read_bytes()).hexdigest(),
    }


def _stage_sample(case: Labeled):
    from integration.metacognition_u03_c07.train import stage_vector
    if case.partition != "pool" or case.label not in (0,1,2):
        raise ValueError("C08 unverified native training example")
    return (
        stage_vector(evidence_features(case.query,case.evidence))
        + f"store64 {BASE+8} {case.label}\ncall c07_train\n"
    )


def _evaluate(file: Path, data: list[Labeled], temperature, threshold) -> dict:
    p = native_validation(file,data,"provenance")
    return {
        "native": quality(data,p,temperature),
        "selective": selective_quality(data,p,temperature,threshold),
        "raw_prediction_sha256":sha256(
            json.dumps(p,sort_keys=True).encode()
        ).hexdigest(),
    }


def campaign(output: Path, c07_checkpoint: Path, c07_report: Path) -> dict:
    before, apks = freeze_assets(), apk_files()
    base = json.loads(Path(c07_report).read_text())
    if not base.get("passed") or base.get("mode_selected") != "provenance":
        raise ValueError("C08 cannot use unverified C07 training report")
    original_sha = sha256(Path(c07_checkpoint).read_bytes()).hexdigest()
    if original_sha != base["trained_checkpoint_sha256"]:
        raise ValueError("C08 original C07 bank SHA-256 mismatch")
    if sha256(NATIVE.read_bytes()).hexdigest() != base["source_sha256"]:
        raise ValueError("C08 XI source no longer matches C07 bank")

    pool, val = acquire_pool(), validation()
    output = Path(output)
    output.parent.mkdir(parents=True, exist_ok=True)
    started = time.perf_counter_ns()

    # The first (native) pass has no access to any pool label.
    predictions = native_validation(c07_checkpoint,pool,"provenance")
    selected, questions = acquire(pool,predictions)
    random_selected = _random_control(pool)
    native_selected_sha = sha256(json.dumps(
        [x.uid for x in selected],sort_keys=True).encode()
    ).hexdigest()

    # All acquisition decisions are frozen BEFORE any teacher is queried.
    active_data, receipts = _verify_selected(selected)
    random_data, random_receipts = _verify_selected(random_selected)
    with tempfile.TemporaryDirectory(prefix="bbyq-c08-train-only-") as dirname:
        folder = Path(dirname)
        trained = [
            _train_rounds(c07_checkpoint,active_data,folder,"active",val),
            _train_rounds(c07_checkpoint,random_data,folder,"random",val),
        ]
        # Fair comparison: baseline is calibrated on exactly the same
        # NEW validation set, not evaluated with a privileged threshold.
        original_predictions = native_validation(c07_checkpoint,val,"provenance")
        base_temp = select_temperature(val,original_predictions)
        base_threshold = select_threshold(val,original_predictions,base_temp)
        base_record = {
            "mode":"frozen-C07",
            "native_weight_corrections":0,
            "file":Path(c07_checkpoint),
            "temperature":base_temp,
            "answer_threshold":base_threshold,
            "validation":quality(val,original_predictions,base_temp),
            "validation_selective":selective_quality(
                val,original_predictions,base_temp,base_threshold),
            "verified_labels":0, "training_updates":0,
            "sha256":original_sha,
        }
        # Which model is eligible is determined exclusively by validation
        # and risk. Active learning is NOT promoted just for existing.
        baseline_sel = base_record["validation_selective"]
        active_sel = trained[0]["validation_selective"]
        is_eligible = (
            active_sel["unsafe_answers"] == 0
            and active_sel["conflicts_missed"] <= baseline_sel["conflicts_missed"]
            and active_sel["correct_actions"] >= baseline_sel["correct_actions"]
            and active_sel["unjustified_abstentions"] <= baseline_sel["unjustified_abstentions"]
        )
        promoted_mode = "active" if is_eligible and (
            active_sel["correct_actions"] > baseline_sel["correct_actions"]
            or active_sel["unjustified_abstentions"] < baseline_sel["unjustified_abstentions"]
        ) else "frozen-C07"

        # The C08 test generator is FIRST called here, after all selection,
        # hyperparameters, eligibility and model promotion are frozen.
        test = test_reserved()
        separation = check_separation(pool,val,test)
        comparators = [base_record]+trained
        for candidate in comparators:
            candidate["heldout"] = _evaluate(
                candidate["file"],test,candidate["temperature"],
                candidate["answer_threshold"],
            )

        initial_weight_sha = native_weight_digest(c07_checkpoint)
        model_weights = {
            "frozen-C07":initial_weight_sha,
            "active":native_weight_digest(trained[0]["file"]),
            "random":native_weight_digest(trained[1]["file"]),
        }
        active_output = output.parent / "active-trained.rvp"
        shutil.copyfile(trained[0]["file"],active_output)
        if sha256(active_output.read_bytes()).hexdigest()!=trained[0]["sha256"]:
            raise AssertionError("C08 saved checkpoint failed SHA-256")
        # Reopen both new and frozen models to ensure no mutating side
        # effects from analysis or from the comparison of variants.
        if sha256(Path(c07_checkpoint).read_bytes()).hexdigest()!=original_sha:
            raise AssertionError("C08 modified its C07 prerequisite")
        if freeze_assets()!=before or apk_files()!=apks:
            raise AssertionError("C08 changed older checkpoint or generated APK")

        report = {
            "schema":"BBYQ-U03-C08-verified-active-learning-v1",
            "stress_protocol":PROTOCOL,
            "initial_pilot":"GitHub Actions #42388230030, original C08 test was 180/180 for frozen-C07, active and random",
            "pilot_used_for_native_training":False,
            "pilot_used_for_validation_selection":False,
            "fresh_stress_test_first_opened_after_selection":True,
            "passed":True,
            "native_XI_online_updates":True,
            "native_model_abi":"existing C07 c07_train, c07_predict",
            "source_model_sha256":original_sha,
            "active_model_sha256":trained[0]["sha256"],
            "native_weight_sha256_by_mode":model_weights,
            "native_weights_changed_vs_C07":{
                mode:(digest!=initial_weight_sha)
                for mode,digest in model_weights.items()
            },
            "native_weight_corrections_by_mode":{
                mode["mode"]:mode.get("native_weight_corrections",0)
                for mode in comparators
            },
            "new_XI_weight_learning_demonstrated":(
                model_weights["active"]!=initial_weight_sha
            ),
            "trained_file":"active-trained.rvp",
            "selected_before_teacher_sha256":native_selected_sha,
            "pool_unlabeled_count":len(pool),
            "verified_teacher_receipts":len(receipts),
            "random_teacher_receipts":len(random_receipts),
            "verification_questions":questions,
            "teacher_provenance":"synthetic closed-world explicit hash/issuer policy only; no real signatures",
            "budget_candidates":BUDGET,
            "epochs_budget":ROUNDS,
            "no_training_on_C07_CHALLENGE":True,
            "C08_test_opened_only_after_selection":True,
            "promotion_decided_on_validation_only":True,
            "promotion_mode":promoted_mode,
            "partition":separation,
            "comparisons":[
                {k:v for k,v in candidate.items() if k!="file"}
                for candidate in comparators
            ],
            "all_checkpoints_frozen_count":len(before),
            "all_prior_checkpoints_sha256_unchanged":True,
            "apk_built":False,
            "runtime_wall_ms":round((time.perf_counter_ns()-started)/1e6,3),
            "limitations":[
                "Oracle feedback is simulated from a declared evidence policy, NOT a human or independent external verification.",
                "Acquisition may use provenance flags and native margins but never any pool class labels before selection.",
                "A low ECE on synthetic conditions does not demonstrate truthfulness or calibration in natural conversation.",
                "Native online XI updates do not change C1/VQC/QRL/QMemory trained weights.",
                "Comparison evaluates synthetic new-source distractors; C07 CHALLENGE labels were not reused.",
                "Model promotion is validation-only and may reject an apparently useful candidate.",
            ],
        }
        output.write_text(json.dumps(report,ensure_ascii=False,indent=2,default=str)+"\n")
    return report


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--c07-checkpoint",type=Path,
                    default=ROOT/"build/c07/epistemic-trained.rvp")
    ap.add_argument("--c07-report",type=Path,
                    default=ROOT/"build/c07/training-report.json")
    ap.add_argument("--out",type=Path,
                    default=ROOT/"build/c08/active-report.json")
    args=ap.parse_args()
    report=campaign(args.out,args.c07_checkpoint,args.c07_report)
    print(json.dumps({
        "passed":True,
        "promoted":report["promotion_mode"],
        "pool":report["pool_unlabeled_count"],
        "selected_and_verified":report["verified_teacher_receipts"],
        "validation":{m["mode"]:m["validation_selective"]
                      for m in report["comparisons"]},
        "heldout":{m["mode"]:m["heldout"]["selective"]
                   for m in report["comparisons"]},
        "no_C07_test_training":True,
        "checkpoint_sha256":report["active_model_sha256"],
        "apk_built":False,
    },ensure_ascii=False))


if __name__=="__main__":
    main()
