// Q03/Q04 acceptance: VQC and QRL EACH have a real 1000-qubit
// processor. The actual Born readout feeds native XI training, not a detached
// GHZ demonstration or the historical two-qubit proxy model.
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import {spawnSync} from 'node:child_process';
import {fileURLToPath} from 'node:url';
import {quantumCommand} from '../cli.mjs';

const [runtimeArg,outArg]=process.argv.slice(2);
if(!runtimeArg||!outArg)throw Error('Usage: agents1000-native.mjs ORIGINAL_REVERSE_PC FRESH_DIRECTORY');
const runtime=path.resolve(runtimeArg),out=path.resolve(outArg);
if(fs.existsSync(out))throw Error('Use an unused directory');
fs.mkdirSync(out,{recursive:true});
const repo=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'../../..');
const state=path.join(out,'agents'),legacy=path.join(out,'existing-2q');
const sha=file=>crypto.createHash('sha256').update(fs.readFileSync(file)).digest('hex');
const model=path.join(state,'memory.rvp');
let checks=0;
const eq=(a,b,msg)=>{assert.deepEqual(a,b,msg);checks++;};
const ok=(c,msg)=>{assert.ok(c,msg);checks++;};
const Q=(dir,command,...args)=>quantumCommand({root:repo,build:out,argv:[
 '--runtime='+runtime,'--state='+dir,command,...args.map(String)]});
const time=fn=>{const t=performance.now(),value=fn();return {result:value,ms:Math.round((performance.now()-t)*100)/100};};
const fresh=time(()=>Q(state,'init-agents-1000'));
eq(fresh.result.ok,true,'initialize authentic 1000-qubit VQC + 1000-qubit QRL');
eq(fresh.result.vqc1000_qubits,1000,'first agent truly occupies 1000 qubits');
eq(fresh.result.qrl1000_qubits,1000,'second agent truly occupies its own 1000 qubits');
eq(fresh.result.active_qubits,2000,'total 2000 actual active qubits in two components');
eq(fresh.result.largest_component,1000,'each GHZ component is width 1000');
ok(sha(model).length===64,'persistent RVPC2 saved');
const a0=Q(state,'agents-1000-audit');
eq(a0.state_unchanged,true,'audit leaves trained state unchanged');
eq(a0.vqc1000_updates,0,'new VQC starts without training');
eq(a0.qrl1000_updates,0,'new QRL starts without training');
const original=Q(state,'status');
eq(original.vqc2_trained,false,'old VQC2 remains a separate initial model');
eq(original.qrl2_trained,false,'old QRL2 remains independent');
eq(original.active_qubits,2000,'old models do not secretly account for new 2000-qubit register');
const measurements=[];
const before0=Q(state,'vqc1000-infer',0);
eq(before0.measured_action,0,'untrained VQC1000 quantum circuit predicts 0');
eq(before0.processor_qubits,1000,'prediction actually uses 1000-qubit VQC circuit');
eq(before0.input_dimensions,1000,'1000 input feature slots');
eq(before0.model_parameters,1000,'1000 trainable binary phase parameters');
eq(before0.entangling_gates_per_forward_pass,1998,'forward pass uncomputes and restores 999 controlled links');
eq(before0.state_unchanged,true,'Born readout did not overwrite weights');
for(const [index,label] of [[0,1],[17,0],[500,1],[999,1]]){
 const result=Q(state,'vqc1000-train',index,label);
 eq(result.processor_qubits,1000,'VQC1000 training used real 1000-qubit measured forward pass');
 eq(result.trained_parameter_index,index,'updated feature index is exact');
 eq(result.reward_from_xi,result.measured_action===label?100:0,'VQC reward computed in XI from measured action');
 const next=Q(state,'vqc1000-infer',index);
 eq(next.measured_action,label,'native XI learned 1000-qubit VQC feature '+index);
 eq(next.state_unchanged,true,'VQC1000 inference does not retrain');
 measurements.push({agent:'VQC1000',index,label,prior_action:result.measured_action,
  reward:result.reward_from_xi,updated_weight:result.new_weight,post_action:next.measured_action});
}
eq(Q(state,'agents-1000-status').vqc1000_updates,4,'four direct VQC parameter updates');
for(const [indices,expected] of [
 [[0,500],0],[[0,17,500],0],[[0,500,999],1],[[500,999],0],[[999],1]
]){
 const r=Q(state,'vqc1000-infer',...indices);
 eq(r.measured_action,expected,'coherent 1000-qubit parity generalization '+indices);
 eq(r.active_qubits,2000,'both large agents remain active during VQC inference');
}
const r0=Q(state,'qrl1000-act',1);
eq(r0.measured_action,0,'untrained QRL1000 selects action zero from its own 1000-qubit circuit');
eq(r0.processor_qubits,1000,'QRL policy action uses 1000 physical simulated qubits');
for(const [index,goal] of [[1,1],[54,0],[700,1],[999,1]]){
 const updated=Q(state,'qrl1000-train',index,goal);
 eq(updated.processor_qubits,1000,'QRL1000 reward update follows 1000-qubit Born action');
 eq(updated.reward_from_xi,updated.measured_action===goal?100:0,
  'QRL environment calculated reward in native XI');
 const observed=Q(state,'qrl1000-act',index);
 eq(observed.measured_action,goal,'QRL1000 changed policy from verified environment reward');
 eq(observed.state_unchanged,true,'QRL inference read-only');
 measurements.push({agent:'QRL1000',index,goal,old_action:updated.measured_action,
  reward:updated.reward_from_xi,new_action:observed.measured_action,weight:updated.new_weight});
}
eq(Q(state,'agents-1000-status').qrl1000_updates,4,'four explicit QRL environment-reward updates');
const replay=Q(state,'qrl1000-train',999,1);
eq(replay.reward_from_xi,100,'QRL positive reinforcement after correct policy');
eq(replay.measured_action,1,'QRL action actually measured, not inferred on the host');
eq(Q(state,'qrl1000-act',999).measured_action,1,'QRL correct action retained');
for(const [indices,expected] of [
 [[1,700],0],[[1,700,999],1],[[54,700],1],[[1,999],0]
]){
 const r=Q(state,'qrl1000-act',...indices);
 eq(r.measured_action,expected,'QRL1000 coherent action on previously unseen feature combination');
}
const verified=Q(state,'agents-1000-audit');
eq(verified.vqc1000_updates,4,'VQC training retained after QRL learning');
eq(verified.qrl1000_updates,5,'QRL distinct updates persisted');
eq(verified.active_qubits,2000,'two 1000-qubit agent components survive training');
eq(verified.state_unchanged,true,'two-agent audit does not train');

const stable=sha(model),outputs=[];
for(const role of [0,1]){
 const control=path.join(out,'ablation-'+role+'.xi');
 fs.writeFileSync(control,'#!reverse-pc-machine-v1\nstore8 8120000000000000001 '+role+'\nhalt\n');
 const configured=path.join(out,'ablation-'+role+'.rvp');
 const c=spawnSync(runtime,['run',control,model,configured],{encoding:'utf8',timeout:60000});
 eq(c.status,0,'scientific ablation frame');
 const detached=path.join(out,'ablation-'+role+'-out.rvp');
 const x=spawnSync(runtime,['run',path.join(repo,'ai/xi/qml_qrl/agents1000-ablate.xi'),configured,detached],
  {encoding:'utf8',timeout:180000,maxBuffer:8*1024*1024});
 eq(x.status,0,'1000-qubit last-spectator phase ablation executes');
 const events=x.stdout.trim().split('\n').filter(Boolean).map(z=>JSON.parse(z));
 const ps=events.find(e=>e.type==='probz')?.probability_one;
 const ez=events.find(e=>e.type==='expectation')?.value;
 eq(ps,1,'remote qubit #999 actually flips GHZ-measured policy outcome');
 eq(ez,-1,'global phase on remote qubit maps to negative measured Z');
 outputs.push({agent:role===0?'VQC1000':'QRL1000',remote_phase_flip_output:ps,
  expectation_z:ez,physical_remote_qubit:role===0?1099:2199});
}
eq(sha(model),stable,'scientific test never touched trained model');
let rejected=false;
try{Q(state,'qrl1000-act',1000);}catch(e){rejected=true;}
ok(rejected,'index outside 0..999 rejected');
eq(sha(model),stable,'invalid dimension cannot corrupt persistent QRL weights');
rejected=false;
try{Q(state,'enable-agents-1000');}catch(e){rejected=true;}
ok(rejected,'duplicate registration of two 1000-qubit agents is forbidden');
eq(sha(model),stable,'duplicate creation leaves trained weights unchanged');

// Compatibility: original VQC2 and QRL2 can still train AFTER the new 2*1000 agents.
const v2=Q(state,'train-xor'),rl2=Q(state,'train-agent');
eq(v2.k,0,'legacy VQC2 train unchanged');
eq(rl2.epochs,1,'legacy QRL2 training unchanged');
eq(Q(state,'classify',0,1).predicted,1,'old VQC2 inference remains correct');
eq(Q(state,'plan',1,0).success,true,'old QRL2 sequence remains correct');
eq(Q(state,'agents-1000-audit').vqc1000_updates,4,'VQC1000 survives 2q training');
eq(Q(state,'agents-1000-audit').qrl1000_updates,5,'QRL1000 survives 2q training');
ok(Q(state,'status').active_qubits>=2000,'both agent processors coexist with original 2q experiments');

// Upgrade an existing session that already has the old VQC2/QRL2 training and GHZ1000.
const prior=Q(legacy,'init-1000');
eq(prior.quantum1000.registered_qubits,1000,'older GHZ1000 fixture');
eq(Q(legacy,'train-xor').k,0,'legacy active training');
eq(Q(legacy,'train-agent').epochs,1,'legacy QRL learning');
const attached=Q(legacy,'enable-agents-1000');
eq(attached.vqc1000_qubits,1000,'upgraded VQC processor');
eq(attached.qrl1000_qubits,1000,'upgraded QRL processor');
eq(Q(legacy,'status').vqc2_trained,true,'preexisting old VQC2 training preserved');
eq(Q(legacy,'status').qrl2_epochs,1,'preexisting old QRL2 checkpoint preserved');
eq(Q(legacy,'agents-1000-audit').state_unchanged,true,'upgraded checkpoint audited');

const report={ok:true,cycle:'Q03-Q04-native-XI-1000-qubit-agents',
 checks,engine:'REVERSE-PC original XI/Mundo X',
 model:{
  vqc1000_qubits:1000,qrl1000_qubits:1000,distinct_entangled_components:2,
  initial_active_qubits:2000,feature_dimension:1000,
  learnable_phase_bits_per_agent:1000,forward_pass_cx_gates:1998,
  architecture:'two independent Clifford/GHZ phase-parity circuits',
  old_vqc2_qrl2_preserved:true
 },
 training:{
  vqc_supervised_samples:4,qrl_environment_reward_samples:5,
  rewards_calculated_in_xi:true,readout_from_real_born_probability:true,
  binary_phase_parameters_updated_in_xi:true,
  heldout_sparse_combinations:9,
  samples:measurements
 },
 ablation:{physical_remote_qubits_are_causally_active:true,results:outputs,
  no_saved_state_mutation:true},
 persistence:{created_in_existing_rvpc2:true,upgrade_original_checkpoint:true,
  saved_rvpc2_sha256:sha(model),bytes:fs.statSync(model).size},
 limitations:[
 'Clifford GHZ phase-parity processor, not arbitrary 1000-qubit universal variational gates.',
 'Supervised one-hot feature learning and reward-shaped one-step bandit for QRL; not sequential quantum RL3.',
 'These limited parity benchmark targets do not demonstrate an advantage over simple classical parity models.',
 'The XI interpreter does not branch directly on the Born measurement; the host transports its value back into XI.',
 '1000 binary trainable phase bits exist per agent, but only a few were updated in this pilot.'
 ],
 init_ms:fresh.ms,
 no_claim_of_quantum_hardware:true};
fs.writeFileSync(path.join(out,'results.json'),JSON.stringify(report,null,2)+'\n');
console.log(JSON.stringify({ok:true,checks,qubits_per_agent:1000,
 active_qubits_2_agents:2000,
 vqc_training:report.training.vqc_supervised_samples,
 qrl_rewards:report.training.qrl_environment_reward_samples,
 ablation_passed:true,old_engines_preserved:true,rvpc2_bytes:report.persistence.bytes}));
