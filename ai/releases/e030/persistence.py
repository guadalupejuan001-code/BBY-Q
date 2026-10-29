#!/usr/bin/env python3
"""Checkpoint transport and external retention examiner. No learning algorithm here."""
import argparse,base64,gzip,hashlib,importlib.util,json,shutil,subprocess
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('runtime');p.add_argument('download');p.add_argument('output');a=p.parse_args()
runtime=str(Path(a.runtime).resolve());src=Path(a.download).resolve();out=Path(a.output).resolve();out.mkdir(parents=True,exist_ok=True)
spec=importlib.util.spec_from_file_location('snapshot_reader',Path('ai/xi/knowledge/tests/native-knowledge.py'));mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
snap=mod.snapshot;T=9200000000000000000;size=3072
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
old=src/'e030-learning/learned-checkpoint.rvp';seed=src/'e029/controller.rvp';app=src/'e029/learned.rxe'
assert sha(old)=='5a0d469fc70248a2afc7a6a319a9a854d6498fa7682d9351e543f0d701ae7cf6'
assert sha(seed)=='ce058a65092dd9892b6fd55276a17287b764a16bc526ccbfa0085154baef9631'
assert sha(app)=='c9a33a322f58ac6d93f18ff3c59678ef637ac9612bb71845e122e8f5c9de43f9'
original=snap(old);base=snap(seed)
dense=bytes(original[1].get(T+i,0) for i in range(size))
assert dense[0]==1 and dense[1024]==2 and dense[1280]==2
assert not any(dense[16:1024])
portable={'format':'BBYQ-E030-pattern-region-v1','base_address':str(T),'length':size,
 'source_checkpoint_sha256':sha(old),'seed_sha256':sha(seed),'app_sha256':sha(app),
 'sha256':hashlib.sha256(dense).hexdigest(),'bytes_base64':base64.b64encode(dense).decode()}
(out/'patterns.json').write_text(json.dumps(portable,indent=2)+'\n')
# Transport exact native output bytes, without interpreting or inducing patterns.
restore=out/'restore.xi'
restore.write_text('#!reverse-pc-machine-v1\n'+''.join('store8 %d %d\n'%(T+i,v) for i,v in enumerate(dense) if v)+'halt\n')
clean=out/'patterns-only.rvp'
subprocess.run([runtime,'run',str(restore),str(seed),str(clean)],check=True,capture_output=True,text=True)
result=snap(clean)
def outside(s):return s[0],{k:v for k,v in s[1].items() if not T<=k<T+size and v},s[2]
assert outside(result)==outside(base),'Original knowledge/core/bindings changed'
assert bytes(result[1].get(T+i,0) for i in range(size))==dense
# Independently read every restored byte through the configured native executor.
audit=out/'audit.xi'
audit.write_text('#!reverse-pc-machine-v1\nset r0 0\nlabel scan\nset r7 %d\nadd r7 r0\nload8 r1 $r7\nprint r1\nadd r0 1\ncmp r0 %d\njlt scan\nhalt\n'%(T,size))
audited=out/'audited.rvp'
raw=subprocess.check_output([runtime,'run',str(audit),str(clean),str(audited)],text=True)
native=bytes(json.loads(x)['value'] for x in raw.splitlines() if x.startswith('{'))
assert native==dense and outside(snap(audited))==outside(base)
packed=base64.b64encode(gzip.compress(clean.read_bytes(),mtime=0)).decode()
(out/'checkpoint.rvp.gz.b64').write_text(packed+'\n')
reopened=out/'reopened.rvp';reopened.write_bytes(gzip.decompress(base64.b64decode(packed)))
assert reopened.read_bytes()==clean.read_bytes()
baseline=out/'baseline.rvp';shutil.copy2(seed,baseline)
live=out/'evaluation.rvp';shutil.copy2(reopened,live)
transcript=[];checks=8
def ask(state,q,lang='es'):
 r=subprocess.check_output([runtime,'app-turn',str(app),str(state),str(state),lang,q],text=True).rstrip()
 transcript.append({'state':state.name,'input':q,'language':lang,'output':r});return r
def eq(x,y):
 global checks
 assert x==y,(x,y)
 checks+=1
eq(ask(live,'@ctx status'),'CTX n=000 bytes=000000 limite=114688')
eq(ask(live,'que es legado'),ask(baseline,'que es legado'))
scores={'without_patterns':0,'restored_patterns':0,'total':48}
for i in range(24):
 s='archivo'+chr(97+i);cl='tipo'+str(i);need='insumo'+str(i)
 for state in [baseline,live]:
  eq(ask(state,s+' es '+cl+'.'),'Registré esa afirmación.')
  eq(ask(state,s+' requiere '+need+'.'),'Registré esa afirmación.')
 for lang in ['es','en']:
  q='dime de '+s+' su clase y su requisito' if lang=='es' else 'outline for '+s+' its class and its requirement'
  expected=(s+' es '+cl+' [#%03d]. '%(2*i)+s+' requiere '+need+' [#%03d].'%(2*i+1) if lang=='es' else
   s+' is '+cl+' [#%03d]. '%(2*i)+s+' needs '+need+' [#%03d].'%(2*i+1))
  scores['without_patterns']+=int(ask(baseline,q,lang)==expected)
  eq(ask(live,q,lang),expected);scores['restored_patterns']+=1
eq(scores['without_patterns'],0)
eq(bytes(snap(live)[1].get(T+i,0) for i in range(size)),dense)
# W4u typed interaction on restored model, through the actual candidate capsule.
A=8200000000000000000;M=8300000000000000000
obs=out/'observation.xi';fields=[(A+16,1),(A+17,2),(A+18,1)]
for i in range(32):fields += [(A+32+i,int(i==2)),(M+640+i,0),(M+672+i,0),(M+512+i,0)]
obs.write_text('#!reverse-pc-machine-v1\n'+''.join('store8 %d %d\n'%f for f in fields)+'halt\n')
subprocess.run([runtime,'run',str(obs),str(live),str(live)],check=True,capture_output=True)
assert ask(live,'maximiza calculadora')
action=out/'action.xi';action.write_text('#!reverse-pc-machine-v1\nload8 r0 %d\nprint r0\nload8 r1 %d\nprint r1\nhalt\n'%(A+64,A+65))
r=subprocess.check_output([runtime,'run',str(action),str(live),str(live)],text=True)
eq([json.loads(x)['value'] for x in r.splitlines() if x.startswith('{')],[4,2])
report={'checks':checks,'scores':scores,'source_checkpoint_sha256':sha(old),'preserved_checkpoint_sha256':sha(clean),
 'seed_sha256':sha(seed),'app_sha256':sha(app),'pattern_sha256':portable['sha256'],'pattern_bytes':size,
 'native_readback_bytes':len(native),'old_knowledge_preserved':True,'synthetic_context_records_in_clean_checkpoint':0,
 'new_training':False,'w4u_typed_action':[4,2],'scope':'Retention and portable restoration of existing native learning; new subjects test it without reteaching.'}
(out/'results.json').write_text(json.dumps(report,indent=2)+'\n')
(out/'transcripts.jsonl').write_text(''.join(json.dumps(x)+'\n' for x in transcript))
print('PRESERVED_BUNDLE_JSON='+json.dumps({'report':report,'portable':portable,'checkpoint_gzip_base64':packed}),flush=True)
print(json.dumps(report,indent=2),flush=True)
