#!/usr/bin/env python3
"""Paired A/B time-and-transport benchmark with frozen U02 code unchanged."""
from __future__ import annotations

import argparse
from contextlib import nullcontext
import json
import os
from pathlib import Path
import random
import subprocess
import sys

from integration.audit_u03_c00 import profile as c00
from .client import CachedXiSession, activate

ROOT = c00.ROOT


def worker(mode, scenario):
    if mode == "baseline":
        return c00.run_worker(scenario)
    if mode != "cached":
        raise ValueError("Unknown runtime experiment")
    # C00 resets its trace after synthetic setup. Reset transport metrics at
    # that exact boundary too, excluding feedback/replay priming.
    old_reset = c00.NativeTrace.reset

    def reset(self):
        CachedXiSession.reset_counters()
        return old_reset(self)

    c00.NativeTrace.reset = reset
    try:
        CachedXiSession.reset_counters()
        with activate():
            report = c00.run_worker(scenario)
        report["c01_transport"] = dict(CachedXiSession.stats)
        return report
    finally:
        c00.NativeTrace.reset = old_reset


def orchestrate(samples, timeout, output):
    frozen_before, apk_before = c00.freeze_assets(), c00.apk_files()
    pairs = [(scenario, mode, sample) for scenario in c00.SCENARIOS
             for sample in range(samples)
             for mode in ("baseline", "cached")]
    random.Random(2026110601).shuffle(pairs)
    raw = {"baseline": {s: [] for s in c00.SCENARIOS},
           "cached": {s: [] for s in c00.SCENARIOS}}
    for scenario, mode, sample in pairs:
        command = [
            sys.executable, "-m", "integration.runtime_u03_c01.benchmark",
            "--worker", scenario, "--mode", mode,
        ]
        proc = subprocess.run(command, cwd=ROOT, capture_output=True,
                              text=True, timeout=timeout, check=False)
        if proc.returncode:
            raise RuntimeError(
                f"C01 {mode}/{scenario} {sample} exited {proc.returncode}: "
                + proc.stderr[-4000:] + proc.stdout[-1000:])
        record = json.loads(proc.stdout.strip().splitlines()[-1])
        if not record["valid"]:
            raise AssertionError("Invalid C01 test: " + str((mode, scenario, record)))
        raw[mode][scenario].append(record)
        print(json.dumps({
            "C01": scenario, "mode": mode, "sample": sample,
            "wall_ms": record["wall_ms"],
            "logical_xi_bytes": record["native_trace"]["source_bytes_sent_to_xi"],
        }), flush=True)
    comparison = {}
    for scenario in c00.SCENARIOS:
        base = raw["baseline"][scenario]
        opt = raw["cached"][scenario]
        b_wall = c00.stats([v["wall_ms"] for v in base])
        c_wall = c00.stats([v["wall_ms"] for v in opt])
        b_wire = c00.stats([
            v["native_trace"]["source_bytes_sent_to_xi"] for v in base])
        c_wire = c00.stats([
            v["c01_transport"]["xi_wire_payload_bytes"] for v in opt])
        comparison[scenario] = {
            "baseline_wall_ms": b_wall,
            "cached_wall_ms": c_wall,
            "wall_ratio_baseline_over_cached":
                round(b_wall["median"] / c_wall["median"], 3)
                if c_wall["median"] else None,
            "baseline_XI_exec_payload_bytes": b_wire,
            "cached_XI_exec_and_library_payload_bytes": c_wire,
            "protocol_payload_reduction_fraction":
                round(1 - c_wire["median"] / b_wire["median"], 5)
                if b_wire["median"] else None,
            "optimized_library_registrations": c00.stats([
                v["c01_transport"]["libraries_registered"] for v in opt]),
            "optimized_library_hits": c00.stats([
                v["c01_transport"]["library_cache_hits"] for v in opt]),
        }
    if c00.freeze_assets() != frozen_before:
        raise AssertionError("C01 modified a frozen model, source or archive")
    if c00.apk_files() != apk_before:
        raise AssertionError("C01 built an APK")
    report = {
        "version": "U03-C01-transport-1",
        "passed": True,
        "checkpoint_and_source_unchanged": True,
        "frozen_asset_count": len(frozen_before),
        "apk_built": False,
        "samples_per_scenario": samples,
        "system": c00.system_profile(),
        "comparisons": comparison,
        "raw": raw,
        "caveats": [
            "C01 caches only immutable XI library text inside one runtime process.",
            "Original native Runtime::execute still parses and executes full source.",
            "No cache of quantum state, no persistent XI sessions across turns.",
            "Measurements are Linux host, not Android or physical quantum hardware.",
            "Two or three samples are exploratory; do not infer stable speedups.",
            "Compare baseline EXEC source bytes against cached EXECREF+CODELIB payload; framing overhead is omitted.",
            "Feedback scenario's preparation is excluded from timing in both modes.",
        ],
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n")
    return report


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--worker", choices=c00.SCENARIOS)
    p.add_argument("--mode", choices=("baseline", "cached"), default="baseline")
    p.add_argument("--samples", type=int, default=2)
    p.add_argument("--timeout", type=int, default=160)
    p.add_argument("--out", type=Path, default=ROOT / "build/c01/comparison.json")
    args = p.parse_args()
    if args.worker:
        print(json.dumps(worker(args.mode, args.worker), ensure_ascii=False))
    else:
        if not 1 <= args.samples <= 12:
            p.error("samples must be between 1 and 12")
        report = orchestrate(args.samples, args.timeout, args.out)
        print(json.dumps({
            "passed": True, "checkpoints_unchanged": True,
            "apk_built": False, "comparison": {
                k: {"wall_ratio": v["wall_ratio_baseline_over_cached"],
                    "wire_reduction": v["protocol_payload_reduction_fraction"]}
                for k, v in report["comparisons"].items()},
            "output": str(args.out),
        }, ensure_ascii=False))


if __name__ == "__main__":
    main()
