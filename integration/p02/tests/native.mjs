// End-to-end native E034 sidecar examination with a frozen artifact and an
// independently created X10-like SQLite transaction. No simulated XI answers.
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import zlib from 'node:zlib';
import {performance} from 'node:perf_hooks';
import {DatabaseSync} from 'node:sqlite';
import {installRelational,verifyRelational,relationalTurn,learnedSeed,CAPSULE_SHA,LEARNED_SHA} from '../../../ai/personal/p02/relational.mjs';
import {cells,readNumber} from '../../../ai/personal/x10/pages.mjs';

const [runtimeArg,appArg,outputArg]=process.argv.slice(2);
if(!outputArg)throw Error('Usage: node integration/p02/tests/native.mjs REVERSE_PC VERIFIED_E034_APP NEW_OUTPUT_DIR');
const runtime=path.resolve(runtimeArg),app=path.resolve(appArg),out=path.resolve(outputArg);
if(fs.existsSync(out))throw Error('Select a new evidence directory.');
fs.mkdirSync(out,{recursive:true});
const build=path.join(out,'build'),session=path.join(out,'session'),base=8400000000000000000n;
fs.mkdirSync(path.join(build,'capacity'),{recursive:true});fs.mkdirSync(path.join(build,'native'));
fs.mkdirSync(session);
fs.writeFileSync(path.join(build,'capacity','build.json'),'{"version":"X10-Paged-Capacity-1"}\n');
fs.writeFileSync(path.join(build,'native','build.json'),'{"version":"X09-All-Training-1"}\n');
const sha=x=>crypto.createHash('sha256').update(x).digest('hex');
const originalCap=sha(fs.readFileSync(path.join(build,'capacity','build.json')));
const originalNative=sha(fs.readFileSync(path.join(build,'native','build.json')));
const manifest=installRelational(build,app);
assert.equal(manifest.ok,true);
assert.equal(manifest.capsule_sha256,CAPSULE_SHA);
assert.equal(manifest.seed_sha256,LEARNED_SHA);
assert.equal(installRelational(build,app).alreadyInstalled,true);
assert.equal(sha(fs.readFileSync(path.join(build,'capacity','build.json'))),originalCap);
assert.equal(sha(fs.readFileSync(path.join(build,'native','build.json'))),originalNative);
assert.equal(sha(verifyRelational(build).seed),LEARNED_SHA);
const db=new DatabaseSync(path.join(session,'memory.sqlite'));db.exec('PRAGMA synchronous=FULL');
const rows=[],start=performance.now();
function ask(text,{learn=false,language='es'}={}){
 const job=path.join(out,'job');fs.mkdirSync(job,{recursive:true});
 const tick=performance.now();db.exec('BEGIN IMMEDIATE');
 let result;
 try{
  result=relationalTurn(db,{runtime,build,job,raw:Buffer.from(text),language,learn});
  assert.equal(result.ok,true);
  db.exec('COMMIT');
 }catch(error){db.exec('ROLLBACK');throw error;}
 finally{for(const f of fs.readdirSync(job))fs.rmSync(path.join(job,f),{force:true,recursive:true});}
 const row={input:text,learn,language,response:result.response,ms:performance.now()-tick,digest:result.relational_state_sha256};
 rows.push(row);return result;
}
function status(){
 const row=db.prepare('SELECT data,digest FROM relational_state WHERE id=1').get();
 const raw=zlib.gunzipSync(row.data),mapFile=path.join(out,'inspect.rvp');
 assert.equal(sha(raw),row.digest);
 fs.writeFileSync(mapFile,raw);
 const map=cells(mapFile),journal=readNumber(map,base+3n,1);
 fs.unlinkSync(mapFile);return {digest:row.digest,journal};
}
// Real, restricted E034 conversation plus retained historical context commands.
const greeting=ask('hola');
assert.match(greeting.response,/Hola/);
assert.equal(status().digest,LEARNED_SHA,'read-only greeting must retain original training exactly');
const open=ask('El taller galaxa abre el viernes.',{learn:true});
assert.match(open.response,/Registré esa relación/);
const place=ask('El taller galaxa está en la sala naranja.',{learn:true});
assert.match(place.response,/Registré esa relación/);
assert.equal(status().journal,2,'two explicitly taught relational events');
const originalFacts=status().journal;
const comp=ask('¿Qué día abre y dónde está el taller galaxa?');
assert.match(comp.response,/viernes.*sala naranja/s);
assert.match(comp.response,/#r001/);
assert.match(comp.response,/#r002/);
assert.equal(status().journal,originalFacts);
const follow=ask('¿Y dónde está ese taller?');
assert.match(follow.response,/sala naranja/);
assert.equal(status().journal,originalFacts,'follow-up did not insert a fact');
const withoutLearn=ask('El taller galaxa está en la sala verde.');
assert.match(withoutLearn.response,/no se guardó/);
assert.equal(status().journal,originalFacts,'ordinary statement was not persisted');
const repeat=ask('¿Dónde está el taller galaxa?');
assert.match(repeat.response,/sala naranja/);
assert.equal(status().journal,originalFacts);
const context=ask('@ctx add Registro alfa persistente',{learn:true});
assert.match(context.response,/CTX guardado/);
const get=ask('@ctx get 0');
assert.match(get.response,/Registro alfa persistente/);
const dryClear=ask('@ctx clear');
assert.match(dryClear.response,/no se guardó ni borró/);
assert.match(ask('@ctx get 0').response,/Registro alfa persistente/,'read-only clear cannot erase E027 archive');
const dryAdd=ask('@ctx add Registro beta NO persistente');
assert.match(dryAdd.response,/no se guardó ni borró/);
assert.match(ask('@ctx status').response,/n=001/,'read-only append cannot persist an E027 archive record');
// Explicit correction persists while preserving previous evidence.
const correction=ask('Corrijo: el taller galaxa está en la sala verde.',{learn:true});
assert.match(correction.response,/Registré esa relación/);
const revised=ask('¿Qué día abre y dónde está el taller galaxa?');
assert.match(revised.response,/viernes.*sala verde/s);
const cite=ask('@rel source 2');
assert.match(cite.response,/sala naranja/);
// Make sure the original E034 checkpoint is immutable and the old user
// training store never replaced by the sidecar (separate database region).
assert.equal(sha(learnedSeed().raw),LEARNED_SHA);
assert.equal(sha(fs.readFileSync(path.join(build,'capacity','build.json'))),originalCap);
assert.equal(sha(fs.readFileSync(path.join(build,'native','build.json'))),originalNative);
const prior=status(),job=path.join(out,'bad-transaction');fs.mkdirSync(job);
db.exec('BEGIN IMMEDIATE');
assert.throws(()=>relationalTurn(db,{runtime,build,job,raw:Buffer.from('x'.repeat(241)),learn:true}),/240 bytes/);
db.exec('ROLLBACK');
assert.deepEqual(status(),prior,'invalid long request rolled back');
db.close();
const times=rows.map(x=>x.ms).sort((a,b)=>a-b),pct=p=>times[Math.min(times.length-1,Math.ceil(p*times.length)-1)];
const report={ok:true,fixture:'frozen E034 native capsule from historical GitHub Action; original E034 seed from main',
 tests:rows.length+11,actual_native_turns:rows.length,seed_sha256:LEARNED_SHA,capsule_sha256:CAPSULE_SHA,
 median_ms:pct(.5),p95_ms:pct(.95),elapsed_ms:performance.now()-start,
 assertion_scope:'explicit E034 tool mode; read-only focus persistence; isolated relational SQLite state; no X09 ZIP or complete X10 live chat',
 android_validated:false,original_x10_files_unchanged:true,rows};
fs.writeFileSync(path.join(out,'results.json'),JSON.stringify(report,null,2)+'\n');
console.log(JSON.stringify({ok:true,actual_native_turns:rows.length,tests:report.tests,median_ms:report.median_ms,p95_ms:report.p95_ms}));
