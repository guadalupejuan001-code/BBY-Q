"""Actual original XI JNI transport with optional C01 library references.

No inference outputs or native states are memoized. Every request executes
Runtime::execute. Profiling records host/JNI packet wall, not gate CPU.
"""
from contextlib import contextmanager
from contextvars import ContextVar
from pathlib import Path
import json
import time
from java import jclass

Native = jclass("com.bbyq.personal.XiSession")
_SOURCE_CACHE = ContextVar("u03_mobile_source_cache", default=False)
_PACKET_SINK = ContextVar("u03_mobile_packet_sink", default=None)

@contextmanager
def transport_scope(*, cached=False, packets=None):
    a = _SOURCE_CACHE.set(bool(cached))
    b = _PACKET_SINK.set(packets)
    try:
        yield
    finally:
        _PACKET_SINK.reset(b)
        _SOURCE_CACHE.reset(a)

class XiSession:
    def __init__(self, binary, state):
        self.handle = None
        self.path = Path(state)
        if not self.path.is_file():
            raise FileNotFoundError(f"Original XI checkpoint missing: {state}")
        self.handle = Native.open(self.path.read_bytes())
        if not self.handle:
            raise RuntimeError("Original REVERSE-PC JNI session unavailable")
        self.execute_count = 0
        self._libraries = {}
        self._cached = _SOURCE_CACHE.get()
        self._sink = _PACKET_SINK.get()
        self.source_bytes_sent = 0

    def execute(self, source):
        if self.handle is None:
            raise RuntimeError("Closed XI session")
        started = time.perf_counter_ns()
        prefix, split, library = source.partition("\nhalt\n")
        if self._cached and split and library:
            identifier = self._libraries.get(library)
            if identifier is None:
                identifier = int(Native.internLibrary(self.handle, library))
                self._libraries[library] = identifier
                self.source_bytes_sent += len(library.encode())
            variable = prefix + split
            raw = bytes(Native.executeReference(self.handle, identifier, variable))
            self.source_bytes_sent += len(variable.encode())
        else:
            raw = bytes(Native.execute(self.handle, source))
            self.source_bytes_sent += len(source.encode())
        ended = time.perf_counter_ns()
        events = [json.loads(row) for row in raw.decode("utf-8").splitlines()
                  if row.startswith("{")]
        self.execute_count += 1
        if self._sink is not None:
            # Exclude library definitions after HALT from executed-call labels.
            import re
            self._sink.append({
                "bank":self.path.stem, "start_ns":started, "end_ns":ended,
                "host_packet_ms":(ended-started)/1e6,
                "calls":re.findall(r"(?m)^\s*call\s+([a-zA-Z0-9_]+)\s*$",prefix),
                "source_bytes":len(source.encode()),
                "cached_transport":self._cached,
            })
        return events, (ended-started)/1e6

    def save(self, destination):
        if self.handle is None:
            raise RuntimeError("Closed XI session")
        dest=Path(destination)
        dest.parent.mkdir(parents=True,exist_ok=True)
        dest.write_bytes(bytes(Native.checkpoint(self.handle)))

    def metrics(self):
        if self.handle is None:
            raise RuntimeError("Closed XI session")
        return {**json.loads(str(Native.transportMetrics(self.handle))),
                "xi_jni_invocations":self.execute_count,
                "python_source_bytes_sent":self.source_bytes_sent,
                "exclusive_native_cpu_ms":None}

    def close(self):
        if self.handle is not None:
            Native.releaseIntegrated(self.handle)
            self.handle=None
            self._libraries.clear()

    def __enter__(self):return self
    def __exit__(self,*args):self.close()
