"""Shared-task byte transport. Inference, state rules and gradients execute in XI."""
from pathlib import Path
import gzip,hashlib,importlib.util,json,struct,sys,tempfile
ROOT=Path(__file__).resolve().parents[2];RT=ROOT/'deps/reverse-pc'
sys.path.insert(0,str(RT/'scripts'))
from xi_session_client import XiSession
def module(name,path):
 s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
QC=module('entity_qchat',ROOT/'integration/qchat100/engine.py')
A=8140000000000000000;Q=8160000000000000000;M=8170000000000000000;E=8184000000000000000
P=json.loads((ROOT/'integration/entity/protocol.json').read_text())
LIB='\n'.join((ROOT/p).read_text() for p in ['ai/xi/quantum3/common.xi','ai/xi/quantum3/benchmarks.xi','ai/xi/balance/qrl3-curriculum.xi','ai/xi/quantum3/step.xi','ai/xi/qchat100/model.xi','ai/xi/qmemory/model.xi','ai/xi/entity/workspace.xi','ai/xi/entity/credit.xi'])
VOCAB=json.loads((ROOT/'integration/balance/release/qchat100/vocabulary.json').read_text())+['mover','izquierda','derecha','objetivo','alcanzado']
TEXT={-1:'necesito más información .',0:'mover a la izquierda .',1:'mover a la derecha .',2:'objetivo alcanzado .'}
TOKENS={k:[VOCAB.index(t) for t in QC.words(v)] for k,v in TEXT.items()}
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def seed(split,i):return int.from_bytes(hashlib.sha256(f'E02:{P["seed"]}:{split}:{i}'.encode()).digest()[:4],'little')&0x7fffffff
def source(body):return '#!reverse-pc-machine-v1\nbudget 100000000\n'+body+'\nhalt\n'+LIB
def run(s,body):return s.execute(source(body))[0]
def metrics(ev):return {e['name']:e['value'] for e in ev if e.get('type')=='metric'}
def emit_int(address,name):return f'load64 r0 {address}\nitof f0 r0\nfemit {name} f0\n'
def workspace(values):
 return ''.join(f'{"fstore" if type(v)is float else "store64"} {E+k} {v}\n' for k,v in values.items())
def material(s,address,size):
 ev=run(s,f'mem_materialize {address} {size}');return bytes.fromhex(next(e['hex'] for e in ev if e['type']=='memory_materialization'))
def boot(folder):
 folder=Path(folder);folder.mkdir(parents=True,exist_ok=True)
 release=ROOT/'integration/balance/release'
 for name,part in [('v3','v3'),('memory','qmemory'),('voice','qchat100')]:
  m=json.loads((release/part/'manifest.json').read_text());(folder/(name+'.rvp')).write_bytes(gzip.decompress((release/part/m['file']).read_bytes()))
 import subprocess
 subprocess.run([str(RT/'build/reverse_pc'),'init',str(folder/'entity.rvp')],capture_output=True,check=True)
 with XiSession(RT/'build/xi_session',folder/'voice.rvp') as s:
  run(s,f'store64 {Q+8} {len(VOCAB)}\nfstore {Q+32} .10');s.save(folder/'voice-initial.rvp')
 (folder/'voice.rvp').unlink();(folder/'voice-initial.rvp').rename(folder/'voice.rvp')

class Entity:
 def __init__(self,folder):
  self.folder=Path(folder);self.sessions={n:XiSession(RT/'build/xi_session',self.folder/(n+'.rvp')) for n in ['v3','memory','voice','entity']}
 def __enter__(self):return self
 def __exit__(self,*args):
  for s in self.sessions.values():s.close()
 def save(self,folder):
  folder=Path(folder);folder.mkdir(parents=True,exist_ok=True)
  for n,s in self.sessions.items():s.save(folder/(n+'.rvp'))
 def identities(self):
  v=self.sessions['v3'];c=self.sessions['voice'];m=self.sessions['memory'];e=self.sessions['entity']
  parts={}
  for name,base,meta in [('vqc',A+100000,A+4000),('qrl',A+200000,A+5000)]:
   data=b''.join(material(v,base+d,8000) for d in [0,10000,20000])+material(v,meta,48);parts[name]=hashlib.sha256(data).hexdigest()
  parts['memory']=hashlib.sha256(material(m,M+64,24)).hexdigest()
  parts['entity']=hashlib.sha256(material(e,E+1000,40)).hexdigest()
  # Full readout and bias coverage, with native materialization bounded per page.
  raw=b''.join(material(c,Q+100000+i,min(60000,888832-i)) for i in range(0,888832,60000))+material(c,Q+990000,1016)
  parts['voice']=hashlib.sha256(raw).hexdigest();return parts
 def voice(self,w,mode=0):
  s=self.sessions['voice'];prefix=[];ids=[];body=workspace(w)
  run(s,body)
  for _ in range(12):
   raw=QC.bits('',prefix)
   ev=run(s,QC.stage(raw)+'call entity_voice_bits\n'+f'store64 {Q+80} {mode}\ncall qchat_encode\ncall qchat_next')
   t=next(e['value'] for e in ev if e.get('type')=='register' and e.get('register')=='r12')
   if t==0:return {'text':QC.detokenize(prefix),'ids':ids,'terminated':True}
   if not 0<=t<len(VOCAB):raise ValueError('Invalid entity voice token')
   ids.append(t);prefix.append(VOCAB[t])
  return {'text':QC.detokenize(prefix),'ids':ids,'terminated':False}
 def episode(self,split,index,train=False,control=None,gate=True):
  v=self.sessions['v3'];m=self.sessions['memory'];c=self.sessions['entity']
  n=seed(split,index);bit=(n>>3)&1;position=index%7
  memory_present=int(index%14!=12);sensor_present=int(index%14!=13)
  base={8:memory_present,16:sensor_present,24:position,176:int(gate)}
  # Native environment creates sensor data and a withheld label. The label is
  # used only by the result verifier and supervised feedback, never inference.
  sample=f'store64 {A+256} {n}\nstore64 {A+280} {int(control=="vqc-ablated")}\nstore64 {A+272} 0\nfstore {A+296} {.6 if index%4==0 else .1}\ncall vqc_sample\n'
  ev=run(v,sample+f'store64 {A} 0\ncall select_agent\ncall forward\nfemit probability f21\nfload f0 {A+128}\nfemit withheld_label f0')
  observed=metrics(ev);teacher=int(observed['withheld_label']);prob=float(observed['probability'])
  # A binary association is written using the learned quantum gate, then read.
  body='qprepare 20000 4\n'+('x 20001\n' if bit else '')+f'set r14 20000\nset r7 20001\nfload f5 {M+64}\ncall qm_exchange\n'
  if control=='memory-erased':body+='qprepare 20000 4\n'
  memory=metrics(run(m,body+'fexpect f0 Z:20000\nfset f1 1\nfsub f1 f0\nfdiv f1 2\nfemit memory_probability f1'))['memory_probability']
  ev=run(c,workspace({**base,40:float(memory),48:prob})+'call entity_infer\n'+''.join(emit_int(E+k,name) for k,name in [(88,'valid'),(72,'goal'),(56,'class'),(64,'rule')]))
  inferred=metrics(ev);goal=int(inferred['goal']);act=-1;right=.5
  if inferred['valid']:
   if control=='qrl-random':
    ev=run(v,f'store64 {A+256} {n+1}\ncall random_uniform\nfemit random f30')
    act=int(metrics(ev)['random']>=.5) if position!=goal else 2
   else:
    ev=run(v,f'store64 {A+344} {position}\nstore64 {A+352} {goal}\nstore64 {A+360} 0\nstore64 {A+312} 12\nstore64 {A+320} 2\ncall qrl_step')
    plan=metrics(ev);act=2 if plan['terminal'] else int(plan['action']);right=float(plan.get('probability_right',.5))
  values={**base,40:float(memory),48:prob,56:int(inferred['class']),64:int(inferred['rule']),72:goal,80:act,88:int(inferred['valid']),160:right}
  ev=run(c,workspace(values)+'call entity_decide\n'+emit_int(E+80,'action')+f'fload f0 {E+112}\nfemit confidence f0')
  decision=metrics(ev);values[80]=int(decision['action'])
  voice=self.voice(values,mode=int(control=='voice-ablated'))
  body=workspace({**values,264:teacher,272:bit,592:len(voice['ids'])})+''.join(f'store8 {E+600+j} {t}\n' for j,t in enumerate(voice['ids']))
  body+='call entity_voice_check\ncall entity_score\n'+emit_int(E+144,'voice_correct')+emit_int(E+288,'gold_action')+f'fload f0 {E+304}\nfemit action_correct f0'
  result=metrics(run(c,body));row={'index':index,'seed':n,'position':position,'memory_present':memory_present,'sensor_present':sensor_present,'memory_probability':memory,'class_probability':prob,'goal':goal,'action':values[80],'voice':voice['text'],'confidence':decision['confidence'],**result}
  if train:
   # Native credit uses verified targets and the proposal actually made.
   run(c,'call entity_learn')
   if memory_present and sensor_present:
    run(v,workspace({**values,264:teacher,272:bit,304:float(result['action_correct'])})+f'store64 {A+344} {position}\nstore64 {A+352} {goal}\nstore64 {A+360} 0\nstore64 {A+312} 12\ncall entity_qrl_feedback')
    run(v,sample+f'store64 {A} 0\nfstore {A+4024} .01\ncall supervised_update')
   if index%42==0:
    run(m,f'store64 {M+16} 0\nstore64 {M+200} {n}\nstore64 {M+208} 2\ncall qm_data\nstore8 {M+10000} {bit}\nstore8 {M+11000} 0\nstore8 {M+50000} {bit}\ncall qm_train')
  return row
 def voice_train(self,epochs):
  s=self.sessions['voice'];examples=[]
  for action in [-1,0,1,2]:
   for bit in [0,1]:
    prefix=[]
    for target in [*TOKENS[action],0]:
     raw=QC.bits('',prefix);w={80:action,64:bit,56:1-bit,24:3}
     examples.append((raw,w,target));prefix.append(VOCAB[target])
  for i,(raw,w,t) in enumerate(examples):
   run(s,workspace(w)+QC.stage(raw)+f'call entity_voice_bits\nstore64 {Q+80} 0\ncall qchat_encode\nstore64 {Q+48} {t}\nstore64 {Q+72} {QC.BANK+i*QC.STRIDE}\ncall qchat_cache')
  body=f'fstore {Q+32} .10\nset r15 0\nlabel e02_epoch\nset r14 0\nlabel e02_case\nmov r0 r14\nmul r0 {QC.STRIDE}\nadd r0 {QC.BANK}\nstore64 {Q+72} r0\nstore64 {E+400} r14\nstore64 {E+408} r15\ncall qchat_load_case\ncall qchat_train\nload64 r14 {E+400}\nload64 r15 {E+408}\nadd r14 1\ncmp r14 {len(examples)}\njlt e02_case\nadd r15 1\ncmp r15 {epochs}\njlt e02_epoch'
  run(s,body);return epochs*len(examples)
def evaluate(folder,split,n,control=None):
 with Entity(folder) as e:
  before=e.identities();rows=[e.episode(split,i,control=control) for i in range(n)];assert e.identities()==before
 k=sum(int(r['joint_success']) for r in rows);v=sum(int(r['voice_correct']) for r in rows);missing=[r for r in rows if not(r['memory_present'] and r['sensor_present'])]
 return {'episodes':n,'joint_correct':k,'joint_accuracy':k/n,'voice_correct':v,'voice_accuracy':v/n,'missing_refusal':sum(r['action']==-1 for r in missing)/len(missing) if missing else 1.,'mean_brier':sum((r['confidence']-r['joint_success'])**2 for r in rows)/n,'cases':rows}
