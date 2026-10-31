// P03 native XI reasoning program. Its immutable human-readable XI source is
// stored compressed to keep the repository compact; no model weights or eval.
import fs from 'node:fs';
import zlib from 'node:zlib';
import crypto from 'node:crypto';

export const REASON_BASE=9190000000000000000n+65536n;
export const REASON_MAX_BYTES=640;
export const REASON_SHA256='90e377f00e0be1a1c2b8fb3ed0800af2b0fdfd261c94bd66c4f2519db0ae5317';
export const REASON_MODE=Object.freeze({
 unsupported:0,proved:1,unknown:2,conflict:3,disproved:4,partial:5
});
export function reasonSource(){
 const source=fs.readFileSync(new URL('./reason.xi.gz.b64',import.meta.url),'utf8').trim();
 const packed=Buffer.from(source,'base64');
 if(packed.toString('base64')!==source)throw Error('P03 source encoding mismatch.');
 const uncompressed=zlib.gunzipSync(packed,{maxOutputLength:64000});
 const digest=crypto.createHash('sha256').update(uncompressed).digest('hex');
 if(digest!==REASON_SHA256)throw Error('P03 native XI source digest mismatch.');
 const text=new TextDecoder('utf-8',{fatal:true}).decode(uncompressed);
 if(!text.startsWith('#!reverse-pc-machine-v1\n')||!text.includes('label p03_eq\n')||!text.includes('label p03_sentence_loop\n'))
  throw Error('P03 XI source contains an incompatible entry point.');
 return text;
}
