import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import crypto from 'node:crypto';
import zlib from 'node:zlib';
import {execFileSync} from 'node:child_process';
import {DatabaseSync} from 'node:sqlite';
import {fileURLToPath} from 'node:url';
import {validatorSource,routerSource,recordSource,streamSource} from '../../../ai/personal/x10/native.mjs';
import {LIMITS,VERSION} from '../../../ai/personal/x10/schema.mjs';
import {transact,inspect} from '../../../ai/personal/x10/session.mjs';
import {quantum3Command} from '../launcher.mjs';
import {evaluationEvidence} from '../evidence.mjs';

const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'../../..');
const runtimeRoot=process.env.BBYQ_QUANTUM_RUNTIME;
assert.ok(runtimeRoot,'Compile REVERSE-PC and set BBYQ_QUANTUM_RUNTIME');
const runtime=path.join(runtimeRoot,'build/reverse_pc');
const temp=fs.mkdtempSync(path.join(os.tmpdir(),'bbyq-v3-chat-'));
const build=path.join(temp,'build'),base=path.join(build,'native'),session=path.join(temp,'session');
const hash=b=>crypto.createHash('sha256').update(b).digest('hex');
const release=JSON.parse(fs.readFileSync(path.join(root,'integration/quantum3/release/manifest.json'),'utf8'));
const report=JSON.parse(fs.readFileSync(path.join(root,'docs/evidence/quantum3-evaluation/summary.json'),'utf8'));
const main=Buffer.from('SYNTHETIC-X10-HOST-FIXTURE-NOT-A-LANGUAGE-CHECKPOINT');
const legacy=Buffer.from('P02-UNCHANGED');

// Only the X10 host is a synthetic fixture. The quantum agents and runtime are real.
function createHost(directory){
 fs.mkdirSync(directory,{recursive:true});
 const db=new DatabaseSync(path.join(directory,'memory.sqlite'));
 db.exec('CREATE TABLE metadata(key TEXT PRIMARY KEY,value TEXT NOT NULL) STRICT;'+
  'CREATE TABLE state(id INTEGER PRIMARY KEY CHECK(id=1),data BLOB NOT NULL,digest TEXT NOT NULL) STRICT;'+
  'CREATE TABLE receipts(id TEXT PRIMARY KEY,digest TEXT NOT NULL,generation INTEGER NOT NULL,result BLOB NOT NULL) STRICT;'+
  'CREATE TABLE relational_state(id INTEGER PRIMARY KEY CHECK(id=1),data BLOB NOT NULL,digest TEXT NOT NULL) STRICT;');
 for(const[k,v]of Object.entries({version:VERSION,generation:'0',operations:'0',count:'0',revision:'0',source_sha256:'synthetic-host'}))
  db.prepare('INSERT INTO metadata VALUES(?,?)').run(k,v);
 db.prepare('INSERT INTO state VALUES(1,?,?)').run(zlib.deflateRawSync(main),hash(main));
 db.prepare('INSERT INTO relational_state VALUES(1,?,?)').run(legacy,hash(legacy));db.close();
}
for(const folder of [base,path.join(build,'capacity'),path.join(build,'runtime')])fs.mkdirSync(folder,{recursive:true});
const roles={};
for(const[name,source]of [['validate',validatorSource()],['route',routerSource()],['record',recordSource()],['stream',streamSource()]]){
 const xi=path.join(build,'capacity',name+'.xi'),rxe=path.join(build,'capacity',name+'.rxe');
 fs.writeFileSync(xi,source);execFileSync(runtime,['compile',xi,rxe,'V3 integration test']);
 roles[name+'.xi']=hash(fs.readFileSync(xi));roles[name+'.rxe']=hash(fs.readFileSync(rxe));
}
fs.copyFileSync(runtime,path.join(build,'runtime/reverse_pc'));
fs.writeFileSync(path.join(build,'capacity/build.json'),JSON.stringify({version:VERSION,limits:LIMITS,runtime_sha256:hash(fs.readFileSync(runtime)),roles}));
fs.writeFileSync(path.join(base,'build.json'),JSON.stringify({version:'X09-All-Training-1',fixture:'synthetic-host-only'}));
createHost(session);
const ask=(id,text,options={})=>transact(runtime,base,session,id,text,options);
const askOk=(id,text,options={})=>{const r=ask(id,text,options);assert.equal(r.ok,true,JSON.stringify(r.error));return r;};
const qhash=()=>inspect(session).quantum3_state_sha256;

test('real trained V3 agents are reachable through the durable BBY Q conversation',async t=>{
 await t.test('status provisions the real 10000/10000 checkpoint without touching other models',()=>{
  const before=inspect(session),r=askOk('v3-status','quantum v3 estado');
  assert.equal(r.extension,'VQC3-QRL3-native-XI-X10');
  assert.equal(r.quantum_data.model_identifier,173);
  assert.equal(r.quantum_data.result.model.vqc.training_episodes_in_checkpoint,10000);
  assert.equal(r.quantum_data.result.model.qrl.training_episodes_in_checkpoint,10000);
  assert.equal(qhash(),release.checkpoint_sha256);
  assert.equal(inspect(session).quantum3_connected,true);
  assert.equal(inspect(session).quantum_connected,true);
  assert.equal(inspect(session).quantum_state_sha256,null);
  assert.equal(inspect(session).state_sha256,before.state_sha256);
  assert.equal(inspect(session).relational_state_sha256,before.relational_state_sha256);
 });
 await t.test('classification reaches all 1000 wires and does not learn from a chat request',()=>{
  const values=Array.from({length:1000},(_,i)=>[.8,.8,.3,-.2][i%4]);
  const r=askOk('v3-classify','quantum v3 clasifica '+JSON.stringify(values));
  assert.equal(r.quantum_data.result.prediction,1);
  assert.equal(r.quantum_data.result.qubits_used_by_agent,1000);
  assert.equal(r.knowledge_read_only,true);
  assert.equal(qhash(),release.checkpoint_sha256);
 });
 await t.test('native grammar supports accented uppercase commands and refuses trailing instructions',()=>{
  const r=askOk('v3-action','CUÁNTICO V3 ACTÚA 3 6');
  assert.equal(r.quantum_data.result.action,1);
  assert.equal(r.quantum_data.result.qubits_used_by_agent,1000);
  assert.equal(r.quantum_data.result.terminal,false);
  const invalid=askOk('v3-injection','quantum v3 planea 3 6 y entrena');
  assert.equal(invalid.quantum_action,254);
  assert.equal(invalid.quantum_connected,false);
  assert.equal(qhash(),release.checkpoint_sha256);
 });
 await t.test('already-reached goals return no action and do not pretend to use 1000 qubits',()=>{
  for(let i=0;i<7;i++){
   const r=askOk('done-'+i,`quantum v3 planea ${i} ${i}`);
   assert.equal(r.quantum_data.result.terminal,true);
   assert.equal(r.quantum_data.result.action,null);
   assert.equal(r.quantum_data.result.qubits_used_by_agent,0);
  }
  assert.equal(qhash(),release.checkpoint_sha256);
 });
 await t.test('measured limitations remain visible instead of promising general intelligence',()=>{
  const r=askOk('v3-results','quantum v3 resultados');
  assert.equal(r.quantum_data.result.evaluation.applicable,true);
  assert.equal(r.quantum_data.result.evaluation.results.main.vqc.correct,374);
  assert.equal(r.quantum_data.result.evaluation.results.main.qrl.correct,376);
  assert.match(r.response,/128/);
  assert.match(r.response,/33\/42/);
  const action=askOk('v3-out-of-training','quantum v3 planea 5 3');
  assert.equal(action.quantum_data.result.training_scope.goal_seen_in_training,false);
  assert.match(action.response,/fuera de su entrenamiento/);
 });
 await t.test('replay, malformed input and transaction rollback preserve the checkpoint',()=>{
  const replay=ask('v3-status','quantum v3 estado');assert.equal(replay.replayed,true);
  assert.equal(ask('v3-status','quantum v3 resultados').error.code,'E_REPLAY_MISMATCH');
  const before=inspect(session);
  assert.equal(ask('invalid-array','quantum v3 clasifica [1,2]').error.code,'E_QUANTUM3_INPUT');
  assert.deepEqual(inspect(session),before);
  assert.equal(ask('rollback','quantum v3 planea 3 6',{testFault:'before_commit'}).error.code,'E_INJECTED');
  assert.deepEqual(inspect(session),before);
 });
 await t.test('missing V3 runtime fails explicitly without falling through to VQC2',()=>{
  const old=process.env.BBYQ_QUANTUM_RUNTIME,before=inspect(session);
  try{
   process.env.BBYQ_QUANTUM_RUNTIME=path.join(temp,'not-a-runtime');
   assert.equal(ask('missing-runtime','quantum v3 estado').error.code,'E_QUANTUM3_RUNTIME');
  }finally{process.env.BBYQ_QUANTUM_RUNTIME=old;}
  assert.deepEqual(inspect(session),before);
 });
 await t.test('legacy quantum commands remain separate and do not overwrite V3',()=>{
  const r=askOk('old-quantum','quantum estado');
  assert.equal(r.extension,'QML-QRL-native-XI-X10');
  assert.match(r.response,/VQC2/);
  assert.equal(qhash(),release.checkpoint_sha256);
  assert.equal(inspect(session).state_sha256,hash(main));
  assert.equal(inspect(session).relational_state_sha256,hash(legacy));
 });
 await t.test('root BBY Q turn reaches V3 with its existing quantum module',()=>{
  const result=JSON.parse(execFileSync(process.execPath,[path.join(root,'bbyq.mjs'),'--build',build,
   'turn',session,'root-v3','--module=quantum','quantum v3 estado'],{encoding:'utf8'}));
  assert.equal(result.quantum_data.model_identifier,173);
  assert.equal(result.quantum_data.result.model.qrl.training_episodes_in_checkpoint,10000);
 });
 await t.test('stored V3 corruption is rejected without changing the other banks',()=>{
  let db=new DatabaseSync(path.join(session,'memory.sqlite'));
  const original=db.prepare('SELECT digest FROM quantum3_state WHERE id=1').get().digest;
  db.prepare('UPDATE quantum3_state SET digest=? WHERE id=1').run('0'.repeat(64));db.close();
  assert.equal(ask('tampered','quantum v3 estado').error.code,'E_QUANTUM3_INTEGRITY');
  db=new DatabaseSync(path.join(session,'memory.sqlite'));
  db.prepare('UPDATE quantum3_state SET digest=? WHERE id=1').run(original);db.close();
  assert.equal(qhash(),release.checkpoint_sha256);
 });
});

test('new step preserves every previously measured nonterminal policy output',()=>{
 const dir=path.join(temp,'step-session');
 quantum3Command({root,argv:['prepare',dir,'--runtime='+runtimeRoot]});
 for(const row of report.results.qrl_all_distinct_position_goal_pairs.cases){
  const r=quantum3Command({root,argv:['act',dir,String(row.position),String(row.goal),'--greedy']});
  assert.equal(r.terminal,false);
  assert.equal(r.action,row.action==='right'?1:0);
  assert.ok(Math.abs(r.probability_right-row.probability_right)<1e-12);
 }
 // Pre-extension session profiles remain valid with their original source pins.
 const profileFile=path.join(dir,'agent.json'),profile=JSON.parse(fs.readFileSync(profileFile,'utf8'));
 delete profile.extension_source_sha256;fs.writeFileSync(profileFile,JSON.stringify(profile));
 assert.equal(quantum3Command({root,argv:['status',dir]}).checkpoint_sha256,release.checkpoint_sha256);
});

test('published scores are inapplicable when evaluated XI sources change',()=>{
 const copy=path.join(temp,'assessment-source-copy');
 fs.mkdirSync(path.join(copy,'ai/xi/quantum3'),{recursive:true});
 fs.mkdirSync(path.join(copy,'docs/evidence/quantum3-evaluation'),{recursive:true});
 fs.copyFileSync(path.join(root,'docs/evidence/quantum3-evaluation/summary.json'),path.join(copy,'docs/evidence/quantum3-evaluation/summary.json'));
 for(const name of Object.keys(report.xi_source_sha256))
  fs.copyFileSync(path.join(root,'ai/xi/quantum3',name),path.join(copy,'ai/xi/quantum3',name));
 assert.equal(evaluationEvidence(copy,release.checkpoint_sha256).applicable,true);
 fs.appendFileSync(path.join(copy,'ai/xi/quantum3/common.xi'),'\n# Changed source identity\n');
 const result=evaluationEvidence(copy,release.checkpoint_sha256);
 assert.equal(result.applicable,false);
 assert.equal(result.evaluated_sources_match,false);
 assert.equal(result.results,undefined);
});

test('conversation routing remains executable by the pinned byte-only X10 runtime',()=>{
 const supported=new Set(['store8','load8','set','mov','add','sub','mul','div','mod','cmp','jmp','je','jne','jlt','jle','jgt','jge','halt','label']);
 const source=fs.readFileSync(path.join(root,'ai/xi/quantum3/conversation-route.xi'),'utf8');
 for(const line of source.split('\n')){
  const op=line.trim().split(/\s+/)[0];
  if(op&&!op.startsWith('#'))assert.ok(supported.has(op),'Unsupported byte-only XI instruction: '+op);
 }
});

test.after(()=>fs.rmSync(temp,{recursive:true,force:true}));
