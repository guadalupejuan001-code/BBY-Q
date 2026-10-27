#!/usr/bin/env python3
"""Stream synthetic labeled mathematics into XI; no host-side agent inference.

Candidate primitives are designed in XI. The teacher supplies opaque concept
IDs and observed consequences, never the correct primitive ID to the learner.
"""
import argparse
import base64
import gzip
import hashlib
import importlib.util
import json
from pathlib import Path
import struct
import subprocess
import time

ROOT=Path(__file__).resolve().parents[1]
REPO=ROOT.parents[2]
M=7900000000000000000
PARENT_SHA='aa8be33d964af55d9976f46745775113d6996630cbbfad3bb5c2b4d75833e9d0'
spec=importlib.util.spec_from_file_location('e019',ROOT.parent/'open/tests/native-e019.py')
e019=importlib.util.module_from_spec(spec);spec.loader.exec_module(e019)
snapshot=e019.snapshot


def rows():
    return [line.split('|') for line in (ROOT/'data/operators.psv').read_text().splitlines() if line and not line.startswith('#')]


FAMILIES={int(concept):int(family) for concept,family,_,_ in rows()}


def teacher(family,a,b):
    # Training grid: a=0..511,b=1..512. Signed consequences distinguish
    # subtraction from absolute distance; division uses exact products.
    x=a*b if family==4 else a
    result={1:lambda:x-b,2:lambda:x+b,3:lambda:x*b,4:lambda:x//b,
            5:lambda:x%b,6:lambda:min(x,b),7:lambda:max(x,b),8:lambda:abs(x-b)}[family]()
    return x,b,result


def u32(memory,address):return sum(memory.get(address+i,0)<<(8*i) for i in range(4))


class Campaign:
    def __init__(self,runtime,out):
        self.runtime=str(Path(runtime).resolve());self.out=Path(out).resolve();self.out.mkdir(parents=True,exist_ok=True)
        self.state=self.out/'state.rvp';self.next=self.out/'next.rvp';self.program=self.out/'event.xi'
        self.parent=gzip.decompress(base64.b64decode((REPO/'ai/checkpoints/BBYQ_E019_Context_Questions_ES_EN.rvp.gz.b64').read_bytes()))
        assert hashlib.sha256(self.parent).hexdigest()==PARENT_SHA
        self.state.write_bytes(self.parent);self.original=snapshot(self.state)
        self.batch_code=(ROOT/'learn-batch.xi').read_text().split('\n',1)[1]
        self.batch_times=[];self.processed=0;self.digest=hashlib.sha256()

    def run(self,code,reject=False):
        self.program.write_text(code);self.next.unlink(missing_ok=True)
        before=self.state.read_bytes() if reject else None
        start=time.perf_counter()
        result=subprocess.run([self.runtime,'run',str(self.program),str(self.state),str(self.next)],capture_output=True,text=True,timeout=60)
        elapsed=time.perf_counter()-start
        if reject:
            assert result.returncode!=0,'invalid input accepted'
            assert not self.next.exists() and self.state.read_bytes()==before
        else:
            assert result.returncode==0,result.stderr
            self.next.replace(self.state)
        return elapsed,result.stdout

    def preserve(self):
        core,memory,bindings=snapshot(self.state)
        assert core==self.original[0] and bindings==self.original[2]
        assert {a:b for a,b in memory.items() if not M<=a<M+100000}==self.original[1]
        assert not any(memory.get(M+i,0) for i in range(16,32))
        assert not any(M+10000<=a<M+20240 for a in memory)
        assert u32(memory,M+8)==self.processed
        return memory

    def batch(self,concept,observations,mode=0,reject=False):
        assert 1<=len(observations)<=1024
        fields=[(M+16,mode),(M+17,concept),(M+18,len(observations)%256),(M+19,len(observations)//256)]
        packed=b''.join(struct.pack('<IHi',*obs) for obs in observations)
        code='#!reverse-pc-machine-v1\n'+''.join(f'store8 {address} {value}\n' for address,value in fields)
        code+=''.join(f'store8 {M+10000+i} {value}\n' for i,value in enumerate(packed))+self.batch_code
        elapsed,_=self.run(code,reject=reject)
        if reject:return elapsed
        self.batch_times.append(elapsed)
        if mode==0:
            self.processed+=len(observations)
            self.digest.update(b''.join(bytes([concept])+struct.pack('<IHi',*obs) for obs in observations))
        return elapsed


def main():
    p=argparse.ArgumentParser();p.add_argument('runtime');p.add_argument('--out',default='evidence/e020')
    p.add_argument('--per-concept',type=int,default=512*512);p.add_argument('--batch',type=int,default=1024)
    args=p.parse_args();assert 1<=args.per_concept<=512*512 and 1<=args.batch<=1024
    e=Campaign(args.runtime,args.out);e.run((ROOT/'birth.xi').read_text())
    start=time.perf_counter()
    for concept,family in sorted(FAMILIES.items()):
        for offset in range(0,args.per_concept,args.batch):
            indices=range(offset,min(offset+args.batch,args.per_concept))
            e.batch(concept,[teacher(family,i//512,i%512+1) for i in indices])
            if e.processed%65536==0:
                e.preserve();print('E020_NATIVE_TRAINING_PROGRESS',e.processed,'SECONDS',round(time.perf_counter()-start,2),flush=True)
        mem=e.preserve()
        a=M+128+(concept-1)*64
        assert u32(mem,a+4)==args.per_concept
        print('E020_CONCEPT_LEARNED',concept,'MASK',mem.get(a,0),'ROWS',args.per_concept,flush=True)
    elapsed=time.perf_counter()-start
    report={'parent_sha256':PARENT_SHA,'training_examples':e.processed,'examples_per_concept':args.per_concept,
            'batch_size':args.batch,'batches':len(e.batch_times),'training_seconds':elapsed,
            'examples_per_second':e.processed/elapsed,'corpus_sha256':e.digest.hexdigest(),
            'checkpoint_bytes_before':len(e.parent),'checkpoint_bytes_after_training':e.state.stat().st_size,
            'all_examples_consumed_inside_xi':True,'original_state_unchanged':True,
            'data':'synthetic structured integer arithmetic; not unrestricted natural language or new world facts'}
    (e.out/'training.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(report,ensure_ascii=False,indent=2),flush=True)


if __name__=='__main__':main()
