#!/usr/bin/env python3
"""Native equivalence: original XI vs opt-in C01. Models are never retrained."""
from __future__ import annotations

from contextlib import nullcontext
import json
from pathlib import Path
import tempfile

from integration.audit_u03_c00.profile import freeze_assets, apk_files, MISSION
from integration.unified.session import Session
from .client import activate


def sanitize(data):
    if isinstance(data, dict):
        return {key: sanitize(value) for key, value in data.items() if key not in ("elapsed_ms",)}
    if isinstance(data, list):
        return [sanitize(value) for value in data]
    return data


def session_trial(optimized: bool):
    with (activate() if optimized else nullcontext()):
        with tempfile.TemporaryDirectory(prefix="bbyq-c01-identical-") as temporary:
            db = Path(temporary) / "anonymous.sqlite"
            with Session(db) as session:
                initial = session.snapshot()
                arithmetic = session.turn("t-math", "calcula 7 + 3")
                if not arithmetic["ok"]:
                    raise AssertionError("arithmetic route rejected")
                text = session.turn("t-text", "¿puedes decir qué es memoria?")
                mission = session.turn("t-mission", MISSION)
                if not mission["ok"] or not mission["results"][-1]["voice"]["faithful"]:
                    raise AssertionError("U02 mission regressed")
                snap_before_replay = session.snapshot()
                replay = session.turn("t-mission", MISSION)
                if replay != mission or session.snapshot() != snap_before_replay:
                    raise AssertionError("idempotent replay changed model state")
                before_injection = session.snapshot()
                try:
                    session.turn(
                        "t-crash",
                        "guarda la regla Otra con valor 0 observa Brisa con muestra 122121 y resuelve desde 3",
                        fail_after=2,
                    )
                except RuntimeError:
                    pass
                else:
                    raise AssertionError("injected failure was not observed")
                if session.snapshot() != before_injection:
                    raise AssertionError("injected failure modified a checkpoint")
                feedback = session.turn("t-feedback", "aprende de la última tarea")
                if not feedback["ok"]:
                    raise AssertionError("original verified feedback failed")
                recall = session.turn("t-recall", "lee la regla Faro Azul")
                if not recall["ok"]:
                    raise AssertionError("quantum memory recall failed")
                return sanitize({
                    "initial": initial,
                    "arithmetic": arithmetic,
                    "text": text,
                    "mission": mission,
                    "replay": replay,
                    "feedback": feedback,
                    "recall": recall,
                    "final_snapshot": session.snapshot(),
                    "history": session.history(),
                })


def run():
    before, apk_before = freeze_assets(), apk_files()
    reference = session_trial(optimized=False)
    updated = session_trial(optimized=True)
    if updated != reference:
        mismatches = [key for key in reference if reference[key] != updated.get(key)]
        raise AssertionError("C01 changed original result/state: " + str(mismatches))
    after = freeze_assets()
    if before != after or apk_files() != apk_before:
        raise AssertionError("C01 changed a frozen asset or created an APK")
    return {
        "passed": True,
        "runtime_output_and_checkpoint_equal": True,
        "scenarios": ["math", "text", "mission", "replay", "rollback", "feedback", "recall"],
        "checkpoints_unchanged": True,
        "protected_file_count": len(before),
        "apk_built": False,
        "semantic_result_sha256": __import__("hashlib").sha256(json.dumps(reference, sort_keys=True, ensure_ascii=False).encode()).hexdigest(),
    }


def main():
    result = run()
    print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()
