"""C08 newly authored unlabeled acquisition pool and split-disjoint evaluation.

The old C07 CHALLENGE labels are NEVER read or used for C08 training.
Subjects, sources and scenarios are new for each partition. The acquisition
pool does not contain target labels: a synthetic verifier supplies them
ONLY after a case is selected. No real-life trust is claimed by the
content-hash/issuer allowlist toy policy.
"""
from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
import json
import random

from integration.metacognition_u03_c07.dataset import (
    DAY, LABELS, evidence, independent_target, trusted,
)

SIZES = {"pool": 360, "validation": 135, "test": 180}
SEEDS = {"pool": 202611080801, "validation": 202611080802, "test": 202611080803}
PREDICATES = ("activo", "completo", "operativo")


@dataclass(frozen=True)
class Unlabeled:
    uid: str
    query: dict
    evidence: tuple[dict, ...]
    partition: str

    def as_dict(self):
        return {"uid": self.uid, "query": self.query, "evidence": list(self.evidence)}


@dataclass(frozen=True)
class Labeled:
    uid: str
    query: dict
    evidence: tuple[dict, ...]
    label: int
    partition: str


def _new_scenario(partition: str, index: int, category: int,
                  rng: random.Random) -> tuple[dict, tuple[dict, ...]]:
    # Deterministic IDs and source strings prevent literal memorization and
    # ensure no C07 or C08 other-partition identity is shared.
    subject = f"C08{partition.upper()}_N{index:04d}_{rng.randrange(10000,99999)}"
    predicate = PREDICATES[(index + len(partition)) % len(PREDICATES)]
    query = {"subject": subject, "predicate": predicate}
    sources = [
        f"{prefix}:c08-{partition}-{index:04d}-{i}"
        for i, prefix in enumerate(("laboratorio", "registro", "auditor", "registro", "auditor"))
    ]
    positive = index % 2
    rows = []
    mode = index % 6
    if category == 0:
        rows.append(evidence(subject, predicate, positive, sources[0], age=index%5))
        if mode in (2,5):
            rows.append(evidence(subject, predicate, positive, sources[1], age=index%3))
        if mode == 3:
            rows.append(evidence(subject, predicate, 1-positive, sources[2], attested=False))
    elif category == 1:
        if mode == 0:
            pass
        elif mode == 1:
            rows.append(evidence(subject, predicate, positive, sources[0], attested=False))
        elif mode == 2:
            rows.append(evidence(subject, predicate, positive, sources[0], age=91, ttl=30))
        elif mode == 3:
            rows.append(evidence(subject, predicate, positive, "anonymous:"+partition+str(index)))
        elif mode == 4:
            rows.append(evidence(subject, predicate, positive, sources[0], tamper=True))
        else:
            rows.append(evidence(subject, predicate, positive, sources[1], age=90, ttl=50))
    elif category == 2:
        rows.extend((
            evidence(subject, predicate, positive, sources[0], age=index%4),
            evidence(subject, predicate, 1-positive, sources[1], age=index%3),
        ))
        if mode in (2,5):
            rows.append(evidence(subject, predicate, positive, sources[2]))
    else:
        raise ValueError("C08 invalid case class")

    # The new acquisition domain contains signed/fresh but *irrelevant*
    # observations. They must not interfere with an applicable fact.
    distractors = 1 + (index % 3)
    for i in range(distractors):
        other_source=f"auditor:c08-{partition}-{index:04d}-noise-{i}"
        if i % 2:
            row = evidence(subject, predicate+"_ajeno", 1-positive, other_source)
        else:
            row = evidence(subject+"_ajeno", predicate, 1-positive, other_source)
        rows.append(row)
    if mode in (3,5):
        rows.append(evidence(subject, predicate, 1-positive, sources[4], attested=False))
    rng.shuffle(rows)
    result = tuple(rows)
    if independent_target(query, result) != category:
        raise AssertionError("C08 synthetic label contradicts declared evidence policy")
    return query, result


def _build(partition: str) -> list[tuple[Unlabeled, int]]:
    if partition not in SIZES:
        raise ValueError("C08 unknown partition")
    n = SIZES[partition]
    if n % len(LABELS):
        raise AssertionError("C08 requires balanced labels")
    rng = random.Random(SEEDS[partition])
    entries = []
    for label in range(len(LABELS)):
        for index in range(n // len(LABELS)):
            query, rows = _new_scenario(partition, index, label, rng)
            uid = sha256(
                f"C08:{partition}:{index}:{label}:{query['subject']}".encode()
            ).hexdigest()[:20]
            entries.append((Unlabeled(uid, query, rows, partition), label))
    rng.shuffle(entries)
    return entries


def acquire_pool() -> list[Unlabeled]:
    # Discard the reference class before exposing any pool candidates.
    return [example for example, _ in _build("pool")]


def validation() -> list[Labeled]:
    return [Labeled(example.uid, example.query, example.evidence, label, "validation")
            for example, label in _build("validation")]


def test_reserved() -> list[Labeled]:
    """ONLY invoke after all native checkpoints/thresholds are frozen."""
    return [Labeled(example.uid, example.query, example.evidence, label, "test")
            for example, label in _build("test")]


def synthetic_teacher_confirm(case: Unlabeled) -> dict:
    """Explicit educational source verification only AFTER acquisition.

    Uses synthetic closed-world evidence policy, not a real-world oracle.
    The source digests must be internally consistent; otherwise the
    decision is 'ask_for_evidence', not an invented factual answer.
    """
    if case.partition != "pool":
        raise ValueError("C08 training receipt may only confirm selected pool cases")
    target = independent_target(case.query, case.evidence)
    digest = sha256(json.dumps(case.as_dict(), ensure_ascii=False,
                               sort_keys=True).encode()).hexdigest()
    return {
        "uid": case.uid, "label": target, "verified_scenario_sha256": digest,
        "verifier": "synthetic closed-world C07 evidence policy",
        "real_signature_checked": False,
    }


def check_separation(pool: list[Unlabeled], val: list[Labeled],
                     test: list[Labeled]) -> dict:
    groups = {"pool": pool, "validation": val, "test": test}
    all_names = set()
    all_sources = set()
    all_uids = set()
    sha = {}
    for name, cases in groups.items():
        if len(cases) != SIZES[name]:
            raise AssertionError("C08 split count mismatch")
        names = {row.query["subject"] for row in cases}
        sources = {e["source"] for row in cases for e in row.evidence}
        uids = {row.uid for row in cases}
        if names & all_names or sources & all_sources or uids & all_uids:
            raise AssertionError("C08 overlapping evaluation subjects/sources")
        all_names |= names
        all_sources |= sources
        all_uids |= uids
        sha[name] = sha256(json.dumps(
            [row.as_dict() if isinstance(row, Unlabeled) else {
                "uid": row.uid, "query": row.query, "evidence": list(row.evidence),
                "label": row.label,
            } for row in cases], ensure_ascii=False,
            sort_keys=True).encode()).hexdigest()
    return {
        "counts": dict(SIZES), "disjoint_queries_sources_uids": True,
        "classes_balanced": all(
            sum(c.label == label for c in val) == len(val)//3 and
            sum(c.label == label for c in test) == len(test)//3
            for label in range(3)
        ),
        "source_authentication": "only synthetic content hash and allowlist",
        "sha256": sha,
    }
