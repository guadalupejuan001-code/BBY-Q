#!/usr/bin/env python3
"""C12 native XI cross-block capacity, interference and cost experiments.

The only engines are original U02 Session/REVERSE-PC XI/Ether. C11 is a
baseline/weight-audit library, not an alternative learner. Training,
inference, counterfactuals, and trajectory tests run on isolated SQLite
backups; teacher labels are evaluated ONLY after all inference receipts.
"""
from __future__ import annotations

import argparse
from hashlib import sha256
import json
from pathlib import Path
import tempfile
import time

from integration.audit_u03_c00.profile import ROOT, freeze_assets, apk_files, stats
from integration.joint_u03_c11.campaign import _clone, _episode, _read_weights, score_runs, _eligible
from integration.joint_u03_c11.native import HEADS, bank_weight_hashes, native_sample_teacher
from integration.joint_u03_c11.protocol import CONTROLS
from integration.memory_u03_c09.view import UnifiedMemoryView
from integration.unified.session import Session
from .protocol import (
    SCHEMA, MODES, OPERATIONS, TRAIN, VALIDATION, TEST, LOAD, REVISIT,
    heldout_test, separate,
)


def _initialize(database: Path) -> dict:
    """New U02-only empty original checkpoint, never user or C11 training data."""
    with Session(database) as model:
        view = UnifiedMemoryView(model).snapshot()
        if len(view["bank_sha256"]) != 7 or not view["C1_synchronized_with_U02"]:
            raise AssertionError("C12 original common checkpoint invalid")
        if view["new_memory_authorities"] != 0:
            raise AssertionError("C12 introduced a second memory authority")
        return {"snapshot": model.snapshot(), "original_v3": model.initial["v3"]}


def _training_arm(database: Path, *, train: bool) -> dict:
    before, _ = _read_weights(database)
    log = []
    started = time.perf_counter_ns()
    with Session(database) as model:
        for index, case in enumerate(TRAIN):
            receipt = model.turn(f"c12-training-task-{index}", case.prompt())
            mission = next((r for r in reversed(receipt.get("results", []))
                            if r.get("kind") == "mission"), {})
            valid = bool(receipt.get("ok") and mission.get("status") == 1)
            row = {
                "sample_sha256": sha256(case.prompt().encode()).hexdigest(),
                "task_ok": valid,
                "native_class": mission.get("class"),
                "native_rule": mission.get("rule_value"),
                "independent_feedback": False,
            }
            if train and valid:
                feedback = model.turn(f"c12-training-feedback-{index}",
                                      "aprende de la última tarea")
                f = next((r for r in reversed(feedback.get("results", []))
                          if r.get("kind") == "feedback"), {})
                row["independent_feedback"] = bool(
                    feedback.get("ok") and f.get("supervision") == "independent-labels"
                )
                row["native_updates"] = f.get("updates", {})
                if not row["independent_feedback"]:
                    raise AssertionError("C12 native supervised feedback was not verified")
            log.append(row)
        final = model.snapshot()
        view = UnifiedMemoryView(model).snapshot()
        if not view["C1_synchronized_with_U02"] or view["new_memory_authorities"] != 0:
            raise AssertionError("C12 training desynchronized original U02/C1")
    after, audited = _read_weights(database)
    if audited != final:
        raise AssertionError("C12 native parameter audit mutated checkpoint")
    changes = {name: before[name] != after[name] for name in HEADS}
    if not train and any(changes.values()):
        raise AssertionError("C12 frozen control updated XI native parameters")
    return {
        "train_requested": train,
        "training_rows": log,
        "native_feedback_count": sum(r["independent_feedback"] for r in log),
        "native_parameter_sha_before": before,
        "native_parameter_sha_after": after,
        "native_parameter_changed": changes,
        "xi_parameter_regions_changed": sum(changes.values()),
        "checkpoint": final,
        "training_wall_ms": round((time.perf_counter_ns() - started) / 1e6, 3),
    }


def _timed_episode(source: Path, case, control=None) -> dict:
    start = time.perf_counter_ns()
    # C11's primitive executes ORIGINAL XI/U02 and clones the DB for every
    # inference. No teacher, feedback or hidden label enters the call.
    row = _episode(source, case, control=control)
    row["host_wall_ms_including_clone"] = round(
        (time.perf_counter_ns() - start) / 1e6, 3
    )
    row["cross_block_ops_seen"] = {
        name: operation in row["native_trace_ops"]
        for name, operation in OPERATIONS.items()
    }
    return row


def _evaluate(arms: dict[str, Path], cases, *, initial_v3: bytes, controls=(None,)):
    """Collect EVERY prediction from EVERY arm before any XI teacher call."""
    observations = {}
    for mode, path in arms.items():
        observations[mode] = [
            _timed_episode(path, case, control)
            for case in cases for control in controls
        ]
    teachers = {case.seed: native_sample_teacher(initial_v3, case.seed)
                for case in cases}
    scored = {}
    for mode, rows in observations.items():
        score = score_runs(rows, teachers, cases)
        score["cost_wall_ms_including_clone"] = stats([
            row["host_wall_ms_including_clone"] for row in rows
        ])
        score["all_native_blocks_traced"] = sum(
            all(row["cross_block_ops_seen"].values()) for row in rows
        )
        score["all_failures_retained"] = len(score["raw"]) == len(rows)
        scored[mode] = score
    return scored


def _trajectory(source: Path, cases, *, label: str) -> dict:
    """Different tasks executed IN ONE ORIGINAL XI session to expose interference.

    The Session commits original memory changes to a throwaway clone.
    Nothing is trained; we audit actual native parameter regions before and
    after the full trajectory and all seven authenticated original banks.
    """
    with tempfile.TemporaryDirectory(prefix="bbyq-c12-trajectory-") as tmp:
        db = Path(tmp) / "trajectory.sqlite"
        _clone(source, db)
        t0 = time.perf_counter_ns()
        rows = []
        with Session(db) as model:
            before = model.snapshot()
            native_before = bank_weight_hashes(model._banks())
            for index, case in enumerate(cases):
                start = time.perf_counter_ns()
                receipt = model.turn(f"c12-{label}-{index}", case.prompt())
                mission = next((r for r in reversed(receipt.get("results", []))
                                if r.get("kind") == "mission"), {})
                operations = sorted({
                    e.get("operation") for e in receipt.get("trace", [])
                    if isinstance(e.get("operation"), str)
                })
                view = UnifiedMemoryView(model).snapshot()
                rows.append({
                    "sample_sha256": sha256(case.prompt().encode()).hexdigest(),
                    "seed": case.seed,
                    "receipt_ok": bool(receipt.get("ok")),
                    "class": mission.get("class"),
                    "rule": mission.get("rule_value"),
                    "action": mission.get("action"),
                    "goal": mission.get("goal"),
                    "supported": mission.get("supported") is True,
                    "voice_faithful": mission.get("voice", {}).get("faithful") is True,
                    "voice_terminated": mission.get("voice", {}).get("terminated") is True,
                    "native_ops": operations,
                    "six_blocks_traced": all(
                        op in operations for op in OPERATIONS.values()
                    ),
                    "c1_u02_synced": view["C1_synchronized_with_U02"],
                    "seven_authenticated_banks": len(view["bank_sha256"]) == 7,
                    "new_memory_authorities": view["new_memory_authorities"],
                    "host_wall_ms": round((time.perf_counter_ns() - start) / 1e6, 3),
                })
            after = model.snapshot()
            native_after = bank_weight_hashes(model._banks())
            final_view = UnifiedMemoryView(model).snapshot()
        if any(r["new_memory_authorities"] for r in rows):
            raise AssertionError("C12 trajectory created a new memory authority")
        identity_changed = {
            key: native_before[key] != native_after[key] for key in HEADS
        }
        revisited = None
        if label == "revisit":
            def state(row):
                return {k: row[k] for k in (
                    "class", "rule", "action", "goal", "supported",
                    "voice_faithful", "voice_terminated"
                )}
            revisited = {
                "first": state(rows[0]),
                "after_intervening_task": state(rows[-1]),
                "changed": state(rows[0]) != state(rows[-1]),
            }
        return {
            "path": label,
            "total": len(rows),
            "successful_receipts": sum(r["receipt_ok"] for r in rows),
            "full_six_block_traces": sum(r["six_blocks_traced"] for r in rows),
            "synchronized": sum(r["c1_u02_synced"] for r in rows),
            "bank_audits_ok": sum(r["seven_authenticated_banks"] for r in rows),
            "parameter_changed_during_inference_only": identity_changed,
            "params_unchanged_during_inference": not any(identity_changed.values()),
            "before_revision": before["revision"],
            "after_revision": after["revision"],
            "final_memory_fact_count": len(final_view["facts"]),
            "revisited": revisited,
            "host_wall_ms_including_audits": round((time.perf_counter_ns()-t0)/1e6,3),
            "steps": rows,
        }


def _score_trajectory(summaries, fixtures, native_v3):
    """Unseal synthetic labels only AFTER both experiment arms finish."""
    expected = {r.seed: native_sample_teacher(native_v3, r.seed)
                for r in dict((r.seed, r) for r in fixtures).values()}
    for mode, summary in summaries.items():
        rows = summary["steps"]
        summary["native_class_correct_vs_separate_XI"] = sum(
            r["class"] == expected[r["seed"]] for r in rows
        )
        summary["user_rule_recalled_correctly"] = sum(
            r["rule"] == next(x.bit for x in fixtures if x.seed == r["seed"])
            for r in rows
        )
        summary["cost_per_step_ms"] = stats([r["host_wall_ms"] for r in rows])


def campaign(output: Path) -> dict:
    original_protected = freeze_assets()
    original_apks = apk_files()
    if len(original_protected) != 159:
        raise AssertionError("C12 original protected manifest is not 159 files")
    splits = separate()
    output = Path(output)
    output.parent.mkdir(parents=True, exist_ok=True)
    started = time.perf_counter_ns()

    with tempfile.TemporaryDirectory(prefix="bbyq-c12-original-xi-") as tmp:
        work = Path(tmp)
        common = work / "original-u02.sqlite"
        origin = _initialize(common)
        origin_sha = sha256(common.read_bytes()).hexdigest()
        arms = {}
        for mode in MODES:
            dest = work / (mode + ".sqlite")
            _clone(common, dest)
            arms[mode] = dest

        trained = {
            mode: _training_arm(arms[mode], train=(mode == "joint-verified"))
            for mode in MODES
        }
        if not trained["joint-verified"]["native_feedback_count"]:
            raise AssertionError("C12 no real original XI supervised update executed")

        # Validate on 4 new cases; freeze selection BEFORE opening TEST.
        validation = _evaluate(arms, VALIDATION, initial_v3=origin["original_v3"])
        eligible = _eligible(
            validation["frozen"], validation["joint-verified"],
            trained["joint-verified"]["native_parameter_changed"]
        )
        selection = "joint-verified" if eligible else "frozen"
        candidate_before_test = {
            "selected_using_validation_only": selection,
            "joint_strict_gain": eligible,
            "trained_native_weights_changed":
                trained["joint-verified"]["native_parameter_changed"],
        }

        test_cases = heldout_test()
        test = _evaluate(arms, test_cases, initial_v3=origin["original_v3"])
        ablations = _evaluate(
            {"joint-verified": arms["joint-verified"]},
            test_cases[:2], initial_v3=origin["original_v3"],
            controls=CONTROLS,
        )
        capacity = {mode: _trajectory(arms[mode], LOAD, label="load")
                    for mode in MODES}
        interference = {mode: _trajectory(arms[mode], REVISIT, label="revisit")
                        for mode in MODES}
        _score_trajectory(capacity, LOAD, origin["original_v3"])
        _score_trajectory(interference, REVISIT, origin["original_v3"])

        if sha256(common.read_bytes()).hexdigest() != origin_sha:
            raise AssertionError("C12 mutated the original U02 control checkpoint")
        if freeze_assets() != original_protected or apk_files() != original_apks:
            raise AssertionError("C12 changed protected checkpoint/source or created APK")
        candidate = output.parent / "c12-synthetic-joint-candidate.sqlite"
        _clone(arms["joint-verified"], candidate)
        candidate_sha = sha256(candidate.read_bytes()).hexdigest()

        report = {
            "schema": SCHEMA,
            "passed": True,
            "architecture": "BBY Q -> w4U -> QdU",
            "original_reference": "original U02 XI/Ether, exact C11 PR #97 head",
            "external_world_validation": False,
            "real_quantum_hardware_used": False,
            "new_model_created": False,
            "new_primary_memory_authorities": 0,
            "protected_files": len(original_protected),
            "frozen_assets_unchanged": True,
            "prior_checkpoint_sha256": origin_sha,
            "previous_checkpoints_preserved": True,
            "new_apks": [],
            "apk_built": False,
            "splits": splits,
            "training": trained,
            "validation": validation,
            "decision_pre_test": candidate_before_test,
            "heldout_test": test,
            "ablations": ablations,
            "capacity": capacity,
            "interference": interference,
            "candidate_file": candidate.name,
            "candidate_sha256": candidate_sha,
            "candidate_promoted_to_production": False,
            "host_elapsed_ms": round((time.perf_counter_ns() - started)/1e6,3),
            "conclusions_limitations": [
                "Original XI software simulator; not physical qubit entanglement, teleportation or hardware advantage.",
                "Capacity is the observed finite tested matrix, never a maximum theoretical capacity.",
                "The given XI teacher is synthetic, supplied only after all native inference and is not an external ground truth.",
                "The supplied rule bit in each mission is explicit user supervision, not a hidden VQC class label.",
                "Ablations of 2 cases are descriptive and not statistically causal estimates.",
                "Measured wall-clock includes disposable SQLite clone/setup and differs from Android latency.",
                "Training is not promoted; holdout metrics have not authorized deployment.",
            ],
        }
        output.write_text(json.dumps(report,ensure_ascii=False,indent=2) + "\n")
        return report


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out",type=Path,default=ROOT/"build/c12/campaign.json")
    args = parser.parse_args()
    report = campaign(args.out)
    print(json.dumps({
        "passed": report["passed"],
        "training_feedback": report["training"]["joint-verified"]["native_feedback_count"],
        "changed_weights": report["training"]["joint-verified"]["native_parameter_changed"],
        "validation": {k: v["class_correct"] for k,v in report["validation"].items()},
        "heldout": {k: v["class_correct"] for k,v in report["heldout_test"].items()},
        "selected_in_lab": report["decision_pre_test"]["selected_using_validation_only"],
        "capacity": {k: v["successful_receipts"] for k,v in report["capacity"].items()},
        "revisit": {k: v["revisited"]["changed"] for k,v in report["interference"].items()},
        "protected": report["protected_files"], "apk_built": False,
    },ensure_ascii=False))


if __name__=="__main__":
    main()
