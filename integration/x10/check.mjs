import fs from 'node:fs';
import path from 'node:path';
import assert from 'node:assert/strict';
import zlib from 'node:zlib';
import {DatabaseSync} from 'node:sqlite';
import {spawn,execFileSync} from 'node:child_process';
import {fileURLToPath} from 'node:url';
import {initialize,transact,inspect,upgradeSession} from '../../ai/personal/x10/session.mjs';
import {initialize as initializeX09,transact as transactX09} from '../../ai/personal/x09/session.mjs';
import {LIMITS,LEGACY_ROWS,LEGACY_BANK} from '../../ai/personal/x10/schema.mjs';
import {sha,cells,readBytes} from '../../ai/personal/x10/pages.mjs';

const repository=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'../..');
const [buildArg,outArg,...flags]=process.argv.slice(2);
if(!outArg)throw Error('Usage: node integration/x10/check.mjs X10_BUILD NEW_EVIDENCE_DIRECTORY [--full-capacity]');
const build=path.resolve(buildArg),base=path.join(build,'native'),runtime=path.join(build,'runtime/reverse_pc'),out=path.resolve(outArg);
if(fs.existsSync(out))throw Error('Choose a fresh evidence directory');fs.mkdirSync(out,{recursive:true});
const observations=[];
async function check(name,fn){const started=performance.now();const detail=await fn();observations.push({name,ok:true,milliseconds:performance.now()-started,...detail});console.log('PASS '+name);}
const pristine=path.join(out,'pristine');
const lesson=(key,definition='un dato de prueba',revision)=>`aprende: ${key}\ndefinición: ${definition}\nrequiere: memoria\nfuente: X10-test\npáginas: 1`;
const clone=name=>{const directory=path.join(out,name);fs.mkdirSync(directory);fs.copyFileSync(path.join(pristine,'memory.sqlite'),path.join(directory,'memory.sqlite'));return directory;};
const ask=(session,id,message,options)=>{const result=transact(runtime,base,session,id,message,options);assert.equal(result.ok,true,JSON.stringify(result));return result;};
const database=session=>new DatabaseSync(path.join(session,'memory.sqlite'));
const metadata=(db,key)=>db.prepare('SELECT value FROM metadata WHERE key=?').get(key).value;
const setMeta=(db,key,value)=>db.prepare('UPDATE metadata SET value=? WHERE key=?').run(String(value),key);
const worker=(session,id,message)=>new Promise((resolve,reject)=>{const p=spawn(process.execPath,[path.join(repository,'integration/x10/tests/worker.mjs'),runtime,base,session,id,message],{stdio:['ignore','pipe','pipe']});let stdout='',stderr='';p.stdout.on('data',b=>stdout+=b);p.stderr.on('data',b=>stderr+=b);p.on('error',reject);p.on('close',code=>code?reject(Error(stderr)):resolve(JSON.parse(stdout)));});

await check('original-seed-and-every-legacy-lesson-preserved',()=>{
 const result=initialize(pristine,base),source=path.join(base,'model.rvp');assert.equal(result.lessons,480);assert.equal(result.source_sha256,sha(fs.readFileSync(source)));
 const map=cells(source),db=database(pristine);try{for(let i=0;i<4096;i++){const address=LEGACY_ROWS+BigInt(i*640);if(map.get(address)!==1)continue;const record=readBytes(map,address,640),key=record.subarray(16,16+record[1]),saved=db.prepare('SELECT record FROM lessons WHERE key=?').get(key);assert.deepEqual(Buffer.from(saved.record),record);}assert.equal(inspect(pristine).state_sha256,result.source_sha256);}finally{db.close();}
 return {legacy_lessons_compared:480,entire_source_sha256:result.source_sha256};
});
await check('learn-reopen-query-correct-and-forget',()=>{
 const session=clone('records');const learned=ask(session,'learn',lesson('Aurora'));assert.equal(learned.lessons,481);
 const answer=ask(session,'query','¿qué es aurora y qué requiere?');assert.match(answer.response,/aurora es un dato de prueba/);assert.match(answer.response,/aurora requiere memoria/);
 const bad=transact(runtime,base,session,'bad-correction',lesson('aurora').replace('aprende:','corrige lección:').replace('\ndefinición:', '\nrevisión: 0\ndefinición:'));assert.equal(bad.ok,false);assert.equal(bad.error.code,'E_REVISION');
 const corrected=lesson('aurora','un dato corregido').replace('aprende:','corrige lección:').replace('\ndefinición:',`\nrevisión: ${learned.revision}\ndefinición:`);ask(session,'correct',corrected);assert.match(ask(session,'after-correct','qué es aurora').response,/dato corregido/);
 const source=ask(session,'source','de dónde sabes aurora');assert.match(source.response,/X10-test/);ask(session,'forget','olvida lección: aurora');assert.equal(inspect(session).lessons,480);
});
await check('idempotence-conflicts-and-atomic-rollback',()=>{
 const session=clone('transactions'),request=lesson('delta');const first=ask(session,'same-id',request);const replay=ask(session,'same-id',request);assert.equal(replay.replayed,true);assert.equal(replay.generation,first.generation);
 assert.equal(transact(runtime,base,session,'same-id',lesson('other')).error.code,'E_REPLAY_MISMATCH');
 assert.equal(transact(runtime,base,session,'conflict',lesson('delta','otra definición')).error.code,'E_CONFLICT');
 const before=inspect(session),failed=transact(runtime,base,session,'fault',lesson('rollback'),{testFault:'before_commit'});assert.equal(failed.ok,false);const after=inspect(session);assert.deepEqual(after,before);
 const db=database(session);try{assert.equal(db.prepare('SELECT count(*) AS n FROM lessons WHERE key=?').get(Buffer.from('rollback')).n,0);assert.equal(db.prepare('SELECT count(*) AS n FROM receipts WHERE id=?').get('fault').n,0);}finally{db.close();}
 assert.equal(ask(session,'fault',lesson('rollback')).lessons,482);
});
await check('malformed-fields-never-change-learning',()=>{
 const session=clone('invalid'),before=inspect(session);
 for(const message of [lesson('x'.repeat(65)),lesson('valid','x'.repeat(225)),lesson('valid').replace('\nfuente: X10-test',''),lesson('valid')+'\nextra',lesson('valid').replace('memoria','\tmemoria')])assert.equal(transact(runtime,base,session,'bad-'+sha(Buffer.from(message)).slice(0,12),message).ok,false);
 assert.deepEqual(inspect(session),before);
});
await check('CRLF-and-capitalized-training-fields-remain-compatible',()=>{
 const session=clone('crlf'),message=(lesson('Aurora')+'\n').replace('definición:','Definición:').replace('requiere:','REQUIERE:').replace('fuente:','Fuente:').replace('páginas:','Páginas:').replaceAll('\n','\r\n');
 ask(session,'crlf',message);assert.match(ask(session,'query','QUÉ ES AURORA').response,/aurora es un dato de prueba/);
});
await check('unicode-pages-and-invalid-sequences-are-atomic',()=>{
 const session=clone('unicode'),prefix='repite exactamente:\n',body='x'.repeat(8192-Buffer.byteLength(prefix)-1)+'🧠ñ中';
 assert.equal(ask(session,'unicode',prefix+body).response,body);const before=inspect(session);
 for(const [i,bytes]of [Buffer.from([0xc0,0x80]),Buffer.from([0xed,0xa0,0x80]),Buffer.from([0xf4,0x90,0x80,0x80]),Buffer.from([0xe2,0x82]),Buffer.from([0])].entries())assert.equal(transact(runtime,base,session,'bad-utf-'+i,Buffer.concat([Buffer.from(prefix+'x'.repeat(8200)),bytes])).ok,false);
 assert.equal(transact(runtime,base,session,'surrogate','\ud800').error.code,'E_UTF16');assert.deepEqual(inspect(session),before);
});
await check('one-MiB-input-and-response-above-old-output-ceiling',()=>{
 const session=clone('maximum-text'),prefix=Buffer.from('repite exactamente:\n'),body=Buffer.alloc(LIMITS.input_bytes-prefix.length,120),message=Buffer.concat([prefix,body]);
 const result=ask(session,'maximum',message);assert.equal(Buffer.byteLength(result.response),body.length);assert.equal(sha(Buffer.from(result.response)),sha(body));
 const before=inspect(session),oversized=transact(runtime,base,session,'too-large',Buffer.concat([message,Buffer.from('x')]));assert.equal(oversized.error.code,'E_SIZE');assert.deepEqual(inspect(session),before);
 return {input_bytes:message.length,output_bytes:body.length,pages:Math.ceil(message.length/LIMITS.page_bytes)};
});
await check('summaries-read-past-64-KiB-and-retain-native-text',()=>{
 const session=clone('summary'),first='A'.repeat(100000)+'.',text=first+' Dos. Tres. Cuatro.';
 const result=ask(session,'summary','resume en 2 frases:\n'+text);assert.equal(result.response,'Resumen extractivo: '+first+' Dos.');
 assert.equal(ask(session,'decimal','resume en 1 frases:\nEl valor es 3.14 y sigue. Otra.').response,'Resumen extractivo: El valor es 3.14 y sigue.');
 const unknown=transact(runtime,base,session,'unknown-long','consulta: '+'a'.repeat(20000));assert.equal(unknown.error.code,'E_UNSUPPORTED_TEXT');
 return {input_bytes:Buffer.byteLength(text),output_bytes:Buffer.byteLength(result.response)};
});
await check('original-reasoning-dictionary-campaign-and-book-still-run',()=>{
 const session=clone('old-modules');assert.equal(ask(session,'math','calcula 17 + 25').response,'El resultado es 42.');
 for(const[id,text]of [['dictionary','define casa'],['campaign','edificio incluye libro'],['book','lee página 1'],['lesson','qué es ahorro']]){const result=ask(session,id,text);assert.ok(result.response.length>1);if(id==='book')assert.match(result.response,/Babilonia/);}
});
await check('legacy-curriculum-updates-are-visible-to-preserved-state',()=>{
 const session=clone('legacy-sync'),db=database(session);let row,key;
 try{row=db.prepare('SELECT key,record FROM lessons JOIN legacy_slots USING(key) LIMIT 1').get();key=Buffer.from(row.key).toString();}finally{db.close();}
 const old=Buffer.from(row.record),revision=old.readUInt32LE(8),correct=lesson(key,'una definición actualizada').replace('aprende:','corrige lección:').replace('\ndefinición:',`\nrevisión: ${revision}\ndefinición:`);
 ask(session,'update',correct);ask(session,'fallback','calcula 1 + 2');
 const next=database(session);try{const saved=next.prepare('SELECT data FROM state WHERE id=1').get(),state=path.join(out,'synchronized.rvp');fs.writeFileSync(state,zlib.inflateRawSync(saved.data));const map=cells(state),slot=next.prepare('SELECT slot FROM legacy_slots WHERE key=?').get(row.key).slot,record=readBytes(map,LEGACY_ROWS+BigInt(slot*640),640);assert.equal(record.subarray(80,80+record[2]).toString(),'una definición actualizada');assert.equal(next.prepare('SELECT count(*) AS n FROM dirty_slots').get().n,0);fs.unlinkSync(state);}finally{next.close();}
});
await check('session-continues-past-4096-historical-operations',()=>{
 const session=clone('history-limit'),db=database(session),receipt=zlib.deflateRawSync(Buffer.from(JSON.stringify({ok:true,committed:true,generation:1,response:'synthetic history fixture'})));
 try{db.exec('BEGIN');const statement=db.prepare('INSERT INTO receipts VALUES(?,?,?,?)');for(let i=0;i<4096;i++)statement.run('history-'+i,'0'.repeat(64),i+1,receipt);setMeta(db,'operations',4096);setMeta(db,'generation',4096);db.exec('COMMIT');}finally{db.close();}
 assert.equal(ask(session,'real-4097','@learn status').generation,4097);assert.equal(inspect(session).operations,4097);
});
await check('concurrent-retries-have-one-durable-commit',async()=>{
 const session=clone('concurrent'),results=await Promise.all([worker(session,'parallel',lesson('paralelo')),worker(session,'parallel',lesson('paralelo'))]);assert.equal(results.filter(r=>r.replayed===false).length,1);assert.equal(results.filter(r=>r.replayed===true).length,1);assert.equal(inspect(session).operations,1);assert.equal(inspect(session).lessons,481);
});
await check('old-session-state-and-replay-history-migrate',()=>{
 const old=path.join(out,'old-x09'),fresh=path.join(out,'migrated');initializeX09(old,base);const original=transactX09(runtime,base,old,'old-request','calcula 2 + 3');assert.equal(original.ok,true);
 const before=sha(fs.readFileSync(path.join(old,'HEAD.json')));const result=upgradeSession(runtime,base,old,fresh);assert.equal(result.original_training_preserved,true);assert.equal(sha(fs.readFileSync(path.join(old,'HEAD.json'))),before);
 const replay=ask(fresh,'old-request','calcula 2 + 3');assert.equal(replay.replayed,true);assert.equal(replay.response,'El resultado es 5.');assert.equal(ask(fresh,'next','@learn status').generation,original.generation+1);
});
await check('tampered-native-role-is-refused-before-commit',()=>{
 const session=clone('integrity'),file=path.join(build,'capacity/route.rxe'),original=fs.readFileSync(file),before=inspect(session);try{fs.appendFileSync(file,'x');assert.equal(transact(runtime,base,session,'bad-role','@learn status').error.code,'E_BUILD');assert.deepEqual(inspect(session),before);}finally{fs.writeFileSync(file,original);}
});
await check('CLI-default-build-and-file-input',()=>{
 const session=clone('cli'),file=path.join(out,'message.txt');fs.writeFileSync(file,'repite exactamente:\nHola desde un archivo.');const result=JSON.parse(execFileSync(process.execPath,[path.join(repository,'bbyq.mjs'),'--build',build,'turn',session,'cli-file','--file',file],{encoding:'utf8'}));assert.equal(result.response,'Hola desde un archivo.');
});
if(flags.includes('--full-capacity'))await check('all-1048576-native-record-pages-and-capacity-refusal',()=>{
 const session=clone('full-capacity'),db=database(session),initial=Number(metadata(db,'count')),started=performance.now();
 try{
  db.exec('BEGIN IMMEDIATE');const insert=db.prepare('INSERT INTO lessons VALUES(?,?,?)');
  for(let i=initial;i<LIMITS.lessons-1;i++){
   const key=Buffer.from('capacity-'+i),record=Buffer.alloc(640);record[0]=1;record[1]=key.length;record[2]=4;record[3]=7;record[4]=9;record[5]=1;record[6]=5;record.writeUInt32LE(1,8);key.copy(record,16);record.write('dato',80);record.write('memoria',304);record.write('sintetico',528);record.write('-',560);insert.run(key,record,sha(record));
   if(i%200000===0)console.log('CAPACITY populated '+i+' synthetic records');
  }
  setMeta(db,'count',LIMITS.lessons-1);db.exec('COMMIT');assert.equal(db.prepare('SELECT count(*) AS n FROM lessons').get().n,LIMITS.lessons-1);
 }finally{db.close();}
 const filled=ask(session,'last-real-slot',lesson('ultimo-espacio'));assert.equal(filled.lessons,LIMITS.lessons);
 for(const index of [initial,Math.floor(LIMITS.lessons/2),LIMITS.lessons-2])assert.match(ask(session,'read-'+index,'qué es capacity-'+index).response,/ es dato/);
 const before=inspect(session),blocked=transact(runtime,base,session,'overflow',lesson('fuera-del-limite'));assert.equal(blocked.error.code,'E_CAPACITY');assert.deepEqual(inspect(session),before);
 ask(session,'delete-final','olvida lección: ultimo-espacio');assert.equal(ask(session,'reuse-final',lesson('espacio-recuperado')).lessons,LIMITS.lessons);
 const audit=database(session);let records;try{records=audit.prepare('SELECT count(*) AS n FROM lessons').get().n;assert.equal(audit.prepare('PRAGMA integrity_check').get().integrity_check,'ok');}finally{audit.close();}
 return {actual_stored_records:records,synthetic_capacity_fixture:true,trained_original_lessons:initial,synthetic_population_milliseconds:performance.now()-started,database_bytes:fs.statSync(path.join(session,'memory.sqlite')).size};
});
if(flags.includes('--full-capacity'))await check('all-1048576-session-receipts-limit-and-replay-at-capacity',()=>{
 const session=clone('full-receipts'),db=database(session),message='historical capacity fixture',digest=sha(Buffer.concat([Buffer.from('chat\0\0'),Buffer.from(message)]));
 try{
  db.exec('BEGIN IMMEDIATE');const insert=db.prepare('INSERT INTO receipts VALUES(?,?,?,?)');
  for(let i=0;i<LIMITS.session_operations-1;i++){
   const id='synthetic-'+i,result={ok:true,committed:true,version:'X10-Paged-Capacity-1',generation:i+1,requestId:id,replayed:false,response:'Historial sintético de prueba.'};insert.run(id,digest,i+1,zlib.deflateRawSync(Buffer.from(JSON.stringify(result)),{level:1}));
   if(i&&i%200000===0)console.log('CAPACITY populated '+i+' synthetic receipts');
  }
  setMeta(db,'operations',LIMITS.session_operations-1);setMeta(db,'generation',LIMITS.session_operations-1);db.exec('COMMIT');
 }finally{db.close();}
 const final=ask(session,'last-real-operation','@learn status');assert.equal(final.generation,LIMITS.session_operations);assert.equal(ask(session,'last-real-operation','@learn status').replayed,true);
 for(const i of [0,500000,LIMITS.session_operations-2]){const replay=ask(session,'synthetic-'+i,message);assert.equal(replay.replayed,true);assert.equal(replay.generation,i+1);assert.equal(replay.requestId,'synthetic-'+i);}
 const before=inspect(session);assert.equal(transact(runtime,base,session,'overflow','@learn status').error.code,'E_SESSION_CAPACITY');assert.deepEqual(inspect(session),before);
 const audit=database(session);let receipts;try{receipts=audit.prepare('SELECT COUNT(*) AS n FROM receipts').get().n;assert.equal(receipts,LIMITS.session_operations);}finally{audit.close();}
 return {actual_stored_receipts:receipts,synthetic_history_fixture:true,native_turns_simulated:false,database_bytes:fs.statSync(path.join(session,'memory.sqlite')).size};
});
const result={ok:true,version:'X10-Paged-Capacity-1',checks:observations.length,limits:LIMITS,full_capacity_executed:flags.includes('--full-capacity'),platform:'Linux x86-64 / Node '+process.versions.node,android_validated:false,observations};
fs.writeFileSync(path.join(out,'results.json'),JSON.stringify(result,null,2)+'\n');console.log(JSON.stringify({ok:true,checks:result.checks,results:path.join(out,'results.json')}));
