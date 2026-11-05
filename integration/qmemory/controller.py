#!/usr/bin/env python3
"""Bounded autonomous experiment. Learning, data and both forward models are XI."""
import argparse
import gzip
import hashlib
import json
import os
from pathlib import Path
import statistics
import struct
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[2]
XI = ROOT/'ai/xi/qmemory/model.xi'
A = 8170000000000000000

def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def seed(base, split, i): return int.from_bytes(hashlib.sha256(f'QM181:{base}:{split}:{i}'.encode()).digest()[:4], 'little') & 0x7fffffff

def atomic(p, value):
    pending = p.with_suffix(p.suffix+'.pending')
    with pending.open('w') as f:
        json.dump(value, f, ensure_ascii=False, indent=2); f.write('\n'); f.flush(); os.fsync(f.fileno())
    pending.replace(p)

def source(body): return '#!reverse-pc-machine-v1\nbudget 100000000\n'+body+'\nhalt\n'+XI.read_text()

def emit(): return 'femit loss f25\nitof f0 r6\nfemit correct f0\nitof f0 r7\nfemit correction_cases f0\nitof f0 r8\nfemit correction_correct f0'

def metrics(events): return {e['name']:e['value'] for e in events if e['type']=='metric'}

class Engine:
    def __init__(self, runtime, state):
        self.runtime = Path(runtime).resolve()
        self.library = XI.read_text()
        sys.path.insert(0, str(self.runtime/'scripts'))
        from xi_session_client import XiSession
        self.s = XiSession(self.runtime/'build/xi_session', state)
    def execute(self, body): return self.s.execute('#!reverse-pc-machine-v1\nbudget 100000000\n'+body+'\nhalt\n'+self.library)
    def __enter__(self): return self
    def __exit__(self, *args): self.s.close()
    def parameters(self):
        ev, _ = self.execute(f'mem_materialize {A+64} 56\nload64 r0 {A+24}\nprint r0\nload64 r0 {A+32}\nprint r0')
        raw=bytes.fromhex(next(e['hex'] for e in ev if e['type']=='memory_materialization'))
        v=struct.unpack('<7d',raw)
        counters=[e['value'] for e in ev if e['type']=='register']
        return {'quantum_angles':list(v[:3]),'classical_angles':list(v[4:7]),'quantum_updates':counters[0],'classical_updates':counters[1]}
    def episode(self, role, case_seed, delay, train=False, reset=False, trace=False):
        if role not in [0,1] or not 0<=delay<=12: raise ValueError('Invalid experiment input')
        body=f'store64 {A+16} {role}\nstore64 {A+200} {case_seed}\nstore64 {A+208} {delay}\nstore64 {A+48} {int(reset)}\ncall qm_data\n'
        if trace: body+='qtrace reset\n'
        body+='call qm_train\n' if train else 'call qm_forward\ncall qm_score\n'
        body+=emit()
        if trace: body+='\nqtrace report\nqstats\nstats'
        ev,ms=self.execute(body)
        result=dict(metrics(ev),transport_ms=ms,seed=case_seed,delay=delay)
        if trace:
            result['trace']=next(e for e in ev if e['type']=='quantum_trace')
            result['backend']=next(e for e in ev if e['type']=='quantum_stats')
            result['stats']=next(e for e in ev if e['type']=='stats')
        return result


def birth(runtime, out, groups):
    empty=out/'empty.rvp'; state=out/'initial.rvp'
    subprocess.run([str(Path(runtime)/'build/reverse_pc'),'init',str(empty)],check=True,capture_output=True)
    with Engine(runtime,empty) as e:
        body=f'store64 {A} 181\nstore64 {A+8} {groups}\nfstore {A+128} 1.2\nfstore {A+136} .001\n'
        for offset,value in [(64,.3),(72,.4),(80,.35),(96,.3),(104,.4),(112,.35)]: body+=f'fstore {A+offset} {value}\n'
        body+='set r15 0\nlabel reserve\nmov r0 r15\nmul r0 4\nadd r0 20000\nqprepare $r0 4\nadd r15 1\n'+f'cmp r15 {groups}\njlt reserve'
        e.execute(body);e.s.save(state)
    return state


def evaluate(runtime, state, groups, base_seed, split, repeats=2, delays=(3,7), role=0, reset=False):
    original=sha(state);rows=[]
    with Engine(runtime,state) as e:
        before=e.parameters()
        for delay in delays:
            for i in range(repeats):rows.append(e.episode(role,seed(base_seed,split,delay*100+i),delay,reset=reset,trace=(len(rows)==0)))
        assert before==e.parameters(), 'Inference modified trained parameters'
        usage=e.s.metrics()
    assert sha(state)==original
    correct=int(sum(r['correct'] for r in rows));total=groups*len(rows)
    corrected=int(sum(r['correction_cases'] for r in rows));corrected_ok=int(sum(r['correction_correct'] for r in rows))
    return {'correct':correct,'examples':total,'accuracy':correct/total,'mse':statistics.mean(r['loss'] for r in rows),'correction_accuracy':corrected_ok/corrected if corrected else None,'episodes':len(rows),'cases':rows,'usage':usage}


def auto(args):
    out=Path(args.output).resolve();runtime=Path(args.runtime).resolve();manifest=out/'HEAD.json'
    identity={'schema':1,'model':181,'groups':args.groups,'qubits':4*args.groups,'base_seed':args.seed,'max_cycles':args.max_cycles,'steps_per_cycle':args.steps_per_cycle,'native_source_sha256':sha(XI),'controller_sha256':sha(__file__),'runtime_sha256':sha(runtime/'build/xi_session')}
    if args.resume:
        head=json.loads(manifest.read_text())
        if head['identity']!=identity: raise ValueError('Resume requires the same budget, source, seed and runtime')
        checkpoint=out/head['checkpoint'];assert sha(checkpoint)==head['checkpoint_sha256']
        if head['status']=='completed':
            report=json.loads((out/'report.json').read_text())
            print(json.dumps({'completed':True,'replayed':True,'barrier_passed':report['barrier_passed'],'quantum':report['test']['trained_quantum']['accuracy'],'frozen':report['test']['frozen_angles']['accuracy'],'erased':report['test']['memory_erased']['accuracy'],'classical':report['test']['trained_classical']['accuracy'],'report':str(out/'report.json')}),flush=True)
            return report
        cycle=head['cycle'];updates=head['updates'];history=head['history']
    else:
        if out.exists(): raise ValueError('Choose a fresh output or explicitly resume it')
        out.mkdir(parents=True);checkpoint=birth(runtime,out,args.groups);cycle=updates=0;history=[]
        head={'identity':identity,'checkpoint':checkpoint.name,'checkpoint_sha256':sha(checkpoint),'cycle':0,'updates':0,'history':history,'status':'running'};atomic(manifest,head)
    initial=out/'initial.rvp'
    frozen=evaluate(runtime,initial,args.groups,args.seed,'validation',repeats=2)
    initial_hash=sha(initial)
    checkpoint_hash=sha(checkpoint)
    started=time.monotonic()
    while cycle<args.max_cycles and head['status']!='testing':
        assert sha(XI)==identity['native_source_sha256'], 'Native implementation changed during this run'
        with Engine(runtime,checkpoint) as e:
            for _ in range(args.steps_per_cycle):
                case_seed=seed(args.seed,'train',updates);delay=updates%7
                q=e.episode(0,case_seed,delay,train=True)
                c=e.episode(1,case_seed,delay,train=True)
                updates+=1
            next_cycle=cycle+1
            destination=out/f'cycle-{next_cycle:03d}.rvp'
            # A crash after SAVE but before HEAD may leave an orphan; never overwrite it.
            if destination.exists(): destination=out/f'cycle-{next_cycle:03d}-{time.time_ns()}.rvp'
            e.s.save(destination);params=e.parameters()
        assert sha(checkpoint)==checkpoint_hash
        validation=evaluate(runtime,destination,args.groups,args.seed,'validation',repeats=2)
        item={'cycle':next_cycle,'updates_per_model':updates,'quantum':validation,'parameters':params,'last_training':{'quantum':q,'classical':c}}
        history.append(item);cycle=next_cycle;checkpoint=destination;checkpoint_hash=sha(checkpoint)
        reached=validation['accuracy']>=.95 and validation['accuracy']-frozen['accuracy']>=.15
        head={'identity':identity,'checkpoint':checkpoint.name,'checkpoint_sha256':checkpoint_hash,'cycle':cycle,'updates':updates,'history':history,'status':'testing' if reached or cycle==args.max_cycles else 'running'};atomic(manifest,head)
        print(json.dumps({'cycle':cycle,'updates':updates,'validation_accuracy':validation['accuracy'],'validation_mse':validation['mse'],'angles':params['quantum_angles'],'criterion_reached':reached}),flush=True)
        if reached:break
    # Fresh test seeds and unseen delays are never used to choose angles or stop training.
    test=evaluate(runtime,checkpoint,args.groups,args.seed,'test',repeats=4,delays=(2,8,12))
    frozen_test=evaluate(runtime,initial,args.groups,args.seed,'test',repeats=4,delays=(2,8,12))
    erased=evaluate(runtime,checkpoint,args.groups,args.seed,'test',repeats=4,delays=(2,8,12),reset=True)
    classical=evaluate(runtime,checkpoint,args.groups,args.seed,'test',repeats=4,delays=(2,8,12),role=1)
    trace=test['cases'][0]
    assert trace['stats']['active_qubits']==4*args.groups
    backend=trace['backend'];assert trace['stats']['components']==sum(backend[k] for k in ['clifford_components','adaptive_components','reduced_components'])
    assert sha(initial)==initial_hash and sha(checkpoint)==checkpoint_hash
    assert sha(XI)==identity['native_source_sha256'], 'Native implementation changed during this run'
    report={'ok':True,'identity':identity,'status':'completed','budget_exhausted':cycle==args.max_cycles,'cycles':cycle,'updates_per_model':updates,'checkpoint':checkpoint.name,'checkpoint_sha256':checkpoint_hash,'initial_checkpoint_sha256':initial_hash,'protocol':{'readout':'Fixed p=(1-<Z_memory>)/2; zero trained output weights','measurement':'Analytic Born expectations and threshold classification, not finite-shot physical measurements','quantum_trainable_parameters':3,'classical_trainable_parameters':3,'quantum_memory_bits':args.groups,'ancillas_per_memory':3,'component_width':4,'mps':False,'gradient':'Native XI central finite difference; repeated gates are not treated with an invalid single-use parameter shift','optimizer':'Native XI SGD; noise learning rate normalized by its reuse count','training_delays':list(range(7)),'test_delays':[2,8,12],'generated_data_and_labels':'Native XI; query circuit never reads target cells','seed_splits':['train','validation','test'],'classical_state':'Two scalar states per association; all the same supplied inputs','timings':'Exploratory single-host CPU timings, not a quantum speedup benchmark'},'history':history,'test':{'trained_quantum':test,'frozen_angles':frozen_test,'memory_erased':erased,'trained_classical':classical},'barrier_passed':test['accuracy']>=.95 and test['accuracy']-frozen_test['accuracy']>=.15 and erased['accuracy']<=.60,'quantum_advantage_claimed':False,'wall_seconds_this_run':time.monotonic()-started}
    atomic(out/'report.json',report);head['status']='completed';head['barrier_passed']=report['barrier_passed'];head['active_checkpoint']=checkpoint.name if report['barrier_passed'] else None;atomic(manifest,head)
    print(json.dumps({'completed':True,'barrier_passed':report['barrier_passed'],'quantum':test['accuracy'],'frozen':frozen_test['accuracy'],'erased':erased['accuracy'],'classical':classical['accuracy'],'report':str(out/'report.json')}),flush=True)
    return report


def main():
    p=argparse.ArgumentParser(description='Bounded autonomous quantum-memory experiment')
    sub=p.add_subparsers(dest='command',required=True)
    a=sub.add_parser('auto');a.add_argument('output');a.add_argument('--runtime',required=True);a.add_argument('--groups',type=int,default=250,choices=range(1,251));a.add_argument('--seed',type=int,default=181173);a.add_argument('--max-cycles',type=int,default=8,choices=range(1,33));a.add_argument('--steps-per-cycle',type=int,default=10,choices=range(1,101));a.add_argument('--resume',action='store_true')
    s=sub.add_parser('status');s.add_argument('output')
    b=sub.add_parser('prepare');b.add_argument('output');b.add_argument('--runtime',required=True)
    args=p.parse_args()
    if args.command=='status':print(json.dumps(json.loads((Path(args.output)/'HEAD.json').read_text()),ensure_ascii=False,indent=2))
    elif args.command=='prepare':
        target=Path(args.output).resolve()
        if target.exists():raise ValueError('Choose a new memory session; existing models are preserved')
        release=ROOT/'integration/qmemory/release';m=json.loads((release/'manifest.json').read_text())
        if sha(XI)!=m['native_source_sha256']:raise ValueError('Release requires its original native source')
        compressed=release/m['file']
        if Path(m['file']).name!=m['file'] or compressed.stat().st_size>5*1024*1024:raise ValueError('Invalid release file')
        if sha(compressed)!=m['gzip_sha256']:raise ValueError('Release archive hash mismatch')
        with gzip.open(compressed,'rb') as f:data=f.read(16*1024*1024+1)
        if len(data)>16*1024*1024 or hashlib.sha256(data).hexdigest()!=m['checkpoint_sha256']:raise ValueError('Release checkpoint hash mismatch')
        runtime=Path(args.runtime).resolve()
        for name in ['build/reverse_pc','build/xi_session']:
            if not (runtime/name).is_file():raise ValueError('Compile the pinned XI runtime first')
        target.parent.mkdir(parents=True,exist_ok=True)
        import tempfile,shutil
        stage=Path(tempfile.mkdtemp(prefix='.qmemory-prepare-',dir=target.parent))
        try:
            (stage/'trained.rvp').write_bytes(data)
            with Engine(runtime,stage/'trained.rvp') as e:
                result=e.episode(0,seed(181173,'release-check',0),8)
                if result['correct']<.95*250:raise ValueError('Release did not reproduce under this runtime')
            identity={**m['identity'],'runtime_sha256':sha(runtime/'build/xi_session'),'controller_sha256':sha(__file__)}
            report_file=release/'training-report.json'
            if sha(report_file)!=m['training_report_sha256']:raise ValueError('Release report hash mismatch')
            report=json.loads(report_file.read_text());report['checkpoint']='trained.rvp';report['identity']=identity
            atomic(stage/'report.json',report)
            atomic(stage/'HEAD.json',{'identity':identity,'status':'completed','checkpoint':'trained.rvp','active_checkpoint':'trained.rvp','checkpoint_sha256':m['checkpoint_sha256'],'barrier_passed':True,'cycles':m['cycles'],'updates':m['updates_per_model'],'history':[]})
            if target.exists():raise ValueError('Destination appeared; refusing overwrite')
            stage.rename(target)
        finally:
            if stage.exists():shutil.rmtree(stage)
        print(json.dumps({'ok':True,'session':str(target),'qubits':1000,'checkpoint_sha256':m['checkpoint_sha256'],'experimental_binary_memory':True}))
    else:auto(args)

if __name__=='__main__':main()
