"""Byte transport for a learned XI readout of VQC's quantum measurements."""
import math,random,re,struct
from .common import ROOT,C1,A,QUANTUM_LIBRARY,encoded,digest,material

B=8186000000000000000
MAGIC=240605;NR=16;HASHNR=8;NF=NR+1;NH=0;W1=NF;W2=NF+1;NP=NF+2
STRIDE=256
ADDR={'B':B,'NR':NR,'NF':NF,'NH':NH,'NP':NP,'W1':W1,'W2':W2,
      'MAGIC':MAGIC,'HASHNR':HASHNR,'GAIN':math.sqrt(HASHNR/1000),'ALIGNGAIN':1/math.sqrt(250),
      'IN':B+128,'MEAN':B+512,'SCALE':B+768,'HID':B+1024,'DH':B+1280,
      'P':B+2048,'G':B+8192,'MOM':B+12288,'VAR':B+16384,
      'NORMAL':B+40960,'PROJ':B+100000,'CACHE':B+1000000,
      'PHASE':B+500000,'OUTBIAS':B+2048+8*NF,'GOUTBIAS':B+8192+8*NF,
      'SKIP':B+2048+8*(NF+1),'GSKIP':B+8192+8*(NF+1)}
TEMPLATE=ROOT/'ai/xi/unified/perception-decoder.xi.in'
HEAD_LIBRARY=re.sub(r'@([A-Z0-9]+)(?:\+(\d+))?',lambda m:str(ADDR[m[1]]+int(m[2] or 0)),TEMPLATE.read_text())
LIBRARY=QUANTUM_LIBRARY+'\n'+HEAD_LIBRARY

def x_ablated_library():
    lines=HEAD_LIBRARY.splitlines()
    lines=['fset f0 0' if line.startswith('fexpect f0 ') and 'X:' in line else line for line in lines]
    return QUANTUM_LIBRARY+'\n'+'\n'.join(lines)

def run(native,body):
    return native.execute('#!reverse-pc-machine-v1\nbudget 100000000\n'+body+'\nhalt\n'+LIBRARY)[0]

def floats(native,address,count):return list(struct.unpack('<'+'d'*count,material(native,address,8*count)))
def stage(address,values):return ''.join(f'fstore {address+8*i} {float(value)!r}\n' for i,value in enumerate(values))

def initialize(native,seed=2026110601):
    parameters=[0.]*NP;parameters[-1]=1.
    run(native,f'store64 {B} {MAGIC}\nstore64 {B+8} {NF}\nstore64 {B+16} {NH}\nstore64 {B+24} 0\nstore64 {B+32} 0\nfstore {B+40} .03\nfstore {B+48} 1\nfstore {B+56} 1\n'+stage(ADDR['P'],parameters)+stage(ADDR['SCALE'],[1.]*NF))
    return {'projection':'exact Pauli conjugation of the existing encoder, angle round-trip and per-channel midrange, residual mean, standard deviation and half-range; no raw sensor, label or generator seed is read','observables':11500,'projection_sha256':digest(HEAD_LIBRARY.encode()),
            'features':NF,'hidden':NH,'trainable_parameters':NP,'input':'actual native Pauli expectations and original logit','optimizer':'native XI mini-batch Adam','native_source_sha256':C1.sha(TEMPLATE)}

def cache_body(index):
    address=ADDR['CACHE']+STRIDE*index
    # The cache carries a separate teacher view. Inference only loads the
    # first NF floats and original logit at +192; it never loads +200.
    body='call u2_project\n'
    for i in range(NF):body+=f'fload f0 {ADDR["IN"]+8*i}\nfstore {address+8*i} f0\n'
    body+=f'fload f0 {B+64}\nfstore {address+192} f0\nfload f0 {A+128}\nfstore {address+200} f0'
    return body+'\n'

def cache(native,index):
    # Separate EXEC packets reset registers; the last native forward logit
    # lives in memory and must be restored before projecting a cached case.
    run(native,f'fload f20 {A+112}\n'+cache_body(index));return ADDR['CACHE']+STRIDE*index

def parameter_identity(native):
    # Include inference parameters and normalization; optimizer counters are
    # intentionally excluded from this parameter identity.
    data=material(native,ADDR['P'],NP*8)+material(native,ADDR['MEAN'],NF*8)+material(native,ADDR['SCALE'],NF*8)
    return digest(data)

def publish_region(native):
    """Only the new bank region, for preservation of existing personal banks."""
    ranges=[(B,128),(ADDR['MEAN'],NF*8),(ADDR['SCALE'],NF*8),(ADDR['P'],NP*8),
            (ADDR['MOM'],NP*8),(ADDR['VAR'],NP*8)]
    result=[]
    for address,size in ranges:
        for start in range(0,size,60000):result.append((address+start,material(native,address+start,min(60000,size-start))))
    return result
