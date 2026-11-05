#!/usr/bin/env python3
"""Verify deployed parameter identity and native behavior after packaging."""
import gzip,json,tempfile
from pathlib import Path
import run as R
from cli import release

def main():
    root,active,models=release();report=json.loads((root/'evaluation.json').read_text());checks=[]
    with tempfile.TemporaryDirectory(prefix='bbyq-balanced-verify-') as temporary:
        states={}
        for name,m in models.items():
            p=Path(temporary)/(name+'.rvp');p.write_bytes(gzip.decompress((root/name/m['file']).read_bytes()));assert R.sha(p)==m['checkpoint_sha256'];states[name]=p;checks.append(name+' checkpoint hash')
        with R.XiSession(R.RT/'build/xi_session',states['v3']) as session:
            for name in ['vqc','qrl']:
                p=R.parameters(session,name);selected=report['selection'][name]['selected'];assert p['sha256']==selected['parameters'];checks.append(name+' merged parameter identity')
        measured=R.qrl_eval(states['v3'],'release-verification',8);assert measured['pairs_correct']>=40;checks.append('trained policy covers at least 40/42 distinct pairs')
        folder=root/'qchat100';vocabulary=json.loads((folder/'vocabulary.json').read_text());lex=set(json.loads((folder/'input-vocabulary.json').read_text()));history=set(json.loads((folder/'history-vocabulary.json').read_text()))
        expected={'hola':'Hola X.','quien eres':'Soy BBY Q.','cuantos cubits tienes':'Tengo cien cúbits.','que es memoria':'La memoria conserva información.','que es circuito':'Un circuito aplica puertas a los cúbits.','que es xi':'XI es nuestro lenguaje de instrucciones.'}
        with R.QE.Native(R.RT,states['qchat100']) as model:
            for prompt,answer in expected.items():
                result=model.generate(prompt,vocabulary,input_vocabulary=lex,history_vocabulary=history);assert result['text']==answer,(prompt,result['text']);assert result['terminated'];checks.append('language retention: '+prompt)
        memory=R.QM.evaluate(R.RT,states['qmemory'],250,91933,'release-verification',repeats=1,delays=(2,8,12));assert memory['accuracy']>=.99;checks.append('continued quantum memory independent native cases')
    output={'ok':True,'checks':checks,'count':len(checks),'version':active['version']}
    target=R.ROOT/'build/balance-release-checks.json';R.atomic(target,output);print(json.dumps(output))

if __name__=='__main__':main()
