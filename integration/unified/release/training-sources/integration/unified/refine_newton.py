#!/usr/bin/env python3
"""Finish the native readout fit with full-training-set damped Newton steps.

Python compiles and transports XI instructions. Gradients, curvature,
Cholesky solve and coefficient updates all execute in the native runtime.
"""
import argparse,json,shutil,time
from pathlib import Path
from .common import ROOT,C1,read,write,entity_models,integer
from . import perception as P
from .train_head import stage_rows,evaluate,export,base_identity

H=P.B+50000;L=P.B+60000;Y=P.B+64000;DELTA=P.B+65000

def feature(index,register):
    return f'fset f{register} 1\n' if index==P.W1 else f'fload f{register} {P.ADDR["NORMAL"]+8*index}\n'

def system(native,rows,indices,damping=.0001):
    """Build sum Hessian and gradient, using training cache teachers only."""
    size=len(indices);P.run(native,P.stage(H,[0.]*(size*(size+1))))
    for first in range(0,len(rows),256):
        chunk=rows[first:first+256];body=stage_rows(chunk,teachers=True)
        for case in range(len(chunk)):
            address=P.ADDR['CACHE']+case*P.STRIDE
            body+=f'store64 {P.B+112} {address}\ncall u2_load_features\ncall u2_forward\nfload f22 {P.B+72}\nfmov f23 f22\nfload f0 {address+200}\nfsub f23 f0\nfset f24 1\nfsub f24 f22\nfmul f24 f22\nfload f25 {P.B+88}\nfmul f23 f25\nfmul f24 f25\n'
            for i,index in enumerate(indices):
                body+=feature(index,0)+f'fmul f0 f23\nfload f1 {H+8*(i*(size+1)+size)}\nfadd f1 f0\nfstore {H+8*(i*(size+1)+size)} f1\n'
                for j,other in enumerate(indices):
                    cell=H+8*(i*(size+1)+j)
                    body+=feature(index,0)+feature(other,1)+f'fmul f0 f1\nfmul f0 f24\nfload f1 {cell}\nfadd f1 f0\nfstore {cell} f1\n'
        P.run(native,body)
    P.run(native,''.join(f'fload f0 {H+8*(i*(size+1)+i)}\nfadd f0 {damping}\nfstore {H+8*(i*(size+1)+i)} f0\n' for i in range(size)))
    return P.floats(native,H,size*(size+1))

def solve(native,indices,step=1.):
    """Native Cholesky, triangular solves, then theta -= step * delta."""
    size=len(indices);body=''
    for i in range(size):
        for j in range(i+1):
            body+=f'fload f0 {H+8*(i*(size+1)+j)}\n'
            for k in range(j):body+=f'fload f1 {L+8*(i*size+k)}\nfload f2 {L+8*(j*size+k)}\nfmul f1 f2\nfsub f0 f1\n'
            if i==j:body+='fmax f0 .000000000001\nfsqrt f0 f0\n'
            else:body+=f'fload f1 {L+8*(j*size+j)}\nfdiv f0 f1\n'
            body+=f'fstore {L+8*(i*size+j)} f0\n'
    for i in range(size):
        body+=f'fload f0 {H+8*(i*(size+1)+size)}\n'
        for k in range(i):body+=f'fload f1 {L+8*(i*size+k)}\nfload f2 {Y+8*k}\nfmul f1 f2\nfsub f0 f1\n'
        body+=f'fload f1 {L+8*(i*size+i)}\nfdiv f0 f1\nfstore {Y+8*i} f0\n'
    for i in reversed(range(size)):
        body+=f'fload f0 {Y+8*i}\n'
        for k in range(i+1,size):body+=f'fload f1 {L+8*(k*size+i)}\nfload f2 {DELTA+8*k}\nfmul f1 f2\nfsub f0 f1\n'
        body+=f'fload f1 {L+8*(i*size+i)}\nfdiv f0 f1\nfstore {DELTA+8*i} f0\n'
    for i,index in enumerate(indices):body+=f'fload f0 {DELTA+8*i}\nfmul f0 {step}\nfload f1 {P.ADDR["P"]+8*index}\nfsub f1 f0\nfstore {P.ADDR["P"]+8*index} f1\n'
    body+=f'load64 r0 {P.B+24}\nadd r0 1\nstore64 {P.B+24} r0'
    P.run(native,body)

def main():
    parser=argparse.ArgumentParser();parser.add_argument('previous',type=Path);parser.add_argument('folder',type=Path);parser.add_argument('--iterations',type=int,default=30);args=parser.parse_args()
    previous=args.previous;folder=args.folder;folder.mkdir(parents=True,exist_ok=True);parent=read(previous/'selection.json')
    checkpoint=previous/parent.get('path',parent['checkpoint']);assert C1.sha(checkpoint)==parent['sha256']
    protocol=read(previous/'protocol.json');protocol.update({'continuation_of':{'epoch':parent['epoch'],'checkpoint_sha256':C1.sha(checkpoint),'selection_sha256':C1.sha(previous/'selection.json')},'optimizer':'XI Adam warm-up followed by full-training-set damped Newton; native curvature and Cholesky solve','native_newton_iterations_max':args.iterations,'native_hessian_damping':.0001,'selection':'minimum validation Brier among eligible models after the complete registered optimization budget; no first-eligible early stop'})
    write(folder/'protocol.json',protocol)
    for name in ('configuration.json','baseline.json'):shutil.copyfile(previous/name,folder/name)
    hashes=read(previous/'training-sources.json')
    for name,sha in hashes.items():
        source=previous/'sources'/name;assert C1.sha(source)==sha
        target=folder/'sources'/name;target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(source,target)
    source='integration/unified/refine_newton.py';hashes[source]=C1.sha(ROOT/source)
    target=folder/'sources'/source;target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(ROOT/source,target);write(folder/'training-sources.json',hashes)
    def rows(split):return [json.loads(line) for line in (previous/(split+'-features.jsonl')).read_text().splitlines()]
    train=rows('train');validation={name:rows(name) for name in protocol['validation_splits']};candidates=[];best=None
    original=folder/'original.rvp';original.write_bytes(entity_models()['v3'])
    with C1.XiSession(C1.RT/'build/xi_session',checkpoint) as native:
        assert integer(native,P.B)==P.MAGIC and integer(native,P.B+8)==P.NF
        parameters=base_identity(native);indices=read(folder/'configuration.json')['training_feature_selection']['selected_features']+[P.W1]
        # Later online Adam starts with clean moments after Newton changes
        # the optimization scale. Learned inference coefficients are retained.
        P.run(native,P.stage(P.ADDR['MOM'],[0.]*P.NP)+P.stage(P.ADDR['VAR'],[0.]*P.NP)+f'fstore {P.B+48} 1\nfstore {P.B+56} 1')
        for iteration in range(1,args.iterations+1):
            started=time.perf_counter();epoch=parent['epoch']+iteration
            system(native,train,indices);solve(native,indices)
            P.run(native,f'load64 r0 {P.B+32}\nadd r0 {len(train)}\nstore64 {P.B+32} r0')
            results={name:evaluate(native,data) for name,data in validation.items()};iid=results['validation-iid'];ood=results['validation-ood'];minimum=min(row['accuracy'] for row in results.values());brier=sum(row['brier'] for row in results.values())/len(results)
            eligible=iid['correct']==iid['total'] and ood['accuracy']>=.99 and brier<=.01
            entry={'epoch':epoch,'newton_iteration':iteration,'minimum_accuracy':minimum,'mean_brier':brier,'eligible':eligible,'parameter_sha256':P.parameter_identity(native),'validation':{name:{k:v for k,v in value.items() if k!='cases'} for name,value in results.items()}}
            write(folder/f'validation-{epoch:03}.json',results);candidates.append(entry)
            print({**entry,'seconds':round(time.perf_counter()-started,2)},flush=True)
            if best is None or (eligible,-brier)>(best['eligible'],-best['mean_brier']):
                destination=folder/f'candidate-{epoch:03}.rvp';native.save(destination);entry.update(checkpoint=destination.name,checkpoint_sha256=C1.sha(destination));best=dict(entry);write(folder/'selection.json',best)
            write(folder/'candidates.json',candidates)
        assert base_identity(native)==parameters
    with C1.XiSession(C1.RT/'build/xi_session',folder/best['checkpoint']) as native:export(native,original,folder/'perception.rvp')
    best.update(path='perception.rvp',sha256=C1.sha(folder/'perception.rvp'),preserved_original_parameters=parameters);write(folder/'selection.json',best);print({'selected':best},flush=True)

if __name__=='__main__':main()
