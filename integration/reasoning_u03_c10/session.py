"""C10 opt-in native XI evidence planner over C09, original turns unchanged."""
from __future__ import annotations

from integration.memory_u03_c09.session import MemorySession
from .planner import Goal
from .engine import Reasoner


class ReasoningSession(MemorySession):
    """BBY Q authority remains U02 session / one SQLite database.

    w4U/QdU orchestration is not replaced or bypassed. This adapter exposes
    a typed read-only experiment whose native execution lives only inside a
    temporary U02 clone. Original turn method remains exactly inherited.
    """

    def __init__(self,database,readers=None,*,parallel_hash_workers=4,memo=None):
        super().__init__(database,readers=readers,
                         parallel_hash_workers=parallel_hash_workers,memo=memo)
        self.reasoning=Reasoner(self)
        self.last_reasoning_plan=None

    def prove_alert(self, observation: str, *, overlay=()) -> dict:
        result=self.reasoning.plan(
            Goal("prove_alert",observation),overlay=overlay)
        self.last_reasoning_plan=result
        return result

    def plan_mission(self, observation: str, association: str,
                     *, position: int=3, overlay=()) -> dict:
        result=self.reasoning.plan(
            Goal("plan_mission",observation,association,position),overlay=overlay)
        self.last_reasoning_plan=result
        return result
