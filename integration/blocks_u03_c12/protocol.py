"""C12 independent native XI multi-block evaluation protocol.

These are fresh synthetic task identities; none repeats C11 teacher labels,
names, rules, seeds or prompts. The original U02 parser and XI are unchanged.
"""
from __future__ import annotations

from hashlib import sha256
import json

from integration.joint_u03_c11.protocol import Heldout, TRAINED_SEEDS, validation as c11_val, heldout_test as c11_test

SCHEMA = "BBYQ-U03-C12-native-cross-block-v1"
MODES = ("frozen", "joint-verified")
OPERATIONS = {
    "C1": "c1_encode_input/c1_next",
    "QMemory": "qm_read",
    "VQC": "vqc_forward",
    "Entity": "entity_infer",
    "QRL": "qrl_step",
    "QChat": "qchat_encode/qchat_next",
}
TRAIN = (
    Heldout("training", "Olmo", "Cauce Dorado", 27120101, position=2, bit=1),
    Heldout("training", "Bambu", "Clave Boreal", 27120102, position=5, bit=1),
)
VALIDATION = (
    Heldout("validation", "Roble", "Trama Gris", 27120211, position=0, bit=0),
    Heldout("validation", "Puma", "Cima Clara", 27120212, position=6, bit=1),
    Heldout("validation", "Coral", "Ruta Nueva", 27120213, position=4, bit=0),
    Heldout("validation", "Duna", "Marea Alta", 27120214, position=1, bit=1),
)
TEST = (
    Heldout("test", "Sauce", "Punto Libre", 27120321, position=6, bit=1),
    Heldout("test", "Cobre", "Valle Seco", 27120322, position=0, bit=0),
    Heldout("test", "Tigre", "Delta Sur", 27120323, position=5, bit=1),
    Heldout("test", "Nieve", "Linea Roja", 27120324, position=1, bit=0),
    Heldout("test", "Lago", "Corte Verde", 27120325, position=3, bit=1),
    Heldout("test", "Llama", "Plaza Azul", 27120326, position=2, bit=0),
)
LOAD = (
    Heldout("load", "Azul", "Giro Norte", 27120431, position=0, bit=0),
    Heldout("load", "Sierra", "Paso Claro", 27120432, position=1, bit=1),
    Heldout("load", "Nopal", "Piedra Blanca", 27120433, position=2, bit=0),
    Heldout("load", "Rayo", "Luz Serena", 27120434, position=3, bit=1),
    Heldout("load", "Alfil", "Arco Verde", 27120435, position=4, bit=0),
    Heldout("load", "Vapor", "Nube Negra", 27120436, position=6, bit=1),
)
# Revisit A after B in ONE native U02 session: same task, same explicit
# supervised memory bit. This measures context interference; not new learning.
REVISIT = (TEST[0], TEST[1], TEST[0])


def heldout_test():
    """Call only after freezing the validation-only promotion decision."""
    return TEST


def separate() -> dict:
    splits = {"training": TRAIN, "validation": VALIDATION, "test": TEST, "load": LOAD}
    all_cases = [x for cases in splits.values() for x in cases]
    earlier = [x for x in (*c11_val(), *c11_test())]
    names = {s.lower() for row in earlier for s in (row.name, row.rule)} | {"nara", "faro azul"}
    seeds = {x.seed for x in earlier} | TRAINED_SEEDS
    tokens = set()
    prompts = set()
    for case in all_cases:
        assert case.position in range(7) and case.bit in (0, 1)
        assert case.seed not in seeds, "C12 reused an earlier teacher seed"
        assert case.name.lower() not in names and case.rule.lower() not in names, "C12 reused a C11 identity"
        assert case.name.lower() not in tokens and case.rule.lower() not in tokens, "C12 duplicate task identity"
        assert case.prompt() not in prompts, "C12 duplicated a prompt"
        tokens.update((case.name.lower(), case.rule.lower()))
        seeds.add(case.seed)
        prompts.add(case.prompt())
    assert len(TRAIN) == 2 and len(VALIDATION) == 4
    assert len(TEST) == 6 and len(LOAD) == 6
    assert {r.bit for r in (*VALIDATION, *TEST)} == {0, 1}
    assert {r.position for r in (*VALIDATION, *TEST)} == set(range(7))
    assert REVISIT[0] == REVISIT[2] and REVISIT[0] != REVISIT[1]
    return {
        "c11_names_seeds_prompts_disjoint": True,
        "all_cross_split_seeds_and_identities_disjoint": True,
        "evaluation_contains_both_rules_and_seven_positions": True,
        "counts": {name: len(rows) for name, rows in splits.items()},
        "sha256": {name: sha256(json.dumps([r.as_dict() for r in rows],sort_keys=True).encode()).hexdigest()
                   for name, rows in splits.items()},
    }
