#!/usr/bin/env python3
"""Link native temporal learner over the exact previously evaluated E031 source."""
import argparse,hashlib,json,subprocess
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('runtime');p.add_argument('prior');p.add_argument('out');a=p.parse_args()
runtime=str(Path(a.runtime).resolve());prior=Path(a.prior).resolve()/'dictionary';out=Path(a.out).resolve();out.mkdir(parents=True,exist_ok=True)
sha=lambda f:hashlib.sha256(Path(f).read_bytes()).hexdigest()
assert sha(prior/'dictionary.rxe')=='340a2b288a3659265c954fc93250fe33ac7df905c48c58caf7179bbe6e911fa6'
parent=(prior/'dictionary-linked.xi').read_text()
source=Path('ai/releases/e032/temporal.xi').read_text()+parent.replace('#!reverse-pc-machine-v1','label te_parent_entry',1)
(out/'temporal-linked.xi').write_text(source)
def run(*x):return subprocess.run([runtime,*map(str,x)],check=True,capture_output=True,text=True)
# Recompile parent first: verification, not new learning.
run('compile',prior/'dictionary-linked.xi',out/'parent-code.rxe','parent source verification')
run('pack-app',out/'parent-code.rxe',prior/'controller.rvp',out/'parent-repacked.rxe','org.reverse.bbyq','BBY Q','E031-Dictionary-1-dev','d9440d5300900b0418c8f14b4713b882c7f375dc')
assert sha(out/'parent-repacked.rxe')==sha(prior/'dictionary.rxe'),'Parent source/capsule mismatch'
run('compile',out/'temporal-linked.xi',out/'temporal-code.rxe','BBY Q temporal separation and learned frames')
run('pack-app',out/'temporal-code.rxe',prior/'controller.rvp',out/'temporal.rxe','org.reverse.bbyq','BBY Q','E032-Temporal-1-dev','c93592e0cce4ccfdb3d66a062e6ab737a643dc4a')
report={'version':'E032-Temporal-1-dev','candidate_sha256':sha(out/'temporal.rxe'),'parent_sha256':sha(prior/'dictionary.rxe'),'exact_parent_repack':True,'language_and_learning':'XI','limits':'64 learned two-slot frames, 256 signed facts, three relative time buckets; no dates, aspect or open conjugation yet'}
(out/'build.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report),flush=True)
