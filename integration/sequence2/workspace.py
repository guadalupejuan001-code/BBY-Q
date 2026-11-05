"""Transactional C1 successor: learned readers and grounded native XI tools.

SQLite publishes a whole sparse native checkpoint and its exact dictionaries
with one result. A failed task or crash cannot publish only its first steps.
"""
import copy,gzip,hashlib,json,sqlite3,tempfile,unicodedata
from pathlib import Path
import engine as E
from schema import ROOT
from tools import Tools,build_zero,expand

def encoded(value):return json.dumps(value,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()
def digest(value):return hashlib.sha256(value).hexdigest()

class ContextText(E.Model):
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        self.library+='\n'+expand((ROOT/'ai/xi/sequence2/context.xi.in').read_text())
    def prepare(self,*args,**kwargs):
        value=super().prepare(*args,**kwargs)
        import data as D
        topics=[self.codec.ids[topic] for topic,_ in D.TOPICS]
        self.run(E.stage64(E.C+500,[len(topics)])+E.stage64(E.C+512,topics)+'call c2_text_context')
        return value

def read_models(folder):
    folder=Path(folder);manifest=folder/'manifest.json'
    if manifest.exists():
        m=json.loads(manifest.read_text());models={}
        for source,sha in m.get('sources',{}).items():
            if E.sha(ROOT/source)!=sha:raise ValueError('Frozen source identity mismatch: '+source)
        binding=m['binding']
        for name,key in [('vocabulary.json','vocabulary_sha256'),('output-vocabulary.json','output_vocabulary_sha256'),('semantic-vocabulary.json','semantic_vocabulary_sha256')]:
            if key not in binding:continue
            actual=json.loads((folder/name).read_text())
            if digest(encoded(actual))!=binding[key]:raise ValueError('Checkpoint dictionary binding mismatch')
        if E.sha(folder/'model.xi')!=binding['native_source_sha256']:raise ValueError('Checkpoint source binding mismatch')
        for name,item in m['models'].items():
            chunks=[]
            for part in item['parts']:
                raw=(folder/part['file']).read_bytes()
                if len(raw)!=part['bytes'] or digest(raw)!=part['sha256']:raise ValueError('Corrupt checkpoint part')
                chunks.append(raw)
            packed=b''.join(chunks)
            if digest(packed)!=item['gzip_sha256']:raise ValueError('Corrupt packed checkpoint')
            raw=gzip.decompress(packed)
            if digest(raw)!=item['checkpoint_sha256']:raise ValueError('Corrupt native checkpoint')
            models[name]=raw
    else:
        selection=json.loads((folder/'selection.json').read_text());models={}
        for name,entry in selection.items():
            raw=(folder/entry['path']).read_bytes()
            if digest(raw)!=entry['sha256']:raise ValueError('Selected native checkpoint changed')
            models[name]=raw
    if set(models)!={'text','intent'}:raise ValueError('Both selected readers are required')
    return models

class Workspace:
    def __init__(self,database,readers=None):
        self.folder=Path(readers or ROOT/'integration/sequence2/release')
        self.models=read_models(self.folder)
        self.vocabulary=json.loads((self.folder/'vocabulary.json').read_text())
        self.output=json.loads((self.folder/'output-vocabulary.json').read_text())
        self.native=(self.folder/'model.xi').read_text()
        semantic=self.folder/'semantic-vocabulary.json'
        self.semantic=semantic.read_bytes() if semantic.exists() else None
        build_zero()
        paths=[ROOT/'integration/sequence2/engine.py',ROOT/'integration/sequence2/tools.py',ROOT/'integration/sequence2/workspace.py',ROOT/'integration/sequence2/schema.py',ROOT/'integration/sequence2/data.py',
               ROOT/'integration/sequence2/grammar.py',ROOT/'ai/xi/sequence2/tools.xi.in',ROOT/'ai/xi/sequence2/context.xi.in',
               ROOT/'ai/personal/zero/core.xi.in',ROOT/'ai/personal/zero/model.mjs',ROOT/'ai/personal/zero/schema.mjs']
        self.identity={'models':{k:digest(v) for k,v in self.models.items()},
                       'vocabulary':digest(encoded(self.vocabulary)),'output':digest(encoded(self.output)),
                       'native':digest(self.native.encode()),
                       'semantic_vocabulary':digest(self.semantic) if self.semantic is not None else None,
                       'sources':{str(p.relative_to(ROOT)):E.sha(p) for p in paths}}
        database=Path(database);database.parent.mkdir(parents=True,exist_ok=True)
        self.db=sqlite3.connect(str(database),timeout=60,isolation_level=None)
        self.db.execute('PRAGMA journal_mode=WAL');self.db.execute('PRAGMA synchronous=FULL')
        self.db.execute('CREATE TABLE IF NOT EXISTS state (id INTEGER PRIMARY KEY CHECK(id=1), snapshot BLOB NOT NULL, sha TEXT NOT NULL, metadata BLOB NOT NULL, metadata_sha TEXT NOT NULL, identity BLOB NOT NULL, revision INTEGER NOT NULL)')
        self.db.execute('CREATE TABLE IF NOT EXISTS requests (id TEXT PRIMARY KEY, fingerprint TEXT NOT NULL, result BLOB NOT NULL)')
        self.db.execute('BEGIN IMMEDIATE')
        try:
            row=self.db.execute('SELECT identity FROM state WHERE id=1').fetchone()
            if row is None:
                raw=self.models['intent'];metadata={'vocabulary':self.vocabulary,'entities':{},'previous':''}
                self.db.execute('INSERT INTO state VALUES(1,?,?,?,?,?,0)',(raw,digest(raw),encoded(metadata),digest(encoded(metadata)),encoded(self.identity)))
            elif json.loads(row[0])!=self.identity:raise ValueError('Workspace source/model identity changed; explicit migration required')
            self.db.execute('COMMIT')
        except BaseException:self.db.execute('ROLLBACK');self.close();raise

    def __enter__(self):return self
    def __exit__(self,*args):self.close()
    def close(self):self.db.close()

    def snapshot(self):
        row=self.db.execute('SELECT sha,metadata,revision FROM state WHERE id=1').fetchone()
        return {'sha256':row[0],'metadata_sha256':digest(row[1]),'revision':row[2]}

    def turn(self,request_id,prompt,fail_after=None,ablate_intent=False):
        if not isinstance(prompt,str) or not isinstance(request_id,str) or not request_id:raise ValueError('A text prompt and nonempty request ID are required')
        fingerprint=digest(encoded({'text':prompt,'ablate_intent':ablate_intent}))
        self.db.execute('BEGIN IMMEDIATE')
        try:
            prior=self.db.execute('SELECT fingerprint,result FROM requests WHERE id=?',(request_id,)).fetchone()
            if prior:
                if prior[0]!=fingerprint:raise ValueError('Request ID was already used for different input')
                self.db.execute('COMMIT');return json.loads(prior[1])
            raw,expected,metadata,metadata_sha,identity,revision=self.db.execute('SELECT snapshot,sha,metadata,metadata_sha,identity,revision FROM state WHERE id=1').fetchone()
            if digest(raw)!=expected:raise ValueError('Corrupt native workspace snapshot')
            if digest(metadata)!=metadata_sha:raise ValueError('Corrupt native workspace dictionaries')
            if json.loads(identity)!=self.identity:raise ValueError('Workspace identity mismatch')
            before=json.loads(metadata);next_meta=copy.deepcopy(before)
            result=None;next_raw=raw
            with tempfile.TemporaryDirectory(prefix='bbyq-c1-turn-') as temporary:
                local=Path(temporary);state=local/'intent.rvp';state.write_bytes(raw);(local/'model.xi').write_text(self.native)
                if self.semantic is not None:(local/'semantic-vocabulary.json').write_bytes(self.semantic)
                with E.Model(state,next_meta['vocabulary'],self.output) as model:
                    # The prediction is the learned XI result. Structural
                    # parsing cannot overwrite a disagreement with a label.
                    prediction=model.intent(prompt,ablate=ablate_intent)
                    adapter=Tools(model,next_meta);parsed=adapter.parse(prompt)
                    label=prediction['intent']
                    if parsed and parsed['intent']==label:
                        result=adapter.execute(parsed,fail_after=fail_after)
                        result.update({'intent':label,'rule':parsed['rule'],'reader_log_probability':prediction['log_probability']})
                    elif parsed:
                        result={'ok':False,'status':0,'intent':label,'reason':'Reader and tool contract disagree','expected_contract':parsed['intent'],'results':[]}
                    elif label!=1:
                        result={'ok':False,'status':0,'intent':label,'reason':'No supported grounded contract','results':[]}
                    else:
                        text_state=local/'text.rvp';text_state.write_bytes(self.models['text'])
                        with ContextText(text_state,self.vocabulary,self.output) as text:
                            generated=text.generate(prompt,before.get('previous',''))
                        refusal=generated['tokens']==E.output_words('necesito más ejemplos para aprender .')
                        result={'ok':generated['terminated'] and not refusal,'status':0 if refusal else 1,
                                'intent':label,'results':[{'kind':'text',**generated}]}
                    if result['ok'] and not any(r['kind']=='cancel' for r in result['results']):
                        next_meta['vocabulary']=list(model.codec.words)
                        next_meta['previous']=prompt if len(E.words(prompt))<=64 else ''
                        next_meta['previous_supported']=len(E.words(prompt))<=64
                        saved=local/'next.rvp';model.s.save(saved);next_raw=saved.read_bytes()
                    else:next_meta=before
            result['request_id']=request_id;result['committed']=bool(result['ok'] and not any(r['kind']=='cancel' for r in result['results']))
            if result['committed']:
                self.db.execute('UPDATE state SET snapshot=?,sha=?,metadata=?,metadata_sha=?,revision=? WHERE id=1',
                                (next_raw,digest(next_raw),encoded(next_meta),digest(encoded(next_meta)),revision+1))
            self.db.execute('INSERT INTO requests VALUES(?,?,?)',(request_id,fingerprint,encoded(result)))
            self.db.execute('COMMIT');return result
        except BaseException:
            self.db.execute('ROLLBACK');raise
