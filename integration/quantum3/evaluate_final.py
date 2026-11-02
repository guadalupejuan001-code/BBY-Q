#!/usr/bin/env python3
"""Export reproducible held-out answers and native state/action trajectories."""
import argparse
import json
from pathlib import Path
import statistics
from types import SimpleNamespace
from campaign import A, XI, Experiment, metrics, sample_seed, sha, wilson

parser=argparse.ArgumentParser()
parser.add_argument('--runtime',required=True)
parser.add_argument('--session-binary')
parser.add_argument('--campaign',required=True)
parser.add_argument('--output',required=True)
args=parser.parse_args()
campaign=Path(args.campaign).resolve(); manifest=json.loads((campaign/'manifest.json').read_text())
identity=manifest['identity'];checkpoint=campaign/manifest['latest_checkpoint']
assert sha(checkpoint)==manifest['latest_checkpoint_sha256']
out=Path(args.output).resolve();out.mkdir(parents=True,exist_ok=True)
options=SimpleNamespace(runtime=args.runtime,session_binary=args.session_binary,step_budget=100000000,
                        agent=identity['agent'],task=identity['task'],seed=identity['seed'],episodes=1,
                        eval_size=manifest['evaluation_size_per_split'],classical=identity['classical'],
                        analytic=identity.get('analytic_classical_equivalent',False),
                        joint_mode=identity.get('joint_mode','independent'),initial_checkpoint=None,
                        output=str(out/'fixture'),resume=False)
e=Experiment(options)
summaries={}
for split in ['iid','ood']:
    values=[]
    with e.Session(e.binary,checkpoint) as session, (out/f'{split}.jsonl').open('w') as rows:
        before=e.model_state(session)
        for i in range(e.args.eval_size):
            events,ms=session.execute(e.source(e.stage(split,i)))
            item=dict(metrics(events),example=i,seed=sample_seed(e.args.seed,split,i),transport_ms=ms)
            values.append(item);rows.write(json.dumps(item)+'\n')
        assert before==e.model_state(session),'held-out evaluation modified learned parameters'
    if e.args.agent=='vqc':
        correct=sum(int(v['probability']>=.5)==int(v['label']) for v in values)
        score=correct/len(values);metric='accuracy'
    else:
        correct=sum(v['success'] for v in values);score=correct/len(values);metric='success_rate'
    expected=manifest['milestones'][-1][split][metric]
    assert score==expected,'final score did not reproduce from checkpoint'
    summaries[split]={metric:score,'wilson95':wilson(correct,len(values)),'examples':len(values),'reproduced_campaign':True}
summaries['random']=e.evaluate(checkpoint,random=True)
summaries['zeroed_observations']=e.evaluate(checkpoint,ablate=True)

trajectories=[]
if e.args.agent=='qrl' and e.joint_mode=='independent' and not e.args.classical:
    e.lib='\n'.join((XI/f).read_text() for f in ['common.xi','benchmarks.xi','qrl3-traced.xi'])
    with e.Session(e.binary,checkpoint) as session:
        before=e.model_state(session)
        for i in range(4):
            events,_=session.execute(e.source('qtrace reset\n'+e.stage('ood',i)+'\nqtrace report'))
            trajectory=[];step={}
            for event in events:
                if event.get('name') in ['state_position','state_goal','chosen_action','action_probability_right','next_position']:
                    step[event['name']]=event['value']
                    if event['name']=='next_position':trajectory.append(step);step={}
            trace=next(x for x in events if x['type']=='quantum_trace')
            assert trace['distinct_observed_qubits']==1000
            result=metrics(events)
            assert len(trajectory)==result['decisions']
            trajectories.append({'example':i,'seed':sample_seed(e.args.seed,'ood',i),'steps':trajectory,
                                 'success':result['success'],'reward':result['reward'],'trace':trace})
        assert before==e.model_state(session)
    (out/'trajectories.json').write_text(json.dumps(trajectories,indent=2)+'\n')
summary={'campaign':campaign.name,'checkpoint_sha256':sha(checkpoint),'identity':identity,
         'evaluation':summaries,'native_trajectories':len(trajectories)}
(out/'summary.json').write_text(json.dumps(summary,indent=2)+'\n')
print(json.dumps(summary))
