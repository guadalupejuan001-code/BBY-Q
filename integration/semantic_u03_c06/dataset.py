"""C06 independently labeled, split-disjoint compositional evaluation curriculum.

The label comes from held-out template authoring, NOT from the C05 semantic
sidecar or native interpreter. New entities and entire phrasings are disjoint
between train/validation/test. Test examples are only opened after model
selection from validation results.
"""
from __future__ import annotations

import hashlib
import json
import random
from dataclasses import dataclass

# Class IDs are a supervised task, not user-facing XI contract IDs.
LABELS = ("prohibit_action", "exclude_topic", "affirm_action")
TEMPLATES = {
    "train": (
        ("no definas {a}", 0), ("nunca expliques {a}", 0),
        ("no me expliques {a}", 0), ("no quiero que definas {a}", 0),
        ("no resuelvas {a}", 0), ("nunca recuerdes {a}", 0),
        ("define {a} no {b}", 1), ("explica {a} no {b}", 1),
        ("define {a} y no {b}", 1), ("explica {a} pero no {b}", 1),
        ("guarda {a} no {b}", 1), ("recuerda {a} y no {b}", 1),
        ("define {a}", 2), ("explica {a}", 2),
        ("guarda {a}", 2), ("recuerda {a}", 2),
        ("resuelve {a}", 2), ("lee {a}", 2),
    ),
    "validation": (
        ("por favor no definas {a}", 0),
        ("jamás me expliques {a}", 0),
        ("no quiero que resuelvas {a}", 0),
        ("guarda {a} y no {b}", 1),
        ("explica {a}, no {b}", 1),
        ("resuelve {a} no {b}", 1),
        ("por favor define {a}", 2),
        ("lee la regla {a}", 2),
        ("por favor recuerda {a}", 2),
    ),
    "test": (
        ("no me definas {a}", 0),
        ("por favor nunca expliques {a}", 0),
        ("no quiero que recuerdes {a}", 0),
        ("define {a}, pero no {b}", 1),
        ("recuerda {a} no {b}", 1),
        ("resuelve {a} y no {b}", 1),
        ("por favor explica {a}", 2),
        ("recuerda la regla {a}", 2),
        ("muestra el estado de {a}", 2),
    ),
}
COUNT = {"train": 360, "validation": 90, "test": 120}
SEEDS = {"train": 202611070601, "validation": 202611070602, "test": 202611070603}
SYLLABLES = ("bra", "tri", "xel", "nor", "via", "qui", "zen", "mal",
             "ila", "oax", "fer", "lum", "vex", "pra", "sol", "qui")


@dataclass(frozen=True)
class Example:
    uid: str
    prompt: str
    label: int
    template: str
    a: str
    b: str

    def as_dict(self):
        return {
            "uid": self.uid, "prompt": self.prompt, "label": self.label,
            "template": self.template, "a": self.a, "b": self.b,
        }


def split(name: str) -> list[Example]:
    if name not in TEMPLATES:
        raise ValueError("C06 unknown corpus split")
    rng = random.Random(SEEDS[name])
    count = COUNT[name]
    templates = TEMPLATES[name]
    by_class = {
        klass: [f for f, label in templates if label == klass]
        for klass in range(3)
    }
    if count % 3:
        raise AssertionError("Class balancing required")
    rows = []
    for label in range(3):
        for i in range(count // 3):
            # An explicit split prefix and disjoint randomized tokens ensure
            # no identity shared between splits, including previous C1 vocab.
            a = f"{name[:2].upper()}_{rng.choice(SYLLABLES)}{rng.choice(SYLLABLES)}{i:04d}"
            b = f"{name[:2].upper()}_{rng.choice(SYLLABLES)}{rng.choice(SYLLABLES)}{i + 1000:04d}"
            template = by_class[label][i % len(by_class[label])]
            prompt = template.format(a=a, b=b)
            uid = hashlib.sha256(f"{name}:{label}:{i}:{prompt}".encode()).hexdigest()[:16]
            rows.append(Example(uid, prompt, label, template, a, b))
    rng.shuffle(rows)
    return rows


def verify_disjoint() -> dict:
    groups = {k: split(k) for k in TEMPLATES}
    seen_templates, seen_entities, seen_prompts = set(), set(), set()
    for name, rows in groups.items():
        templates = set(TEMPLATES[name])
        names = {v for row in rows for v in (row.a, row.b)}
        prompts = {row.prompt for row in rows}
        if seen_templates & templates or seen_entities & names or seen_prompts & prompts:
            raise AssertionError("C06 split leaked a template, entity or prompt")
        if len(prompts) != len(rows):
            raise AssertionError("C06 duplicate example")
        if [sum(e.label == i for e in rows) for i in range(3)] != [len(rows)//3]*3:
            raise AssertionError("C06 class imbalance")
        seen_templates |= templates
        seen_entities |= names
        seen_prompts |= prompts
    return {
        "counts": {name: len(rows) for name, rows in groups.items()},
        "template_counts": {name: len(TEMPLATES[name]) for name in TEMPLATES},
        "disjoint_templates": True, "disjoint_entities": True,
        "disjoint_prompts": True,
        "label_source": "dataset template metadata only; not C05 features",
        "corpus_sha256": {
            name: hashlib.sha256(json.dumps(
                [e.as_dict() for e in rows], sort_keys=True,
                ensure_ascii=False).encode()).hexdigest()
            for name, rows in groups.items()
        },
    }
