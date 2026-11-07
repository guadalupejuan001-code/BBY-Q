#!/usr/bin/env python3
"""C03 proof: model archive cache does not change ONE native operation or bank."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import tempfile

from integration.audit_u03_c00.profile import MISSION, apk_files, freeze_assets
from integration.persist_u03_c02.conformance import identical_trial
from integration.unified.session import Session
from .session import CachedSession, archive_cache_scope


def warm_reopen():
    with tempfile.TemporaryDirectory(prefix="bbyq-u03-c03-reopen-") as directory:
        database = Path(directory) / "knowledge.sqlite"
        with archive_cache_scope() as memo:
            with CachedSession(database) as first:
                original_mission = first.turn("mission", MISSION)
                if not original_mission["ok"]:
                    raise AssertionError("Cached original mission failed")
                before = first.snapshot()
                history = first.history()
            after_first = memo.snapshot()
            with CachedSession(database) as reopened:
                # U02 checks request ID before running native code; do not
                # pretend a cached model archive bypasses one XI mission.
                replay = reopened.turn("mission", MISSION)
                if replay != original_mission or reopened.snapshot() != before:
                    raise AssertionError("C03 changed an idempotent original receipt")
                if reopened.history() != history:
                    raise AssertionError("C03 changed original history")
                current = reopened.turn("recovery", "lee la regla Faro Azul")
                if not current["ok"] or current["results"][-1].get("value") != 1:
                    raise AssertionError("C03 lost the original quantum association")
                final = reopened.snapshot()
            after_reopen = memo.snapshot()
        with Session(database) as legacy:
            if legacy.snapshot() != final:
                raise AssertionError("Original U02 cannot read a C03 checkpoint")
            if legacy.history()[-1]["request_id"] != "recovery":
                raise AssertionError("Original U02 history differs")
        if after_reopen["hits"] <= after_first["hits"]:
            raise AssertionError("C03 did not reuse any authenticated frozen archives")
        if after_reopen["bypassed_native_executions"] != 0:
            raise AssertionError("C03 illegally skipped XI quantum work")
        return {
            "same_original_receipts": True,
            "same_original_recovery": True,
            "same_checkpoint_sha256": True,
            "first_open": after_first,
            "reopen": after_reopen,
        }


def run():
    protected, original_apks = freeze_assets(), apk_files()
    reference = identical_trial(Session)
    with archive_cache_scope() as memo:
        # First C03 session authenticates and caches compressed assets.
        candidate = identical_trial(CachedSession)
        first = memo.snapshot()
        # Second C03 session must reuse the original authenticated bytes.
        candidate_repeat = identical_trial(CachedSession)
        second = memo.snapshot()
    if reference != candidate or reference != candidate_repeat:
        mismatch = [key for key in reference if
                    reference[key] != candidate.get(key)
                    or reference[key] != candidate_repeat.get(key)]
        raise AssertionError("C03 U02 full receipt/checkpoint mismatch: " + str(mismatch))
    if second["hits"] <= first["hits"] or second["reused_checkpoint_bytes"] <= 0:
        raise AssertionError("Original release archive cache did not record real reuse")
    if second["bypassed_native_executions"] != 0:
        raise AssertionError("C03 skipped a native XI operation")
    restarted = warm_reopen()
    if freeze_assets() != protected or apk_files() != original_apks:
        raise AssertionError("C03 altered a frozen release file or generated an APK")
    return {
        "passed": True,
        "original_U02_checkpoint_and_full_receipt_equal": True,
        "original_U02_restart_passed": True,
        "real_content_verified_model_cache_hit": True,
        "native_XI_inference_bypassed": False,
        "models_before_after_unchanged": True,
        "first_load": first,
        "repeated_load": second,
        "warm_reopen": restarted,
        "protected_file_count": len(protected),
        "apk_built": False,
        "reference_sha256": hashlib.sha256(json.dumps(reference, sort_keys=True, ensure_ascii=False).encode()).hexdigest(),
        "rejected_experiment": {
            "name": "elide repeated VQC forward",
            "reason": "32,155 bytes of V3 checkpoint changed when a repeat XI circuit was skipped",
            "status": "REJECTED, not active in C03",
        },
    }


if __name__ == "__main__":
    print(json.dumps(run(), ensure_ascii=False))
