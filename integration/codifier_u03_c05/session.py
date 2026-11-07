"""Opt-in C05 semantic frame attached to the U03/C04 native entity.

Original XI inference, training, SQLite persistence and output are not changed.
C05 stores the analysis on this Python session only for inspection, evaluation
and the future C06 learned-semantic training stage. It does not pretend that
the frozen QChat model has already learned the new annotations.
"""
from __future__ import annotations

import json

from integration.planner_u03_c04.runtime import PlannedSession
from integration.unified.common import digest
from .semantic import analyze, wire_encode


class SemanticSession(PlannedSession):
    def __init__(self, database, readers=None, *, parallel_hash_workers=4, memo=None):
        super().__init__(database, readers=readers,
                         parallel_hash_workers=parallel_hash_workers, memo=memo)
        self.last_semantic = None
        self.last_semantic_wire = None

    def _previous_text(self) -> str:
        row = self.db.execute("SELECT metadata,sha FROM unified_state WHERE id=1").fetchone()
        if row is None or digest(row[0]) != row[1]:
            raise ValueError("Corrupt unified metadata: C05 refuses semantic context")
        previous = json.loads(row[0]).get("previous", "")
        if not previous:
            old = self.db.execute("SELECT metadata,metadata_sha FROM state WHERE id=1").fetchone()
            if old is None or digest(old[0]) != old[1]:
                raise ValueError("Corrupt compatible language context")
            previous = json.loads(old[0]).get("previous", "")
        return previous if isinstance(previous, str) else ""

    def turn(self, request_id, prompt, payload=None, fail_after=None, control=None):
        self.last_semantic = None
        self.last_semantic_wire = None
        if not isinstance(prompt, str):
            return super().turn(request_id, prompt, payload=payload,
                                fail_after=fail_after, control=control)
        # Candidate semantics are extracted and validated BEFORE native
        # inference, but never injected into U02 banks or routing decisions.
        # This isolates the C05 representation until C06 trains a native head.
        previous = self._previous_text()
        frame = analyze(prompt, previous)
        packet = wire_encode(frame)
        result = super().turn(request_id, prompt, payload=payload,
                              fail_after=fail_after, control=control)
        self.last_semantic = frame
        self.last_semantic_wire = packet
        return result
