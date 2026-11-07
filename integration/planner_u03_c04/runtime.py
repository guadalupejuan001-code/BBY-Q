"""U03 C04 opt-in native resource planner; exact U02 control flow.

Expensive VQC, QRL, QMemory, entity and voice XI processes are LAZY:
opening a native bank happens only when its original runtime method
actually asks to execute/read it. All original XI instructions are still
executed in order, and all checkpoint bytes and rollback paths stay U02.

Only SHA-256 calculations over independent immutable bank blobs run in
parallel. SQLite rows and Python native sessions are never accessed by
worker threads.
"""
from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from contextvars import ContextVar
from hashlib import sha256
from types import FunctionType, SimpleNamespace
from typing import Any

from integration.unified import session as frozen_session
from integration.unified import quantum as frozen_quantum
from integration.unified import contracts as frozen_contracts
from integration.unified import common as frozen_common
from integration.cache_u03_c03.session import CachedSession
from .planner import make_plan, topological_order

_METRICS: ContextVar[dict[str, Any] | None] = ContextVar(
    "bbyq_u03_c04_turn_plan", default=None
)
_ORIGINAL_XI_SESSION = frozen_common.C1.XiSession


def _stats() -> dict:
    return {
        "native_lazy_bank_handles": 0,
        "native_bank_processes_started": [],
        "native_bank_processes_avoided": [],
        "immutable_bank_hashes_verified": 0,
        "hash_worker_count": 0,
        "stateful_xi_circuits_skipped": 0,
        "native_stateful_parallel_executions": 0,
        "dependency_plan": None,
    }


class LazyNativeBank:
    """Context-managed exact original XI session instantiated on first use."""

    def __init__(self, binary, state):
        self._binary = binary
        self._state = state
        self._native = None
        self._closed = False
        self._metrics = _METRICS.get()
        self._name = getattr(state, "stem", str(state).split("/")[-1].split(".")[0])
        if self._metrics is not None:
            self._metrics["native_lazy_bank_handles"] += 1

    def _backend(self):
        if self._closed:
            raise RuntimeError("C04 attempted access to a closed native bank")
        if self._native is None:
            self._native = _ORIGINAL_XI_SESSION(self._binary, self._state)
            if self._metrics is not None:
                self._metrics["native_bank_processes_started"].append(self._name)
        return self._native

    def execute(self, source):
        return self._backend().execute(source)

    def save(self, path):
        return self._backend().save(path)

    def metrics(self):
        return self._backend().metrics()

    @property
    def process(self):
        return self._backend().process

    def close(self):
        if not self._closed:
            self._closed = True
            if self._native is not None:
                self._native.close()
            elif self._metrics is not None:
                self._metrics["native_bank_processes_avoided"].append(self._name)

    def __enter__(self):
        if self._closed:
            raise RuntimeError("C04 cannot reenter a closed native bank")
        return self

    def __exit__(self, *_):
        self.close()


class _C1Proxy:
    """Only C1.XiSession is virtualized; all other frozen fields forwarded."""

    XiSession = LazyNativeBank

    def __getattr__(self, item):
        return getattr(frozen_common.C1, item)


class LazyReadoutQuantum(frozen_quantum.Quantum):
    """Defer read-only V3 magic probe until V3 is actually needed.

    A quantum language math or status task does not need its classifier.
    For perception, policy, feedback and any derived-fact refresh the original
    VQC readout is loaded from the same native state through the original
    integer() call. No measurements, parameters or instructions are removed.
    """

    def __init__(self, sessions, metadata, directory, project):
        self.sessions = sessions
        self.meta = metadata
        self.directory = directory
        self.project = project
        self.trace = []
        self._readout = None

    @property
    def readout_magic(self):
        if self._readout is None:
            self._readout = frozen_common.integer(self.sessions["v3"], frozen_quantum.P.B)
        return self._readout

    @property
    def perception_active(self):
        return self.readout_magic == frozen_quantum.P.MAGIC


class PlannedTools(frozen_contracts.Tools):
    def parse(self, prompt):
        parsed = super().parse(prompt)
        result = make_plan(parsed)
        topological_order(result)
        stats = _METRICS.get()
        if stats is not None:
            stats["dependency_plan"] = result.as_dict()
        return parsed


def _clone_with_globals(method, overrides):
    ns = dict(method.__globals__)
    ns.update(overrides)
    copy = FunctionType(
        method.__code__, ns, method.__name__,
        method.__defaults__, method.__closure__,
    )
    copy.__kwdefaults__ = method.__kwdefaults__
    return copy


# The original U02 turn BYTECODE, not a rewrite of its inference logic.
# A separate globals namespace avoids per-thread monkey-patching.
_PLANNED_TURN = _clone_with_globals(
    frozen_session.Session.turn,
    {
        "C1": _C1Proxy(),
        "Quantum": LazyReadoutQuantum,
        "Tools": PlannedTools,
    },
)


class PlannedSession(CachedSession):
    """C04 planner with optional C03 immutable model cache and parallel SHA."""

    def __init__(self, database, readers=None, *, parallel_hash_workers=4, memo=None):
        if not 1 <= parallel_hash_workers <= 8:
            raise ValueError("C04 hash worker budget must be 1..8")
        self._hash_workers = parallel_hash_workers
        self.last_plan_stats = _stats()
        super().__init__(database, readers=readers, memo=memo)

    def _banks(self):
        # SQLite connection is used ONLY on the calling thread.
        rows = list(self.db.execute("SELECT name,snapshot,sha FROM unified_banks"))
        workers = min(self._hash_workers, len(rows))
        if workers > 1:
            with ThreadPoolExecutor(max_workers=workers) as pool:
                hashes = list(pool.map(lambda row: sha256(row[1]).hexdigest(), rows))
        else:
            hashes = [sha256(raw).hexdigest() for _, raw, _ in rows]
        stats = _METRICS.get()
        if stats is not None:
            stats["immutable_bank_hashes_verified"] = len(rows)
            stats["hash_worker_count"] = workers
        for (name, _, expected), actual in zip(rows, hashes):
            if actual != expected:
                raise ValueError("Corrupt unified bank: " + name)
        return {name: raw for name, raw, _ in rows}

    def turn(self, request_id, prompt, payload=None, fail_after=None, control=None):
        stats = _stats()
        token = _METRICS.set(stats)
        try:
            return _PLANNED_TURN(
                self, request_id, prompt,
                payload=payload, fail_after=fail_after, control=control,
            )
        finally:
            self.last_plan_stats = stats
            _METRICS.reset(token)
