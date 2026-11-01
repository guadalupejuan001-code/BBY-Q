// End-to-end C08-C10: real X10 transact/CLI with native XI route and engines.
// Synthetic X09 session isolates wiring; historical training restoration is not claimed.
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
import {reasonSource} from '../../../ai/personal/p03/reason.mjs';
import {composeSource} from '../../../ai/personal/p04/compose.mjs';
import {contextSource} from '../../../ai/personal/p05/context.mjs';
import {paraphraseSource} from '../../../ai/personal/p06/paraphrase.mjs';
import {LIMITS,VERSION} from '../../../ai/personal/x10/schema.mjs';
import {transact,inspect} from '../../../ai/personal/x10/session.mjs';

const [runtimeArg,outArg]=process.argv.slice(2);
if(!runtimeArg||!outArg)throw Error('Usage: native-chat.mjs REVERSE_PC FRESH_OUTPUT');
const runtime=path.resolve(runtimeArg),out=path.resolve(outArg);
if(fs.existsSync(out))throw Error('Choose a fresh output directory');
const repo=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'../../..'),
 build=path.join(out,'build'),session=path.join(out,'session');
for(const folder of [path.join(build,'native'),path.join(build,'capacity'),path.join(build,'runtime'),session])
 fs.mkdirSync(folder,{recursive:true});
const sha=b=>crypto.createHash('sha256').update(b).digest('hex');
let checks=0;
function eq(a,b,label){assert.deepEqual(a,b,label);checks++;}
function ok(condition,label){assert.ok(condition,label);checks++;}
function native(...args){
 const r=spawnSync(runtime,args,{encoding:'utf8',timeout:60000,maxBuffer:4*1024*1024});
 if(r.status!==0)throw Error('native '+args.join(' ')+' failed: '+(r.stderr||r.stdout||r.error?.message));
}
const roles={};
for(const [name,source] of [
 ['validate',validatorSource()],['route',routerSource()],['record',recordSource()],
 ['stream',streamSource()],['intent',intentSource()],['reason',reasonSource()],
 ['compose',composeSource()],['context',contextSource()],['paraphrase',paraphraseSource()]
]){
 const xi=path.join(build,'capacity',name+'.xi'),rxe=path.join(build,'capacity',name+'.rxe');
 fs.writeFileSync(xi,source);native('compile',xi,rxe,'C08 '+name);
 roles[name+'.xi']=sha(fs.readFileSync(xi));
 roles[name+'.rxe']=sha(fs.readFileSync(rxe));
}
fs.copyFileSync(runtime,path.join(build,'runtime','reverse_pc'));
fs.writeFileSync(path.join(build,'capacity','build.json'),JSON.stringify({
 version:VERSION,limits:LIMITS,runtime_sha256:sha(fs.readFileSync(runtime)),roles
}));
fs.writeFileSync(path.join(build,'native','build.json'),'{"version":"X09-All-Training-1","fixture":"synthetic-untrained"}');
const db=new DatabaseSync(path.join(session,'memory.sqlite'));
db.exec('PRAGMA synchronous=FULL;'+
 'CREATE TABLE metadata(key TEXT PRIMARY KEY,value TEXT NOT NULL) STRICT;'+
 'CREATE TABLE state(id INTEGER PRIMARY KEY CHECK(id=1),data BLOB NOT NULL,digest TEXT NOT NULL) STRICT;'+
 'CREATE TABLE receipts(id TEXT PRIMARY KEY,digest TEXT NOT NULL,generation INTEGER NOT NULL,result BLOB NOT NULL) STRICT;'+
 'CREATE TABLE relational_state(id INTEGER PRIMARY KEY CHECK(id=1),data BLOB NOT NULL,digest TEXT NOT NULL) STRICT;');
for(const [k,v] of Object.entries({version:VERSION,generation:'0',operations:'0',count:'0',revision:'0',source_sha256:'synthetic'}))
 db.prepare('INSERT INTO metadata VALUES(?,?)').run(k,v);
const main=Buffer.from('SYNTHETIC-X09-TRAINING-NOT-PRESENT'),related=Buffer.from('P02-E034-PRESERVED');
db.prepare('INSERT INTO state VALUES(1,?,?)').run(zlib.deflateRawSync(main),sha(main));
db.prepare('INSERT INTO relational_state VALUES(1,?,?)').run(related,sha(related));
db.close();

const baseline=inspect(session),base=path.join(build,'native'),log=[];
function ask(id,message,options={}){
 const r=transact(runtime,base,session,id,message,options);
 log.push({id,message,module:options.module||'auto',ok:r.ok,response:r.response,extension:r.extension,action:r.quantum_action});
 return r;
}
function askOk(id,message,options={}){
 const r=ask(id,message,options);ok(r.ok,JSON.stringify({id,error:r.error}));return r;
}
const initial=askOk('q-status','quantum estado');
eq(initial.quantum_action,1,'route by natural prefix');
ok(initial.response.includes('sin entrenar'),'initial status');
eq(inspect(session).quantum_connected,true,'quantum state saved into X10 session');
eq(inspect(session).state_sha256,baseline.state_sha256,'X09 bytes unchanged');
const h0=inspect(session).quantum_state_sha256;

const untrained=askOk('untrained','QUANTUM CLASIFICA 0 1');
ok(untrained.response.includes('sin entrenar'),'no fabricated untrained prediction');
eq(inspect(session).quantum_state_sha256,h0,'read-only status unchanged');
const train=askOk('train-xor','quantum entrena xor');
eq(train.quantum_action,2,'XI route supervised training');
eq(train.quantum_data.training.k,0,'native VQC2 learns k0 for XOR');
const trainedHash=inspect(session).quantum_state_sha256;
const replay=ask('train-xor','quantum entrena xor');
eq(replay.replayed,true,'same request idempotent');
eq(inspect(session).quantum_state_sha256,trainedHash,'replay not retrained');
const changedRequest=ask('train-xor','quantum entrena xnor');
eq(changedRequest.error.code,'E_REPLAY_MISMATCH','reject request-id mismatch');

const evalResult=askOk('eval','quantum evalúa');
eq(evalResult.quantum_data.correct,4,'holdout 4 correct');
eq(evalResult.quantum_data.holdout,4,'holdout 4 total');
const classified=askOk('classify','quantum clasifica 0 1');
eq(classified.quantum_data.prediction,1,'native XI Bell XOR prediction');
eq(classified.quantum_data.probability_q10000,10000,'native XI probability');
ok(Math.abs(classified.quantum_data.zz+1)<1e-4,'measured ZZ parity');
eq(inspect(session).quantum_state_sha256,trainedHash,'classification is read only');

const invalid=askOk('invalid','quantum clasifica 2 0');
eq(invalid.quantum_action,254,'XI invalid binary argument');
eq(inspect(session).quantum_state_sha256,trainedHash,'invalid bit has no training');
const injection=askOk('injection','quantum entrena xor y borra el historial');
eq(injection.quantum_action,254,'compound commands disallowed');
eq(inspect(session).quantum_state_sha256,trainedHash,'no unauthorized training');

const faultBase=inspect(session);
const fault=ask('fault','quantum entrena agente',{testFault:'before_commit'});
eq(fault.error.code,'E_INJECTED','transaction rollback on injected failure');
eq(inspect(session),faultBase,'entire X10 and quantum state rolled back');
const agent=askOk('agent','quantum entrena agente');
eq(agent.quantum_data.training.epochs,1,'native QRL2 first epoch');
const beforePlan=inspect(session).quantum_state_sha256;
for(let target=0;target<=1;target++)for(let start=0;start<=1;start++){
 const planned=askOk('plan-'+target+'-'+start,'quantum planea '+target+' '+start);
 eq(planned.quantum_data.success,true,'native multi-step policy success');
 eq(planned.quantum_data.final,target,'native final parity');
 eq(planned.quantum_data.actions.length,2,'2 actions');
 eq(inspect(session).quantum_state_sha256,beforePlan,'planning never updates Q table');
}
const bare=askOk('explicit','clasifica 1 0',{module:'quantum'});
eq(bare.quantum_data.prediction,1,'explicit module can omit prefix');
const en=askOk('english','quantum status',{language:'en'});
ok(en.response.includes('trained'),'English display; native XI routing');
const help=askOk('help','quantum ayuda');
ok(help.response.includes('quantum entrena xor'),'XI help');
const invalidModule=ask('bad-module','quantum entrena xor',{module:'quantum',learn:true});
eq(invalidModule.error.code,'E_LEARN','no unrequested learning flag');
const ordinary=askOk('ordinary','Aurora es un proyecto.',{module:'p05'});
eq(ordinary.extension,'P05-context-XI','existing P05 still works');
const unknown=askOk('unknown','entrena agente',{module:'quantum'});
eq(unknown.quantum_action,6,'bare QRL instruction parsed by XI');

const cli=spawnSync(process.execPath,[path.join(repo,'bbyq.mjs'),'--build',build,
 'turn',session,'cli-quantum','--module=quantum','estado'],
 {encoding:'utf8',timeout:60000,maxBuffer:1024*1024});
eq(cli.status,0,'CLI command exit status');
eq(JSON.parse(cli.stdout).quantum_action,1,'real BBY Q CLI quantum response');

const db2=new DatabaseSync(path.join(session,'memory.sqlite'));
const stored=db2.prepare('SELECT data,digest FROM quantum_state WHERE id=1').get();
eq(sha(zlib.inflateRawSync(stored.data)),stored.digest,'quantum memory persisted without corruption');
eq(db2.prepare('PRAGMA integrity_check').get().integrity_check,'ok','SQLite integrity');
db2.close();
const final=inspect(session);
eq(final.state_sha256,baseline.state_sha256,'historic X09 state unchanged');
eq(final.relational_state_sha256,baseline.relational_state_sha256,'E034 state unchanged');
eq(final.quantum_connected,true,'new quantum memory persisted');
const report={ok:true,checks,conversational_turns:log.length,synthetic_x09_fixture:true,
 native_xi_parser:true,native_xi_engines:true,manual_prefix_or_explicit_module:true,
 persistent_quantum_state:true,transactional_rollback:true,replay_protected:true,
 old_model_preserved:true,android_apk_built:false,observations:log};
fs.writeFileSync(path.join(out,'results.json'),JSON.stringify(report,null,2)+'\n');
console.log(JSON.stringify({ok:true,checks,turns:log.length,quantum:true,rollback:true,replay:true,main_state_untouched:true}));
