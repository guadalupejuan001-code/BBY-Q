#!/usr/bin/env python3
"""Real state survives SAVE/close/reload between teaching and later queries."""
import argparse
import json
from pathlib import Path
import tempfile
from controller import A, Engine, sha, metrics


def demo(run, runtime, teacher=1, correction=0, distractors=10):
    root=Path(run).resolve();head=json.loads((root/'HEAD.json').read_text())
    if not head.get('barrier_passed') or not head.get('active_checkpoint'):
        raise ValueError('No accepted memory checkpoint in this run')
    initial=root/head['active_checkpoint'];original=sha(initial)
    if original!=head['checkpoint_sha256']:raise ValueError('Checkpoint hash mismatch')
    if head['identity']['native_source_sha256']!=sha(Path(__file__).resolve().parents[2]/'ai/xi/qmemory/model.xi'):
        raise ValueError('Native memory implementation changed')
    if sha(Path(runtime)/'build/xi_session')!=head['identity']['runtime_sha256']:
        raise ValueError('Use the original pinned runtime')
    out=Path(tempfile.mkdtemp(prefix='conversation-',dir=root))
    state=initial;turns=[]
    query='fexpect f0 Z:20000\nfset f1 1\nfsub f1 f0\nfdiv f1 2\nfemit probability_one f1'
    def turn(name, body):
        nonlocal state
        destination=out/(str(len(turns))+'.rvp')
        with Engine(runtime,state) as engine:
            before=engine.parameters()
            ev,ms=engine.execute(body+'\n'+query)
            p=metrics(ev)['probability_one']
            assert before==engine.parameters()
            engine.s.save(destination)
        # The next turn opens a NEW native process and resumes this quantum state.
        with Engine(runtime,destination) as restored:
            ev,_=restored.execute(query)
            assert abs(metrics(ev)['probability_one']-p)<1e-12
        turns.append({'operation':name,'probability_one':p,'predicted':int(p>=.5),'state_sha256':sha(destination),'reload_reproduced':True,'elapsed_ms':ms})
        state=destination
    body='qprepare 20000 4\n'+('x 20001\n' if teacher else '')+f'set r14 20000\nset r7 20001\nfload f5 {A+64}\ncall qm_exchange'
    turn('teach',body)
    noise=[]
    for i in range(distractors):
        if i%2:noise.append('x 20003')
        noise += [f'set r14 20000\nset r7 20003\nfload f5 {A+80}\ncall qm_exchange']
    turn('distractors', '\n'.join(noise))
    turn('correct',('x 20002\n' if correction else '')+f'set r14 20000\nset r7 20002\nfload f5 {A+72}\ncall qm_exchange')
    turn('more_distractors','\n'.join(noise))
    # Erase host-side data/target cells for this slot. The query still uses only Z.
    turn('query_after_data_erasure',f'store8 {A+10000} 0\nstore8 {A+11000} 0\nstore8 {A+12000} 0\nstore8 {A+50000} 0')
    assert sha(initial)==original
    return {'ok':True,'teacher':teacher,'correction':correction,'distractors_per_segment':distractors,'turns':turns,'success':turns[0]['predicted']==teacher and turns[-1]['predicted']==correction,'parameter_checkpoint_unchanged':True,'scope':'One binary association in one four-qubit slot; no generated language or online weight update.'}


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('run');p.add_argument('--runtime',required=True);p.add_argument('--teacher',type=int,choices=[0,1],default=1);p.add_argument('--correction',type=int,choices=[0,1],default=0);p.add_argument('--distractors',type=int,choices=range(13),default=10)
    a=p.parse_args();print(json.dumps(demo(a.run,a.runtime,a.teacher,a.correction,a.distractors),ensure_ascii=False,indent=2))
