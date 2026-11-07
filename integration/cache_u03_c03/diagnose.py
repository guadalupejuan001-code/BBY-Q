#!/usr/bin/env python3
"""Explain C03 differences without changing any model or database in the repo."""
from pathlib import Path
import hashlib
import json
import tempfile

from integration.audit_u03_c00.profile import MISSION
from integration.unified.session import Session
from .session import CachedSession


def sample(cls):
    with tempfile.TemporaryDirectory(prefix="c03-diagnose-") as tmp:
        with cls(Path(tmp) / "scratch.sqlite") as s:
            response = s.turn("mission", MISSION)
            banks = s._banks()
            snapshot = s.snapshot()
            return {
                "ok": response["ok"],
                "snapshot": snapshot,
                "bank_images": banks,
                "cache": s.last_cache_stats if isinstance(s, CachedSession) else None,
                "response_trace": response["trace"],
            }


def run():
    original, candidate = sample(Session), sample(CachedSession)
    mismatches = {}
    for name in sorted(original["bank_images"]):
        before = original["bank_images"][name]
        after = candidate["bank_images"][name]
        if before != after:
            first = next((i for i, (a, b) in enumerate(zip(before, after)) if a != b),
                         min(len(before), len(after)))
            differences = sum(a != b for a, b in zip(before, after)) + abs(len(before) - len(after))
            mismatches[name] = {
                "before_sha256": hashlib.sha256(before).hexdigest(),
                "after_sha256": hashlib.sha256(after).hexdigest(),
                "before_bytes": len(before), "after_bytes": len(after),
                "first_different_offset": first, "bytes_different": differences,
            }
    return {
        "response_equal": original["ok"] == candidate["ok"]
        and original["response_trace"] == candidate["response_trace"],
        "snapshot_equal": original["snapshot"] == candidate["snapshot"],
        "different_banks": mismatches,
        "other_snapshot_fields": {
            key: [original["snapshot"][key], candidate["snapshot"][key]]
            for key in original["snapshot"] if key != "banks"
            and original["snapshot"][key] != candidate["snapshot"][key]
        },
        "cached_metrics": candidate["cache"],
        "apk_built": False,
    }


if __name__ == "__main__":
    print(json.dumps(run(), ensure_ascii=False))
