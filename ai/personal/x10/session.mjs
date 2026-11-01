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
import {relationalTurn} from '../p02/relational.mjs';
import {REASON_MAX_BYTES,REASON_MODE} from '../p03/reason.mjs';
import {COMPOSE_LIMIT} from '../p04/compose.mjs';
import {history,contextTurn,saveConversation} from '../p05/store.mjs';
import {PARAPHRASE_MAX_INPUT,PARAPHRASE_MODES} from '../p06/paraphrase.mjs';
import {quantumConversation} from '../../../integration/qml_qrl/conversation.mjs';
import {cognitiveDecision,cognitiveTurn} from '../../../integration/c12/shadow.mjs';
import {c14Shadow} from '../../../integration/c14/shadow.mjs';
import {c15Shadow,recordFeedback} from '../../../integration/c15/agent.mjs';

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
function synchronizeLegacy(db,runtime,input,job,keepDirty=false){
 const dirty=db.prepare('SELECT slot,record FROM dirty_slots ORDER BY slot').all();if(!dirty.length)return;
 for(const[rowIndex,item]of dirty.entries()){
  let source='#!reverse-pc-machine-v1\n';for(const[i,value]of Buffer.from(item.record).entries())source+=`store8 ${LEGACY_ROWS+BigInt(item.slot*ROW_BYTES+i)} ${value}\n`;
  if(rowIndex===dirty.length-1){const count=db.prepare('SELECT COUNT(*) AS n FROM legacy_slots JOIN lessons USING(key)').get().n,revision=Number(get(db,'revision'));for(const[address,value,n]of [[LEGACY_BANK+2n,count,2],[LEGACY_BANK+8n,revision,4]])for(let i=0;i<n;i++)source+=`store8 ${address+BigInt(i)} ${Math.floor(value/256**i)%256}\n`;}
  source+='halt\n';const file=path.join(job,'sync-legacy.xi');fs.writeFileSync(file,source);run(runtime,['run',file,input,input]);
 }
 if(!keepDirty)db.exec('DELETE FROM dirty_slots');
}
function fallback(db,runtime,base,raw,options,job,readOnly=false){
 if(raw.length>16384)throw fail('E_UNSUPPORTED_TEXT','Esta operación conserva su límite de 16384 bytes. Los mensajes de hasta 1 MiB admiten repetición exacta y resumen extractivo.');
 const stored=db.prepare('SELECT data,digest FROM state WHERE id=1').get(),bytes=zlib.inflateRawSync(stored.data,{maxOutputLength:32*1024*1024});
 if(sha(bytes)!==stored.digest)throw fail('E_STATE','La memoria persistente no coincide con su huella.');
 const input=path.join(job,'main.rvp'),output=path.join(job,'next.rvp');fs.writeFileSync(input,bytes,{mode:0o600});synchronizeLegacy(db,runtime,input,job,readOnly);
 let result;
 if(options.operation==='import'){
  const m=JSON.parse(fs.readFileSync(path.join(base,'build.json'))),source=path.join(base,'conversation.xi');if(sha(fs.readFileSync(source))!==m.conversation_source_sha256)throw fail('E_BUILD','Fuente de importación alterada.');
  const r=importDocument(runtime,source,input,output,options.title,raw);result={ok:true,committed:true,response:'Documento incorporado.',bytes:r.bytes,parts:r.parts};
 }else result=legacyChat(runtime,base,input,output,raw,{language:options.language});
 if(!result.ok)throw fail(result.error.code,result.error.message);
 // Generated programs are durable attachments, not paths into a deleted job.
 const attachments={};if(fs.existsSync(output+'.files'))for(const name of fs.readdirSync(output+'.files'))attachments[name]=fs.readFileSync(path.join(output+'.files',name)).toString('base64');
 // A non-teaching message may execute the old reasoning modules, but its
 // tentative RVPC2 changes are discarded. Preserve pending X10 dirty slots.
 if(!readOnly){
  const next=fs.readFileSync(output);db.prepare('UPDATE state SET data=?,digest=? WHERE id=1').run(zlib.deflateRawSync(next),sha(next));
  const revision=readNumber(cells(output),LEGACY_BANK+8n);put(db,'revision',Math.max(revision,Number(get(db,'revision'))));
 }
 // Prevent a legacy acknowledgement from claiming a fact was durably saved.
 const acknowledged=['Registré tus datos.','Registré esa afirmación.'];
 const response=readOnly&&acknowledged.includes(result.response)?'Recibí la afirmación, pero no la guardé como aprendizaje. Para conservarla, pide «recuerda que ...».':result.response;
 return {...result,response,output:undefined,...(Object.keys(attachments).length?{attachments}:{}),extension:'X09-preserved',knowledge_read_only:readOnly};
}
function generalized(db,pages,raw,roles,{explicit=false}={}){
 if(!roles['paraphrase.rxe']){
  if(explicit)throw fail('E_P06_BUILD','P06 necesita reconstruir X10 con el rol nativo de reformulación.');
  return null;
 }
 if(raw.length>PARAPHRASE_MAX_INPUT)return explicit?{ok:true,response:'Este texto supera el límite P06 de 512 bytes. No cambié ninguna memoria.',extension:'P06-abstained-XI',knowledge_read_only:true,paraphrase_handled:false}:null;
 const transformed=pages.paraphrase(raw);
 const abstain={ok:true,response:'No reconozco una equivalencia lingüística comprobada para esa frase. No voy a cambiar su significado ni inventar una respuesta.',extension:'P06-abstained-XI',knowledge_read_only:true,paraphrase_handled:false};
 if(!transformed.handled)return explicit?abstain:null;
 const canonical=Buffer.from(transformed.canonical,'utf8');let result;
 if(transformed.mode===PARAPHRASE_MODES.recall&&roles['context.rxe']){
  const rows=history(db),decision=pages.context(canonical,rows.map(row=>row.utterance));
  result=contextTurn(db,decision,rows);
 }else if([PARAPHRASE_MODES.poem,PARAPHRASE_MODES.story,PARAPHRASE_MODES.explanation].includes(transformed.mode)&&roles['compose.rxe']){
  const composed=pages.compose(canonical),expected=transformed.mode===PARAPHRASE_MODES.poem?1:transformed.mode===PARAPHRASE_MODES.story?2:3;
  if(composed.handled&&composed.mode===expected)
   result={ok:true,response:composed.response,extension:'P04-native-XI',composition_mode:composed.mode,composition_units:composed.count,knowledge_read_only:true};
 }else if(transformed.mode===PARAPHRASE_MODES.reasoning&&roles['reason.rxe']){
  let reason;
  try{reason=pages.reason(canonical);}catch(e){if(e.code!=='E_P03_FORMAT')throw e;}
  if(reason?.eligible&&reason.unparsed===0&&![REASON_MODE.partial,REASON_MODE.unsupported].includes(reason.mode))
   result={ok:true,response:reason.response,extension:'P03-native-XI',reasoning_mode:reason.mode,reasoning_premises:reason.premises,knowledge_read_only:true};
 }
 if(!result)return explicit?abstain:null;
 return {...result,paraphrase_handled:true,paraphrase_rule:transformed.rule,
  paraphrase_mode:transformed.mode,paraphrase_canonical:transformed.canonical,
  paraphrase_engine:'P06-native-XI',knowledge_read_only:true};
}
function execute(db,runtime,base,raw,options,roles,job){
 const pages=new NativePages(runtime,roles,job);pages.validate(raw);
 // The host checks a prefix only to avoid extra native startup for ordinary chat.
 // Authorization, full grammar and operand parsing belong to the XI router.
 const quantumCandidate=options.module==='quantum'||((options.module===undefined||options.module==='x10')&&/^(?:quantum |cuantico |cuántico |bby q quantum )/i.test(raw.subarray(0,64).toString('utf8')));
 if(options.operation!=='import'&&quantumCandidate){
  const decision=pages.quantumRoute(raw);
  if(options.module==='quantum'||decision.prefixed)
   return quantumConversation(db,{runtime,base,job,decision,language:options.language||'es'});
 }
 if(options.module==='c15'){
  if(options.operation==='import'||!options.rlFeedback)
   throw fail('E_C15_FEEDBACK','C15 requiere una calificación explícita de una respuesta anterior.');
  return recordFeedback(db,{runtime,job,feedback:options.rlFeedback,language:options.language||'es'});
 }
 if(options.module==='cognitive'){
  if(options.operation==='import')throw fail('E_COGNITIVE_IMPORT','No se puede importar material como retroalimentación Q.');
  return cognitiveTurn(db,{runtime,roles,job,raw,feedback:options.policyFeedback??null,language:options.language||'es'});
 }
 if(options.module==='p06'){
  if(options.operation==='import')throw fail('E_OPERATION','P06 no procesa importaciones ni modifica entrenamientos.');
  return generalized(db,pages,raw,roles,{explicit:true});
 }
 if(options.operation!=='import'&&(options.module===undefined||options.module==='x10'||options.module==='p05')){
  if(!roles['context.rxe']){
   if(options.module==='p05')throw fail('E_BUILD','Se necesita reconstruir el rol de memoria P05.');
  }else{
   const rows=history(db),decision=pages.context(raw,rows.map(row=>row.utterance));
   const recalled=contextTurn(db,decision,rows,{explicit:options.module==='p05'});
   if(recalled)return recalled;
  }
 }
 if(options.module==='p04'){
  if(options.operation==='import')throw fail('E_OPERATION','P04 no importa documentos.');
  const composed=pages.compose(raw);
  if(!composed.handled)throw fail('E_P04_FORMAT','P04 admite poemas, cuentos e informes causales basados en datos explícitos.');
  return {ok:true,response:composed.response,extension:'P04-native-XI',composition_mode:composed.mode,
   composition_units:composed.count,knowledge_read_only:true,intent_read_only:true};
 }
 if(options.module==='p03'){
  if(options.operation==='import')throw fail('E_OPERATION','P03 no importa documentos ni cambia entrenamientos.');
  const intent=pages.intent(raw),reason=pages.reason(raw);
  return {ok:true,response:reason.response,extension:'P03-native-XI',reasoning_mode:reason.mode,
   reasoning_premises:reason.premises,reasoning_unparsed:reason.unparsed,reasoning_proof_nodes:reason.proof_nodes,
   knowledge_read_only:true,intent:intent.name,intent_confidence:intent.confidence,intent_read_only:true};
 }
 if(options.module==='e034'){
  if(options.operation==='import')throw fail('E_OPERATION','La importación de documentos sigue perteneciendo a X10.');
  const intent=pages.intent(raw),result=relationalTurn(db,{runtime,build:path.resolve(base,'..'),job,raw,language:options.language||'es',learn:options.learn===true});
  return {...result,intent:intent.name,intent_confidence:intent.confidence,intent_read_only:!options.learn};
 }
 if(options.operation==='import')return fallback(db,runtime,base,raw,options,job);
 const route=pages.route(raw),intent=pages.intent(raw);
 const intentMeta={intent:intent.name,intent_confidence:intent.confidence,intent_rule:intent.rule,intent_read_only:intent.readOnly};
 if(route.mode===2||route.mode===3)return {ok:true,response:pages.stream(raw,route.mode),extension:'X10-streamed-text',...intentMeta};
 if(route.mode!==1){
  if((intent.name==='creation'||intent.name==='explanation')&&raw.length<=COMPOSE_LIMIT&&roles['compose.rxe']){
   const composed=pages.compose(raw);
   if(composed.handled)return {ok:true,response:composed.response,extension:'P04-native-XI',
    composition_mode:composed.mode,composition_units:composed.count,knowledge_read_only:true,...intentMeta};
  }
  // Only the native XI program can decide whether a user supplied a complete,
  // supported syllogism. Unsupported/ambiguous text retains the old X09 path.
  if(raw.length<=REASON_MAX_BYTES&&roles['reason.rxe']){
   let reasoning;
   try{reasoning=pages.reason(raw);}catch(error){if(error.code!=='E_P03_FORMAT')throw error;}
   if(reasoning?.eligible&&reasoning.unparsed===0&&reasoning.mode!==REASON_MODE.partial&&reasoning.mode!==REASON_MODE.unsupported)
    return {ok:true,response:reasoning.response,extension:'P03-native-XI',reasoning_mode:reasoning.mode,
     reasoning_premises:reasoning.premises,reasoning_unparsed:reasoning.unparsed,
     reasoning_proof_nodes:reasoning.proof_nodes,knowledge_read_only:true,...intentMeta};
  }
  // Native P06 proposes only bounded, read-only paraphrases after all
  // existing skills had the chance to process the original message.
  if(raw.length<=PARAPHRASE_MAX_INPUT&&roles['paraphrase.rxe']&&
     !['teaching','correction'].includes(intent.name)){
   const alternative=generalized(db,pages,raw,roles);
   if(alternative)return {...alternative,...intentMeta};
  }
  return {...fallback(db,runtime,base,raw,options,job,intent.readOnly),...intentMeta};
 }
 const old=route.operation===8?undefined:db.prepare('SELECT record,digest FROM lessons WHERE key=?').get(route.key);
 if(old&&sha(old.record)!==old.digest)throw fail('E_RECORD','La página de entrenamiento no coincide con su huella.');
 // A missing definition can still be known by an older reasoning module.
 if(!old&&route.operation>=4&&route.operation<=7)return {...fallback(db,runtime,base,raw,options,job,true),...intentMeta};
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
 return {ok:true,response:result.response,extension:'X10-paged-lessons',lessons:result.count,revision:result.revision,...intentMeta};
}
export function transact(runtime,base,root,requestId,message,options={}){
 let db,job,outcome,inTransaction=false;
 try{
  if(typeof requestId!=='string'||!/^[A-Za-z0-9_.-]{1,96}$/.test(requestId))throw fail('E_REQUEST_ID','Identificador de operación no válido.');
  if(typeof message==='string'&&!message.isWellFormed())throw fail('E_UTF16','El texto contiene un sustituto Unicode sin pareja.');
  if(!(typeof message==='string'||Buffer.isBuffer(message)||message instanceof Uint8Array))throw fail('E_INPUT_TYPE','Se requiere texto o bytes UTF-8.');
  if(options.language!==undefined&&!['es','en'].includes(options.language))throw fail('E_LANGUAGE','Idioma no válido.');
  if(options.operation!==undefined&&!['chat','import'].includes(options.operation))throw fail('E_OPERATION','Operación no compatible.');
  if(options.module!==undefined&&!['x10','e034','p03','p04','p05','p06','quantum','cognitive','c15'].includes(options.module))throw fail('E_MODULE','Módulo conversacional desconocido.');
  if(options.learn!==undefined&&typeof options.learn!=='boolean')throw fail('E_LEARN','La autorización de aprendizaje debe ser booleana.');
  if(options.learn===true&&options.module!=='e034')throw fail('E_LEARN','--learn solo se admite en el módulo E034.');
  if(options.shadow!==undefined&&typeof options.shadow!=='boolean')throw fail('E_COGNITIVE_OPTION','El modo de observación debe ser booleano.');
  if(options.shadowC14!==undefined&&typeof options.shadowC14!=='boolean')throw fail('E_C14_OPTION','El modo C14 debe ser booleano.');
  if(options.shadowC15!==undefined&&typeof options.shadowC15!=='boolean')
   throw fail('E_C15_OPTION','El modo C15 debe ser booleano.');
  if(options.rlFeedback!==undefined){
   const f=options.rlFeedback;
   if(options.module!=='c15'||!f||typeof f.targetId!=='string'||
      !/^[A-Za-z0-9_.-]{1,96}$/.test(f.targetId)||
      !Number.isInteger(f.reward)||f.reward<0||f.reward>100)
    throw fail('E_C15_FEEDBACK','Solo --module=c15 permite --rl-feedback=ID,0..100.');
  }
  if(options.module==='c15'&&!options.rlFeedback)
   throw fail('E_C15_FEEDBACK','Calificación explícita obligatoria para C15.');
  if(options.shadowC15&&options.module==='c15')
   throw fail('E_C15_OPTION','No se observa una respuesta nueva durante una calificación.');
  if(options.shadowC15&&options.operation==='import')
   throw fail('E_C15_IMPORT','C15 no evalúa importaciones de documentos.');
  if(options.shadowC14&&options.operation==='import')throw fail('E_C14_IMPORT','C14 no analiza importaciones de documentos.');
  if(options.policyFeedback!==undefined){
   const f=options.policyFeedback;
   if(options.module!=='cognitive'||!f||!Number.isInteger(f.action)||f.action<0||f.action>3||
     !Number.isInteger(f.reward)||f.reward<0||f.reward>100)
    throw fail('E_COGNITIVE_FEEDBACK','Solo --module=cognitive acepta feedback explícito (ruta 0..3, recompensa 0..100).');
  }
  const raw=Buffer.from(message);if(!raw.length)throw fail('E_EMPTY','El mensaje está vacío.');if(raw.length>LIMITS.input_bytes)throw fail('E_SIZE','El mensaje supera 1048576 bytes.');
  if(!fs.existsSync(fileOf(root)))throw fail('E_SESSION','Sesión X10 no inicializada.');
  const languageTag=options.language===undefined||options.language==='es'?'':('\0language:'+options.language);
  // Preserve historic X09/X10 replay identifiers for the default path.
  const moduleTag=options.module==='e034'?'\0module:e034\0learn:'+(options.learn===true?'1':'0'):options.module==='p03'?'\0module:p03':options.module==='p04'?'\0module:p04':options.module==='p05'?'\0module:p05':options.module==='p06'?'\0module:p06':options.module==='quantum'?'\0module:quantum':options.module==='cognitive'?'\0module:cognitive':options.module==='c15'?'\0module:c15':'';
  const cognitiveTag=(options.shadow?'\0cognitive-shadow:1':'')+(options.shadowC14?'\0c14-shadow:1':'')+(options.shadowC15?'\0c15-shadow:1':'')+(options.policyFeedback?'\0policy-feedback:'+options.policyFeedback.action+','+options.policyFeedback.reward:'')+(options.rlFeedback?'\0rl-feedback:'+options.rlFeedback.targetId+','+options.rlFeedback.reward:'');
  const digest=sha(Buffer.concat([Buffer.from((options.operation||'chat')+'\0'+(options.title||'')+'\0'),raw,Buffer.from(languageTag+moduleTag+cognitiveTag)]));
  const {roles}=verified(runtime,base);db=connect(root);db.exec('BEGIN IMMEDIATE');inTransaction=true;
  if(get(db,'version')!==VERSION)throw fail('E_SESSION','Versión de sesión incompatible.');
  const existing=db.prepare('SELECT digest,result FROM receipts WHERE id=?').get(requestId);
  if(existing){if(existing.digest!==digest)throw fail('E_REPLAY_MISMATCH','El identificador ya corresponde a otro contenido.');const receipt=decode(existing.result);db.exec('ROLLBACK');inTransaction=false;return outcome={...receipt,replayed:true};}
  const generation=Number(get(db,'generation'));
  if(options.expectedGeneration!==undefined&&options.expectedGeneration!==generation)throw fail('E_STALE','La sesión cambió; vuelve a leer su revisión.');
  if(Number(get(db,'operations'))>=LIMITS.session_operations)throw fail('E_SESSION_CAPACITY','Se alcanzó la capacidad de operaciones de esta sesión.');
  job=fs.mkdtempSync(path.join(path.resolve(root),'.x10-turn-'));
  const result=execute(db,runtime,base,raw,options,roles,job);
  if(options.shadow&&options.module!=='cognitive'&&options.operation!=='import'){
   const shadowDir=path.join(job,'shadow-audit');fs.mkdirSync(shadowDir,{mode:0o700});
   result.cognitive_shadow=cognitiveDecision(db,{runtime,roles,job:shadowDir,raw});
   // The actual response is unchanged; this is a non-intervening recommendation.
   result.cognitive_shadow.actual_extension=result.extension??null;
  }
  if(options.shadowC14&&options.operation!=='import'){
   const shadowDir=path.join(job,'c14-shadow');
   try{
    result.c14_shadow=c14Shadow(db,{runtime,roles,job:shadowDir,raw});
    result.c14_shadow.actual_extension=result.extension??null;
   }catch(error){
    // Observational research may fail without cancelling a valid X10 response.
    result.c14_shadow={available:false,applied:false,engine:'C14 native XI',
     code:error.code||'E_C14_NATIVE',reason:error.message};
   }
  }
  if(options.shadowC15&&options.operation!=='import'){
   const shadowDir=path.join(job,'c15-shadow');
   try{
    result.c15_shadow=c15Shadow(db,{runtime,roles,job:shadowDir,raw,result});
    result.c15_shadow.actual_extension=result.extension??null;
   }catch(error){
    // A failed experimental observation must NEVER suppress a valid X10 reply.
    result.c15_shadow={available:false,applied:false,engine:'C15 XI',
     code:error.code||'E_C15_NATIVE',reason:error.message};
   }
  }
  if(Buffer.byteLength(result.response)>LIMITS.output_bytes)throw fail('E_OUTPUT_SIZE','La respuesta supera 1048576 bytes.');
  // Existing X10 builds without P05 remain untouched until their roles are rebuilt.
  if(roles['context.rxe']&&options.operation!=='import')saveConversation(db,raw,result,requestId,generation+1);
  const {context_skip_record,...publicResult}=result;
  const receipt={...publicResult,ok:true,committed:true,version:VERSION,generation:generation+1,requestId,replayed:false,transport:{input_bytes:raw.length,output_bytes:Buffer.byteLength(result.response),page_bytes:LIMITS.page_bytes}};
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
 const db=connect(root);try{const state=db.prepare('SELECT length(data) AS compressed_bytes,digest FROM state WHERE id=1').get();const hasRelational=!!db.prepare("SELECT 1 FROM sqlite_master WHERE type='table' AND name='relational_state'").get();const linked=hasRelational?db.prepare('SELECT digest FROM relational_state WHERE id=1').get():null;const quantumExists=!!db.prepare("SELECT 1 FROM sqlite_master WHERE type='table' AND name='quantum_state'").get();const quantum=quantumExists?db.prepare('SELECT digest FROM quantum_state WHERE id=1').get():null;const cognitiveExists=!!db.prepare("SELECT 1 FROM sqlite_master WHERE type='table' AND name='cognitive_policy'").get();const cognitive=cognitiveExists?db.prepare('SELECT digest FROM cognitive_policy WHERE id=1').get():null;const c15Exists=!!db.prepare("SELECT 1 FROM sqlite_master WHERE type='table' AND name='c15_policy'").get();
 const c15=c15Exists?db.prepare('SELECT digest FROM c15_policy WHERE id=1').get():null;
 const c15FeedbackExists=!!db.prepare("SELECT 1 FROM sqlite_master WHERE type='table' AND name='c15_feedback'").get();
 const c15Feedback=c15FeedbackExists?db.prepare('SELECT count(*) AS n FROM c15_feedback').get().n:0;
 const contextAvailable=!!db.prepare("SELECT 1 FROM sqlite_master WHERE type='table' AND name='conversation_turns'").get();const contextTurns=contextAvailable?db.prepare('SELECT COUNT(*) AS n FROM conversation_turns').get().n:0;return {ok:true,version:get(db,'version'),generation:Number(get(db,'generation')),operations:Number(get(db,'operations')),lessons:Number(get(db,'count')),revision:Number(get(db,'revision')),limits:LIMITS,source_sha256:get(db,'source_sha256'),state_sha256:state.digest,compressed_state_bytes:state.compressed_bytes,relational_enabled:!!linked,relational_state_sha256:linked?.digest||null,conversation_index_turns:contextTurns,quantum_connected:!!quantum,quantum_state_sha256:quantum?.digest||null,cognitive_policy_sha256:cognitive?.digest||null,c15_policy_sha256:c15?.digest||null,c15_feedback_events:c15Feedback,integrity:db.prepare('PRAGMA integrity_check').get().integrity_check};}finally{db.close();}
}
