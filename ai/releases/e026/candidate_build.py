#!/usr/bin/env python3
"""Link an XI-only composition adapter; preserve authentic E025 unchanged."""
import importlib.util, json, subprocess, hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parent
BASE=ROOT.parent/"e025"
spec=importlib.util.spec_from_file_location("authentic_e025_build",BASE/"build.py")
original=importlib.util.module_from_spec(spec);spec.loader.exec_module(original)

def build(runtime, output, assets=None):
    if assets is not None:
        raise ValueError("Experimental candidate is not an Android deployment")
    out=Path(output).resolve()
    original.build(runtime,out)
    source=(BASE/"conversation-linked.xi").read_text()
    for marker in ["label finish\nhalt","label ui_finish\nhalt"]:
        if source.count(marker)!=1:
            raise ValueError("E025 entry/exit contract changed")
        source=source.replace(marker,marker.split("\n")[0]+"\njmp c26_finish")
    source=source.replace("#!reverse-pc-machine-v1","label c26_base_entry",1)
    linked=(ROOT/"prefix.xi").read_text()+source+(ROOT/"suffix.xi").read_text()
    (out/"candidate.xi").write_text(linked)
    def run(*items):
        return subprocess.check_output([str(runtime),*map(str,items)],text=True)
    run("compile",out/"candidate.xi",out/"candidate-code.rxe","BBY Q E026 composition candidate")
    run("pack-app",out/"candidate-code.rxe",out/"controller.rvp",out/"candidate.rxe",
        "org.reverse.bbyq","BBY Q","E026-TwoFacts-dev","973837fb00322b6a15546d0f7ad9dac11afcb00e")
    # Test copies use the conventional filename, but authentic E025 bytes remain separately available.
    (out/"authentic-E025.rxe").write_bytes((out/"BBY-Q.rxe").read_bytes())
    (out/"BBY-Q.rxe").write_bytes((out/"candidate.rxe").read_bytes())
    report={"version":"E026-TwoFacts-dev","app_sha256":hashlib.sha256((out/"BBY-Q.rxe").read_bytes()).hexdigest(),
        "seed_sha256":hashlib.sha256((out/"controller.rvp").read_bytes()).hexdigest(),
        "intelligence":"XI only; four engineered conjunctive forms, atomic queries and responses delegated to E025",
        "scope":"Candidate engineering; no new learned patterns and no Android deployment"}
    (out/"candidate.json").write_text(json.dumps(report,indent=2)+"\n")
    return report
