// Durable transactions for opaque native memory pages, state and receipts.
// SQLite performs storage/indexing only; text decisions remain in XI roles.
import fs from 'node:fs';
import path from 'node:path';
import zlib from 'node:zlib';
import crypto from 'node:crypto';
import {DatabaseSync} from 'node:sqlite';
import {chat as legacyChat} from '../x09/io.mjs';
import {importDocument} from '../x03/io.mjs';
import {SCHEMA as CAMPAIGN_SCHEMA} from '../x09/campaign/schema.mjs';
import {LIMITS,VERSION,LEGACY_BANK,LEGACY_ROWS,LEGACY_CAPACITY,ROW_BYTES} from './schema.mjs';
import {NativePages,sha,fail,cells,readBytes,readNumber,run,verified} from './pages.mjs';

const encode=value=>zlib.deflateRawSync(Buffer.from(JSON.stringify(value)));
const decode=bytes=>JSON.parse(zlib.inflateRawSync(bytes,{maxOutputLength:64*1024*1024}));
const fileOf=root=>path.join(path.resolve(root),'memory.sqlite');
const connect=root=>{const db=new DatabaseSync(fileOf(root));db.exec('PRAGMA busy_timeout=60000; PRAGMA synchronous=FULL; PRAGMA foreign_keys=ON;');return db;};
const get=(db,key)=>db.prepare('SELECT value FROM metadata WHERE key=?').get(key)?.value;
const put=(db,key,value)=>db.prepare('INSERT INTO metadata(key,value) VALUES(?,?) ON CONFLICT(key) DO UPDATE SET value=excluded.value').run(key,String(value));
const errorResult=error=>({ok:false,committed:false,error:{code:error.code||'E_X10',message:error.message}});
function publishDirectory(staging,destination){
 if(fs.existsSync(destination))throw fail('E_DESTINATION','Elige una sesión nueva.');fs.renameSync(staging,destination);
 try{const fd=fs.openSync(path.dirname(destination),'r');try{fs.fsyncSync(fd);}finally{fs.closeSync(fd);}return {};}
 catch(error){return {durability:{ok:false,message:error.message}};}
}
function validateMain(runtime,base,state,job){
 const manifest=JSON.parse(fs.readFileSync(path.join(base,'build.json')));
 if(manifest.version!=='X09-All-Training-1')throw fail('E_BUILD','Se requiere la base X09 completa.');
 for(const name of ['guard.xi','guard-x07.xi']){const f=path.join(base,name);if(sha(fs.readFileSync(f))!==manifest.roles_sha256[name])throw fail('E_BUILD','Guardia de memoria alterada.');run(runtime,['run',f,state,path.join(job,'checked.rvp')]);}
 // Also verifies the checksum through the original native state loader.
 const map=cells(state);
 if(readNumber(map,LEGACY_BANK,1)!==87||readNumber(map,LEGACY_BANK+1n,1)!==2||readNumber(map,9180000000000000002n,1)!==CAMPAIGN_SCHEMA)throw fail('E_STATE','Se requiere un estado completo X09.');
 return map;
}
export function initialize(root,base,initial,options={}){
 root=path.resolve(root);if(fs.existsSync(root))throw fail('E_DESTINATION','Elige una sesión nueva.');
 const runtime=path.resolve(base,'../runtime/reverse_pc');verified(runtime,base);
 const parent=path.dirname(root);fs.mkdirSync(parent,{recursive:true});const staging=fs.mkdtempSync(path.join(parent,'.x10-init-'));
 let db;
 try{
  const manifest=JSON.parse(fs.readFileSync(path.join(base,'build.json'))),bytes=initial?fs.readFileSync(initial):zlib.gunzipSync(fs.readFileSync(path.join(base,'model.rvp.gz')),{maxOutputLength:32*1024*1024});
  if(!initial&&sha(bytes)!==manifest.model_sha256)throw fail('E_STATE','La semilla entrenada no coincide.');
  const state=path.join(staging,'source.rvp');fs.writeFileSync(state,bytes,{mode:0o600});const map=validateMain(runtime,base,state,staging);
  db=connect(staging);db.exec(`
   PRAGMA journal_mode=DELETE;
   CREATE TABLE metadata(key TEXT PRIMARY KEY,value TEXT NOT NULL) STRICT;
   CREATE TABLE state(id INTEGER PRIMARY KEY CHECK(id=1),data BLOB NOT NULL,digest TEXT NOT NULL) STRICT;
   CREATE TABLE lessons(key BLOB PRIMARY KEY,record BLOB NOT NULL CHECK(length(record)=640),digest TEXT NOT NULL) STRICT;
   CREATE TABLE legacy_slots(key BLOB PRIMARY KEY,slot INTEGER UNIQUE NOT NULL) STRICT;
   CREATE TABLE dirty_slots(slot INTEGER PRIMARY KEY,record BLOB NOT NULL CHECK(length(record)=640)) STRICT;
   CREATE TABLE receipts(id TEXT PRIMARY KEY,digest TEXT NOT NULL,generation INTEGER NOT NULL,result BLOB NOT NULL) STRICT;
   BEGIN IMMEDIATE;
  `);
  const insert=db.prepare('INSERT INTO lessons VALUES(?,?,?)'),slots=db.prepare('INSERT INTO legacy_slots VALUES(?,?)');let count=0;
  for(let slot=0;slot<LEGACY_CAPACITY;slot++){
   const address=LEGACY_ROWS+BigInt(slot*ROW_BYTES);if(readNumber(map,address,1)!==1)continue;
   const record=readBytes(map,address,ROW_BYTES),length=record[1];if(length<1||length>64)throw fail('E_STATE','Clave de lección no válida.');
   const key=record.subarray(16,16+length);insert.run(key,record,sha(record));slots.run(key,slot);count++;
  }
  if(count!==readNumber(map,LEGACY_BANK+2n,2))throw fail('E_STATE','El banco contiene un recuento incompatible.');
  put(db,'version',VERSION);put(db,'generation',0);put(db,'operations',0);put(db,'count',count);put(db,'revision',readNumber(map,LEGACY_BANK+8n));put(db,'limits',JSON.stringify(LIMITS));put(db,'source_sha256',sha(bytes));
  db.prepare('INSERT INTO state VALUES(1,?,?)').run(zlib.deflateRawSync(bytes),sha(bytes));
  if(options.history){
   const {head,root:oldRoot}=options.history;
   const receipt=db.prepare('INSERT INTO receipts VALUES(?,?,?,?)');let operations=0;
   for(const[id,item]of Object.entries(head.requests)){
    if(!/^[A-Za-z0-9_.-]{1,96}$/.test(id)||!/^[a-zA-Z0-9-]+$/.test(item.directory)||!/^[a-f0-9]{64}$/.test(item.digest))throw fail('E_HISTORY','Historial anterior incompatible.');
    const result=JSON.parse(fs.readFileSync(path.join(oldRoot,'versions',item.directory,'receipt.json')));
    receipt.run(id,item.digest,result.generation,encode(result));operations++;
   }
   put(db,'generation',head.generation);put(db,'operations',operations);
  }
  db.exec('COMMIT');db.close();db=null;
  for(const name of ['source.rvp','checked.rvp'])fs.unlinkSync(path.join(staging,name));
  fs.chmodSync(fileOf(staging),0o600);const publication=publishDirectory(staging,root);
  return {ok:true,version:VERSION,session:root,lessons:count,limits:LIMITS,source_sha256:sha(bytes),original_training_preserved:true,...publication};
 }finally{if(db)db.close();if(fs.existsSync(staging))fs.rmSync(staging,{recursive:true,force:true});}
}
export function upgradeSession(runtime,base,oldRoot,newRoot){
 verified(runtime,base);oldRoot=path.resolve(oldRoot);
 const head=JSON.parse(fs.readFileSync(path.join(oldRoot,'HEAD.json')));
 if(!/^[a-zA-Z0-9-]+$/.test(head.directory))throw fail('E_SESSION','Referencia de sesión no válida.');
 const input=path.join(oldRoot,'versions',head.directory,'state.rvp');if(sha(fs.readFileSync(input))!==head.state_sha256)throw fail('E_STATE','El estado anterior no coincide con su huella.');
 // The old session is only read; state and all replay identifiers are retained.
 return initialize(newRoot,base,input,{history:{head,root:oldRoot}});
}
function synchronizeLegacy(db,runtime,input,job){
 const dirty=db.prepare('SELECT slot,record FROM dirty_slots ORDER BY slot').all();if(!dirty.length)return;
 for(const[rowIndex,item]of dirty.entries()){
  let source='#!reverse-pc-machine-v1\n';for(const[i,value]of Buffer.from(item.record).entries())source+=`store8 ${LEGACY_ROWS+BigInt(item.slot*ROW_BYTES+i)} ${value}\n`;
  if(rowIndex===dirty.length-1){const count=db.prepare('SELECT COUNT(*) AS n FROM legacy_slots JOIN lessons USING(key)').get().n,revision=Number(get(db,'revision'));for(const[address,value,n]of [[LEGACY_BANK+2n,count,2],[LEGACY_BANK+8n,revision,4]])for(let i=0;i<n;i++)source+=`store8 ${address+BigInt(i)} ${Math.floor(value/256**i)%256}\n`;}
  source+='halt\n';const file=path.join(job,'sync-legacy.xi');fs.writeFileSync(file,source);run(runtime,['run',file,input,input]);
 }
 db.exec('DELETE FROM dirty_slots');
}
function fallback(db,runtime,base,raw,options,job){
 if(raw.length>16384)throw fail('E_UNSUPPORTED_TEXT','Esta operación conserva su límite de 16384 bytes. Los mensajes de hasta 1 MiB admiten repetición exacta y resumen extractivo.');
 const stored=db.prepare('SELECT data,digest FROM state WHERE id=1').get(),bytes=zlib.inflateRawSync(stored.data,{maxOutputLength:32*1024*1024});
 if(sha(bytes)!==stored.digest)throw fail('E_STATE','La memoria persistente no coincide con su huella.');
 const input=path.join(job,'main.rvp'),output=path.join(job,'next.rvp');fs.writeFileSync(input,bytes,{mode:0o600});synchronizeLegacy(db,runtime,input,job);
 let result;
 if(options.operation==='import'){
  const m=JSON.parse(fs.readFileSync(path.join(base,'build.json'))),source=path.join(base,'conversation.xi');if(sha(fs.readFileSync(source))!==m.conversation_source_sha256)throw fail('E_BUILD','Fuente de importación alterada.');
  const r=importDocument(runtime,source,input,output,options.title,raw);result={ok:true,committed:true,response:'Documento incorporado.',bytes:r.bytes,parts:r.parts};
 }else result=legacyChat(runtime,base,input,output,raw,{language:options.language});
 if(!result.ok)throw fail(result.error.code,result.error.message);
 // Generated programs are durable attachments, not paths into a deleted job.
 const attachments={};if(fs.existsSync(output+'.files'))for(const name of fs.readdirSync(output+'.files'))attachments[name]=fs.readFileSync(path.join(output+'.files',name)).toString('base64');
 const next=fs.readFileSync(output);db.prepare('UPDATE state SET data=?,digest=? WHERE id=1').run(zlib.deflateRawSync(next),sha(next));
 const revision=readNumber(cells(output),LEGACY_BANK+8n);put(db,'revision',Math.max(revision,Number(get(db,'revision'))));
 return {...result,output:undefined,...(Object.keys(attachments).length?{attachments}:{}),extension:'X09-preserved'};
}
function execute(db,runtime,base,raw,options,roles,job){
 const pages=new NativePages(runtime,roles,job);pages.validate(raw);
 if(options.operation==='import')return fallback(db,runtime,base,raw,options,job);
 const route=pages.route(raw);
 if(route.mode===2||route.mode===3)return {ok:true,response:pages.stream(raw,route.mode),extension:'X10-streamed-text'};
 if(route.mode!==1)return fallback(db,runtime,base,raw,options,job);
 const old=route.operation===8?undefined:db.prepare('SELECT record,digest FROM lessons WHERE key=?').get(route.key);
 if(old&&sha(old.record)!==old.digest)throw fail('E_RECORD','La página de entrenamiento no coincide con su huella.');
 // A missing definition can still be known by an older reasoning module.
 if(!old&&route.operation>=4&&route.operation<=7)return fallback(db,runtime,base,raw,options,job);
 const beforeCount=Number(get(db,'count')),beforeRevision=Number(get(db,'revision'));
 const result=pages.record(old?Buffer.from(old.record):null,{count:beforeCount,revision:beforeRevision});
 if(result.status&&result.status!==3)throw fail(['','','E_CONFLICT','E_MISSING','E_CAPACITY','E_REVISION'][result.status]||'E_RECORD',result.response);
 if(result.status===3&&route.operation===2)throw fail('E_MISSING',result.response);
 if(result.record){db.prepare('INSERT INTO lessons VALUES(?,?,?) ON CONFLICT(key) DO UPDATE SET record=excluded.record,digest=excluded.digest').run(route.key,result.record,sha(result.record));}
 else if(route.operation===3)db.prepare('DELETE FROM lessons WHERE key=?').run(route.key);
 if(result.revision!==beforeRevision){
  put(db,'count',result.count);put(db,'revision',result.revision);
  const legacy=db.prepare('SELECT slot FROM legacy_slots WHERE key=?').get(route.key);if(legacy)db.prepare('INSERT INTO dirty_slots VALUES(?,?) ON CONFLICT(slot) DO UPDATE SET record=excluded.record').run(legacy.slot,result.record||Buffer.alloc(ROW_BYTES));
 }
 return {ok:true,response:result.response,extension:'X10-paged-lessons',lessons:result.count,revision:result.revision};
}
export function transact(runtime,base,root,requestId,message,options={}){
 let db,job,outcome,inTransaction=false;
 try{
  if(typeof requestId!=='string'||!/^[A-Za-z0-9_.-]{1,96}$/.test(requestId))throw fail('E_REQUEST_ID','Identificador de operación no válido.');
  if(typeof message==='string'&&!message.isWellFormed())throw fail('E_UTF16','El texto contiene un sustituto Unicode sin pareja.');
  if(!(typeof message==='string'||Buffer.isBuffer(message)||message instanceof Uint8Array))throw fail('E_INPUT_TYPE','Se requiere texto o bytes UTF-8.');
  if(options.language!==undefined&&!['es','en'].includes(options.language))throw fail('E_LANGUAGE','Idioma no válido.');
  if(options.operation!==undefined&&!['chat','import'].includes(options.operation))throw fail('E_OPERATION','Operación no compatible.');
  const raw=Buffer.from(message);if(!raw.length)throw fail('E_EMPTY','El mensaje está vacío.');if(raw.length>LIMITS.input_bytes)throw fail('E_SIZE','El mensaje supera 1048576 bytes.');
  if(!fs.existsSync(fileOf(root)))throw fail('E_SESSION','Sesión X10 no inicializada.');
  const languageTag=options.language===undefined||options.language==='es'?'':('\0language:'+options.language),digest=sha(Buffer.concat([Buffer.from((options.operation||'chat')+'\0'+(options.title||'')+'\0'),raw,Buffer.from(languageTag)]));
  const {roles}=verified(runtime,base);db=connect(root);db.exec('BEGIN IMMEDIATE');inTransaction=true;
  if(get(db,'version')!==VERSION)throw fail('E_SESSION','Versión de sesión incompatible.');
  const existing=db.prepare('SELECT digest,result FROM receipts WHERE id=?').get(requestId);
  if(existing){if(existing.digest!==digest)throw fail('E_REPLAY_MISMATCH','El identificador ya corresponde a otro contenido.');const receipt=decode(existing.result);db.exec('ROLLBACK');inTransaction=false;return outcome={...receipt,replayed:true};}
  const generation=Number(get(db,'generation'));
  if(options.expectedGeneration!==undefined&&options.expectedGeneration!==generation)throw fail('E_STALE','La sesión cambió; vuelve a leer su revisión.');
  if(Number(get(db,'operations'))>=LIMITS.session_operations)throw fail('E_SESSION_CAPACITY','Se alcanzó la capacidad de operaciones de esta sesión.');
  job=fs.mkdtempSync(path.join(path.resolve(root),'.x10-turn-'));
  const result=execute(db,runtime,base,raw,options,roles,job);
  if(Buffer.byteLength(result.response)>LIMITS.output_bytes)throw fail('E_OUTPUT_SIZE','La respuesta supera 1048576 bytes.');
  const receipt={...result,ok:true,committed:true,version:VERSION,generation:generation+1,requestId,replayed:false,transport:{input_bytes:raw.length,output_bytes:Buffer.byteLength(result.response),page_bytes:LIMITS.page_bytes}};
  put(db,'generation',generation+1);put(db,'operations',Number(get(db,'operations'))+1);
  if(Buffer.byteLength(JSON.stringify(receipt))>64*1024*1024)throw fail('E_RECEIPT_SIZE','El comprobante supera la capacidad configurada.');
  db.prepare('INSERT INTO receipts VALUES(?,?,?,?)').run(requestId,digest,generation+1,encode(receipt));
  if(options.testFault==='before_commit')throw fail('E_INJECTED','Injected failure before commit');
  db.exec('COMMIT');inTransaction=false;return outcome=receipt;
 }catch(error){if(db&&inTransaction)try{db.exec('ROLLBACK');}catch{}return outcome=errorResult(error);}
 finally{if(db)db.close();if(job)try{fs.rmSync(job,{recursive:true,force:true});}catch(error){if(outcome)outcome.cleanup={ok:false,message:error.message};}}
}
export function inspect(root){
 if(!fs.existsSync(fileOf(root)))throw fail('E_SESSION','Sesión X10 no inicializada.');
 const db=connect(root);try{const state=db.prepare('SELECT length(data) AS compressed_bytes,digest FROM state WHERE id=1').get();return {ok:true,version:get(db,'version'),generation:Number(get(db,'generation')),operations:Number(get(db,'operations')),lessons:Number(get(db,'count')),revision:Number(get(db,'revision')),limits:LIMITS,source_sha256:get(db,'source_sha256'),state_sha256:state.digest,compressed_state_bytes:state.compressed_bytes,integrity:db.prepare('PRAGMA integrity_check').get().integrity_check};}finally{db.close();}
}
