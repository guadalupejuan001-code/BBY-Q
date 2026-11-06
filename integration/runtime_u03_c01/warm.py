#!/usr/bin/env python3
"""C01 warm-session benchmark: distinguishes repeated process launch from RESTORE.

Run same task sequence against U02 and pooled XI; no persistent user DB.
"""
from __future__ import annotations

import argparse
from contextlib import nullcontext
import json
from pathlib import Path
import random
import subprocess
import sys
import tempfile
import time

from integration.audit_u03_c00 import profile as c00
from integration.unified.session import Session
from .client import CachedXiSession, activate

ROOT = c00.ROOT
READ_TEXT = "lee la regla Faro Azul"


def one(mode):
    if mode not in ("baseline", "pooled"):
        raise ValueError("Use baseline or pooled")
    ctx = activate(pool_sessions=True) if mode == "pooled" else nullcontext()
    with ctx, tempfile.TemporaryDirectory(prefix="bbyq-c01-warm-") as tmp:
        with Session(Path(tmp) / "sandbox.sqlite") as session:
            initial = session.turn("prime", c00.MISSION)
            if not initial["ok"]:
                raise AssertionError("Warm case failed to prepare shared task")
            CachedXiSession.reset_counters()
            start = time.perf_counter_ns()
            values = []
            for i in range(3):
                result = session.turn("read-" + str(i), READ_TEXT)
                if not result["ok"] or result["results"][-1].get("value") != 1:
                    raise AssertionError("Warm recall diverged")
                values.append(result["results"][-1]["value"])
            feedback = session.turn("teach", "aprende de la última tarea")
            if not feedback["ok"] or feedback["results"][-1]["kind"] != "feedback":
                raise AssertionError("Warm feedback diverged")
            result = session.turn("read-after-feedback", READ_TEXT)
            if not result["ok"] or result["results"][-1].get("value") != 1:
                raise AssertionError("Warm learned recall diverged")
            wall_ms = (time.perf_counter_ns() - start) / 1e6
            return {
                "mode": mode, "wall_ms": round(wall_ms, 3),
                "read_values": values + [result["results"][-1]["value"]],
                "feedback_succeeded": bool(feedback["results"][-1]["success"]),
                "bank_hashes": session.snapshot()["banks"],
                "native_transport": dict(CachedXiSession.stats) if mode == "pooled" else None,
            }


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--worker", choices=("baseline", "pooled"))
    p.add_argument("--samples", type=int, default=2)
    p.add_argument("--timeout", type=int, default=180)
    p.add_argument("--out", type=Path, default=ROOT / "build/c01/warm.json")
    args = p.parse_args()
    if args.worker:
        print(json.dumps(one(args.worker), ensure_ascii=False))
        return
    if not 1 <= args.samples <= 8:
        p.error("samples must be between 1 and 8")
    frozen, before_apks = c00.freeze_assets(), c00.apk_files()
    order = [(mode, i) for mode in ("baseline", "pooled")
             for i in range(args.samples)]
    random.Random(2026110602).shuffle(order)
    raw = {"baseline": [], "pooled": []}
    for mode, i in order:
        proc = subprocess.run(
            [sys.executable, "-m", "integration.runtime_u03_c01.warm",
             "--worker", mode],
            cwd=ROOT, capture_output=True, text=True, timeout=args.timeout,
        )
        if proc.returncode:
            raise RuntimeError(
                f"Warm {mode} iteration {i} failed: "
                + proc.stderr[-4000:] + proc.stdout[-1200:])
        value = json.loads(proc.stdout.strip().splitlines()[-1])
        raw[mode].append(value)
        print(json.dumps({"mode": mode, "sample": i,
                          "wall_ms": value["wall_ms"]}), flush=True)
    bank_sets = {tuple(sorted(row["bank_hashes"].items()))
                 for items in raw.values() for row in items}
    if len(bank_sets) != 1:
        raise AssertionError("Warm benchmark changed verified model checkpoints")
    if c00.freeze_assets() != frozen or c00.apk_files() != before_apks:
        raise AssertionError("Frozen asset or APK changed during warm benchmarks")
    base = c00.stats([v["wall_ms"] for v in raw["baseline"]])
    opt = c00.stats([v["wall_ms"] for v in raw["pooled"]])
    report = {
        "passed": True,
        "original_and_pooled_bank_hashes_equal": True,
        "models_unchanged": True, "apk_built": False,
        "samples_per_mode": args.samples,
        "baseline_wall_ms": base, "pooled_wall_ms": opt,
        "wall_ratio_baseline_over_pooled":
            round(base["median"] / opt["median"], 3),
        "workload": "after warmup mission: 3 verified recall turns, 1 feedback, 1 recall turn",
        "raw": raw,
        "system": c00.system_profile(),
        "caveats": [
            "Warmup excluded from elapsed time in both variants.",
            "The optimized mode retains processes and their RSS between turns.",
            "This test is host Linux and does not prove Android savings.",
            "Only two repetitions by default; no statistical confidence claims.",
        ],
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n")
    print(json.dumps({
        "passed": True, "warm_wall_ratio": report["wall_ratio_baseline_over_pooled"],
        "bank_hashes_equal": True, "apk_built": False,
    }))


if __name__ == "__main__":
    main()
