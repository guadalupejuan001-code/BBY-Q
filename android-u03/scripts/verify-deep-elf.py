#!/usr/bin/env python3
"""Audit PT_LOAD alignment of actual APK and nested Chaquopy extension ELFs."""
from pathlib import Path
from hashlib import sha256
import io,json,struct,sys,zipfile

def elf(raw,name):
    if raw[:4]!=b'\x7fELF' or raw[4]!=2:raise ValueError('Unsupported native ELF: '+name)
    endian='<' if raw[5]==1 else '>'
    phoff=struct.unpack_from(endian+'Q',raw,32)[0]
    size,count=struct.unpack_from(endian+'HH',raw,54)
    loads=[]
    for i in range(count):
        offset=phoff+i*size
        if struct.unpack_from(endian+'I',raw,offset)[0]==1:loads.append(struct.unpack_from(endian+'Q',raw,offset+48)[0])
    if not loads or min(loads)<16384:raise ValueError('ELF not compatible with 16KB LOAD alignment: '+name+' '+str(loads))
    return {'file':name,'load_alignment':loads,'sha256':sha256(raw).hexdigest()}

def walk(archive,prefix='',depth=0):
    results=[]
    for name in archive.namelist():
        if name.endswith('.so'):results.append(elf(archive.read(name),prefix+name))
        elif depth<2 and 'chaquopy' in name and name.endswith(('.imy','.zip')):
            with zipfile.ZipFile(io.BytesIO(archive.read(name))) as nested:results.extend(walk(nested,prefix+name+'!',depth+1))
    return results

if __name__=='__main__':
    apk=Path(sys.argv[1]);output=Path(sys.argv[2])
    with zipfile.ZipFile(apk) as archive:
        assert archive.testzip() is None
        rows=walk(archive)
    assert len(rows)>=20
    names={r['file'] for r in rows}
    assert {'lib/arm64-v8a/libreverse_os.so','lib/x86_64/libreverse_os.so'}<=names
    report={'all_load_segments_16kb':True,'verified_elf_count':len(rows),'apk_sha256':sha256(apk.read_bytes()).hexdigest(),'files':rows,'physical_device_not_tested':True}
    output.write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({k:v for k,v in report.items() if k!='files'}))
