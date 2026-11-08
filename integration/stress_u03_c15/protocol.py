"""Predeclared C15 XI/SQLite-WAL stress fixtures and non-promotion gates.

All names, rules, seeds and prompts differ from C11-C14 evaluation, except
that the ORIGINAL C12 training corpus remains the already-qualified training
protocol for the explicitly unpromoted joint arm.
"""
from __future__ import annotations
from hashlib import sha256
import json

from integration.joint_u03_c11.protocol import Heldout, validation as c11_val, heldout_test as c11_test, TRAINED_SEEDS
from integration.blocks_u03_c12.protocol import TRAIN as c12_train, VALIDATION as c12_val, TEST as c12_test, LOAD as c12_load
from integration.optimize_u03_c13.campaign import CASES as c13_cases
from integration.bench_u03_c14.protocol import BENCH as c14_cases

SCHEMA = "BBYQ-U03-C15-native-WAL-stress-v1"
LEVELS = (1, 2, 4, 6)
READERS = {1: 1, 2: 2, 4: 2, 6: 3}
READER_SNAPSHOTS = 8
CASES = (
    Heldout("c15-stress", "Arce", "Boveda Cobre", 30150101, position=0, bit=0),
    Heldout("c15-stress", "Viento", "Faro Blanco", 30150102, position=1, bit=1),
    Heldout("c15-stress", "Papiro", "Puerta Sol", 30150103, position=2, bit=0),
    Heldout("c15-stress", "Orion", "Cerro Claro", 30150104, position=3, bit=1),
    Heldout("c15-stress", "Foca", "Campo Sur", 30150105, position=4, bit=0),
    Heldout("c15-stress", "Robledal", "Punto Luna", 30150106, position=5, bit=1),
    Heldout("c15-stress", "Alamo", "Senda Violeta", 30150107, position=6, bit=0),
    Heldout("c15-stress", "Pizarra", "Huella Bronce", 30150108, position=0, bit=1),
)
COLLISION = CASES[6]
COLLISION_DIFFERENT_PROMPT = CASES[7]
FAULT = CASES[7]
CACHE_CASES = CASES[:3]
EXPECTED_NATIVE_OPERATIONS = (
    "c1_encode_input/c1_next", "qm_read", "vqc_forward",
    "entity_infer", "qrl_step", "qchat_encode/qchat_next",
)
ARMS = ("u02-frozen", "c12-joint-unpromoted")
C13_ROUTE = "c13-cache-frozen-experimental"


def separation():
    seen = (*c11_val(), *c11_test(), *c12_train, *c12_val(), *c12_test,
            *c12_load, *c13_cases, *c14_cases)
    seeds = {row.seed for row in seen} | TRAINED_SEEDS | {88113}
    tokens = {value.lower() for row in seen for value in (row.name,row.rule)}
    tokens.update(("nara", "faro azul"))
    prompts = {row.prompt() for row in seen}
    new = set()
    for row in CASES:
        assert row.seed not in seeds and row.seed not in new
        assert row.name.lower() not in tokens and row.rule.lower() not in tokens
        assert row.prompt() not in prompts
        assert row.position in range(7) and row.bit in (0,1)
        new.add(row.seed)
        tokens.update((row.name.lower(),row.rule.lower()))
    assert len(CASES)==8 and {x.bit for x in CASES}=={0,1}
    assert set(LEVELS)==set(READERS) and LEVELS==tuple(sorted(LEVELS))
    assert LEVELS[-1]<=len(CASES)
    assert FAULT!=COLLISION
    return {
        "independent_of_C11_through_C14":True,
        "case_count":len(CASES),
        "levels":LEVELS,
        "readers_per_level":READERS,
        "reader_snapshots_per_worker":READER_SNAPSHOTS,
        "source_training_unchanged":True,
        "sha256":sha256(json.dumps([row.as_dict() for row in CASES],sort_keys=True).encode()).hexdigest(),
        "simulated_qubits_only":True,
    }
