#!/usr/bin/env python3
"""C03 A/B: checksum-authenticated frozen release cache vs original U02 init."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import random
import subprocess
import sys
import tempfile
import time

from integration.audit_u03_c00 import profile as c00
from integration.unified.common import C1
from integration.unified.session import Session
from .session import CachedSession, archive_cache_scope

ROOT = c00.ROOT
MODES = ("original", "c03")
CASES = ("reopen", "arithmetic", "mission", "feedback")


def worker(mode: str, scenario: str):
    if mode not in MODES or scenario not in CASES:
        raise ValueError("Unknown C03 benchmark variant")
    factory = Session if mode == "original" else CachedSession
    trace = c00.NativeTrace()
    trace.attach(C1.XiSession)
    try:
        with tempfile.TemporaryDirectory(prefix="bbyq-c03-immutable-benchmark-") as temp:
            database = Path(temp) / "test.sqlite"
            with archive_cache_scope() as memo:
                with factory(database) as first:
                    if scenario == "feedback":
                        prior = first.turn("prime", c00.MISSION)
                        if not prior["ok"]:
                            raise AssertionError("Feedback preparation failed")
                    else:
                        first.snapshot()
                # Cache is warm only on the optimized variant; no background
                # work and no user databases. Both variants open same schema.
                trace.reset()
                trace.enabled = True
                start = time.perf_counter_ns()
                with factory(database) as session:
                    if scenario == "reopen":
                        output = {"ok": True, "snapshot": session.snapshot()}
                    elif scenario == "arithmetic":
                        output = session.turn("measure", "calcula 7 + 3")
                    elif scenario == "mission":
                        output = session.turn("measure", c00.MISSION)
                    else:
                        output = session.turn("measure", "aprende de la última tarea")
                    if not output["ok"]:
                        raise AssertionError("Original native U02 benchmark case failed")
                elapsed = (time.perf_counter_ns() - start) / 1e6
                trace.enabled = False
                execs = c00.summarize_events(trace.events)["native_api"].get("execute", {}).get("count", 0)
                snapshot = memo.snapshot()
                if mode == "c03" and snapshot["hits"] < 1:
                    raise AssertionError("C03 did not reuse immutable authenticated checkpoint")
                return {
                    "mode": mode, "scenario": scenario, "wall_ms": round(elapsed, 3),
                    "native_XI_EXEC": int(execs),
                    "cache": snapshot, "apk_built": False,
                }
    finally:
        trace.enabled = False
        trace.detach()


def benchmark(samples: int, timeout: int, destination: Path):
    before, apk_before = c00.freeze_assets(), c00.apk_files()
    schedule = [(scenario, mode, i) for scenario in CASES
                for mode in MODES for i in range(samples)]
    random.Random(2026110609).shuffle(schedule)
    raw = {s: {m: [] for m in MODES} for s in CASES}
    for scenario, mode, sample in schedule:
        proc = subprocess.run(
            [sys.executable, "-m", "integration.cache_u03_c03.benchmark",
             "--worker", scenario, "--mode", mode],
            cwd=ROOT, capture_output=True, text=True, timeout=timeout
        )
        if proc.returncode:
            raise RuntimeError(f"C03 {mode}/{scenario} sample {sample}: "
                               + proc.stderr[-3000:] + proc.stdout[-500:])
        output = json.loads(proc.stdout.strip().splitlines()[-1])
        raw[scenario][mode].append(output)
        print(json.dumps({"scenario": scenario, "mode": mode, "sample": sample,
                          "wall_ms": output["wall_ms"], "native_XI_EXEC": output["native_XI_EXEC"],
                          "archive_hits": output["cache"]["hits"]}), flush=True)
    summary = {}
    for scenario, groups in raw.items():
        original = c00.stats([x["wall_ms"] for x in groups["original"]])
        cached = c00.stats([x["wall_ms"] for x in groups["c03"]])
        xi_original = c00.stats([x["native_XI_EXEC"] for x in groups["original"]])
        xi_cached = c00.stats([x["native_XI_EXEC"] for x in groups["c03"]])
        if xi_original["median"] != xi_cached["median"]:
            raise AssertionError("C03 changed real XI execution count")
        summary[scenario] = {
            "original_wall_ms": original,
            "cached_wall_ms": cached,
            "wall_ratio_original_over_cached": round(original["median"]/cached["median"], 4),
            "native_exec_original": xi_original,
            "native_exec_cached": xi_cached,
            "skipped_XI_execution": 0,
            "cache_model_hits": c00.stats([x["cache"]["hits"] for x in groups["c03"]]),
            "reused_checkpoint_bytes": c00.stats([
                x["cache"]["reused_checkpoint_bytes"] for x in groups["c03"]]),
        }
    if c00.freeze_assets() != before or c00.apk_files() != apk_before:
        raise AssertionError("C03 modified a protected checkpoint or produced APK")
    report = {
        "passed": True,
        "model_checksum_and_checkpoint_unchanged": True,
        "frozen_assets_count": len(before),
        "apk_built": False,
        "system": c00.system_profile(),
        "samples_per_scenario": samples,
        "summary": summary, "raw": raw,
        "interpretation": [
            "C03 only reuses authenticated immutable release archive bytes in a warm Python process.",
            "No native VQC or QMemory forward execution may be bypassed.",
            "All original XI executions, states and checkpoint serialization remain identical.",
            "Every model cache hit re-hashes actual manifest, source and checkpoint input bytes.",
            "The cache increases Python resident memory and retains frozen models until scope exit.",
            "A/B runs in isolated Linux GitHub runners; not a measured improvement on Android.",
            "Small samples and uncertain runner load do not prove speedups in general.",
            "A trial that skipped the repeated VQC changed 32,155 bytes of v3 checkpoint; it was rejected.",
        ],
    }
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(report, indent=2, ensure_ascii=False)+"\n")
    return report


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--worker", choices=CASES)
    p.add_argument("--mode", choices=MODES, default="original")
    p.add_argument("--samples", type=int, default=2)
    p.add_argument("--timeout", type=int, default=180)
    p.add_argument("--out", type=Path, default=ROOT/"build/c03/benchmark.json")
    a = p.parse_args()
    if a.worker:
        print(json.dumps(worker(a.mode, a.worker), ensure_ascii=False))
        return
    if not 1 <= a.samples <= 12:
        p.error("samples must be 1..12")
    results = benchmark(a.samples,a.timeout,a.out)
    print(json.dumps({
        "passed": True, "frozen_assets_unchanged": True,
        "apk_built": False,
        "ratio": {k:v["wall_ratio_original_over_cached"] for k,v in results["summary"].items()},
    }))


if __name__ == "__main__":
    main()
