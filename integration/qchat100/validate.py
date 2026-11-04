#!/usr/bin/env python3
"""Native feature causality, real SGD, checkpoint and conversation regression."""
import argparse
import json
from pathlib import Path
import random
import tempfile
import types
from engine import A,BANK,ROOT,Native,bits,stage,sha
from cli import prepare,run,load

def main():
    p=argparse.ArgumentParser();p.add_argument('--runtime',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
    a=p.parse_args();runtime=a.runtime.resolve();release=ROOT/'integration/qchat100/release'
    checks=0
    with tempfile.TemporaryDirectory(prefix='qchat100-validation-') as temp:
        root=Path(temp);session=root/'session'
        prepared=prepare(session,runtime,release);head,_,state=load(session);original=sha(state)
        assert prepared['qubits']==100 and prepared['training_updates']>0
        with Native(runtime,state) as n:
            rng=random.Random(632911)
            for _ in range(32):
                raw=[rng.randrange(2) for _ in range(100)]
                events,_=n.execute(stage(raw)+f'call qchat_encode\nmem_materialize {A+2000} 100\nstats\nqstats')
                material=next(e for e in events if e['type']=='memory_materialization')
                assert list(bytes.fromhex(material['hex']))==raw
                q=next(e for e in events if e['type']=='quantum_stats')
                assert q['clifford_components']==1 and q['norm']==1 and q['payload_bytes']==3300
                checks+=100
            # One real native SGD update must change readout parameters.
            raw=bits('hola',[],input_vocabulary=set(head['input_vocabulary']),history_vocabulary=set(head['history_vocabulary']))
            before,_=n.execute(f'mem_materialize {A+100000} 6944\nload64 r0 {A+24}\nprint r0')
            weights=next(e['hex'] for e in before if e['type']=='memory_materialization')
            count=next(e['value'] for e in before if e['type']=='register')
            n.execute(stage(raw)+f'store64 {A+80} 0\ncall qchat_encode\ncall qchat_active\nstore64 {A+48} {head["vocabulary"].index("hola")}\ncall qchat_train')
            after,_=n.execute(f'mem_materialize {A+100000} 6944\nload64 r0 {A+24}\nprint r0')
            assert next(e['hex'] for e in after if e['type']=='memory_materialization')!=weights
            assert next(e['value'] for e in after if e['type']=='register')==count+1
            n.save(root/'continued.rvp');checks+=2
        assert sha(state)==original
        expected={'hola':'Hola X.','quien eres':'Soy BBY Q.','cuantos cubits tienes':'Tengo cien cúbits.',
                  'que es memoria':'La memoria conserva información.','que es circuito':'Un circuito aplica puertas a los cúbits.',
                  'que es xi':'XI es nuestro lenguaje de instrucciones.'}
        replies=[]
        for prompt,target in expected.items():
            result=run(types.SimpleNamespace(command='ask',session=str(session),message=prompt,previous=''))
            assert result['text']==target,(prompt,result['text'])
            assert result['terminated'];replies.append({'input':prompt,'response':result['text']});checks+=1
        request=types.SimpleNamespace(command='turn',session=str(session),id='hello-1',message='hola')
        first=run(request);again=run(request);assert first==again;checks+=1
        saved=(session/'conversation.json').read_bytes()
        try:run(types.SimpleNamespace(command='turn',session=str(session),id='hello-1',message='quien eres'))
        except ValueError:pass
        else:raise AssertionError('Conflicting request ID accepted')
        assert (session/'conversation.json').read_bytes()==saved;checks+=1
        exported=root/'export.rvp';run(types.SimpleNamespace(command='export',session=str(session),output=str(exported)))
        assert sha(exported)==original and sha(state)==original;checks+=1
        reopened=run(types.SimpleNamespace(command='ask',session=str(session),message='quien eres',previous=''))
        assert reopened['text']=='Soy BBY Q.';checks+=1
        try:prepare(session,runtime,release)
        except ValueError:pass
        else:raise AssertionError('Existing session overwritten')
        assert sha(state)==original;checks+=1
        report={'ok':True,'checks':checks,'random_100_qubit_feature_vectors':32,'state_exactness':'Clifford','tolerance':0,
                'native_sgd_parameter_update_verified':True,'original_checkpoint_preserved':True,'reopen_verified':True,
                'quantum_advantage_claimed':False,'checkpoint_sha256':original,'examples':replies}
    a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(report,ensure_ascii=False,indent=2))

if __name__=='__main__':main()
