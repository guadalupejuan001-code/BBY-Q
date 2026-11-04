#!/usr/bin/env python3
"""Restore verified existing X08 and V3 assets. No new model is trained."""
from pathlib import Path
import json,gzip,hashlib,tarfile,io
root=Path(__file__).resolve().parents[2]
dest=root/'android-personal/app/src/main/assets/engine'
dest.mkdir(parents=True,exist_ok=True)
sha=lambda b:hashlib.sha256(b).hexdigest()
release=json.loads((root/'integration/x08/release/manifest.json').read_text())
archive=root/'integration/x08/release/native.tar.gz'
assert sha(archive.read_bytes())==release['archives']['native']['sha256']
files={}
selected={'model.rvp.gz':'chat-model.rvp.gz','front.rxe':'front.rxe','code.rxe':'code.rxe','guard.xi':'guard.xi','text-finish.xi':'text-finish.xi'}
with tarfile.open(archive,'r:gz') as t:
 for source,name in selected.items():
  data=t.extractfile('native/'+source).read()
  assert sha(data)==release['archives']['native']['files'][source],source
  (dest/name).write_bytes(data);files[name]=sha(data)
assert sha(gzip.decompress((dest/'chat-model.rvp.gz').read_bytes()))==release['model_sha256']
q=root/'integration/quantum3/release'
qm=json.loads((q/'manifest.json').read_text())
data=(q/qm['file']).read_bytes()
assert sha(data)==qm['gzip_sha256']
assert sha(gzip.decompress(data))==qm['checkpoint_sha256']
(dest/'quantum-model.rvp.gz').write_bytes(data);files['quantum-model.rvp.gz']=sha(data)
for name in ['common','benchmarks','qrl3','qrl3-act']:
 data=(root/'ai/xi/quantum3'/f'{name}.xi').read_bytes()
 (dest/f'v3-{name}.xi').write_bytes(data);files[f'v3-{name}.xi']=sha(data)
manifest={'version':'BBY Q Personal X 1.0','chat':'X08-Training-Language-1','chat_model_sha256':release['model_sha256'],'concepts':release['concepts'],'relations':release['relations'],'quantum_model_sha256':qm['checkpoint_sha256'],'quantum_model_identifier':173,'qubits_per_agent':1000,'quantum_training_episodes_per_agent':10000,'quantum_backend':'native reduced/factorized; no MPS','files':files,'external_services':False,'new_conversational_quantum_model':False}
(dest/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
print(json.dumps({'ok':True,'files':len(files),'assets_bytes':sum(p.stat().st_size for p in dest.iterdir()),'chat_model_sha256':release['model_sha256'],'quantum_model_sha256':qm['checkpoint_sha256']}))
