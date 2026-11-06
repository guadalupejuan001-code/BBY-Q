#!/usr/bin/env python3
"""Post-hoc frozen-model diagnostics; never used for tuning or selection."""
import argparse
import json
from pathlib import Path
from types import SimpleNamespace
from compare_topologies import A, VARIANTS, SEEDS, experiment, publish, sha

p=argparse.ArgumentParser()
p.add_argument('--runtime',required=True)
p.add_argument('--campaigns',required=True)
p.add_argument('--output',required=True)
args=p.parse_args()
root=Path(args.campaigns).resolve();out=Path(args.output).resolve()
assert not out.exists()
dense=[];policies=[]
for seed in SEEDS:
    for variant in VARIANTS:
        name=f'vqc-dense-seed{seed}-{variant}'
        result=json.loads((root/name/'result.json').read_text())
        rows=result['trained']['iid']['observations']
        dense.append({'seed':seed,'variant':variant,
            'predicted_classes':sorted({int(x['probability']>=.5) for x in rows}),
            'probability_minimum':min(x['probability'] for x in rows),
            'probability_maximum':max(x['probability'] for x in rows),
            'samples':len(rows)})
        name=f'qrl-line_easy-seed{seed}-{variant}'
        settings=SimpleNamespace(runtime=args.runtime,output=str(root/'diagnostic-transport'),
            variant=variant,agent='qrl',task='line_easy',seed=seed,episodes=1000,samples=1)
        m,e,birth=experiment(settings)
        state=root/name/'checkpoint-01000.rvp';original=sha(state);rows=[]
        with e.Session(e.binary,state) as s:
            for position,goal in [(3,0),(3,6),(3,1),(3,5),(1,0),(5,6)]:
                body=(f'store64 {A} 1\nstore64 {A+280} 0\nstore64 {A+344} {position}\n'
                      f'store64 {A+352} {goal}\nstore64 {A+360} 0\nstore64 {A+312} 8\n'
                      'call select_agent\ncall qrl_observe\ncall forward\nfemit probability_right f21')
                events,_=s.execute(e.source(body));probability=m.metrics(events)['probability_right']
                rows.append({'position':position,'goal':goal,'probability_right':probability})
        assert sha(state)==original
        policies.append({'seed':seed,'variant':variant,'checkpoint_sha256':original,'states':rows})
publish(out,{'posthoc':True,'used_for_tuning':False,'model_updates':False,
    'scope':'Saved dense holdout predictions and six explicitly staged QRL states per frozen checkpoint; not additional training or a new test-set success rate.',
    'dense_classification':dense,'qrl_policy_probes':policies})
print(json.dumps({'saved':str(out),'dense_models':len(dense),'qrl_models':len(policies)}))
