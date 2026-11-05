import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import crypto from 'node:crypto';
import {fileURLToPath} from 'node:url';
import {execFileSync} from 'node:child_process';
import {quantum3Command} from '../launcher.mjs';
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'../../..');
const runtime=process.env.BBYQ_QUANTUM_RUNTIME;
assert.ok(runtime,'BBYQ_QUANTUM_RUNTIME must point to compiled REVERSE-PC');
const temp=fs.mkdtempSync(path.join(os.tmpdir(),'bbyq-v3-integration-'));
const session=path.join(temp,'session'),input=path.join(temp,'input.json');
fs.writeFileSync(input,JSON.stringify(Array.from({length:1000},(_,i)=>[1.6,.8,1.1,1.4][i%4])));
const call=(...argv)=>quantum3Command({root,argv});
const hash=p=>crypto.createHash('sha256').update(fs.readFileSync(p)).digest('hex');
const head=()=>JSON.parse(fs.readFileSync(path.join(session,'HEAD.json'),'utf8'));
const manifest=JSON.parse(fs.readFileSync(path.join(root,'integration/quantum3/release/manifest.json'),'utf8'));
let first;
test('integrates the existing trained native agents without resetting their learning',async t=>{
 await t.test('prepare validates the released checkpoint and preserves both 10000-episode agents',()=>{
  first=call('prepare',session,'--runtime='+runtime);
  assert.equal(first.model.qubits_per_agent,1000);
  assert.equal(first.model.model_identifier,173);
  assert.equal(first.model.vqc.training_episodes_in_checkpoint,10000);
  assert.equal(first.model.qrl.training_episodes_in_checkpoint,10000);
  assert.equal(first.checkpoint_sha256,manifest.checkpoint_sha256);
  assert.equal(first.model.vqc.rotation_parameters_changed,1000);
  assert.equal(first.model.qrl.rotation_parameters_changed,1000);
  assert.throws(()=>call('prepare',session,'--runtime='+runtime),/new session directory/);
 });
 await t.test('canonical quantum command reaches V3 instead of the historical two-qubit path',async()=>{
  const {quantumCommand}=await import('../../qml_qrl/cli.mjs');
  const status=quantumCommand({root,build:path.join(temp,'no-x10-build'),argv:['v3','status',session]});
  assert.equal(status.model.vqc.training_episodes_in_checkpoint,10000);
  assert.equal(status.model.model_identifier,173);
  assert.equal(status.checkpoint_sha256,first.checkpoint_sha256);
 });
 await t.test('real classification and policy actions use 1000 observed qubits without changing the checkpoint',()=>{
  const before=hash(path.join(session,'HEAD.json'));
  const vqc=call('classify',session,input);
  assert.equal(vqc.qubits_used_by_agent,1000);
  assert.equal(vqc.trace.distinct_rotated_qubits,1000);
  assert.equal(vqc.trace.max_prepared_block,4);
  const qrl=call('act',session,'3','6','--greedy');
  assert.equal(qrl.qubits_used_by_agent,1000);
  assert.equal(qrl.trace.max_prepared_block,4);
  assert.equal(hash(path.join(session,'HEAD.json')),before);
 });
 await t.test('continues the existing supervised learning and handles duplicate requests exactly once',()=>{
  const before=head(),parent=path.join(session,before.file);
  const update=call('learn-class',session,'class-001',input,'1');
  assert.equal(update.revision,1);assert.equal(update.replayed,false);
  assert.equal(update.parent_checkpoint_sha256,before.sha256);
  assert.notEqual(update.checkpoint_sha256,before.sha256);
  assert.equal(hash(parent),before.sha256);
  const again=call('learn-class',session,'class-001',input,'1');
  assert.equal(again.replayed,true);assert.equal(head().revision,1);
  assert.equal(again.checkpoint_sha256,update.checkpoint_sha256);
  assert.throws(()=>call('learn-class',session,'class-001',input,'0'),/different input/);
  assert.equal(call('status',session).model.vqc.training_episodes_in_checkpoint,10001);
  assert.equal(call('status',session).evaluation.applicable,false);
  assert.equal(call('results',session).evaluation.applicable,false);
 });
 await t.test('invalid training and writer conflicts leave the published model intact',()=>{
  const before=hash(path.join(session,'HEAD.json')),bad=path.join(temp,'bad.json');
  fs.writeFileSync(bad,'[1,2]');
  assert.throws(()=>call('learn-class',session,'bad',bad,'0'));
  assert.equal(hash(path.join(session,'HEAD.json')),before);
  fs.writeFileSync(path.join(session,'.write-lock'),'test');
  assert.throws(()=>call('learn-class',session,'busy',input,'0'),e=>e.code==='E_BUSY');
  fs.unlinkSync(path.join(session,'.write-lock'));
  assert.equal(hash(path.join(session,'HEAD.json')),before);
  assert.equal(fs.readdirSync(session).some(x=>x.startsWith('.input-')),false);
 });
 await t.test('sequential reinforcement learning continues QRL and preserves the initial model',()=>{
  const before=head();
  const update=call('learn-episode',session,'rl-001','--slip=0.15','--horizon=12');
  assert.equal(update.revision,2);
  assert.equal(update.qubits_used_by_agent,1000);
  assert.equal(hash(path.join(session,before.file)),before.sha256);
  const status=call('status',session);
  assert.equal(status.model.vqc.training_episodes_in_checkpoint,10001);
  assert.equal(status.model.qrl.training_episodes_in_checkpoint,10001);
  assert.equal(call('learn-episode',session,'rl-001').replayed,true);
  assert.equal(head().revision,2);
 });
 await t.test('request IDs that are JavaScript property names remain legitimate isolated receipts',()=>{
  const update=call('learn-class',session,'__proto__',input,'1');
  assert.equal(update.replayed,false);assert.equal(head().revision,3);
  assert.equal(call('learn-class',session,'__proto__',input,'1').replayed,true);
  assert.equal(head().revision,3);
 });
 await t.test('exports a reusable unchanged RVPC2 checkpoint and refuses overwrite',()=>{
  const destination=path.join(temp,'export.rvp'),result=call('export',session,destination);
  assert.equal(hash(destination),head().sha256);
  assert.equal(result.sha256,head().sha256);
  assert.throws(()=>call('export',session,destination),e=>e.code==='EEXIST');
 });
 if(process.env.BBYQ_TEST_CANONICAL_CLI==='1')await t.test('root BBY Q launcher exposes the trained agents',()=>{
  const result=JSON.parse(execFileSync(process.execPath,[path.join(root,'bbyq.mjs'),'quantum','v3','status',session],{encoding:'utf8'}));
  assert.equal(result.ok,true);assert.equal(result.model.qubits_per_agent,1000);
 });
 await t.test('runtime or published checkpoint tampering is rejected',()=>{
  const h=head(),state=path.join(session,h.file),bytes=fs.readFileSync(state);
  fs.appendFileSync(state,'x');
  assert.throws(()=>call('status',session),/hash mismatch/);
  fs.writeFileSync(state,bytes);
  const configFile=path.join(session,'agent.json'),original=fs.readFileSync(configFile),config=JSON.parse(original);
  config.session_sha256='0'.repeat(64);fs.writeFileSync(configFile,JSON.stringify(config));
  assert.throws(()=>call('status',session),/runtime changed/);
  fs.writeFileSync(configFile,original);
  assert.equal(call('status',session).revision,3);
 });
});
test.after(()=>fs.rmSync(temp,{recursive:true,force:true}));
