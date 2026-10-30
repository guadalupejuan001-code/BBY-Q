import fs from 'node:fs';
import crypto from 'node:crypto';
import zlib from 'node:zlib';
export const sha256=b=>crypto.createHash('sha256').update(b).digest('hex');
export function readState(file){let bytes=fs.readFileSync(file);if(file.endsWith('.gz'))bytes=zlib.gunzipSync(bytes);if(bytes.subarray(0,5).toString()!=='RVPC2')throw Error('Expected RVPC2 state');const n=Number(bytes.readBigUInt64LE(5));if(!Number.isSafeInteger(n)||n<0||29+n>bytes.length)throw Error('Invalid RVPC2 memory boundary');const cells=new Map();for(const line of bytes.subarray(29+n).toString().split('\n')){const[t,a,v]=line.split(' ');if(t==='O'&&Number(v))cells.set(BigInt(a),Number(v));}return{bytes,cells,sha256:sha256(bytes)};}
export const byte=(s,a)=>s.cells.get(a)||0;
export const readBytes=(s,a,n)=>Buffer.from(Array.from({length:n},(_,i)=>byte(s,a+BigInt(i))));
