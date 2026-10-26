"""Measure real XI transport, snapshot size and process cost, with no invented numbers."""
import json
import os
import platform
import resource
import statistics
import tempfile
import time
from pathlib import Path

from bbyq.model import experience, new_entity
from bbyq.store import NativeStore


def main():
    with tempfile.TemporaryDirectory(prefix="bbyq-bench-") as folder:
        store = NativeStore(Path(folder) / "bench.rvp")
        store.initialize(new_entity("native-benchmark"))
        durations = []
        for i in range(24):
            observation = {"signal": ((i * 7 % 21) - 10) / 10,
                           "pressure": ((i * 11 % 21) - 10) / 10}
            t0 = time.perf_counter_ns()
            store.transact(lambda state: experience(state, observation,
                                                   -1 if i % 2 == 0 else 1, int(i % 3 == 0)))
            durations.append((time.perf_counter_ns() - t0) / 1e6)
        current = store.read()
        info = store.stats()
        assert current["steps"] == 24
        metrics = {
            "experiment": "BBYQ-NATIVE-B001", "iterations": 24,
            "milliseconds_per_persisted_step": durations,
            "median_milliseconds": statistics.median(durations),
            "p95_milliseconds_nearest_rank": sorted(durations)[22],
            "state_bytes_RVPC2": info["rvpc2_bytes"],
            "native_stats": info["native"],
            "ru_maxrss_kib_linux": resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss
            if platform.system() == "Linux" else None,
            "python_version": platform.python_version(), "os": platform.platform(),
            "runtime_path": os.environ.get("BBYQ_REVERSE_PC"),
            "notes": "Real subprocess XI read/modify/write latency. No quantum speedup implied. "
                     "Max RSS covers child processes, not isolated allocator bytes.",
        }
        out = Path(os.environ.get("BBYQ_NATIVE_BENCH_OUTPUT", folder + "/result.json"))
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(metrics, indent=2, sort_keys=True) + "\n")
        print(json.dumps(metrics, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
