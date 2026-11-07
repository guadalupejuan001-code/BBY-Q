#!/usr/bin/env python3
"""C07 integrated native metacognition: no change to C1 or earlier states."""
from __future__ import annotations

from hashlib import sha256
import json
from pathlib import Path
import tempfile

from integration.audit_u03_c00.profile import ROOT, MISSION, freeze_assets, apk_files
from integration.cache_u03_c03.session import archive_cache_scope
from integration.unified.session import Session
from .dataset import evidence, unfamiliar_cases
from .session import MetaSession

TURN_SEQUENCE=(
    ("a","calcula 7 + 3"),
    ("m",MISSION),
    ("f","aprende de la última tarea"),
    ("c","no resuelvas Nara"),
)


def clean(value):
    if isinstance(value,dict):
        return {key:clean(x) for key,x in value.items() if key!="elapsed_ms"}
    if isinstance(value,list):
        return [clean(x) for x in value]
    return value


def scenario(cls, c06, r06, c07, r07):
    with tempfile.TemporaryDirectory(prefix="bbyq-c07-epistemic-shadow-") as tmp:
        db=Path(tmp)/"temporary.sqlite"
        with archive_cache_scope():
            if cls is Session:
                entity=Session(db)
            else:
                entity=MetaSession(db,c06_checkpoint=c06,c06_report=r06,
                                   c07_checkpoint=c07,c07_report=r07)
            with entity:
                results=[clean(entity.turn(identifier,text)) for identifier,text in TURN_SEQUENCE]
                snapshot=entity.snapshot()
                history=clean(entity.history())
                if cls is not Session:
                    query={"subject":"Nara", "predicate":"operativo"}
                    supported=entity.assess_evidence(
                        query,(evidence("Nara","operativo",1,"laboratorio:1"),))
                    if supported["recommended_action"]!="answer":
                        raise AssertionError("C07 unjustified abstention with supported fact")
                    missing=entity.assess_evidence(query,())
                    if missing["recommended_action"]!="ask_for_evidence":
                        raise AssertionError("C07 answered without evidence")
                    conflict=entity.assess_evidence(query,(
                        evidence("Nara","operativo",1,"laboratorio:1"),
                        evidence("Nara","operativo",0,"registro:2"),
                    ))
                    if conflict["recommended_action"]!="report_conflict":
                        raise AssertionError("C07 ignored an authenticated contradiction")
                    unsupported=[]
                    for q,rows in unfamiliar_cases():
                        e=entity.assess_evidence(q,rows)
                        if e["recommended_action"]!="ask_for_evidence":
                            raise AssertionError("C07 misrepresented unsupported information")
                        unsupported.append(e["recommended_action"])
                    if snapshot!=entity.snapshot() or history!=clean(entity.history()):
                        raise AssertionError("C07 observation altered original SQLite or banks")
                    if any(x["authoritative"] for x in (supported,missing,conflict)):
                        raise AssertionError("C07 shadow result promoted itself to source of truth")
                replay=clean(entity.turn("m",MISSION))
                if replay!=results[1] or snapshot!=entity.snapshot():
                    raise AssertionError("C07 changed original idempotent native receipt")
                try:
                    entity.turn("aborted","guarda la regla Otra con valor 0 observa Brisa con muestra 122121 y resuelve desde 3",
                                fail_after=2)
                except RuntimeError:
                    pass
                else:
                    raise AssertionError("C07 did not propagate original rollback")
                if snapshot!=entity.snapshot():
                    raise AssertionError("C07 changed native state after rollback")
                status={"results":results,"snapshot":snapshot,"history":history}
        with Session(db) as original:
            if original.snapshot()!=snapshot or clean(original.history())!=history:
                raise AssertionError("Original U02 did not reopen identical C07 knowledge")
        return status


def main():
    before,apks=freeze_assets(),apk_files()
    c06=ROOT/"build/c06/semantic-trained.rvp"
    r06=ROOT/"build/c06/training-report.json"
    c07=ROOT/"build/c07/epistemic-trained.rvp"
    r07=ROOT/"build/c07/training-report.json"
    sha_before=[sha256(p.read_bytes()).hexdigest() for p in (c06,c07)]
    baseline=scenario(Session,c06,r06,c07,r07)
    shadow=scenario(MetaSession,c06,r06,c07,r07)
    if baseline!=shadow:
        raise AssertionError("C07 added hidden changes to original U02 user responses")
    with tempfile.TemporaryDirectory() as temp:
        corrupted=Path(temp)/"corrupted.rvp"
        raw=c07.read_bytes()
        corrupted.write_bytes(raw[:30]+bytes([raw[30]^1])+raw[31:])
        try:
            MetaSession(Path(temp)/"reject.sqlite",
                        c06_checkpoint=c06,c06_report=r06,
                        c07_checkpoint=corrupted,c07_report=r07)
        except ValueError:
            pass
        else:
            raise AssertionError("C07 accepted falsified trained checkpoint")
    if [sha256(p.read_bytes()).hexdigest() for p in (c06,c07)]!=sha_before:
        raise AssertionError("C07 observational inference updated training model")
    if freeze_assets()!=before or apk_files()!=apks:
        raise AssertionError("C07 touched prior checkpoint or built APK")
    report={
        "passed":True,
        "native_XI_meta_shadow_passed":True,
        "original_U02_receipts_history_and_checkpoints_identical":True,
        "native_C06_C07_checkpoint_hashes_preserved":True,
        "supported_fact_answered":True,
        "missing_evidence_abstained":True,
        "conflicting_evidence_reported":True,
        "unfamiliar_cases_abstained":4,
        "replay_rollback_and_original_restart_passed":True,
        "corrupt_C07_checkpoint_rejected":True,
        "models_routed_to_original_answer":False,
        "frozen_asset_count":len(before),
        "frozen_assets_unchanged":True,
        "apk_built":False,
    }
    target=ROOT/"build/c07/integration.json"
    target.write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n")
    print(json.dumps(report,ensure_ascii=False))


if __name__=="__main__":
    main()
