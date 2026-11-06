#!/usr/bin/env python3
"""C02 differential validation against U02 plus real concurrent-writer recovery."""
from __future__ import annotations

import concurrent.futures
import hashlib
import json
from pathlib import Path
import tempfile
from contextlib import closing

from integration.audit_u03_c00.profile import MISSION, apk_files, freeze_assets
from integration.unified.session import Session
from .optimistic import OptimisticSession, StaleSnapshot


def sanitize(value):
    if isinstance(value, dict):
        return {key: sanitize(item) for key, item in value.items() if key != "elapsed_ms"}
    if isinstance(value, list):
        return [sanitize(x) for x in value]
    return value


def identical_trial(klass):
    with tempfile.TemporaryDirectory(prefix="bbyq-c02-differential-") as directory:
        database = Path(directory) / "knowledge.sqlite"
        with klass(database) as session:
            start = session.snapshot()
            math = session.turn("math", "calcula 7 + 3")
            text = session.turn("text", "¿puedes decir qué es memoria?")
            mission = session.turn("mission", MISSION)
            if not math["ok"] or not mission["ok"]:
                raise AssertionError("C02 failed old U02 math or shared mission")
            before_replay = session.snapshot()
            replay = session.turn("mission", MISSION)
            if replay != mission or session.snapshot() != before_replay:
                raise AssertionError("C02 repeated an already committed request")
            try:
                session.turn("crash", "guarda la regla Otra con valor 0 observa Brisa con muestra 122121 y resuelve desde 3",
                             fail_after=2)
            except RuntimeError:
                pass
            else:
                raise AssertionError("Injected failure did not occur")
            if session.snapshot() != before_replay:
                raise AssertionError("C02 failed to undo injected failure")
            corrected = session.turn("correct", "corrige la regla Faro Azul a 0")
            explanation = session.turn("explain", "explica la última tarea")
            feedback = session.turn("feedback", "aprende de la última tarea")
            recall = session.turn("recall", "lee la regla Faro Azul")
            query = session.turn("query", "dime si observación Nara es alerta")
            if not (corrected["ok"] and explanation["ok"] and feedback["ok"] and
                    recall["ok"] and query["ok"]):
                raise AssertionError("C02 did not preserve original knowledge/feedback contracts")
            result = {
                "initial": start, "math": math, "text": text, "mission": mission,
                "replay": replay, "corrected": corrected, "explanation": explanation,
                "feedback": feedback, "recall": recall, "query": query,
                "snapshot": session.snapshot(), "history": session.history(),
            }
        # A completely new original U02 process must see the same durable state.
        with Session(database) as reader:
            if reader.snapshot() != result["snapshot"] or reader.history() != result["history"]:
                raise AssertionError("C02 data not compatible with original U02 restart")
        return sanitize(result)


def concurrent_retry():
    with tempfile.TemporaryDirectory(prefix="bbyq-c02-optimistic-race-") as directory:
        database = Path(directory) / "concurrent.sqlite"
        with OptimisticSession(database) as session:
            injected = []
            def concurrent_change(attempt):
                if attempt == 1:
                    with Session(database) as other:
                        other.turn("external", "calcula 3 + 4")
                    injected.append(attempt)
            session.before_publish = concurrent_change
            result = session.turn("ours", "calcula 7 + 3")
            if not result["ok"] or session.last_metrics["conflicts"] != 1:
                raise AssertionError("C02 did not detect and retry a real external commit")
            if session.last_metrics["attempts"] != 2:
                raise AssertionError("C02 used stale data instead of recomputing")
        with Session(database) as read:
            receipts = {x["request_id"] for x in read.history()}
            if receipts != {"ours", "external"}:
                raise AssertionError("Optimistic merge lost a concurrent receipt")
        return {"passed": True, "retried_after_external_commit": True,
                "attempts": 2, "both_receipts_preserved": True}


def same_id_race():
    with tempfile.TemporaryDirectory(prefix="bbyq-c02-same-id-") as directory:
        database = Path(directory) / "duplicate.sqlite"
        with Session(database):
            pass
        def one(_):
            with OptimisticSession(database) as session:
                return session.turn("simultaneous", "guarda la regla Bruma con valor 1")
        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as workers:
            results = list(workers.map(one, (0, 1)))
        if results[0] != results[1] or not results[0]["ok"]:
            raise AssertionError("Parallel identical request IDs were not idempotent")
        with Session(database) as verified:
            if len([x for x in verified.history() if x["request_id"] == "simultaneous"]) != 1:
                raise AssertionError("C02 committed duplicate receipts")
        return {"passed": True, "deduplicated_same_id": True}


def bounded_retry():
    with tempfile.TemporaryDirectory(prefix="bbyq-c02-retry-bound-") as directory:
        database = Path(directory) / "bounded.sqlite"
        with OptimisticSession(database, max_retries=1) as session:
            def always_change(attempt):
                with Session(database) as writer:
                    writer.turn("external-" + str(attempt), "calcula 3 + 4")
            session.before_publish = always_change
            try:
                session.turn("should-not-commit", "calcula 7 + 3")
            except StaleSnapshot:
                pass
            else:
                raise AssertionError("C02 ignored optimistic retry budget")
        with Session(database) as check:
            receipt_ids = [x["request_id"] for x in check.history()]
            if receipt_ids != ["external-1"]:
                raise AssertionError("C02 published stale or partial data on failed retry")
        return {"passed": True, "no_partial_commit": True}


def main():
    old_assets, old_apks = freeze_assets(), apk_files()
    baseline, candidate = identical_trial(Session), identical_trial(OptimisticSession)
    if baseline != candidate:
        mismatch = [name for name in baseline if baseline[name] != candidate.get(name)]
        raise AssertionError("U02 vs C02 semantic or checkpoint mismatch: " + str(mismatch))
    race, duplicate, exhausted = concurrent_retry(), same_id_race(), bounded_retry()
    if freeze_assets() != old_assets or apk_files() != old_apks:
        raise AssertionError("C02 damaged frozen assets or produced APK")
    report = {
        "passed": True,
        "modes": ["U02 original", "U03-C02 optimistic"],
        "semantic_and_checkpoint_equal": True,
        "restart_with_original_session_passed": True,
        "concurrent_retry": race,
        "same_request_id_parallel": duplicate,
        "bounded_conflict_retries": exhausted,
        "frozen_assets_sha256_unchanged": True,
        "frozen_asset_count": len(old_assets),
        "apk_built": False,
        "reference_sha256": hashlib.sha256(json.dumps(baseline, sort_keys=True, ensure_ascii=False).encode()).hexdigest(),
        "scope": "Isolated synthetic knowledge and tasks; no personal database and no installed Android build.",
    }
    print(json.dumps(report, ensure_ascii=False))


if __name__ == "__main__":
    main()
