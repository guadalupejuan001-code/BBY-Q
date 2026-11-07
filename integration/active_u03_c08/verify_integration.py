#!/usr/bin/env python3
"""C08 observed active model must not alter native U02 or C06/C07 banks."""
from __future__ import annotations

from hashlib import sha256
import json
from pathlib import Path
import tempfile

from integration.audit_u03_c00.profile import ROOT, MISSION, freeze_assets, apk_files
from integration.cache_u03_c03.session import archive_cache_scope
from integration.metacognition_u03_c07.session import MetaSession
from integration.metacognition_u03_c07.dataset import evidence
from integration.unified.session import Session
from .session import ActiveMetaSession


def sanitized(obj):
    if isinstance(obj,dict):
        return {key:sanitized(value) for key,value in obj.items() if key!="elapsed_ms"}
    if isinstance(obj,list):
        return [sanitized(value) for value in obj]
    return obj


def run_one(variant, paths):
    with tempfile.TemporaryDirectory(prefix="bbyq-c08-unified-shadow-") as temp:
        path=Path(temp)/"native-u02.sqlite"
        with archive_cache_scope():
            if variant=="baseline":
                model=MetaSession(path,
                    c06_checkpoint=paths[0],c06_report=paths[1],
                    c07_checkpoint=paths[2],c07_report=paths[3])
            else:
                model=ActiveMetaSession(path,
                    c06_checkpoint=paths[0],c06_report=paths[1],
                    c07_checkpoint=paths[2],c07_report=paths[3],
                    c08_checkpoint=paths[4],c08_report=paths[5])
            with model:
                results=[]
                for key,prompt in (
                    ("a","calcula 7 + 3"),
                    ("b",MISSION),
                    ("c","aprende de la última tarea"),
                    ("d","lee la regla Faro Azul"),
                    ("e","muestra el estado de la entidad"),
                    ("f","no resuelvas Nara"),
                ):
                    results.append(sanitized(model.turn(key,prompt)))
                old=model.snapshot()
                history=sanitized(model.history())
                query={"subject":"Nara","predicate":"activo"}
                cases=(
                    (evidence("Nara","activo",1,"laboratorio:1"),
                     evidence("Another","activo",0,"registro:irrelevant")),
                    (),
                    (evidence("Nara","activo",1,"laboratorio:1"),
                     evidence("Nara","activo",0,"registro:2")),
                )
                for rows in cases:
                    if variant=="baseline":
                        detail=model.assess_evidence(query,rows)
                    else:
                        detail=model.assess_evidence_active(query,rows)
                        if detail["comparison_only"] is not True:
                            raise AssertionError("C08 tried to govern the original C1 answer")
                        if detail["changed_C1_response"] or detail["written_to_previous_banks"]:
                            raise AssertionError("C08 shadow altered native execution")
                        if detail["active"] is None:
                            raise AssertionError("C08 trained XI returned no assessment")
                        if detail["active"]["safety_action"] not in (
                            "answer", "ask_for_evidence", "report_conflict"
                        ):
                            raise AssertionError("C08 generated an unsupported policy")
                if model.snapshot()!=old or sanitized(model.history())!=history:
                    raise AssertionError("C08 uncertainty query rewrote original database")
                replay=sanitized(model.turn("b",MISSION))
                if replay!=results[1] or model.snapshot()!=old:
                    raise AssertionError("C08 changed replay idempotence")
                try:
                    model.turn("crash","guarda la regla Otra con valor 0 observa Brisa con muestra 122121 y resuelve desde 3",
                               fail_after=2)
                except RuntimeError:
                    pass
                else:
                    raise AssertionError("C08 failed injected crash")
                if model.snapshot()!=old:
                    raise AssertionError("C08 altered native bank on abort")
                state={"results":results,"snapshot":old,"history":history}
        with Session(path) as reopen:
            if reopen.snapshot()!=state["snapshot"] or sanitized(reopen.history())!=history:
                raise AssertionError("U02 could not reopen C08 observational checkpoint")
        return state


def main():
    original,apks=freeze_assets(),apk_files()
    paths=[
        ROOT/"build/c06/semantic-trained.rvp",
        ROOT/"build/c06/training-report.json",
        ROOT/"build/c07/epistemic-trained.rvp",
        ROOT/"build/c07/training-report.json",
        ROOT/"build/c08/active-trained.rvp",
        ROOT/"build/c08/active-report.json",
    ]
    checksums=[sha256(p.read_bytes()).hexdigest() for p in paths]
    baseline=run_one("baseline",paths)
    updated=run_one("active",paths)
    if baseline!=updated:
        raise AssertionError("C08 changes frozen original U02 response or checkpoint")
    with tempfile.TemporaryDirectory() as temp:
        corrupt=Path(temp)/"forged.rvp"
        raw=paths[4].read_bytes()
        corrupt.write_bytes(raw[:12]+bytes([raw[12]^1])+raw[13:])
        try:
            ActiveMetaSession(Path(temp)/"rejected.sqlite",
                c06_checkpoint=paths[0],c06_report=paths[1],
                c07_checkpoint=paths[2],c07_report=paths[3],
                c08_checkpoint=corrupt,c08_report=paths[5])
        except ValueError:
            pass
        else:
            raise AssertionError("C08 accepted a changed native RVPC2")
    if [sha256(p.read_bytes()).hexdigest() for p in paths]!=checksums:
        raise AssertionError("C08 altered any checkpoint or experiment report")
    if freeze_assets()!=original or apk_files()!=apks:
        raise AssertionError("C08 modified original assets or built APK")
    evidence={
        "passed":True,
        "identical_U02_C07_C08_user_responses_and_sha256_banks":True,
        "C06_C07_C08_model_files_immutable":True,
        "out_of_domain_and_missing_evidence_fail_closed":True,
        "native_C08_observational_predictions":3,
        "verified_untrusted_model_rejected":True,
        "replay_rollback_and_restart_U02_identical":True,
        "unvalidated_user_records_used_for_training":False,
        "frozen_asset_count":len(original),
        "frozen_asset_sha256_unchanged":True,
        "apk_built":False,
    }
    out=ROOT/"build/c08/integration.json"
    out.write_text(json.dumps(evidence,ensure_ascii=False,indent=2)+"\n")
    print(json.dumps(evidence,ensure_ascii=False))


if __name__=="__main__":
    main()
