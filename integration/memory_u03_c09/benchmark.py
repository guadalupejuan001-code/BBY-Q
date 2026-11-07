#!/usr/bin/env python3
"""C09 direct authenticated read/index overhead vs original U02 snapshot."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import statistics
import tempfile
import time

from integration.audit_u03_c00.profile import ROOT, MISSION,freeze_assets,apk_files
from integration.unified.session import Session
from .view import UnifiedMemoryView


def measure(samples, output):
    if not 1<=samples<=15:
        raise ValueError("C09 samples must be 1..15")
    frozen, apks=freeze_assets(),apk_files()
    with tempfile.TemporaryDirectory(prefix="bbyq-c09-benchmark-") as tmp:
        with Session(Path(tmp)/"synthetic.sqlite") as session:
            result=session.turn("mission",MISSION)
            if not result["ok"]:
                raise AssertionError("C09 frozen native mission failed")
            baseline=session.snapshot()
            timing={"u02_snapshot_ms":[],"c09_full_ms":[],"c09_filtered_ms":[]}
            view=UnifiedMemoryView(session)
            initial_view=view.snapshot()
            for _ in range(samples):
                for name,op in (
                    ("u02_snapshot_ms",session.snapshot),
                    ("c09_full_ms",view.snapshot),
                    ("c09_filtered_ms",lambda:view.snapshot("Faro Azul")),
                ):
                    t=time.perf_counter_ns()
                    data=op()
                    timing[name].append((time.perf_counter_ns()-t)/1e6)
                    if name=="c09_full_ms" and data["view_sha256"]!=initial_view["view_sha256"]:
                        raise AssertionError("C09 read index is not stable")
            if session.snapshot()!=baseline:
                raise AssertionError("C09 benchmark mutated original bank")
    if freeze_assets()!=frozen or apk_files()!=apks:
        raise AssertionError("C09 benchmark created APK or changed source")
    report={
        "passed":True,"samples":samples,"read_only":True,
        "median_ms":{name:round(statistics.median(values),3)
                     for name,values in timing.items()},
        "raw_ms":{name:[round(x,3) for x in values] for name,values in timing.items()},
        "bank_sha256_count":len(initial_view["bank_sha256"]),
        "source_fact_count":len(initial_view["facts"]),
        "protected_asset_count":len(frozen),
        "frozen_assets_unchanged":True,"apk_built":False,
        "caveats":[
            "This measures full cryptographic checks over the original native bank blobs; it is audit overhead, not inference acceleration.",
            "The baseline Session.snapshot reports stored hashes but does not rehash every bank; costs are not functionality-identical.",
            "Measurements are on one synthetic SQLite database in Linux GitHub CI, not on Android.",
            "The view makes no new memory authority and never writes to the native state.",
        ],
    }
    output=Path(output)
    output.parent.mkdir(parents=True,exist_ok=True)
    output.write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n")
    return report


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--samples",type=int,default=3)
    p.add_argument("--out",type=Path,default=ROOT/"build/c09/benchmark.json")
    args=p.parse_args()
    report=measure(args.samples,args.out)
    print(json.dumps({
        "passed":True,"samples":report["samples"],
        "median_ms":report["median_ms"],
        "protected_asset_count":report["protected_asset_count"],
        "apk_built":False,
    },ensure_ascii=False))


if __name__=="__main__":
    main()
