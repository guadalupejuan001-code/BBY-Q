// Q03-Q04: two distinct 1000-qubit Clifford processors actually compute
// VQC1000 predictions and QRL1000 actions, then XI updates their own
// 1000-slot parameter vectors from verified measurement/reward outcomes.
// JavaScript is strictly input/JSONL/byte/checkpoint transport, not a model.
// This is a binary-phase GHZ parity model; NOT a 2^1000 universal circuit.
import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import {spawnSync} from 'node:child_process';

const A=8120000000000000000n;
const P=8100000000000000000n;
const hash=file=>crypto.createHash('sha256').update(fs.readFileSync(file)).digest('hex');
function fail(message){const e=new Error(message);e.code='E_Q1000_AGENT';throw e;}
function parseIndex(raw){
 if(typeof raw!=='string'||!/^(?:0|[1-9]\d{0,3})$/.test(raw)||Number(raw)>999)
  fail('Cada índice de característica debe ser un entero entre 0 y 999.');
 return Number(raw);
}
function parseBit(raw,label){
 if(raw!=='0'&&raw!=='1')fail(label+' debe ser 0 o 1.');
 return Number(raw);
}
function verifyStats(event){
 const stats=event.find(x=>x.type==='stats');
 if(!stats||stats.active_qubits<2000||stats.active_qubits>4096||
  stats.largest_component!==1000||stats.components<2||
  stats.limits?.max_active_qubits<2000||
  stats.limits?.max_component_qubits<1000)
   fail('El procesador no tiene DOS componentes físicos simulados de 1000 cúbits.');
 return stats;
}
function verifyBirth(events){
 const ex=events.filter(x=>x.type==='expectation').map(x=>x.value);
 const probs=events.filter(x=>x.type==='probz').map(x=>x.probability_one);
 const regs=events.filter(x=>x.type==='register').map(x=>x.value);
 const stats=verifyStats(events);
 if(ex.length!==2||ex.some(x=>Math.abs(x-1)>1e-9)||
  probs.length!==2||probs.some(x=>Math.abs(x-.5)>1e-9)||
  regs.length!==1||regs[0]!==1000)
  fail('El nuevo motor no verificó ambos registros GHZ-1000.');
 return {vqc1000_qubits:1000,qrl1000_qubits:1000,
  active_qubits:stats.active_qubits,component_count:stats.components,
  largest_component:stats.largest_component};
}
function runXi(runtime,source,input,output){
 const r=spawnSync(runtime,['run',source,input,output],{
  encoding:'utf8',timeout:180000,maxBuffer:8*1024*1024});
 if(r.status!==0)fail('XI '+path.basename(source)+': '+(r.stderr||r.error?.message||r.stdout||'failed'));
 try{return r.stdout.trim().split(/\r?\n/).filter(x=>x.startsWith('{')).map(x=>JSON.parse(x));}
 catch(e){fail('XI entregó datos no reconocibles: '+e.message);}
}
function frame(dir,fields){
 const file=path.join(dir,'agent-frame.xi');
 const lines=['#!reverse-pc-machine-v1'];
 for(const [offset,value] of fields){
  if(!Number.isInteger(value)||value<0||value>255)fail('Byte fuera del contrato de transporte de los agentes');
  lines.push('store8 '+(A+BigInt(offset))+' '+value);
 }
 lines.push('halt');
 fs.writeFileSync(file,lines.join('\n')+'\n',{mode:0o600});
 return file;
}
function resultOf(events,role){
 const p=events.filter(x=>x.type==='probz').map(x=>x.probability_one);
 const e=events.filter(x=>x.type==='expectation').map(x=>x.value);
 const regs=events.filter(x=>x.type==='register').map(x=>x.value);
 const stats=verifyStats(events);
 if(p.length!==2||![0,1].includes(p[0])||Math.abs(p[1]-.5)>1e-9||
   e.length!==2||Math.abs(e[0]-(p[0]===0?1:-1))>1e-9||
   Math.abs(e[1]-1)>1e-9||
   regs.length!==2||regs[0]!==1000||regs[1]!==role)
  fail('La respuesta del agente no procede de una medición verificable de su circuito GHZ-1000.');
 return {measured_action:p[0],processor_qubits:1000,
   measurement_z_expectation:e[0],ghz_restored_zz:e[1],
   ghz_restored_p_one:p[1],active_qubits:stats.active_qubits,
   largest_component:stats.largest_component,
   input_dimensions:1000,model_parameters:1000,entangling_gates_per_forward_pass:1998,
   circuit:'1000-qubit GHZ phase oracle, 999 inverse CX, H, Born readout, H, 999 CX, phase uncompute'};
}
const listArgs=values=>{
 if(!values.length||values.length>32)fail('Usa 1..32 índices de características entre 0 y 999.');
 const indices=values.map(parseIndex);
 if(new Set(indices).size!==indices.length)fail('No se repiten índices de características.');
 return indices;
};
export function quantumAgents1000({root,runtime,state,command,values}){
 const memory=path.join(state,'memory.rvp');
 const program=name=>path.join(root,'ai/xi/qml_qrl',name+'.xi');
 const call=(name,from,to)=>runXi(runtime,program(name),from,to);
 if(command==='init-agents-1000'){
  if(values.length||fs.existsSync(state))fail('Crea una carpeta nueva para init-agents-1000.');
  fs.mkdirSync(path.dirname(state),{recursive:true});
  const dir=fs.mkdtempSync(path.join(path.dirname(state),'.bbyq-1000-agents-init-'));
  try{
   let previous=path.join(dir,'blank.rvp');
   const boot=spawnSync(runtime,['init',previous],{encoding:'utf8',timeout:60000});
   if(boot.status!==0)fail('No se pudo inicializar Ether: '+(boot.stderr||''));
   let i=0,report;
   for(const name of ['core-birth','vqc2-birth','qrl2-birth','q1000-birth','agents1000-birth']){
    const next=path.join(dir,'step-'+(++i)+'.rvp'),events=call(name,previous,next);
    if(name==='agents1000-birth')report=verifyBirth(events);
    if(previous!==path.join(dir,'blank.rvp'))fs.unlinkSync(previous);
    previous=next;
   }
   fs.renameSync(previous,path.join(dir,'memory.rvp'));
   fs.unlinkSync(path.join(dir,'blank.rvp'));
   fs.renameSync(dir,state);
   return {ok:true,action:command,engine:'XI VQC1000+QRL1000',
    ...report,state_sha256:hash(memory),old_engines_preserved:true,
    training:'not-yet-trained; each agent has its OWN 1000-qubit processor'};
  }finally{if(fs.existsSync(dir))fs.rmSync(dir,{recursive:true,force:true});}
 }
 if(!fs.existsSync(memory))fail('No hay memoria RVPC2; utiliza init-agents-1000.');
 const job=fs.mkdtempSync(path.join(state,'.qagent1000-'));
 const original=hash(memory);
 try{
  if(command==='enable-agents-1000'){
   if(values.length)fail('enable-agents-1000 no admite argumentos.');
   const before=call('q1000-stats',memory,path.join(job,'scan.rvp'));
   const stats=before.find(x=>x.type==='stats');
   if(!stats)fail('No hay estadísticas Ether.');
   let input=memory;
   if(stats.active_qubits<=4){
    input=path.join(job,'ghz-base.rvp');
    const events=call('q1000-birth',memory,input);
    const e=events.filter(x=>x.type==='expectation').map(x=>x.value);
    if(e.length!==3||Math.abs(e[0]-1)>1e-9||Math.abs(e[1]-1)>1e-9)
     fail('No se pudo instalar el GHZ-1000 del VQC.');
   }else{
    if(stats.largest_component!==1000||stats.active_qubits>1004)
     fail('No se permite ampliar una memoria con cúbits desconocidos o ya asignados.');
    call('q1000-audit',memory,path.join(job,'pre-audit.rvp'));
   }
   const next=path.join(job,'agents.rvp');
   const attached=verifyBirth(call('agents1000-birth',input,next));
   fs.renameSync(next,memory);
   return {ok:true,action:command,engine:'XI VQC1000+QRL1000',
    ...attached,old_engines_preserved:true,state_sha256:hash(memory)};
  }
  if(command==='agents-1000-audit'||command==='agents-1000-status'){
   if(values.length)fail(command+' no admite argumentos.');
   const events=call('agents1000-audit',memory,path.join(job,'audit.rvp'));
   const ex=events.filter(x=>x.type==='expectation').map(x=>x.value);
   const ps=events.filter(x=>x.type==='probz').map(x=>x.probability_one);
   const regs=events.filter(x=>x.type==='register').map(x=>x.value);
   const stats=verifyStats(events);
   if(ex.length!==2||ex.some(x=>Math.abs(x-1)>1e-9)||
     ps.length!==2||ps.some(x=>Math.abs(x-.5)>1e-9)||regs.length!==2)
    fail('Auditoría de ambos agentes de 1000 cúbits incompleta.');
   return {ok:true,action:command,engine:'XI VQC1000+QRL1000',
    vqc1000_qubits:1000,qrl1000_qubits:1000,
    active_qubits:stats.active_qubits,largest_component:stats.largest_component,
    vqc1000_updates:regs[0],qrl1000_updates:regs[1],
    state_unchanged:hash(memory)===original,state_sha256:original};
  }
  const isTrain=command==='vqc1000-train'||command==='qrl1000-train';
  const isInfer=command==='vqc1000-infer'||command==='qrl1000-act';
  if(!isTrain&&!isInfer)fail('Comando desconocido de agente: '+command);
  const role=command.startsWith('qrl')?1:0;
  let indices,target;
  if(isTrain){
   if(values.length!==2)fail('Uso: '+command+' INDEX_0_TO_999 OBJETIVO_0_OR_1.');
   indices=[parseIndex(values[0])];
   target=parseBit(values[1],'La etiqueta/objetivo');
  }else indices=listArgs(values);
  const fields=[[1,role],[2,indices.length],[3,target??0],[4,0],[5,0]];
  for(const [i,index] of indices.entries())fields.push([20+2*i,index%256],[21+2*i,Math.floor(index/256)]);
  const configured=path.join(job,'configured.rvp');
  runXi(runtime,frame(job,fields),memory,configured);
  const staged=path.join(job,'features.rvp');
  const selected=call('agents1000-stage',configured,staged);
  if(selected.filter(x=>x.type==='register')[0]?.value!==indices.length)
   fail('El motor XI no preparó la entrada dimensional solicitada.');
  const quantumOutput=path.join(job,'measured.rvp');
  const readout=resultOf(call('agents1000-infer',staged,quantumOutput),role);
  const base={ok:true,action:command,engine:role===0?'XI VQC1000':'XI QRL1000',
   input_positions:indices,...readout,quantum_measurement_used:true,
   quantum_hardware:false,mode:'1000-qubit stabilizer phase oracle, native XI'};
  if(!isTrain)return {...base,state_unchanged:hash(memory)===original,state_sha256:original};
  // The Born measurement is transported into native XI as a byte: the host
  // DOES NOT generate the reward, train weights or choose the action.
  const observed=path.join(job,'observed.rvp');
  runXi(runtime,frame(job,[[4,readout.measured_action]]),staged,observed);
  let input=observed,rewardFromXi=null;
  if(role===1){
   const rewardFile=path.join(job,'reward.rvp');
   const e=call('agents1000-reward',observed,rewardFile);
   rewardFromXi=e.filter(x=>x.type==='register')[0]?.value;
   if(![0,100].includes(rewardFromXi))fail('Recompensa nativa de entorno incorrecta.');
   input=rewardFile;
  }
  const trained=path.join(job,'trained.rvp');
  const rows=call('agents1000-update',input,trained).filter(x=>x.type==='register').map(x=>x.value);
  if(rows.length!==7||rows[0]!==role||rows[1]!==indices[0]||
    ![0,1].includes(rows[2])||rows[3]<1||rows[4]<1||rows[5]!==readout.measured_action||
    ![0,100].includes(rows[6])||(role===1&&rows[6]!==rewardFromXi))
   fail('Aprendizaje XI no coincide con la acción realmente medida.');
  fs.renameSync(trained,memory);
  return {...base,trained_parameter_index:indices[0],new_weight:rows[2],
    visits_this_parameter:rows[3],updates_total:rows[4],reward_from_xi:rows[6],
    label_or_environment_goal:target,prior_state_sha256:original,state_sha256:hash(memory),
    feedback_source:'quantum Born readout -> native XI reward/update'};
 }finally{fs.rmSync(job,{recursive:true,force:true});}
}
