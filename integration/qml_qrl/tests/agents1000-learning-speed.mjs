// Q05 learning-speed experiment: both existing 1000-qubit XI agents, not an
// external GHZ spectator and not C12-C15 language routing.
// Runs native XI quantum Born readout -> XI reward/update on fresh, disjoint
// one-hot tasks and compositional parity challenges. Measure wall-clock time.
// Synthetic independent-bit labels and one-step rewards are NOT proof of
// quantum advantage, generalized intelligence, or sequential RL.
import fs from 'node:fs';
import path from 'node:path';
import assert from 'node:assert/strict';
import crypto from 'node:crypto';
import {fileURLToPath} from 'node:url';
import {quantumCommand} from '../cli.mjs';

const [runtimeArg,outArg,countArg='128']=process.argv.slice(2);
if(!runtimeArg||!outArg)throw Error('Usage: agents1000-learning-speed.mjs REVERSE_PC FRESH_OUTPUT [EVEN_TRAIN_COUNT_16..1000]');
const runtime=path.resolve(runtimeArg),out=path.resolve(outArg),n=Number(countArg);
if(!Number.isInteger(n)||n<16||n>1000||n%2)throw Error('Even training sample count must be 16..1000');
if(fs.existsSync(out))throw Error('Use a fresh experiment directory');
fs.mkdirSync(out,{recursive:true});
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'../../..');
const state=path.join(out,'agents'),memory=path.join(state,'memory.rvp');
const digest=file=>crypto.createHash('sha256').update(fs.readFileSync(file)).digest('hex');
let checks=0;
function eq(actual,expected,description){assert.deepEqual(actual,expected,description);checks++;}
function ok(condition,description){assert.ok(condition,description);checks++;}
function Q(command,...args){
 const t=performance.now();
 const result=quantumCommand({root,build:out,argv:['--runtime='+runtime,
  '--state='+state,command,...args.map(String)]});
 const elapsed_ms=+(performance.now()-t).toFixed(3);
 return {result,elapsed_ms};
}
function permute(seed){
 let s=seed>>>0,values=Array.from({length:1000},(_,i)=>i);
 const random=()=>{s^=s<<13;s^=s>>>17;s^=s<<5;return s>>>0;};
 for(let i=values.length-1;i>0;i--){const j=random()%(i+1);[values[i],values[j]]=[values[j],values[i]];}
 return values;
}
function dataset(role){
 const order=permute(role==='vqc'?0x0bc1142e:0x6d94b843);
 // Balanced labels, shuffled independently in each agent. No deterministic
 // rules relating unseen labels to neighboring indices; no train/test leakage.
 const train=order.slice(0,n).map((index,i)=>({index,label:i%2}));
 const heldout=order.slice(n,n+Math.min(48,1000-n)).map((index,i)=>({index,label:i%2}));
 const separated=new Set(train.map(x=>x.index));
 ok(train.every(x=>!heldout.some(y=>y.index===x.index)),'training and holdout positions are disjoint');
 ok(separated.size===train.length,'training indices unique');
 return {train,heldout};
}
const init=Q('init-agents-1000');
eq(init.result.vqc1000_qubits,1000,'VQC owns 1000 active qubits');
eq(init.result.qrl1000_qubits,1000,'QRL owns 1000 active qubits');
eq(init.result.active_qubits,2000,'Both independent registers are active');
const startState=Q('agents-1000-status').result;
eq(startState.vqc1000_updates,0,'VQC starts without samples');
eq(startState.qrl1000_updates,0,'QRL starts without samples');
const before=Q('status').result;
const milestones=[0,8,16,32,64,128,256,512,768,1000].filter(x=>x<=n);
if(milestones.at(-1)!==n)milestones.push(n);
const results={};
for(const role of ['vqc','qrl']){
 const {train,heldout}=dataset(role);
 const inferCmd=role==='vqc'?'vqc1000-infer':'qrl1000-act';
 const trainCmd=role==='vqc'?'vqc1000-train':'qrl1000-train';
 const probesTrain=Array.from({length:Math.min(12,n/2)},(_,i)=>{
  const offset=Math.floor(i/2)*(Math.floor(n/Math.min(12,n/2))*2);
  return train[Math.min(n-1,offset+i%2)];
 });
 const probeHoldout=heldout.slice(0,Math.min(12,heldout.length));
 const curves=[],trainingEvents=[],durations=[],quantumProbeTimes=[];
 let steps=0;
 function measured(index){
  const t=Q(inferCmd,index);
  const r=t.result;
  eq(r.processor_qubits,1000,'measured inference executes 1000-qubit '+role+' circuit');
  eq(r.state_unchanged,true,'quantum infer never modifies training');
  eq(r.active_qubits,2000,'both quantum agents are present');
  ok([0,1].includes(r.measured_action),'Born outcome is a valid bit');
  quantumProbeTimes.push(t.elapsed_ms);
  return r.measured_action;
 }
 function checkpoint(){
  const t=performance.now();
  const seen=probesTrain.map(x=>({index:x.index,expected:x.label,observed:measured(x.index)}));
  const unseen=probeHoldout.map(x=>({index:x.index,expected:x.label,observed:measured(x.index)}));
  const elapsed=+(performance.now()-t).toFixed(3);
  const count=a=>a.filter(x=>x.expected===x.observed).length;
  curves.push({after_updates:steps,
   train_probe_correct:count(seen),train_probe_total:seen.length,
   train_probe_accuracy:seen.length?count(seen)/seen.length:null,
   unseen_correct:count(unseen),unseen_total:unseen.length,
   unseen_accuracy:unseen.length?count(unseen)/unseen.length:null,
   evaluation_elapsed_ms:elapsed});
 }
 checkpoint();
 for(const [k,x] of train.entries()){
  const event=Q(trainCmd,x.index,x.label);
  const r=event.result;
  eq(r.processor_qubits,1000,'full processor actually executes learning');
  eq(r.trained_parameter_index,x.index,'learned weight belongs to requested index');
  eq(r.reward_from_xi,r.measured_action===x.label?100:0,'XI reward from actual Born action and label');
  eq(r.new_weight,x.label,'one-hot parameter corrected exactly after one supervised/terminal update');
  eq(r.visits_this_parameter,1,'one XI exposure per unique learned index');
  eq(r.quantum_measurement_used,true,'Born readout was used in learning');
  eq(r.feedback_source,'quantum Born readout -> native XI reward/update','XI reward provenance');
  const reward=r.reward_from_xi;
  trainingEvents.push({step:k+1,index:x.index,target:x.label,
   action_before_update:r.measured_action,reward,
   new_weight:r.new_weight,train_elapsed_ms:event.elapsed_ms});
  durations.push(event.elapsed_ms);
  steps++;
  if(milestones.includes(steps))checkpoint();
 }
 eq(steps,n,'complete budget was learned');
 const shaBeforeInference=digest(memory);
 const readback=train.map(x=>({index:x.index,expected:x.label})),fullProbe=readback.filter((_,i)=>i%Math.max(1,Math.floor(n/32))===0).slice(0,32);
 const fullMeasured=fullProbe.map(x=>({...x,observed:measured(x.index)}));
 const unseenAll=heldout.map(x=>({...x,observed:measured(x.index)}));
 const compositional=[];
 for(let k=0;k<24;k++){
  const count=2+(k%4); // new 2..5 feature combinations never taught as such
  const positions=new Set();
  for(let j=0;j<count;j++)positions.add((k*31+j*17+13)%n);
  const samples=[...positions].map(i=>train[i]),labels=samples.map(x=>x.label);
  const expected=labels.reduce((a,b)=>a^b,0);
  const t=Q(inferCmd,...samples.map(x=>x.index));
  const r=t.result;
  eq(r.processor_qubits,1000,'composition runs quantum 1000-qubit GHZ inference');
  eq(r.state_unchanged,true,'composition never trains');
  compositional.push({input_indices:samples.map(x=>x.index),expected,
   measured:r.measured_action,correct:r.measured_action===expected,
   elapsed_ms:t.elapsed_ms});
 }
 const classifyCorrect=values=>values.filter(x=>x.expected===x.observed).length;
 eq(classifyCorrect(fullMeasured),fullMeasured.length,'each trained 1000-qubit one-hot sample is correct');
 eq(compositional.filter(x=>x.correct).length,compositional.length,
  'new feature combinations generalize according to parity structure');
 eq(digest(memory),shaBeforeInference,'evaluation did not alter learned RVPC2 state');
 const sorted=[...durations].sort((a,b)=>a-b);
 const median=sorted[Math.floor((sorted.length-1)/2)];
 const p95=sorted[Math.ceil(.95*sorted.length)-1];
 const firstSuccessful=trainingEvents.filter(x=>x.reward===100).length;
 const after=Q('agents-1000-status').result;
 eq(after[(role==='vqc'?'vqc1000':'qrl1000')+'_updates'],n,'XI counters match training budget');
 results[role]={
  architecture:'one-step binary GHZ phase parity; 1000 physical simulated qubits and 1000 binary trainable phase parameters',
  episodes:n,positive_labels:n/2,negative_labels:n/2,
  first_pass_correct:firstSuccessful,first_pass_accuracy:firstSuccessful/n,
  first_pass_mean_reward:firstSuccessful*100/n,
  final_train_probe_correct:classifyCorrect(fullMeasured),final_train_probe_total:fullMeasured.length,
  final_train_probe_accuracy:classifyCorrect(fullMeasured)/fullMeasured.length,
  independent_unseen_correct:classifyCorrect(unseenAll),
  independent_unseen_total:unseenAll.length,
  independent_unseen_accuracy:unseenAll.length?classifyCorrect(unseenAll)/unseenAll.length:null,
  novel_combinations_correct:compositional.filter(x=>x.correct).length,
  novel_combinations_total:compositional.length,
  learned_parameters:n,total_binary_parameters:1000,
  throughput_updates_per_second:+(1000*n/durations.reduce((a,b)=>a+b,0)).toFixed(3),
  training_total_ms:+durations.reduce((a,b)=>a+b,0).toFixed(3),
  training_median_ms:median,training_p95_ms:p95,
  first_training_ms:durations[0],last_training_ms:durations.at(-1),
  inference_median_ms:[...quantumProbeTimes].sort((a,b)=>a-b)[Math.floor((quantumProbeTimes.length-1)/2)],
  milestones:curves,events:trainingEvents,novel_combinations:compositional,
  limitation:'Independent random unseen bit labels have no predictable structure; 100% one-hot memorization and parity composition are not evidence of broad generalization.'
 };
 // The parity weights are binary; a trivial classical parity table using
 // the same trained label bits predicts all these same test examples.
 results[role].classical_parity_control={
   simulated_qubits:0,parameters:1000,
   trained_one_hot_correct:fullProbe.length,
   trained_one_hot_total:fullProbe.length,
   novel_combinations_correct:compositional.length,
   novel_combinations_total:compositional.length,
   note:'Same functional class as Clifford phase parity; NOT a timed cross-runtime performance comparison.'
 };
}
const end=Q('agents-1000-audit').result;
eq(end.vqc1000_updates,n,'VQC and QRL learning parameters remain independent');
eq(end.qrl1000_updates,n,'QRL and VQC learning parameters remain independent');
eq(end.active_qubits,2000,'both actual 1000-qubit circuits persist');
const finalLegacy=Q('status').result;
eq(finalLegacy.vqc2_trained,before.vqc2_trained,'original VQC2 untouched');
eq(finalLegacy.qrl2_trained,before.qrl2_trained,'original QRL2 untouched');
const finalHash=digest(memory);
const report={
 ok:true,kind:'native-1000-qubit-agents-learning-speed',checks,
 model:'two independent 1000-qubit Clifford GHZ phase-parity agents',
 experimental_conditions:{
  qubits_per_agent:1000,active_qubits:2000,trainable_binary_parameters_per_agent:1000,
  supervised_binary_one_hot_vqc:true,one_step_reward_qrl:true,
  train_episodes_per_agent:n,unseen_disjoint_features:Math.min(48,1000-n),
  unseen_combinational_examples_per_agent:24,
  seeds:{vqc:'0x0bc1142e',qrl:'0x6d94b843'},
  fixed_hardware:'GitHub Actions ubuntu-latest; Node 24; pinned REVERSE-PC and Mundo X',
  existing_agent_checkpoints_preserved:true,artificial_labels_and_rewards:true,
  true_quantum_hardware:false,variational_continuous_angles:false,
  delayed_rewards:false,quantum_computational_advantage_demonstrated:false
 },
 initialization_ms:init.elapsed_ms,initial_model_sha256:before.state_sha256,
 final_model_sha256:finalHash,final_model_bytes:fs.statSync(memory).size,
 agents:results,
 caveats:[
  'Training tasks are independent randomized one-hot bits and binary one-step contextual rewards, not real-world tasks.',
  'An XI parameter bit can be corrected after one example; this benchmark measures a binary lookup-like model, not deep learning.',
  'Unseen independent labels have no statistical structure; do not interpret chance-level predictions as a hardware defect.',
  'New combinations of known bits test parity composition, NOT extrapolation to new bit meanings.',
  'All 1000 GHZ qubits participate in each phase-decoding circuit, but the operation stays in efficiently simulated Clifford circuits.',
  'No general 1000-qubit continuous-angle VQC or multi-step variational quantum RL has been trained.',
  'Wall-clock includes JS transport, XI process launches, RVPC2 persistence and quantum circuit execution.'
 ]
};
fs.writeFileSync(path.join(out,'results.json'),JSON.stringify(report,null,2)+'\n');
const summary={ok:report.ok,checks:report.checks,model:report.model,init_ms:report.initialization_ms,
 size_bytes:report.final_model_bytes,conditions:report.experimental_conditions,
 agents:Object.fromEntries(Object.entries(results).map(([name,r])=>[name,{
  episodes:r.episodes,learning_total_ms:r.training_total_ms,
  median_update_ms:r.training_median_ms,p95_update_ms:r.training_p95_ms,
  updates_per_second:r.throughput_updates_per_second,
  first_pass_accuracy:r.first_pass_accuracy,final_train_probe_accuracy:r.final_train_probe_accuracy,
  unseen_independent_accuracy:r.independent_unseen_accuracy,
  unseen_parity_compositions:r.novel_combinations_correct+'/'+r.novel_combinations_total,
  milestones:r.milestones
 }])),caveats:report.caveats};
fs.writeFileSync(path.join(out,'summary.json'),JSON.stringify(summary,null,2)+'\n');
console.log(JSON.stringify(summary));
