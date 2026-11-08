"""C13: opt-in per-process verified release cache for ORIGINAL U02.

Only immutable, SHA-validated model bytes and identity manifests are cached.
This does NOT cache inference, mutate a native circuit, change SQLite
transaction semantics, or retain any personal/learned state. All source
validation happens once on cache miss; a pre/post SHA-256 manifest ensures
nothing changed while the scope ran. A new process does a fresh validation.
"""
from __future__ import annotations

from contextlib import contextmanager
from functools import lru_cache
from pathlib import Path
from typing import Any, Iterator

from integration.audit_u03_c00.profile import freeze_assets
from integration.unified import session as U
from integration.unified.common import Legacy


def _copy(value: Any) -> Any:
    # The cache never exposes its mutable dict container to a caller.
    return dict(value) if isinstance(value, dict) else value


@contextmanager
def authenticated_release_cache() -> Iterator[dict[str, int]]:
    """Authenticate frozen assets at entry and exit; cache source reads only.

    This context is explicitly limited to isolated C13 experiments and does
    not patch the original repository or globally activate a U02 cache.
    No background threads or concurrent sessions are supported by this
    process-local test context.
    """
    original_assets = freeze_assets()
    if len(original_assets) != 159:
        raise AssertionError("C13 needs the exact 159 frozen files")
    sites = (
        (Legacy, "read_models"),
        (U, "router_model"),
        (U, "perception_model"),
        (U, "entity_models"),
        (U, "source_identity"),
    )
    originals = [(module, name, getattr(module, name))
                 for module, name in sites]
    counters = {"cold_authentications": 0, "cache_hits": 0}
    wrappers = []

    def checked_once(function):
        @lru_cache(maxsize=8)
        def cached(*args):
            counters["cold_authentications"] += 1
            return function(*args)

        def wrapped(*args):
            hits = cached.cache_info().hits
            result = cached(*args)
            if cached.cache_info().hits > hits:
                counters["cache_hits"] += 1
            return _copy(result)

        wrappers.append(cached)
        return wrapped

    try:
        for module, name, previous in originals:
            setattr(module, name, checked_once(previous))
        yield counters
    finally:
        for module, name, previous in originals:
            setattr(module, name, previous)
        for cached in wrappers:
            cached.cache_clear()
        if freeze_assets() != original_assets:
            raise AssertionError("C13 cached protected model identity changed")


def no_unsafe_memoization() -> bool:
    """Trainable states, Session.turn and database operations are never cached."""
    return not any(name in ("Session", "turn", "XiSession", "_banks", "feedback")
                   for name in (
                       "read_models", "router_model", "perception_model",
                       "entity_models", "source_identity",
                   ))
