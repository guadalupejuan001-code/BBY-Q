#!/usr/bin/env python3
"""Check the native decoder, isolated input view and actual XI gradients."""
import json,math,random,statistics,tempfile
from pathlib import Path
from .common import ROOT,C1,A,entity_models,metrics,integer,write
from . import perception as P
from .train_head import select_decoded,evaluate as evaluate_head
from .refine_newton import system,solve,DELTA

def environment(seed):
    return f'store64 {A+256} {seed}\nstore64 {A+272} 0\nstore64 {A+280} 0\nfstore {A+296} .1\ncall vqc_sample\nstore64 {A} 0\ncall select_agent\ncall forward\n'

def expected_features(angles,logit):
    values=[logit/10]
    for q in range(4):
        channel=angles[q::4];middle=(min(channel)+max(channel))/2
        values.extend((middle,statistics.fmean(channel)-middle,statistics.pstdev(channel),(max(channel)-min(channel))/2))
    return values

def main():
    checks=[];gradients=[];phase_error=0.;feature_error=0.
    with tempfile.TemporaryDirectory(prefix='bbyq-u02-gradient-') as temporary:
        path=Path(temporary)/'v3.rvp';path.write_bytes(entity_models()['v3'])
        with C1.XiSession(C1.RT/'build/xi_session',path) as native:
            P.initialize(native)
            for seed in (88113,88114,1111914917,1816370752):
                values=metrics(P.run(native,environment(seed)+'femit before f21\ncall u2_apply\nfemit after f21'))
                assert values['before']==values['after'],values
            checks.append('zero residual reproduces the original native VQC probability exactly')
            # Compare both recovered phases and every aggregate: phase-only
            # tests cannot detect scratch that aliases a running extremum.
            rng=random.Random(2026110604);angles=[rng.uniform(-.15,2.55) for _ in range(1000)]
            angles[:4]=[0.,math.pi/2,-math.pi/2,math.pi-.4]
            original_rotations=P.floats(native,A+100000,1000)
            for index in (None,0,3,4,127,499,999):
                if index==499:P.run(native,P.stage(A+100000,[rng.uniform(-2.8,2.8) for _ in range(1000)]))
                current=angles[:]
                if index is not None:current[index]+=.123
                P.run(native,P.stage(A+300000,current)+f'store64 {A} 0\nstore64 {A+280} 0\ncall select_agent\ncall forward\ncall u2_project')
                recovered=P.floats(native,P.ADDR['PHASE'],1000)
                phase_error=max(phase_error,max(abs(x-y) for x,y in zip(current,recovered)))
                logit=P.floats(native,A+112,1)[0];actual=P.floats(native,P.ADDR['IN'],P.NF)
                feature_error=max(feature_error,max(abs(x-y) for x,y in zip(actual,expected_features(current,logit))))
            assert phase_error<1e-8,phase_error
            assert feature_error<1e-8,feature_error
            P.run(native,P.stage(A+100000,original_rotations))
            checks.append('actual Pauli correlations recover external angles on all 1000 wires with original and independently varied encoder rotations, including zero and both quadratures')
            checks.append('all 17 aggregate features match an independent oracle after first, boundary and final wire perturbations')
            P.run(native,environment(560031)+P.cache_body(0)+P.stage(P.ADDR['SCALE'],[.1]*P.NF))
            target=int(P.floats(native,A+128,1)[0]);address=P.ADDR['CACHE']
            P.run(native,f'store64 {P.B+112} {address}\ncall u2_clear_gradients\ncall u2_train_cached\ncall u2_adam\ncall u2_apply')
            before=P.floats(native,P.B+72,1)[0];phases=P.floats(native,P.ADDR['PHASE'],1000)
            values=metrics(P.run(native,f'fstore {A+128} {float(1-target)}\nfstore {P.B+96} {float(1-target)}\nfstore {address+200} {float(1-target)}\nstore64 {A+256} 77777\n'+P.stage(A+600,[999.,-999.,999.,-999.])+P.stage(A+300000,[0.]*1000)+'call u2_apply\nfemit p f21'))
            assert values['p']==before and P.floats(native,P.ADDR['PHASE'],1000)==phases
            checks.append('trained inference ignores forged labels, seed, withheld latents and erased raw input with quantum state held fixed')
            P.run(native,f'fstore {address+200} {float(target)}\nstore64 {P.B+112} {address}\ncall u2_clear_gradients\ncall u2_train_cached')
            parameters=P.floats(native,P.ADDR['P'],P.NP);analytic=P.floats(native,P.ADDR['G'],P.NP)
            assert abs(analytic[0])>1e-8 and abs(analytic[P.W1])>1e-8
            for index in (0,1,P.NF-1,P.W1,P.W2):
                base=P.ADDR['P']+8*index;epsilon=1e-5;losses=[]
                for sign in (-1,1):
                    values=metrics(P.run(native,f'fstore {base} {parameters[index]+sign*epsilon!r}\ncall u2_forward\nfemit p f21'))
                    probability=values['p'];losses.append(-math.log(probability) if target else -math.log1p(-probability))
                numeric=(losses[1]-losses[0])/(2*epsilon)
                P.run(native,f'fstore {base} {parameters[index]!r}')
                assert abs(numeric-analytic[index])<2e-6,(index,numeric,analytic[index])
                gradients.append({'index':index,'analytic':analytic[index],'finite_difference':numeric,'absolute_error':abs(numeric-analytic[index])})
            assert integer(native,P.B+24)==1 and integer(native,P.B+32)==2
            checks.append('XI gradients match finite differences for feature weights, bias and logit coefficient; optimizer counters advance')
            P.run(native,P.stage(P.ADDR['MEAN'],[0.]*P.NF)+P.stage(P.ADDR['SCALE'],[1.]*P.NF))
            rows=[]
            for sign in (-1.,1.):
                for nuisance in (-1.,1.):
                    features=[0.]*P.NF;features[0]=sign;features[1]=sign;features[2]=nuisance
                    rows.append({'seed':len(rows),'features':features,'label':int(sign>0),'old_logit':sign*10})
            selection=select_decoded(native,rows)
            assert selection['selected_features']==[1] and selection['covariance'][:3]==[.5,.5,0.],selection
            assert P.floats(native,P.ADDR['SKIP'],1)==[0.]
            checks.append('native training-only feature selection keeps a predictive decoded statistic, rejects independent noise and excludes the former logit')
            before=evaluate_head(native,rows);matrix=system(native,rows,[1,P.W1]);expected=[0.]*6
            for row,case in zip(rows,before['cases']):
                vector=[row['features'][1],1.];probability=case['probability']
                for i in range(2):
                    for j in range(2):expected[3*i+j]+=probability*(1-probability)*vector[i]*vector[j]
                    expected[3*i+2]+=(probability-row['label'])*vector[i]
            expected[0]+=.0001;expected[4]+=.0001
            assert max(abs(x-y) for x,y in zip(matrix,expected))<1e-10,(matrix,expected)
            solve(native,[1,P.W1]);delta=P.floats(native,DELTA,2)
            residual=max(abs(sum(matrix[3*i+j]*delta[j] for j in range(2))-matrix[3*i+2]) for i in range(2))
            assert residual<1e-10 and evaluate_head(native,rows)['brier']<before['brier']
            checks.append('native Newton curvature matches an independent Hessian, the Cholesky solve satisfies its linear system and a training step reduces error')
    report={'passed':True,'count':len(checks),'checks':checks,'maximum_phase_error':phase_error,'maximum_feature_error':feature_error,'maximum_newton_solve_residual':residual,'gradient_checks':gradients,'apk_built':False}
    destination=ROOT/'build/unified/perception-checks.json';destination.parent.mkdir(parents=True,exist_ok=True);write(destination,report);print(json.dumps(report,ensure_ascii=False))

if __name__=='__main__':main()
