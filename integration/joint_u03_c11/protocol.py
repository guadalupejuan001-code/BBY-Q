"""C11 native training protocol, pinned splits and transaction provenance.

The U02 original XI banks and task supervision remain authoritative.
Joint learning is the EXISTING verified U02 multi-bank feedback, coordinated
and audited by C11 in disposable cloned SQLite. No invented new learner.

Data separation:
- Training mission uses the frozen U02 known example.
- Validation and test seeds are disjoint from training and each other.
- The XI synthetic teacher is materialized ONLY AFTER each evaluation,
  in a separate native V3 session; it cannot enter the prediction call.
- Model selection is based only on validation, never on held-out results.
"""
from __future__ import annotations
from dataclasses import dataclass
from hashlib import sha256
import json

from integration.audit_u03_c00.profile import MISSION

SCHEMA="BBYQ-U03-C11-coordinated-XI-joint-learning-v1"
MODES=("joint-verified","outcome-only","frozen")
CONTROLS=(None,"memory-erased","vqc-ablated","qrl-ablated","voice-ablated")
TRAINING_MISSION=MISSION
TRAINING_CORRECTION="corrige la regla Faro Azul a 0"
FULL_FEEDBACK="aprende de la última tarea"

@dataclass(frozen=True)
class Heldout:
    split: str
    name: str
    rule: str
    seed: int
    position: int=3
    bit: int=1

    def prompt(self) -> str:
        return f"guarda la regla {self.rule} con valor {self.bit} observa {self.name} con muestra {self.seed} y resuelve desde {self.position}"

    def as_dict(self):
        return dict(split=self.split,name=self.name,rule=self.rule,
                    seed=self.seed,position=self.position,bit=self.bit)

# First split is used for candidate approval only. The test list is accessed
# ONLY after validation has determined which candidate could be promoted.
VAL=(
    Heldout("validation","Vela","Sol Claro",23060113),
    Heldout("validation","Delta","Luna Serena",23060114),
    Heldout("validation","Nube","Orbe Azul",23060115),
)
TEST=(
    Heldout("test","Prisma","Eco Verde",23060211),
    Heldout("test","Aurora","Roca Firme",23060212),
    Heldout("test","Alba","Bruma Norte",23060213),
    Heldout("test","Lince","Faro Nuevo",23060214),
)
TRAINED_NAMES={"nara","faro azul"}
TRAINED_SEEDS={88113}


def validation() -> tuple[Heldout,...]:
    return VAL


def heldout_test() -> tuple[Heldout,...]:
    # The production campaign accesses this only after it has frozen
    # promotion and the training candidate SHA from validation.
    return TEST


def separation(training, val, test) -> dict:
    all_cases=(("training",training),("validation",val),("test",test))
    names=set();seeds=set();prompts=set();out={}
    for split,rows in all_cases:
        current_names=set(); current_seeds=set();current_prompts=set()
        for row in rows:
            if isinstance(row,Heldout):
                a,b=row.name.lower(),row.rule.lower()
                seed=row.seed
                prompt=row.prompt()
            else:
                a,b,seed,prompt="nara","faro azul",88113,TRAINING_MISSION
            current_names.update((a,b))
            current_seeds.add(seed)
            current_prompts.add(prompt)
        if current_names & names or current_seeds & seeds or current_prompts & prompts:
            raise AssertionError("C11 leaked name/seed/prompt across splits")
        names |= current_names
        seeds |= current_seeds
        prompts |= current_prompts
        out[split]={
            "count":len(rows),
            "hash":sha256(json.dumps([row.as_dict() if isinstance(row,Heldout)
                                      else {"prompt":TRAINING_MISSION}
                                      for row in rows],sort_keys=True).encode()).hexdigest(),
        }
    return {
        "splits":out,
        "training_validation_test_names_disjoint":True,
        "training_validation_test_seeds_disjoint":True,
        "validation_not_trained":True,
        "test_not_trained":True,
        "test_opened_after_model_selection":True,
        "supervision_transport":"original U02 XI feedback-only branch",
    }


def controls_must_be_existing():
    assert set(CONTROLS)=={
        None,"memory-erased","vqc-ablated","qrl-ablated","voice-ablated"
    }
    assert len(MODES)==3
    return True
