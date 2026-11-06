#!/usr/bin/env python3
"""Independent native VQC continuation, without training on the opened test."""
import argparse,hashlib,json
from pathlib import Path
from .common import ROOT,C1,A,encoded,digest,read,write,run,metrics,entity_models,material

def seed(split,index):return int.from_bytes(hashlib.sha256(f'U01:perception:2026110704:{split}:{index}'.encode()).digest()[:4],'little')&0x7fffffff
def sample(split,index):return f'store64 {A+256} {seed(split,index)}\nstore64 {A+280} 0\nstore64 {A+272} 0\nfstore {A+296} .1\ncall vqc_sample\nstore64 {A} 0\n'

def evaluate(path,count=256):
    rows=[]
    with C1.XiSession(C1.RT/'build/xi_session',path) as native:
        for i in range(count):
            values=metrics(run(native,sample('validation',i)+'call select_agent\ncall forward\nfemit probability f21\nfload f0 '+str(A+128)+'\nfemit label f0'))
            rows.append({'seed':seed('validation',i),**values})
    correct=sum(int(row['probability']>=.5)==int(row['label']) for row in rows)
    return {'correct':correct,'total':count,'accuracy':correct/count,'brier':sum((row['probability']-row['label'])**2 for row in rows)/count,'cases':rows}

def main():
    parser=argparse.ArgumentParser();parser.add_argument('folder',type=Path);args=parser.parse_args();folder=args.folder;folder.mkdir(parents=True,exist_ok=True)
    protocol={'seed':2026110704,'training_examples':2048,'checkpoints':[512,2048],'validation_examples':256,'selection':'highest independent validation accuracy, then lowest Brier; opened U01 reserved data are never supplied to training','learning_rate':.05,'teacher':'native synthetic environment only','apk_built':False}
    write(folder/'perception-protocol.json',protocol);initial=folder/'v3-original.rvp';initial.write_bytes(entity_models()['v3']);candidates=[]
    baseline=evaluate(initial);print({'baseline':{k:v for k,v in baseline.items() if k!='cases'}},flush=True);write(folder/'perception-baseline.json',baseline)
    with C1.XiSession(C1.RT/'build/xi_session',initial) as native:
        # Existing learned rotations and QRL parameters are preserved. Native
        # SGD continues the VQC readout and its established rotation schedule.
        run(native,f'fstore {A+4024} .05')
        for i in range(2048):
            run(native,sample('train',i)+'call supervised_update')
            if (i+1)%128==0:print({'training':i+1},flush=True)
            if i+1 in protocol['checkpoints']:
                path=folder/f'v3-{i+1:04}.rvp';native.save(path);validation=evaluate(path);write(folder/f'perception-validation-{i+1:04}.json',validation)
                entry={'path':path.name,'sha256':C1.sha(path),'updates':i+1,**{k:v for k,v in validation.items() if k!='cases'}};candidates.append(entry);print(entry,flush=True);write(folder/'perception-candidates.json',candidates)
    accepted=[item for item in candidates if item['accuracy']>=baseline['accuracy'] and item['brier']<=baseline['brier']]
    selected=max(accepted,key=lambda item:(item['accuracy'],-item['brier'])) if accepted else {'path':initial.name,'sha256':C1.sha(initial),'updates':0,**{k:v for k,v in baseline.items() if k!='cases'}}
    write(folder/'perception-selected.json',selected);print({'selected':selected},flush=True)

if __name__=='__main__':main()
