"""Executable C16 Android integration, not an archive of unused stages.

BBY Q keeps one authoritative U02 SQLite database. Original C03/C04/C05,
C06, C09 and C10 are invoked on real routes. C07/C08 have explicit typed
observational routes; experimental learners never replace personal banks.
"""
from contextlib import contextmanager
from hashlib import sha256
from pathlib import Path
from types import SimpleNamespace
import json, os, struct, tempfile, time
import u03_mobile as base

_memo=None
_ready=False
_heads={}
_DIAGNOSTICS={}

def _dump(value):return json.dumps(value,ensure_ascii=False,sort_keys=True)
def _sha(value):return sha256(value).hexdigest()
def _record(name,value):
    _DIAGNOSTICS[name]={'time_ns':time.time_ns(),'result':value}
    return value

def _head(cycle):
    info=_heads[cycle]
    if _sha(info['path'].read_bytes())!=info['sha']:
        raise RuntimeError('Altered original native '+cycle+' checkpoint')
    return info

def _prepare_zero(root):
    # Android exposes /data/user/0 and /data/data aliases. Original schema.ROOT
    # resolves __file__, so its build-cache identity keys use canonical paths.
    # Match that exact original identity without bypassing source verification.
    import tools as original_tools
    root=Path(root).resolve()
    if Path(original_tools.ROOT).resolve()!=root:
        raise RuntimeError('Original Zero tools point outside authenticated runtime')
    paths=[original_tools.ROOT/p for p in ('integration/zero/build.mjs',
        'ai/personal/zero/model.mjs','ai/personal/zero/schema.mjs',
        'ai/personal/zero/core.xi.in')]
    for name in ('build/zero/zero.xi','build/zero/schema.json'):
        expected=base._manifest['files_sha256'][name]
        if _sha((root/name).read_bytes())!=expected:
            raise RuntimeError('Generated original XI Zero artifact changed: '+name)
    identity={str(p):_sha(p.read_bytes()) for p in paths}
    marker=original_tools.ROOT/'build/zero/.source-identity.json'
    marker.write_text(_dump(identity)+'\n')
    # Run the original guard: it must now authenticate the CI-built files
    # rather than try to invoke a Node executable on the Android device.
    original_tools.build_zero()

def initialize(files_dir,bundle_path,manifest_json):
    global _memo,_ready,_heads
    with base._lock:
        original=json.loads(base.initialize(files_dir,bundle_path,manifest_json))
        _prepare_zero(base._root)
        from integration.cache_u03_c03.session import ArchiveMemo
        from integration.reasoning_u03_c10.session import ReasoningSession
        folder=base._root/'integration/mobile_u03_c16/heads'
        provenance=json.loads((folder/'provenance.json').read_text())
        recovered={}
        for cycle in ('c06','c07','c08'):
            expected=provenance['heads'][cycle]
            path=folder/(cycle+'.rvp');report=folder/(cycle+'.json')
            if _sha(path.read_bytes())!=expected['checkpoint_sha256']:
                raise RuntimeError(cycle+' original trained checkpoint is missing or corrupt')
            if _sha(report.read_bytes())!=expected['report_sha256']:
                raise RuntimeError(cycle+' original training/calibration report mismatch')
            doc=json.loads(report.read_text())
            if doc.get('passed') is not True:raise RuntimeError('Unqualified head '+cycle)
            native=base._root/('ai/xi/c06/semantic-head.xi' if cycle=='c06' else 'ai/xi/c07/epistemic-head.xi')
            if cycle!='c08':
                want=doc.get('native_source_sha256',doc.get('source_sha256'))
                if _sha(native.read_bytes())!=want:raise RuntimeError('Head native code changed: '+cycle)
            recovered[cycle]={'path':path,'report':doc,'sha':expected['checkpoint_sha256']}
        if recovered['c08']['report']['source_model_sha256']!=recovered['c07']['sha']:
            raise RuntimeError('C08 original C07 lineage mismatch')
        _heads=recovered
        _memo=ArchiveMemo(max_bytes=32*1024*1024,max_entries=12)
        with ReasoningSession(base._db,memo=_memo,parallel_hash_workers=2) as s:
            audit=s.inspect_memory()
            if len(audit['bank_sha256'])!=7 or not audit['C1_synchronized_with_U02']:
                raise RuntimeError('C09/C10 mobile integration rejected memory identity')
        _ready=True
        original.update(integration='C16 integrated mobile routes',
            live_modules=['C03','C04','C05','C06','C09'],
            typed_modules=['C07','C08','C10'],
            sandbox_modules=['C01','C02','C11','C12','C13','C14','C15'],
            recovered_original_heads={k:v['sha'] for k,v in _heads.items()})
        return _dump(original)

def _session():
    if not _ready:raise RuntimeError('Integrated U03 runtime is not ready')
    from integration.reasoning_u03_c10.session import ReasoningSession
    return ReasoningSession(base._db,memo=_memo,parallel_hash_workers=2)

def personal_snapshot():
    from integration.unified.session import Session
    with Session(base._db) as s:return s.snapshot()

@contextmanager
def personal_unchanged():
    before=personal_snapshot()
    try:yield before
    finally:
        after=personal_snapshot()
        if before!=after:raise RuntimeError('A diagnostic changed authoritative personal U02 state')

def semantic(text):
    info=_head('c06')
    from integration.unified.common import C1
    from integration.semantic_u03_c06.train import NATIVE,B,VOCAB,OUTPUT,stage_features
    from integration.semantic_u03_c06.features import features
    from integration.semantic_u03_c06.dataset import LABELS
    with C1.Model(info['path'],VOCAB,OUTPUT) as head:
        head.library+='\n'+NATIVE.read_text()
        events=head.run(stage_features(features(text,mode='semantic'))+
                        'call c06_predict\n'+f'mem_materialize {B+16} 8')
        frames=[r for r in events if r.get('type')=='memory_materialization']
        if len(frames)!=1:raise RuntimeError('C06 native classifier returned malformed frames')
        predicted=struct.unpack('<q',bytes.fromhex(frames[0]['hex']))[0]
        if predicted not in range(len(LABELS)):raise RuntimeError('C06 invalid native decision')
    return {'cycle':'C06','native_XI':True,'label':LABELS[predicted],
            'label_id':predicted,'checkpoint_sha256':info['sha'],
            'scope':'three synthetic semantic classes, observational',
            'overrides_C1':False,'model_promoted':False}

def turn(request_id,prompt,payload_json=''):
    with base._lock:
        from xi_session_client import transport_scope
        from integration.codifier_u03_c05.semantic import analyze,wire_encode
        started=time.perf_counter_ns()
        packets=[]
        with _session() as s:
            before=s.snapshot()
            meta=json.loads(s.db.execute('SELECT metadata FROM unified_state WHERE id=1').fetchone()[0])
            frame=analyze(prompt,meta.get('previous',''))
            wire=wire_encode(frame)
            with transport_scope(cached=True,packets=packets):
                result=s.turn(request_id,prompt,json.loads(payload_json) if payload_json else None)
            after=s.snapshot()
            memory=s.inspect_memory()
            planner=s.last_plan_stats
        # Observational model failure must not turn a committed user action
        # into an error or a second execution. Preserve the real receipt.
        try:head=semantic(prompt)
        except Exception as exc:head={'available':False,'error':str(exc),'overrides_C1':False}
        native=[r for r in result.get('trace',[]) if 'native' in r]
        output={'ok':bool(result.get('ok')),'reply':base._reply(result),
            'receipt':result,'receipt_sha256':_sha(json.dumps(result,sort_keys=True,
                separators=(',',':'),ensure_ascii=False).encode()),
            'trace':result.get('trace',[]),'native_XI':bool(native) and all(r['native'] is True for r in native),
            'original_U02':result.get('entity')=='U02',
            'before_revision':before['revision'],'after_revision':after['revision'],
            'C1_U02_synchronized':memory['C1_synchronized_with_U02'],
            'C03':_memo.snapshot(),'C04':planner,
            'C05':{'frame':frame,'wire_sha256':_sha(wire)},'C06':head,
            'C09':{'view_sha256':memory['view_sha256'],'read_only':True,
                   'new_memory_authorities':memory['new_memory_authorities']},
            'C00':{'wall_ms':round((time.perf_counter_ns()-started)/1e6,3),
                   'native_packets':len(packets),'exclusive_gate_cpu_ms':None},
            'orchestration':'BBY Q -> w4U -> QdU; original authority unchanged'}
        _record('last_turn',{'revision':after['revision'],'receipt_sha256':output['receipt_sha256'],
                            'actual_native_packets':len(packets),'C06_executed':head.get('native_XI',False)})
        return _dump(output)

def _evidence(args):
    from integration.unified.common import C1
    from integration.metacognition_u03_c07.train import NATIVE,infer,probabilities,guarded_action
    from integration.metacognition_u03_c07.features import is_unsupported
    from integration.metacognition_u03_c07.dataset import LABELS
    from integration.active_u03_c08.dataset import Unlabeled
    from integration.active_u03_c08.learner import ask_for_verification
    query=args.get('query');rows=args.get('evidence',[])
    if is_unsupported(query,rows):
        return {'status':'unsupported','recommended_action':'ask_for_evidence',
                'native_executed':False,'personal_memory_written':False}
    case=SimpleNamespace(query=query,evidence=tuple(rows))
    results={}
    for cycle in ('c07','c08'):
        info=_head(cycle)
        with C1.Model(info['path'],['<pad>'],['<eos>']) as model:
            model.library+='\n'+NATIVE.read_text()
            prediction=infer(model,[case],'provenance')[0]
        field='modes' if cycle=='c07' else 'comparisons'
        mode='provenance' if cycle=='c07' else 'active'
        config=next(r for r in info['report'][field] if r['mode']==mode)
        p=probabilities(prediction['scores'],config['temperature'])
        act=guarded_action(case,prediction,config['temperature'],config['answer_threshold'])
        result={'native_class':LABELS[prediction['predicted']],
            'recommended_action':LABELS[act],'class_confidence':max(p),
            'confidence_is_truth_probability':False,'native_XI':True,
            'checkpoint_sha256':info['sha'],'model_promoted':False}
        if cycle=='c08' and act==1:
            row=Unlabeled('android-observation-only',query,tuple(rows),'pool')
            result['clarification']=ask_for_verification(row,prediction)['question']
        results[cycle.upper()]=result
    return {'status':'evaluated','assessments':results,
            'scope':'synthetic typed provenance; not real-world fact authentication',
            'personal_memory_written':False,'C08_comparison_only':True}

def operation(name,args_json='{}'):
    with base._lock:
        if not _ready:raise RuntimeError('U03 integration not initialized')
        args=json.loads(args_json or '{}')
        if not isinstance(args,dict):raise ValueError('Typed operation arguments required')
        # Raw data is never interpreted as a function name or code path.
        if name=='memory':
            with _session() as s:result=s.inspect_memory(args.get('subject'))
        elif name=='plan':
            with personal_unchanged(),_session() as s:
                result=s.plan_mission(args['observation'],args['association'],position=int(args.get('position',3)))
        elif name=='prove':
            with personal_unchanged(),_session() as s:result=s.prove_alert(args['observation'])
        elif name=='semantic':
            with personal_unchanged():result=semantic(args['text'])
        elif name=='evidence':
            with personal_unchanged():result=_evidence(args)
        elif name=='training':
            import u03_training
            result=u03_training.run(args,base._root,base._db)
        elif name in ('transport','persistence','c11','c12','cache','profile','stress','candidate'):
            import u03_experiments
            with personal_unchanged():result=u03_experiments.run(name,args,base._root,base._db)
        elif name=='capabilities':result=capabilities()
        elif name=='reports':result=_DIAGNOSTICS
        else:raise ValueError('Unsupported explicit Android integration action: '+str(name))
        if name not in ('reports','capabilities'):_record(name,result)
        return _dump(result)

def capabilities():
    return {'integration':'C17 personal training','production':{
        'C00':'measured host/native packet telemetry',
        'C01':'native JNI code-library references, not cached responses',
        'C03':'authenticated immutable archive memo',
        'C04':'original dependency/lazy-bank planner',
        'C05':'semantic frame alongside original C1 receipt',
        'C06':'recovered native trained semantic head; observational',
        'C09':'verified unified memory on the same SQLite'},
        'interactive':{'C07':'typed evidence inference','C08':'original active candidate comparison and clarification',
        'C10':'verified native plan/proof in sandbox',
        'C17':'persistent user lessons, native joint feedback, validation, explicit activation/restore and export'},
        'laboratory':{'C02':'optimistic persistence parity','C11':'joint native training and parameter audit',
        'C12':'cross-block native learning comparison','C13':'serialized cache experiment',
        'C14':'Android JNI packet profiling','C15':'Android rollback/replay/concurrency'},
        'not_claimed':['physical GPU compute integration','unlimited concurrency','AGI','physical quantum advantage'],
        'C11_C12_auto_promotion':False,'C08_auto_promotion':False,'C13_global_enabled':False,
        'reports_available':list(_DIAGNOSTICS)}

def status():
    with base._lock:
        import u03_training
        # Reconcile a durable activation/restore before taking either public
        # snapshot. Both views therefore describe the same live authority.
        training=u03_training.run({'action':'status'},base._root,base._db)
        with _session() as s:
            state=s.snapshot();audit=s.inspect_memory()
        personal_training_active=bool(training.get('active'))
        return _dump({'entity':'U02','snapshot':state,'bank_count':len(state['banks']),
            'memory':audit,'personal_training':training,
            # Legacy clients expect this field. It becomes false only after
            # an explicit user activation; restoring the original returns it
            # to true. A candidate can include memory lessons as well as
            # native joint feedback. Automatic promotion remains disabled.
            'C11_C12_unpromoted':not personal_training_active,
            'personal_training_active':personal_training_active,
            'C11_C12_automatic_promotion':False,'C13_cache_disabled':True,
            'GPU_virtual_compute_ported':False,'capabilities':capabilities()})

def panel():
    return base.panel()+'\n\nC16 Android: rutas ejecutables M01–M06.\n'+_dump(capabilities())

def history():return base.history()

