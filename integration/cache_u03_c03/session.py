"""C03: checksum-keyed cache of *immutable* native model checkpoints.

The original U02 Session and XI/Ether runtime are untouched. In particular,
native VQC/QRL/Memory operations are NEVER skipped: trial C03-0 proved that
eliding a repeated forward changed 32,155 bytes of the V3 checkpoint.

C03 therefore eliminates only repeated authenticated decompression and
source loading for immutable, frozen release archives, across Session opens
in the same explicit scope. Every cache lookup re-hashes its dependencies;
the original SHA-bound loader runs on every miss.
"""
from __future__ import annotations

from collections import OrderedDict
from contextlib import contextmanager
from contextvars import ContextVar
from hashlib import sha256
import json
from pathlib import Path
from threading import RLock
from types import FunctionType, SimpleNamespace

from integration.unified import session as unified_session
from integration.unified import common
from integration.sequence2 import workspace as c1_workspace

ROOT = common.ROOT
_MAX_CACHE_BYTES = 96 * 1024 * 1024
_CURRENT_CACHE: ContextVar["ArchiveMemo | None"] = ContextVar(
    "bbyq_u03_c03_archive_cache", default=None
)


def _program_files(kind: str, folder: Path) -> tuple[Path, ...]:
    """Exactly the inputs on which the original authenticating loader depends."""
    folder = Path(folder).resolve()
    manifest_path = folder / "manifest.json"
    if not manifest_path.is_file():
        # Development folders without an immutable manifest are not cached.
        return ()
    manifest = json.loads(manifest_path.read_text())
    files = {manifest_path}
    for source in manifest.get("sources", {}):
        files.add(ROOT / source)
    for source in manifest.get("native_source_sha256", {}):
        files.add(ROOT / source)
    if kind in ("router", "c1"):
        files.update(folder / name for name in (
            "vocabulary.json", "output-vocabulary.json",
            "semantic-vocabulary.json", "model.xi",
        ) if (folder / name).is_file())
    if kind == "router":
        files.update(folder / part["file"] for part in manifest["router"]["parts"])
    elif kind == "perception":
        item = manifest.get("perception")
        if item is not None:
            files.add(folder / item["file"])
    elif kind == "c1":
        for item in manifest["models"].values():
            files.update(folder / part["file"] for part in item["parts"])
    elif kind == "entity":
        files.update(folder / item["file"] for item in manifest["models"].values())
    else:
        raise ValueError("Unsupported archive cache kind")
    return tuple(sorted(Path(p).resolve() for p in files))


def _bound_input_digest(kind: str, folder: Path) -> tuple[str, int] | None:
    """Re-hash the actual input bytes on EVERY lookup, not stat or mtime."""
    deps = _program_files(kind, folder)
    if not deps:
        return None
    h = sha256()
    total = 0
    for path in deps:
        raw = path.read_bytes()
        total += len(raw)
        h.update(str(path).encode("utf-8"))
        h.update(b"\0")
        h.update(len(raw).to_bytes(8, "little"))
        h.update(raw)
    return h.hexdigest(), total


def _weight(value):
    if isinstance(value, (bytes, bytearray)):
        return len(value)
    if isinstance(value, dict):
        return sum(_weight(item) for item in value.values())
    raise TypeError("C03 may cache only immutable checkpoint bytes")


def _copy_immutable(value):
    if isinstance(value, bytes):
        return value
    if isinstance(value, dict):
        return dict(value)
    raise TypeError("C03 cannot publish mutable model objects")


class ArchiveMemo:
    """Thread-safe bounded archive cache with content-verified invalidation."""

    def __init__(self, max_bytes=_MAX_CACHE_BYTES, max_entries=12):
        if max_bytes < 1 or max_entries < 1:
            raise ValueError("Cache capacities must be positive")
        self.max_bytes, self.max_entries = int(max_bytes), int(max_entries)
        self._entries = OrderedDict()
        self._bytes = 0
        self._lock = RLock()
        self.stats = {
            "hits": 0, "misses": 0, "evictions": 0,
            "reused_checkpoint_bytes": 0,
            "validated_input_bytes": 0, "bypassed_native_executions": 0,
        }

    def get(self, kind: str, folder: Path, loader):
        folder = Path(folder).resolve()
        with self._lock:
            signature = _bound_input_digest(kind, folder)
            if signature is None:
                self.stats["misses"] += 1
                return loader()
            fingerprint, source_bytes = signature
            self.stats["validated_input_bytes"] += source_bytes
            key = (kind, str(folder), fingerprint)
            if key in self._entries:
                value, weight = self._entries[key]
                self._entries.move_to_end(key)
                self.stats["hits"] += 1
                self.stats["reused_checkpoint_bytes"] += weight
                return _copy_immutable(value)

            self.stats["misses"] += 1
            # Original loader performs binding, gzip and SHA verification.
            value = loader()
            weight = _weight(value)
            if weight <= self.max_bytes:
                # Expire older identities for same kind/path on source change.
                for prior in list(self._entries):
                    if prior[:2] == key[:2]:
                        self._bytes -= self._entries.pop(prior)[1]
                while self._entries and (
                    self._bytes + weight > self.max_bytes
                    or len(self._entries) >= self.max_entries
                ):
                    _, (_, removed) = self._entries.popitem(last=False)
                    self._bytes -= removed
                    self.stats["evictions"] += 1
                self._entries[key] = (_copy_immutable(value), weight)
                self._bytes += weight
            return _copy_immutable(value)

    def snapshot(self):
        with self._lock:
            return {
                **self.stats, "resident_bytes": self._bytes,
                "entries": len(self._entries),
                "scope": "explicit Python process scope; no personal disk cache",
            }

    def clear(self):
        with self._lock:
            self._entries.clear()
            self._bytes = 0


@contextmanager
def archive_cache_scope(max_bytes=_MAX_CACHE_BYTES, max_entries=12):
    """Share verified immutable archives only during this bounded context."""
    memo = ArchiveMemo(max_bytes=max_bytes, max_entries=max_entries)
    token = _CURRENT_CACHE.set(memo)
    try:
        yield memo
    finally:
        _CURRENT_CACHE.reset(token)
        memo.clear()


def _memoized(kind, folder, loader):
    memo = _CURRENT_CACHE.get()
    if memo is None:
        return loader()
    return memo.get(kind, Path(folder), loader)


def _router(folder):
    return _memoized("router", folder, lambda: unified_session.router_model(folder))


def _perception(folder):
    return _memoized("perception", folder, lambda: unified_session.perception_model(folder))


def _entity_models():
    return _memoized("entity", ROOT / "integration/entity/release", common.entity_models)


def _c1_models(folder):
    return _memoized("c1", folder, lambda: c1_workspace.read_models(folder))


def _clone(method, overrides):
    globals_ = dict(method.__globals__)
    globals_.update(overrides)
    compiled = FunctionType(
        method.__code__, globals_, method.__name__,
        method.__defaults__, method.__closure__,
    )
    compiled.__kwdefaults__ = method.__kwdefaults__
    return compiled


# Both constructors use precisely their original Python bytecode but read
# compressed immutable archives via a scoped, checksum-keyed adapter. No
# module-global monkey patches, no feature ABI changes and no new DB schema.
_C1_INIT = _clone(c1_workspace.Workspace.__init__, {"read_models": _c1_models})


class _CachedLegacyWorkspace(c1_workspace.Workspace):
    __init__ = _C1_INIT


_C03_INIT = _clone(
    unified_session.Session.__init__,
    {
        "router_model": _router,
        "perception_model": _perception,
        "entity_models": _entity_models,
        "Legacy": SimpleNamespace(Workspace=_CachedLegacyWorkspace),
    },
)


class CachedSession(unified_session.Session):
    """Opt-in compatible U02 session; native inference is unchanged."""

    def __init__(self, database, readers=None, memo: ArchiveMemo | None = None):
        active = memo if memo is not None else _CURRENT_CACHE.get()
        token = _CURRENT_CACHE.set(active)
        try:
            _C03_INIT(self, database, readers)
        finally:
            _CURRENT_CACHE.reset(token)
        self.archive_memo = active
        self.last_cache_stats = active.snapshot() if active is not None else {}
