"""Ten bounded evidence features for native XI C07 metacognitive learning.

Never reads Sample.label, scenario_id, the authored class or a predicted
C06 semantic label. Evidence trust is determined from explicit provenance:
a synthetic source registry, finite TTL and content SHA. This is not real
internet fact checking or learned source authentication.
"""
from __future__ import annotations
import math
from .dataset import trusted, DAY, PREDICATES

FEATURE_COUNT = 10
CLASSES = 3
MODES = ("provenance", "no-provenance", "no-contrast")
SCHEMA = "BBYQ-U03-C07-native-metacognition-v1"


def evidence_features(query: dict, rows, *, mode="provenance") -> tuple[float, ...]:
    if mode not in MODES:
        raise ValueError("Unknown C07 ablation")
    if not isinstance(query, dict) or set(query) != {"subject", "predicate"}:
        raise ValueError("C07 requires explicit subject and predicate")
    if not isinstance(query["subject"], str) or not isinstance(query["predicate"], str):
        raise ValueError("C07 evidence question must be typed text")
    if not isinstance(rows, (list, tuple)) or len(rows) > 24:
        raise ValueError("C07 evidence capacity 0..24")
    seen_pos = seen_neg = unsigned = stale = irrelevant = 0
    matching = 0
    sources = set()
    for row in rows:
        if not isinstance(row, dict):
            raise ValueError("Malformed C07 evidence row")
        is_matching = (
            row.get("subject") == query["subject"]
            and row.get("predicate") == query["predicate"]
        )
        if not is_matching:
            irrelevant += 1
            continue
        matching += 1
        value = row.get("value")
        if mode == "no-provenance":
            # Treat every reported value as if it were evidence. This
            # ablation hides source, date and cryptographic content checks.
            accepted = type(value) is int and value in (0,1)
        else:
            accepted = trusted(row, query)
        if accepted:
            if value == 1:
                seen_pos += 1
            else:
                seen_neg += 1
            sources.add(row.get("source"))
        elif mode != "no-provenance":
            if row.get("expires_day", DAY) < DAY:
                stale += 1
            else:
                unsigned += 1
    # This contrast indicator is computed from source-qualified evidence,
    # not from the authoritative task label or the C05 polarity parser.
    contrast = float(bool(seen_pos and seen_neg))
    if mode == "no-contrast":
        contrast = 0.0
    x = (
        1.0,
        min(seen_pos,2)/2.0,
        min(seen_neg,2)/2.0,
        contrast,
        min(seen_pos+seen_neg,3)/3.0,
        min(unsigned,3)/3.0,
        min(stale,3)/3.0,
        min(irrelevant,3)/3.0,
        float(bool(matching)),
        min(len(sources),3)/3.0,
    )
    if len(x) != FEATURE_COUNT or any(not math.isfinite(v) for v in x):
        raise AssertionError("Malformed C07 feature vector")
    return x


def is_unsupported(query: dict, rows) -> bool:
    """A separate fail-closed guard; not trained/selected on heldout labels."""
    if not isinstance(query, dict) or query.get("predicate") not in PREDICATES:
        return True
    if not isinstance(query.get("subject"), str) or not query["subject"].strip():
        return True
    if not isinstance(rows, (list, tuple)) or len(rows) > 24:
        return True
    return any(not isinstance(item, dict) for item in rows)
