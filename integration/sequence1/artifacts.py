"""Checksum-verified transport of compressed native checkpoint parts."""
import hashlib
from pathlib import Path

def model_bytes(folder,entry):
 folder=Path(folder)
 if entry.get('parts'):
  chunks=[]
  for part in entry['parts']:
   data=(folder/part['file']).read_bytes()
   if len(data)!=part['bytes'] or hashlib.sha256(data).hexdigest()!=part['sha256']:raise RuntimeError('Checkpoint part identity mismatch')
   chunks.append(data)
  data=b''.join(chunks)
 else:data=(folder/entry['file']).read_bytes()
 if len(data)!=entry['gzip_bytes'] or hashlib.sha256(data).hexdigest()!=entry['gzip_sha256']:raise RuntimeError('Compressed checkpoint identity mismatch')
 return data
