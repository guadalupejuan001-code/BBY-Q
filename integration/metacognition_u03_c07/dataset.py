"""C07 independent synthetic evidence/provenance curriculum.

The authored scenario label does not come from the learned head, and feature
functions cannot access it. Split-specific claim subjects, sources, and
scenario strings are disjoint; the heldout test is instantiated only after
model selection. 'Signatures' are synthetic content digests, NOT real identity
authentication. This evaluates a bounded epistemic task, not world knowledge.
"""
from __future__ import annotations
from dataclasses import dataclass
from hashlib import sha256
import json
import random

LABELS = ("answer", "ask_for_evidence", "report_conflict")
SPLIT_COUNTS = {"train": 540, "validation": 135, "test": 180, "challenge": 180}
SEEDS = {"train": 202611070701, "validation": 202611070702, "test": 202611070703,
         "challenge": 202611070704}
PREDICATES = ("activo", "completo", "operativo")
TRUSTED_PREFIX = ("laboratorio", "registro", "auditor")
DAY = 23000


@dataclass(frozen=True)
class Sample:
    uid: str
    query: dict
    evidence: tuple[dict, ...]
    label: int
    family: str
    scenario_id: str

    def as_dict(self):
        return {
            "uid": self.uid, "query": self.query,
            "evidence": list(self.evidence), "label": self.label,
            "family": self.family, "scenario_id": self.scenario_id,
        }


def _digest(e: dict) -> str:
    # Checks content consistency, not an asymmetric cryptographic signature.
    payload = {key: e[key] for key in
               ("subject", "predicate", "value", "source", "observed_day", "expires_day")}
    return sha256(json.dumps(payload, sort_keys=True,
                             separators=(",", ":")).encode()).hexdigest()


def evidence(subject: str, predicate: str, value: int, source: str, *,
             age=0, ttl=30, attested=True, tamper=False) -> dict:
    if type(value) is not int or value not in (0, 1):
        raise ValueError("C07 requires binary observed proposition")
    row = {
        "subject": subject, "predicate": predicate, "value": value,
        "source": source, "observed_day": DAY-age,
        "expires_day": DAY-age+ttl, "attested": bool(attested),
    }
    row["content_sha256"] = _digest(row)
    if tamper:
        row["content_sha256"] = "00"*32
    return row


def trusted(row: dict, query: dict) -> bool:
    """Synthetic evidence acceptance criteria, not a proof of real truth."""
    if not isinstance(row, dict) or not isinstance(query, dict):
        return False
    if row.get("subject") != query.get("subject") or row.get("predicate") != query.get("predicate"):
        return False
    if row.get("value") not in (0, 1) or type(row.get("value")) is not int:
        return False
    if row.get("source", "").split(":")[0] not in TRUSTED_PREFIX:
        return False
    if row.get("attested") is not True:
        return False
    if row.get("observed_day", DAY+1) > DAY or row.get("expires_day", -1) < DAY:
        return False
    try:
        return row.get("content_sha256") == _digest(row)
    except (KeyError, TypeError, ValueError):
        return False


def independent_target(query: dict, rows: tuple[dict, ...]) -> int:
    """Audit oracle, used only for post-hoc labels/evaluation, never features."""
    reliable_values = {row["value"] for row in rows if trusted(row, query)}
    if len(reliable_values) == 2:
        return 2
    if not reliable_values:
        return 1
    return 0


def _sources(split: str, i: int, count: int = 3) -> list[str]:
    kind = TRUSTED_PREFIX[i % len(TRUSTED_PREFIX)]
    return [f"{kind}:{split}-{i:04d}-{j}" for j in range(count)]


def _make(split: str, i: int, label: int, rng: random.Random) -> Sample:
    subject = f"{split.upper()}_Entidad_{i:04d}_{rng.randint(100,999)}"
    predicate = PREDICATES[(i+len(split))%len(PREDICATES)]
    query = {"subject": subject, "predicate": predicate}
    sources = _sources(split, i, 5)
    positive = (i + (len(split)%3)) % 2
    negative = 1-positive
    rows = []
    # Distinct scenarios are authored independently of feature extraction.
    # Even the same label has varied provenance and decoys to prevent single
    # textual/position shortcuts.
    variation = i % 5
    if label == 0:  # At least one fresh authenticated matching assertion.
        rows.append(evidence(subject,predicate,positive,sources[0],age=variation))
        if variation in (1,4):
            rows.append(evidence(subject,predicate,positive,sources[1],age=variation+1))
        if variation in (2,3):
            rows.append(evidence(subject,predicate,negative,sources[2],attested=False))
    elif label == 1:  # Missing/unsupported/expired evidence => ask.
        if variation == 0:
            pass
        elif variation == 1:
            rows.append(evidence(subject,predicate,positive,sources[0],attested=False))
        elif variation == 2:
            rows.append(evidence(subject,predicate,positive,sources[0],age=90,ttl=30))
        elif variation == 3:
            rows.append(evidence(subject,predicate,positive,"unknown:"+split+str(i)))
        else:
            rows.append(evidence(subject,predicate,positive,sources[0],tamper=True))
        if variation in (2,4):
            rows.append(evidence(subject,predicate,negative,sources[2],attested=False))
    elif label == 2:  # Genuine opposing evidence with verified provenance.
        rows.extend((
            evidence(subject,predicate,positive,sources[0],age=variation),
            evidence(subject,predicate,negative,sources[1],age=variation+1),
        ))
        if variation in (2,4):
            rows.append(evidence(subject,predicate,positive,sources[2],age=2))
    else:
        raise ValueError("Unexpected C07 reference label")
    # Distractors may be fresh/attested, but do not match query.
    if variation in (0,2,4):
        rows.append(evidence(subject+"_otro",predicate,positive,sources[3]))
    if variation in (1,3):
        rows.append(evidence(subject,"otra_propiedad",negative,sources[4]))
    if split == "challenge":
        # Newly reserved *after* the initial calibration audit: extra,
        # authorized BUT irrelevant evidence exercises source/query binding.
        rows.append(evidence(subject+"_ajeno",predicate,negative,
                             f"registro:challenge-extra-{i}"))
        rows.append(evidence(subject,"otro_atributo",positive,
                             f"auditor:challenge-attribute-{i}"))
    rng.shuffle(rows)
    sample = Sample(
        uid=sha256(f"{split}-{i}-{label}".encode()).hexdigest()[:16],
        query=query, evidence=tuple(rows), label=label,
        family=split+"_"+LABELS[label]+"_"+str(variation),
        scenario_id=f"{split}/{label}/{i}",
    )
    if independent_target(query, sample.evidence) != label:
        raise AssertionError("C07 synthetic scenario label violates evidence policy")
    return sample


def split(name: str) -> list[Sample]:
    if name not in SPLIT_COUNTS:
        raise ValueError("Unknown C07 split")
    rng = random.Random(SEEDS[name])
    size = SPLIT_COUNTS[name]
    if size % len(LABELS):
        raise AssertionError("C07 classes must be balanced")
    result = [_make(name, i, label, rng) for label in range(3)
              for i in range(size//3)]
    rng.shuffle(result)
    if len({e.uid for e in result}) != len(result):
        raise AssertionError("C07 repeated a sample UID")
    return result


def verify_disjoint() -> dict:
    sets = {name: split(name) for name in SPLIT_COUNTS}
    seen_subjects = set()
    seen_sources = set()
    seen_cases = set()
    for name, rows in sets.items():
        subjects = {r.query["subject"] for r in rows}
        sources = {e["source"] for r in rows for e in r.evidence}
        scenarios = {r.scenario_id for r in rows}
        if (subjects & seen_subjects or sources & seen_sources or scenarios & seen_cases):
            raise AssertionError("C07 source/query/test leakage")
        if any(sum(r.label == cls for r in rows) != len(rows)//3 for cls in range(3)):
            raise AssertionError("C07 class skew")
        seen_subjects |= subjects
        seen_sources |= sources
        seen_cases |= scenarios
    return {
        "counts": {name: len(rows) for name, rows in sets.items()},
        "subject_source_scenario_disjoint": True,
        "balanced": True, "source_trust": "synthetic allowlist plus content digest",
        "hashes": {
            name: sha256(json.dumps([r.as_dict() for r in rows],
                                    sort_keys=True, ensure_ascii=False).encode()).hexdigest()
            for name, rows in sets.items()
        },
    }


def unfamiliar_cases() -> list[tuple[dict, list[dict]]]:
    """Out-of-domain evidence requires safe abstention; not trained on."""
    return [
        ({"subject":"OOD_001","predicate":"predice_el_futuro"}, [
            evidence("OOD_001","predice_el_futuro",1,"laboratorio:unknown")]),
        ({"subject":"OOD_002","predicate":"operativo"}, [
            evidence("OOD_002","operativo",1,"untrusted:extra")]),
        ({"subject":"OOD_003","predicate":"operativo"}, [
            evidence("OOD_003","operativo",1,"registro:test-unverified",attested=False)]),
        ({"subject":"OOD_004","predicate":"no_autorizado"}, []),
    ]
