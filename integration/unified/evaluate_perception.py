#!/usr/bin/env python3
"""Independent held-out classification using 1000 transported observations.

The environment and its label live in a different native process. The model
receives numeric observations, never the environment's seed or teacher.
"""
import argparse,hashlib,json,statistics,struct,tempfile
from pathlib import Path
from .common import ROOT,C1,A,encoded,digest,read,write,entity_models,run as environment_run,material,metrics,integer
from .session import perception_model
from .upgrades import bank_parameters
from .train_head import seed as training_seed
from . import perception as P

def seed(namespace,tag,index):return int.from_bytes(hashlib.sha256(f'U02:classification:{namespace}:{tag}:{index}'.encode()).digest()[:4],'little')&0x7fffffff

def evaluate(readers,count=1024,noise=.1,namespace=2026110602,tag='fresh-iid'):
    protocol=read(Path(readers)/'readout-training-protocol.json')
    training={training_seed('train',i) for i in range(protocol['training_examples'])}
    validation={training_seed(split,i) for split in protocol['validation_splits'] for i in range(protocol['validation_examples_per_split'])}
    seeds=[seed(namespace,tag,i) for i in range(count)]
    assert len(set(seeds))==count and not set(seeds)&(training|validation)
    rows=[]
    with tempfile.TemporaryDirectory(prefix='bbyq-u02-external-test-') as temporary:
        directory=Path(temporary);candidate=directory/'candidate.rvp';environment=directory/'environment.rvp'
        candidate.write_bytes(perception_model(readers));environment.write_bytes(entity_models()['v3'])
        with C1.XiSession(C1.RT/'build/xi_session',candidate) as model,C1.XiSession(C1.RT/'build/xi_session',environment) as verifier:
            before={'base':bank_parameters(model),'readout':P.parameter_identity(model),'updates':integer(model,P.B+24),'samples':integer(model,P.B+32)}
            for index,current in enumerate(seeds):
                body=f'store64 {A+256} {current}\nstore64 {A+272} 0\nfstore {A+296} {noise}\ncall vqc_sample\nmem_materialize {A+300000} 8000\nfload f0 {A+128}\nfemit label f0'
                events=environment_run(verifier,body)
                raw=bytes.fromhex(next(event['hex'] for event in events if event.get('type')=='memory_materialization'))
                values=list(struct.unpack('<'+'d'*1000,raw))
                body=P.stage(A+300000,values)+f'fstore {A+128} -999\nstore64 {A+256} 0\n'+P.stage(A+600,[0.]*4)
                body+=f'store64 {A} 0\nstore64 {A+280} 0\ncall select_agent\ncall forward\nfemit baseline f21\ncall u2_apply\nfemit probability f21'
                predictions=metrics(P.run(model,body));label=int(metrics(events)['label']);probability=float(predictions['probability']);baseline=float(predictions['baseline'])
                # A paired control reads the same state and Z expectations,
                # replacing only the additional X observation by zero.
                ablated=P.x_ablated_library()
                source=f'#!reverse-pc-machine-v1\nbudget 100000000\nfload f20 {A+112}\ncall u2_apply\nfemit p f21\nhalt\n'+ablated
                ablated_probability=float(metrics(model.execute(source)[0])['p'])
                rows.append({'index':index,'verifier_seed':current,'input_sha256':digest(raw),'label':label,'probability':probability,'base_probability':baseline,'x_ablated_probability':ablated_probability,'correct':int(probability>=.5)==label,'base_correct':int(baseline>=.5)==label,'x_ablated_correct':int(ablated_probability>=.5)==label})
                if (index+1)%128==0:print({'classification_holdout':tag,'completed':index+1,'total':count},flush=True)
            after={'base':bank_parameters(model),'readout':P.parameter_identity(model),'updates':integer(model,P.B+24),'samples':integer(model,P.B+32)}
            assert before==after,'Classification evaluation trained or changed model parameters'
    correct=sum(row['correct'] for row in rows);old_correct=sum(row['base_correct'] for row in rows);floor=.995 if noise==.1 else .99
    ablated_correct=sum(row['x_ablated_correct'] for row in rows)
    return {'passed':correct/count>=floor,'correct':correct,'total':count,'accuracy':correct/count,'minimum_accuracy':floor,'brier':statistics.fmean((row['probability']-row['label'])**2 for row in rows),'base_correct':old_correct,'base_accuracy':old_correct/count,'base_brier':statistics.fmean((row['base_probability']-row['label'])**2 for row in rows),'x_ablated_correct':ablated_correct,'x_ablated_accuracy':ablated_correct/count,'ablation':'same state, Z observations and parameters; additional X observations zeroed','namespace':namespace,'tag':tag,'noise':noise,'input':'all 1000 external numeric observations; no generator seed or teacher passed to the model','parameter_identity':before,'no_test_learning':True,'cases':rows,'apk_built':False}

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--readers',type=Path,default=ROOT/'integration/unified/release');parser.add_argument('--count',type=int,default=1024);parser.add_argument('--noise',type=float,default=.1);parser.add_argument('--seed',type=int,default=2026110602);parser.add_argument('--tag',default='fresh-iid');parser.add_argument('--output',type=Path,default=ROOT/'build/unified/classification-test.json');args=parser.parse_args()
    report=evaluate(args.readers,args.count,args.noise,args.seed,args.tag);args.output.parent.mkdir(parents=True,exist_ok=True);write(args.output,report);print(json.dumps({k:v for k,v in report.items() if k!='cases'},ensure_ascii=False))
    if not report['passed']:raise SystemExit(1)

if __name__=='__main__':main()
