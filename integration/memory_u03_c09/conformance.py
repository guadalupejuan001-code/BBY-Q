#!/usr/bin/env python3
"""C09 exact real native U02-C09 parity and readonly unified memory audit."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import tempfile

from integration.audit_u03_c00.profile import ROOT, MISSION, apk_files, freeze_assets
from integration.unified.session import Session
from .session import MemorySession
from .view import UnifiedMemoryView, external_claim


CASES=(
    ("mission",MISSION),
    ("recall","lee la regla Faro Azul"),
    ("feedback","aprende de la última tarea"),
    ("math","calcula 7 + 3"),
    ("another","guarda la regla Eco Verde con valor 0"),
)


def canonical(item):
    if isinstance(item,dict):
        return {k:canonical(v) for k,v in item.items() if k!="elapsed_ms"}
    if isinstance(item,list):
        return [canonical(x) for x in item]
    return item


def trial(klass):
    with tempfile.TemporaryDirectory(prefix="bbyq-c09-native-memory-") as td:
        path=Path(td)/"original.sqlite"
        reports=[]
        with klass(path) as entity:
            original=entity.snapshot()
            memory=UnifiedMemoryView(entity)
            initial=memory.snapshot()
            if len(initial["bank_sha256"])!=7 or initial["facts"]:
                # Initial C1 registry can be nonempty depending on prior source
                # identity, but U02's new empty native database should have
                # no user-supplied facts.
                if any(x["kind"] in ("qmemory_association","vqc_projection")
                       for x in initial["facts"]):
                    raise AssertionError("C09 invented an initial memory fact")
            for identifier,prompt in CASES:
                result=entity.turn(identifier,prompt)
                if not result["ok"]:
                    raise AssertionError("C09 native historical contract failed: "+identifier)
                before_index=entity.snapshot()
                report=memory.snapshot()
                filtered=memory.snapshot("Faro Azul")
                if entity.snapshot()!=before_index:
                    raise AssertionError("C09 snapshot mutated U02 memory")
                if report["bank_sha256"]!=before_index["banks"]:
                    raise AssertionError("C09 bank identities differ from U02")
                reports.append({
                    "result":canonical(result),
                    "memory_sha":report["view_sha256"],
                    "filter_count":len(filtered["facts"]),
                    "native_revision":before_index["revision"],
                })
            final=entity.snapshot()
            indexed=memory.snapshot()
            association=next(
                x for x in indexed["facts"]
                if x["kind"]=="qmemory_association" and x["subject"]=="faro azul"
            )
            if association["value"]!=1 or association["provenance"]!="explicit-user-supervision":
                raise AssertionError("C09 did not preserve source-verified user association")
            projection=next(
                x for x in indexed["facts"]
                if x["kind"]=="vqc_projection" and x["subject"]=="observación nara"
            )
            # Original feedback updates the perception revision, so the
            # previously calculated projection is not current until refreshed.
            if projection["status"]!="stale":
                raise AssertionError("C09 silently used an outdated VQC projection")
            changed=memory.reconcile("Faro Azul",overlay=[
                external_claim("Faro Azul","valor",0,"unknown:unverified")
            ])
            if changed["status"]!="conflict_unresolved" or changed["new_writes"]!=0:
                raise AssertionError("C09 failed to flag external disagreement")
            after=entity.snapshot()
            if final!=after:
                raise AssertionError("C09 conflict view modified original native memory")
            history=canonical(entity.history())
            baseline={
                "starting":original,
                "turns":reports,
                "final":final,
                "history":history,
                "observations":indexed["stale_projections"],
                "source_fact_count":len(indexed["facts"]),
                "source_bank_count":len(indexed["bank_sha256"]),
                "contradiction_detected":changed["status"],
            }
            # Existing Session.turn performs exact idempotent replay and
            # propagates native crashes; the optional index must not
            # interfere with that original control path.
            repeated=canonical(entity.turn("mission",MISSION))
            if repeated!=reports[0]["result"] or entity.snapshot()!=final:
                raise AssertionError("C09 altered original native idempotence")
            try:
                entity.turn(
                    "crash",
                    "guarda la regla Otra con valor 0 observa Brisa con muestra 122121 y resuelve desde 3",
                    fail_after=2,
                )
            except RuntimeError:
                pass
            else:
                raise AssertionError("C09 failed original native rollback injection")
            if entity.snapshot()!=final:
                raise AssertionError("C09 modified banks after failed transaction")
        with Session(path) as legacy_reader:
            if legacy_reader.snapshot()!=final or canonical(legacy_reader.history())!=history:
                raise AssertionError("C09 native state not readable by original U02")
        return baseline


def main():
    before, apks=freeze_assets(),apk_files()
    original=trial(Session)
    c09=trial(MemorySession)
    if original!=c09:
        keys=[k for k in original if original[k]!=c09.get(k)]
        raise AssertionError("C09 differs from U02 semantics or checkpoints: "+str(keys))
    if freeze_assets()!=before or apk_files()!=apks:
        raise AssertionError("C09 changed protected assets or generated APK")
    result={
        "passed":True,
        "U02_C09_exact_response_bank_and_history_equal":True,
        "read_only_index_and_contradiction_verified":True,
        "stale_VQC_projection_detected":True,
        "U02_replay_rollback_and_original_restart_equal":True,
        "native_banks_verified":c09["source_bank_count"],
        "source_records_observed":c09["source_fact_count"],
        "frozen_asset_count":len(before),
        "frozen_assets_unchanged":True,
        "apk_built":False,
        "original_execution_reference_sha256":hashlib.sha256(
            json.dumps(original,ensure_ascii=False,sort_keys=True).encode()
        ).hexdigest(),
    }
    dest=ROOT/"build/c09/conformance.json"
    dest.parent.mkdir(parents=True,exist_ok=True)
    dest.write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n")
    print(json.dumps(result,ensure_ascii=False))


if __name__=="__main__":
    main()
