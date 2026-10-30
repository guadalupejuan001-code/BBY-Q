// Byte framing and native page I/O only. No text interpretation or ranking.
import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import {spawnSync} from 'node:child_process';
import {B,INPUT,LENGTH,TOTAL,OFFSET,STATUS,KEY,KEY_LENGTH,RECORD,ROW_BYTES,COUNT,REVISION,EXISTS,CAPACITY,MODE,OP,START,SEEN,SENTENCES,ENDED,LIMITS,VERSION} from './schema.mjs';

export const sha=bytes=>crypto.createHash('sha256').update(bytes).digest('hex');
export function fail(code,message){const error=new Error(message);error.code=code;return error;}
export function cells(file){
 const bytes=fs.readFileSync(file);
 if(bytes.length<29||bytes.subarray(0,5).toString()!=='RVPC2')throw fail('E_STATE','Invalid RVPC2 state');
 const core=bytes.readBigUInt64LE(5),memory=bytes.readBigUInt64LE(13);
 if(core+memory!==BigInt(bytes.length-29))throw fail('E_STATE','Invalid RVPC2 lengths');
 const map=new Map();
 for(const line of bytes.subarray(29+Number(core)).toString().split('\n'))if(line.startsWith('O ')){const end=line.indexOf(' ',2),value=Number(line.slice(end+1));if(value)map.set(BigInt(line.slice(2,end)),value);}
 return map;
}
export const readBytes=(map,address,n)=>Buffer.from(Array.from({length:n},(_,i)=>map.get(address+BigInt(i))||0));
export const readNumber=(map,address,n=4)=>{let result=0;for(let i=0;i<n;i++)result+=(map.get(address+BigInt(i))||0)*256**i;return result;};
export function run(runtime,args){
 const p=spawnSync(runtime,args,{encoding:'utf8',timeout:30000,maxBuffer:4*1024*1024});
 if(p.status!==0)throw fail('E_NATIVE',p.stderr||p.error?.message||'El ejecutor XI no terminó.');
 return p.stdout;
}
export function speech(jsonl){
 const out=[];for(const line of jsonl.split('\n'))if(line.startsWith('{')){const event=JSON.parse(line);if(event.type==='register'&&event.register==='r14'){if(!Number.isInteger(event.value)||event.value<0||event.value>255)throw fail('E_OUTPUT','Invalid native output byte');out.push(event.value);}}
 return Buffer.from(out);
}
export function verified(runtime,base){
 const directory=path.join(base,'..','capacity'),manifest=JSON.parse(fs.readFileSync(path.join(directory,'build.json')));
 if(manifest.version!==VERSION||JSON.stringify(manifest.limits)!==JSON.stringify(LIMITS))throw fail('E_BUILD','Entrega X10 incompatible.');
 if(sha(fs.readFileSync(runtime))!==manifest.runtime_sha256)throw fail('E_BUILD','El ejecutor no coincide con X10.');
 const roles={};for(const[name,digest]of Object.entries(manifest.roles)){const file=path.join(directory,name);if(sha(fs.readFileSync(file))!==digest)throw fail('E_BUILD','Activo X10 alterado: '+name);roles[name]=file;}
 return {manifest,roles};
}
export class NativePages{
 constructor(runtime,roles,directory){this.runtime=runtime;this.roles=roles;this.directory=directory;this.state=path.join(directory,'page.rvp');this.sequence=0;run(runtime,['init',this.state]);}
 stage({data=Buffer.alloc(0),offset=0,total=data.length,numbers=[],bytes=[]}={}){
  const lines=['#!reverse-pc-machine-v1'];
  const put=(address,value,n=4)=>{if(!Number.isSafeInteger(value)||value<0||value>=256**n)throw fail('E_FRAME','Invalid native integer');for(let i=0;i<n;i++)lines.push(`store8 ${address+BigInt(i)} ${Math.floor(value/256**i)%256}`);};
  put(LENGTH,data.length);put(TOTAL,total);put(OFFSET,offset);
  for(const[a,v,n]of numbers)put(a,v,n);
  for(const[a,buffer]of [[INPUT,data],...bytes])for(const[i,v]of buffer.entries())lines.push(`store8 ${a+BigInt(i)} ${v}`);
  lines.push('halt');const file=path.join(this.directory,'frame.xi');fs.writeFileSync(file,lines.join('\n')+'\n',{mode:0o600});run(this.runtime,['run',file,this.state,this.state]);
 }
 role(name){return run(this.runtime,['run',this.roles[name],this.state,this.state]);}
 map(){return cells(this.state);}
 validate(raw){
  if(!raw.length)throw fail('E_EMPTY','El mensaje está vacío.');
  if(raw.length>LIMITS.input_bytes)throw fail('E_SIZE',`El mensaje supera ${LIMITS.input_bytes} bytes.`);
  for(let offset=0;offset<raw.length;offset+=LIMITS.page_bytes){this.stage({data:raw.subarray(offset,offset+LIMITS.page_bytes),offset,total:raw.length});this.role('validate.rxe');if(readNumber(this.map(),STATUS,1))throw fail('E_UTF8','El mensaje contiene UTF-8 no válido o un control no permitido.');}
  if(readNumber(this.map(),B+48n,1))throw fail('E_UTF8','El mensaje termina en una secuencia UTF-8 incompleta.');
 }
 route(raw){this.stage({data:raw.subarray(0,LIMITS.page_bytes),total:raw.length});this.role('route.rxe');const map=this.map();if(readNumber(map,STATUS,1))throw fail('E_FORMAT','Se requiere una lección completa dentro de los límites de sus campos.');return {mode:readNumber(map,MODE,1),operation:readNumber(map,OP,1),key:readBytes(map,KEY,readNumber(map,KEY_LENGTH,1))};}
 record(record,{count,revision,capacity=LIMITS.lessons}){
  this.stage({numbers:[[COUNT,count],[REVISION,revision],[CAPACITY,capacity],[EXISTS,record?1:0,1]],bytes:[[RECORD,record||Buffer.alloc(ROW_BYTES)]]});
  const response=speech(this.role('record.rxe')),map=this.map();
  return {response:new TextDecoder('utf-8',{fatal:true}).decode(response),status:readNumber(map,STATUS,1),record:readNumber(map,EXISTS,1)?readBytes(map,RECORD,ROW_BYTES):null,count:readNumber(map,COUNT),revision:readNumber(map,REVISION)};
 }
 stream(raw,mode){
  const parts=mode===3?[Buffer.from('Resumen extractivo: ')]:[];let total=parts.reduce((n,p)=>n+p.length,0);
  this.stage({numbers:[[SEEN,0],[ENDED,0,1],[B+83n,0,1]]});
  for(let offset=0;offset<raw.length;offset+=LIMITS.page_bytes){
   this.stage({data:raw.subarray(offset,offset+LIMITS.page_bytes),offset,total:raw.length});
   const output=speech(this.role('stream.rxe'));total+=output.length;if(total>LIMITS.output_bytes)throw fail('E_OUTPUT_SIZE','La respuesta supera la capacidad configurada.');parts.push(output);
  }
  return new TextDecoder('utf-8',{fatal:true}).decode(Buffer.concat(parts));
 }
}
