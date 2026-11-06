"""XI grammar compiler and typed calls to the existing native Zero tools."""
import json,re,struct,subprocess
from decimal import Decimal
from pathlib import Path
from schema import ROOT,C,S
import engine as E
from grammar import RULES,SLOTS,lexical_words

K=8040000000000000000
A={'K':K,'PT':K+10000,'PN':K+13000,'PI':K+16000,
   'START':K+20000,'LENGTH':K+22000,'CAP':K+24000,'PAT':K+40000,
   'FACTS':K+100000,'RULES':K+200000,'ARG':K+3000}
Z=9185000000000000000

def expand(source):
    addresses={**S,**A,'Z':Z}
    return re.sub(r'@([A-Z]+)(?:\+(\d+))?',lambda m:str(addresses[m[1]]+int(m[2] or 0)),source)

def source(vocabulary):
    ids={w:i for i,w in enumerate(vocabulary)}
    output=[]
    # Punctuation removal happens natively, leaving arithmetic operators and
    # original-index mappings intact for exact captured UTF-8 spans.
    ignored=[ids[w] for w in ['.',',',':',';','?','!','¿','¡'] if w in ids]
    output+=['label c2_parse','store64 @K+64 0','store64 @K+72 0',
             'store64 @K+80 0','set r8 0','set r9 0','label c2_clean',
             'load64 r0 @C+8','cmp r8 r0','jge c2_clean_done',
             'mov r0 r8','mul r0 8','add r0 @T','load64 r1 $r0']
    for value in ignored:output += [f'cmp r1 {value}','je c2_clean_next']
    output+=['mov r0 r9','mul r0 8','add r0 @PT','store64 $r0 r1',
             'mov r0 r8','add r0 @NF','load8 r1 $r0','mov r0 r9','mul r0 8',
             'add r0 @PN','store64 $r0 r1','mov r0 r9','mul r0 8','add r0 @PI',
             'store64 $r0 r8','add r9 1','label c2_clean_next','add r8 1',
             'jmp c2_clean','label c2_clean_done','store64 @K+80 r9']
    for index,rule in enumerate(RULES):
        pattern=[];seen=set()
        for token in rule.pattern.split():
            if token.startswith('{'):
                name=token[1:-1];slot=SLOTS.index(name)
                code=-(201+slot) if name in seen else -(1+slot) if name in ['a','b'] else -(101+slot)
                seen.add(name);pattern.append(code)
            else:pattern.append(ids[token])
        output += [E.stage64(A['PAT'],pattern).strip(),f'store64 @K+88 {len(pattern)}','call c2_match',
                   'cmp r0 1',f'jne c2_rule_{index}_next',f'store64 @K+64 {index+1}',
                   f'store64 @K+72 {rule.intent}','ret',f'label c2_rule_{index}_next']
    output += ['ret']
    native=(ROOT/'ai/xi/sequence2/tools.xi.in').read_text()
    return expand('\n'.join(output)+'\n'+native)

def build_zero():
    import fcntl
    directory=ROOT/'build/zero';directory.mkdir(parents=True,exist_ok=True)
    paths=[ROOT/'integration/zero/build.mjs',ROOT/'ai/personal/zero/model.mjs',
           ROOT/'ai/personal/zero/schema.mjs',ROOT/'ai/personal/zero/core.xi.in']
    identity={str(p):E.sha(p) for p in paths};marker=directory/'.source-identity.json'
    with (directory/'.build.lock').open('w') as lock:
        fcntl.flock(lock,fcntl.LOCK_EX)
        if marker.exists() and json.loads(marker.read_text())==identity and all((directory/name).exists() for name in ['zero.xi','schema.json']):return
        subprocess.run(['node',str(ROOT/'integration/zero/build.mjs')],check=True,capture_output=True)
        marker.write_text(json.dumps(identity)+'\n')

class Tools:
    """A transport adapter: native XI selects rules, mutates facts and solves.

    Captured strings become exact dictionary symbols; the host only formats
    commands, stages typed fields and renders the native result.
    """
    def __init__(self,model,metadata):
        self.model=model;self.meta=metadata;self.zero_schema=json.loads((ROOT/'build/zero/schema.json').read_text())
        self.zero_source=(ROOT/'build/zero/zero.xi').read_text()
        # Keep the established binary64 calculator, with a narrower explicit
        # range so rounded large-integer intermediates cannot masquerade as
        # exact small results after a later subtraction.
        if self.zero_source.count('label zero_math_apply_store\n')!=1:raise ValueError('Calculator source contract changed')
        self.zero_source=self.zero_source.replace('label zero_math_apply_store\n',
            'label zero_math_apply_store\nfcmp f0 -9007199254740991\njlt zero_math_apply_bad\nfcmp f0 9007199254740991\njgt zero_math_apply_bad\n')
        for word in sorted(lexical_words()|set('.,:;?!¿¡')):model.codec.id(word)
        self.model.library+='\n'+source(model.codec.words)

    def entity(self,value):
        canonical=' '.join(E.words(value))
        records=self.meta.setdefault('entities',{})
        if canonical not in records:records[canonical]={'id':2000000+len(records),'display':value}
        return records[canonical]['id']

    def display(self,identifier):
        return next((r['display'] for r in self.meta.get('entities',{}).values() if r['id']==identifier),str(identifier))

    def integer(self,offset):return struct.unpack('<q',self.model.memory(K+offset,8))[0]
    def numbers(self,address,count):return list(struct.unpack('<'+'q'*count,self.model.memory(address,count*8)))

    def parse(self,prompt):
        encoded=self.model.prepare(prompt);self.model.run('call c2_parse')
        code=self.integer(64)
        if not code:return None
        n=self.integer(80);original=self.numbers(A['PI'],n);captures={}
        for index,name in enumerate(SLOTS):
            start,length=self.numbers(A['CAP']+16*index,2)
            if length and start+length<=n:
                first=encoded['tokens'][original[start]];last=encoded['tokens'][original[start+length-1]]
                captures[name]=encoded['raw'][first['start']:last['start']+last['length']].decode('utf-8')
        return {'rule':code,'intent':self.integer(72),'captures':captures}

    def raw_zero(self,command):
        self.model.run(f'store64 {Z+24} {command}')
        return self.model.s.execute(self.zero_source)[0]

    def grounded(self):
        self.model.run('call c2_knowledge')

    def execute(self,parsed,fail_after=None):
        captures=parsed['captures'];results=[];proof=[]
        def value(text):return captures[text[1:]] if text.startswith('$') else text
        for index,action in enumerate(RULES[parsed['rule']-1].actions):
            op=action[0]
            if op in ['cancel','greet']:
                result={'kind':op,'status':1,'text':'De acuerdo; no ejecutaré esa petición.' if op=='cancel' else 'Hola, X.'}
            elif op=='put':
                _,subject,relation,obj,polarity,mode=action
                rel=self.zero_schema['words'].get(relation) or self.entity(relation)
                args=[self.entity(value(subject)),rel,self.entity(value(obj)),polarity,
                      {'exact':0,'relation':1,'polarity':2}[mode]]
                self.model.run(E.stage64(A['ARG'],args)+'call c2_put')
                result={'kind':op,'status':self.integer(56),'subject':value(subject),'value':value(obj),'polarity':polarity}
            elif op=='rule':
                _,kind,goal=action;es=self.zero_schema['words']['es']
                row=[-1,es,self.entity(value(kind)),1,0,0,0,0,-1,es,self.entity(value(goal)),1,1,0,1,0]
                self.model.run(E.stage64(A['ARG'],row)+'call c2_rule_put')
                result={'kind':op,'status':self.integer(56)}
            elif op=='lookup':
                _,subject,relation=action
                self.model.run(E.stage64(A['ARG'],[self.entity(value(subject)),self.entity(relation)])+'call c2_lookup')
                result={'kind':op,'status':self.integer(56)}
                if result['status']==1:result['value']=self.display(self.integer(104))
            elif op in ['query','route']:
                self.grounded()
                if op=='query':
                    _,subject,relation,obj,polarity=action
                    atom=[self.entity(value(subject)),self.zero_schema['words'][relation],self.entity(value(obj)),polarity]
                else:
                    _,subject,goal=action;atom=[self.entity(value(subject)),self.zero_schema['words']['conecta'],self.entity(value(goal)),1]
                self.model.run(E.stage64(Z+16384,atom))
                self.raw_zero(1 if op=='query' else 2);status=struct.unpack('<q',self.model.memory(Z+16,8))[0]
                result={'kind':op,'status':status}
                if op=='route' and status==1:
                    count=struct.unpack('<q',self.model.memory(Z+112,8))[0]
                    result['path']=[self.display(v) for v in reversed(self.numbers(Z+300000,count))]
                if op=='query' and status in [1,-1]:
                    count=struct.unpack('<q',self.model.memory(Z+176,8))[0]
                    result['proof']=self.numbers(Z+304096,count)
            else:
                if op=='math':expression=captures[action[1]]
                elif op=='binary':expression=f'{captures[action[1]]} {action[2]} {captures[action[3]]}'
                else:raise ValueError('Undeclared tool action')
                tokens=E.words(expression);body=E.stage64(Z+48,[len(tokens)+1])
                valid=True
                for i,token in enumerate(tokens,1):
                    number=bool(E.NUMBER.fullmatch(token));literal=self.zero_schema['words'].get(token)
                    if not number and token not in ['(',')','+','-','*','/','por','entre']:
                        valid=False;break
                    literal=self.zero_schema['words'].get({'por':'*','entre':'/'}.get(token,token),literal or 4)
                    body+=E.stage64(Z+4096+8*i,[literal])+E.stage64(Z+8192+8*i,[int(number)])
                    if number:
                        numeric=float(token.replace(',','.'))
                        if not __import__('math').isfinite(numeric) or abs(Decimal(token.replace(',','.')))>2**53-1:valid=False;break
                        body+=f'fstore {Z+12288+8*i} {numeric}\n'
                if not valid:result={'kind':'math','status':4,'reason':'Unsupported or inexact numeric expression'}
                else:
                    self.model.run(body);self.raw_zero(3)
                    status=struct.unpack('<q',self.model.memory(Z+16,8))[0];result={'kind':'math','status':status}
                    if status==1:
                        number=struct.unpack('<d',self.model.memory(Z+96,8))[0]
                        if not __import__('math').isfinite(number):result={'kind':'math','status':4,'reason':'Nonfinite result'}
                        else:result['value']=number
            results.append(result);proof.append({'native_rule':parsed['rule'],'action':index,'operation':op,'status':result['status']})
            if result['status'] not in [1,-1]:return {'ok':False,'results':results,'trace':proof,'status':result['status']}
            if fail_after==index+1:raise RuntimeError('Injected failure after native operation')
        return {'ok':True,'status':1,'results':results,'trace':proof}
