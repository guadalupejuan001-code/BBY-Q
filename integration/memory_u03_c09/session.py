"""U03 C09: existing BBY Q U02 memory is the ONE authority.

Adds an optional verified semantic index to a C04 session. The original
turn() bytecode/SQL persistence and every XI/C06/C07/C08 training bank are
unchanged. No new database tables or checkpoint format.
"""
from integration.planner_u03_c04.runtime import PlannedSession
from .view import UnifiedMemoryView


class MemorySession(PlannedSession):
    def __init__(self,database,readers=None,*,parallel_hash_workers=4,memo=None):
        super().__init__(database,readers=readers,
                         parallel_hash_workers=parallel_hash_workers,memo=memo)
        self.memory = UnifiedMemoryView(self)

    def inspect_memory(self,subject=None):
        return self.memory.snapshot(subject)

    def compare_memory(self,subject,*,predicate="valor",overlay=()):
        return self.memory.reconcile(subject,predicate=predicate,overlay=overlay)
