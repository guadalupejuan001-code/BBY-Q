"""Android-native executable laboratories for existing U03 experiments.

Only disposable SQLite copies are written. Original U02/XI runs every
inference/gradient. C11/C12 candidates are preserved under a lab directory,
not promoted to the user's live SQLite. No process-killing test runs from UI.
"""
from concurrent.futures import ThreadPoolExecutor
from contextlib import nullcontext
from hashlib import sha256
from pathlib import Path
import json, os, shutil, sqlite3, statistics, tempfile, threading, time

MISSION='guarda la regla Faro Azul con valor 1 observa Nara con muestra 88113 y resuelve desde 3'
TESTS=('calcula 7 + 3',MISSION)


def _digest(value):
    return sha256(json.dumps(value,sort_keys=True,ensure_ascii=False,separators=(',',':')).encode()).hexdigest()

def _canon(value):
    if isinstance(value,dict):return {k:_canon(v) for k,v in value.items() if k!='elapsed_ms'}
    if isinstance(value,list):return [_canon(v) for v in value]
    return value

def _copy(source,target):
    with sqlite3.connect(str(source),timeout=60) as src:
        with sqlite3.connect(str(target),timeout=60) as dst:src.backup(dst)

def _snapshot(path):
    from integration.unified.session import Session
    with Session(path) as model:return model.snapshot()

def _empty(path):
    from integration.unified.session import Session
    from integration.memory_u03_c09.view import UnifiedMemoryView
    with Session(path) as s:
        view=UnifiedMemoryView(s).snapshot()
        if len(view['bank_sha256'])!=7 or not view['C1_synchronized_with_U02']:
            raise RuntimeError('Laboratory source failed original bank authentication')
        return s.initial['v3']

def _measure(source,case,index=0,*,cached=False,optimistic=False,control=None):
    from integration.unified.session import Session
    from integration.persist_u03_c02.optimistic import OptimisticSession
    from xi_session_client import transport_scope
    with tempfile.TemporaryDirectory(prefix='u03-mobile-trial-') as td:
        db=Path(td)/'copy.sqlite'
        start=time.perf_counter_ns();_copy(source,db)
        events=[]
        cls=OptimisticSession if optimistic else Session
        with transport_scope(cached=cached,packets=events):
            with cls(db) as model:
                kwargs={'control':control} if control else {}
                result=model.turn('mobile-test-'+str(index),case,**kwargs)
                metrics=getattr(model,'last_metrics',None)
        snapshot=_snapshot(db)
        return {'receipt':_canon(result),'snapshot':snapshot,'native_packets':events,
                'wall_ms':(time.perf_counter_ns()-start)/1e6,
                'persistence_metrics':metrics}

def _transport(root,lab):
    source=lab/'source.sqlite';_empty(source)
    rows=[]
    for i,prompt in enumerate(TESTS):
        a=_measure(source,prompt,i,cached=False)
        b=_measure(source,prompt,i,cached=True)
        if a['receipt']!=b['receipt'] or a['snapshot']!=b['snapshot']:
            raise RuntimeError('C01 Android source-cache altered original XI result/state')
        rows.append({'native_receipts_equal':True,'native_snapshots_equal':True,
            'reference_ms':round(a['wall_ms'],3),'cached_ms':round(b['wall_ms'],3),
            'real_XI_calls':len(b['native_packets'])})
    return {'cycle':'C01','passed':True,'trials':rows,
        'inference_results_cached':False,'source_interning_only':True,
        'speedup_claimed':False,'personal_database_writes':0}

def _persistence(root,lab):
    source=lab/'source.sqlite';_empty(source)
    rows=[]
    for i,prompt in enumerate(TESTS):
        a=_measure(source,prompt,i)
        b=_measure(source,prompt,i,optimistic=True)
        if a['receipt']!=b['receipt'] or a['snapshot']!=b['snapshot']:
            raise RuntimeError('C02 original optimistic persistence changed XI state/receipt')
        rows.append({'identical':True,'reference_ms':round(a['wall_ms'],3),
                     'optimistic_ms':round(b['wall_ms'],3),'metrics':b['persistence_metrics']})
    return {'cycle':'C02','passed':True,'trials':rows,
            'default_persistence_replaced':False,'personal_database_writes':0}

def _joint(cycle,root,lab,keep):
    from integration.joint_u03_c11.campaign import (
        _prepared,_read_weights,_learn_one,_episode,score_runs)
    from integration.joint_u03_c11.native import native_sample_teacher
    from integration.joint_u03_c11 import protocol as p11
    from integration.blocks_u03_c12 import protocol as p12
    from integration.blocks_u03_c12.campaign import _training_arm
    from integration.unified.session import Session
    source=lab/'source.sqlite'
    original_v3=_empty(source)
    if cycle=='c11':_prepared(source)
    arms={name:lab/(name+'.sqlite') for name in ('frozen','joint-verified')}
    for path in arms.values():_copy(source,path)
    results={}
    if cycle=='c11':
        before,_=_read_weights(source)
        for name,path in arms.items():results[name]=_learn_one(path,name,before)
        cases=p11.heldout_test()
    else:
        for name,path in arms.items():results[name]=_training_arm(path,train=name=='joint-verified')
        cases=p12.TEST
    # Use original fixed held-out cases as CROSS-PLATFORM REGRESSION, not a
    # new discovery claim, and reveal original synthetic teachers only AFTER
    # every arm has returned its native predictions.
    observations={name:[_episode(path,case) for case in cases] for name,path in arms.items()}
    teachers={case.seed:native_sample_teacher(original_v3,case.seed) for case in cases}
    scores={name:score_runs(rows,teachers,cases) for name,rows in observations.items()}
    initial,_=_read_weights(source)
    frozen,_=_read_weights(arms['frozen'])
    candidate,snapshot=_read_weights(arms['joint-verified'])
    if initial!=frozen:raise RuntimeError('Frozen control parameters changed')
    changes={k:initial[k]!=candidate[k] for k in initial}
    # Publish candidate ONLY to its explicit laboratory location; never
    # copy these parameters into the authoritative personal SQLite.
    keep.mkdir(parents=True,exist_ok=True)
    candidate_file=keep/(cycle+'-candidate.sqlite')
    pending=keep/(cycle+'-candidate.pending.sqlite')
    _copy(arms['joint-verified'],pending)
    os.replace(pending,candidate_file)
    result={'cycle':cycle.upper(),'passed':True,
        'parameter_changes':changes,'changed_regions':sum(changes.values()),
        'before_weight_sha256':initial,'candidate_weight_sha256':candidate,
        'candidate_snapshot':snapshot,
        'evaluation':{name:{k:score[k] for k in ('total','class_correct','supported_faithful')}
                      for name,score in scores.items()},
        'scope':'original fixed synthetic regression on Android, not new unseen-domain evidence',
        'labels_revealed_after_inference':True,'model_promoted':False,
        'candidate_saved':candidate_file.name,'personal_database_writes':0}
    (keep/(cycle+'-report.json')).write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    return result

def _candidate(args,lab,keep):
    cycle=args.get('cycle','c12')
    if cycle not in ('c11','c12'):raise ValueError('Candidate must be C11 or C12')
    report_path=keep/(cycle+'-report.json')
    source=keep/(cycle+'-candidate.sqlite')
    if not source.exists() or not report_path.exists():
        raise ValueError('Run the '+cycle.upper()+' training laboratory first')
    report=json.loads(report_path.read_text())
    from integration.joint_u03_c11.campaign import _read_weights
    weights,snapshot=_read_weights(source)
    if weights!=report['candidate_weight_sha256'] or snapshot!=report['candidate_snapshot']:
        raise RuntimeError('Saved experimental candidate identity changed')
    prompt=args.get('text')
    if not isinstance(prompt,str) or not prompt.strip():raise ValueError('Candidate test needs text')
    trial=_measure(source,prompt)
    return {'cycle':cycle.upper(),'receipt':trial['receipt'],
            'native_XI_executed':bool(trial['native_packets']),
            'tested_in_disposable_copy':True,'candidate_modified':False,
            'model_promoted':False,'personal_database_writes':0}

def _cache(root,lab):
    from integration.optimize_u03_c13.cache import authenticated_release_cache
    from integration.blocks_u03_c12.campaign import _training_arm
    source=lab/'source.sqlite';_empty(source)
    joint=lab/'joint.sqlite';_copy(source,joint);_training_arm(joint,train=True)
    result={}
    for arm,db in (('frozen',source),('c12-unpromoted',joint)):
        rows=[]
        for rep in range(3):
            for i,prompt in enumerate(TESTS):
                records={}
                order=(False,True) if rep%2==0 else (True,False)
                for cached in order:
                    started=time.perf_counter_ns()
                    scope=authenticated_release_cache() if cached else nullcontext()
                    with scope:trial=_measure(db,prompt,i)
                    # All scope-entry/exit authentication costs are included.
                    trial['total_with_scope_ms']=(time.perf_counter_ns()-started)/1e6
                    records[cached]=trial
                a,b=records[False],records[True]
                if a['receipt']!=b['receipt'] or a['snapshot']!=b['snapshot']:
                    raise RuntimeError('C13 cache changed native receipts/checkpoints')
                rows.append({'reference_ms':a['total_with_scope_ms'],
                             'cached_ms':b['total_with_scope_ms'],'exact_parity':True})
        a=statistics.median(r['reference_ms'] for r in rows)
        b=statistics.median(r['cached_ms'] for r in rows)
        result[arm]={'pairs':len(rows),'reference_median_ms':a,'cached_median_ms':b,
                    'observed_reduction_pct':100*(a-b)/a,'raw':rows}
    return {'cycle':'C13','passed':True,'arms':result,'serialized_scope':True,
        'cache_enabled_globally':False,'model_promoted':False,
        'personal_database_writes':0,'scope':'Android host timings including authentication; descriptive only'}

def _profile(root,lab):
    from integration.bench_u03_c14.native_packets import packet_owner,BANKS
    source=lab/'source.sqlite';_empty(source)
    trial=_measure(source,MISSION)
    events=trial['native_packets']
    ordered=sorted(events,key=lambda r:r['start_ns'])
    if any(a['end_ns']>b['start_ns'] for a,b in zip(ordered,ordered[1:])):
        raise RuntimeError('Overlapping JNI packets cannot be billed exclusively')
    totals={k:0.0 for k in BANKS}
    for row in events:totals[packet_owner(row['bank'],row['calls'])]+=row['host_packet_ms']
    if abs(sum(totals.values())-sum(r['host_packet_ms'] for r in events))>0.001:
        raise RuntimeError('C14 JNI packet double-counting')
    # Run original supported U02 inference ablations on copies.
    controls=(None,'memory-erased','vqc-ablated','qrl-ablated','voice-ablated')
    ablations=[]
    for control in controls:
        row=_measure(source,MISSION,control=control)
        mission=next((r for r in reversed(row['receipt'].get('results',[])) if r.get('kind')=='mission'),{})
        ablations.append({'control':control or 'normal','receipt_ok':row['receipt'].get('ok'),
             'class':mission.get('class'),'rule':mission.get('rule_value'),
             'action':mission.get('action'),'voice':mission.get('voice'),
             'wall_ms':row['wall_ms']})
    return {'cycle':'C14','passed':True,'packets':len(events),
            'disjoint_host_packet_ms':totals,'end_to_end_ms':trial['wall_ms'],
            'exclusive_native_gate_cpu_ms':None,'source_bytes':sum(r['source_bytes'] for r in events),
            'ablations':ablations,'ablations_are_descriptive_not_accuracy_scores':True,
            'hardware_GPU_used':False,'personal_database_writes':0}

def _reader_view(db):
    from integration.unified.common import digest
    with sqlite3.connect('file:'+str(db)+'?mode=ro',uri=True,timeout=60,isolation_level=None) as c:
        c.execute('BEGIN')
        try:
            row=c.execute('SELECT metadata,sha,revision FROM unified_state WHERE id=1').fetchone()
            banks=c.execute('SELECT name,snapshot,sha FROM unified_banks').fetchall()
            if digest(row[0])!=row[1] or len(banks)!=7 or any(digest(raw)!=want for _,raw,want in banks):
                raise RuntimeError('Torn mobile WAL snapshot')
            language=c.execute('SELECT sha,metadata_sha FROM state WHERE id=1').fetchone()
            if json.loads(row[0]).get('language_sync')!=list(language):raise RuntimeError('C1 desynchronized')
            return row[2]
        finally:c.execute('ROLLBACK')

def _stress(root,lab):
    from integration.unified.session import Session
    from integration.blocks_u03_c12.campaign import _training_arm
    from integration.memory_u03_c09.view import UnifiedMemoryView
    rootdb=lab/'root.sqlite';_empty(rootdb)
    outputs={}
    for arm in ('frozen','c12-unpromoted'):
        db=lab/(arm+'.sqlite');_copy(rootdb,db)
        if arm!='frozen':_training_arm(db,train=True)
        start=threading.Barrier(4);committed=threading.Event()
        revision=_reader_view(db)
        def writer(index):
            start.wait(timeout=30)
            with Session(db) as s:
                r=s.turn('c16-writer-'+str(index),'calcula '+str(index+7)+' + 3')
                if not r['ok']:raise RuntimeError('Native concurrent writer failed')
                committed.set()
                return _canon(r)
        def reader(index):
            start.wait(timeout=30)
            before=_reader_view(db)
            if not committed.wait(timeout=120):raise RuntimeError('No post-commit WAL sample')
            after=_reader_view(db)
            if after<=revision or after<before:raise RuntimeError('Reader missed committed revision')
            return {'before':before,'after':after,'postcommit_verified':True}
        t0=time.perf_counter_ns()
        with ThreadPoolExecutor(max_workers=4) as pool:
            ws=[pool.submit(writer,i) for i in range(2)]
            rs=[pool.submit(reader,i) for i in range(2)]
            receipts=[f.result(timeout=180) for f in ws]
            readers=[f.result(timeout=180) for f in rs]
        elapsed=(time.perf_counter_ns()-t0)/1e6
        with Session(db) as s:
            prior=s.snapshot()
            for i,r in enumerate(receipts):
                replay=s.turn('c16-writer-'+str(i),'calcula '+str(i+7)+' + 3')
                if _canon(replay)!=r:raise RuntimeError('Concurrent receipt replay changed')
            if s.snapshot()!=prior:raise RuntimeError('Replay executed twice')
            try:s.turn('c16-writer-0','calcula 999 + 3')
            except ValueError:pass
            else:raise RuntimeError('Conflicting request ID accepted')
            rollback=[]
            for cut in (1,2,3):
                before=s.snapshot();history=s.history()
                try:s.turn('c16-failure-'+str(cut),MISSION,fail_after=cut)
                except RuntimeError:pass
                else:raise RuntimeError('Fault injection failed to execute')
                if s.snapshot()!=before or s.history()!=history:raise RuntimeError('Rollback leaked state')
                rollback.append(cut)
            final=s.snapshot()
            if s.db.execute('PRAGMA integrity_check').fetchone()[0]!='ok':raise RuntimeError('SQLite corruption')
        with Session(db) as reopened:
            audit=UnifiedMemoryView(reopened).snapshot()
            if reopened.snapshot()!=final or not audit['C1_synchronized_with_U02']:
                raise RuntimeError('Mobile restart lost native state')
        outputs[arm]={'writers':2,'readers':readers,'committed':2,'exact_replay':True,
            'rollback_cutpoints':rollback,'reopen_exact':True,'different_payload_rejected':True,
            'wall_ms':elapsed,'tasks_per_second_observed':2000/elapsed}
    return {'cycle':'C15','passed':True,'arms':outputs,
            'process_kill_during_XI_tested':False,'physical_device_tested':False,
            'scope':'two writers/two readers, native math, rollback after mission steps and reopen on Android',
            'personal_database_writes':0}

def run(name,args,root,personal_db):
    root=Path(root);personal_db=Path(personal_db)
    keep=personal_db.parent/'laboratory'
    keep.mkdir(parents=True,exist_ok=True)
    # This is a resource preflight, not a claimed system-capacity ceiling.
    if shutil.disk_usage(keep).free<256*1024*1024:
        raise RuntimeError('Laboratorio necesita 256 MiB libres para copias aisladas; no se modificó tu memoria')
    before=_snapshot(personal_db)
    started=time.perf_counter_ns()
    try:
        with tempfile.TemporaryDirectory(prefix='c16-',dir=keep) as td:
            lab=Path(td)
            if name=='transport':result=_transport(root,lab)
            elif name=='persistence':result=_persistence(root,lab)
            elif name in ('c11','c12'):result=_joint(name,root,lab,keep)
            elif name=='cache':result=_cache(root,lab)
            elif name=='profile':result=_profile(root,lab)
            elif name=='stress':result=_stress(root,lab)
            elif name=='candidate':result=_candidate(args,lab,keep)
            else:raise ValueError('Unknown laboratory action')
        result['experiment_wall_ms']=round((time.perf_counter_ns()-started)/1e6,3)
        result['personal_snapshot_sha256']=_digest(before)
        (keep/(name+'-last.json')).write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
        return result
    finally:
        if _snapshot(personal_db)!=before:
            raise RuntimeError('Laboratory changed personal state; reject result')
