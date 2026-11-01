#!/usr/bin/env node
// C11 integrity preflight. Provenance differs from validation against an actual
// owner's full X09/X10 release; report that distinction explicitly.
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import assert from 'node:assert/strict';
import {fileURLToPath} from 'node:url';
import {decodedBytes,parseState,sha256} from '../x09/tests/retention/state.mjs';
import {initialize,transact,inspect} from '../../ai/personal/x10/session.mjs';

const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'../..');
const args=process.argv.slice(2),at=args.indexOf('--x10-build');
const build=at>=0?args[at+1]:null;
if(at>=0&&(!build||args.length!==2))throw Error('Usage: node integration/c11/audit.mjs [--x10-build /path/to/verified/build]');
if(at<0&&args.length)throw Error('Unknown arguments');
const evidence={
 ok:false,cycle:'C11',repository:'BBY-Q',
 historical_checks:{},x09_release:{},real_x10:{status:'not_executed',reason:'verified owner X09 build not supplied'},
 notes:[]
};
const history=JSON.parse(fs.readFileSync(path.join(root,'integration/x09/tests/retention/historical-states.json')));
const versions=history.states.filter(x=>x.kind==='versioned_checkpoint');
let hashes=0,bytes=0;
for(const version of versions){
 const file=path.join(root,version.path.replace(/^checkpoints\//,''));
 const raw=decodedBytes(file);
 assert.equal(sha256(raw),version.state_sha256,'Historical snapshot changed: '+version.path);
 parseState(raw);hashes++;bytes+=raw.length;
}
const manifest=JSON.parse(fs.readFileSync(path.join(root,'ai/checkpoints/e022-manifest.json')));
const e022=path.join(root,'ai/checkpoints',manifest.file);
const checkpoint=decodedBytes(e022);
assert.equal(checkpoint.length,manifest.decoded_bytes,'E022 size mismatch');
assert.equal(sha256(checkpoint),manifest.decoded_sha256,'E022 checksum mismatch');
parseState(checkpoint);
evidence.historical_checks={ok:true,verified_versioned_states:hashes,
 checkpoint_decoded_bytes:bytes,e022_sha256:manifest.decoded_sha256,
 previous_constructs_reported:manifest.previous_constructions,
 original_language_training_replayed:false};
const release=JSON.parse(fs.readFileSync(path.join(root,'integration/x09/release/manifest.json')));
assert.equal(release.version,'X09-All-Training-1');
assert.match(release.model_sha256,/^[a-f0-9]{64}$/);
const releaseDir=path.join(root,'integration/x09/release');
evidence.x09_release={
 model_expected_sha256:release.model_sha256,
 restored_model_present:fs.existsSync(path.join(releaseDir,'native.tar.gz'))&&fs.existsSync(path.join(releaseDir,'reverse_pc.gz')),
 verification:'manifest_only_until_restored',
 estimated_lessons_from_prior_x10_validation:480
};
if(build){
 const directory=path.resolve(build),base=path.join(directory,'native');
 const runtime=path.join(directory,'runtime/reverse_pc');
 const temporary=fs.mkdtempSync(path.join(os.tmpdir(),'bbyq-c11-real-'));
 const session=path.join(temporary,'session');
 try{
  assert.ok(fs.existsSync(path.join(base,'model.rvp.gz')),'X09 build is not available');
  const source=fs.readFileSync(path.join(base,'model.rvp'));
  assert.equal(sha256(source),release.model_sha256,'Verified historical X09 model is not the expected release');
  const created=initialize(session,base);
  assert.equal(created.ok,true);
  assert.equal(created.lessons,480,'Original 480 X09 lesson records were not retained');
  const before=inspect(session);
  assert.equal(before.state_sha256,sha256(source));
  const ask=(id,message)=>{const result=transact(runtime,base,session,id,message);assert.equal(result.ok,true,JSON.stringify(result));return result;};
  const response=ask('c11-legacy','calcula 17 + 25');
  assert.match(response.response,/\b42\b/);
  const first=ask('c11-status','quantum estado');
  assert.equal(first.quantum_connected,true);
  const train=ask('c11-train','quantum entrena xor');
  assert.equal(train.quantum_data.training.k,0);
  const sampled=ask('c11-infer','quantum clasifica 0 1');
  assert.equal(sampled.quantum_data.prediction,1);
  const agent=ask('c11-agent','quantum entrena agente');
  assert.equal(agent.quantum_data.training.epochs,1);
  const planned=ask('c11-plan','quantum planea 1 0');
  assert.equal(planned.quantum_data.success,true);
  const after=inspect(session);
  assert.equal(after.state_sha256,before.state_sha256,'Historical X09 state changed during new engine use');
  assert.equal(after.lessons,before.lessons,'Historical lessons count changed');
  assert.equal(after.revision,before.revision,'Historical lesson revisions changed');
  assert.equal(after.integrity,'ok');
  evidence.real_x10={
   status:'passed',legacy_lessons:created.lessons,original_state_sha256:before.state_sha256,
   after_state_sha256:after.state_sha256,quantum_state_sha256:after.quantum_state_sha256,
   original_response:response.response,quantum_trained:true};
  evidence.x09_release.verification='restored_real_x10_passed';
 }finally{fs.rmSync(temporary,{recursive:true,force:true});}
}else evidence.notes.push('CI verifies repository checkpoints, not the complete X09 release: supply a verified X10 build to run owner-model acceptance.');
evidence.ok=true;
console.log(JSON.stringify(evidence,null,2));
