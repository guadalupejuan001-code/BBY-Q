"""C03: transactional, turn-local memoization of native XI readouts.

The original U02 Session.turn bytecode executes with an isolated global name
binding for Quantum. Neither the original source, SQLite schema, native XI
code, checkpoints nor model parameters are changed. The memo exists only
inside one C03Quantum instance and is destroyed at the end of that turn.

A hit reuses prior *native* events, and still executes the original symbolic
projection/contract code. A hit does not claim to have executed XI twice.
The original U02 trace format is retained for exact receipt compatibility;
actual cache hits are measured separately.
"""
from __future__ import annotations

from collections import OrderedDict
from contextvars import ContextVar
from copy import deepcopy
from hashlib import sha256
from types import FunctionType
from typing import Any

from integration.unified import session as unified_session
from integration.unified.quantum import Quantum as BaseQuantum
from integration.unified.common import A

_CACHE_STATS: ContextVar[dict[str, Any] | None] = ContextVar(
    "bbyq_c03_turn_cache_stats", default=None
)
CACHE_CAPACITY = 8


def fresh_stats() -> dict[str, Any]:
    return {
        "vqc_hits": 0, "vqc_misses": 0,
        "memory_hits": 0, "memory_misses": 0,
        "invalidations": {"v3": 0, "memory": 0},
        "evictions": 0,
        "avoided_native_exec": 0, "avoided_source_bytes": 0,
        "cache_scope": "single-turn-only",
    }


class C03Quantum(BaseQuantum):
    """Reuse identical classifier and read-only memory events within one turn.

    Any *other* native call to the affected bank invalidates its cache. A
    feedback update, QRL policy step, quantum association write, or changed
    readout therefore never borrows the earlier native result. Cache keys
    contain the complete program body, model revision and readout version.
    """

    def __init__(self, sessions, metadata, directory, project):
        super().__init__(sessions, metadata, directory, project)
        self._c03_caches: dict[str, OrderedDict] = {
            "v3": OrderedDict(), "memory": OrderedDict()
        }
        self._c03_epochs = {"v3": 0, "memory": 0}
        self._c03_stats = _CACHE_STATS.get()

    def _invalidate(self, bank: str) -> None:
        self._c03_epochs[bank] += 1
        cache = self._c03_caches[bank]
        if cache:
            cache.clear()
        if self._c03_stats is not None:
            self._c03_stats["invalidations"][bank] += 1

    @staticmethod
    def _eligible(bank: str, body: str, operation: str, details: dict) -> bool:
        if bank == "v3" and operation == "vqc_forward":
            # Explicit counterfactual controls must always execute natively.
            return (
                details.get("input_sha256") is not None
                and f"store64 {A + 280} 0\n" in body
                and "call select_agent\ncall forward\n" in body
                and "call u2_apply" in body
            )
        if bank == "memory" and operation == "qm_read":
            # Erased-memory ablation calls qprepare; never cache those.
            return "qprepare" not in body and "fexpect" in body
        return False

    def stage(self, bank, body, operation, **details):
        if bank not in self._c03_caches:
            return super().stage(bank, body, operation, **details)
        if not self._eligible(bank, body, operation, details):
            self._invalidate(bank)
            return super().stage(bank, body, operation, **details)

        # Hash full canonical native body, *not* only name or seed; revision
        # and readout magic prevent cross-parameter accidental reuse.
        identity = (
            operation,
            sha256(body.encode("utf-8")).digest(),
            self._c03_epochs[bank],
            self.meta.get("perception_revision", 0),
            self.readout_magic if bank == "v3" else None,
            tuple(sorted(details.items())),
        )
        cache = self._c03_caches[bank]
        suffix = "vqc" if bank == "v3" else "memory"
        if identity in cache:
            events = cache[identity]
            cache.move_to_end(identity)
            # Preserve the original trace/receipts while distinguishing
            # executed vs reused work in instrumentation (NOT in model state).
            self.trace.append({
                "bank": bank, "operation": operation, "native": True, **details
            })
            if self._c03_stats is not None:
                self._c03_stats[suffix + "_hits"] += 1
                self._c03_stats["avoided_native_exec"] += 1
                self._c03_stats["avoided_source_bytes"] += len(body.encode("utf-8"))
            return deepcopy(events)

        events = super().stage(bank, body, operation, **details)
        # Only successfully completed native observations may enter the cache.
        cache[identity] = deepcopy(events)
        if len(cache) > CACHE_CAPACITY:
            cache.popitem(last=False)
            if self._c03_stats is not None:
                self._c03_stats["evictions"] += 1
        if self._c03_stats is not None:
            self._c03_stats[suffix + "_misses"] += 1
        return events


# U02 source is frozen by its release manifest. Bind its *original* turn
# function to an isolated globals dictionary, changing only the Quantum
# dependency. This avoids unsafe global monkey-patching across threads and
# preserves all original U02 control-flow, atomic commit, error paths and
# checkpoint serialization.
_ORIGINAL_TURN = unified_session.Session.turn
if "Quantum" not in _ORIGINAL_TURN.__code__.co_names:
    raise RuntimeError("C03: U02 turn no longer loads Quantum; explicit audit required")
_ISOLATED_GLOBALS = dict(_ORIGINAL_TURN.__globals__)
_ISOLATED_GLOBALS["Quantum"] = C03Quantum
_C03_TURN = FunctionType(
    _ORIGINAL_TURN.__code__,
    _ISOLATED_GLOBALS,
    _ORIGINAL_TURN.__name__,
    _ORIGINAL_TURN.__defaults__,
    _ORIGINAL_TURN.__closure__,
)
_C03_TURN.__kwdefaults__ = _ORIGINAL_TURN.__kwdefaults__


class CachedSession(unified_session.Session):
    """Opt-in C03 API. Standard Session and C02 never see this cache."""

    def __init__(self, database, readers=None):
        super().__init__(database, readers)
        self.last_cache_stats = fresh_stats()

    def turn(self, request_id, prompt, payload=None, fail_after=None, control=None):
        stats = fresh_stats()
        token = _CACHE_STATS.set(stats)
        try:
            return _C03_TURN(
                self, request_id, prompt,
                payload=payload, fail_after=fail_after, control=control,
            )
        finally:
            self.last_cache_stats = stats
            _CACHE_STATS.reset(token)
