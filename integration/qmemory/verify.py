#!/usr/bin/env python3
"""Native integration checks: useful circuit learning, durable memory and bounded automation."""
import argparse
from contextlib import redirect_stdout
import io
import json
from pathlib import Path
from types import SimpleNamespace
import tempfile
from controller import A, Engine, auto, birth, sha
from demo import demo


def verify(runtime):
    checks=0
    def require(ok):
        nonlocal checks
        assert ok
        checks+=1
    with tempfile.TemporaryDirectory(prefix='qmemory-verify-') as tmp:
        root=Path(tmp);kernel=root/'kernel';kernel.mkdir();initial=birth(runtime,kernel,4)
        with Engine(runtime,initial) as e:
            e.execute(f'fstore {A+64} 1.5707963267948966\nfstore {A+72} 1.5707963267948966\nfstore {A+80} 0\nstore64 {A+208} 10\nstore64 {A+48} 0\nstore64 {A+16} 0')
            body=''
            for i,(t,c) in enumerate([(0,0),(0,1),(1,0),(1,1)]):body+=f'store8 {A+10000+i} {t}\nstore8 {A+11000+i} 1\nstore8 {A+12000+i} {c}\n'
            ev,_=e.execute(body+f'call qm_forward\nmem_materialize {A+51000} 32')
            raw=next(x['hex'] for x in ev if x['type']=='memory_materialization')
            import struct
            values=struct.unpack('<4d',bytes.fromhex(raw))
            for actual,expected in zip(values,[0,1,0,1]):require(abs(actual-expected)<1e-12)
            # Replacing target cells must not affect any inference output.
            e.execute('\n'.join(f'store8 {A+50000+i} 1' for i in range(4)))
            ev,_=e.execute(f'call qm_forward\nmem_materialize {A+51000} 32')
            require(raw==next(x['hex'] for x in ev if x['type']=='memory_materialization'))
        options=SimpleNamespace(output=str(root/'auto'),runtime=str(runtime),groups=250,seed=181173,max_cycles=3,steps_per_cycle=10,resume=False)
        with redirect_stdout(io.StringIO()):r=auto(options)
        require(r['barrier_passed']);require(r['test']['trained_quantum']['accuracy']>=.95)
        require(r['test']['trained_quantum']['accuracy']-r['test']['frozen_angles']['accuracy']>=.15)
        require(r['test']['memory_erased']['accuracy']<=.6)
        require(r['test']['trained_classical']['accuracy']>=.95)
        require(r['identity']['qubits']==1000)
        require(r['history'][-1]['parameters']['quantum_updates']==r['updates_per_model'])
        require(r['protocol']['quantum_trainable_parameters']==3)
        require(not r['quantum_advantage_claimed'])
        checkpoint=root/'auto'/r['checkpoint'];before=sha(checkpoint)
        options.resume=True
        with redirect_stdout(io.StringIO()):again=auto(options)
        require(again['updates_per_model']==r['updates_per_model']);require(sha(checkpoint)==before)
        # Resume a crash in the testing phase without repeating any training.
        head_file=root/'auto/HEAD.json';head=json.loads(head_file.read_text());head['status']='testing';head_file.write_text(json.dumps(head))
        with redirect_stdout(io.StringIO()):again=auto(options)
        require(again['updates_per_model']==r['updates_per_model']);require(sha(checkpoint)==before)
        for teacher in [0,1]:
            for correction in [0,1]:
                d=demo(root/'auto',runtime,teacher,correction,10)
                require(d['success']);require(all(x['reload_reproduced'] for x in d['turns']))
                require(d['turns'][-1]['predicted']==correction)
        require(sha(checkpoint)==before)
        # Budget exhaustion does not silently activate an unqualified candidate.
        weak=SimpleNamespace(output=str(root/'weak'),runtime=str(runtime),groups=4,seed=181173,max_cycles=1,steps_per_cycle=1,resume=False)
        with redirect_stdout(io.StringIO()):bad=auto(weak)
        require(bad['budget_exhausted']);require(not bad['barrier_passed'])
        require(json.loads((root/'weak/HEAD.json').read_text())['active_checkpoint'] is None)
        # Refuse a corrupted checkpoint before starting another native process.
        with checkpoint.open('ab') as f:f.write(b'x')
        try:
            with redirect_stdout(io.StringIO()):auto(options)
        except AssertionError:require(True)
        else:require(False)
    return {'ok':True,'native_checks':checks,'qubits':1000,'readout_trainable_parameters':0,'quantum_advantage_claimed':False}

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--runtime',required=True);p.add_argument('--output');a=p.parse_args();r=verify(Path(a.runtime).resolve())
    if a.output:
        output=Path(a.output);output.parent.mkdir(parents=True,exist_ok=True);output.write_text(json.dumps(r,indent=2)+'\n')
    print(json.dumps(r))
