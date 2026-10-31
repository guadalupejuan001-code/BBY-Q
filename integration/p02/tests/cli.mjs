// Exercise real bbyq.mjs turn/status/receipts for E034 against a synthetic,
// deliberately untrained X10 storage fixture. This does NOT test the X09 seed.
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import zlib from 'node:zlib';
import {spawnSync} from 'node:child_process';
import {DatabaseSync} from 'node:sqlite';
import {fileURLToPath} from 'node:url';
import {validatorSource,routerSource,recordSource,streamSource} from '../../../ai/personal/x10/native.mjs';
import {intentSource} from '../../../ai/personal/p01/intent.mjs';
import {LIMITS,VERSION} from '../../../ai/personal/x10/schema.mjs';
import {installRelational,LEARNED_SHA} from '../../../ai/personal/p02/relational.mjs';
import {transact,inspect} from '../../../ai/personal/x10/session.mjs';

const [runtimeArg,appArg,outputArg]=process.argv.slice(2);
if(!outputArg)throw Error('Usage: cli.mjs REVERSE_PC E034_APP NEW_OUTPUT_DIR');
const runtime=path.resolve(runtimeArg),app=path.resolve(appArg),out=path.resolve(outputArg);
if(fs.existsSync(out))throw Error('Choose a new CLI evidence directory.');
const repo=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'../../..');
const build=path.join(out,'build'),session=path.join(out,'session');
fs.mkdirSync(path.join(build,'native'),{recursive:true});
fs.mkdirSync(path.join(build,'capacity'),{recursive:true});
fs.mkdirSync(path.join(build,'runtime'),{recursive:true});fs.mkdirSync(session);
const sha=bytes=>crypto.createHash('sha256').update(bytes).digest('hex');
function native(...args){
 const p=spawnSync(runtime,args,{encoding:'utf8',timeout:30000,maxBuffer:4*1024*1024});
 if(p.status!==0)throw Error('native XI: '+(p.stderr||p.stdout||p.error?.message));
}
const roles={};
for(const [name,code] of [['validate',validatorSource()],['route',routerSource()],['record',recordSource()],['stream',streamSource()],['intent',intentSource()]]){
 const source=path.join(build,'capacity',name+'.xi'),compiled=path.join(build,'capacity',name+'.rxe');
 fs.writeFileSync(source,code);native('compile',source,compiled,'BBY Q P02 X10 test '+name);
 roles[name+'.xi']=sha(fs.readFileSync(source));roles[name+'.rxe']=sha(fs.readFileSync(compiled));
}
fs.copyFileSync(runtime,path.join(build,'runtime','reverse_pc'));
fs.writeFileSync(path.join(build,'capacity','build.json'),JSON.stringify({version:VERSION,limits:LIMITS,
 runtime_sha256:sha(fs.readFileSync(runtime)),roles},null,2)+'\n');
fs.writeFileSync(path.join(build,'native','build.json'),'{"version":"X09-All-Training-1","fixture":"synthetic-untrained"}\n');
assert.equal(sha(fs.readFileSync(app)),'a0edbe6122beb5ab57d0e2dbd60c26524bc946737806eb71f2ed133fde068a28');
installRelational(build);
const db=new DatabaseSync(path.join(session,'memory.sqlite'));
db.exec(
 'CREATE TABLE metadata(key TEXT PRIMARY KEY,value TEXT NOT NULL) STRICT;'+
 'CREATE TABLE state(id INTEGER PRIMARY KEY CHECK(id=1),data BLOB NOT NULL,digest TEXT NOT NULL) STRICT;'+
 'CREATE TABLE receipts(id TEXT PRIMARY KEY,digest TEXT NOT NULL,generation INTEGER NOT NULL,result BLOB NOT NULL) STRICT;'
);
for(const [key,value] of Object.entries({version:VERSION,generation:'0',operations:'0',count:'0',revision:'0',source_sha256:'synthetic-x10-no-x09-training'}))
 db.prepare('INSERT INTO metadata VALUES(?,?)').run(key,value);
const synthetic=Buffer.from('SYNTHETIC_P02_NO_X09_PAYLOAD');
db.prepare('INSERT INTO state VALUES(1,?,?)').run(zlib.deflateRawSync(synthetic),sha(synthetic));
db.close();
const originalState=inspect(session).state_sha256;
const q=(id,message,options={})=>transact(runtime,path.join(build,'native'),session,id,message,{language:'es',module:'e034',...options});
const lines=[];
function check(label,r,needle){
 assert.equal(r.ok,true,JSON.stringify({label,error:r.error}));
 if(needle)assert.match(r.response,needle);
 lines.push({label,request:r.requestId,generation:r.generation,response:r.response,replayed:r.replayed,extension:r.extension});
 return r;
}
const hello=check('greeting',q('one','hola'),/Hola/);
assert.equal(hello.extension,'E034-isolated-XI');
const replay=check('replay',q('one','hola'),/Hola/);
assert.equal(replay.replayed,true);
assert.equal(inspect(session).generation,1);
assert.equal(q('one','hola',{learn:true}).error.code,'E_REPLAY_MISMATCH');
check('teach-day',q('day','El taller korla abre el viernes.',{learn:true}),/Registré esa relación/);
check('teach-place',q('place','El taller korla está en el patio norte.',{learn:true}),/Registré esa relación/);
const composed=check('composition',q('joint','¿Qué día abre y dónde está el taller korla?'),/viernes.*patio norte/s);
assert.equal(composed.learn_requested,false);
check('followup',q('follow','¿Y dónde está ese taller?'),/patio norte/);
const pre=inspect(session);
const injected=q('failed','El taller korla abre el jueves.',{learn:true,testFault:'before_commit'});
assert.equal(injected.ok,false);assert.equal(injected.error.code,'E_INJECTED');
assert.deepEqual(inspect(session),pre);
check('after-rollback',q('still','¿Qué día abre y dónde está el taller korla?'),/viernes.*patio norte/s);
const now=inspect(session);
assert.equal(now.relational_enabled,true);
assert.notEqual(now.relational_state_sha256,LEARNED_SHA);
assert.equal(now.state_sha256,originalState,'Main untrained X10 state was never rewritten');
const mainCLI=path.join(repo,'bbyq.mjs');
const p=spawnSync(process.execPath,[mainCLI,'--build',build,'turn',session,'cli-one','--module=e034','¿Dónde está el taller korla?'],{encoding:'utf8',timeout:30000,maxBuffer:1024*1024});
assert.equal(p.status,0,p.stderr);
const output=JSON.parse(p.stdout);assert.equal(output.ok,true);assert.match(output.response,/patio norte/);
assert.equal(inspect(session).state_sha256,originalState);
const report={ok:true,base:'synthetic X10 SQLite fixture (no X09 runtime model)',execution:'real NativePages, verified XI P01/X10 roles, E034 app-turn, bbyq.mjs CLI and X10 SQLite receipts',
  interactions:lines.length+2,main_state_untouched:true,replay_conflict_rejected:true,rollback_verified:true,cli_verified:true,rows:lines};
fs.writeFileSync(path.join(out,'result.json'),JSON.stringify(report,null,2)+'\n');
console.log(JSON.stringify({ok:true,interactions:report.interactions,main_state_untouched:true,replay_conflict_rejected:true,rollback_verified:true,cli_verified:true}));
