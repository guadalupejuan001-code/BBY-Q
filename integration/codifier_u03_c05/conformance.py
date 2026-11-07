#!/usr/bin/env python3
"""C05 exact differential against original U02/U03 C04, including feedback.

The new semantic frame never enters the trained C1 model, state authority or
SQLite commit. Its correctness is measured separately from the original
learned predictions and from any future C06 training campaign.
"""
from __future__ import annotations

from contextlib import nullcontext
import hashlib
import json
from pathlib import Path
import tempfile

from integration.audit_u03_c00.profile import ROOT, MISSION, apk_files, freeze_assets
from integration.unified.session import Session
from integration.planner_u03_c04.runtime import PlannedSession
from integration.cache_u03_c03.session import archive_cache_scope
from .semantic import analyze, raw_roundtrip, wire_decode
from .session import SemanticSession


def without_clocks(value):
    if isinstance(value, dict):
        return {k: without_clocks(v) for k, v in value.items() if k != "elapsed_ms"}
    if isinstance(value, list):
        return [without_clocks(v) for v in value]
    return value


TURN_SEQUENCE = [
    ("math", "calcula 7 + 3", None),
    ("text", "¿puedes decir qué es memoria?", None),
    ("memory", "guarda la regla Faro Azul con valor 1", None),
    ("recall", "lee la regla Faro Azul", None),
    ("mission", MISSION, None),
    ("explain", "explica la última tarea", None),
    ("feedback", "aprende de la última tarea", None),
    ("recall-after", "lee la regla Faro Azul", None),
    ("context", "repítelo", None),
    ("prohibited", "no resuelvas Nara", None),
    ("new-data", "observa Nara con muestra 88114", None),
    ("subsequent", "resuelve Nara usando la regla Faro Azul desde 3", None),
]


def trial(klass):
    with tempfile.TemporaryDirectory(prefix="bbyq-c05-native-differential-") as temporary:
        path = Path(temporary) / "synthetic.sqlite"
        context = archive_cache_scope() if klass is not Session else nullcontext()
        sidecars = []
        with context, klass(path) as entity:
            initial = entity.snapshot()
            receipts = []
            for name, prompt, payload in TURN_SEQUENCE:
                result = entity.turn(name, prompt, payload=payload)
                receipts.append(result)
                if isinstance(entity, SemanticSession):
                    doc = entity.last_semantic
                    if doc is None or wire_decode(entity.last_semantic_wire) != doc:
                        raise AssertionError("C05 did not expose authentic semantic transport")
                    if raw_roundtrip(doc)[0] != prompt.encode("utf-8"):
                        raise AssertionError("C05 semantic layer changed request")
                    sidecars.append({
                        "name": name,
                        "events": len(doc["events"]),
                        "negations": len(doc["negations"]),
                        "references": len(doc["references"]),
                    })
            before = entity.snapshot()
            duplicate = entity.turn("mission", MISSION)
            if duplicate != receipts[4] or entity.snapshot() != before:
                raise AssertionError("C05 repeated an idempotent native mission")
            try:
                entity.turn("mission", MISSION + " otra")
            except ValueError:
                pass
            else:
                raise AssertionError("C05 allowed collision of request IDs")
            prior = entity.snapshot()
            try:
                entity.turn("abort", "guarda la regla Otra con valor 0 observa Brisa con muestra 122121 y resuelve desde 3",
                            fail_after=2)
            except RuntimeError:
                pass
            else:
                raise AssertionError("C05 did not fail injected atomic turn")
            if entity.snapshot() != prior:
                raise AssertionError("C05 changed native checkpoint after rollback")
            if isinstance(entity, SemanticSession) and entity.last_semantic is not None:
                raise AssertionError("C05 published speculative sidecar after failure")
            output = {
                "initial": initial,
                "receipts": receipts, "duplicate": duplicate,
                "snapshot": entity.snapshot(),
                "history": entity.history(),
            }
        with Session(path) as old:
            if old.snapshot() != output["snapshot"] or old.history() != output["history"]:
                raise AssertionError("U02 could not reopen exact C05 knowledge and receipts")
        return without_clocks(output), sidecars


def main():
    frozen, before_apks = freeze_assets(), apk_files()
    baseline, _ = trial(Session)
    c04, _ = trial(PlannedSession)
    new, sidecars = trial(SemanticSession)
    if baseline != c04 or baseline != new:
        errors = [name for name in baseline if baseline[name] != new.get(name)]
        raise AssertionError("C05 incompatible with original U02 checkpoints: " + str(errors))
    if len(sidecars) != len(TURN_SEQUENCE):
        raise AssertionError("C05 lost semantic sidecar from a valid turn")
    negated = next(row for row in sidecars if row["name"] == "prohibited")
    if negated["negations"] != 1:
        raise AssertionError("C05 lost scoped negation")
    if freeze_assets() != frozen or apk_files() != before_apks:
        raise AssertionError("C05 modified a frozen checkpoint or generated an APK")
    result = {
        "passed": True,
        "original_U02_C04_C05_exact_bank_sha_and_receipts_equal": True,
        "original_U02_restart_passed": True,
        "native_feedback_memory_context_and_atomic_rollback_equal": True,
        "sidecar_frames_checked": len(sidecars),
        "negative_command_frame_preserved": True,
        "frozen_asset_count": len(frozen),
        "frozen_sources_unchanged": True,
        "native_model_training_performed": False,
        "apk_built": False,
        "semantic_result_sha256": hashlib.sha256(
            json.dumps(new, ensure_ascii=False, sort_keys=True).encode()
        ).hexdigest(),
        "sidecar_stats": sidecars,
    }
    outfile = ROOT / "build/c05/conformance.json"
    outfile.parent.mkdir(parents=True, exist_ok=True)
    outfile.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps({k: v for k, v in result.items() if k != "sidecar_stats"},
                     ensure_ascii=False))


if __name__ == "__main__":
    main()
