"""Versioned data layout; the running algorithms are native XI programs."""
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
C=8150000000000000000
OLD_Q=8160000000000000000
S={'C':C,'T':C+10000,'TL':C+15000,'H':C+20000,'HL':C+21000,'NF':C+25000,'NV':C+26000,'FRAME':C+2000,'MEASURED':C+2200,'F':C+100000,'G':C+110000,'BIAS':C+5000000,'CACHE':C+100000000,'SM':C+500000000,'W':C+1000000000000,'RAW':C+60000,'HRAW':C+80000,'OBS':OLD_Q+2000,'BITS':OLD_Q+1000,'QM':OLD_Q}
FIELD_WIDTHS=[20,20,16,2,7,7,6,16,6]
FEATURE_STRIDE=1<<40
NODE_STRIDE=1<<47
HEAD_STRIDE=1<<55
MAX_FEATURES=1024
LIMITS={'tokens':256,'history_tokens':64,'output_tokens':64,'word_id':1<<20,'raw_bytes':16384}
S['SK']=C+502000000

def expand(text):
 import re
 return re.sub(r'@([A-Z]+)(?:\+(\d+))?',lambda m:str(S[m[1]]+int(m[2] or 0)),text)
