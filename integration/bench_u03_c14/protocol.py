"""C14 predeclared novel tasks; no reuse of C11/C12/C13 test labels.

The training remains the original C12 supervised XI learning on its own
historical synthetic task set. C14 uses no new feedback during evaluation;
native synthetic VQC teachers are computed separately *after* all predictions.
"""
from __future__ import annotations
from hashlib import sha256
import json

from integration.joint_u03_c11.protocol import (
    Heldout, TRAINED_SEEDS, validation as c11_val, heldout_test as c11_test,
)
from integration.blocks_u03_c12.protocol import (
    TRAIN as c12_train, VALIDATION as c12_val, TEST as c12_test, LOAD as c12_load,
)
from integration.optimize_u03_c13.campaign import CASES as c13_cases

SCHEMA = "BBYQ-U03-C14-disjoint-XI-packets-v1"
BENCH = (
    Heldout("c14-native", "Fresno", "Raiz Naciente", 29140101, position=0, bit=0),
    Heldout("c14-native", "Topacio", "Norte Limpio", 29140102, position=2, bit=1),
    Heldout("c14-native", "Cerezo", "Roca Amarilla", 29140103, position=4, bit=0),
    Heldout("c14-native", "Palma", "Cauce Lejano", 29140104, position=6, bit=1),
    Heldout("c14-native", "Granate", "Arco Dorado", 29140105, position=1, bit=0),
    Heldout("c14-native", "Mistral", "Sol Frio", 29140106, position=5, bit=1),
)
# Run A→B→A with different memory rules in a single original U02 session.
INTERFERENCE = (BENCH[0], BENCH[3], BENCH[0])
ABLATIONS = BENCH[:4]
CONCURRENT = (BENCH[4], BENCH[5])
ROUTES = {
    "u02-frozen": ("frozen", False),
    "c12-joint-unpromoted": ("joint", False),
    "c13-cache-frozen-experimental": ("frozen", True),
}
NATIVE_CONTROLS = (None, "memory-erased", "vqc-ablated", "qrl-ablated", "voice-ablated")


def separation():
    old=(*c11_val(),*c11_test(),*c12_train,*c12_val,*c12_test,*c12_load,*c13_cases)
    all_seeds={r.seed for r in old} | TRAINED_SEEDS | {88113}
    all_names={a.lower() for r in old for a in (r.name,r.rule)} | {"nara","faro azul"}
    all_prompts={r.prompt() for r in old}
    current_seeds=set()
    current_names=set()
    assert len(BENCH)==6 and len(ABLATIONS)==4 and len(CONCURRENT)==2
    assert set(ROUTES)=={"u02-frozen","c12-joint-unpromoted","c13-cache-frozen-experimental"}
    assert set(NATIVE_CONTROLS)=={None,"memory-erased","vqc-ablated","qrl-ablated","voice-ablated"}
    for row in BENCH:
        assert row.seed not in all_seeds and row.seed not in current_seeds
        assert row.name.lower() not in all_names and row.rule.lower() not in all_names
        assert row.name.lower() not in current_names and row.rule.lower() not in current_names
        assert row.prompt() not in all_prompts
        assert row.bit in (0,1) and 0<=row.position<=6
        current_seeds.add(row.seed)
        current_names.update((row.name.lower(),row.rule.lower()))
    assert {r.bit for r in BENCH}=={0,1}
    assert set(r.position for r in BENCH)=={0,1,2,4,5,6}
    assert INTERFERENCE[0]==INTERFERENCE[2] and INTERFERENCE[0]!=INTERFERENCE[1]
    return {
        "novel_vs_C11_C12_C13":True,
        "rules_both_values":True,
        "case_count":len(BENCH),
        "ablations_cases":len(ABLATIONS),
        "sha256":sha256(json.dumps([c.as_dict() for c in BENCH],sort_keys=True).encode()).hexdigest(),
        "benchmark_prompts_not_trained":True,
        "physical_quantum_hardware":False,
    }
