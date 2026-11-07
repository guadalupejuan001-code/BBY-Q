#!/usr/bin/env python3
"""C03: interleaved isolated A/B profiling of genuine XI EXEC avoidance."""
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
from .session import CachedSession

ROOT = c00.ROOT
MODES = ("original", "c03")
CASES = ("mission", "observe", "feedback", "replay", "separate-mission")


def one(mode, scenario):
    if mode not in MODES or scenario not in CASES:
        raise ValueError("Unknown C03 A/B scenario or mode")
    factory = CachedSession if mode == "c03" else Session
    tracer = c00.NativeTrace()
    tracer.attach(C1.XiSession)
    try:
        with tempfile.TemporaryDirectory(prefix="bbyq-c03-benchmark-") as temp:
            with factory(Path(temp) / "synthetic.sqlite") as session:
                if scenario in ("feedback", "replay"):
                    first = session.turn("prime", c00.MISSION)
                    if not first["ok"]:
                        raise AssertionError("C03 benchmark prime failed")
                if scenario == "separate-mission":
                    association = session.turn("remember", "guarda la regla Faro Azul con valor 1")
                    observation = session.turn("observe-prime", "observa Nara con muestra 88113")
                    if not association["ok"] or not observation["ok"]:
                        raise AssertionError("C03 separate-turn setup failed")
                tracer.reset()
                tracer.enabled = True
                started = time.perf_counter_ns()
                if scenario == "mission":
                    answer = session.turn("measurement", c00.MISSION)
                elif scenario == "observe":
                    answer = session.turn("measurement", "observa Nara con muestra 88113")
                elif scenario == "feedback":
                    answer = session.turn("measurement", "aprende de la última tarea")
                elif scenario == "separate-mission":
                    answer = session.turn("measurement", "resuelve Nara usando la regla Faro Azul desde 3")
                else:
                    answer = session.turn("prime", c00.MISSION)
                elapsed = (time.perf_counter_ns() - started) / 1e6
                tracer.enabled = False
                if not answer["ok"]:
                    raise AssertionError("Original XI result did not commit")
                native = c00.summarize_events(tracer.events)
                data = {
                    "scenario": scenario, "mode": mode,
                    "wall_ms": round(elapsed, 3),
                    "xi_exec_calls": int(native["native_api"].get("execute", {}).get("count", 0)),
                    "xi_logical_source_bytes": native["source_bytes_sent_to_xi"],
                    "xi_native_cpu_ms_observed": native["native_cpu_ms_observed"],
                    "cache": dict(session.last_cache_stats) if mode == "c03" else None,
                    "semantic_result": "ok",
                }
                if mode == "c03":
                    if scenario == "mission" and data["cache"]["vqc_hits"] != 1:
                        raise AssertionError("C03 did not eliminate one duplicate VQC execution")
                    if scenario != "mission" and data["cache"]["vqc_hits"] != 0:
                        raise AssertionError("C03 leaked VQC entries across tasks/updates")
                return data
    finally:
        tracer.enabled = False
        tracer.detach()


def run(samples, timeout, output):
    before, before_apks = c00.freeze_assets(), c00.apk_files()
    order = [(scenario, mode, index) for scenario in CASES
             for mode in MODES for index in range(samples)]
    random.Random(2026110606).shuffle(order)
    cases = {name: {mode: [] for mode in MODES} for name in CASES}
    for scenario, mode, index in order:
        proc = subprocess.run(
            [sys.executable, "-m", "integration.cache_u03_c03.benchmark",
             "--worker", scenario, "--mode", mode],
            cwd=ROOT, capture_output=True, text=True, timeout=timeout
        )
        if proc.returncode:
            raise RuntimeError(
                f"C03 {scenario}/{mode}/{index} failed: "
                + proc.stderr[-4000:] + proc.stdout[-500:]
            )
        sample = json.loads(proc.stdout.strip().splitlines()[-1])
        cases[scenario][mode].append(sample)
        print(json.dumps({
            "scenario": scenario, "mode": mode,
            "iteration": index, "wall_ms": sample["wall_ms"],
            "xi_exec_calls": sample["xi_exec_calls"],
            "native_source_bytes": sample["xi_logical_source_bytes"],
        }), flush=True)

    summaries = {}
    for scenario, versions in cases.items():
        baseline, optimized = versions["original"], versions["c03"]
        elapsed_base = c00.stats([x["wall_ms"] for x in baseline])
        elapsed_opt = c00.stats([x["wall_ms"] for x in optimized])
        exec_base = c00.stats([x["xi_exec_calls"] for x in baseline])
        exec_opt = c00.stats([x["xi_exec_calls"] for x in optimized])
        bytes_base = c00.stats([x["xi_logical_source_bytes"] for x in baseline])
        bytes_opt = c00.stats([x["xi_logical_source_bytes"] for x in optimized])
        summaries[scenario] = {
            "original_wall_ms": elapsed_base,
            "c03_wall_ms": elapsed_opt,
            "wall_ratio_original_over_c03": round(
                elapsed_base["median"] / elapsed_opt["median"], 4),
            "original_native_exec_calls": exec_base,
            "c03_native_exec_calls": exec_opt,
            "native_exec_avoided": round(exec_base["median"] - exec_opt["median"], 1),
            "original_native_source_bytes": bytes_base,
            "c03_native_source_bytes": bytes_opt,
            "native_source_reduction_percent": round(
                100 * (1 - bytes_opt["median"] / bytes_base["median"]), 2
            ) if bytes_base["median"] else None,
            "vqc_cache_hits": c00.stats(
                [x["cache"]["vqc_hits"] for x in optimized]),
        }
    if c00.freeze_assets() != before or c00.apk_files() != before_apks:
        raise AssertionError("C03 modified frozen checkpoint or generated APK")
    data = {
        "passed": True, "version": "BBYQ-U03-C03-native-memo-v1",
        "runner": c00.system_profile(), "samples_per_scenario": samples,
        "frozen_asset_count": len(before), "frozen_assets_unchanged": True,
        "apk_built": False, "summary": summaries, "raw": cases,
        "caveats": [
            "This caches only a duplicate native VQC readout or repeated QMemory read within one turn.",
            "Original XI programs, simulator, parameters and checkpoint binary representation are unchanged.",
            "C03 observations are never shared across turns, even if names or seeds match.",
            "A hit preserves original receipt trace shape while being counted separately as no new native EXEC.",
            "Timing includes Python orchestration and instrumentation; sampled Linux CI runner, not Android.",
            "With few samples, observed latency changes are exploratory and non-generalizable.",
            "Do not treat saved XI source bytes as reduction in persistent memory or physical quantum advantage.",
        ],
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n")
    return data


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--worker", choices=CASES)
    p.add_argument("--mode", choices=MODES, default="original")
    p.add_argument("--samples", type=int, default=2)
    p.add_argument("--timeout", type=int, default=180)
    p.add_argument("--out", type=Path, default=ROOT / "build/c03/benchmark.json")
    args = p.parse_args()
    if args.worker:
        print(json.dumps(one(args.mode, args.worker), ensure_ascii=False))
    else:
        if not 1 <= args.samples <= 12:
            p.error("samples must be 1..12")
        report = run(args.samples, args.timeout, args.out)
        print(json.dumps({
            "passed": report["passed"],
            "frozen_assets_unchanged": report["frozen_assets_unchanged"],
            "apk_built": False,
            "summary": {
                key: {name: value[name] for name in
                      ("wall_ratio_original_over_c03", "native_exec_avoided",
                       "native_source_reduction_percent", "vqc_cache_hits")}
                for key, value in report["summary"].items()
            },
        }, ensure_ascii=False))


if __name__ == "__main__":
    main()
