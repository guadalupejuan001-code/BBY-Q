"""Durable authority backed by REVERSE-PC's *actual* XI/InverseMemory CLI.

BBY Q stores one canonical JSON byte sequence at addresses in InverseMemory.
The world state and learned hypotheses are not duplicated in an SQLite sidecar.
REVERSE-PC owns RVPC2, transactional execution, rollback, and atomic rename.
"""
from __future__ import annotations

from contextlib import contextmanager
import fcntl
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
from typing import Callable

from .model import validate_entity
from .compact import encode as compact_encode, decode as compact_decode

BASE_ADDRESS = 1000000000000000
MAX_PAYLOAD = 24_000  # Under InverseMemory's 65,536-byte projection/override limits.
HEADER_LEN = 4
COMPACT_FLAG = 1 << 31


class NativeStore:
    def __init__(self, state_path: str | Path, runtime: str | None = None):
        self.state_path = Path(state_path).expanduser().resolve()
        self.runtime = runtime or os.environ.get("BBYQ_REVERSE_PC") or shutil.which("reverse_pc")
        if not self.runtime:
            raise RuntimeError("REVERSE-PC binary required: --reverse-pc /path/to/reverse_pc")

    @contextmanager
    def _lock(self):
        self.state_path.parent.mkdir(parents=True, exist_ok=True)
        # The .lock file is coordination only, never a second copy of state.
        with open(str(self.state_path) + ".lock", "a+b") as stream:
            fcntl.flock(stream.fileno(), fcntl.LOCK_EX)
            try:
                yield
            finally:
                fcntl.flock(stream.fileno(), fcntl.LOCK_UN)

    def _native(self, *args: str) -> str:
        p = subprocess.run([str(self.runtime), *map(str, args)],
                           capture_output=True, text=True, check=False, timeout=90)
        if p.returncode != 0:
            raise RuntimeError(f"REVERSE-PC rejected transaction: {p.stderr.strip()}")
        return p.stdout

    def _run(self, program: str, readonly: bool) -> list[dict]:
        if not self.state_path.is_file():
            raise FileNotFoundError(self.state_path)
        with tempfile.TemporaryDirectory(prefix="bbyq-xi-") as directory:
            instruction = Path(directory) / "commands.xi"
            instruction.write_text(program, encoding="ascii")
            destination = Path(directory) / "discarded.rvp" if readonly else self.state_path
            raw = self._native("run", str(instruction), str(self.state_path), str(destination))
            return [json.loads(line) for line in raw.splitlines() if line.strip()]

    def _materialize(self, count: int) -> bytes:
        records = self._run(f"mem_materialize {BASE_ADDRESS} {count}\n", readonly=True)
        if len(records) != 1 or records[0].get("type") != "memory_materialization":
            raise RuntimeError("Unexpected REVERSE-PC materialization response")
        data = bytes.fromhex(records[0]["hex"])
        if len(data) != count:
            raise RuntimeError("Truncated InverseMemory response")
        return data

    def _load_unlocked(self):
        header = self._materialize(HEADER_LEN)
        length_and_flags = int.from_bytes(header, "little")
        size = length_and_flags & ~COMPACT_FLAG
        if size == 0:
            return None, header
        if size > MAX_PAYLOAD:
            raise ValueError("BBY Q state length exceeds safety budget")
        raw = self._materialize(HEADER_LEN + size)
        if raw[:HEADER_LEN] != header:
            raise ValueError("Concurrent or damaged BBY Q snapshot")
        data = raw[HEADER_LEN:]
        if length_and_flags & COMPACT_FLAG:
            data = compact_decode(data, MAX_PAYLOAD)
        entity = json.loads(data.decode("utf-8"))
        validate_entity(entity)
        return entity, raw

    @staticmethod
    def _encode(entity: dict) -> bytes:
        validate_entity(entity)
        payload = json.dumps(entity, separators=(",", ":"), sort_keys=True,
                             allow_nan=False, ensure_ascii=True).encode("utf-8")
        if len(payload) > MAX_PAYLOAD:
            raise ValueError("BBY Q state exceeds 24,000-byte experimental limit")
        compact = compact_encode(payload)
        if len(compact) < len(payload):
            return (len(compact) | COMPACT_FLAG).to_bytes(HEADER_LEN, 'little') + compact
        return len(payload).to_bytes(HEADER_LEN, "little") + payload

    def _write_unlocked(self, entity: dict, old: bytes) -> None:
        new = self._encode(entity)
        # Byte deltas: InverseMemory stores only exceptions to its global zero rule.
        # Zero old tail bytes so shortening the encoding also releases overrides.
        commands = [f"mem_store {BASE_ADDRESS+i} {new[i] if i < len(new) else 0}"
                    for i in range(max(len(new), len(old)))
                    if (new[i] if i < len(new) else 0) != (old[i] if i < len(old) else 0)]
        if commands:
            self._run("\n".join(commands) + "\n", readonly=False)

    def initialize(self, entity: dict) -> None:
        """Atomically publish the first snapshot, never an incomplete birth.

        Failed validation, XI transactions, or native process errors leave no
        user-visible .rvp at all. Hard-link publication rejects overwrites,
        including writers that do not participate in the advisory lock.
        """
        with self._lock():
            if self.state_path.exists():
                raise FileExistsError("Refusing to replace an existing BBY Q entity")
            with tempfile.TemporaryDirectory(prefix='.bbyq-birth-',
                                             dir=self.state_path.parent) as directory:
                staged = NativeStore(Path(directory) / 'birth.rvp', self.runtime)
                staged._native('init', str(staged.state_path))
                staged._write_unlocked(entity, b"\x00" * HEADER_LEN)
                loaded, _ = staged._load_unlocked()
                if loaded != entity:
                    raise RuntimeError('Initial state did not survive REVERSE-PC restoration')
                os.link(staged.state_path, self.state_path)

    def read(self) -> dict:
        with self._lock():
            entity, _ = self._load_unlocked()
            if entity is None:
                raise ValueError("Uninitialized BBY Q state")
            return entity

    def transact(self, change: Callable[[dict], object]) -> tuple[dict, object]:
        with self._lock():
            entity, old = self._load_unlocked()
            if entity is None:
                raise ValueError("Uninitialized BBY Q state")
            result = change(entity)
            self._write_unlocked(entity, old)
            return entity, result

    def stats(self) -> dict:
        with self._lock():
            info = self._run("mem_stats\nstats\n", readonly=True)
            return {"native": info, "rvpc2_bytes": self.state_path.stat().st_size}

    def execute_probe(self, xi: str) -> list[dict]:
        """Read-only/failed-contract probes for tests; no persistent commit."""
        with self._lock():
            return self._run(xi, readonly=True)
