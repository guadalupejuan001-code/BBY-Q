"""Android XiSession transport for original BBY Q U02 C1/E02 runtime.

The original Linux XI subprocess is replaced by the same native
reverse_pc::rvpc2::Runtime exposed through JNI. The original sources and
original checkpoints are unmodified and remain SHA-validated.
"""
import json
from pathlib import Path
import time
from java import jclass

Native = jclass("com.bbyq.personal.XiSession")


class XiSession:
    def __init__(self, binary, state):
        self.handle = None
        state = Path(state)
        if not state.is_file():
            raise FileNotFoundError(f"Original XI state missing: {state}")
        self.handle = Native.open(state.read_bytes())
        if not self.handle:
            raise RuntimeError("Native REVERSE-PC XI JNI session unavailable")
        self.execute_count = 0

    def execute(self, source):
        if self.handle is None:
            raise RuntimeError("Closed XI session")
        start = time.perf_counter_ns()
        raw = bytes(Native.execute(self.handle, source))
        text = raw.decode("utf-8")
        events = [json.loads(line) for line in text.splitlines()
                  if line.startswith("{")]
        self.execute_count += 1
        return events, (time.perf_counter_ns() - start) / 1e6

    def save(self, destination):
        if self.handle is None:
            raise RuntimeError("Closed XI session")
        dest = Path(destination)
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(bytes(Native.checkpoint(self.handle)))

    def metrics(self):
        # No synthetic CPU/IO metrics: Android host doesn't expose CLI /proc.
        return {"xi_jni_invocations": self.execute_count,
                "measured_runtime_cpu_ms": None}

    def close(self):
        if self.handle is not None:
            Native.release(self.handle)
            self.handle = None

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()
