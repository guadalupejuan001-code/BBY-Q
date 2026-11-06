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
    if mode not in ("cached", "pooled"):
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
        with activate(pool_sessions=(mode == "pooled")):
            report = c00.run_worker(scenario)
        report["c01_transport"] = dict(CachedXiSession.stats)
        return report
    finally:
        c00.NativeTrace.reset = old_reset


def orchestrate(samples, timeout, output):
    frozen_before, apk_before = c00.freeze_assets(), c00.apk_files()
    pairs = [(scenario, mode, sample) for scenario in c00.SCENARIOS
             for sample in range(samples)
             for mode in ("baseline", "cached", "pooled")]
    random.Random(2026110601).shuffle(pairs)
    raw = {mode: {s: [] for s in c00.SCENARIOS}
           for mode in ("baseline", "cached", "pooled")}
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
        b_wall = c00.stats([v["wall_ms"] for v in base])
        b_wire = c00.stats([
            v["native_trace"]["source_bytes_sent_to_xi"] for v in base])
        entry = {
            "baseline_wall_ms": b_wall,
            "baseline_XI_exec_payload_bytes": b_wire,
        }
        for variant in ("cached", "pooled"):
            records = raw[variant][scenario]
            wall = c00.stats([v["wall_ms"] for v in records])
            wire = c00.stats([
                v["c01_transport"]["xi_wire_payload_bytes"] for v in records])
            entry.update({
                variant + "_wall_ms": wall,
                variant + "_wall_ratio_baseline_over_variant":
                    round(b_wall["median"] / wall["median"], 3)
                    if wall["median"] else None,
                variant + "_XI_exec_and_library_payload_bytes": wire,
                variant + "_protocol_payload_reduction_fraction":
                    round(1 - wire["median"] / b_wire["median"], 5)
                    if b_wire["median"] else None,
                variant + "_library_registrations": c00.stats([
                    v["c01_transport"]["libraries_registered"] for v in records]),
                variant + "_library_hits": c00.stats([
                    v["c01_transport"]["library_cache_hits"] for v in records]),
                variant + "_native_processes_started": c00.stats([
                    v["c01_transport"]["native_processes_started"] for v in records]),
                variant + "_restores": c00.stats([
                    v["c01_transport"]["restores"] for v in records]),
            })
        comparison[scenario] = entry
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
            "C01 caches immutable XI library text; pooled mode optionally restores RVPC2 into a bounded resident process.",
            "Original native Runtime::execute still parses and executes full source.",
            "No results or quantum states are cached; pooled processes are restored from fresh authenticated RVPC2 snapshots before reuse.",
            "The pooled mode retains worker RSS between turns (maximum six idle native processes per audit scope).",
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
    p.add_argument("--mode", choices=("baseline", "cached", "pooled"), default="baseline")
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
                k: {"cached_wall_ratio": v["cached_wall_ratio_baseline_over_variant"],
                    "pooled_wall_ratio": v["pooled_wall_ratio_baseline_over_variant"],
                    "cached_wire_reduction": v["cached_protocol_payload_reduction_fraction"],
                    "pooled_wire_reduction": v["pooled_protocol_payload_reduction_fraction"]}
                for k, v in report["comparisons"].items()},
            "output": str(args.out),
        }, ensure_ascii=False))


if __name__ == "__main__":
    main()
