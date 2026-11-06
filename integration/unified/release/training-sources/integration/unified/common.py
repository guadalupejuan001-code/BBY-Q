"""Pinned native components and transport shared by the unified entity."""
import gzip,hashlib,importlib.util,json,struct,sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'integration/sequence2'))
import engine as C1
import workspace as Legacy
import tools as C1Tools
import data as C1Data
from grammar import Rule

def module(name,path):
    spec=importlib.util.spec_from_file_location(name,path);result=importlib.util.module_from_spec(spec);spec.loader.exec_module(result);return result

Entity=module('bbyq_unified_original_entity',ROOT/'integration/entity/engine.py')
XiSession=C1.XiSession
A=Entity.A;Q=Entity.Q;M=Entity.M;E=Entity.E

def encoded(value):return json.dumps(value,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()
def digest(value):return hashlib.sha256(value).hexdigest()
def read(path):return json.loads(Path(path).read_text())
def write(path,value):Path(path).write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n')
def key(value):return ' '.join(C1.words(value))

def entity_models():
    folder=ROOT/'integration/entity/release';m=read(folder/'manifest.json');result={}
    if not m['passed']:raise ValueError('E02 was not qualified')
    for path,sha in m['native_source_sha256'].items():
        if C1.sha(ROOT/path)!=sha:raise ValueError('E02 native source identity changed')
    for name,item in m['models'].items():
        packed=(folder/item['file']).read_bytes()
        if digest(packed)!=item['gzip_sha256']:raise ValueError('Corrupt E02 model')
        raw=gzip.decompress(packed)
        if digest(raw)!=item['checkpoint_sha256']:raise ValueError('Corrupt E02 checkpoint')
        result[name]=raw
    return result

QUANTUM_LIBRARY=Entity.LIB+'\n'+(ROOT/'ai/xi/entity/feedback.xi').read_text()
def run(session,body):
    return session.execute('#!reverse-pc-machine-v1\nbudget 100000000\n'+body+'\nhalt\n'+QUANTUM_LIBRARY)[0]
def metrics(events):return Entity.metrics(events)
def integer(session,address):return struct.unpack('<q',material(session,address,8))[0]
def floating(session,address):return struct.unpack('<d',material(session,address,8))[0]
def material(session,address,size):
    events=run(session,f'mem_materialize {address} {size}')
    return bytes.fromhex(next(event['hex'] for event in events if event.get('type')=='memory_materialization'))
def stage_bytes(address,value):return C1.stage_bytes(address,value)

def source_identity():
    paths=[*sorted((ROOT/'integration/unified').glob('*.py')),*sorted((ROOT/'ai/xi/unified').glob('*'))]
    return {str(path.relative_to(ROOT)):C1.sha(path) for path in paths if path.is_file()}
