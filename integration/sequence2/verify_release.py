#!/usr/bin/env python3
"""Verify frozen measurements and replay native predictions without retuning."""
import argparse,json,tempfile
from pathlib import Path
import engine as E
from schema import ROOT
from workspace import read_models,digest,encoded

def main():
    p=argparse.ArgumentParser();p.add_argument('--readers',type=Path,default=ROOT/'integration/sequence2/release');args=p.parse_args();f=args.readers
    m=json.loads((f/'manifest.json').read_text());evaluation=json.loads((f/'validation.json').read_text());checks=[]
    assert m['apk_built'] is False and m['active_in_android'] is False
    assert E.sha(f/'validation.json')==m['validation_sha256'] and E.sha(f/'protocol.json')==m['protocol_sha256']
    for source,sha in m['sources'].items():assert E.sha(ROOT/source)==sha,source
    for name,sha in m.get('validation_reports',{}).items():assert E.sha(f/name)==sha,name
    checks.append('frozen source, vocabulary, model, validation and protocol identities')
    assert all(g['correct']/g['total']>=.9 for head in ['text','intent'] for g in evaluation[head]['groups'].values())
    checks.append('every measured reader capability passes its registered floor')
    models=read_models(f);words=json.loads((f/'vocabulary.json').read_text());output=json.loads((f/'output-vocabulary.json').read_text());reloaded={}
    with tempfile.TemporaryDirectory(prefix='c1-release-') as folder:
        local=Path(folder);(local/'model.xi').write_bytes((f/'model.xi').read_bytes());(local/'model-binding.json').write_bytes((f/'model-binding.json').read_bytes())
        if (f/'semantic-vocabulary.json').exists():(local/'semantic-vocabulary.json').write_bytes((f/'semantic-vocabulary.json').read_bytes())
        for head,number in [('text',0),('intent',1)]:
            path=local/(head+'.rvp');path.write_bytes(models[head]);seen=set()
            with E.Model(path,words,output) as model:
                assert model.number(224+8*number)==m['models'][head]['native_updates']
                for row in evaluation[head]['cases']:
                    key=row['expected_intent'] if number else row.get('kind','known')
                    if key in seen:continue
                    seen.add(key)
                    if number:assert model.intent(row['input'],row.get('previous',''))['intent']==row['intent']
                    else:
                        got=model.generate(row['input'],row.get('previous',''));assert got['tokens']==row['tokens'] and got['terminated']==row['terminated']
            reloaded[head]=len(seen)
            try:E.Model(path,words+['wrong-dictionary'],output)
            except ValueError:pass
            else:raise AssertionError('Mismatched dictionary was accepted')
    checks.append('real native reload, training counters and mismatched-dictionary rejection')
    promotion=f/'promotion.json'
    if promotion.exists():
        q=json.loads(promotion.read_text());report=json.loads((f/'reserved.json').read_text())
        assert q['candidate_manifest_sha256']==E.sha(f/'manifest.json')
        assert q['reserved_sha256']==E.sha(f/'reserved.json')
        assert report['total']==200 and report['reserved'] and report['namespace']==m['reserved_test']['namespace']
        assert all(v['correct']/v['total']>=.9 for v in report['families'].values())
        checks.append('independent reserved tasks remain bound to the tested candidate')
    report={'passed':True,'checks':checks,'native_reloaded_groups':reloaded,'apk_built':False}
    (ROOT/'build/sequence2/release-checks.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');print(json.dumps(report,ensure_ascii=False))

if __name__=='__main__':main()
