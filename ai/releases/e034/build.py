#!/usr/bin/env python3
"""Verify E033 source/capsule and link the native relation composition operator."""
import argparse,base64,gzip,hashlib,json,re,subprocess
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('runtime');p.add_argument('prior');p.add_argument('out');a=p.parse_args()
runtime=str(Path(a.runtime).resolve());prior=Path(a.prior).resolve()/'minimal';out=Path(a.out).resolve();out.mkdir(parents=True,exist_ok=True)
sha=lambda f:hashlib.sha256(Path(f).read_bytes()).hexdigest()
def run(*x):return subprocess.run([runtime,*map(str,x)],check=True,capture_output=True,text=True)
parent=prior/'minimal.rxe';assert sha(parent)=='14334cc91e164ee0299bda3a0a785bd8b0f5e3f41fab744f747d8de1a63dd4f2'
seed=out/'controller.rvp';seed.write_bytes(gzip.decompress(base64.b64decode(Path('ai/releases/e025/controller.rvp.gz.b64').read_text())))
assert sha(seed)=='ce058a65092dd9892b6fd55276a17287b764a16bc526ccbfa0085154baef9631'
source=(prior/'minimal-linked.xi').read_text()
assert not any(8300000000000000000<=int(x)<8300000000000000016 for x in re.findall(r'\b[0-9]{19}\b',source))
run('compile',prior/'minimal-linked.xi',out/'parent-code.rxe','BBY Q minimal shared relation states in Ether')
run('pack-app',out/'parent-code.rxe',seed,out/'parent-repacked.rxe','org.reverse.bbyq','BBY Q','E033-Minimal-Relations-1-dev','d8d26d43c2d9aa8ce7c8e910a7cc543d101fc941')
assert sha(out/'parent-repacked.rxe')==sha(parent)
native=Path('ai/releases/e034/relations.xi').read_text()
assert all(8400000000000000000<=int(x)<8400000000000073728 or 7400000000000000000<=int(x)<7400000000000002000 or 8300000000000000000<=int(x)<8300000000000000016 for x in re.findall(r'\b[0-9]{19}\b',native))
tail=source.split('label mr_parent_entry\n',1)[1]
linked=native+'label mr_parent_entry\n'+tail
(out/'composed-linked.xi').write_text(linked)
run('compile',out/'composed-linked.xi',out/'code.rxe','BBY Q typed relational composition in Ether')
run('pack-app',out/'code.rxe',seed,out/'composed.rxe','org.reverse.bbyq','BBY Q','E034-Relational-Composition-1-dev','e47c537ad2f6ba15e04d0d985737dbf9bb14ba9e')
print(json.dumps({'parent_exact_repack':True,'candidate_sha256':sha(out/'composed.rxe'),'candidate_bytes':(out/'composed.rxe').stat().st_size}),flush=True)
