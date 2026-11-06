"""Opt-in, bounded program-library transport using original XI execution.

Only the *transport* is cached, never the quantum state or model parameters.
The old native API remains the default. Instrumentation is isolated by context.
"""
from __future__ import annotations

from contextlib import contextmanager
import json
from pathlib import Path

from integration.unified import common
from integration.unified import quantum as quantum_module

BASE_XI = common.C1.XiSession
ROOT = common.ROOT
C01_BINARY = ROOT / "deps/reverse-pc/build/xi_session_c01"
DELIMITER = "\nhalt\n"
MIN_LIBRARY_BYTES = 512


class CachedXiSession(BASE_XI):
    """Native session with source-library registration, no changes to XI semantics."""

    stats = {
        "libraries_registered": 0,
        "library_cache_hits": 0,
        "exec_ref": 0,
        "exec_fallback": 0,
        "xi_wire_payload_bytes": 0,
        "logical_execute_source_bytes": 0,
    }

    @classmethod
    def reset_counters(cls) -> None:
        cls.stats = {name: 0 for name in cls.stats}

    def __init__(self, binary, state):
        del binary  # Experimental binary is explicit and cannot replace standard XI.
        if not C01_BINARY.is_file():
            raise FileNotFoundError("C01 native binary must be built separately: " + str(C01_BINARY))
        super().__init__(C01_BINARY, state)
        self._libraries: dict[str, int] = {}
        try:
            capabilities, _ = self._request("C01CAP")
            if json.loads(capabilities).get("cached_library_transport") != 1:
                raise RuntimeError("C01 cached transport capability not available")
        except BaseException:
            self.close()
            raise

    def _cached_request(self, command: str, payload: str):
        # Count the bytes sent over native stdin (excludes a few bytes of
        # packet header; all experimental variants use identical framing).
        self.stats["xi_wire_payload_bytes"] += len(payload.encode("utf-8"))
        return super()._request(command, payload)

    def execute(self, source: str):
        if not isinstance(source, str):
            raise TypeError("XI source must be text")
        self.stats["logical_execute_source_bytes"] += len(source.encode("utf-8"))
        prefix, marker, library = source.partition(DELIMITER)
        if marker and len(library.encode("utf-8")) >= MIN_LIBRARY_BYTES:
            prepared = prefix + marker
            number = self._libraries.get(library)
            if number is None:
                response, _ = self._cached_request("CODELIB", library)
                number = int(response)
                if number <= 0:
                    raise RuntimeError("Invalid C01 library handle")
                self._libraries[library] = number
                self.stats["libraries_registered"] += 1
            else:
                self.stats["library_cache_hits"] += 1
            result, elapsed = self._cached_request("EXECREF", f"{number}\n{prepared}")
            self.stats["exec_ref"] += 1
        else:
            result, elapsed = self._cached_request("EXEC", source)
            self.stats["exec_fallback"] += 1
        return [json.loads(row) for row in result.splitlines() if row.startswith("{")], elapsed


@contextmanager
def activate():
    """Install C01 only within an experiment and restore every original alias."""
    slots = [
        (common.C1, "XiSession"),
        (common, "XiSession"),
        (quantum_module, "XiSession"),
    ]
    old = [(module, key, getattr(module, key)) for module, key in slots]
    try:
        for module, key, _ in old:
            setattr(module, key, CachedXiSession)
        yield CachedXiSession
    finally:
        for module, key, original in reversed(old):
            setattr(module, key, original)
