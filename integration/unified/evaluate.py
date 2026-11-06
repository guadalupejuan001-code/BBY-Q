#!/usr/bin/env python3
"""Reserved full-pipeline transfer tasks and causal component controls.

The independent verifier creates labels in a separate native process. Labels
never enter Session.turn or the shared inference workspace.
"""
import argparse,concurrent.futures,hashlib,json,random,tempfile
from contextlib import ExitStack
from types import SimpleNamespace
from pathlib import Path
from .common import ROOT,C1,Entity,A,encoded,digest,read,write,run,metrics,entity_models,integer
from .session import Session,perception_model
from . import perception as P

def reserved(count,namespace=2026110705):
    rng=random.Random(namespace);rows=[]
    for i in range(count):
        seed=int.from_bytes(hashlib.sha256(f'U01:reserved:{namespace}:{i}'.encode()).digest()[:4],'little')&0x7fffffff
        name=['Órbita Prisma','Nube Índigo','Ñandú Boreal','Ámbar Naciente'][i%4]+' '+str(i)
        association=['Viento Jade','Estrella Lejana','Bruma Ébano'][i%3]+' '+str(i)
        bit=rng.randrange(2);position=1+rng.randrange(5)
        prompt=f'guarda la regla {association} con valor {bit} observa {name} con muestra {seed} y resuelve desde {position}'
        rows.append({'index':i,'seed':seed,'bit':bit,'position':position,'prompt':prompt,'name':name,'association':association})
    return rows

def worker(rows,readers):
    result=[]
    with tempfile.TemporaryDirectory(prefix='bbyq-unified-reserved-') as temporary:
        directory=Path(temporary);verifier=directory/'verifier.rvp';verifier.write_bytes(entity_models()['v3'])
        with Session(directory/'entity.sqlite',readers) as session,C1.XiSession(C1.RT/'build/xi_session',verifier) as native:
            def parameters(suffix):
                banks=session._banks()
                with ExitStack() as stack:
                    states={}
                    for name in ('v3','memory','voice','entity'):
                        path=directory/(name+'-'+suffix+'.rvp');path.write_bytes(banks[name]);states[name]=stack.enter_context(C1.XiSession(C1.RT/'build/xi_session',path))
                    result=Entity.Entity.identities(SimpleNamespace(sessions=states))
                    if integer(states['v3'],P.B)==P.MAGIC:result['perception_readout']=P.parameter_identity(states['v3'])
                    return result
            initial=parameters('before')
            for index,row in enumerate(rows):
                value=session.turn('reserved-'+str(row['index']),row['prompt'])
                task=value['results'][-1] if value['results'] else {};ops={t['operation'] for t in value.get('trace',[])}
                gold=int(metrics(run(native,f'store64 {A+256} {row["seed"]}\nstore64 {A+272} 0\nfstore {A+296} .1\ncall vqc_sample\nfload f0 {A+128}\nfemit label f0'))['label'])
                goal=(gold^row['bit'])*6;action=0 if goal<row['position'] else 1
                stages={'c1_encode_input/c1_next','qm_exchange','qm_read','vqc_forward','entity_infer','qrl_step','entity_decide','qchat_encode/qchat_next','entity_voice_check'}
                result.append({**row,'expected_class':gold,'expected_goal':goal,'expected_action':action,'correct':bool(value['ok'] and value['committed'] and task.get('action')==action and task.get('voice',{}).get('faithful')),'all_stages_executed':stages<=ops,'result':value})
                if (index+1)%10==0:print(json.dumps({'worker_progress':index+1,'worker_total':len(rows)},ensure_ascii=False),flush=True)
            assert session.snapshot()['tasks']==len(rows),'A full task failed to commit'
            assert parameters('after')==initial,'Reserved evaluation changed trained quantum parameters'
    return result

def controls(readers):
    def probe(control,sample,bit):
        with tempfile.TemporaryDirectory(prefix='bbyq-unified-ablation-') as temporary,Session(Path(temporary)/'entity.sqlite',readers) as session:
            prompt=f'guarda la regla Faro Azul con valor {bit} observa Nara con muestra {sample} y resuelve desde 3'
            baseline=session.turn('baseline',prompt)['results'][-1]
            value=session.turn('control',prompt,control=control);task=value['results'][-1]
            return {'control':control or 'intact','sample':sample,'action':task.get('action'),'goal':task.get('goal'),'voice':task.get('voice'),'ok':value['ok'],'committed':value['committed'],'trace':value['trace'],'baseline':{'action':baseline['action'],'goal':baseline['goal'],'voice':baseline['voice']}}
    rows=[]
    for control in (None,'memory-erased','vqc-ablated','qrl-ablated','voice-ablated'):
        if control=='vqc-ablated':
            # Erasing all observables produces one constant input. Probe both
            # fixed opposite classes, retaining both outcomes, so a learned
            # readout's constant response cannot invalidate the control.
            probes=[probe(control,88113,1),probe(control,88114,0)]
            for value in probes:value['causal_effect']=value['goal']!=value['baseline']['goal']
            assert any(value['causal_effect'] for value in probes),'VQC ablation did not affect either shared premise'
            value=dict(next(value for value in probes if value['causal_effect']));value['probes']=probes;rows.append(value)
        else:rows.append(probe(control,88113,1))
    for row in rows[1:]:
        intact=row['baseline'];row['causal_effect']=row['action']!=intact['action'] or row['voice']!=intact['voice'] or not row['ok']
        if row['control']=='vqc-ablated':assert row['goal']!=intact['goal'],'VQC control did not change the shared premise'
        assert row['causal_effect'],row
    return rows

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--readers',type=Path,default=ROOT/'integration/unified/release');parser.add_argument('--count',type=int,default=200);parser.add_argument('--workers',type=int,default=4);parser.add_argument('--seed',type=int,default=2026110705);parser.add_argument('--integration-only',action='store_true',help='Still report every prediction error; use native integration execution as the exit criterion');parser.add_argument('--output',type=Path,default=ROOT/'build/unified/reserved.json');args=parser.parse_args()
    if args.count<1 or args.workers<1:raise ValueError('Positive task and worker counts required')
    rows=reserved(args.count,args.seed);groups=[rows[i::args.workers] for i in range(args.workers)]
    with tempfile.TemporaryDirectory(prefix='bbyq-u02-evaluation-binding-') as temporary:
        path=Path(temporary)/'v3.rvp';path.write_bytes(perception_model(args.readers) or entity_models()['v3'])
        with C1.XiSession(C1.RT/'build/xi_session',path) as native:
            readout_identity=P.parameter_identity(native) if integer(native,P.B)==P.MAGIC else None
    with concurrent.futures.ThreadPoolExecutor(max_workers=args.workers) as pool:
        batches=list(pool.map(lambda group:worker(group,args.readers),groups))
    cases=sorted([row for batch in batches for row in batch],key=lambda r:r['index']);correct=sum(row['correct'] for row in cases);all_stages=sum(row['all_stages_executed'] for row in cases)
    report={'passed':correct==len(cases) and all_stages==len(cases),'integration_passed':all_stages==len(cases),'tasks':len(cases),'correct':correct,'accuracy':correct/len(cases),'all_stages_executed':all_stages,'reserved_seed':args.seed,'perception_parameter_sha256':readout_identity,'test_kind':'new names, seeds, binary rules and nonterminal positions; declared native environment and supported grammar','source':'every task enters Session.turn as one natural-language request; no test feedback','controls':controls(args.readers),'cases':cases,'apk_built':False}
    args.output.parent.mkdir(parents=True,exist_ok=True);write(args.output,report);print(json.dumps({k:v for k,v in report.items() if k!='cases'},ensure_ascii=False))
    if not (report['integration_passed'] if args.integration_only else report['passed']):raise SystemExit(1)

if __name__=='__main__':main()
