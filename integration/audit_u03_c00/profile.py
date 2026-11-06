#!/usr/bin/env python3
"""C00: reproducible, non-training host measurements of BBY Q U02.

Never uses a user's database. A subprocess and fresh SQLite database are used
for every synthetic case. No core/agent/checkpoint code is changed.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import platform
import re
import resource
import statistics
import subprocess
import sys
import tempfile
import time
from contextlib import ExitStack
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
SCENARIOS = ("initialization", "arithmetic", "text", "mission", "feedback", "replay")
MISSION = "guarda la regla Faro Azul con valor 1 observa Nara con muestra 88113 y resuelve desde 3"
PINNED_PARENT = "ae3afcf52500954ce8849d9bf7c8f0286f5b172b"
FROZEN_PATHS = (
    "integration/sequence1/experiment",
    "integration/sequence2/release",
    "integration/entity/release",
    "integration/unified/release",
    "ai/xi/qmemory",
    "ai/xi/quantum3",
)


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as file:
        for chunk in iter(lambda: file.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def freeze_assets(root: Path = ROOT) -> dict[str, str]:
    """Hashes *every* source/asset under the audited, immutable paths."""
    found: dict[str, str] = {}
    for relative in FROZEN_PATHS:
        directory = root / relative
        if not directory.is_dir():
            raise FileNotFoundError("Missing audit root: " + relative)
        for path in sorted(directory.rglob("*")):
            if path.is_file() and "__pycache__" not in path.parts and path.suffix != ".pyc":
                found[path.relative_to(root).as_posix()] = sha256(path)
    return found


def apk_files(root: Path = ROOT) -> set[str]:
    """Track output APKs only; do not treat existing repository assets as builds."""
    result = set()
    for relative in ("build", "android-personal/app/build"):
        directory = root / relative
        if directory.is_dir():
            result.update(path.relative_to(root).as_posix() for path in directory.rglob("*.apk"))
    return result


def io_counters(pid: int) -> dict[str, int]:
    try:
        data = {}
        for line in Path(f"/proc/{pid}/io").read_text().splitlines():
            key, value = line.split(":", 1)
            data[key] = int(value.strip())
        return {key: data.get(key, 0) for key in ("read_bytes", "write_bytes")}
    except (FileNotFoundError, PermissionError, ValueError, OSError):
        return {}


def cpu_ms(pid: int) -> float | None:
    try:
        # The command field can contain spaces/parentheses. Parse *after* the final ')'.
        fields = Path(f"/proc/{pid}/stat").read_text().rsplit(")", 1)[1].split()
        ticks = int(fields[11]) + int(fields[12])  # utime, stime
        return ticks * 1000 / os.sysconf("SC_CLK_TCK")
    except (FileNotFoundError, PermissionError, IndexError, ValueError, OSError):
        return None


def vmhwm_kib(pid: int) -> int | None:
    try:
        for line in Path(f"/proc/{pid}/status").read_text().splitlines():
            if line.startswith("VmHWM:"):
                return int(line.split()[1])
    except (FileNotFoundError, PermissionError, ValueError, OSError):
        pass
    return None


def usage_cpu_ms() -> float:
    used = resource.getrusage(resource.RUSAGE_SELF)
    return (used.ru_utime + used.ru_stime) * 1000


def difference(after: dict[str, int], before: dict[str, int]) -> dict[str, int]:
    return {key: max(0, after[key] - before[key]) for key in after.keys() & before.keys()}


def invoked_calls(source: str) -> list[str]:
    # Source contains the complete XI library *after* HALT. Ignore library
    # definitions: scanning all text yields false "executed" operations.
    prelude = source.split("\nhalt\n", 1)[0]
    return re.findall(r"(?m)^\s*call\s+([a-zA-Z0-9_]+)\s*$", prelude)


def stats(values: list[float]) -> dict[str, float]:
    if not values:
        return {}
    sorted_values = sorted(values)
    rank = max(0, int(__import__("math").ceil(.95 * len(values))) - 1)
    return {
        "min": round(sorted_values[0], 3),
        "median": round(statistics.median(values), 3),
        "p95_nearest_rank": round(sorted_values[rank], 3),
        "max": round(sorted_values[-1], 3),
    }


class NativeTrace:
    """Temporary instrumentation only inside one isolated audit process."""

    def __init__(self):
        self.enabled = False
        self.events: list[dict[str, Any]] = []
        self.native_peak_kib = 0
        self._old: dict[str, Any] = {}

    def attach(self, session_class):
        tracer = self
        self._old = {name: getattr(session_class, name)
                     for name in ("__init__", "execute", "save", "close")}
        original = self._old

        def init(native, *args, **kwargs):
            t = time.perf_counter_ns()
            answer = original["__init__"](native, *args, **kwargs)
            if tracer.enabled:
                tracer.events.append({"type": "session_open",
                                      "wall_ms": (time.perf_counter_ns() - t) / 1e6})
            return answer

        def execute(native, source):
            if not tracer.enabled:
                return original["execute"](native, source)
            pid = native.process.pid
            before_cpu, before_io = cpu_ms(pid), io_counters(pid)
            start = time.perf_counter_ns()
            try:
                return original["execute"](native, source)
            finally:
                elapsed = (time.perf_counter_ns() - start) / 1e6
                after_cpu, after_io = cpu_ms(pid), io_counters(pid)
                peak = vmhwm_kib(pid)
                if peak is not None:
                    tracer.native_peak_kib = max(tracer.native_peak_kib, peak)
                tracer.events.append({
                    "type": "execute", "wall_ms": elapsed,
                    "source_bytes": len(source.encode("utf-8")),
                    "calls": invoked_calls(source),
                    "native_cpu_ms": max(0.0, after_cpu - before_cpu)
                    if before_cpu is not None and after_cpu is not None else None,
                    "native_io_bytes": difference(after_io, before_io),
                })

        def save(native, target):
            start = time.perf_counter_ns()
            try:
                return original["save"](native, target)
            finally:
                if tracer.enabled:
                    tracer.events.append({"type": "save",
                                          "wall_ms": (time.perf_counter_ns() - start) / 1e6})

        def close(native):
            start = time.perf_counter_ns()
            try:
                return original["close"](native)
            finally:
                if tracer.enabled:
                    tracer.events.append({"type": "close",
                                          "wall_ms": (time.perf_counter_ns() - start) / 1e6})

        session_class.__init__ = init
        session_class.execute = execute
        session_class.save = save
        session_class.close = close
        self._class = session_class

    def detach(self):
        if self._old:
            for name, function in self._old.items():
                setattr(self._class, name, function)

    def reset(self):
        self.events.clear()
        self.native_peak_kib = 0


def summarize_events(events: list[dict[str, Any]]) -> dict[str, Any]:
    types: dict[str, dict[str, float]] = {}
    calls: dict[str, dict[str, float]] = {}
    native_cpu = 0.0
    native_source = 0
    native_io = {"read_bytes": 0, "write_bytes": 0}
    for event in events:
        entry = types.setdefault(event["type"], {"count": 0, "wall_ms": 0.0})
        entry["count"] += 1
        entry["wall_ms"] += event["wall_ms"]
        if event["type"] != "execute":
            continue
        native_source += event["source_bytes"]
        if event["native_cpu_ms"] is not None:
            native_cpu += event["native_cpu_ms"]
        for key in native_io:
            native_io[key] += event["native_io_bytes"].get(key, 0)
        for call in event["calls"]:
            line = calls.setdefault(call, {"count": 0, "enclosing_exec_wall_ms": 0.0})
            line["count"] += 1
            line["enclosing_exec_wall_ms"] += event["wall_ms"]
    # Do not sum per-call "enclosing" durations: several calls can share a packet.
    return {
        "native_api": types, "call_invocations": calls,
        "source_bytes_sent_to_xi": native_source,
        "native_cpu_ms_observed": round(native_cpu, 3),
        "native_io_bytes_observed": native_io,
    }


def run_worker(scenario: str) -> dict[str, Any]:
    from integration.unified.common import C1
    from integration.unified.session import Session

    native = NativeTrace()
    native.attach(C1.XiSession)
    try:
        with tempfile.TemporaryDirectory(prefix="bbyq-c00-no-user-state-") as directory:
            db = Path(directory) / "sandbox.sqlite"
            with ExitStack() as stack:
                if scenario == "initialization":
                    native.reset()
                    native.enabled = True
                    t0, c0, io0 = time.perf_counter_ns(), usage_cpu_ms(), io_counters(os.getpid())
                    session = stack.enter_context(Session(db))
                    session.snapshot()
                    elapsed = (time.perf_counter_ns() - t0) / 1e6
                    cpu = usage_cpu_ms() - c0
                    own_io = difference(io_counters(os.getpid()), io0)
                    valid = True
                    status = "initialized"
                else:
                    session = stack.enter_context(Session(db))
                    if scenario in ("feedback", "replay"):
                        original = session.turn("prime", MISSION)
                        if not original["ok"]:
                            raise AssertionError("Could not prepare frozen mission")
                        frozen = session.snapshot()
                    native.reset()
                    native.enabled = True
                    t0, c0, io0 = time.perf_counter_ns(), usage_cpu_ms(), io_counters(os.getpid())
                    if scenario == "arithmetic":
                        result = session.turn("check", "calcula 7 + 3")
                        valid = bool(result["ok"])
                    elif scenario == "text":
                        result = session.turn("check", "¿puedes decir qué es memoria?")
                        # Diagnostic only. A refusal is not called an accuracy failure.
                        valid = isinstance(result.get("results"), list)
                    elif scenario == "mission":
                        result = session.turn("check", MISSION)
                        task = result["results"][-1] if result["results"] else {}
                        valid = bool(result["ok"] and task.get("voice", {}).get("faithful"))
                    elif scenario == "feedback":
                        result = session.turn("check", "aprende de la última tarea")
                        valid = bool(result["ok"] and result["results"][-1]["kind"] == "feedback")
                    elif scenario == "replay":
                        result = session.turn("prime", MISSION)
                        valid = result == original and session.snapshot() == frozen
                    else:
                        raise ValueError("Unknown C00 case: " + scenario)
                    elapsed = (time.perf_counter_ns() - t0) / 1e6
                    cpu = usage_cpu_ms() - c0
                    own_io = difference(io_counters(os.getpid()), io0)
                    status = "ok" if result.get("ok") else "abstained_or_rejected"
                native.enabled = False
                report = {
                    "scenario": scenario,
                    "valid": valid,
                    "outcome": status,
                    "wall_ms": round(elapsed, 3),
                    "python_cpu_ms": round(cpu, 3),
                    "python_io_bytes": own_io,
                    "native_vm_hwm_kib_observed": native.native_peak_kib,
                    "python_vm_hwm_kib_process": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
                    "native_trace": summarize_events(native.events),
                }
                if not valid:
                    raise AssertionError(f"C00 invariant failed for {scenario}: {status}")
                return report
    finally:
        native.enabled = False
        native.detach()


def system_profile() -> dict[str, Any]:
    cpu_model = None
    try:
        for line in Path("/proc/cpuinfo").read_text().splitlines():
            if line.startswith("model name"):
                cpu_model = line.split(":", 1)[1].strip()
                break
    except OSError:
        pass
    return {
        "platform": platform.platform(),
        "python": platform.python_version(),
        "cpu_model": cpu_model,
        "logical_cpus": os.cpu_count(),
        "github_runner": bool(os.getenv("GITHUB_ACTIONS")),
        "github_sha": os.getenv("GITHUB_SHA"),
        "reproducibility_note": "CPU, RSS and I/O are host/runner measurements, not Android measurements.",
    }


def run_parent(samples: int, timeout: int, destination: Path) -> dict[str, Any]:
    before = freeze_assets()
    apk_before = apk_files()
    groups: dict[str, list[dict[str, Any]]] = {}
    for scenario in SCENARIOS:
        groups[scenario] = []
        for i in range(samples):
            proc = subprocess.run(
                [sys.executable, "-m", "integration.audit_u03_c00.profile", "--worker", scenario],
                cwd=ROOT, text=True, capture_output=True, timeout=timeout,
                check=False,
            )
            if proc.returncode:
                raise RuntimeError(
                    f"C00 {scenario} iteration {i + 1} failed (exit {proc.returncode}): "
                    + proc.stderr[-6000:] + proc.stdout[-1500:]
                )
            raw = proc.stdout.strip().splitlines()
            if not raw:
                raise RuntimeError(f"C00 {scenario} did not emit measurements")
            data = json.loads(raw[-1])
            groups[scenario].append(data)
    after = freeze_assets()
    newly_created_apks = apk_files() - apk_before
    if before != after:
        changed = sorted(set(before) ^ set(after) |
                         {k for k in before.keys() & after.keys() if before[k] != after[k]})
        raise AssertionError("Frozen checkpoint/source changed: " + ", ".join(changed[:12]))
    if newly_created_apks:
        raise AssertionError("C00 must not build an APK: " + str(sorted(newly_created_apks)))
    aggregates = {}
    for mode, records in groups.items():
        aggregates[mode] = {
            "wall_ms": stats([row["wall_ms"] for row in records]),
            "python_cpu_ms": stats([row["python_cpu_ms"] for row in records]),
            "source_bytes_sent_to_xi": stats([
                row["native_trace"]["source_bytes_sent_to_xi"] for row in records]),
            "execute_calls": stats([
                row["native_trace"]["native_api"].get("execute", {}).get("count", 0)
                for row in records]),
        }
    result = {
        "schema": "BBYQ-U03-C00-v1",
        "parent_commit": PINNED_PARENT,
        "system": system_profile(),
        "scenario_count": len(SCENARIOS),
        "samples_per_scenario": samples,
        "all_case_invariants_passed": all(
            item["valid"] for rows in groups.values() for item in rows),
        "frozen_asset_count": len(before),
        "frozen_asset_sha256": before,
        "checkpoint_and_source_unchanged": before == after,
        "new_apks": [],
        "apk_built": False,
        "measurements": groups,
        "aggregates": aggregates,
        "methodology": [
            "One new subprocess and throwaway SQLite database for each observation.",
            "Source files and checkpoint archives hashed before and after.",
            "Wall timing excludes unrelated setup except in initialization.",
            "XI EXEC telemetry includes host-to-native source bytes and observed native CPU.",
            "Per-call durations are enclosing packet durations, not exclusive function times.",
            "VmHWM and proc I/O are Linux estimates and may be unavailable on other hosts.",
            "Text refusal is observed, not falsely scored as a correct definition.",
            "No personal data, retraining, installation, Gradle or APK compilation.",
        ],
    }
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n")
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description="Audit BBY Q C00 without modifying trained banks")
    parser.add_argument("--worker", choices=SCENARIOS, help=argparse.SUPPRESS)
    parser.add_argument("--samples", type=int, default=2)
    parser.add_argument("--timeout", type=int, default=160)
    parser.add_argument("--out", type=Path, default=ROOT / "build/c00/profile.json")
    options = parser.parse_args()
    if options.worker:
        print(json.dumps(run_worker(options.worker), ensure_ascii=False))
    else:
        if not 1 <= options.samples <= 20 or not 20 <= options.timeout <= 1200:
            parser.error("samples must be 1..20 and timeout 20..1200")
        report = run_parent(options.samples, options.timeout, options.out)
        print(json.dumps({
            "passed": report["all_case_invariants_passed"],
            "assets_unchanged": report["checkpoint_and_source_unchanged"],
            "frozen_assets": report["frozen_asset_count"],
            "samples_per_scenario": report["samples_per_scenario"],
            "wall_ms": {k: v["wall_ms"] for k, v in report["aggregates"].items()},
            "apk_built": False,
            "output": str(options.out),
        }, ensure_ascii=False))


if __name__ == "__main__":
    main()
