#!/usr/bin/env python3
"""Cross-ABI fixtures from the exact pinned XI/RXE runtime."""
from pathlib import Path
import sys,json,subprocess,gzip,struct,hashlib
root=Path(__file__).resolve().parents[2];assets=root/'android-personal/app/src/main/assets/engine'
rt=root/'deps/reverse-pc/build/reverse_pc'
work=root/'build/personal-host';work.mkdir(parents=True,exist_ok=True)
state=work/'chat.rvp';state.write_bytes(gzip.decompress((assets/'chat-model.rvpbin').read_bytes()))
original=hashlib.sha256(state.read_bytes()).hexdigest()
def run(program):return subprocess.run([rt,'run',program,state,state],capture_output=True,text=True,check=True).stdout
F=9100000000000200000;C=F+256
def byte(address):
 b=state.read_bytes();n=struct.unpack_from('<Q',b,5)[0];prefix='O '+str(address)+' '
 for line in b[29+n:].decode().splitlines():
  if line.startswith(prefix):return int(line[len(prefix):])
 return 0
def chat(message):
 raw=message.encode();run(assets/'guard.xi')
 frame='#!reverse-pc-machine-v1\n'+''.join(f'store8 {a} {v}\n' for a,v in [(F+2,1),(F+3,0),(F+4,1),(F+8,len(raw)&255),(F+9,len(raw)>>8),(F+10,0)])
 frame+=''.join(f'store8 {C+i} {v}\n' for i,v in enumerate(raw))+'halt\n'
 p=work/'frame.xi';p.write_text(frame);run(p)
 out=run(assets/'front.rxe')
 if byte(9120000000000000002)==0:out=run(assets/'code.rxe')
 assert byte(F+3) in [1,2] and byte(F+2)==0,(message,byte(F+3),byte(F+10))
 response=bytes(e['value'] for line in out.splitlines() if line.startswith('{') for e in [json.loads(line)] if e.get('type')=='register' and e.get('register') in ['r14','r9']).decode()
 assert response.strip(),message
 run(assets/'text-finish.xi');return response
messages=['hola','calcula 17 + 25','que es ingreso y que requiere?','repite exactamente:\nHola X, música y memoria.','aprende: prueba movil\ndefinición: una leccion personal de X\nrequiere: memoria\nfuente: X\npáginas: 1','que es prueba movil y que requiere?']
fixtures=[]
for m in messages:
 r=chat(m);fixtures.append({'input':m,'response':r});print(json.dumps({'input':m,'response':r},ensure_ascii=False),flush=True)
assert '42' in fixtures[1]['response']
assert 'Hola X, música y memoria.' in fixtures[3]['response']
assert 'una leccion personal de X'.lower() in fixtures[5]['response'].lower()
(assets/'chat-fixtures.json').write_text(json.dumps(fixtures,ensure_ascii=False,indent=2)+'\n')
(work/'evidence.json').write_text(json.dumps({'ok':True,'cases':len(fixtures),'chat_seed_sha256':original,'source':'existing native XI X08','new_language_model':False},indent=2)+'\n')
test_assets=root/'android-personal/app/src/androidTest/assets';test_assets.mkdir(parents=True,exist_ok=True)
(test_assets/'migration-model.rvpbin').write_bytes(gzip.compress(state.read_bytes(),mtime=0))
sys.path.insert(0,str(root/'integration/qchat100'))
from engine import bits
inputs=json.loads((root/'integration/qchat100/release/input-vocabulary.json').read_text())
history=json.loads((root/'integration/qchat100/release/history-vocabulary.json').read_text())
cases=[('hola',[],''),('qué es memoria',['la'],'hola'),('explícalo otra vez',[],'qué es memoria'),('¡Árbol, XI! 🎸',['bby','q'],'Ether y memoria')]
(test_assets/'qchat-codec.json').write_text(json.dumps([{'prompt':p,'prefix':v,'previous':h,'bits':bits(p,v,h,inputs,history)} for p,v,h in cases],ensure_ascii=False)+'\n')
