"""Exact text/token transport for native C1 inference and learning."""
import gzip,hashlib,json,math,re,struct,subprocess,sys,tempfile,unicodedata
from pathlib import Path
from schema import ROOT,C,S,FIELD_WIDTHS,LIMITS
sys.path.insert(0,str(ROOT/'deps/reverse-pc/scripts'))
from xi_session_client import XiSession
RT=ROOT/'deps/reverse-pc'
TOKEN=re.compile(r'\d+(?:[.,]\d+)?|[^\W\d_][\w\u0300-\u036f]*|_\w*|[^\s]',re.UNICODE)
NUMBER=re.compile(r'[0-9]+(?:[.,][0-9]+)?')
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def words(text):return [unicodedata.normalize('NFC',m.group()).lower() for m in TOKEN.finditer(text)]
def output_words(text):return re.findall(r'\w+|[.!?,]',text.lower(),re.UNICODE)
def detokenize(tokens):
 proper={'x':'X','bby':'BBY','q':'Q','xi':'XI','ether':'Ether'};value=' '.join(proper.get(t,t) for t in tokens);value=re.sub(r'\s+([.!?,])',r'\1',value);return value[:1].upper()+value[1:]
class Codec:
 def __init__(self,vocabulary):
  assert vocabulary[0]=='<pad>' and len(vocabulary)<LIMITS['word_id'];self.words=list(vocabulary);self.ids={w:i for i,w in enumerate(vocabulary)}
 def id(self,word):
  if word not in self.ids:
   if len(self.words)>=LIMITS['word_id']:raise ValueError('Word dictionary capacity reached')
   self.ids[word]=len(self.words);self.words.append(word)
  return self.ids[word]
 def text(self,text):
  raw=text.encode('utf-8')
  if len(raw)>LIMITS['raw_bytes']:raise ValueError('Input byte capacity exceeded')
  rows=[]
  for m in TOKEN.finditer(text):
   token=m.group();key=unicodedata.normalize('NFC',token).lower();start=len(text[:m.start()].encode('utf-8'));size=len(token.encode('utf-8'));value=float(key.replace(',','.')) if NUMBER.fullmatch(key) else None
   if value is not None and not math.isfinite(value):raise ValueError('Numeric value outside finite range')
   rows.append({'id':self.id(key),'key':key,'start':start,'length':size,'numeric':value})
  return {'raw':raw,'tokens':rows}
def source(body):return '#!reverse-pc-machine-v1\nbudget 100000000\n'+body+'\nhalt\n'+(ROOT/'build/sequence1/model.xi').read_text()
def stage64(address,values):return ''.join(f'store64 {address+8*i} {int(v)}\n' for i,v in enumerate(values))
def stage_bytes(address,data):return ''.join(f'store8 {address+i} {v}\n' for i,v in enumerate(data))
def frame_bits(fields):
 assert len(fields)==len(FIELD_WIDTHS);out=[]
 for value,width in zip(fields,FIELD_WIDTHS):
  assert 0<=value<1<<width;out.extend((value>>i)&1 for i in range(width))
 assert len(out)==100;return out
def decode_bits(raw):
 assert len(raw)==100;out=[];offset=0
 for width in FIELD_WIDTHS:out.append(sum(raw[offset+i]<<i for i in range(width)));offset+=width
 return out
def birth(path,text_vocabulary,intent_classes=11):
 subprocess.run([str(RT/'build/reverse_pc'),'init',str(path)],capture_output=True,check=True)
 pending=Path(path).with_suffix('.initialized.rvp')
 with XiSession(RT/'build/xi_session',path) as s:
  s.execute(source(stage64(C+208,[text_vocabulary,intent_classes])+f'fstore {C+112} .05\nstore64 {C+1000} 1001'));s.save(pending)
 pending.replace(path)
class Model:
 def __init__(self,path,vocabulary,output):
  self.s=XiSession(RT/'build/xi_session',path);self.codec=Codec(vocabulary);self.output=output;self.output_ids={w:i for i,w in enumerate(output)};self.library=(ROOT/'build/sequence1/model.xi').read_text();self.prompt_count=0
 def __enter__(self):return self
 def __exit__(self,*args):self.s.close()
 def run(self,body):return self.s.execute('#!reverse-pc-machine-v1\nbudget 100000000\n'+body+'\nhalt\n'+self.library)[0]
 def memory(self,address,size):return bytes.fromhex(next(e['hex'] for e in self.run(f'mem_materialize {address} {size}') if e['type']=='memory_materialization'))
 def number(self,offset):return struct.unpack('<q',self.memory(C+offset,8))[0]
 def prepare(self,prompt,previous='',cache=None,retain_bytes=True):
  if len(list(TOKEN.finditer(prompt)))>LIMITS['tokens']:raise ValueError('Input token capacity exceeded')
  if len(list(TOKEN.finditer(previous)))>LIMITS['history_tokens']:raise ValueError('History token capacity exceeded')
  p=self.codec.text(prompt);h=self.codec.text(previous);self.prompt_count=len(p['tokens'])
  body=stage64(C+8,[len(p['tokens']),len(h['tokens'])])+stage64(S['T'],[r['id'] for r in p['tokens']])+stage64(S['TL'],[r['length'] for r in p['tokens']])+stage64(S['H'],[r['id'] for r in h['tokens']])+stage64(S['HL'],[r['length'] for r in h['tokens']])
  body+=stage_bytes(S['NF'],[int(r['numeric'] is not None) for r in p['tokens']])+''.join(f'fstore {S["NV"]+i*8} {r["numeric"]}\n' for i,r in enumerate(p['tokens']) if r['numeric'] is not None)
  if retain_bytes:body+=stage_bytes(S['RAW'],p['raw'])+stage_bytes(S['HRAW'],h['raw'])+stage64(C+304,[len(p['raw']),len(h['raw'])])
  self.run(body+'call c1_encode_input');assert self.number(184)==1,'Native frame rejected'
  if cache is not None:self.run(f'store64 {C+128} {cache}\ncall c1_cache_input')
  return p
 def active(self,prefix,head=0,cache=None,ablate=False):
  last=self.output_ids[prefix[-1]] if prefix else 0;before=self.output_ids[prefix[-2]] if len(prefix)>1 else 0
  body=(f'store64 {C+128} {cache}\ncall c1_load_input\n' if cache is not None else '')+stage64(C+56,[head])+stage64(C+88,[last,before,len(prefix)])+f'store64 {C+192} {2 if ablate else 0}\ncall c1_prefix\n'
  return body
 def generate(self,prompt,previous='',ablate=False):
  p=self.prepare(prompt,previous);prefix=[];logp=0.;started=__import__('time').perf_counter()
  for _ in range(64):
   events=self.run(self.active(prefix,ablate=ablate)+'call c1_next');token=next(e['value'] for e in events if e['type']=='register' and e.get('register')=='r12');logp+=next(e['value'] for e in events if e.get('name')=='log_probability')
   if token==0:return {'text':detokenize(prefix),'tokens':prefix,'terminated':True,'log_probability':logp,'elapsed_ms':(__import__('time').perf_counter()-started)*1000}
   assert 0<token<len(self.output);prefix.append(self.output[token])
  return {'text':detokenize(prefix),'tokens':prefix,'terminated':False,'log_probability':logp}
 def intent(self,prompt,previous='',ablate=False):
  self.prepare(prompt,previous);events=self.run(self.active([],head=1,ablate=ablate)+'call c1_next');return {'intent':next(e['value'] for e in events if e['type']=='register' and e.get('register')=='r12'),'log_probability':next(e['value'] for e in events if e.get('name')=='log_probability')}
