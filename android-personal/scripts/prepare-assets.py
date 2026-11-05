#!/usr/bin/env python3
"""Restore verified existing X08 and V3 assets. No new model is trained."""
from pathlib import Path
import json,gzip,hashlib,tarfile,io,subprocess,sys,zipfile
root=Path(__file__).resolve().parents[2]
dest=root/'android-personal/app/src/main/assets/engine'
dest.mkdir(parents=True,exist_ok=True)
sha=lambda b:hashlib.sha256(b).hexdigest()
balanced=root/'integration/balance/release'
active=json.loads((balanced/'active.json').read_text()) if (balanced/'active.json').exists() else None
if active:
 assert active['schema']==1 and active['balanced'] is True
 assert sha((balanced/'evaluation.json').read_bytes())==active['evaluation_sha256']
 assert sha((root/'integration/balance/protocol.json').read_bytes())==active['protocol_sha256']
 for part in active['components']:
  assert active['components'][part]['directory']==part
  assert sha((balanced/part/'manifest.json').read_bytes())==active['components'][part]['manifest_sha256']
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
q=balanced/'v3' if active else root/'integration/quantum3/release'
qm=json.loads((q/'manifest.json').read_text())
data=(q/qm['file']).read_bytes()
assert sha(data)==qm['gzip_sha256']
assert sha(gzip.decompress(data))==qm['checkpoint_sha256']
(dest/'quantum-model.rvpbin').write_bytes(data);files['quantum-model.rvpbin']=sha(data)
for name in ['common','benchmarks','qrl3','qrl3-act','step']:
 source=root/'ai/xi/balance/qrl3-curriculum.xi' if active and name=='qrl3' else root/'ai/xi/quantum3'/f'{name}.xi'
 data=source.read_bytes()
 (dest/f'v3-{name}.xi').write_bytes(data);files[f'v3-{name}.xi']=sha(data)
identities={'chat':sha((release['model_sha256']+files['front.rxe']+files['code.rxe']).encode()),'quantum':sha((qm['checkpoint_sha256']+''.join(files['v3-'+name+'.xi'] for name in ['common','benchmarks','qrl3','step'])).encode())}
for family,label in [('qchat100','qchat'),('qmemory','qmemory')]:
 folder=balanced/family if active else root/'integration'/family/'release';m=json.loads((folder/'manifest.json').read_text());data=(folder/m['file']).read_bytes()
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
if active:
 manifest.update({'version':'BBY Q X10 Android 2.1 E01','balanced_version':'E01','training_episodes':qm['training_episodes'],'previous_identities':json.loads((root/'integration/balance/android-2.0.json').read_text())['identities']})
 manifest.pop('quantum_training_episodes_per_agent',None)
 # Test-only fixtures exercise real 2.0 -> E01 model migration without bloating the app.
 tests=root/'android-personal/app/src/androidTest/assets';tests.mkdir(parents=True,exist_ok=True)
 for label,folder in [('quantum','quantum3'),('qchat','qchat100'),('qmemory','qmemory')]:
  old=root/'integration'/folder/'release';old_manifest=json.loads((old/'manifest.json').read_text())
  (tests/('old-'+label+'.rvpbin')).write_bytes((old/old_manifest['file']).read_bytes())
 (tests/'old-identities.json').write_text(json.dumps(manifest['previous_identities']))
(dest/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
print(json.dumps({'ok':True,'files':len(files),'assets_bytes':sum(p.stat().st_size for p in dest.iterdir()),'chat_model_sha256':release['model_sha256'],'quantum_model_sha256':qm['checkpoint_sha256']}))
