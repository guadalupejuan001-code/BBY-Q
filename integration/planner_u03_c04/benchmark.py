#!/usr/bin/env python3
"""C04 measured A/B of selective native process launch and parallel SHA checks.

Same pinned U02 XI engine, same C03 frozen-release archive cache on BOTH
sides. No inference shortcuts: only unused bank subprocesses are not opened.
"""
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
from integration.cache_u03_c03.session import CachedSession, archive_cache_scope
from .runtime import PlannedSession

ROOT = c00.ROOT
MODES = ("c03-baseline", "c04-planner")
SCENARIOS = ("math", "text", "status", "recall", "policy", "mission", "feedback", "replay")


def worker(mode, case):
    if mode not in MODES or case not in SCENARIOS:
        raise ValueError("Unknown C04 benchmark scenario")
    klass = CachedSession if mode == "c03-baseline" else PlannedSession
    native_trace = c00.NativeTrace()
    native_trace.attach(C1.XiSession)
    try:
        with tempfile.TemporaryDirectory(prefix="bbyq-c04-test-") as temp:
            database = Path(temp) / "benchmark.sqlite"
            with archive_cache_scope():
                with klass(database) as session:
                    if case == "recall":
                        assert session.turn("prime", "guarda la regla Faro Azul con valor 1")["ok"]
                    elif case in ("feedback", "replay"):
                        assert session.turn("prime", c00.MISSION)["ok"]
                    native_trace.reset()
                    native_trace.enabled = True
                    t = time.perf_counter_ns()
                    if case == "math":
                        result = session.turn("measure", "calcula 7 + 3")
                    elif case == "text":
                        result = session.turn("measure", "¿puedes decir qué es memoria?")
                    elif case == "status":
                        result = session.turn("measure", "muestra el estado de la entidad")
                    elif case == "recall":
                        result = session.turn("measure", "lee la regla Faro Azul")
                    elif case == "policy":
                        result = session.turn("measure", "decide desde 3 hasta 6")
                    elif case == "mission":
                        result = session.turn("measure", c00.MISSION)
                    elif case == "feedback":
                        result = session.turn("measure", "aprende de la última tarea")
                    else:
                        result = session.turn("prime", c00.MISSION)
                    elapsed = (time.perf_counter_ns() - t) / 1e6
                    native_trace.enabled = False
                    if case != "text" and not result["ok"]:
                        raise AssertionError("Original native scenario failed: " + case)
                    trace = c00.summarize_events(native_trace.events)
                    opened = trace["native_api"].get("session_open", {}).get("count", 0)
                    xi = trace["native_api"].get("execute", {}).get("count", 0)
                    planned = session.last_plan_stats if mode == "c04-planner" else None
                    return {
                        "mode": mode, "scenario": case,
                        "wall_ms": round(elapsed, 3),
                        "xi_processes_opened": opened, "xi_exec": xi,
                        "xi_source_bytes": trace["source_bytes_sent_to_xi"],
                        "native_cpu_ms_observed": trace["native_cpu_ms_observed"],
                        "lazy_bank_processes_avoided": (
                            len(planned["native_bank_processes_avoided"]) if planned else 0
                        ),
                        "sha_workers": planned["hash_worker_count"] if planned else 1,
                        "result_ok": bool(result["ok"]),
                        "apk_built": False,
                    }
    finally:
        native_trace.enabled = False
        native_trace.detach()


def measure(samples, timeout, output):
    before, old_apks = c00.freeze_assets(), c00.apk_files()
    schedule = [(case, mode, iteration) for case in SCENARIOS
                for mode in MODES for iteration in range(samples)]
    random.Random(2026110704).shuffle(schedule)
    raw = {case: {mode: [] for mode in MODES} for case in SCENARIOS}
    for case, mode, i in schedule:
        proc = subprocess.run([
            sys.executable, "-m", "integration.planner_u03_c04.benchmark",
            "--worker", case, "--mode", mode,
        ], cwd=ROOT, text=True, capture_output=True, timeout=timeout)
        if proc.returncode:
            raise RuntimeError(f"C04 {case}/{mode}/{i}: " +
                               proc.stderr[-5000:] + proc.stdout[-1500:])
        record = json.loads(proc.stdout.strip().splitlines()[-1])
        raw[case][mode].append(record)
        print(json.dumps({
            "case": case, "mode": mode, "sample": i,
            "wall_ms": record["wall_ms"],
            "xi_processes_opened": record["xi_processes_opened"],
            "xi_exec": record["xi_exec"],
        }), flush=True)

    results = {}
    for case, groups in raw.items():
        old, new = groups[MODES[0]], groups[MODES[1]]
        wall_old = c00.stats([r["wall_ms"] for r in old])
        wall_new = c00.stats([r["wall_ms"] for r in new])
        starts_old = c00.stats([r["xi_processes_opened"] for r in old])
        starts_new = c00.stats([r["xi_processes_opened"] for r in new])
        exec_old = c00.stats([r["xi_exec"] for r in old])
        exec_new = c00.stats([r["xi_exec"] for r in new])
        if exec_old["median"] < exec_new["median"]:
            raise AssertionError("C04 unexpectedly increased XI EXEC count: " + case)
        results[case] = {
            "baseline_wall_ms": wall_old,
            "planned_wall_ms": wall_new,
            "wall_ratio_baseline_over_plan": round(wall_old["median"] / wall_new["median"], 4),
            "baseline_native_processes": starts_old,
            "planned_native_processes": starts_new,
            "processes_avoided": round(starts_old["median"] - starts_new["median"], 2),
            "baseline_native_xi_exec": exec_old,
            "planned_native_xi_exec": exec_new,
        }
    if c00.freeze_assets() != before or c00.apk_files() != old_apks:
        raise AssertionError("C04 changed frozen asset or created an APK")
    data = {
        "passed": True, "version": "BBYQ-U03-C04-selective-native-v1",
        "protected_files_unchanged": True, "protected_file_count": len(before),
        "samples_per_scenario": samples,
        "system": c00.system_profile(),
        "results": results, "raw": raw, "apk_built": False,
        "limitations": [
            "Native quantum program order and all XI calculations preserved.",
            "Only previously unconditional, unused V3/Memory/Voice/Entity subprocess launches are deferred.",
            "Independent frozen-bank SHA-256 digests are the only currently parallel computations.",
            "No stateful XI circuit executes in parallel; unsafe parallelism was deliberately withheld.",
            "Both comparison variants share the C03 verified archive cache for a fair C04 estimate.",
            "Neither variant is the Android build, and no battery/energy/performance claims transfer to phone.",
            "Two or three samples in a shared Linux runner are exploratory, not statistical proof.",
            "Startup of the SQLite session and priming tasks are excluded from each timed turn.",
        ],
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n")
    return data


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--worker", choices=SCENARIOS)
    p.add_argument("--mode", choices=MODES, default="c03-baseline")
    p.add_argument("--samples", type=int, default=2)
    p.add_argument("--timeout", type=int, default=180)
    p.add_argument("--out", type=Path, default=ROOT/"build/c04/benchmark.json")
    a = p.parse_args()
    if a.worker:
        print(json.dumps(worker(a.mode, a.worker), ensure_ascii=False))
        return
    if not 1 <= a.samples <= 12:
        p.error("samples must be 1..12")
    report = measure(a.samples, a.timeout, a.out)
    print(json.dumps({
        "passed": True, "protected_files_unchanged": True, "apk_built": False,
        "ratios": {k:v["wall_ratio_baseline_over_plan"] for k,v in report["results"].items()},
        "processes_avoided": {k:v["processes_avoided"] for k,v in report["results"].items()},
        "output": str(a.out),
    }, ensure_ascii=False))


if __name__ == "__main__":
    main()
