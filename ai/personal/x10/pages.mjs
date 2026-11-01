// Byte framing and native page I/O only. No text interpretation or ranking.
import fs from 'node:fs';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import crypto from 'node:crypto';
import {spawnSync} from 'node:child_process';
import {B,INPUT,LENGTH,TOTAL,OFFSET,STATUS,KEY,KEY_LENGTH,RECORD,ROW_BYTES,COUNT,REVISION,EXISTS,CAPACITY,MODE,OP,START,SEEN,SENTENCES,ENDED,LIMITS,VERSION} from './schema.mjs';
import {INTENT_NAMES,INTENT_ADDRESS} from '../p01/intent.mjs';
import {REASON_BASE,REASON_MAX_BYTES,REASON_MODE} from '../p03/reason.mjs';
import {COMPOSE_BASE,COMPOSE_LIMIT,COMPOSE_MODES} from '../p04/compose.mjs';
import {CONTEXT_BASE,CONTEXT_SLOT_BASE,CONTEXT_SLOT_STRIDE,CONTEXT_MAX_CANDIDATES,CONTEXT_MAX_ENTRY_BYTES,CONTEXT_MAX_QUERY_BYTES,CONTEXT_MODES} from '../p05/context.mjs';
import {PARAPHRASE_BASE,PARAPHRASE_MAX_INPUT,PARAPHRASE_MAX_OUTPUT,PARAPHRASE_MODES,PARAPHRASE_RULES} from '../p06/paraphrase.mjs';

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
 quantumRoute(raw){
  // XI alone interprets quantum conversational intent and operands.
  this.stage({data:raw.subarray(0,96),total:raw.length});
  const source=fileURLToPath(new URL('../../xi/qml_qrl/conversation-route.xi',import.meta.url));
  run(this.runtime,['run',source,this.state,this.state]);
  const m=this.map(),address=8180000000000000000n;
  const action=readNumber(m,address,1),first=readNumber(m,address+1n,1),
   second=readNumber(m,address+2n,1),prefixed=readNumber(m,address+3n,1)===1;
  if(![0,1,2,3,4,5,6,7,8,254].includes(action)||
     ([5,7].includes(action)&&(first>1||second>1)))throw fail('E_QUANTUM_ROUTE','Respuesta XI incompatible.');
  return {action,first,second,prefixed};
 }
 route(raw){this.stage({data:raw.subarray(0,LIMITS.page_bytes),total:raw.length});this.role('route.rxe');const map=this.map();if(readNumber(map,STATUS,1))throw fail('E_FORMAT','Se requiere una lección completa dentro de los límites de sus campos.');return {mode:readNumber(map,MODE,1),operation:readNumber(map,OP,1),key:readBytes(map,KEY,readNumber(map,KEY_LENGTH,1))};}
 intent(raw){
  if(!this.roles['intent.rxe'])throw fail('E_BUILD','El módulo P01 no está presente: reconstruye la entrega X10.');
  this.stage({data:raw.subarray(0,LIMITS.page_bytes),total:raw.length});
  this.role('intent.rxe');const m=this.map(),id=readNumber(m,INTENT_ADDRESS,1);
  if(!Number.isInteger(id)||id<0||id>=INTENT_NAMES.length)throw fail('E_INTENT','Respuesta P01 no válida.');
  return {id,name:INTENT_NAMES[id],confidence:readNumber(m,INTENT_ADDRESS+1n,1),readOnly:readNumber(m,INTENT_ADDRESS+2n,1)!==0,rule:readNumber(m,INTENT_ADDRESS+4n,1)};
 }
 reason(raw){
  if(!this.roles['reason.rxe'])throw fail('E_BUILD','P03 requiere un motor X10 recompilado con su rol XI.');
  if(raw.length>REASON_MAX_BYTES)throw fail('E_P03_SIZE','P03 admite hasta '+REASON_MAX_BYTES+' bytes por problema.');
  this.stage({data:raw,total:raw.length});
  const output=speech(this.role('reason.rxe')),map=this.map();
  const mode=readNumber(map,REASON_BASE,1),invalid=readNumber(map,REASON_BASE+6n,1)!==0;
  if(!Number.isInteger(mode)||mode<0||mode>REASON_MODE.partial)throw fail('E_P03_RESULT','El módulo XI entregó un estado incompatible.');
  if(invalid)throw fail('E_P03_FORMAT','Entrada P03 fuera de los límites sintácticos de su gramática.');
  const response=new TextDecoder('utf-8',{fatal:true}).decode(output);
  if(!response)throw fail('E_P03_RESULT','P03 no emitió ninguna respuesta.');
  return {response,mode,eligible:readNumber(map,REASON_BASE+7n,1)===1,
   premises:readNumber(map,REASON_BASE+1n,1),unparsed:readNumber(map,REASON_BASE+2n,1),
   proof_nodes:readNumber(map,REASON_BASE+3n,1),readOnly:true};
 }
 compose(raw){
  if(!this.roles['compose.rxe'])throw fail('E_BUILD','P04 requiere un motor X10 reconstruido con el rol XI de composición.');
  if(raw.length>COMPOSE_LIMIT)throw fail('E_P04_SIZE','El compositor P04 admite un máximo de '+COMPOSE_LIMIT+' bytes.');
  this.stage({data:raw,total:raw.length});
  const output=speech(this.role('compose.rxe')),map=this.map(),handled=readNumber(map,COMPOSE_BASE,1)===1;
  const mode=readNumber(map,COMPOSE_BASE+1n,1),count=readNumber(map,COMPOSE_BASE+2n,1);
  if(handled&&(mode<1||mode>COMPOSE_MODES.grounded_explanation||count<2||count>6))throw fail('E_P04_RESULT','Estructura P04 incompatible.');
  const response=new TextDecoder('utf-8',{fatal:true}).decode(output);
  if(handled&&!response)throw fail('E_P04_RESULT','P04 no produjo una respuesta.');
  if(!handled&&response)throw fail('E_P04_RESULT','P04 no reconocido produjo texto inesperado.');
  return {handled,mode,count,response,readOnly:true};
 }
 context(raw,entries=[]){
  if(!this.roles['context.rxe'])throw fail('E_BUILD','El rol nativo P05 no está instalado en X10.');
  if(raw.length>CONTEXT_MAX_QUERY_BYTES)return {mode:CONTEXT_MODES.unsupported,slot:0,handled:false};
  if(entries.length>CONTEXT_MAX_CANDIDATES)throw fail('E_CONTEXT_FRAME','Demasiados turnos para la ventana P05.');
  const numbers=[[CONTEXT_BASE+3n,entries.length,1]],bytes=[];
  for(const[i,item]of entries.entries()){
   const source=Buffer.from(item);
   if(source.length>CONTEXT_MAX_ENTRY_BYTES)throw fail('E_CONTEXT_FRAME','Un mensaje previo supera el contrato P05.');
   numbers.push([CONTEXT_BASE+32n+BigInt(2*i),source.length,2]);
   bytes.push([CONTEXT_SLOT_BASE+BigInt(CONTEXT_SLOT_STRIDE*i),source]);
  }
  this.stage({data:raw,total:raw.length,numbers,bytes});
  this.role('context.rxe');const map=this.map();
  const mode=readNumber(map,CONTEXT_BASE,1),slot=readNumber(map,CONTEXT_BASE+1n,1);
  if(mode>CONTEXT_MODES.answer||slot>entries.length)throw fail('E_CONTEXT_RESULT','Selección de historial incompatible.');
  if([CONTEXT_MODES.named,CONTEXT_MODES.pronoun,CONTEXT_MODES.last,CONTEXT_MODES.answer].includes(mode)&&slot<1)
   throw fail('E_CONTEXT_RESULT','Referencia al historial sin entrada.');
  return {mode,slot,handled:mode!==CONTEXT_MODES.unsupported,readOnly:true};
 }
 paraphrase(raw){
  if(!this.roles['paraphrase.rxe'])throw fail('E_P06_BUILD','El rol de reformulación XI no está instalado.');
  if(raw.length>PARAPHRASE_MAX_INPUT)return {handled:false,mode:PARAPHRASE_MODES.unsupported,rule:0,canonical:null,readOnly:true};
  this.stage({data:raw,total:raw.length});
  const bytes=speech(this.role('paraphrase.rxe')),map=this.map();
  const handled=readNumber(map,PARAPHRASE_BASE,1)===1,mode=readNumber(map,PARAPHRASE_BASE+1n,1),
   rule=readNumber(map,PARAPHRASE_BASE+2n,1),n=readNumber(map,PARAPHRASE_BASE+3n,2);
  if(!handled){if(bytes.length)throw fail('E_P06_RESULT','El rol XI emitió texto sin reconocer la frase.');
   return {handled:false,mode:PARAPHRASE_MODES.unsupported,rule:0,canonical:null,readOnly:true};}
  if(mode<1||mode>PARAPHRASE_MODES.reasoning||rule<1||rule>PARAPHRASE_RULES.length||
   PARAPHRASE_RULES[rule-1].mode!==mode||n!==bytes.length||n>PARAPHRASE_MAX_OUTPUT)
   throw fail('E_P06_RESULT','Resultado o tamaño de la reformulación XI incompatible.');
  const canonical=new TextDecoder('utf-8',{fatal:true}).decode(bytes);
  if(!canonical||canonical.includes('\0'))throw fail('E_P06_RESULT','Reformulación vacía o inválida.');
  return {handled:true,mode,rule,canonical,readOnly:true};
 }
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
