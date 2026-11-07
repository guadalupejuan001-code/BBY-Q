"""C06 label-free semantic and surface control features.

NO class labels or C05 inferred negation kind/polarity enter features.
Only literal token spans, relative distances and action positions are used.
The comparison model receives the same capacity but without positional
information; both models train with native XI SGD/perceptron.
"""
from __future__ import annotations

import math
from integration.codifier_u03_c05.semantic import analyze

FEATURES = 8
CLASSES = 3
HEAD_SCHEMA = "BBYQ-U03-C06-ordered-semantic-v1"

def features(text: str, *, mode: str = "semantic") -> tuple[float, ...]:
    if mode not in ("semantic", "bag", "no-order"):
        raise ValueError("C06 unknown feature ablation")
    frame = analyze(text)
    tokens = frame["tokens"]
    keys = [t["key"] for t in tokens]
    events = frame["events"]
    # Direct *positions* from C05 byte/span-aligned event transport.
    # Intentionally do not read event['polarity'], negation['kind'],
    # candidate roles or any supervised label to avoid target leakage.
    verbs = [e["verb_token"] for e in events]
    neg = [n["token"] for n in frame["negations"] if n["operator"] in (
        "no", "nunca", "jamás", "jamas"
    )]
    neg_before = float(any(n < v for n in neg for v in verbs))
    neg_after = float(any(n > v for n in neg for v in verbs))
    # A secondary structural feature: direct negation with a clause's
    # action no more than five tokens later, not an inferred C05 label.
    near_action = float(any(0 < v - n <= 5 for n in neg for v in verbs))
    length = min(len(tokens), 24)/24.0
    has_connector = float(any(k in ("y", "pero", "aunque") for k in keys))
    count_actions = min(len(events), 2)/2.0
    if mode == "semantic":
        x = (1., float(bool(verbs)), float(bool(neg)),
             neg_before, neg_after, near_action, count_actions, length)
    elif mode == "bag":
        # Surface, non-positional control; no C05 verb/negation spans.
        x = (1., float(any(k in (
            "define", "definas", "explica", "expliques", "guarda",
            "recuerda", "resuelve", "resuelvas", "muestra", "lee") for k in keys)),
             float(any(k in ("no", "nunca", "jamás", "jamas") for k in keys)),
             has_connector, float(any(k == "que" for k in keys)),
             float(any(k == "por" for k in keys)),
             float(any(k in ("la", "el") for k in keys)),
             length)
    else:
        # Controlled positional ablation: retain C05 number of verbs and
        # negation presence, erase their relative order and binding.
        x = (1., float(bool(verbs)), float(bool(neg)),
             0., 0., 0., count_actions, length)
    assert len(x) == FEATURES and all(math.isfinite(v) for v in x)
    return x
