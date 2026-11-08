"""Single Android gateway to executable U03 cycles and original XI memory.

A packaged file is not counted as an active feature. Each public action below
calls a real module or an isolated native experiment and returns its evidence.
"""
from __future__ import annotations
from pathlib import Path
from hashlib import sha256
import json,os,sys,shutil,tempfile,threading,time,uuid,zipfile
_lock=threading.RLock()
_root=None
_db=None
_manifest=None
_last_report=None

def hashed(raw):return sha256(raw).hexdigest()

def _verify(root,items):
    for name,want in items.items():
        file=root/name
        if not file.is_file() or hashed(file.read_bytes())!=want:raise RuntimeError('Original U03 source/checkpoint altered: '+name)

def _activate(root):
    for p in (root,root/'deps/reverse-pc/scripts',root/'integration/sequence2'):
        value=str(p)
        if value in sys.path:sys.path.remove(value)
        sys.path.insert(0,value)
    # Original build_zero() checks these exact absolute paths. Its generated
    # XI/schema were already authenticated as bundle members. Record the same
    # source identity so no Node subprocess is needed on Android. No monkeypatch.
    paths=[root/p for p in ('integration/zero/build.mjs','ai/personal/zero/model.mjs',
                           'ai/personal/zero/schema.mjs','ai/personal/zero/core.xi.in')]
    marker=root/'build/zero/.source-identity.json'
    marker.write_text(json.dumps({str(p):hashed(p.read_bytes()) for p in paths})+'\n')

def initialize(files_dir,bundle_path,manifest_json):
    global _root,_db,_manifest
    with _lock:
        m=json.loads(manifest_json)
        if m.get('schema')!='BBYQ-U03-Android-authenticated-runtime-v1':raise ValueError('Unrecognized original runtime manifest')
        if m.get('protected_count')!=159 or m.get('new_memory_authorities')!=0:raise ValueError('Protected model inventory changed')
        if m.get('experimental_c11_c12_promoted') or m.get('C13_cache_enabled'):raise ValueError('Unapproved model/cache promotion')
        archive=Path(bundle_path)
        if hashed(archive.read_bytes())!=m['archive_sha256']:raise ValueError('APK runtime archive hash mismatch')
        base=Path(files_dir);base.mkdir(parents=True,exist_ok=True)
        root=base/('runtime-'+m['archive_sha256'][:16]);stamp=root/'.verified'
        if not stamp.is_file() or stamp.read_text()!=m['archive_sha256']:
            temp=Path(tempfile.mkdtemp(prefix='u03-unpack-',dir=base))
            try:
                with zipfile.ZipFile(archive) as z:
                    names=z.namelist()
                    if len(names)!=len(set(names)) or set(names)!=set(m['files_sha256']):raise ValueError('Runtime archive members mismatch')
                    for name in names:
                        part=Path(name)
                        if part.is_absolute() or '..' in part.parts or name.endswith('/'):raise ValueError('Unsafe runtime path')
                        raw=z.read(name)
                        if hashed(raw)!=m['files_sha256'][name]:raise ValueError('Runtime source SHA mismatch: '+name)
                        target=temp/name;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(raw)
                _verify(temp,m['protected_sha256']);(temp/'.verified').write_text(m['archive_sha256'])
                if root.exists():shutil.rmtree(root)
                temp.rename(root)
            finally:
                if temp.exists():shutil.rmtree(temp)
        # Validate code as well as all historical banks on every process start.
        _verify(root,m['files_sha256']);_activate(root)
        sessions=base/'sessions';sessions.mkdir(parents=True,exist_ok=True)
        db=sessions/'u03-original.sqlite'
        import mobile_cycles as cycles
        cycles.configure(root,db,m)
        with cycles.MobileSession(db) as model:
            snapshot=model.snapshot();audit=model.memory.snapshot()
            if len(snapshot['banks'])!=7 or not audit['C1_synchronized_with_U02']:raise ValueError('Android original U02 banks not synchronized')
            if audit['new_memory_authorities']!=0:raise ValueError('A second memory authority was created')
            if model.db.execute('PRAGMA integrity_check').fetchone()[0]!='ok':raise ValueError('SQLite integrity failed')
        _root,_db,_manifest=root,db,m
        return json.dumps({'ready':True,'entity':'U02','cycles':'C00-C15 executable integration',
            'components':['C1','VQC3','QRL3','QMemory','Entity','QChat100'],'banks':7,
            'historical_assets':159,'checkpoint_identity_verified':True,'C1_U02_synchronized':True,
            'model_promoted':False,'cache_promoted':False,'gpu_C12_ported':False,
            'original_C06_C07_C08_checkpoints_loaded':True,
            'active_main':['C01','C03','C04','C05','C06','C09'],
            'available_actions':['C02','C07','C08','C10','C11','C12','C13','C14','C15'],
            'note':'Availability is not a claim of measured performance or promotion.'},ensure_ascii=False)

def _ready():
    if _root is None or _db is None:raise RuntimeError('Original U03 runtime is not ready')

def _reply(receipt):
    if not receipt.get('ok'):return receipt.get('reason') or receipt.get('error') or 'El motor XI se abstuvo o rechazó esta operación; no se inventó una respuesta.'
    pieces=[]
    for row in receipt.get('results',[]):
        kind=row.get('kind')
        if kind in ('text','greet','cancel'):pieces.append(row.get('text',''))
        elif kind=='math':pieces.append('Resultado XI: '+str(row.get('value')))
        elif kind in ('mission','plan'):
            voice=row.get('voice',{});text=voice.get('text')
            if text:pieces.append(text)
            pieces.append('Decisión: '+str(row.get('action'))+' · objetivo: '+str(row.get('goal')))
        elif kind=='feedback':pieces.append('Aprendizaje XI aplicado: '+json.dumps(row.get('updates',{}),ensure_ascii=False))
        elif kind=='query':pieces.append('Consulta XI: '+str(row.get('status'))+' · evidencia: '+str(row.get('proof',[])))
        elif kind=='lookup':pieces.append(str(row.get('value',row.get('status'))))
        elif kind=='status':pieces.append('Motores: '+', '.join(row.get('components',[])))
        elif kind:pieces.append(kind+': '+json.dumps(row,ensure_ascii=False)[:500])
    return '\n'.join(p for p in pieces if p) or 'Operación original XI completada.'

def _record(name,result):
    global _last_report
    folder=_db.parent.parent/'reports';folder.mkdir(parents=True,exist_ok=True)
    identifier=name+'-'+uuid.uuid4().hex[:12]
    report={'id':identifier,'action':name,'result':result,'report_is_not_model_memory':True}
    temporary=folder/(identifier+'.tmp');target=folder/(identifier+'.json')
    temporary.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');os.replace(temporary,target)
    _last_report=report
    return report

def turn(request_id,prompt,payload_json=''):
    with _lock:
        _ready()
        if not isinstance(request_id,str) or not request_id or not isinstance(prompt,str):raise ValueError('Request ID and text required')
        import mobile_cycles as cycles
        result=cycles.main_turn(request_id,prompt,json.loads(payload_json) if payload_json else None)
        receipt=result['receipt'];trace=receipt.get('trace',[])
        native=[row for row in trace if 'native' in row]
        result.update({'ok':bool(receipt.get('ok')),'reply':_reply(receipt),'trace':trace,
            'native_XI':bool(native) and all(r['native'] is True for r in native),
            'original_U02':receipt.get('entity')=='U02',
            'C1_U02_synchronized':result['C09']['C1_U02_synchronized']})
        _record('turn',result)
        return json.dumps(result,ensure_ascii=False)

def action(name,payload_json='{}'):
    with _lock:
        _ready()
        import mobile_cycles as cycles
        args=json.loads(payload_json or '{}')
        if not isinstance(args,dict):raise ValueError('Typed action input must be a JSON object')
        start=time.perf_counter_ns()
        result=cycles.run_action(name,args)
        report=_record(name,{'data':result,'wall_ms':(time.perf_counter_ns()-start)/1e6})
        return json.dumps(report,ensure_ascii=False)

def status():
    with _lock:
        _ready()
        import mobile_cycles as cycles
        with cycles.MobileSession(_db) as s:
            state=s.snapshot();memory=s.memory.snapshot()
        return json.dumps({'entity':'U02','snapshot':state,'bank_count':len(state['banks']),
            'memory':memory,'C11_C12_unpromoted':True,'C13_cache_disabled':True,
            'GPU_virtual_compute_ported':False,'C03':cycles._MEMO.snapshot(),
            'capability_modes':{
                'C00':'real JNI packet telemetry', 'C01':'native source-library transport',
                'C02':'runnable isolated optimistic-persistence comparator',
                'C03':'content-authenticated archive cache in main session',
                'C04':'lazy native-bank planner in main session',
                'C05':'semantic frame on each turn', 'C06':'original native observational semantic head',
                'C07':'typed evidence evaluation on request','C08':'original active-candidate comparison and clarification',
                'C09':'same-database memory inspection','C10':'original native plan/proof in safe copy',
                'C11':'runnable native learning and weight audit in laboratory copy',
                'C12':'runnable cross-block learning, heldout comparison and A-B-A',
                'C13':'runnable serial experimental comparator, not main cache',
                'C14':'runnable original ablations with real JNI measurements',
                'C15':'mobile writers/readers, rollback, replay and reopen tests; no power-loss claim'},
            'last_report_id':_last_report['id'] if _last_report else None},ensure_ascii=False)

def panel():
    _ready()
    return (_root/'docs/BBY_Q_U03_PANEL.md').read_text()

def history():
    with _lock:
        _ready()
        from integration.unified.session import Session
        with Session(_db) as s:return json.dumps(s.history()[-25:],ensure_ascii=False)

def last_report():
    with _lock:return json.dumps(_last_report,ensure_ascii=False,indent=2)
