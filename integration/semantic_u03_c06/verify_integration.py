#!/usr/bin/env python3
"""End-to-end C06 shadow XI inference without replacing U02 authority."""
from __future__ import annotations

from contextlib import nullcontext
from hashlib import sha256
import json
from pathlib import Path
import tempfile

from integration.audit_u03_c00.profile import ROOT, freeze_assets, apk_files, MISSION
from integration.codifier_u03_c05.session import SemanticSession
from integration.cache_u03_c03.session import archive_cache_scope
from integration.unified.session import Session
from .dataset import LABELS
from .session import ShadowSemanticSession

PROMPTS = (
    ("n0", "no definas Prisma", 0),
    ("x0", "define Prisma no Brisa", 1),
    ("y0", "define Prisma", 2),
    ("r0", "guarda la regla Faro Azul con valor 1", 2),
    ("r1", "lee la regla Faro Azul", 2),
    ("m0", MISSION, 2),
    ("f0", "aprende de la última tarea", 2),
)


def cleaned(x):
    if isinstance(x, dict):
        return {key: cleaned(value) for key, value in x.items() if key != "elapsed_ms"}
    if isinstance(x, list):
        return [cleaned(item) for item in x]
    return x


def trial(cls, cp, report):
    with tempfile.TemporaryDirectory(prefix="bbyq-c06-shadow-") as tmp:
        db = Path(tmp) / "knowledge.sqlite"
        with archive_cache_scope():
            if cls is ShadowSemanticSession:
                entity = cls(db, checkpoint=cp, report=report)
            else:
                entity = cls(db)
            with entity:
                outcomes = []
                for identifier, text, target in PROMPTS:
                    output = entity.turn(identifier, text)
                    prediction = (entity.last_learned_semantic
                                  if isinstance(entity, ShadowSemanticSession) else None)
                    if prediction is not None:
                        if prediction["label_id"] != target or prediction["authoritative"]:
                            raise AssertionError("Shadow XI semantic prediction diverged")
                        if prediction["semantic_class"] != LABELS[target]:
                            raise AssertionError("Native semantic labels changed")
                    outcomes.append(cleaned(output))
                old = entity.snapshot()
                history = cleaned(entity.history())
                result = entity.turn("m0", MISSION)
                if cleaned(result) != outcomes[5] or entity.snapshot() != old:
                    raise AssertionError("Shadow semantic replay changed original native state")
                try:
                    entity.turn("crash",
                                "guarda la regla Otra con valor 0 observa Brisa con muestra 122121 y resuelve desde 3",
                                fail_after=2)
                except RuntimeError:
                    pass
                else:
                    raise AssertionError("Injected failure did not propagate")
                if entity.snapshot() != old:
                    raise AssertionError("Shadow semantic modified rollback")
                if isinstance(entity, ShadowSemanticSession) and entity.last_learned_semantic is not None:
                    raise AssertionError("C06 predicted after aborted native turn")
                state = {"outcomes": outcomes, "snapshot": old, "history": history}
        with Session(db) as original:
            if original.snapshot() != state["snapshot"] or cleaned(original.history()) != history:
                raise AssertionError("U02 cannot reopen exact C06 knowledge state")
        return state


def main():
    old_assets, old_apks = freeze_assets(), apk_files()
    checkpoint = ROOT / "build/c06/semantic-trained.rvp"
    report = ROOT / "build/c06/training-report.json"
    old_sha = sha256(checkpoint.read_bytes()).hexdigest()
    baseline = trial(SemanticSession, checkpoint, report)
    observed = trial(ShadowSemanticSession, checkpoint, report)
    if observed != baseline:
        raise AssertionError("C06 shadow mode changed U02 responses or snapshots")
    with tempfile.TemporaryDirectory() as tmp:
        invalid = Path(tmp) / "invalid.rvp"
        original = checkpoint.read_bytes()
        invalid.write_bytes(original[:10] + bytes([original[10] ^ 0x01]) + original[11:])
        try:
            ShadowSemanticSession(Path(tmp) / "rejected.sqlite",
                                  checkpoint=invalid, report=report)
        except ValueError:
            pass
        else:
            raise AssertionError("C06 accepted a tampered learned checkpoint")
    if sha256(checkpoint.read_bytes()).hexdigest() != old_sha:
        raise AssertionError("C06 shadow readout trained without authorization")
    if freeze_assets() != old_assets or apk_files() != old_apks:
        raise AssertionError("C06 shadow mode changed frozen assets or generated APK")
    result = {
        "passed": True,
        "shadow_XI_classifications": len(PROMPTS),
        "correct_expected_classes": len(PROMPTS),
        "U02_outcome_and_checkpoint_identical": True,
        "replay_and_rollback_preserved": True,
        "invalid_learned_checkpoint_rejected": True,
        "candidate_RVPC2_sha256_before_after_equal": True,
        "frozen_asset_count": len(old_assets),
        "frozen_assets_unchanged": True,
        "apk_built": False,
        "model_routed_to_user_response": False,
    }
    output = ROOT / "build/c06/shadow-conformance.json"
    output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()
