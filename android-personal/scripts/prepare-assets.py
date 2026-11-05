#!/usr/bin/env python3
"""Restore verified existing X08 and V3 assets. No new model is trained."""
from pathlib import Path
import json,gzip,hashlib,tarfile,io,subprocess,sys,zipfile
root=Path(__file__).resolve().parents[2]
dest=root/'android-personal/app/src/main/assets/engine'
dest.mkdir(parents=True,exist_ok=True)
sha=lambda b:hashlib.sha256(b).hexdigest()
release=json.loads((root/'integration/x08/release/manifest.json').read_text())
archive=root/'integration/x08/release/native.tar.gz'
files={}
selected={'model.rvp.gz':'chat-model.rvpbin','front.rxe':'front.rxe','code.rxe':'code.rxe','guard.xi':'guard.xi','text-finish.xi':'text-finish.xi'}
if len(sys.argv)==3 and sys.argv[1]=='--base-apk':
 with zipfile.ZipFile(sys.argv[2]) as z:
  prior=json.loads(z.read('assets/engine/manifest.json'))
  for source,name in selected.items():
   data=z.read('assets/engine/'+name)
   assert sha(data)==release['archives']['native']['files'][source],source
   (dest/name).write_bytes(data);files[name]=sha(data)
else:
 assert sha(archive.read_bytes())==release['archives']['native']['sha256']
 with tarfile.open(archive,'r:gz') as t:
  for source,name in selected.items():
   data=t.extractfile('native/'+source).read()
   assert sha(data)==release['archives']['native']['files'][source],source
   (dest/name).write_bytes(data);files[name]=sha(data)
assert sha(gzip.decompress((dest/'chat-model.rvpbin').read_bytes()))==release['model_sha256']
q=root/'integration/quantum3/release'
qm=json.loads((q/'manifest.json').read_text())
data=(q/qm['file']).read_bytes()
assert sha(data)==qm['gzip_sha256']
assert sha(gzip.decompress(data))==qm['checkpoint_sha256']
(dest/'quantum-model.rvpbin').write_bytes(data);files['quantum-model.rvpbin']=sha(data)
for name in ['common','benchmarks','qrl3','qrl3-act','step']:
 data=(root/'ai/xi/quantum3'/f'{name}.xi').read_bytes()
 (dest/f'v3-{name}.xi').write_bytes(data);files[f'v3-{name}.xi']=sha(data)
identities={'chat':release['model_sha256'],'quantum':qm['checkpoint_sha256']}
for family,label in [('qchat100','qchat'),('qmemory','qmemory')]:
 folder=root/'integration'/family/'release';m=json.loads((folder/'manifest.json').read_text());data=(folder/m['file']).read_bytes()
 assert sha(data)==m['gzip_sha256']
 assert sha(gzip.decompress(data))==m['checkpoint_sha256']
 (dest/(label+'-model.rvpbin')).write_bytes(data)
 source=(root/'ai/xi'/family/'model.xi').read_bytes()
 if 'native_source_sha256' in m:assert sha(source)==m['native_source_sha256']
 (dest/(label+'-model.xi')).write_bytes(source)
 identities[label]=sha((m['checkpoint_sha256']+sha(source)).encode())
 if family=='qchat100':
  for name in ['vocabulary','input-vocabulary','history-vocabulary']:
   data=(folder/(name+'.json')).read_bytes();assert sha(data)==m[name.replace('-','_')+'_sha256']
   (dest/('qchat-'+name+'.json')).write_bytes(data)
subprocess.run(['node',str(root/'android-personal/scripts/prepare-unified.mjs')],check=True)
for p in dest.iterdir():
 if p.name not in ['manifest.json','chat-fixtures.json']:files[p.name]=sha(p.read_bytes())
manifest={'version':'BBY Q X10 Android 2.0','chat':'X10-Android-2','chat_seed':'X08-Training-Language-1','chat_model_sha256':release['model_sha256'],'concepts':release['concepts'],'relations':release['relations'],'quantum_model_sha256':qm['checkpoint_sha256'],'quantum_model_identifier':173,'qubits_per_agent':1000,'quantum_training_episodes_per_agent':10000,'quantum_backend':'native reduced/factorized; no MPS','files':files,'identities':identities,'external_services':False,'new_conversational_quantum_model':False,'session_storage':'one SQLite transaction: states, lessons, context, history, receipts','scope':{'x10_native_roles':['intent','lessons','stream','reason','compose','context','paraphrase'],'qchat100':'preserved small word generator, fixed Clifford encoder','qmemory':'250 keyed binary associations; trained write gate, replacement and readout','v3':'preserved numeric classifier and line-navigation policy','desktop_modules_preserved':True}}
(dest/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
print(json.dumps({'ok':True,'files':len(files),'assets_bytes':sum(p.stat().st_size for p in dest.iterdir()),'chat_model_sha256':release['model_sha256'],'quantum_model_sha256':qm['checkpoint_sha256']}))
