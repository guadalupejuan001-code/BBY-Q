"""Executable Android U03 integration; original sources/checkpoints are unchanged.

Main session: C01 JNI library transport, C03 verified archives, C04 lazy XI,
C05 semantic frames, C06 native observational head, C09 verified memory.
C10 produces native plans on copies. C07/C08 consume explicit typed evidence.
C11-C15 are runnable, isolated experiments; none silently promotes a model.
"""
from __future__ import annotations
from contextlib import contextmanager
from hashlib import sha256
from pathlib import Path
from types import SimpleNamespace
from concurrent.futures import ThreadPoolExecutor
import json,sqlite3,struct,tempfile,time,threading,uuid,resource
from integration.unified.session import Session
from integration.unified.common import C1,encoded
from integration.cache_u03_c03.session import ArchiveMemo
from integration.codifier_u03_c05.session import SemanticSession
from integration.memory_u03_c09.view import UnifiedMemoryView
from integration.reasoning_u03_c10.engine import Reasoner
from integration.reasoning_u03_c10.planner import Goal
from xi_session_client import trace_scope

_ROOT=None
_DB=None
_MANIFEST=None
_MEMO=ArchiveMemo(max_bytes=32*1024*1024)
_CANDIDATES=None
MISSION='guarda la regla Faro Azul con valor 1 observa Nara con muestra 88113 y resuelve desde 3'

class MobileSession(SemanticSession):
    def __init__(self,database,**kwargs):
        super().__init__(database,memo=_MEMO,parallel_hash_workers=2,**kwargs)
        self.memory=UnifiedMemoryView(self)
        self.reasoner=Reasoner(self)

def configure(root,db,manifest):
    global _ROOT,_DB,_MANIFEST,_CANDIDATES
    _ROOT=Path(root);_DB=Path(db);_MANIFEST=manifest
    path=_ROOT/'integration/mobile_candidates/index.json'
    _CANDIDATES=json.loads(path.read_text())
    if _CANDIDATES.get('schema')!='BBYQ-Android-original-candidates-v1':raise ValueError('Unknown original C06-C08 candidate manifest')
    for cycle in ('c06','c07','c08'):candidate(cycle)

def digest(value):return sha256(encoded(value)).hexdigest()

def candidate(cycle):
    info=_CANDIDATES['models'][cycle]
    folder=_ROOT/'integration/mobile_candidates'
    model=folder/info['model'];report=folder/info['report']
    if sha256(model.read_bytes()).hexdigest()!=info['model_sha256']:raise ValueError('Candidate weight SHA mismatch: '+cycle)
    if sha256(report.read_bytes()).hexdigest()!=info['report_sha256']:raise ValueError('Candidate report SHA mismatch: '+cycle)
    return model,json.loads(report.read_text())

def current_snapshot():
    with Session(_DB) as s:return s.snapshot()

def source_audit():
    for name,expected in _MANIFEST['protected_sha256'].items():
        if sha256((_ROOT/name).read_bytes()).hexdigest()!=expected:raise ValueError('Protected checkpoint changed: '+name)
    return {'protected_files':159,'all_sha256_unchanged':True}

def summarize_trace(stats):
    totals={};rows=stats['packets'];ordered=sorted(rows,key=lambda x:x['start_ns'])
    if any(a['end_ns']>b['start_ns'] for a,b in zip(ordered,ordered[1:])):raise ValueError('Overlapping packet timings cannot be called exclusive')
    for r in rows:totals[r['owner']]=totals.get(r['owner'],0)+r['wall_ms']
    return {k:v for k,v in stats.items() if k!='packets'}|{
        'packet_wall_ms_by_owner':{k:round(v,3) for k,v in totals.items()},
        'packet_spans_nonoverlapping':True,'not_exclusive_gate_CPU':True,
        'inference_results_cached':False}

def semantic(prompt):
    from integration.semantic_u03_c06.train import NATIVE,B,VOCAB,OUTPUT,stage_features
    from integration.semantic_u03_c06.features import features
    from integration.semantic_u03_c06.dataset import LABELS
    path,report=candidate('c06')
    if sha256(NATIVE.read_bytes()).hexdigest()!=report['native_source_sha256']:raise ValueError('C06 XI source identity mismatch')
    with C1.Model(path,VOCAB,OUTPUT) as model:
        model.library+='\n'+NATIVE.read_text()
        events=model.run(stage_features(features(prompt,mode='semantic'))+'call c06_predict\n'+f'mem_materialize {B+16} 8')
        frames=[r for r in events if r.get('type')=='memory_materialization']
        if len(frames)!=1:raise ValueError('Missing C06 native prediction')
        predicted=struct.unpack('<q',bytes.fromhex(frames[0]['hex']))[0]
    if predicted not in range(len(LABELS)):raise ValueError('Invalid C06 class')
    return {'cycle':'C06','label':LABELS[predicted],'native_XI':True,
        'checkpoint_sha256':report['trained_checkpoint_sha256'],
        'observational':True,'replaces_C1_response':False}

def evidence(query,rows):
    from integration.metacognition_u03_c07.features import is_unsupported
    from integration.metacognition_u03_c07.train import NATIVE,infer,probabilities,guarded_action
    from integration.metacognition_u03_c07.dataset import LABELS
    from integration.active_u03_c08.dataset import Unlabeled
    from integration.active_u03_c08.learner import ask_for_verification
    if is_unsupported(query,rows):
        return {'status':'unsupported','action':'ask_for_evidence','native_prediction':None,'writes_to_user_memory':0}
    row=SimpleNamespace(query=query,evidence=tuple(rows));result={}
    for cycle in ('c07','c08'):
        path,report=candidate(cycle)
        if cycle=='c07':
            if sha256(NATIVE.read_bytes()).hexdigest()!=report['source_sha256']:raise ValueError('C07 source changed')
            config=next(x for x in report['modes'] if x['mode']=='provenance')
        else:
            if report['source_model_sha256']!=_CANDIDATES['models']['c07']['model_sha256']:raise ValueError('C08 lost its C07 baseline')
            config=next(x for x in report['comparisons'] if x['mode']=='active')
        with C1.Model(path,['<pad>'],['<eos>']) as model:
            model.library+='\n'+NATIVE.read_text();prediction=infer(model,[row],'provenance')[0]
        probability=probabilities(prediction['scores'],config['temperature'])
        action=guarded_action(row,prediction,config['temperature'],config['answer_threshold'])
        item={'native_class':LABELS[prediction['predicted']], 'guarded_action':LABELS[action],
            'class_confidence':max(probability),'not_probability_of_world_truth':True,
            'native_XI':True,'candidate_promoted':False}
        if cycle=='c08':
            item['verification_question']=ask_for_verification(
                Unlabeled('android-explicit-evidence',query,tuple(rows),'pool'),prediction)['question']
        result[cycle]=item
    return {'status':'evaluated','evaluations':result,'writes_to_user_memory':0,
            'scope':'original bounded C07/C08 evidence schema; not real-world source authentication'}

def main_turn(request_id,prompt,payload=None):
    start=time.perf_counter_ns()
    with trace_scope() as stats:
        with MobileSession(_DB) as model:
            before=model.snapshot();receipt=model.turn(request_id,prompt,payload)
            after=model.snapshot();memory=model.memory.snapshot()
            plan=model.last_plan_stats;frame=model.last_semantic
        # C06 uses its own original checkpoint only after the six main engines
        # have closed. No extra head can consume one of their active JNI slots.
        try:learned=semantic(prompt)
        except Exception as exc:learned={'available':False,'error':str(exc),'replaces_C1_response':False}
    return {'receipt':receipt,'receipt_sha256':digest(receipt),
        'before_revision':before['revision'],'after_revision':after['revision'],
        'C03':_MEMO.snapshot(),'C04':plan,'C05':frame,'C06':learned,
        'C09':{'view_sha256':memory['view_sha256'],'C1_U02_synchronized':memory['C1_synchronized_with_U02'],
               'bank_count':len(memory['bank_sha256'])},
        'C00_C01_C14':summarize_trace(stats),'wall_ms':round((time.perf_counter_ns()-start)/1e6,3)}

def memory(subject=None):
    with MobileSession(_DB) as s:return s.memory.snapshot(subject)

def plan(observation,association=None,position=3,kind='plan_mission'):
    with MobileSession(_DB) as s:
        goal=Goal(kind,observation,association,position)
        return s.reasoner.plan(goal)

def backup(source,destination):
    with sqlite3.connect(str(source),isolation_level=None) as src:
        with sqlite3.connect(str(destination),isolation_level=None) as dest:src.backup(dest)

def mission(receipt):return next((x for x in reversed(receipt.get('results',[])) if x.get('kind')=='mission'),{})

@contextmanager
def laboratory(name):
    before=current_snapshot();source_audit()
    directory=_DB.parent.parent/'laboratory'/(name+'-'+uuid.uuid4().hex[:12])
    directory.mkdir(parents=True,exist_ok=False)
    frozen=directory/'source.sqlite';backup(_DB,frozen)
    try:yield directory,frozen
    finally:
        if current_snapshot()!=before:raise RuntimeError('Laboratory unexpectedly changed personal U02 memory')
        source_audit()

def weight_hashes(db):
    from integration.joint_u03_c11.native import bank_weight_hashes
    with Session(db) as s:return bank_weight_hashes(s._banks())

def _run(db,request,prompt,control=None):
    with Session(db) as s:
        before=s.snapshot();r=s.turn(request,prompt,control=control);after=s.snapshot()
        return {'receipt':r,'receipt_sha256':digest(r),'before':before,'after':after}

def learning(cycle):
    if cycle not in ('c11','c12'):raise ValueError('Choose C11 or C12')
    from integration.joint_u03_c11.protocol import TRAINING_MISSION
    from integration.blocks_u03_c12.protocol import TRAIN
    from integration.joint_u03_c11.native import native_sample_teacher
    from integration.joint_u03_c11.protocol import Heldout
    # Predeclared mobile regression cases, not external observations or
    # additional user knowledge. Labels are unsealed after both predictions.
    heldout=(Heldout('mobile','Abeto Movil','Linde Cian',39160111,position=1,bit=0),
             Heldout('mobile','Jaspe Movil','Cauce Indigo',39160112,position=5,bit=1))
    prompts=[TRAINING_MISSION] if cycle=='c11' else [x.prompt() for x in TRAIN]
    with laboratory(cycle) as (directory,source):
        initial=weight_hashes(source);paths={}
        with Session(source) as s:v3=s.initial['v3']
        reports={}
        for arm in ('frozen','joint'):
            db=directory/(arm+'.sqlite');backup(source,db);paths[arm]=db
            updates=[]
            for i,prompt in enumerate(prompts):
                r=_run(db,'mobile-'+cycle+'-'+str(i),prompt)['receipt']
                if not r.get('ok'):raise RuntimeError('Native training mission rejected: '+str(r))
                if arm=='joint':
                    feedback=_run(db,'mobile-'+cycle+'-feedback-'+str(i),'aprende de la última tarea')['receipt']
                    rows=[x for x in feedback.get('results',[]) if x.get('kind')=='feedback']
                    if not feedback.get('ok') or not rows or rows[-1].get('supervision')!='independent-labels':raise RuntimeError('Unverified native feedback')
                    updates.append(rows[-1])
            hashes=weight_hashes(db)
            if arm=='frozen' and hashes!=initial:raise RuntimeError('Frozen control changed learned weights')
            # Each heldout case gets an isolated backup of its arm.
            predictions=[]
            for i,case in enumerate(heldout):
                test=directory/(arm+'-test-'+str(i)+'.sqlite');backup(db,test)
                r=_run(test,'mobile-heldout-'+str(i),case.prompt())['receipt'];m=mission(r)
                predictions.append({'seed':case.seed,'ok':bool(r.get('ok')),'class':m.get('class'),
                    'rule':m.get('rule_value'),'action':m.get('action')})
            reports[arm]={'weight_sha256':hashes,'changed_regions':{k:hashes[k]!=initial[k] for k in hashes},
                'verified_feedback':len(updates),'updates':updates,'predictions':predictions}
        labels={c.seed:native_sample_teacher(v3,c.seed) for c in heldout}
        for arm,row in reports.items():
            row['correct']=sum(x['class']==labels[x['seed']] for x in row['predictions']);row['total']=len(heldout)
        if not any(reports['joint']['changed_regions'].values()):raise RuntimeError('Feedback produced no audited parameter changes')
        interference=None
        if cycle=='c12':
            db=directory/'revisit.sqlite';backup(paths['joint'],db)
            values=[]
            for i,c in enumerate((heldout[0],heldout[1],heldout[0])):
                m=mission(_run(db,'revisit-'+str(i),c.prompt())['receipt'])
                values.append({k:m.get(k) for k in ('class','rule_value','action','goal')})
            interference={'A_B_A':values,'A_changed_after_B':values[0]!=values[2]}
        result={'cycle':cycle.upper(),'native_XI':True,'arms':reports,'initial_weight_sha256':initial,
            'interference':interference,'candidate_database':str(paths['joint']),
            'candidate_promoted':False,'user_database_unchanged':True,
            'synthetic_mobile_regression_only':True,'labels_unsealed_after_predictions':True,
            'same_or_better_accuracy_claimed':False}
        (directory/'evidence.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
        return result

def persistence():
    from integration.persist_u03_c02.optimistic import OptimisticSession
    with laboratory('c02') as (d,source):
        a=d/'original.sqlite';b=d/'optimistic.sqlite';backup(source,a);backup(source,b)
        reference=_run(a,'c02-parity','calcula 17 + 25')
        with OptimisticSession(b) as s:
            result=s.turn('c02-parity','calcula 17 + 25');snap=s.snapshot();metrics=s.last_metrics
            replay=s.turn('c02-parity','calcula 17 + 25')
            if result!=replay or snap!=s.snapshot():raise RuntimeError('C02 replay changed native state')
        if digest(result)!=reference['receipt_sha256'] or snap!=reference['after']:raise RuntimeError('C02 differs from original U02')
        return {'cycle':'C02','native_XI':True,'receipt_and_checkpoint_equal':True,
                'replay_without_second_update':True,'metrics':metrics,'user_database_unchanged':True}

def cache_comparison():
    from integration.optimize_u03_c13.cache import authenticated_release_cache
    with laboratory('c13') as (d,source):
        values={};records={}
        for cached in (False,True):
            from contextlib import nullcontext
            start=time.perf_counter_ns();rows=[]
            scope=authenticated_release_cache() if cached else nullcontext(None)
            with scope as counter:
                for i in range(2):
                    db=d/(str(cached)+'-'+str(i)+'.sqlite');backup(source,db)
                    rows.append(_run(db,'cache-parity-'+str(i),'calcula 7 + 3'))
                counts=dict(counter) if counter is not None else {}
            values[str(cached)]={'total_wall_including_scope_ms':(time.perf_counter_ns()-start)/1e6,'cache_counts':counts}
            records[cached]=rows
        for a,b in zip(records[False],records[True]):
            if a['receipt_sha256']!=b['receipt_sha256'] or a['after']!=b['after']:raise RuntimeError('C13 cache changed native output')
        return {'cycle':'C13','serial_exclusive_scope':True,'measurements':values,
            'receipt_and_checkpoint_equal':True,'cache_promoted':False,
            'performance_advantage_claimed':False,'user_database_unchanged':True}

def ablations():
    from integration.bench_u03_c14.protocol import BENCH,NATIVE_CONTROLS
    with laboratory('c14') as (d,source):
        rows=[]
        for i,case in enumerate(BENCH[:2]):
            for control in NATIVE_CONTROLS:
                db=d/(str(i)+'-'+str(control)+'.sqlite');backup(source,db)
                start=time.perf_counter_ns()
                with trace_scope() as stats:r=_run(db,'ablation-'+str(i),case.prompt(),control)['receipt']
                m=mission(r)
                rows.append({'case':case.seed,'control':control or 'normal','ok':bool(r.get('ok')),
                    'class':m.get('class'),'rule':m.get('rule_value'),'action':m.get('action'),
                    'voice_faithful':m.get('voice',{}).get('faithful'),
                    'wall_ms':(time.perf_counter_ns()-start)/1e6,'packets':summarize_trace(stats)})
        return {'cycle':'C14','trials':rows,'trial_count':len(rows),'failed_ablations_retained':True,
            'mobile_scope':'two cases, five original controls; not the full historical Linux campaign',
            'user_database_unchanged':True}

def stress():
    with laboratory('c15') as (d,source):
        db=d/'wal.sqlite';backup(source,db)
        with Session(db) as s:initial=s.snapshot()
        barrier=threading.Barrier(3);committed=threading.Event()
        def writer(i):
            barrier.wait(timeout=30)
            r=_run(db,'mobile-writer-'+str(i),'calcula '+str(i+7)+' + 3')
            committed.set();return r
        def reader():
            barrier.wait(timeout=30);seen=[]
            for phase in range(2):
                if phase and not committed.wait(timeout=90):raise RuntimeError('No commit observed')
                con=sqlite3.connect('file:'+str(db)+'?mode=ro',uri=True,isolation_level=None,timeout=60)
                try:
                    con.execute('BEGIN');rows=con.execute('SELECT name,snapshot,sha FROM unified_banks').fetchall()
                    if len(rows)!=7 or any(sha256(raw).hexdigest()!=expected for _,raw,expected in rows):raise RuntimeError('Torn mobile WAL bank')
                    revision=con.execute('SELECT revision FROM unified_state WHERE id=1').fetchone()[0];seen.append(revision);con.execute('ROLLBACK')
                finally:con.close()
            if seen[-1]<=initial['revision']:raise RuntimeError('Reader did not see a committed revision')
            return seen
        start=time.perf_counter_ns()
        with ThreadPoolExecutor(max_workers=3) as pool:
            tasks=[pool.submit(writer,i) for i in range(2)];watch=pool.submit(reader)
            results=[f.result(timeout=120) for f in tasks];revisions=watch.result(timeout=120)
        elapsed=(time.perf_counter_ns()-start)/1e6
        with Session(db) as s:
            before=s.snapshot()
            for i,r in enumerate(results):
                replay=s.turn('mobile-writer-'+str(i),'calcula '+str(i+7)+' + 3')
                if digest(replay)!=r['receipt_sha256']:raise RuntimeError('Mobile replay differs')
            if s.snapshot()!=before:raise RuntimeError('Mobile replay duplicated writes')
            collision=False
            try:s.turn('mobile-writer-0','calcula 99 + 1')
            except ValueError:collision=True
            if not collision or s.snapshot()!=before:raise RuntimeError('Conflicting ID was not rejected')
            for cut in (1,2,3):
                snap=s.snapshot();history=s.history()
                try:s.turn('mobile-rollback-'+str(cut),MISSION,fail_after=cut)
                except RuntimeError:pass
                else:raise RuntimeError('Rollback injection was not exercised')
                if s.snapshot()!=snap or s.history()!=history:raise RuntimeError('Rollback changed original state')
            if s.db.execute('PRAGMA integrity_check').fetchone()[0]!='ok':raise RuntimeError('Mobile SQLite integrity failed')
            final=s.snapshot()
        with Session(db) as reopened:
            if reopened.snapshot()!=final:raise RuntimeError('Restart lost committed state')
        return {'cycle':'C15','writers':2,'readers':1,'authenticated_read_revisions':revisions,
            'post_commit_observed':True,'committed_requests':2,'replay_exact':True,
            'different_payload_collision_rejected':True,'rollbacks':3,'reopen_exact':True,
            'wall_ms':elapsed,'tasks_per_second':2000/elapsed,'user_database_unchanged':True,
            'power_failure_or_native_crash_not_tested':True}

def transport_check():
    with laboratory('c01') as (d,source):
        rows=[]
        for use in (False,True):
            db=d/(str(use)+'.sqlite');backup(source,db)
            with trace_scope(library=use) as trace:r=_run(db,'transport-parity','calcula 7 + 3')
            rows.append((r,summarize_trace(trace)))
        if rows[0][0]['receipt_sha256']!=rows[1][0]['receipt_sha256'] or rows[0][0]['after']!=rows[1][0]['after']:raise RuntimeError('C01 JNI library transport changed exact XI state')
        if rows[1][1]['cache_hits']<1:raise RuntimeError('C01 code library was never reused')
        return {'cycle':'C01','exact_output_and_checkpoint':True,'baseline':rows[0][1],
            'library_transport':rows[1][1],'user_database_unchanged':True}

def assessment_demo():
    from integration.metacognition_u03_c07.dataset import evidence as make
    query={'subject':'Componente de laboratorio','predicate':'operativo'}
    rows=[make(query['subject'],query['predicate'],1,'laboratorio:android-A'),
          make(query['subject'],query['predicate'],0,'auditor:android-B')]
    return evidence(query,rows)|{'demo_is_synthetic':True}

def run_action(name,args):
    actions={'C01':transport_check,'C02':persistence,'C11':lambda:learning('c11'),
             'C12':lambda:learning('c12'),'C13':cache_comparison,'C14':ablations,'C15':stress,
             'EVIDENCE_DEMO':assessment_demo}
    if name in actions:return actions[name]()
    if name=='MEMORY':return memory(args.get('subject'))
    if name=='PLAN':return plan(str(args['observation']),str(args['association']),int(args.get('position',3)))
    if name=='PROVE':return plan(str(args['observation']),kind='prove_alert')
    if name=='EVIDENCE':return evidence(args['query'],args['evidence'])
    if name=='SEMANTIC':return semantic(str(args['prompt']))
    if name=='AUDIT':return source_audit()|{'C03':_MEMO.snapshot(),'memory':memory()}
    raise ValueError('Unknown mobile action: '+name)
