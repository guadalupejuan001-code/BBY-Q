// End-to-end X10 transactional/CLI test using a synthetic untrained X09 state.
// This verifies native P03 dispatch; it is not a full restored X09 integration.
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
import {reasonSource,REASON_SHA256} from '../../../ai/personal/p03/reason.mjs';
import {LIMITS,VERSION} from '../../../ai/personal/x10/schema.mjs';
import {transact,inspect} from '../../../ai/personal/x10/session.mjs';
const [runtimeArg,outputArg]=process.argv.slice(2);
if(!outputArg)throw Error('Usage: node integration/p03/tests/cli.mjs REVERSE_PC NEW_OUTPUT_DIR');
const runtime=path.resolve(runtimeArg),out=path.resolve(outputArg);
if(fs.existsSync(out))throw Error('P03 CLI fixture requires an empty directory.');
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'../../..'),build=path.join(out,'build'),session=path.join(out,'session');
for(const p of [path.join(build,'capacity'),path.join(build,'native'),path.join(build,'runtime'),session])
 fs.mkdirSync(p,{recursive:true});
const sha=x=>crypto.createHash('sha256').update(x).digest('hex');
function native(...args){
 const p=spawnSync(runtime,args,{encoding:'utf8',timeout:40000,maxBuffer:4*1024*1024});
 if(p.status!==0)throw Error('P03 native compiler: '+(p.stderr||p.error?.message||p.stdout));
}
const roles={};
for(const[name,source]of [['validate',validatorSource()],['route',routerSource()],['record',recordSource()],['stream',streamSource()],['intent',intentSource()],['reason',reasonSource()]]){
 const xi=path.join(build,'capacity',name+'.xi'),rx=path.join(build,'capacity',name+'.rxe');
 fs.writeFileSync(xi,source);native('compile',xi,rx,'BBY Q P03 '+name);
 roles[name+'.xi']=sha(fs.readFileSync(xi));roles[name+'.rxe']=sha(fs.readFileSync(rx));
}
fs.copyFileSync(runtime,path.join(build,'runtime','reverse_pc'));
fs.writeFileSync(path.join(build,'capacity','build.json'),JSON.stringify({version:VERSION,limits:LIMITS,
 runtime_sha256:sha(fs.readFileSync(runtime)),roles,reasoning:{source_sha256:REASON_SHA256}},null,2)+'\n');
fs.writeFileSync(path.join(build,'native','build.json'),'{"version":"X09-All-Training-1","fixture":"untrained-invalid-state"}\n');
const db=new DatabaseSync(path.join(session,'memory.sqlite'));
db.exec('PRAGMA synchronous=FULL;'+
 'CREATE TABLE metadata(key TEXT PRIMARY KEY,value TEXT NOT NULL) STRICT;'+
 'CREATE TABLE state(id INTEGER PRIMARY KEY CHECK(id=1),data BLOB NOT NULL,digest TEXT NOT NULL) STRICT;'+
 'CREATE TABLE receipts(id TEXT PRIMARY KEY,digest TEXT NOT NULL,generation INTEGER NOT NULL,result BLOB NOT NULL) STRICT;'+
 'CREATE TABLE relational_state(id INTEGER PRIMARY KEY CHECK(id=1),data BLOB NOT NULL,digest TEXT NOT NULL) STRICT;');
for(const[key,value]of Object.entries({version:VERSION,generation:'0',operations:'0',count:'0',revision:'0',source_sha256:'synthetic'}))
 db.prepare('INSERT INTO metadata VALUES(?,?)').run(key,value);
const payload=Buffer.from('SYNTHETIC-P03-NO-X09-MODEL'),marker=Buffer.from('P02-MEMORY-SENTINEL');
db.prepare('INSERT INTO state VALUES(1,?,?)').run(zlib.deflateRawSync(payload),sha(payload));
db.prepare('INSERT INTO relational_state VALUES(1,?,?)').run(marker,sha(marker));
db.close();
const initial=inspect(session),base=path.join(build,'native');
function ask(id,message,options={}){return transact(runtime,base,session,id,message,options);}
const text='Todos los gatos son mamíferos. Todos los mamíferos son animales. Luna es un gato. ¿Luna es animal?';
const original=ask('automatic',text,{language:'es'});
assert.equal(original.ok,true,JSON.stringify(original.error));
assert.equal(original.extension,'P03-native-XI');
assert.equal(original.reasoning_mode,1);
assert.match(original.response,/luna -> gato -> mamiferos -> animales/);
assert.equal(original.knowledge_read_only,true);
assert.equal(original.reasoning_premises,3);
const replay=ask('automatic',text,{language:'es'});
assert.equal(replay.replayed,true);
assert.equal(replay.generation,1);
const switched=ask('automatic',text,{language:'es',module:'p03'});
assert.equal(switched.error.code,'E_REPLAY_MISMATCH','module-specific request identity must differ');
const negative=ask('explicit','Luna no es gato. ¿Luna es gato?',{module:'p03'});
assert.equal(negative.reasoning_mode,4);
assert.match(negative.response,/niega expresamente/);
const contradiction=ask('contradiction','Luna es gato. Luna no es gato. ¿Luna es gato?',{module:'p03'});
assert.equal(contradiction.reasoning_mode,3);
const unknown=ask('unknown','Todos los gatos son mamíferos. Luna es gato. ¿Luna es reptil?',{module:'p03'});
assert.equal(unknown.reasoning_mode,2);
const ambiguous=ask('partial','Luna es gato. Pero Luna no es gato. ¿Luna es gato?',{module:'p03'});
assert.equal(ambiguous.reasoning_mode,5);
const prior=inspect(session),injected=ask('failed',text,{module:'p03',testFault:'before_commit'});
assert.equal(injected.ok,false);
assert.equal(injected.error.code,'E_INJECTED');
assert.deepEqual(inspect(session),prior,'failed inference receipt does not commit');
const oversize=ask('oversize','x'.repeat(641),{module:'p03'});
assert.equal(oversize.error.code,'E_P03_SIZE');
assert.deepEqual(inspect(session),prior,'oversize does not commit');
const learn=ask('write-forbidden',text,{module:'p03',learn:true});
assert.equal(learn.error.code,'E_LEARN');
assert.deepEqual(inspect(session),prior,'P03 never authorizes learning');
const cli=spawnSync(process.execPath,[path.join(root,'bbyq.mjs'),'--build',build,'turn',session,'cli-test','--module=p03','A es mayor que B. B es mayor que C. ¿A es mayor que C?'],
 {encoding:'utf8',timeout:30000,maxBuffer:1024*1024});
assert.equal(cli.status,0,cli.stderr);
assert.match(JSON.parse(cli.stdout).response,/a -> b -> c/);
const state=inspect(session);
assert.equal(state.state_sha256,initial.state_sha256,'X09/X10 memory not touched');
assert.equal(state.relational_state_sha256,initial.relational_state_sha256,'E034 sidecar not touched');
assert.equal(state.integrity,'ok');
const report={ok:true,test_scope:'real X10 NativePages and CLI on synthetic invalid X09 state',native_p03_compiled:true,
 automatic_mode:true,explicit_mode:true,replay:true,contradictions:true,no_false_negation:true,
 rollback:true,oversize_rejected:true,no_learning:true,original_state_preserved:true,related_e034_sidecar_preserved:true,
 android_validated:false,seeded_x09_model_tested:false,checks:16};
fs.writeFileSync(path.join(out,'results.json'),JSON.stringify(report,null,2)+'\n');
console.log(JSON.stringify(report));
