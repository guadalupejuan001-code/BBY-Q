#!/usr/bin/env python3
"""Compare the independent closed-form XI baseline with simulated circuits."""
import argparse
import json
from pathlib import Path
import struct
from types import SimpleNamespace
from campaign import A, Experiment, metrics

parser=argparse.ArgumentParser()
parser.add_argument('--runtime',required=True)
parser.add_argument('--session-binary')
parser.add_argument('--checkpoint',required=True)
parser.add_argument('--output',required=True)
args=parser.parse_args()
out=Path(args.output).resolve();out.parent.mkdir(parents=True,exist_ok=True)
shared=dict(runtime=args.runtime,session_binary=args.session_binary,step_budget=10000000,
            agent='vqc',task='dense',seed=173,episodes=20,eval_size=8,output=str(out.parent/'analytic-fixture'),
            resume=False,joint_mode='independent',initial_checkpoint=None)
q=Experiment(SimpleNamespace(**shared,classical=False,analytic=False))
c=Experiment(SimpleNamespace(**shared,classical=True,analytic=True))
errors=[]
with q.Session(q.binary,Path(args.checkpoint).resolve()) as qs, c.Session(c.binary,Path(args.checkpoint).resolve()) as cs:
    for sample in range(8):
        values=[]
        for e,s in [(q,qs),(c,cs)]:
            body=e.stage('iid',sample)+f'\nmem_materialize {A+310000} 8000'
            events,_=s.execute(e.source(body))
            z=struct.unpack('<1000d',bytes.fromhex(next(x['hex'] for x in events if x['type']=='memory_materialization')))
            values.append((z,metrics(events)['probability']))
        errors += [abs(a-b) for a,b in zip(values[0][0],values[1][0],strict=True)]
        errors.append(abs(values[0][1]-values[1][1]))
    assert max(errors)<1e-11,'closed form disagrees with actual circuit'
    traces=[]
    for e,s in [(q,qs),(c,cs)]:
        events,_=s.execute(e.source('qtrace reset\n'+e.stage('iid',0)+'\nqtrace report'))
        traces.append(next(x for x in events if x['type']=='quantum_trace'))
    assert traces[0]['distinct_observed_qubits']==1000
    assert traces[1]['distinct_observed_qubits']==traces[1]['distinct_rotated_qubits']==0
    # Same labels/optimizer; compare actual learned theta and weights, not just
    # inference from a fixed model. Floating operation ordering may differ.
    for ep in range(10):
        qs.execute(q.source(q.stage('train',ep,training=True)))
        cs.execute(c.source(c.stage('train',ep,training=True)))
    parameters=[]
    for e,s in [(q,qs),(c,cs)]:
        events,_=s.execute(e.source(f'mem_materialize {A+100000} 8000\nmem_materialize {A+110000} 8000'))
        parameters.append([v for row in events if row['type']=='memory_materialization'
                           for v in struct.unpack('<1000d',bytes.fromhex(row['hex']))])
    parameter_error=max(abs(a-b) for a,b in zip(*parameters,strict=True))
    assert parameter_error<1e-10,'equivalent optimizer updates diverged'
summary={'ok':True,'observations_compared':8000,'maximum_observation_or_probability_error':max(errors),
         'trained_parameter_max_error_after_10_examples':parameter_error,
         'quantum_trace':traces[0],'analytic_classical_trace':traces[1],
         'quantum_computational_advantage_demonstrated':False}
out.write_text(json.dumps(summary,indent=2)+'\n')
print(json.dumps(summary))
