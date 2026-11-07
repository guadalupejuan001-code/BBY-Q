#!/usr/bin/env python3
"""C03 differential proof: original U02 vs exact turn-scoped VQC/QMemory memo."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import tempfile

from integration.audit_u03_c00.profile import MISSION, apk_files, freeze_assets
from integration.persist_u03_c02.conformance import identical_trial, sanitize
from integration.unified.session import Session
from .session import CachedSession


def exercise(klass):
    """Capture full receipts, native bank SHA, history and explicit cache stats."""
    with tempfile.TemporaryDirectory(prefix="bbyq-u03-c03-proof-") as directory:
        path = Path(directory) / "sandbox.sqlite"
        with klass(path) as q:
            initial = q.snapshot()
            first = q.turn("mission", MISSION)
            if not first["ok"] or not first["results"][-1]["voice"]["faithful"]:
                raise AssertionError("Original mission diverged")
            native_trace = first["trace"]
            if sum(row["operation"] == "vqc_forward" for row in native_trace) != 2:
                raise AssertionError("Expected double native VQC readout provenance in original receipt")
            cache_stats = dict(q.last_cache_stats) if hasattr(q, "last_cache_stats") else None
            prior = q.snapshot()
            replay = q.turn("mission", MISSION)
            if replay != first or q.snapshot() != prior:
                raise AssertionError("Idempotent replay changed persistent model state")
            same_id_rejected = False
            try:
                q.turn("mission", MISSION + " otra")
            except ValueError:
                same_id_rejected = True
            if not same_id_rejected or q.snapshot() != prior:
                raise AssertionError("C03 re-used a different prompt under a prior ID")

            memory = q.turn("remember-other", "corrige la regla Faro Azul a 0")
            recall = q.turn("recall", "lee la regla Faro Azul")
            # New sample should never carry a previous turn's VQC cache.
            observation = q.turn("new-sample", "observa Nara con muestra 88114")
            second_stats = dict(q.last_cache_stats) if hasattr(q, "last_cache_stats") else None
            another = q.turn("second-task", "resuelve Nara usando la regla Faro Azul desde 3")
            another_stats = dict(q.last_cache_stats) if hasattr(q, "last_cache_stats") else None
            if not all(v["ok"] for v in [memory, recall, observation, another]):
                raise AssertionError("Updated memory/sample was not applied")

            # A native supervised feedback follows the original *last* task;
            # never serve a stale VQC cache after parameters can change.
            feedback = q.turn("feedback", "aprende de la última tarea")
            feedback_stats = dict(q.last_cache_stats) if hasattr(q, "last_cache_stats") else None
            if not feedback["ok"]:
                raise AssertionError("Feedback failed after second task")

            snap = q.snapshot()
            try:
                q.turn("injected-error",
                       "guarda la regla Otra con valor 0 observa Brisa con muestra 122121 y resuelve desde 3",
                       fail_after=2)
            except RuntimeError:
                pass
            else:
                raise AssertionError("C03 did not propagate crash")
            if snap != q.snapshot():
                raise AssertionError("Rollback after cache miss changed a trained bank")

            status = {
                "first": first, "replay": replay, "remember": memory,
                "recall": recall, "observation": observation, "second_task": another,
                "feedback": feedback, "initial": initial,
                "snapshot": q.snapshot(), "history": q.history(),
            }
        with Session(path) as reader:
            if reader.snapshot() != status["snapshot"] or reader.history() != status["history"]:
                raise AssertionError("Original U02 cannot reload C03-computed checkpoint")
        return sanitize(status), {
            "first": cache_stats,
            "observation": second_stats,
            "separate_mission": another_stats,
            "feedback": feedback_stats,
        }


def control_case(control: str, cls):
    with tempfile.TemporaryDirectory(prefix="bbyq-u03-c03-control-") as tmp:
        with cls(Path(tmp) / "control.sqlite") as session:
            result = session.turn("test-" + control, MISSION, control=control)
            return sanitize(result), session.snapshot(), (
                dict(session.last_cache_stats) if hasattr(session, "last_cache_stats") else None
            )


def run():
    protected, original_apks = freeze_assets(), apk_files()
    standard = identical_trial(Session)
    memo = identical_trial(CachedSession)
    if standard != memo:
        mismatch = [name for name in standard if standard[name] != memo.get(name)]
        raise AssertionError("C03 cannot preserve U02 receipts/checkpoints: " + str(mismatch))
    ref, _ = exercise(Session)
    cand, stats = exercise(CachedSession)
    if ref != cand:
        mismatch = [name for name in ref if ref[name] != cand.get(name)]
        raise AssertionError("C03 double-VQC memo changed full native semantics: " + str(mismatch))
    if stats["first"]["vqc_hits"] != 1 or stats["first"]["vqc_misses"] != 1:
        raise AssertionError("C03 failed to avoid exactly one duplicate XI VQC execution")
    if stats["observation"]["vqc_hits"] != 0 or stats["separate_mission"]["vqc_hits"] != 0:
        raise AssertionError("VQC cache was erroneously retained between turns")
    if stats["feedback"]["vqc_hits"] != 0:
        raise AssertionError("C03 cached a training/update call")
    controls = {}
    for name in ("memory-erased", "vqc-ablated", "qrl-ablated"):
        old_receipt, old_state, _ = control_case(name, Session)
        new_receipt, new_state, metrics = control_case(name, CachedSession)
        if old_receipt != new_receipt or old_state != new_state:
            raise AssertionError("C03 changed an ablation: " + name)
        if name == "vqc-ablated" and metrics["vqc_hits"] != 0:
            raise AssertionError("Counterfactual perception unexpectedly cached")
        controls[name] = {"equal": True, "vqc_hits": metrics["vqc_hits"]}
    if freeze_assets() != protected or apk_files() != original_apks:
        raise AssertionError("C03 changed a source, model or created an APK")

    return {
        "passed": True,
        "full_receipt_and_checkpoint_equal": True,
        "original_U02_restart_passed": True,
        "idempotence_and_rejection_passed": True,
        "rollback_after_caching_passed": True,
        "feedback_and_new_observation_equal": True,
        "ablations": controls,
        "mission": stats["first"],
        "turn_scope": {
            "observation": stats["observation"],
            "separate_mission": stats["separate_mission"],
            "feedback": stats["feedback"],
        },
        "protected_file_count": len(protected),
        "protected_sources_unchanged": True,
        "apk_built": False,
        "semantic_sha256": hashlib.sha256(json.dumps(ref, sort_keys=True, ensure_ascii=False).encode()).hexdigest(),
    }


def main():
    print(json.dumps(run(), ensure_ascii=False))


if __name__ == "__main__":
    main()
