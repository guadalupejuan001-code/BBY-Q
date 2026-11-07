#!/usr/bin/env python3
"""C04 native differential: exact historical receipts and bank SHA equality.

No original U02 code path is replaced in production. Every C04 execution
uses its own disposable SQLite database and runs the pinned XI simulator.
"""
from __future__ import annotations
import hashlib
import json
from pathlib import Path
import tempfile

from integration.audit_u03_c00.profile import MISSION, freeze_assets, apk_files
from integration.persist_u03_c02.conformance import identical_trial, sanitize
from integration.unified.session import Session
from integration.cache_u03_c03.session import CachedSession, archive_cache_scope
from .runtime import PlannedSession


def plan_exercises(klass):
    with tempfile.TemporaryDirectory(prefix="bbyq-c04-verified-") as temporary:
        database = Path(temporary) / "sandbox.sqlite"
        receipts, plans = [], []
        with archive_cache_scope() as _:
            with klass(database) as session:
                def one(identifier, prompt, **kw):
                    output = session.turn(identifier, prompt, **kw)
                    stats = (dict(session.last_plan_stats) if isinstance(session, PlannedSession)
                             else None)
                    if not output["ok"] and identifier not in ("text", "cancel"):
                        raise AssertionError("C04 task unexpectedly failed: " + identifier)
                    receipts.append(sanitize(output))
                    plans.append(stats)
                    return output
                one("math", "calcula 7 + 3")
                one("text", "¿puedes decir qué es memoria?")
                one("status", "muestra el estado de la entidad")
                one("remember", "guarda la regla Faro Azul con valor 1")
                one("recall", "lee la regla Faro Azul")
                one("policy", "decide desde 3 hasta 6")
                one("mission", MISSION)
                frozen = session.snapshot()
                repeat = session.turn("mission", MISSION)
                if repeat != receipts[-1] or session.snapshot() != frozen:
                    # Original return may include elapsed_ms only for text;
                    # mission has no variable generation clock.
                    raise AssertionError("Replay changed native state")
                one("feedback", "aprende de la última tarea")
                one("recall-after", "lee la regla Faro Azul")
                one("rule", "si alguien es clase cero entonces es alerta")
                one("query", "dime si observación Nara es alerta")
                one("cancel", "no resuelvas Nara")
                try:
                    session.turn(
                        "crash",
                        "guarda la regla Otra con valor 0 observa Brisa con muestra 122121 y resuelve desde 3",
                        fail_after=2,
                    )
                except RuntimeError:
                    pass
                else:
                    raise AssertionError("Injected error did not abort")
                last = session.snapshot()
                state = {"snapshot": last, "history": session.history()}
        with Session(database) as reopened:
            if reopened.snapshot() != state["snapshot"] or reopened.history() != state["history"]:
                raise AssertionError("C04 banks/receipts cannot be restored by original U02")
        return {"receipts": receipts, **state}, plans


def _proof_of_selective_activation(plans):
    labels = ["math", "text", "status", "remember", "recall", "policy",
              "mission", "feedback", "recall-after", "rule", "query", "cancel"]
    results = dict(zip(labels, plans))
    for name in ("math", "text", "status", "rule", "cancel"):
        if results[name]["native_bank_processes_started"]:
            raise AssertionError("C04 activated unused quantum engines for " + name)
    if results["remember"]["native_bank_processes_started"] != ["memory"]:
        raise AssertionError("C04 memory command started unrelated native engines")
    if results["recall"]["native_bank_processes_started"] != ["memory"]:
        raise AssertionError("C04 memory read started unrelated native engines")
    if set(results["policy"]["native_bank_processes_started"]) != {"v3", "voice", "entity"}:
        raise AssertionError("C04 policy did not activate exactly its native dependencies")
    if set(results["mission"]["native_bank_processes_started"]) != {"memory", "v3", "voice", "entity"}:
        raise AssertionError("C04 compound mission failed to activate all necessary banks")
    if set(results["feedback"]["native_bank_processes_started"]) != {"memory", "v3", "voice", "entity"}:
        raise AssertionError("C04 verified feedback did not preserve all native updates")
    if results["query"]["native_bank_processes_started"] != ["v3"]:
        raise AssertionError("C04 failed to execute needed derived-VQC refresh")
    for name, stats in results.items():
        if stats["native_xi_executions_skipped"] != 0 or stats["native_stateful_parallel_executions"] != 0:
            raise AssertionError("C04 performed an uncertified native shortcut: " + name)
        if stats["hash_worker_count"] != 4 or stats["immutable_bank_hashes_verified"] != 7:
            raise AssertionError("C04 did not verify all frozen banks in independent hash workers")
    return {name: {
        "opened": v["native_bank_processes_started"],
        "avoided": v["native_bank_processes_avoided"],
        "hash_workers": v["hash_worker_count"],
        "plan_route": (v["dependency_plan"] or {}).get("route"),
    } for name,v in results.items()}


def run():
    assets, apks = freeze_assets(), apk_files()
    baseline = identical_trial(Session)
    c03 = identical_trial(CachedSession)
    c04 = identical_trial(PlannedSession)
    if baseline != c03 or baseline != c04:
        raise AssertionError("C04 cannot reproduce existing U02/C03 native checkpoints")
    untouched, _ = plan_exercises(Session)
    optimized, plans = plan_exercises(PlannedSession)
    if untouched != optimized:
        mismatch = [k for k in untouched if untouched[k] != optimized.get(k)]
        raise AssertionError("C04 native orchestration changed a result or bank: " + str(mismatch))
    selective = _proof_of_selective_activation(plans)
    if freeze_assets() != assets or apk_files() != apks:
        raise AssertionError("C04 touched a frozen model/source or built APK")
    return {
        "passed": True,
        "original_U02_and_C03_equal": True,
        "native_receipts_and_bank_hashes_equal": True,
        "native_rollback_and_restart_equal": True,
        "all_stateful_XI_calls_preserved": True,
        "selective_activation": selective,
        "protected_file_count": len(assets),
        "checkpoint_sources_unchanged": True,
        "apk_built": False,
        "reference_sha256": hashlib.sha256(
            json.dumps(untouched, sort_keys=True, ensure_ascii=False).encode()
        ).hexdigest(),
    }


if __name__ == "__main__":
    print(json.dumps(run(), ensure_ascii=False))
