#!/usr/bin/env python3
"""Interleaved A/B benchmark of SQLite writer-hold time and end-to-end latency.

All measurements are from synthetic, throwaway workspaces. The optimized
variant trades snapshot-copy cost for shorter database writer lock duration.
No performance improvement is assumed in pass/fail criteria.
"""
from __future__ import annotations

import argparse
from contextlib import closing
import json
from pathlib import Path
import random
import sqlite3
import subprocess
import sys
import tempfile
import time

from integration.audit_u03_c00 import profile as c00
from integration.unified.session import Session
from .optimistic import OptimisticSession

SCENARIOS = ("arithmetic", "text", "mission", "feedback", "replay")
MODES = ("baseline", "optimistic")


def run_one(mode: str, scenario: str):
    if mode not in MODES or scenario not in SCENARIOS:
        raise ValueError("C02 unsupported benchmark mode or case")
    with tempfile.TemporaryDirectory(prefix="bbyq-c02-benchmark-") as directory:
        database = Path(directory) / "synthetic.sqlite"
        klass = Session if mode == "baseline" else OptimisticSession
        with klass(database) as session:
            if scenario in ("feedback", "replay"):
                initial = session.turn("prime", c00.MISSION)
                if not initial["ok"]:
                    raise AssertionError("C02 preconditioning mission failed")
            timestamps = []
            if mode == "baseline":
                def trace(statement):
                    command = statement.strip().upper()
                    if command == "BEGIN IMMEDIATE":
                        timestamps.append(("begin", time.perf_counter_ns()))
                    elif command == "COMMIT":
                        timestamps.append(("commit", time.perf_counter_ns()))
                session.db.set_trace_callback(trace)
            start = time.perf_counter_ns()
            if scenario == "arithmetic":
                output = session.turn("measure", "calcula 7 + 3")
            elif scenario == "text":
                output = session.turn("measure", "¿puedes decir qué es memoria?")
            elif scenario == "mission":
                output = session.turn("measure", c00.MISSION)
            elif scenario == "feedback":
                output = session.turn("measure", "aprende de la última tarea")
            else:
                output = session.turn("prime", c00.MISSION)
            wall_ms = (time.perf_counter_ns() - start) / 1e6
            if mode == "baseline":
                session.db.set_trace_callback(None)
                begin = next((v for key, v in timestamps if key == "begin"), None)
                commit = next((v for key, v in reversed(timestamps) if key == "commit"), None)
                if begin is None or commit is None or commit < begin:
                    raise AssertionError("Could not identify original write transaction")
                # Trace callback is BEFORE COMMIT executes: approximate lower bound.
                metrics = {"write_lock_ms_lower_bound": (commit - begin) / 1e6}
            else:
                metrics = dict(session.last_metrics)
                metrics["write_lock_ms_lower_bound"] = metrics["write_lock_ms"]
            if scenario != "text" and not output["ok"]:
                raise AssertionError("Frozen U02 scenario failed: " + scenario)
            return {
                "mode": mode, "scenario": scenario,
                "wall_ms": round(wall_ms, 3),
                "write_lock_ms_lower_bound": round(metrics["write_lock_ms_lower_bound"], 3),
                "commit_delta": metrics if mode != "baseline" else {},
                "outcome": bool(output.get("ok")),
            }


def run_comparison(samples: int, timeout: int, output: Path):
    frozen, apk_before = c00.freeze_assets(), c00.apk_files()
    schedule = [(mode, scenario, i) for mode in MODES
                for scenario in SCENARIOS for i in range(samples)]
    random.Random(2026110603).shuffle(schedule)
    measured = {s: {m: [] for m in MODES} for s in SCENARIOS}
    for mode, scenario, iteration in schedule:
        process = subprocess.run([
            sys.executable, "-m", "integration.persist_u03_c02.benchmark",
            "--worker", scenario, "--mode", mode],
            cwd=c00.ROOT, capture_output=True, text=True,
            timeout=timeout, check=False)
        if process.returncode:
            raise RuntimeError(f"C02 {mode}/{scenario}/{iteration}: " +
                               process.stderr[-4000:] + process.stdout[-700:])
        row = json.loads(process.stdout.strip().splitlines()[-1])
        measured[scenario][mode].append(row)
        print(json.dumps({
            "case": scenario, "mode": mode, "sample": iteration,
            "wall_ms": row["wall_ms"],
            "write_lock_ms_lower_bound": row["write_lock_ms_lower_bound"],
        }), flush=True)
    aggregates = {}
    for scenario in SCENARIOS:
        baseline = measured[scenario]["baseline"]
        candidate = measured[scenario]["optimistic"]
        b_wall = c00.stats([r["wall_ms"] for r in baseline])
        c_wall = c00.stats([r["wall_ms"] for r in candidate])
        b_lock = c00.stats([r["write_lock_ms_lower_bound"] for r in baseline])
        c_lock = c00.stats([r["write_lock_ms_lower_bound"] for r in candidate])
        aggregates[scenario] = {
            "baseline_wall_ms": b_wall, "optimistic_wall_ms": c_wall,
            "baseline_write_lock_ms": b_lock, "optimistic_write_lock_ms": c_lock,
            "wall_ratio_baseline_over_optimistic": round(
                b_wall["median"] / c_wall["median"], 4),
            "write_lock_ratio_baseline_over_optimistic": round(
                b_lock["median"] / c_lock["median"], 4) if c_lock["median"] else None,
        }
    if c00.freeze_assets() != frozen:
        raise AssertionError("C02 changed a protected source/checkpoint")
    if c00.apk_files() != apk_before:
        raise AssertionError("C02 generated an APK")
    report = {
        "schema": "U03-C02-persistence-comparison-v1",
        "passed": True, "apk_built": False,
        "protected_assets_unchanged": True, "protected_asset_count": len(frozen),
        "system": c00.system_profile(),
        "samples_per_scenario": samples, "comparisons": aggregates,
        "raw": measured,
        "caveats": [
            "Same native U02 model and XI runtime in both branches.",
            "C02 uses one SQLite backup and applies row changes to the live database.",
            "Original writer-lock duration is approximated using SQL trace callbacks before COMMIT.",
            "C02 lock duration includes BEGIN IMMEDIATE through completed COMMIT.",
            "No baseline model retraining and no personal database.",
            "Early-run startup, thermal and filesystem-cache effects may influence these small samples.",
            "Writer lock improvements are not equivalent to lower total CPU, RAM, storage traffic or end-to-end latency.",
            "Runner Linux measurements do not describe Android latency or battery use.",
        ],
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n")
    return report


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--worker", choices=SCENARIOS)
    parser.add_argument("--mode", choices=MODES, default="baseline")
    parser.add_argument("--samples", type=int, default=2)
    parser.add_argument("--timeout", type=int, default=150)
    parser.add_argument("--out", type=Path, default=c00.ROOT / "build/c02/comparison.json")
    args = parser.parse_args()
    if args.worker:
        print(json.dumps(run_one(args.mode, args.worker), ensure_ascii=False))
    else:
        if not 1 <= args.samples <= 12:
            parser.error("samples must be 1..12")
        value = run_comparison(args.samples, args.timeout, args.out)
        print(json.dumps({
            "passed": True,
            "protected_assets_unchanged": True, "apk_built": False,
            "comparison": {
                k: {"latency_ratio": v["wall_ratio_baseline_over_optimistic"],
                    "writer_lock_ratio": v["write_lock_ratio_baseline_over_optimistic"]}
                for k, v in value["comparisons"].items()},
            "output": str(args.out),
        }, ensure_ascii=False))


if __name__ == "__main__":
    main()
