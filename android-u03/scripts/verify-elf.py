#!/usr/bin/env python3
"""Check every ELF packaged directly or inside Chaquopy ZIP/IMY assets.

This tests real PT_LOAD alignment, not a Gradle version label. It does not
replace on-device ARM64 validation. ZIP compression makes 16KB offsets optional
when native libraries are extracted, but ELF LOAD alignment remains required.
"""
import argparse,hashlib,io,json,struct,zipfile
from pathlib import Path

def scan_elf(raw,name):
 if raw[:4]!=b'\x7fELF':raise ValueError('Not an ELF: '+name)
 endian='<' if raw[5]==1 else '>'
 if raw[4]!=2:raise ValueError('Unexpected 32-bit ELF: '+name)
 phoff=struct.unpack_from(endian+'Q',raw,32)[0]
 size,count=struct.unpack_from(endian+'HH',raw,54)
 aligns=[]
 for i in range(count):
  offset=phoff+i*size
  if struct.unpack_from(endian+'I',raw,offset)[0]==1:
   aligns.append(struct.unpack_from(endian+'Q',raw,offset+48)[0])
 if not aligns or min(aligns)<16384:raise ValueError('Non-16KB LOAD alignment '+name+': '+str(aligns))
 return {'file':name,'load_alignment':aligns,'sha256':hashlib.sha256(raw).hexdigest()}

def inspect_zip(z,prefix='',depth=0):
 rows=[]
 for item in z.infolist():
  if item.filename.endswith('.so'):rows.append(scan_elf(z.read(item),prefix+item.filename))
  elif depth<2 and item.filename.endswith(('.imy','.zip')) and 'chaquopy' in item.filename:
   with zipfile.ZipFile(io.BytesIO(z.read(item))) as nested:rows+=inspect_zip(nested,prefix+item.filename+'!',depth+1)
 return rows

def main():
 p=argparse.ArgumentParser();p.add_argument('apk',type=Path);p.add_argument('--out',type=Path,required=True);a=p.parse_args()
 with zipfile.ZipFile(a.apk) as z:
  assert z.testzip() is None
  rows=inspect_zip(z)
  names={r['file'] for r in rows}
  assert {'lib/arm64-v8a/libreverse_os.so','lib/x86_64/libreverse_os.so'}<=names
 result={'passed':True,'elf_files_verified':len(rows),'all_LOAD_alignment_at_least_16384':True,
  'apk_sha256':hashlib.sha256(a.apk.read_bytes()).hexdigest(),'elf':rows}
 a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:v for k,v in result.items() if k!='elf'}))
if __name__=='__main__':main()
