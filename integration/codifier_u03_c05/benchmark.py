#!/usr/bin/env python3
"""C05 latency and semantic transport benchmark with identical native inference.

Do not mistake a deterministic host-side semantic annotation for a trained
language model accuracy improvement. Measure its marginal cost against C04.
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
from integration.planner_u03_c04.runtime import PlannedSession
from integration.cache_u03_c03.session import archive_cache_scope
from .semantic import analyze, raw_roundtrip, wire_decode, wire_encode
from .session import SemanticSession

ROOT = c00.ROOT
MODES = ("c04", "c05")
SCENARIOS = ("math", "negation", "memory", "mission", "text")


def semantic_microbenchmark(count: int = 240) -> dict:
    prompts = [
        f"define {i} no interferencia",
        f"no definas {i}",
        f"Guarda la regla Faro {i} con valor {i%2} observa Nara {i} con muestra {88113+i}",
        f"repítelo",
    ]
    rows = [text for i in range(count // 4) for text in
            (f"define Prisma{i} no Brisa{i}",
             f"no definas Prisma{i}",
             f"guarda la regla Faro{i} con valor {i%2} observa Nara{i} con muestra {88113+i}",
             "repítelo")]
    start = time.perf_counter_ns()
    wire_bytes = 0
    for text in rows:
        frame = analyze(text, "define memoria" if text == "repítelo" else "")
        packet = wire_encode(frame)
        if wire_decode(packet) != frame or raw_roundtrip(frame)[0] != text.encode("utf-8"):
            raise AssertionError("Microbenchmark C05 frame is not lossless")
        wire_bytes += len(packet)
    return {
        "calls": len(rows), "wall_ms": round((time.perf_counter_ns() - start) / 1e6, 3),
        "wire_bytes_total": wire_bytes,
        "type": "C05 host analysis + authenticated framing roundtrip; not native inference",
    }


def run_one(mode: str, scenario: str) -> dict:
    if mode not in MODES or scenario not in SCENARIOS:
        raise ValueError("Unknown C05 benchmark case")
    klass = PlannedSession if mode == "c04" else SemanticSession
    with tempfile.TemporaryDirectory(prefix="bbyq-u03-c05-benchmark-") as temp:
        with archive_cache_scope():
            with klass(Path(temp) / "ephemeral.sqlite") as entity:
                if scenario == "memory":
                    assert entity.turn("prepare", "guarda la regla Faro Azul con valor 1")["ok"]
                start = time.perf_counter_ns()
                if scenario == "math":
                    answer = entity.turn("measure", "calcula 7 + 3")
                elif scenario == "negation":
                    answer = entity.turn("measure", "no resuelvas Nara")
                elif scenario == "memory":
                    answer = entity.turn("measure", "lee la regla Faro Azul")
                elif scenario == "mission":
                    answer = entity.turn("measure", c00.MISSION)
                else:
                    answer = entity.turn("measure", "¿puedes decir qué es memoria?")
                elapsed_ms = (time.perf_counter_ns() - start) / 1e6
                if scenario not in ("text",) and not answer["ok"]:
                    raise AssertionError("Native U02 refused protected C05 scenario")
                semantic = entity.last_semantic if mode == "c05" else None
                if mode == "c05":
                    if raw_roundtrip(semantic)[0] != {
                        "math":"calcula 7 + 3",
                        "negation":"no resuelvas Nara",
                        "memory":"lee la regla Faro Azul",
                        "mission":c00.MISSION,
                        "text":"¿puedes decir qué es memoria?",
                    }[scenario].encode("utf-8"):
                        raise AssertionError("C05 failed to preserve source text")
                return {
                    "mode": mode, "scenario": scenario, "wall_ms": round(elapsed_ms, 3),
                    "result_ok": bool(answer["ok"]),
                    "cached_semantic_wire_bytes": len(entity.last_semantic_wire) if mode == "c05" else 0,
                    "applied_native_model_changes": False, "apk_built": False,
                }


def campaign(samples: int, timeout: int, target: Path) -> dict:
    before, apks = c00.freeze_assets(), c00.apk_files()
    schedule = [(scenario, mode, i)
                for scenario in SCENARIOS for mode in MODES for i in range(samples)]
    random.Random(2026110705).shuffle(schedule)
    observations = {s: {mode: [] for mode in MODES} for s in SCENARIOS}
    for scenario, mode, i in schedule:
        process = subprocess.run([
            sys.executable, "-m", "integration.codifier_u03_c05.benchmark",
            "--worker", scenario, "--mode", mode,
        ], cwd=ROOT, capture_output=True, text=True, timeout=timeout)
        if process.returncode:
            raise RuntimeError("C05 benchmark " + scenario + "/" + mode +
                               " failed: " + process.stderr[-4000:])
        row = json.loads(process.stdout.strip().splitlines()[-1])
        observations[scenario][mode].append(row)
        print(json.dumps({"scenario": scenario, "mode": mode,
                          "sample": i, "wall_ms": row["wall_ms"]}), flush=True)

    comparisons = {}
    for scenario, cases in observations.items():
        baseline = c00.stats([x["wall_ms"] for x in cases["c04"]])
        candidate = c00.stats([x["wall_ms"] for x in cases["c05"]])
        if any(x["result_ok"] != y["result_ok"] for x, y in
               zip(cases["c04"], cases["c05"])):
            raise AssertionError("C05 changed the native decision status")
        comparisons[scenario] = {
            "c04_wall_ms": baseline,
            "c05_wall_ms": candidate,
            "c04_over_c05_ratio": round(baseline["median"] / candidate["median"], 4),
            "semantic_wire_bytes": c00.stats(
                [x["cached_semantic_wire_bytes"] for x in cases["c05"]]),
        }
    if c00.freeze_assets() != before or c00.apk_files() != apks:
        raise AssertionError("C05 benchmark modified frozen state or generated APK")
    report = {
        "passed": True,
        "comparison": comparisons,
        "raw": observations,
        "microbenchmark": semantic_microbenchmark(),
        "frozen_assets_unchanged": True,
        "protected_asset_count": len(before),
        "apk_built": False,
        "samples_per_scenario": samples, "environment": c00.system_profile(),
        "caveats": [
            "C05 is an opt-in host semantic sidecar, not yet an XI learned semantic model.",
            "All actual U02/C04 native responses and checkpoint bytes stay unchanged.",
            "Small Linux runner samples are exploratory; not Android performance.",
            "Semantic frame is in RAM only and does not alter SQLite or add trained parameters.",
            "Semantic candidates are conservative, not a measure of free-form language comprehension.",
            "C06 will evaluate learning on external and unseen semantic patterns separately.",
        ],
    }
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n")
    return report


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--worker", choices=SCENARIOS)
    p.add_argument("--mode", choices=MODES, default="c04")
    p.add_argument("--samples", type=int, default=2)
    p.add_argument("--timeout", type=int, default=160)
    p.add_argument("--out", type=Path, default=ROOT / "build/c05/benchmark.json")
    args = p.parse_args()
    if args.worker:
        print(json.dumps(run_one(args.mode, args.worker), ensure_ascii=False))
    else:
        if not 1 <= args.samples <= 12:
            p.error("samples must be 1..12")
        result = campaign(args.samples, args.timeout, args.out)
        print(json.dumps({
            "passed": True,
            "frozen_assets_unchanged": True, "apk_built": False,
            "ratio": {name: row["c04_over_c05_ratio"]
                      for name, row in result["comparison"].items()},
            "microbenchmark": result["microbenchmark"],
            "out": str(args.out),
        }, ensure_ascii=False))


if __name__ == "__main__":
    main()
