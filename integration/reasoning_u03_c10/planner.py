"""BBY Q C10: bounded, deterministic dependency DAG for native XI reasoning.

The original U02 grammar, Zero reasoning, QMemory, VQC, QRL, entity and
QChat remain the ONLY native executors. This is a typed scheduler of
prerequisites, not a replacement symbolic inference engine.
"""
from __future__ import annotations

from dataclasses import dataclass
import re
from typing import Any

SCHEMA="BBYQ-U03-C10-verified-reason-plan-v1"
VALID_NAME=re.compile(r"[A-Za-zÁÉÍÓÚÜÑáéíóúüñ][A-Za-zÁÉÍÓÚÜÑáéíóúüñ0-9 ]{0,48}\Z")


@dataclass(frozen=True)
class Goal:
    """Two original U02 contracts, no freeform host-invented plans."""

    kind: str
    observation: str
    association: str | None = None
    position: int = 3

    def validate(self) -> None:
        if self.kind not in ("prove_alert", "plan_mission"):
            raise ValueError("C10 supports only grounded U02 proof/mission goals")
        if not isinstance(self.observation,str) or not VALID_NAME.fullmatch(self.observation):
            raise ValueError("C10 observation name is not a bounded plain-text name")
        if type(self.position) is not int or not 0<=self.position<=6:
            raise ValueError("C10 mission position must be integer 0..6")
        if self.kind=="prove_alert":
            if self.association is not None:
                raise ValueError("C10 symbolic alert proof has no rule argument")
        else:
            if not isinstance(self.association,str) or not VALID_NAME.fullmatch(self.association):
                raise ValueError("C10 mission requires an explicitly named supervised rule")


def steps(goal:Goal) -> list[dict[str, Any]]:
    goal.validate()
    order=[
        ("audit_sqlite_WAL_C09","verified-u02-memory"),
        ("require_C1_sync","identity"),
        ("require_current_VQC_input","v3"),
    ]
    if goal.kind=="plan_mission":
        order.append(("require_QMemory_supervision","memory"))
    order.extend([
        ("check_untrusted_conflicts","evidence"),
        ("copy_original_checkpoint","sandbox"),
        ("verify_C09_copy_is_same_revision","sandbox"),
        (
            "run_original_XI_C1_Zero_proof" if goal.kind=="prove_alert"
            else "run_original_XI_QMemory_VQC_Entity_QRL_QChat",
            "original-XI",
        ),
        ("reverify_source_unchanged","identity"),
        ("publish_readonly_derivation","provenance"),
    ])
    out=[]
    for index,(name,bank) in enumerate(order):
        out.append({
            "id":name,
            "bank":bank,
            "dependencies":() if index==0 else (order[index-1][0],),
            "may_mutate_original_checkpoint":False,
            "runs_native_XI":bank=="original-XI",
            "execution":"serial",
        })
    return out


def ordered(nodes:list[dict[str,Any]]) -> list[str]:
    """Reject malformed graph, unknown dependencies and cycles."""
    ids=[node["id"] for node in nodes]
    if len(set(ids))!=len(ids):
        raise ValueError("C10 duplicate dependency ID")
    indegree={identifier:0 for identifier in ids}
    successors={identifier:[] for identifier in ids}
    for node in nodes:
        for dep in node["dependencies"]:
            if dep not in indegree:
                raise ValueError("C10 unknown dependency")
            successors[dep].append(node["id"])
            indegree[node["id"]]+=1
    ready=[identifier for identifier in ids if indegree[identifier]==0]
    traversed=[]
    while ready:
        cursor=ready.pop(0)
        traversed.append(cursor)
        for target in successors[cursor]:
            indegree[target]-=1
            if indegree[target]==0:
                ready.append(target)
    if len(traversed)!=len(nodes):
        raise ValueError("C10 cyclic plan forbidden")
    return traversed


def original_native_prompt(goal:Goal) -> str:
    goal.validate()
    if goal.kind=="prove_alert":
        return f"dime si observación {goal.observation} es alerta"
    return f"resuelve {goal.observation} usando la regla {goal.association} desde {goal.position}"
