#!/usr/bin/env python3
"""Train and select the native quantum readout without opened-test examples."""
import argparse,hashlib,json,math,random,statistics,struct,time
from pathlib import Path
from .common import ROOT,C1,A,encoded,digest,read,write,entity_models,material
from . import perception as P

def seed(split,index):
    return int.from_bytes(hashlib.sha256(f'U02:2026110601:{split}:{index}'.encode()).digest()[:4],'little')&0x7fffffff

def sample(split,index,noise=.1):
    return f'store64 {A+256} {seed(split,index)}\nstore64 {A+280} 0\nstore64 {A+272} 0\nfstore {A+296} {noise}\ncall vqc_sample\nstore64 {A} 0\ncall select_agent\ncall forward\n'

def native_data(native,split,count,start,noise=.1,folder=None,configuration=None):
    rows=[];started=time.perf_counter();path=Path(folder)/(split+'-features.jsonl') if folder else None
    if path is not None:
        binding={'split':split,'count':count,'noise':noise,'projection_sha256':configuration['projection_sha256'],'native_source_sha256':configuration['native_source_sha256'],'base_model_sha256':digest(entity_models()['v3'])}
        manifest=path.with_suffix('.binding.json')
        if manifest.exists():assert read(manifest)==binding,'Cached measurement identity changed'
        else:write(manifest,binding)
        if path.exists():
            for line in path.read_text().splitlines():
                try:row=json.loads(line)
                except json.JSONDecodeError:break
                assert row['seed']==seed(split,len(rows)) and len(row['features'])==P.NF and row['label'] in (0,1)
                rows.append(row)
            path.write_text(''.join(json.dumps(row,separators=(',',':'))+'\n' for row in rows))
    for first in range(len(rows),count,16):
        batch=min(16,count-first)
        # Reuse sixteen slots instead of keeping the entire dataset inside
        # Inverse Memory. Labels and raw measurements are durable transport
        # records; all prediction and optimization still execute in XI.
        body=''.join(sample(split,first+j,.6 if split=='train' and (first+j)%4==0 else noise)+P.cache_body(j) for j in range(batch))
        P.run(native,body)
        raw=material(native,P.ADDR['CACHE'],batch*P.STRIDE);new=[]
        for j in range(batch):
            offset=j*P.STRIDE;features=list(struct.unpack_from('<'+'d'*P.NF,raw,offset))
            new.append({'seed':seed(split,first+j),'cache':start+first+j,'features':features,
                         'old_logit':struct.unpack_from('<d',raw,offset+192)[0],
                         'label':int(struct.unpack_from('<d',raw,offset+200)[0])})
        rows.extend(new)
        if path is not None:
            with path.open('a') as output:
                for row in new:output.write(json.dumps(row,separators=(',',':'))+'\n')
        if (first+batch)%128==0:print({'cache':split,'completed':first+batch,'total':count,'seconds':round(time.perf_counter()-started,2)},flush=True)
    return rows

def stage_rows(rows,teachers=False):
    body=''
    for index,row in enumerate(rows):
        address=P.ADDR['CACHE']+index*P.STRIDE
        body+=P.stage(address,row['features'])+f'fstore {address+192} {row["old_logit"]!r}\n'
        if teachers:body+=f'fstore {address+200} {float(row["label"])}\n'
    return body

def evaluate(native,rows):
    cases=[]
    for first in range(0,len(rows),64):
        chunk=rows[first:first+64];body=stage_rows(chunk)
        for index,row in enumerate(chunk):
            address=P.ADDR['CACHE']+index*P.STRIDE
            body+=f'store64 {P.B+112} {address}\ncall u2_load_features\ncall u2_forward\nfemit p f21\n'
        probabilities=[event['value'] for event in P.run(native,body) if event.get('type')=='metric' and event.get('name')=='p']
        assert len(probabilities)==len(chunk)
        cases.extend({'seed':row['seed'],'label':row['label'],'probability':p,'correct':int(p>=.5)==row['label']} for row,p in zip(chunk,probabilities))
    correct=sum(row['correct'] for row in cases)
    return {'correct':correct,'total':len(cases),'accuracy':correct/len(cases),'brier':statistics.fmean((r['probability']-r['label'])**2 for r in cases),'cases':cases}

def base_identity(native):
    return {name:digest(b''.join(material(native,base+d,8000) for d in (0,10000,20000))+material(native,meta,48))
            for name,base,meta in [('vqc',A+100000,A+4000),('qrl',A+200000,A+5000)]}

def select_decoded(native,rows,minimum=.08):
    """Select decoded statistics from training-label covariance in XI.

    The inaccurate former logit remains a reported baseline, rather than a
    shortcut in the new trained classifier. No validation labels enter here.
    """
    covariance=P.B+30000
    P.run(native,P.stage(covariance,[0.]*P.NF))
    for first in range(0,len(rows),256):
        chunk=rows[first:first+256];body=stage_rows(chunk,teachers=True)
        for index in range(len(chunk)):
            address=P.ADDR['CACHE']+index*P.STRIDE
            # Unroll the feature loop here; duplicate XI label names are not
            # permitted inside a single streaming execution packet.
            body+=f'store64 {P.B+112} {address}\ncall u2_load_features\ncall u2_normalize\nfload f22 {address+200}\nfsub f22 .5\n'
            for j in range(P.NF):
                body+=f'fload f0 {P.ADDR["NORMAL"]+8*j}\nfmul f0 f22\nfload f1 {covariance+8*j}\nfadd f1 f0\nfstore {covariance+8*j} f1\n'
        P.run(native,body)
    body=''
    for j in range(P.NF):
        body+=f'fload f0 {covariance+8*j}\nfdiv f0 {len(rows)}\nfstore {covariance+8*j} f0\nfmul f0 f0\nfsqrt f0 f0\nfcmp f0 {minimum}\njge u2_keep_feature_{j}\nfstore {P.ADDR["SCALE"]+8*j} 0\nlabel u2_keep_feature_{j}\n'
    body+=f'fstore {P.ADDR["SCALE"]} 0\nfstore {P.ADDR["P"]} 0\nfstore {P.ADDR["SKIP"]} 0'
    P.run(native,body)
    scales=P.floats(native,P.ADDR['SCALE'],P.NF)
    result={'method':'native training-only normalized covariance with the binary teacher','minimum_absolute_covariance':minimum,'covariance':P.floats(native,covariance,P.NF),'selected_features':[j for j,scale in enumerate(scales) if scale!=0.],'original_logit_excluded':True,'validation_labels_used':False}
    assert result['selected_features'],'No decoded quantum statistic passed the training-only selector'
    return result

def export(native,initial,destination):
    # Export learned inference and optimizer state only. No dataset cache or
    # teacher view is copied into the deployment checkpoint.
    with C1.XiSession(C1.RT/'build/xi_session',initial) as clean:
        for address,raw in P.publish_region(native):
            for start in range(0,len(raw),4096):P.run(clean,C1.stage_bytes(address+start,raw[start:start+4096]))
        P.run(clean,f'fstore {A+128} 0\nstore64 {A+256} 0\n'+P.stage(A+600,[0.]*4))
        clean.save(destination)

def main():
    parser=argparse.ArgumentParser();parser.add_argument('folder',type=Path);parser.add_argument('--train',type=int,default=4096);parser.add_argument('--validation',type=int,default=512);parser.add_argument('--epochs',type=int,default=60);args=parser.parse_args()
    folder=args.folder;folder.mkdir(parents=True,exist_ok=True)
    protocol={'version':'U02','seed':2026110601,'training_examples':args.train,'training_noise':{'every_fourth':.6,'otherwise':.1},'native_cache_slots':256,'native_override_budget_increased':False,'validation_examples_per_split':args.validation,'validation_splits':['validation-iid','validation-ood'],'training_source':'new native environment samples only','prohibited_training_sources':['U01 reserved and diagnostic tasks','nine known regressions','U02 final test'],
              'model':{'features':P.NF,'hidden':P.NH,'parameters':P.NP,'input':'Pauli correlations of all 1000 qubits and decoded statistical features','feature_selection':'native training-only absolute normalized covariance at least .08; former logit excluded'},'optimizer':'XI Adam, mini-batches of 32; former-logit coefficients constrained to zero','learning_rate':.03,'epochs':args.epochs,'selection':'no IID validation errors, OOD at least .99 and mean Brier at most .01; independent final test stays closed','floor':{'iid_accuracy':1.,'ood_accuracy':.99,'mean_brier':.01},'original_quantum_parameters':'preserved','apk_built':False}
    write(folder/'protocol.json',protocol)
    paths=['integration/unified/train_head.py','integration/unified/perception.py','integration/unified/decoder_source.py','ai/xi/unified/perception-decoder.xi.in','ai/xi/unified/perception-head.xi.in','integration/unified/common.py','ai/xi/quantum3/common.xi','ai/xi/quantum3/benchmarks.xi']
    write(folder/'training-sources.json',{name:C1.sha(ROOT/name) for name in paths})
    for name in paths:
        destination=folder/'sources'/name;destination.parent.mkdir(parents=True,exist_ok=True);destination.write_bytes((ROOT/name).read_bytes())
    train_seeds={seed('train',i) for i in range(args.train)}
    validation_seeds={seed(split,i) for split in protocol['validation_splits'] for i in range(args.validation)}
    assert not train_seeds&validation_seeds and len(train_seeds)==args.train and len(validation_seeds)==2*args.validation
    initial=folder/'original.rvp';initial.write_bytes(entity_models()['v3']);rng=random.Random(2026110601);candidates=[];selected=None
    with C1.XiSession(C1.RT/'build/xi_session',initial) as native:
        original=base_identity(native);configuration=P.initialize(native);write(folder/'configuration.json',configuration)
        train=native_data(native,'train',args.train,0,folder=folder,configuration=configuration)
        val={split:native_data(native,split,args.validation,args.train+i*args.validation,.1 if i==0 else .6,folder=folder,configuration=configuration) for i,split in enumerate(protocol['validation_splits'])}
        # Normalization is computed only from the training input view.
        means=[statistics.fmean(row['features'][j] for row in train) for j in range(P.NF)]
        scales=[1/max(.01,statistics.pstdev(row['features'][j] for row in train)) for j in range(P.NF)]
        P.run(native,P.stage(P.ADDR['MEAN'],means)+P.stage(P.ADDR['SCALE'],scales))
        baseline={split:evaluate(native,rows) for split,rows in val.items()};write(folder/'baseline.json',baseline)
        print({'phase':'baseline','validation':{k:{a:b for a,b in v.items() if a!='cases'} for k,v in baseline.items()}},flush=True)
        configuration['training_feature_selection']=select_decoded(native,train);write(folder/'configuration.json',configuration)
        print({'phase':'training-only-feature-selection',**configuration['training_feature_selection']},flush=True)
        for epoch in range(1,args.epochs+1):
            order=list(train);rng.shuffle(order);started=time.perf_counter()
            for first in range(0,len(order),256):
                chunk=order[first:first+256];body=stage_rows(chunk,teachers=True)
                for small in range(0,len(chunk),32):
                    body+='call u2_clear_gradients\n'
                    for index in range(small,min(small+32,len(chunk))):body+=f'store64 {P.B+112} {P.ADDR["CACHE"]+index*P.STRIDE}\ncall u2_train_cached\n'
                    body+=f'fstore {P.ADDR["GSKIP"]} 0\ncall u2_adam\n'
                P.run(native,body)
            if epoch==1 or epoch%5==0 or epoch==args.epochs:
                validation={split:evaluate(native,rows) for split,rows in val.items()}
                minimum=min(row['accuracy'] for row in validation.values());brier=statistics.fmean(row['brier'] for row in validation.values())
                eligible=validation['validation-iid']['correct']==validation['validation-iid']['total'] and validation['validation-ood']['accuracy']>=.99 and brier<=.01
                entry={'epoch':epoch,'minimum_accuracy':minimum,'mean_brier':brier,'eligible':eligible,'parameter_sha256':P.parameter_identity(native),'validation':{k:{a:b for a,b in v.items() if a!='cases'} for k,v in validation.items()}}
                candidates.append(entry);write(folder/'candidates.json',candidates);write(folder/f'validation-{epoch:03}.json',validation)
                print({**entry,'seconds_this_epoch':round(time.perf_counter()-started,2)},flush=True)
                if selected is None or (eligible,minimum,-brier)>(selected['eligible'],selected['minimum_accuracy'],-selected['mean_brier']):
                    checkpoint=folder/f'candidate-{epoch:03}.rvp';native.save(checkpoint);entry['checkpoint']=checkpoint.name;entry['sha256']=C1.sha(checkpoint);selected=dict(entry);write(folder/'selection.json',selected)
                if eligible:break
        assert base_identity(native)==original,'Readout training changed original quantum parameters'
    checkpoint=folder/selected['checkpoint'];chosen=folder/'perception.rvp'
    with C1.XiSession(C1.RT/'build/xi_session',checkpoint) as native:
        export(native,initial,chosen);assert base_identity(native)==original
    selected.update({'path':chosen.name,'sha256':C1.sha(chosen),'preserved_original_parameters':original});write(folder/'selection.json',selected)
    print({'selected':selected},flush=True)

if __name__=='__main__':main()
