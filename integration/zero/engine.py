"""Byte codec and opaque storage for the native XI general workspace."""
import hashlib,json,re,struct,subprocess,sys,tempfile,unicodedata
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];RT=ROOT/'deps/reverse-pc';BUILD=ROOT/'build/zero'
sys.path.insert(0,str(RT/'scripts'))
from xi_session_client import XiSession
Z=9185000000000000000
OFF={'T':4096,'NF':8192,'NV':12288,'ARG':16384,'RT':16448,'F':100000,'R':200000,'OUT':300000,'PROOF':304096}
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def build():subprocess.run(['node',str(ROOT/'integration/zero/build.mjs')],check=True,capture_output=True)
def tokenize(s):
 s=''.join(c for c in unicodedata.normalize('NFD',s.lower()) if unicodedata.category(c)!='Mn')
 return re.findall(r'\$[a-z]+|\d+(?:\.\d+)?|[\w]+|[.!?;,:()+*/-]',s,re.UNICODE)
class Engine:
 def __init__(self,folder=None):
  self.temp=tempfile.TemporaryDirectory(prefix='bbyq-zero-') if folder is None else None;self.folder=Path(folder or self.temp.name);self.folder.mkdir(parents=True,exist_ok=True)
  self.schema=json.loads((BUILD/'schema.json').read_text());self.vocab=dict(self.schema['words']);self.next_id=1024
  self.facts=[];self.rules=[];self.turns=[]
  saved=self.folder/'knowledge.json'
  if saved.exists():
   saved=json.loads(saved.read_text());self.vocab=saved['vocab'];self.next_id=saved['next'];self.facts=saved['facts'];self.rules=saved['rules']
  state=self.folder/'zero.rvp'
  if not state.exists():subprocess.run([str(RT/'build/reverse_pc'),'init',str(state)],check=True,capture_output=True)
  self.s=XiSession(RT/'build/xi_session',state);self.source=(BUILD/'zero.xi').read_text()
 def __enter__(self):return self
 def __exit__(self,*args):self.close()
 def close(self):
  self.s.close()
  if self.temp:self.temp.cleanup()
 def raw(self,body):return self.s.execute('#!reverse-pc-machine-v1\nbudget 100000000\n'+body+'\nhalt\n')[0]
 def call(self,command):self.raw(f'store64 {Z+24} {command}');return self.s.execute(self.source)[0]
 def integer(self,offset):return struct.unpack('<q',self.bytes(offset,8))[0]
 def bytes(self,offset,size):
  ev=self.raw(f'mem_materialize {Z+offset} {size}');return bytes.fromhex(next(e['hex'] for e in ev if e['type']=='memory_materialization'))
 def numbers(self,offset,size):return list(struct.unpack('<'+'q'*size,self.bytes(offset,size*8)))
 def stage(self,offset,data):self.raw(''.join(f'store64 {Z+offset+8*i} {int(v)}\n' for i,v in enumerate(data)))
 def word(self,w):
  if w not in self.vocab:self.vocab[w]=self.next_id;self.next_id+=1
  return self.vocab[w]
 def parse(self,text,batch=False):
  words=tokenize(text)
  ids=[self.word(w) for w in words[:128]];self.stage(4096,ids);self.stage(32,[len(words)]);self.stage(136,[int(batch)])
  self.raw(''.join(f'store64 {Z+8192+8*i} {int(bool(re.fullmatch(r"[0-9]+(?:\.[0-9]+)?",w)))}\n'+(f'fstore {Z+12288+8*i} {float(w)}\n' if re.fullmatch(r'[0-9]+(?:\.[0-9]+)?',w) else '') for i,w in enumerate(words[:128])))
  self.call(0);op=self.integer(0);result={'op':op,'status':self.integer(16),'words':words}
  if op in [1,3,4,8,9,10,14,15]:result['atom']=self.numbers(16384,4)
  if op in [2,7,12]:result['rule']=self.numbers(16448,16)
  return result
 def knowledge(self,extra_facts=(),extra_rules=(),budget=30000):
  facts=[*self.facts,*extra_facts];rules=[*self.rules,*extra_rules]
  if len(facts)>1024 or len(rules)>256:raise ValueError('Native workspace capacity exceeded')
  data=[]
  for i,fact in enumerate(facts):data.extend([*fact[:4],i+1,0,0,0])
  self.stage(100000,data)
  data=[]
  for i,rule in enumerate(rules):
   row=list(rule);row[13]=i+1;row[14]=1;data.extend(row)
  self.stage(200000,data);self.stage(64,[len(facts),len(rules)]);self.stage(104,[budget])
 def run(self,text,budget=30000):
  lines=[v.strip() for v in re.split(r'[;\n]+',text) if v.strip()];parsed=[];batch=False
  for line in lines:
   p=self.parse(line,batch);parsed.append((line,p));batch|=p['op']==11
  if any(p['op']==0 for _,p in parsed):return {'op':0,'status':0,'unsupported':True}
  if any(p['status']==4 for _,p in parsed):return {'op':-1,'status':4,'invalid':True}
  extras=[];rules=[];results=[];self.stage(224,[1])
  for line,p in parsed:
   op=p['op'];self.parse(line,batch)
   if op in [1,8,9]:
    atom=p['atom']
    if op==8:self.facts=[f for f in self.facts if f[:3]!=atom[:3]]
    if op==9:self.facts=[f for f in self.facts if f!=atom]
    elif atom not in self.facts:self.facts.append(atom)
    results.append({'op':op,'status':1,'atom':atom});self.stage(920,[atom[0],0]);continue
   if op==12:
    self.rules=[r for r in self.rules if r[:13]!=p['rule'][:13]];results.append({'op':op,'status':1});continue
   if op==2:
    rule=p['rule']
    if rule not in self.rules:self.rules.append(rule)
    results.append({'op':op,'status':1});continue
   if op==10:extras.append(p['atom']);continue
   if op==7:rules.append(p['rule']);continue
   if op==11:continue
   if op==6:
    kind=next((r['op'] for r in reversed(self.turns) if r['op'] in [1,2,3,4,5]),3);self.stage(192,[kind]);self.call(4);results.append({'op':6,'status':self.integer(16),'updates':self.integer(944)});continue
   if op in [3,4]:
    if p['status']==5:results.append({'op':op,'status':5});continue
    self.knowledge(extras,rules,budget);self.call(1 if op==3 else 2);status=self.integer(16);count=self.integer(112)
    result={'op':op,'status':status,'count':count,'steps':self.integer(152)}
    if status in [1,2,-1]:
     result['ids']=self.numbers(300000,count)
     if op==3:
      n=self.integer(80);result['facts']=[self.numbers(100000+64*i,8) for i in range(n)];pn=self.integer(176);result['proof']=self.numbers(304096,pn)
     elif count:result['path']=list(reversed(result['ids']))
    results.append(result);continue
   if op==5:
    events=self.call(3);result={'op':op,'status':self.integer(16)}
    if result['status']==1:result['result']=next(e['value'] for e in events if e.get('name')=='result')
    results.append(result)
  for row in results:self.stage(232,[row['status']]);self.call(6)
  self.turns.extend(results);return {'op':parsed[-1][1]['op'],'status':self.integer(224),'results':results}
 def save(self):
  path=self.folder/'knowledge.json';path.write_text(json.dumps({'vocab':self.vocab,'next':self.next_id,'facts':self.facts,'rules':self.rules}))
  next_state=self.folder/'next.rvp';self.s.save(next_state);next_state.replace(self.folder/'zero.rvp')
