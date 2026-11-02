// Q01-Q02: run the original REVERSE-PC runtime on a real 1000-qubit GHZ
// stabilizer component, preserving existing VQC2 and QRL2 XI training.
// The policy still trains on two-qubit experiments; 1000-qubit VQC weights
// or arbitrary statevector simulation are deliberately NOT claimed.
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import {execFileSync,spawnSync} from 'node:child_process';
import {fileURLToPath} from 'node:url';
import {quantumCommand} from '../cli.mjs';

const [runtimeArg,outArg]=process.argv.slice(2);
if(!runtimeArg||!outArg)throw Error('Usage: qubits-1000.mjs ORIGINAL_REVERSE_PC NEW_OUTPUT_DIRECTORY');
const runtime=path.resolve(runtimeArg),out=path.resolve(outArg);
if(fs.existsSync(out))throw Error('An empty output directory is required.');
fs.mkdirSync(out,{recursive:true});
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'../../..');
const stateDir=path.join(out,'existing-agent');
const widthState=path.join(out,'fresh-1000');
const hash=file=>crypto.createHash('sha256').update(fs.readFileSync(file)).digest('hex');
let checks=0;
const eq=(a,b,message)=>{assert.deepEqual(a,b,message);checks++;};
const ok=(a,message)=>{assert.ok(a,message);checks++;};
function Q(state,cmd,...args){
 return quantumCommand({root,build:out,argv:['--runtime='+runtime,'--state='+state,cmd,...args.map(String)]});
}
function raw(program,input,output){
 const r=spawnSync(runtime,['run',program,input,output],
  {encoding:'utf8',timeout:120000,maxBuffer:8*1024*1024});
 return {status:r.status,text:r.stdout,stderr:r.stderr,
  events:r.status===0?r.stdout.trim().split('\n').filter(Boolean).map(line=>JSON.parse(line)):[]};
}
const time=fn=>{const start=performance.now(),result=fn();return {elapsed_ms:+(performance.now()-start).toFixed(2),result};};
const normal=Q(stateDir,'init');
ok(normal.ok,'old two-qubit initialization works');
const initial=Q(stateDir,'status');
eq(initial.vqc2_trained,false,'new VQC2 untrained');
eq(initial.qrl2_trained,false,'new QRL2 untrained');
const trainedVqc=Q(stateDir,'train-xor'),trainedQrl=Q(stateDir,'train-agent');
eq(trainedVqc.k,0,'VQC2 native XOR training');
eq(trainedQrl.epochs,1,'QRL2 native first epoch');
const trainedBefore=Q(stateDir,'status');
eq(trainedBefore.vqc2_k,0,'VQC2 checkpoint before expansion');
eq(trainedBefore.qrl2_epochs,1,'QRL2 checkpoint before expansion');
const memory=path.join(stateDir,'memory.rvp');
const originalSha=hash(memory);
ok(trainedBefore.active_qubits<=4,'old agent contains only the original bounded quantum register');
const enabled=time(()=>Q(stateDir,'enable-1000'));
eq(enabled.result.ok,true,'attach is successful');
eq(enabled.result.registered_qubits,1000,'GHZ has 1000 entangled qubits');
eq(enabled.result.largest_entangled_component,1000,'exactly one 1000-qubit GHZ component exists');
eq(enabled.result.zz_first_last,1,'first and last Z are perfectly correlated');
eq(enabled.result.zz_first_middle,1,'long-distance GHZ Z correlation');
eq(enabled.result.xx_pair,0,'GHZ end-to-end X-pair is not a Bell pair');
eq(enabled.result.p_one_first,.5,'first GHZ qubit in equal superposition');
eq(enabled.result.p_one_last,.5,'last GHZ qubit in equal superposition');
ok(enabled.result.core_max_active_qubits>=1000,'core genuinely admits >=1000 qubits');
ok(enabled.result.core_max_component_qubits>=1000,'core component width sufficient');
ok(enabled.result.state_sha256!==originalSha,'1000 real-qubit register was committed');
const post=Q(stateDir,'status');
eq(post.vqc2_trained,true,'VQC2 remains trained after GHZ initialization');
eq(post.vqc2_k,trainedBefore.vqc2_k,'VQC2 weight preserved');
eq(post.qrl2_trained,true,'QRL2 remains trained after GHZ initialization');
eq(post.qrl2_epochs,trainedBefore.qrl2_epochs,'QRL2 learned checkpoint preserved');
eq(post.largest_entangled_component,1000,'persisted GHZ width');
const sealedHash=hash(memory);
const audit=time(()=>Q(stateDir,'audit-1000'));
eq(audit.result.state_unchanged,true,'1000-qubit audit is read-only');
eq(audit.result.state_sha256,sealedHash,'exact RVPC2 sha after audit');
const prediction=Q(stateDir,'classify',0,1);
eq(prediction.predicted,1,'original Bell VQC2 inference coexists with 1000-qubit component');
eq(prediction.state_unchanged,true,'VQC2 inference retains entire 1000-qubit state');
const plan=Q(stateDir,'plan',1,0);
eq(plan.success,true,'QRL2 planning still succeeds');
eq(plan.state_unchanged,true,'QRL2 inference retains entire 1000-qubit state');
eq(hash(memory),sealedHash,'all working engine queries leave GHZ1000 untouched');
const aud2=Q(stateDir,'audit-1000');
eq(aud2.largest_entangled_component,1000,'GHZ1000 survives Bell inference and multi-step QRL planning');
const trainedAgain=Q(stateDir,'train-agent');
eq(trainedAgain.epochs,2,'QRL2 training continues without reset');
eq(Q(stateDir,'status').vqc2_k,0,'VQC2 original learning preserved after additional QRL training');
eq(Q(stateDir,'audit-1000').largest_entangled_component,1000,'QRL2 reward updates preserve GHZ');

const scratch=path.join(out,'inversed.rvp'),saved=hash(memory);
const inverted=raw(path.join(root,'ai/xi/qml_qrl/q1000-uncompute.xi'),memory,scratch);
eq(inverted.status,0,'full GHZ reversible uncomputation in original XI');
const probabilities=inverted.events.filter(x=>x.type==='probz').map(x=>x.probability_one);
eq(probabilities,[0,0,0],'all probed qubits return to |0> after reversing 999 CX');
eq(hash(memory),saved,'uncompute on scratch does not rewrite shared agent state');
const bad=path.join(out,'damaged-copy.rvp');
const badCreate=raw(path.join(root,'ai/xi/qml_qrl/q1000-bad-marker.xi'),memory,bad);
eq(badCreate.status,0,'synthetic marker corruption on separate scratch state');
const rejected=raw(path.join(root,'ai/xi/qml_qrl/q1000-audit.xi'),bad,path.join(out,'should-not-exist.rvp'));
ok(rejected.status!==0,'native XI rejects corrupt GHZ marker');
ok(!fs.existsSync(path.join(out,'should-not-exist.rvp')),'failed XI audit creates no output state');
eq(hash(memory),saved,'rejection never changes original trained model');
let duplicate=false;
try{Q(stateDir,'enable-1000');}catch{duplicate=true;}
ok(duplicate,'cannot mount a second 1000-qubit register on the same memory');
eq(hash(memory),saved,'duplicate request does not corrupt learned checkpoint');

const fresh=time(()=>Q(widthState,'init-1000'));
eq(fresh.result.ok,true,'new optional fresh 1000-qubit initialization');
eq(fresh.result.quantum1000.registered_qubits,1000,'fresh model receives 1000 actual GHZ qubits');
const freshStatus=Q(widthState,'status');
eq(freshStatus.vqc2_trained,false,'fresh VQC2 remains independent and untrained');
eq(freshStatus.qrl2_trained,false,'fresh QRL2 remains independent and untrained');
eq(freshStatus.active_qubits,1000,'new untouched GHZ contains exactly 1000 simulated qubits');
eq(freshStatus.largest_entangled_component,1000,'all 1000 new qubits are entangled');
const freshSha=hash(path.join(widthState,'memory.rvp'));
eq(Q(widthState,'audit-1000').state_unchanged,true,'fresh GHZ audit is non-mutating');
eq(hash(path.join(widthState,'memory.rvp')),freshSha,'fresh 1000-qubit checkpoint can roundtrip');

const report={ok:true,cycle:'Q01-Q02',checks,engine:'original REVERSE-PC native XI + Mundo X Ether',
 configuration:{ghz_component_qubits:1000,ghz_addresses:'100..1099',
  original_vqc2_qubits:'2,3',original_qrl2_qubits:'4,5',
  qubits_after_working_inference:Q(stateDir,'status').active_qubits,
  max_active_qubits:enabled.result.core_max_active_qubits,
  max_component_qubits:enabled.result.core_max_component_qubits,
  two_qubit_variational_training_expanded_to_1000:false},
 measured:{initial_vqc2_k:trainedBefore.vqc2_k,qrl2_rounds_before:trainedBefore.qrl2_epochs,
  qrl2_rounds_after:trainedAgain.epochs,
  ghz_enable_elapsed_ms:enabled.elapsed_ms,ghz_audit_elapsed_ms:audit.elapsed_ms,
  ghz_fresh_init_elapsed_ms:fresh.elapsed_ms,
  ghz_zz_endpoints:enabled.result.zz_first_last,
  ghz_zz_middle:enabled.result.zz_first_middle,
  ghz_xx_endpoints:enabled.result.xx_pair,
  p_one_first:enabled.result.p_one_first,
  p_one_last:enabled.result.p_one_last,
  core_state_bytes:fs.statSync(memory).size},
 reversible_clifford:true,rollback_tested:true,training_preserved:true,
 interpreted_1000_qubits:'A 1000-qubit Clifford/stabilizer GHZ register plus local 2-qubit VQC/QRL experiments, not a general 1000-qubit VQC/QRL policy.',
 claims_not_made:['arbitrary 2^1000 statevector','1000 trained variational quantum parameters','quantum speedup','1000-qubit quantum hardware']};
fs.writeFileSync(path.join(out,'results.json'),JSON.stringify(report,null,2)+'\n');
console.log(JSON.stringify({ok:true,checks,component_qubits:1000,
 full_ghz_long_range_correlation:true,trained_vqc_and_qrl_compatible:true,
 qrl_continued_training:true,rollback:true,initialization_ms:enabled.elapsed_ms,
 report:path.join(out,'results.json')}));
