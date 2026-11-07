#!/usr/bin/env python3
"""Measure C10 provenance audit/sandbox overhead, never call it a speedup."""
from __future__ import annotations

import argparse
import json
import sqlite3
import statistics
from pathlib import Path
import tempfile
import time

from integration.audit_u03_c00.profile import ROOT, MISSION, freeze_assets, apk_files
from integration.unified.session import Session
from .engine import Reasoner
from .planner import Goal, original_native_prompt

RULE="si alguien es clase cero entonces es alerta"
CASES=(
    Goal("prove_alert","Nara"),
    Goal("plan_mission","Nara","Faro Azul",3),
)


def one_run(samples):
    protected,apks=freeze_assets(),apk_files()
    with tempfile.TemporaryDirectory(prefix="bbyq-c10-speed-audit-") as td:
        root=Path(td)
        with Session(root/"original.sqlite") as source:
            if not source.turn("init-mission",MISSION)["ok"]:
                raise AssertionError("Original XI mission setup failed")
            if not source.turn("init-rule",RULE)["ok"]:
                raise AssertionError("Original native XI rule setup failed")
            before=source.snapshot()
            captured={}
            for goal in CASES:
                direct=[]
                audited=[]
                prompt=original_native_prompt(goal)
                for index in range(samples):
                    # Direct native baseline runs in a *clone* too, as native
                    # programs can change their sandbox state and receipts.
                    new=root/(f"baseline-{goal.kind}-{index}.sqlite")
                    with sqlite3.connect(new,isolation_level=None) as target:
                        source.db.backup(target)
                    with Session(new) as baseline:
                        started=time.perf_counter_ns()
                        result=baseline.turn("direct-probe",prompt)
                        direct.append((time.perf_counter_ns()-started)/1e6)
                        if not result["ok"]:
                            raise AssertionError("Original native XI direct baseline failed")
                    started=time.perf_counter_ns()
                    plan=Reasoner(source).plan(goal)
                    audited.append((time.perf_counter_ns()-started)/1e6)
                    if plan["status"]!=(
                        "native_proof" if goal.kind=="prove_alert" else "native_plan"
                    ):
                        raise AssertionError("C10 rejected exact native provenance test")
                    if source.snapshot()!=before:
                        raise AssertionError("Benchmark C10 changed original U02 source")
                captured[goal.kind]={
                    "direct_native_ms":round(statistics.median(direct),3),
                    "full_audited_C10_ms":round(statistics.median(audited),3),
                    "read_audit_and_copy_overhead_ms":round(
                        statistics.median(audited)-statistics.median(direct),3
                    ),
                    "native_execution_skipped":False,
                }
    if freeze_assets()!=protected or apk_files()!=apks:
        raise AssertionError("C10 performance audit altered frozen state or built APK")
    return {
        "passed":True,
        "samples_per_case":samples,
        "cases":captured,
        "frozen_asset_count":len(protected),
        "apk_built":False,
        "caveats":[
            "Direct XI timing is measured inside a fresh copied SQLite connection, excluding time to create the copy.",
            "C10 includes full C09 SHA audit, clone, native XI and recheck; the two numbers do not measure equivalent security contracts.",
            "C10 is an expensive opt-in traceability function, not a rendering or execution acceleration.",
            "Only the original fixed U02 contracts were tested on synthetic fixtures; not arbitrary reasoning or Android.",
        ],
    }


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--samples",type=int,default=2)
    p.add_argument("--out",type=Path,default=ROOT/"build/c10/benchmark.json")
    args=p.parse_args()
    if not 1<=args.samples<=6:
        p.error("samples must be 1..6")
    data=one_run(args.samples)
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(data,ensure_ascii=False,indent=2)+"\n")
    print(json.dumps(data,ensure_ascii=False))


if __name__=="__main__":
    main()
