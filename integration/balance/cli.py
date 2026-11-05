#!/usr/bin/env python3
"""Read-only access to the accepted balanced models through the real XI runtime."""
import argparse,gzip,json,math
from pathlib import Path
import run as R

def release():
    root=R.ROOT/'integration/balance/release';active=json.loads((root/'active.json').read_text())
    if not active.get('balanced') or active['schema']!=1:raise ValueError('No accepted balanced release')
    assert R.sha(root/'evaluation.json')==active['evaluation_sha256']
    manifests={}
    for name in ['v3','qchat100','qmemory']:
        folder=root/name;m=json.loads((folder/'manifest.json').read_text())
        assert R.sha(folder/'manifest.json')==active['components'][name]['manifest_sha256']
        assert Path(m['file']).name==m['file'] and R.sha(folder/m['file'])==m['gzip_sha256']
        manifests[name]=m
    return root,active,manifests

def main():
    p=argparse.ArgumentParser();p.add_argument('--runtime',type=Path,default=R.RT)
    sub=p.add_subparsers(dest='command',required=True)
    sub.add_parser('status')
    a=sub.add_parser('ask');a.add_argument('message');a.add_argument('--previous',default='')
    a=sub.add_parser('act');a.add_argument('position',type=int,choices=range(7));a.add_argument('goal',type=int,choices=range(7))
    a=sub.add_parser('classify');a.add_argument('input',type=Path)
    args=p.parse_args();R.RT=args.runtime.resolve();root,active,manifests=release()
    if args.command=='status':
        evaluation=json.loads((root/'evaluation.json').read_text())
        result={'ok':True,'version':active['version'],'balanced':True,'v3_training_episodes':manifests['v3']['training_episodes'],'qchat_training_updates':manifests['qchat100']['training_updates'],
          'test_criteria':{k:v['criterion_passed'] for k,v in evaluation['test'].items()},'qubits':{'VQC3':1000,'QRL3':1000,'QChat100':100,'QMemory':1000}}
    else:
        name='qchat100' if args.command=='ask' else 'v3';m=manifests[name];raw=gzip.decompress((root/name/m['file']).read_bytes())
        assert __import__('hashlib').sha256(raw).hexdigest()==m['checkpoint_sha256']
        import tempfile
        with tempfile.TemporaryDirectory(prefix='bbyq-e01-') as folder:
            state=Path(folder)/'model.rvp';state.write_bytes(raw)
            if args.command=='ask':
                vocabulary=json.loads((root/name/'vocabulary.json').read_text());lex=set(json.loads((root/name/'input-vocabulary.json').read_text()));history=set(json.loads((root/name/'history-vocabulary.json').read_text()))
                with R.QE.Native(R.RT,state) as model:result={'ok':True,**model.generate(args.message,vocabulary,args.previous,input_vocabulary=lex,history_vocabulary=history)}
            else:
                if args.command=='act':
                    body=f'store64 {R.A+344} {args.position}\nstore64 {R.A+352} {args.goal}\nstore64 {R.A+360} 0\nstore64 {R.A+312} 12\nstore64 {R.A+320} 2\nstore64 {R.A+280} 0\ncall qrl_step'
                else:
                    values=json.loads(args.input.read_text());assert isinstance(values,list) and len(values)==1000 and all(type(v)in[int,float] and math.isfinite(v) for v in values)
                    body=f'store64 {R.A} 0\nstore64 {R.A+280} 0\n'+''.join(f'fstore {R.A+300000+8*i} {float(v)}\n' for i,v in enumerate(values))+'call select_agent\ncall forward\nfemit probability f21'
                with R.XiSession(R.RT/'build/xi_session',state) as model:result={'ok':True,**R.metrics(R.execute(model,body))}
                if args.command=='classify':result['prediction']=int(result['probability']>=.5)
    print(json.dumps(result,ensure_ascii=False,indent=2))

if __name__=='__main__':main()
