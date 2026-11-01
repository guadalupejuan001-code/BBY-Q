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
ok(untrained.response.includes('no está entrenado'),'no fabricated untrained prediction');
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

 // C12: the new policy never rewrites the legacy reply and only learns on explicit feedback.
 const beforePolicy=inspect(session),cognitiveRead=askOk('c12-read','Explícame la energía.',{module:'cognitive'});
 eq(cognitiveRead.extension,'C12-cognitive-policy-XI','opt-in cognitive route');
 eq(cognitiveRead.cognitive_shadow.feedback_updates,0,'new policy has no training');
 eq(cognitiveRead.cognitive_shadow.suggested_action,0,'zero Q selects safe legacy route');
 eq(cognitiveRead.cognitive_shadow.applied,false,'recommendation never applied to response');
 eq(inspect(session).state_sha256,beforePolicy.state_sha256,'X09 preserved at cognitive initialization');
 const policyHash=inspect(session).cognitive_policy_sha256;
 ok(typeof policyHash==='string'&&policyHash.length===64,'XI policy stored with sha256');
 const trained=askOk('c12-reward','Explícame la energía.',{module:'cognitive',policyFeedback:{action:2,reward:100}});
 eq(trained.cognitive_shadow.suggested_action,2,'XI policy learns explicit best action');
 eq(trained.cognitive_shadow.score_q10000,5000,'XI Q incremental update');
 eq(trained.cognitive_shadow.feedback_updates,1,'one explicit label');
 ok(inspect(session).cognitive_policy_sha256!==policyHash,'policy weights changed after feedback');
 const updatedPolicyHash=inspect(session).cognitive_policy_sha256;
 const replayReward=ask('c12-reward','Explícame la energía.',{module:'cognitive',policyFeedback:{action:2,reward:100}});
 eq(replayReward.replayed,true,'no duplicate policy training on replay');
 eq(inspect(session).cognitive_policy_sha256,updatedPolicyHash,'replay keeps policy weights');
 const mismatchReward=ask('c12-reward','Explícame la energía.',{module:'cognitive',policyFeedback:{action:3,reward:100}});
 eq(mismatchReward.error.code,'E_REPLAY_MISMATCH','different Q feedback rejects old request id');
 const repeated=askOk('c12-score','Explícame la energía.',{module:'cognitive'});
 eq(repeated.cognitive_shadow.suggested_action,2,'Q recommendation survives multiple transactions');
 eq(repeated.cognitive_shadow.read_only,true,'no feedback means no learning');
 eq(inspect(session).cognitive_policy_sha256,updatedPolicyHash,'Q score is read only');
 const snapshot=inspect(session);
 const faultPolicy=ask('c12-injected','Explícame la energía.',{module:'cognitive',policyFeedback:{action:3,reward:80},testFault:'before_commit'});
 eq(faultPolicy.error.code,'E_INJECTED','policy failure injected before atomic X10 commit');
 eq(inspect(session),snapshot,'Q feedback, model and receipt all rolled back');
 const invalidPolicy=ask('c12-invalid','Explícame la energía.',{module:'cognitive',policyFeedback:{action:5,reward:90}});
 eq(invalidPolicy.error.code,'E_COGNITIVE_FEEDBACK','rejects unknown feedback action');
 eq(inspect(session),snapshot,'invalid feedback never mutates anything');
 const oldReply=askOk('c12-old','Nebulosa es un tema.',{module:'p05'});
 const shadowReply=askOk('c12-shadow','Nebulosa es un tema.',{module:'p05',shadow:true});
 eq(shadowReply.response,oldReply.response,'opt-in shadow never substitutes a dialogue response');
 eq(shadowReply.cognitive_shadow.applied,false,'shadow observation only');
 eq(shadowReply.cognitive_shadow.feedback_updates,1,'shadow can see earlier explicit Q feedback');
 eq(inspect(session).cognitive_policy_sha256,updatedPolicyHash,'shadow did not change weights');
 const cliShadow=spawnSync(process.execPath,[path.join(repo,'bbyq.mjs'),'--build',build,'turn',
  session,'c12-cli','--module=cognitive','--shadow','Explícame la energía.'],{encoding:'utf8',timeout:60000,maxBuffer:1024*1024});
 eq(cliShadow.status,0,'cognitive CLI exit');
 eq(JSON.parse(cliShadow.stdout).cognitive_shadow.suggested_action,2,'CLI reads trained XI policy');
 const cliFeedback=spawnSync(process.execPath,[path.join(repo,'bbyq.mjs'),'--build',build,'turn',
  session,'c12-cli-feedback','--module=cognitive','--policy-feedback=2,80','Explícame la energía.'],
  {encoding:'utf8',timeout:60000,maxBuffer:1024*1024});
 eq(cliFeedback.status,0,'explicit feedback CLI exit');
 eq(JSON.parse(cliFeedback.stdout).cognitive_shadow.feedback_updates,2,'CLI forwards explicit feedback to XI');
 eq(inspect(session).state_sha256,baseline.state_sha256,'historic model still untouched after C12');
 const cognitiveFinal=inspect(session),cdb=new DatabaseSync(path.join(session,'memory.sqlite'));
 const policyRecord=cdb.prepare('SELECT data,digest FROM cognitive_policy WHERE id=1').get();
 eq(sha(zlib.inflateRawSync(policyRecord.data)),policyRecord.digest,'Q policy durable digest');
 cdb.close();
 ok(cognitiveFinal.cognitive_policy_sha256!==null,'policy persistence available');


 // C14: opt-in native XI supervised checkpoint recommends routes, never applies.
 const pre14=inspect(session);
 const classic14=askOk('c14-classic','Escribe un poema sobre un faro.',{module:'p05'});
 const shadow14=askOk('c14-shadow','Escribe un poema sobre un faro.',{module:'p05',shadowC14:true});
 eq(shadow14.response,classic14.response,'C14 shadow leaves exact X10/P05 text unchanged');
 eq(shadow14.c14_shadow.available,true,'synthetic XI seed available');
 eq(shadow14.c14_shadow.applied,false,'native XI route not applied');
 eq(shadow14.c14_shadow.suggested_action,3,'native XI recommends P04 for poem');
 eq(shadow14.c14_shadow.abstained,false,'trained creative route has enough evidence');
 eq(shadow14.c14_shadow.trained_examples,800,'pinned supervised seed restored');
 eq(inspect(session).state_sha256,pre14.state_sha256,'C14 never changes X09 main memory');
 eq(inspect(session).cognitive_policy_sha256,pre14.cognitive_policy_sha256,'C14 never changes previous C12 weights');
 const safe14=askOk('c14-safe','Recuerda que mañana revisaré Aurora.',{module:'p05',shadowC14:true});
 eq(safe14.c14_shadow.available,true,'guard can be inspected');
 eq(safe14.c14_shadow.abstained,true,'native C14 abstains on explicit teaching');
 eq(safe14.c14_shadow.suggested_action,0,'guarded route falls back to X10');
 const recall14=askOk('c14-recall','¿Qué dije sobre Aurora?',{module:'p05',shadowC14:true});
 eq(recall14.c14_shadow.applied,false,'P05 response still owns actual recall');
 const replay14=ask('c14-shadow','Escribe un poema sobre un faro.',{module:'p05',shadowC14:true});
 eq(replay14.replayed,true,'C14 replay returns receipt without rebuilding the model');
 const clash14=ask('c14-shadow','Escribe un poema sobre un faro.',{module:'p05'});
 eq(clash14.error.code,'E_REPLAY_MISMATCH','opt-in flag must change X10 replay digest');
 const long14=askOk('c14-long','Orion'.repeat(50),{module:'p05',shadowC14:true});
 eq(long14.c14_shadow.available,false,'out-of-scope >190 byte input does not block X10 response');
 eq(inspect(session).cognitive_policy_sha256,pre14.cognitive_policy_sha256,'C12 training remains intact after C14');
 const c14CLI=spawnSync(process.execPath,[path.join(repo,'bbyq.mjs'),'--build',build,
  'turn',session,'c14-cli','--module=p05','--shadow-c14','Escribe un poema sobre un faro.'],
  {encoding:'utf8',timeout:60000,maxBuffer:1024*1024});
 eq(c14CLI.status,0,'C14 CLI exit');
 eq(JSON.parse(c14CLI.stdout).c14_shadow.suggested_action,3,'C14 CLI XI recommendation');

const report={ok:true,checks,conversational_turns:log.length,synthetic_x09_fixture:true,
 native_xi_parser:true,native_xi_engines:true,manual_prefix_or_explicit_module:true,
 persistent_quantum_state:true,transactional_rollback:true,replay_protected:true,
 old_model_preserved:true,android_apk_built:false,observations:log};
fs.writeFileSync(path.join(out,'results.json'),JSON.stringify(report,null,2)+'\n');
console.log(JSON.stringify({ok:true,checks,turns:log.length,quantum:true,rollback:true,replay:true,main_state_untouched:true}));
