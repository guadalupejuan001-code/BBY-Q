#!/usr/bin/env python3
"""Apply existing E025 regression fixtures to the combined native XI candidate."""
import json, shutil, subprocess, sys
from pathlib import Path

def build_combined(runtime, output):
    output=Path(output).resolve()
    subprocess.check_call(["node","ai/releases/e027/build.mjs",str(runtime),str(output)])
    shutil.copy2(output/"BBY-Q.rxe",output/"authentic-E025.rxe")
    shutil.copy2(output/"candidate.rxe",output/"BBY-Q.rxe")

source=Path("ai/releases/e025/test.py").read_text()
assert source.count("from build import build")==1
source=source.replace("from build import build","build = build_combined")
source=source.replace("'version': 'E025-Chain-1'","'version': 'E027-CtxCompose-2-dev'")
exec(compile(source,"combined_original_fixtures.py","exec"),globals())
