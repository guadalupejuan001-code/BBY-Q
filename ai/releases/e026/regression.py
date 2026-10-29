#!/usr/bin/env python3
"""Run existing E025 regression fixtures against the candidate app."""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
source=(Path(__file__).resolve().parent.parent/"e025/test.py").read_text()
assert source.count("from build import build")==1
source=source.replace("from build import build","from candidate_build import build")
source=source.replace("'version': 'E025-Chain-1'","'version': 'E026-TwoFacts-dev'")
exec(compile(source,"candidate_regression_fixtures.py","exec"),{"__name__":"__main__"})
