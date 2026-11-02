#!/usr/bin/env python3
"""Simulation-cost experiment, independent of the learning problem labels."""
import argparse
import hashlib
import json
from pathlib import Path
import statistics
import subprocess
import sys

parser=argparse.ArgumentParser()
parser.add_argument('--runtime',required=True)
parser.add_argument('--binary',action='append',required=True)
parser.add_argument('--output',required=True)
parser.add_argument('--repeats',type=int,default=10)
args=parser.parse_args()
runtime=Path(args.runtime).resolve()
sys.path.insert(0,str(runtime/'scripts'))
from xi_session_client import XiSession
out=Path(args.output).resolve();out.mkdir(parents=True,exist_ok=True)
empty=out/'empty.rvp'
if not empty.exists(): subprocess.run([runtime/'build/reverse_pc','init',empty],check=True)
results=[]
for binary in args.binary:
    binary=Path(binary).resolve()
    for width in [1,2,4,5,8]:
        lines=['#!reverse-pc-machine-v1','qtrace reset','clock f28','fset f20 0']
        for q in range(0,1000,width):
            lines.append(f'qprepare {5000+q} {width}')
            for j in range(width): lines.append(f'ry {5000+q+j} {.7+.037*((q+j)%13):.17g}')
            for j in range(width-1): lines.append(f'cx {5000+q+j} {5001+q+j}')
            for j in range(width):
                lines += [f'ry {5000+q+j} 0.31',f'fexpect f0 Z:{5000+q+j}','fadd f20 f0']
        lines += ['clock f29','fsub f29 f28','femit native_ms f29','femit observable_sum f20','qtrace report','stats','qstats','halt']
        source='\n'.join(lines)+'\n'
        (out/f'width-{width}.xi').write_text(source)
        observations=[]
        with XiSession(binary,empty) as session:
            for repeat in range(args.repeats+2):
                before=session.metrics()
                events,elapsed=session.execute(source)
                after=session.metrics()
                if repeat<2: continue
                values={e['name']:e['value'] for e in events if e['type']=='metric'}
                observations.append(dict(values,transport_ms=elapsed,cpu_ms=after['cpu_ms']-before['cpu_ms']))
            trace=next(e for e in events if e['type']=='quantum_trace')
            stats=next(e for e in events if e['type']=='quantum_stats')
            assert trace['distinct_rotated_qubits']==trace['distinct_observed_qubits']==trace['active_qubits']==1000
            assert trace['max_prepared_block']==width
            usage=session.metrics()
        result={'binary':binary.name,'binary_sha256':hashlib.sha256(binary.read_bytes()).hexdigest(),
                'block_width':width,'blocks':1000//width,'qubits':1000,
                'median_native_ms':statistics.median(x['native_ms'] for x in observations),
                'median_cpu_ms':statistics.median(x['cpu_ms'] for x in observations),
                'median_transport_ms':statistics.median(x['transport_ms'] for x in observations),
                'observable_sum':observations[0]['observable_sum'],
                'trace':trace,'quantum_stats':stats,'usage':usage,'samples':observations}
        results.append(result)
        out.joinpath('summary.json').write_text(json.dumps({'results':results},indent=2)+'\n')
        print(json.dumps({k:v for k,v in result.items() if k!='samples'}),flush=True)
for width in [1,2,4,5,8]:
    sums=[x['observable_sum'] for x in results if x['block_width']==width]
    assert max(sums)-min(sums)<1e-9,'optimization changed the observable circuit result'
