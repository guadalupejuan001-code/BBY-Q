#!/usr/bin/env python3
"""Source linking and exact parent verification, no external cognitive engine."""
import argparse,base64,gzip,hashlib,json,re,subprocess
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('runtime');p.add_argument('prior');p.add_argument('out');a=p.parse_args()
runtime=str(Path(a.runtime).resolve());prior=Path(a.prior).resolve()/'temporal';out=Path(a.out).resolve();out.mkdir(parents=True,exist_ok=True)
sha=lambda f:hashlib.sha256(Path(f).read_bytes()).hexdigest()
def run(*x):return subprocess.run([runtime,*map(str,x)],check=True,capture_output=True,text=True)
parent=prior/'temporal.rxe';assert sha(parent)=='d2c5e4ebb2b0c3b7af74abc881d6f8c1a5ff2e106f621d0ceba5cb312b525048'
seed=out/'controller.rvp';seed.write_bytes(gzip.decompress(base64.b64decode(Path('ai/releases/e025/controller.rvp.gz.b64').read_text())))
assert sha(seed)=='ce058a65092dd9892b6fd55276a17287b764a16bc526ccbfa0085154baef9631'
source=(prior/'temporal-linked.xi').read_text()
assert not any(8400000000000000000<=int(x)<8400000000000073728 for x in re.findall(r'\b[0-9]{19}\b',source)), 'New region collides with parent source'
run('compile',prior/'temporal-linked.xi',out/'parent-code.rxe','BBY Q temporal separation and learned frames')
run('pack-app',out/'parent-code.rxe',seed,out/'parent-repacked.rxe','org.reverse.bbyq','BBY Q','E032-Temporal-1-dev','c93592e0cce4ccfdb3d66a062e6ab737a643dc4a')
assert sha(out/'parent-repacked.rxe')==sha(parent),'Exact parent source/capsule mismatch'
linked=Path('ai/releases/e033/relations.xi').read_text()+source.replace('#!reverse-pc-machine-v1','label mr_parent_entry',1)
(out/'minimal-linked.xi').write_text(linked)
run('compile',out/'minimal-linked.xi',out/'code.rxe','BBY Q minimal shared relation states in Ether')
run('pack-app',out/'code.rxe',seed,out/'minimal.rxe','org.reverse.bbyq','BBY Q','E033-Minimal-Relations-1-dev','d8d26d43c2d9aa8ce7c8e910a7cc543d101fc941')
report={'version':'E033-Minimal-Relations-1-dev','candidate_sha256':sha(out/'minimal.rxe'),'candidate_bytes':(out/'minimal.rxe').stat().st_size,'parent_bytes':parent.stat().st_size,'parent_exact_repack':True,'learning_and_inference':'XI/Ether','new_region_base':'8400000000000000000','new_region_length':73728}
(out/'build.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report),flush=True)
