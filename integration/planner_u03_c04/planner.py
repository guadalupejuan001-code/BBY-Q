"""Deterministic dependency/resource plan for the frozen U02 contracts.

The plan describes and audits the actual native sequence. It does not
reinterpret the learned XI intent, reorder stateful calls, or skip any
native circuits. Parallel execution is limited to independently verified
immutable SHA-256 digests; quantum state is single-owner.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from integration.unified.contracts import RULES
from integration.unified.common import C1Tools


# Each sequence explicitly preserves the order in the frozen U02 executable.
# These are conservative *potential* dependencies; the original XI code
# decides which branches are actually reached.
STEPS = {
    "remember": (("memory.write", "memory"),),
    "recall": (("memory.read", "memory"),),
    "observe": (("vqc.sample-and-forward", "v3"), ("language.project", "language")),
    "plan": (("qrl.policy", "v3"), ("qchat.voice", "voice"), ("coordinator.verify", "entity")),
    "mission": (
        ("memory.read", "memory"), ("vqc.sample-and-forward", "v3"),
        ("language.project", "language"), ("coordinator.infer", "entity"),
        ("qrl.policy", "v3"), ("coordinator.decide", "entity"),
        ("qchat.voice", "voice"), ("coordinator.verify", "entity"),
    ),
    "feedback": (
        ("coordinator.feedback", "entity"), ("vqc.supervised-update", "v3"),
        ("qrl.credit", "v3"), ("memory.rehearsal", "memory"),
        ("qchat.train", "voice"), ("language.router-train", "router"),
    ),
    "explain": (("task.read", "sqlite"),),
    "status": (("metadata.read", "sqlite"),),
    "cancel": (("metadata.no-write", "sqlite"),),
}


@dataclass(frozen=True)
class Plan:
    route: str
    actions: tuple[str, ...]
    nodes: tuple[tuple[str, str], ...]
    edges: tuple[tuple[str, str], ...]
    banks: tuple[str, ...]
    stateful_native_parallelism: bool

    def as_dict(self) -> dict[str, Any]:
        return {
            "route": self.route,
            "actions": list(self.actions),
            "nodes": [{"id": identifier, "bank": bank} for identifier, bank in self.nodes],
            "edges": [[left, right] for left, right in self.edges],
            "potential_banks": list(self.banks),
            "stateful_native_parallelism": self.stateful_native_parallelism,
            "parallelizable_immutable_bank_hashes": True,
            "runtime_guarantee": "U02 order/branches and original XI runtime unchanged",
        }


def make_plan(parsed: dict | None) -> Plan:
    if parsed is None:
        return Plan("unmatched-text-or-refusal", (), (), (), (), False)
    domain = parsed.get("domain")
    index = parsed.get("rule")
    if not isinstance(index, int) or index < 1:
        raise ValueError("Malformed frozen rule identifier")
    if domain == "quantum":
        if index > len(RULES):
            raise ValueError("Quantum contract index out of range")
        operations = tuple(action[0] for action in RULES[index - 1].actions)
    elif domain == "language":
        if index > len(C1Tools.RULES):
            raise ValueError("Language contract index out of range")
        operations = tuple(action[0] for action in C1Tools.RULES[index - 1].actions)
    else:
        raise ValueError("Unsupported parsed domain")

    nodes = []
    edges = []
    banks = set()
    previous = None
    for i, operation in enumerate(operations):
        if domain == "language":
            # Language tool semantics are still entirely executed by XI.
            # A read of derived VQC facts can trigger conditional refresh.
            steps = ((("language." + operation), "language"),)
        else:
            if operation not in STEPS:
                raise ValueError("Unregistered native operation: " + operation)
            steps = STEPS[operation]
        for j, (label, bank) in enumerate(steps):
            identifier = f"{i}.{j}.{label}"
            nodes.append((identifier, bank))
            if previous is not None:
                edges.append((previous, identifier))
            previous = identifier
            if bank in ("v3", "memory", "voice", "entity"):
                banks.add(bank)
        if domain == "language" and operation in ("query", "lookup", "route"):
            # Conditional read of VQC facts. Opening v3 is justified only if
            # U02 refresh_projections actually examines a stored observation.
            identifier = f"{i}.conditional.vqc-derived-refresh"
            nodes.append((identifier, "v3"))
            edges.append((previous, identifier))
            previous = identifier
            banks.add("v3")
    return Plan(
        domain, operations, tuple(nodes), tuple(edges), tuple(sorted(banks)), False,
    )


def topological_order(plan: Plan) -> list[str]:
    """Explicit validation of acyclic dependencies, no dynamic native dispatch."""
    node_ids = [n for n, _ in plan.nodes]
    indegree = {node: 0 for node in node_ids}
    outgoing = {node: [] for node in node_ids}
    for a, b in plan.edges:
        if a not in indegree or b not in indegree:
            raise ValueError("Unknown dependency in plan")
        outgoing[a].append(b)
        indegree[b] += 1
    ready = [node for node in node_ids if indegree[node] == 0]
    ordered = []
    while ready:
        current = ready.pop(0)
        ordered.append(current)
        for target in outgoing[current]:
            indegree[target] -= 1
            if indegree[target] == 0:
                ready.append(target)
    if len(ordered) != len(node_ids):
        raise ValueError("Cyclic native plan")
    return ordered
