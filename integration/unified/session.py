"""One durable entity: C1, VQC3, QRL3, QMemory, QChat and E02.

All banks, dictionaries, task frames, feedback and receipts commit under the
same SQLite transaction. The original C1 table remains a compatible view of
the same language state, including pre-existing personal facts.
"""
import copy,gzip,json,sqlite3,struct,tempfile
from contextlib import ExitStack
from pathlib import Path
from .common import ROOT,C1,C1Tools,Legacy,Entity,A,E,encoded,digest,read,key,entity_models,source_identity,integer,floating,run
from .contracts import Tools,RULES
from .quantum import Quantum,natural,observations

def router_model(folder):
    folder=Path(folder)
    if (folder/'manifest.json').exists():
        manifest=read(folder/'manifest.json');pieces=[]
        for part in manifest['router']['parts']:
            raw=(folder/part['file']).read_bytes()
            if digest(raw)!=part['sha256']:raise ValueError('Corrupt unified reader part')
            pieces.append(raw)
        raw=gzip.decompress(b''.join(pieces))
        if digest(raw)!=manifest['router']['sha256']:raise ValueError('Corrupt unified reader')
        for name,sha in manifest['binding'].items():
            if C1.sha(folder/name)!=sha:raise ValueError('Unified dictionary/source binding changed')
        for name,sha in manifest['sources'].items():
            if C1.sha(ROOT/name)!=sha:raise ValueError('Unified deployment identity changed: '+name)
    else:
        selected=read(folder/'selected.json');raw=(folder/selected['path']).read_bytes()
        if digest(raw)!=selected['sha256']:raise ValueError('Unified training selection changed')
    return raw

def perception_model(folder):
    folder=Path(folder)
    if (folder/'manifest.json').exists():
        item=read(folder/'manifest.json').get('perception')
        if item is None:return None
        packed=(folder/item['file']).read_bytes()
        if digest(packed)!=item['gzip_sha256']:raise ValueError('Corrupt unified perception archive')
        raw=gzip.decompress(packed)
    elif (folder/'perception-selected.json').exists():
        item=read(folder/'perception-selected.json');raw=(folder/item['path']).read_bytes()
    else:return None
    if digest(raw)!=item['sha256']:raise ValueError('Corrupt unified perception parameters')
    return raw

class Session:
    def __init__(self,database,readers=None):
        self.folder=Path(readers or ROOT/'integration/unified/release');router=router_model(self.folder)
        self.router_words=read(self.folder/'vocabulary.json');self.output=read(self.folder/'output-vocabulary.json')
        self.router_native=(self.folder/'model.xi').read_bytes();self.router_semantic=(self.folder/'semantic-vocabulary.json').read_bytes()
        self.legacy=Legacy.Workspace(database);self.db=self.legacy.db
        self.initial={'router':router,'text':self.legacy.models['text'],**entity_models()}
        perception=perception_model(self.folder)
        if perception is not None:self.initial['v3']=perception
        self.identity={'version':'U01','c1':self.legacy.identity,'models':{n:digest(v) for n,v in self.initial.items()},'router_words':digest(encoded(self.router_words)),'router_native':digest(self.router_native),'router_semantic':digest(self.router_semantic),'sources':source_identity()}
        self.db.executescript('''
          CREATE TABLE IF NOT EXISTS unified_state(id INTEGER PRIMARY KEY CHECK(id=1),metadata BLOB NOT NULL,sha TEXT NOT NULL,identity BLOB NOT NULL,revision INTEGER NOT NULL);
          CREATE TABLE IF NOT EXISTS unified_banks(name TEXT PRIMARY KEY,snapshot BLOB NOT NULL,sha TEXT NOT NULL);
          CREATE TABLE IF NOT EXISTS unified_requests(id TEXT PRIMARY KEY,fingerprint TEXT NOT NULL,result BLOB NOT NULL);
          CREATE TABLE IF NOT EXISTS unified_tasks(id TEXT PRIMARY KEY,frame BLOB NOT NULL,sha TEXT NOT NULL,feedback_id TEXT);
          CREATE TABLE IF NOT EXISTS unified_supervision(name TEXT PRIMARY KEY,value INTEGER NOT NULL);
          CREATE TABLE IF NOT EXISTS unified_task_supervision(id TEXT PRIMARY KEY,rule INTEGER NOT NULL);
        ''')
        self.db.execute('BEGIN IMMEDIATE')
        try:
            row=self.db.execute('SELECT identity FROM unified_state WHERE id=1').fetchone()
            if row is None:
                raw,sha,metadata,metadata_sha=self.db.execute('SELECT snapshot,sha,metadata,metadata_sha FROM state WHERE id=1').fetchone()
                if digest(raw)!=sha or digest(metadata)!=metadata_sha:raise ValueError('Corrupt existing C1 session')
                meta={'associations':{},'observations':{},'projections':{},'previous':'','language_sync':[sha,metadata_sha]}
                self.db.execute('INSERT INTO unified_state VALUES(1,?,?,?,0)',(encoded(meta),digest(encoded(meta)),encoded(self.identity)))
                for name,value in {'language':raw,**self.initial}.items():self.db.execute('INSERT INTO unified_banks VALUES(?,?,?)',(name,value,digest(value)))
            elif json.loads(row[0])!=self.identity:raise ValueError('Unified source/model identity changed; explicit migration required')
            self.db.execute('COMMIT')
        except BaseException:self.db.execute('ROLLBACK');self.close();raise

    def __enter__(self):return self
    def __exit__(self,*args):self.close()
    def close(self):self.legacy.close()

    def snapshot(self):
        row=self.db.execute('SELECT sha,revision FROM unified_state WHERE id=1').fetchone()
        return {'revision':row[1],'metadata_sha256':row[0],'banks':dict(self.db.execute('SELECT name,sha FROM unified_banks')),'language':self.legacy.snapshot(),'tasks':self.db.execute('SELECT count(*) FROM unified_tasks').fetchone()[0],'feedback':self.db.execute('SELECT count(*) FROM unified_tasks WHERE feedback_id IS NOT NULL').fetchone()[0]}

    def history(self):
        # Old and unified clients see one request namespace. Unified receipts
        # are mirrored into requests, so legacy history remains complete.
        return [json.loads(row[0]) for row in self.db.execute('SELECT result FROM requests ORDER BY rowid')]

    def _banks(self):
        result={}
        for name,raw,sha in self.db.execute('SELECT name,snapshot,sha FROM unified_banks'):
            if digest(raw)!=sha:raise ValueError('Corrupt unified bank: '+name)
            result[name]=raw
        return result

    def _task(self,identifier):
        row=self.db.execute('SELECT frame,sha,feedback_id FROM unified_tasks WHERE id=?',(identifier,)).fetchone()
        if row is None:raise ValueError('No completed shared task is available')
        if digest(row[0])!=row[1]:raise ValueError('Corrupt shared task frame')
        return json.loads(row[0]),row[2]

    def turn(self,request_id,prompt,payload=None,fail_after=None,control=None):
        if not isinstance(prompt,str) or not isinstance(request_id,str) or not request_id:raise ValueError('Text and nonempty request ID are required')
        if payload is not None:
            if not isinstance(payload,dict) or set(payload)-{'observations','labels'}:raise ValueError('Unsupported typed payload field')
            if 'observations' in payload:observations(payload['observations'])
            if 'labels' in payload:
                if not isinstance(payload['labels'],dict) or set(payload['labels'])!={'class','rule'}:raise ValueError('Feedback needs class and rule labels')
                for value in payload['labels'].values():natural(value,1)
        fingerprint=digest(encoded({'text':prompt,'payload':payload,'control':control}))
        legacy_fingerprint=digest(encoded({'text':prompt,'ablate_intent':False})) if payload is None and control is None else fingerprint
        self.db.execute('BEGIN IMMEDIATE')
        try:
            prior=self.db.execute('SELECT fingerprint,result FROM unified_requests WHERE id=?',(request_id,)).fetchone()
            if prior:
                if prior[0]!=fingerprint:raise ValueError('Request ID was already used for different input')
                self.db.execute('COMMIT');return json.loads(prior[1])
            prior=self.db.execute('SELECT fingerprint,result FROM requests WHERE id=?',(request_id,)).fetchone()
            if prior:
                if prior[0]!=legacy_fingerprint:raise ValueError('Request ID was already used by the language client')
                self.db.execute('COMMIT');return json.loads(prior[1])
            raw_meta,sha,identity,revision=self.db.execute('SELECT metadata,sha,identity,revision FROM unified_state WHERE id=1').fetchone()
            if digest(raw_meta)!=sha or json.loads(identity)!=self.identity:raise ValueError('Corrupt unified metadata or identity')
            meta=json.loads(raw_meta);banks=self._banks()
            lang_raw,lang_sha,lang_meta,lang_meta_sha,lang_identity,lang_revision=self.db.execute('SELECT snapshot,sha,metadata,metadata_sha,identity,revision FROM state WHERE id=1').fetchone()
            if digest(lang_raw)!=lang_sha or digest(lang_meta)!=lang_meta_sha or json.loads(lang_identity)!=self.legacy.identity:raise ValueError('Corrupt compatible language state')
            language_meta=json.loads(lang_meta)
            if meta['language_sync']!=[lang_sha,lang_meta_sha]:
                banks['language']=lang_raw;meta['previous']=language_meta.get('previous','')
            self.db.execute('SAVEPOINT operations')
            with tempfile.TemporaryDirectory(prefix='bbyq-one-entity-') as temporary,ExitStack() as stack:
                local=Path(temporary);language_dir=local/'language';router_dir=local/'router';language_dir.mkdir();router_dir.mkdir()
                (language_dir/'model.xi').write_text(self.legacy.native);(language_dir/'semantic-vocabulary.json').write_bytes(self.legacy.semantic)
                (router_dir/'model.xi').write_bytes(self.router_native);(router_dir/'semantic-vocabulary.json').write_bytes(self.router_semantic)
                paths={}
                for name,value in banks.items():
                    path=(language_dir if name in ('language','text') else router_dir if name=='router' else local)/(name+'.rvp');path.write_bytes(value);paths[name]=path
                language=stack.enter_context(C1.Model(paths['language'],language_meta['vocabulary'],self.output))
                router=stack.enter_context(C1.Model(paths['router'],meta.get('router_vocabulary',self.router_words),self.output))
                adapter=Tools(language,language_meta)
                predicted=router.intent(prompt);parsed=adapter.parse(prompt)
                sessions={name:stack.enter_context(C1.XiSession(C1.RT/'build/xi_session',paths[name])) for name in ('v3','memory','voice','entity')}
                def project(name,classification,probability,input_sha):
                    subject='observación '+name;canonical=key(subject);base=adapter.base;es=base.zero_schema['words']['es'];old=meta.setdefault('projections',{}).get(canonical)
                    if old and old['class']!=classification:
                        args=[base.entity(subject),es,base.entity('clase uno' if old['class'] else 'clase cero'),-1,2]
                        language.run(C1.stage64(C1Tools.A['ARG'],args)+'call c2_put')
                        if base.integer(56)!=1:raise ValueError('Native projection capacity exceeded')
                    label='clase uno' if classification else 'clase cero'
                    language.run(C1.stage64(C1Tools.A['ARG'],[base.entity(subject),es,base.entity(label),1,2])+'call c2_put')
                    if base.integer(56)!=1:raise ValueError('Native projection capacity exceeded')
                    meta['projections'][canonical]={'class':classification,'probability':probability,'input_sha256':input_sha}
                    return {'subject':subject,'predicate':'es','value':label,'probability':probability,'input_sha256':input_sha,'source':'VQC3 prediction'}
                quantum=Quantum(sessions,meta,local,project);results=[];trace=[{'bank':'router','operation':'c1_encode_input/c1_next','native':True,'qubits':100,'intent':predicted['intent']}]
                if parsed and predicted['intent']==parsed['intent']:
                    if parsed['domain']=='language':
                        if payload:raise ValueError('Typed payload requires a matching quantum contract')
                        result=adapter.base.execute(parsed,fail_after=fail_after)
                        result['trace']=trace+result['trace']
                    else:
                        captures=parsed['captures'];actions=RULES[parsed['rule']-1].actions;result={'ok':True,'status':1,'results':results}
                        if payload and 'observations' in payload and sum(a[0]=='observe' for a in actions)!=1:raise ValueError('Observation payload requires one observation action')
                        if payload and 'labels' in payload and not any(a[0]=='feedback' for a in actions):raise ValueError('Supervision labels are accepted only by explicit feedback')
                        for index,action in enumerate(actions):
                            op=action[0];args=[captures.get(name) if name is not None else None for name in action[1:]]
                            if op=='remember':
                                value=quantum.remember(*args);bit=value.pop('supervision');self.db.execute('INSERT INTO unified_supervision VALUES(?,?) ON CONFLICT(name) DO UPDATE SET value=excluded.value',(key(args[0]),bit))
                            elif op=='recall':value=quantum.recall(*args)
                            elif op=='observe':value=quantum.observe(*args,payload=(payload or {}).get('observations'))
                            elif op=='plan':value=quantum.standalone_plan(*args)
                            elif op=='mission':
                                value=quantum.mission(*args,control=control)
                                if value['status']==1:
                                    task_id=request_id+':'+str(index);raw=encoded(value)
                                    self.db.execute('INSERT INTO unified_tasks VALUES(?,?,?,NULL)',(task_id,raw,digest(raw)))
                                    taught=self.db.execute('SELECT value FROM unified_supervision WHERE name=?',(key(value['association']),)).fetchone()
                                    if taught:self.db.execute('INSERT INTO unified_task_supervision VALUES(?,?)',(task_id,taught[0]))
                                    meta['last_task']=task_id;value={k:v for k,v in value.items() if k not in ('frame_hex','input')};value['task_id']=task_id
                            elif op=='explain':
                                task,_=self._task(meta.get('last_task',''));value={k:v for k,v in task.items() if k not in ('frame_hex','input')};value['kind']='explain';value['status']=1
                            elif op=='status':value={'kind':'status','status':1,'entity':'U01','components':['C1','VQC3','QRL3','QMemory','QChat100','E02'],'associations':len(meta.get('associations',{})),'observations':len(meta.get('observations',{})),'single_transaction':True}
                            elif op=='cancel':value={'kind':'cancel','status':1,'text':'De acuerdo; no ejecutaré esa petición.'}
                            elif op=='feedback':
                                task_id=meta.get('last_task','');task,feedback=self._task(task_id)
                                if feedback is not None:raise ValueError('This task already received feedback; replay the original request ID')
                                teacher=(payload or {}).get('labels')
                                if teacher is None and task['input'] and task['input']['kind']=='synthetic':
                                    taught=self.db.execute('SELECT rule FROM unified_task_supervision WHERE id=?',(task_id,)).fetchone()
                                    if taught:
                                        # Labels are read only in this feedback branch.
                                        run(sessions['v3'],quantum.input_body(task['input']));teacher={'class':int(floating(sessions['v3'],A+128)),'rule':taught[0]}
                                value=quantum.feedback(task,*args,teacher=teacher)
                                # Continue the same learned reader on its verified
                                # contract; keep the text head's parameters intact.
                                router.run(router.active([],head=1)+f'store64 {C1.C+64} {parsed["intent"]}\nfstore {C1.C+112} .01\ncall c1_train')
                                value['updates']['router']=1
                                self.db.execute('UPDATE unified_tasks SET feedback_id=? WHERE id=?',(request_id,task_id));value['task_id']=task_id
                            else:raise ValueError('Unsupported shared operation')
                            results.append(value)
                            if value['status'] not in (1,-1):result.update(ok=False,status=value['status']);break
                            if fail_after==index+1:raise RuntimeError('Injected failure after shared operation')
                        result['trace']=trace+quantum.trace
                elif parsed:result={'ok':False,'status':0,'reason':'Learned reader and contract disagree','expected_contract':parsed['intent'],'results':[],'trace':trace}
                elif payload:raise ValueError('Typed payload requires a supported contract')
                elif predicted['intent']!=1:result={'ok':False,'status':0,'reason':'No supported grounded contract','results':[],'trace':trace}
                else:
                    text=stack.enter_context(Legacy.ContextText(paths['text'],self.legacy.vocabulary,self.output));generated=text.generate(prompt,meta.get('previous') or language_meta.get('previous',''))
                    refusal=generated['tokens']==C1.output_words('necesito más ejemplos para aprender .')
                    result={'ok':generated['terminated'] and not refusal,'status':0 if refusal else 1,'results':[{'kind':'text',**generated}],'trace':trace+[{'bank':'text','operation':'c1_encode_input/c1_next','native':True,'qubits':100}]}
                result.update(request_id=request_id,intent=predicted['intent'],reader_log_probability=predicted['log_probability'],entity='U01')
                result['committed']=bool(result['ok'] and not any(v['kind']=='cancel' for v in result['results']))
                if result['committed']:
                    language_meta['vocabulary']=list(language.codec.words);language_meta['previous']=prompt if len(C1.words(prompt))<=64 else '';language_meta['previous_supported']=len(C1.words(prompt))<=64
                    meta['previous']=language_meta['previous'];meta['router_vocabulary']=list(router.codec.words)
                    changed={'language':language.s,**{name:sessions[name] for name in {t['bank'] for t in quantum.trace} if name in sessions}}
                    if any(v['kind']=='feedback' for v in result['results']):changed['router']=router.s
                    for name,native in changed.items():
                        destination=local/('next-'+name+'.rvp');native.save(destination);raw=destination.read_bytes();banks[name]=raw
                        self.db.execute('UPDATE unified_banks SET snapshot=?,sha=? WHERE name=?',(raw,digest(raw),name))
                    raw=banks['language'];metadata=encoded(language_meta);meta['language_sync']=[digest(raw),digest(metadata)]
                    self.db.execute('UPDATE state SET snapshot=?,sha=?,metadata=?,metadata_sha=?,revision=? WHERE id=1',(raw,digest(raw),metadata,digest(metadata),lang_revision+1))
                    metadata=encoded(meta);self.db.execute('UPDATE unified_state SET metadata=?,sha=?,revision=? WHERE id=1',(metadata,digest(metadata),revision+1))
                else:self.db.execute('ROLLBACK TO operations')
                self.db.execute('RELEASE operations')
            self.db.execute('INSERT INTO unified_requests VALUES(?,?,?)',(request_id,fingerprint,encoded(result)))
            self.db.execute('INSERT INTO requests VALUES(?,?,?)',(request_id,legacy_fingerprint,encoded(result)))
            self.db.execute('COMMIT');return result
        except BaseException:self.db.execute('ROLLBACK');raise
