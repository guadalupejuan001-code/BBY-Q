#!/usr/bin/env python3
"""Reproducible corpus orchestration; all predictions and SGD run in XI."""
import argparse
import collections
import json
from pathlib import Path
import random
import subprocess
import time
from data import corpus,fresh_questions
from engine import A,BANK,STRIDE,FEATURES,Native,source,stage,words,normalize,bits,examples,evaluate,sha

def main():
    p=argparse.ArgumentParser();p.add_argument('--runtime',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
    p.add_argument('--epochs',type=int,default=50);p.add_argument('--seed',type=int,default=20261104)
    p.add_argument('--initial',type=Path)
    p.add_argument('--corpus',type=Path)
    p.add_argument('--history-policy',choices=['all','frequency'],default='all')
    args=p.parse_args();out=args.output.resolve();out.mkdir(parents=True,exist_ok=True)
    if any(out.iterdir()):raise ValueError('Choose an empty output directory; models are preserved')
    assert 1<=args.epochs<=1000,'Epochs must be in 1..1000'
    data=json.loads(args.corpus.read_text()) if args.corpus else corpus()
    data.setdefault('test_scope','held-out phrasings in the supplied corpus; not proof of new factual knowledge')
    assert data['train'] and data['heldout'],'Separate training and evaluation examples are required'
    vocabulary={t for r in data['train'] for t in words(r['response'])}
    base=json.loads((args.initial.parent/'vocabulary.json').read_text()) if args.initial else ['<eos>','<unk>','<bos>']
    vocab=base+sorted(vocabulary-set(base))
    assert len(vocab)<=128,('Vocabulary exceeds native tree',len(vocab))
    frequency=collections.Counter(t for r in data['train'] for s in [r['input'],r.get('previous','')] for t in words(normalize(s)))
    lex=set(frequency);history_lex=lex if args.history_policy=='all' else {t for t,n in frequency.items() if n<10}
    rows=examples(data['train'],vocab,lex,history_lex)
    print(json.dumps({'stage':'corpus','vocabulary':len(vocab),'conversations':len(data['train']),'token_contexts':len(rows),'heldout':len(data['heldout'])}),flush=True)
    (out/'corpus.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')
    (out/'vocabulary.json').write_text(json.dumps(vocab,ensure_ascii=False)+'\n')
    (out/'input-vocabulary.json').write_text(json.dumps(sorted(lex),ensure_ascii=False)+'\n')
    (out/'history-vocabulary.json').write_text(json.dumps(sorted(history_lex),ensure_ascii=False)+'\n')
    runtime=args.runtime.resolve();empty=out/'empty.rvp'
    if args.initial:
        empty.write_bytes(args.initial.read_bytes())
    else:subprocess.run([runtime/'build/reverse_pc','init',empty],check=True,capture_output=True)
    started=time.perf_counter();milestones=[];rng=random.Random(args.seed)
    with Native(runtime,empty) as model:
        events,_=model.execute(f'load64 r0 {A+24}\nprint r0');initial_updates=next(e['value'] for e in events if e.get('type')=='register')
        model.execute(f'store64 {A} 100\nstore64 {A+8} {len(vocab)}\nfstore {A+32} .1\n')
        for first in range(0,len(rows),32):
            body=''
            for i,(raw,label) in enumerate(rows[first:first+32],first):
                body+=stage(raw)+f'store64 {A+48} {label}\nstore64 {A+72} {BANK+i*STRIDE}\ncall qchat_encode\ncall qchat_cache\n'
            model.execute(body)
        model.save(out/'initial.rvp')
        print(json.dumps({'stage':'features_cached','seconds':time.perf_counter()-started}),flush=True)
        initial=evaluate(runtime,out/'initial.rvp',data['heldout'],vocab,input_vocabulary=lex,history_vocabulary=history_lex)
        print(json.dumps({'stage':'initial','accuracy':initial['exact_response_accuracy']}),flush=True)
        for epoch in range(1,args.epochs+1):
            order=list(range(len(rows)));rng.shuffle(order);loss=[]
            for first in range(0,len(order),128):
                body=''.join(f'store64 {A+72} {BANK+i*STRIDE}\ncall qchat_load_case\ncall qchat_train\n' for i in order[first:first+128])
                events,_=model.execute(body)
                loss += [e['value'] for e in events if e.get('type')=='metric' and e.get('name')=='nll']
            if epoch%10==0 or epoch==1 or epoch==args.epochs:
                model.save(out/f'epoch-{epoch:03}.rvp')
                validation=evaluate(runtime,out/f'epoch-{epoch:03}.rvp',data['heldout'],vocab,input_vocabulary=lex,history_vocabulary=history_lex)
                record={'epoch':epoch,'mean_training_nll':sum(loss)/len(loss),'heldout_exact_accuracy':validation['exact_response_accuracy'],'elapsed_seconds':time.perf_counter()-started}
                milestones.append(record);print(json.dumps(record),flush=True)
        # Remove training feature rows from the deployable state. The inference
        # program has no answer table and consults only weights and vocabulary.
        for first in range(0,len(rows),128):
            body=''
            for i in range(first,min(first+128,len(rows))):
                body+=f'set r5 {BANK+i*STRIDE}\nset r6 {BANK+i*STRIDE+FEATURES+1}\nlabel clean_{i}\nstore8 $r5 0\nadd r5 1\ncmp r5 r6\njlt clean_{i}\n'
            model.execute(body)
        model.save(out/'trained.rvp');usage=model.s.metrics()
        events,_=model.execute(f'load64 r0 {A+24}\nprint r0');total_updates=next(e['value'] for e in events if e.get('type')=='register')
    options={'input_vocabulary':lex,'history_vocabulary':history_lex}
    trained=evaluate(runtime,out/'trained.rvp',data['heldout'],vocab,**options)
    train_result=evaluate(runtime,out/'trained.rvp',data['train'],vocab,**options)
    ablated=evaluate(runtime,out/'trained.rvp',data['heldout'],vocab,mode=1,**options)
    control=evaluate(runtime,out/'trained.rvp',data['heldout'],vocab,mode=2,**options)
    seen={tuple(bits(r['input'],[],r.get('previous',''),lex,history_lex)) for r in data['train']}
    candidates=data.get('fresh_questions',fresh_questions() if not args.corpus else data['heldout'])
    fresh=[r for r in candidates if tuple(bits(r['input'],[],r.get('previous',''),lex,history_lex)) not in seen]
    fresh_result=evaluate(runtime,out/'trained.rvp',fresh,vocab,**options)
    assert [r['tokens'] for r in control['cases']]==[r['tokens'] for r in trained['cases']]
    report={'ok':True,'architecture':'100 exact Clifford qubits + native XI hierarchical-softmax readout','qubits':100,'native_pauli_observables':100,
            'classical_product_features':768,'vocabulary':len(vocab),'tree_depth':7,'epochs':args.epochs,'training_conversations':len(data['train']),
            'training_token_contexts':len(rows),'training_updates':total_updates,'initial_training_updates':initial_updates,
            'new_training_updates':len(rows)*args.epochs,'seed':args.seed,'milestones':milestones,
            'initial_heldout':initial,'trained_heldout':trained,'trained_training':train_result,'ablated_quantum_features':ablated,
            'fresh_questions':fresh_result,'analytic_control_identical':True,'quantum_advantage_claimed':False,'mps':False,'state_arithmetic':'exact Clifford integer/sign algebra',
            'readout_arithmetic':'binary64 SGD in XI','circuit_parameters_trained':False,'readout_trained':True,
            'scope':data['test_scope'],'checkpoint_bytes':(out/'trained.rvp').stat().st_size,'checkpoint_sha256':sha(out/'trained.rvp'),
            'initial_checkpoint_sha256':sha(args.initial) if args.initial else None,
            'source_sha256':{name:sha(Path(__file__).resolve().parent/name) for name in ['data.py','engine.py','train.py']},
            'xi_sha256':sha(Path(__file__).resolve().parents[2]/'ai/xi/qchat100/model.xi'),
            'elapsed_seconds':time.perf_counter()-started,'native_usage':usage}
    (out/'training-report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({k:v for k,v in report.items() if k not in ['initial_heldout','trained_heldout','trained_training','ablated_quantum_features','milestones']}),flush=True)

if __name__=='__main__':main()
