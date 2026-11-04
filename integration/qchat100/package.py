#!/usr/bin/env python3
"""Freeze one selected trained model and evaluate fresh question inputs."""
import argparse
import gzip
import json
from pathlib import Path
import shutil
from engine import ROOT,bits,evaluate,sha
from data import fresh_questions
from cli import info

def main():
    p=argparse.ArgumentParser();p.add_argument('--campaign',type=Path,required=True);p.add_argument('--runtime',type=Path,required=True)
    p.add_argument('--output',type=Path,default=ROOT/'integration/qchat100/release')
    a=p.parse_args();out=a.output.resolve();out.mkdir(parents=True,exist_ok=True);campaign=a.campaign.resolve()
    require_empty=not (out/'manifest.json').exists()
    if not require_empty:raise ValueError('Release exists; choose another directory')
    source=campaign/'trained.rvp';vocab=json.loads((campaign/'vocabulary.json').read_text())
    data=json.loads((campaign/'corpus.json').read_text())
    lex=json.loads((campaign/'input-vocabulary.json').read_text())
    # The selected campaign encoded previous utterances with its full input
    # vocabulary. Preserve that exact codec rather than changing its features.
    history=json.loads((campaign/'history-vocabulary.json').read_text()) if (campaign/'history-vocabulary.json').exists() else lex
    for name,values in [('vocabulary.json',vocab),('input-vocabulary.json',lex),('history-vocabulary.json',history)]:
        (out/name).write_text(json.dumps(values,ensure_ascii=False)+'\n')
    options={'input_vocabulary':set(lex),'history_vocabulary':set(history)}
    validation=evaluate(a.runtime,source,data['heldout'],vocab,**options)
    seen={tuple(bits(r['input'],[],r.get('previous',''),set(lex),set(history))) for r in data['train']}
    fresh=[r for r in fresh_questions() if tuple(bits(r['input'],[],r.get('previous',''),set(lex),set(history))) not in seen]
    final=evaluate(a.runtime,source,fresh,vocab,**options)
    ablation=evaluate(a.runtime,source,data['heldout'],vocab,mode=1,**options)
    analytic=evaluate(a.runtime,source,data['heldout'],vocab,mode=2,**options)
    assert [x['tokens'] for x in analytic['cases']]==[x['tokens'] for x in validation['cases']]
    model=info(a.runtime.resolve(),source,vocab)
    old=json.loads((campaign/'training-report.json').read_text())
    report={**old,'selected_campaign':campaign.name,'deployed_vocabulary_validation':validation,'fresh_question_evaluation':final,
            'deployed_ablation':ablation,'deployed_analytic_control_identical':True,
            'selection_basis':'validation questions only; fresh question set evaluated after selection',
            'limitations':['75-word output vocabulary','learned topics and phrasings only','fixed exact Clifford feature map; trained numerical readout',
                           'classically equivalent analytic features produce identical answers; no quantum advantage shown'],
            'native_model':model,'deployed_source_sha256':{f:sha(ROOT/f) for f in ['ai/xi/qchat100/model.xi','integration/qchat100/engine.py','integration/qchat100/cli.py']}}
    (out/'training-report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    compressed=gzip.compress(source.read_bytes(),compresslevel=9,mtime=0)
    (out/'QChat100-Entrenado.rvp.gz').write_bytes(compressed)
    manifest={'schema':1,'qubits':100,'file':'QChat100-Entrenado.rvp.gz','checkpoint_sha256':sha(source),
              'gzip_sha256':sha(out/'QChat100-Entrenado.rvp.gz'),'checkpoint_bytes':source.stat().st_size,
              'vocabulary_sha256':sha(out/'vocabulary.json'),'input_vocabulary_sha256':sha(out/'input-vocabulary.json'),
              'history_vocabulary_sha256':sha(out/'history-vocabulary.json'),'training_report_sha256':sha(out/'training-report.json'),
              'training_updates':model['training_updates'],'output_vocabulary':len(vocab),'quantum_advantage_claimed':False,
              'state_exactness':'Clifford algebra only','learning_arithmetic':'binary64 SGD; native XI',
              'runtime_source':'08c363e6c6855c14026c86046af7183a45f45a98','ether_source':'e2778d962af22f6f1a0794058dd4685fc2573966'}
    (out/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    print(json.dumps({'release':str(out),'gzip_bytes':len(compressed),'native_model':model,
                      'validation_accuracy':validation['exact_response_accuracy'],'fresh_accuracy':final['exact_response_accuracy'],
                      'fresh_count':len(fresh),'ablation_accuracy':ablation['exact_response_accuracy']},ensure_ascii=False),flush=True)

if __name__=='__main__':main()
