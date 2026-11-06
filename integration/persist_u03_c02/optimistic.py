"""C02: speculative XI execution against a consistent SQLite snapshot.

Opt-in alternate to Session.turn. The normal U02 path is never monkey-patched.
Heavy XI inference, checkpoint SAVE and full-bank hashing happen on a private
SQLite copy. A short, revision-guarded transaction publishes *row deltas* to
the live database, or retries if any other writer committed meanwhile.

This is deliberately not a new checkpoint format and does not cache gradients.
"""
from __future__ import annotations

from contextlib import closing
from dataclasses import dataclass
from pathlib import Path
import sqlite3
import tempfile
import time
from typing import Any, Callable

from integration.unified.session import Session


class StaleSnapshot(RuntimeError):
    """Live database changed while staging a turn."""


def ident(name: str) -> str:
    return '"' + name.replace('"', '""') + '"'


@dataclass(frozen=True)
class Table:
    schema: str
    columns: tuple[str, ...]
    primary_key: tuple[str, ...]
    rows: dict[tuple[Any, ...], tuple[Any, ...]]


def table_views(db: sqlite3.Connection) -> dict[str, Table]:
    """Collect base tables with declared primary keys; fail closed on ambiguity."""
    names = db.execute(
        "SELECT name, sql FROM sqlite_master WHERE type='table' "
        "AND name NOT LIKE 'sqlite_%' ORDER BY name"
    ).fetchall()
    result = {}
    for name, schema in names:
        info = db.execute("PRAGMA table_info(" + ident(name) + ")").fetchall()
        columns = tuple(row[1] for row in info)
        keys = tuple(row[1] for row in sorted(info, key=lambda row: row[5]) if row[5])
        if not keys or not columns:
            raise ValueError("C02 cannot safely stage table without PRIMARY KEY: " + name)
        indices = tuple(columns.index(k) for k in keys)
        # A key with NULL is legal in SQLite for non-INTEGER rowid PKs;
        # refuse because it could alias another row during a differential commit.
        rows = {}
        ordering = ("rowid" if "WITHOUT ROWID" not in (schema or "").upper()
                    else ",".join(ident(k) for k in keys))\n        query = "SELECT * FROM " + ident(name) + " ORDER BY " + ordering
        for raw in db.execute(query):
            data = tuple(raw)
            key = tuple(data[i] for i in indices)
            if any(part is None for part in key) or key in rows:
                raise ValueError("Ambiguous C02 SQLite row identity: " + name)
            rows[key] = data
        result[name] = Table(schema, columns, keys, rows)
    return result


@dataclass(frozen=True)
class Action:
    table: str
    kind: str
    key: tuple[Any, ...]
    data: tuple[Any, ...] | None = None


def differences(before: dict[str, Table], after: dict[str, Table]) -> list[Action]:
    if before.keys() != after.keys():
        raise ValueError("C02 schema changed during staging; original Session required")
    out: list[Action] = []
    for name in sorted(before):
        start, end = before[name], after[name]
        if (start.schema, start.columns, start.primary_key) != (
                end.schema, end.columns, end.primary_key):
            raise ValueError("C02 refuses to apply schema migrations: " + name)
        # Deletions then updates then inserts, in deterministic key order.
        for key in start.rows.keys() - end.rows.keys():
            out.append(Action(name, "delete", key))
        for key in start.rows.keys() & end.rows.keys():
            if start.rows[key] != end.rows[key]:
                out.append(Action(name, "update", key, end.rows[key]))
        for key in end.rows.keys() - start.rows.keys():
            out.append(Action(name, "insert", key, end.rows[key]))
    # Inserts follow the after-snapshot's row order within each table:
    # the legacy history endpoint intentionally orders request rows by rowid.
    rank = {"delete": 0, "update": 1, "insert": 2}
    table_index = {name: i for i, name in enumerate(sorted(before))}
    positions = {name: {key: i for i, key in enumerate(after[name].rows)}
                 for name in after}
    out.sort(key=lambda a: (table_index[a.table], rank[a.kind],
                             positions[a.table].get(a.key, -1)))
    return out


def publish(db: sqlite3.Connection, before: dict[str, Table],
            actions: list[Action]) -> None:
    """Called only inside BEGIN IMMEDIATE after checking PRAGMA data_version."""
    for action in actions:
        table = before[action.table]
        columns, pk = table.columns, table.primary_key
        where = " AND ".join(ident(key) + " IS ?" for key in pk)
        quoted_table = ident(action.table)
        if action.kind == "delete":
            cursor = db.execute("DELETE FROM " + quoted_table + " WHERE " + where,
                                action.key)
            if cursor.rowcount != 1:
                raise StaleSnapshot("C02 lost a row during delete")
        elif action.kind == "update":
            mutable = [column for column in columns if column not in pk]
            values = dict(zip(columns, action.data))
            if not mutable:
                raise AssertionError("C02 UPDATE without mutable columns")
            fields = ", ".join(ident(c) + "=?" for c in mutable)
            cursor = db.execute("UPDATE " + quoted_table + " SET " + fields +
                                " WHERE " + where,
                                tuple(values[c] for c in mutable) + action.key)
            if cursor.rowcount != 1:
                raise StaleSnapshot("C02 lost a row during update")
        elif action.kind == "insert":
            db.execute("INSERT INTO " + quoted_table + " (" +
                       ",".join(ident(c) for c in columns) + ") VALUES (" +
                       ",".join("?" for _ in columns) + ")", action.data)
        else:
            raise AssertionError("Unknown C02 delta operation")


class OptimisticSession:
    """One public-facing SQLite state, with opt-in speculative native turns.

    First initialization is delegated to the stable U02 Session constructor.
    No trained state is changed unless the entire staged turn succeeds and
    the original live snapshot still matches the guarded database revision.
    """

    def __init__(self, database: str | Path, readers: Path | None = None,
                 max_retries: int = 3, busy_timeout_ms: int = 20000):
        if not (1 <= max_retries <= 20):
            raise ValueError("max_retries must be between 1 and 20")
        self.database = Path(database).resolve()
        self.readers = readers
        self.max_retries = max_retries
        self.busy_timeout_ms = busy_timeout_ms
        self.before_publish: Callable[[int], None] | None = None  # fault-injection tests
        self.last_metrics: dict[str, Any] = {}
        self.closed = False
        # Bootstrap or U01 migration remains under the authenticated original
        # implementation. Changes to the language identity cannot be invented.
        with Session(self.database, self.readers):
            pass
        self.db = sqlite3.connect(str(self.database), isolation_level=None,
                                  timeout=busy_timeout_ms / 1000)
        self.db.execute("PRAGMA busy_timeout=" + str(busy_timeout_ms))
        self.db.execute("PRAGMA journal_mode=WAL")

    def __enter__(self):
        return self

    def __exit__(self, *_):
        self.close()

    def close(self):
        if not self.closed:
            self.closed = True
            self.db.close()

    def _check_open(self):
        if self.closed:
            raise RuntimeError("C02 session already closed")

    def snapshot(self):
        self._check_open()
        with Session(self.database, self.readers) as session:
            return session.snapshot()

    def history(self):
        self._check_open()
        with Session(self.database, self.readers) as session:
            return session.history()

    def turn(self, request_id: str, prompt: str, payload=None,
             fail_after=None, control=None):
        self._check_open()
        self.last_metrics = {}
        conflicts = 0
        for attempt in range(1, self.max_retries + 1):
            with tempfile.TemporaryDirectory(prefix="bbyq-c02-speculative-") as temp:
                staging = Path(temp) / "candidate.sqlite"
                copy_started = time.perf_counter_ns()
                version_before = self.db.execute("PRAGMA data_version").fetchone()[0]
                with closing(sqlite3.connect(str(staging), isolation_level=None)) as target:
                    self.db.backup(target)
                version_after_copy = self.db.execute("PRAGMA data_version").fetchone()[0]
                if version_after_copy != version_before:
                    conflicts += 1
                    continue
                snapshot_ms = (time.perf_counter_ns() - copy_started) / 1e6
                with closing(sqlite3.connect(str(staging), isolation_level=None)) as stage:
                    before = table_views(stage)
                native_started = time.perf_counter_ns()
                with Session(staging, self.readers) as candidate:
                    result = candidate.turn(request_id, prompt, payload,
                                            fail_after=fail_after, control=control)
                native_ms = (time.perf_counter_ns() - native_started) / 1e6
                with closing(sqlite3.connect(str(staging), isolation_level=None)) as stage:
                    after = table_views(stage)
                actions = differences(before, after)
                if self.before_publish is not None:
                    self.before_publish(attempt)
                commit_started = time.perf_counter_ns()
                self.db.execute("BEGIN IMMEDIATE")
                try:
                    # A competing U02, C01, legacy or C02 connection has
                    # committed since the snapshot: never overwrite its data.
                    if self.db.execute("PRAGMA data_version").fetchone()[0] != version_after_copy:
                        raise StaleSnapshot("Concurrent SQLite writer advanced data_version")
                    publish(self.db, before, actions)
                    self.db.execute("COMMIT")
                except BaseException as exc:
                    self.db.execute("ROLLBACK")
                    if isinstance(exc, StaleSnapshot):
                        conflicts += 1
                        continue
                    raise
                commit_ms = (time.perf_counter_ns() - commit_started) / 1e6
                self.last_metrics = {
                    "attempts": attempt,
                    "conflicts": conflicts,
                    "snapshot_ms": round(snapshot_ms, 3),
                    "native_compute_ms": round(native_ms, 3),
                    "write_lock_ms": round(commit_ms, 3),
                    "published_row_changes": len(actions),
                    "updated_tables": sorted({change.table for change in actions}),
                }
                return result
        raise StaleSnapshot(
            "C02 aborted after bounded concurrency retries without modifying its turn"
        )
