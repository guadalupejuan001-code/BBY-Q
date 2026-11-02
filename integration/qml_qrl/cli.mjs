// C07: a minimal transport for the TWO native XI learning engines.
// This module cannot train, infer, reward, or choose actions: XI alone does.
import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import {execFileSync} from 'node:child_process';
import {quantumAgents1000} from './agents1000.mjs';

const A=8100000000000000000n;
const address=n=>String(A+BigInt(n));
const fail=message=>{const error=new Error(message);error.code='E_QML_QRL';throw error;};
const hash=p=>crypto.createHash('sha256').update(fs.readFileSync(p)).digest('hex');
const registers=events=>events.filter(item=>item.type==='register').map(item=>item.value);
const matches=events=>events.filter(item=>item.type==='expectation');
const probs=events=>events.filter(item=>item.type==='probz').map(item=>item.probability_one);
const bit=(value,name)=>{if(value!=='0'&&value!=='1')fail(name+' debe ser 0 o 1.');return Number(value);};
const fileName='memory.rvp';

function native(runtime,args){
  const stdout=execFileSync(runtime,args,{encoding:'utf8',timeout:120000,maxBuffer:8*1024*1024});
  return stdout.trim().split(/\r?\n/).filter(Boolean).map(line=>JSON.parse(line));
}
function validateQ1000(events){
 const statistics=events.find(e=>e.type==='stats');
 const values=matches(events).map(e=>e.value),probabilities=probs(events);
 if(!statistics||statistics.largest_component!==1000||
    statistics.active_qubits<1000||statistics.active_qubits>4096||
    statistics.limits?.max_active_qubits<1000||
    statistics.limits?.max_component_qubits<1000||
    values.length!==3||Math.abs(values[0]-1)>1e-9||
    Math.abs(values[1]-1)>1e-9||Math.abs(values[2])>1e-9||
    probabilities.length!==2||probabilities.some(x=>Math.abs(x-0.5)>1e-9))
    fail('El registro GHZ-1000 no superó las verificaciones nativas de dimensión, entrelazamiento y probabilidades.');
 return {registered_qubits:1000,active_qubits:statistics.active_qubits,
  largest_entangled_component:statistics.largest_component,
  core_max_active_qubits:statistics.limits.max_active_qubits,
  core_max_component_qubits:statistics.limits.max_component_qubits,
  zz_first_last:values[0],zz_first_middle:values[1],xx_pair:values[2],
  p_one_first:probabilities[0],p_one_last:probabilities[1],
  representation:'Clifford/stabilizer GHZ; not arbitrary 2^1000 amplitudes',
  trained_policy_qubits:2};
}
function configFile(directory,pairs){
  const name=path.join(directory,'input.xi');
  fs.writeFileSync(name,'#!reverse-pc-machine-v1\n'+pairs.map(([p,v])=>'store8 '+address(p)+' '+v).join('\n')+'\nhalt\n');
  return name;
}
export function quantumCommand({root,build,argv}){
  const args=[],flags={};
  for(const arg of argv){
    if(arg.startsWith('--runtime='))flags.runtime=arg.slice(10);
    else if(arg.startsWith('--state='))flags.state=arg.slice(8);
    else args.push(arg);
  }
  const [command,...values]=args;
  if(!flags.state||!command)fail('Uso: quantum --runtime=REVERSE_PC --state=CARPETA init|init-1000|enable-1000|audit-1000|init-agents-1000|enable-agents-1000|agents-1000-status|vqc1000-train INDEX LABEL|vqc1000-infer INDICES|qrl1000-train INDEX GOAL|qrl1000-act INDICES|status|train-xor|train-xnor|eval|classify BIT BIT|train-agent|plan OBJETIVO ESTADO.');
  const runtime=path.resolve(flags.runtime||path.join(build,'runtime/reverse_pc'));
  if(!fs.existsSync(runtime))fail('No se encontró reverse_pc; especifica --runtime=.');
  const state=path.resolve(flags.state),memory=path.join(state,fileName);
  if(['init-agents-1000','enable-agents-1000','agents-1000-audit','agents-1000-status',
      'vqc1000-train','vqc1000-infer','qrl1000-train','qrl1000-act'].includes(command))
    return quantumAgents1000({root,runtime,state,command,values});
  const program=name=>path.join(root,'ai/xi/qml_qrl',name+'.xi');
  const invoke=(script,input,output)=>native(runtime,['run',script,input,output]);
  if(command==='init'||command==='init-1000'){
    if(values.length)fail('init no admite argumentos.');
    if(fs.existsSync(state))fail('La carpeta de memoria ya existe; no se sobrescribe.');
    fs.mkdirSync(path.dirname(state),{recursive:true});
    const staging=fs.mkdtempSync(path.join(path.dirname(state),'.bbyq-quantum-init-'));
    try{
      const blank=path.join(staging,'blank.rvp'),core=path.join(staging,'core.rvp'),vqc=path.join(staging,'vqc.rvp');
      native(runtime,['init',blank]);
      invoke(program('core-birth'),blank,core);
      invoke(program('vqc2-birth'),core,vqc);
      invoke(program('qrl2-birth'),vqc,path.join(staging,fileName));
      let quantum1000=null;
      if(command==='init-1000'){
        const attached=path.join(staging,'ghz1000.rvp');
        const report=invoke(program('q1000-birth'),path.join(staging,fileName),attached);
        quantum1000=validateQ1000(report);
        fs.renameSync(attached,path.join(staging,fileName));
      }
      for(const filename of ['blank.rvp','core.rvp','vqc.rvp'])fs.unlinkSync(path.join(staging,filename));
      fs.renameSync(staging,state);
      return {ok:true,action:command,engine:'XI',state,sha256:hash(memory),
       vqc2:'not-trained',qrl2:'not-trained',
       ...(quantum1000?{quantum1000}: {})};
    }finally{if(fs.existsSync(staging))fs.rmSync(staging,{recursive:true,force:true});}
  }
  if(!fs.existsSync(memory))fail('Memoria no inicializada. Ejecuta quantum ... init.');
  const job=fs.mkdtempSync(path.join(state,'.bbyq-quantum-'));
  const run=(name,input,filename)=>invoke(program(name),input,path.join(job,filename));
  const original=hash(memory);
  try{
    if(command==='enable-1000'){
      if(values.length)fail('enable-1000 no admite argumentos.');
      const before=run('q1000-stats',memory,'q1000-preflight.rvp').find(e=>e.type==='stats');
      if(!before||before.active_qubits>4||before.largest_component>2)
        fail('La memoria incluye cúbits no reservados por VQC2/QRL2. No se insertará GHZ-1000 encima de un circuito desconocido.');
      const events=run('q1000-birth',memory,'q1000-attached.rvp');
      const quantum1000=validateQ1000(events);
      fs.renameSync(path.join(job,'q1000-attached.rvp'),memory);
      return {ok:true,action:command,engine:'XI GHZ-1000',...quantum1000,
       prior_training_preserved:true,state_sha256:hash(memory)};
    }
    if(command==='audit-1000'){
      if(values.length)fail('audit-1000 no admite argumentos.');
      const events=run('q1000-audit',memory,'q1000-audited.rvp');
      const quantum1000=validateQ1000(events);
      return {ok:true,action:command,engine:'XI GHZ-1000',...quantum1000,
       state_unchanged:hash(memory)===original,state_sha256:original};
    }
    if(command==='status'){
      if(values.length)fail('status no admite argumentos.');
      const r=registers(run('vqc2-status',memory,'status.rvp'));
      const stats=run('q1000-stats',memory,'width.rvp').find(e=>e.type==='stats');
      return {ok:true,action:command,state_sha256:original,
       active_qubits:stats?.active_qubits??null,
       largest_entangled_component:stats?.largest_component??null,
       core_max_active_qubits:stats?.limits?.max_active_qubits??null,
       core_max_component_qubits:stats?.limits?.max_component_qubits??null,
       version_vqc2:r[0],vqc2_trained:r[1]===1,vqc2_k:r[1]===1?r[2]:null,version_qrl2:r[3],qrl2_trained:r[4]===1,qrl2_epochs:r[5]};
    }
    if(command==='train-xor'||command==='train-xnor'){
      if(values.length)fail('train no admite argumentos.');
      run(command==='train-xor'?'vqc2-feed-xor':'vqc2-feed-xnor',memory,'dataset.rvp');
      const events=run('vqc2-train',path.join(job,'dataset.rvp'),'trained.rvp');
      const r=registers(events);
      fs.renameSync(path.join(job,'trained.rvp'),memory);
      return {ok:true,action:command,engine:'XI VQC2 Bell',k:r[0],brier_penalized_q10000:r[1],state_sha256:hash(memory)};
    }
    if(command==='eval'){
      if(values.length)fail('eval no admite argumentos.');
      const r=registers(run('vqc2-eval',memory,'evaluated.rvp'));
      return {ok:true,action:command,correct:r[0],holdout:4,brier_q10000:r[1],state_unchanged:hash(memory)===original};
    }
    if(command==='classify'){
      if(values.length!==2)fail('Uso: classify BIT0 BIT1.');
      const x0=bit(values[0],'BIT0'),x1=bit(values[1],'BIT1');
      invoke(configFile(job,[[4700,x0],[4701,x1]]),memory,path.join(job,'configured.rvp'));
      const events=run('vqc2-infer',path.join(job,'configured.rvp'),'inferred.rvp');
      const r=registers(events);
      return {ok:true,action:command,engine:'XI VQC2 Bell',inputs:[x0,x1],k:r[0],p_parity_one_q10000:r[1],predicted:r[2],input_parity:r[3],bell_zz_expectation:matches(events)[0]?.value,bell_xx_expectation:matches(events)[1]?.value,qubit_one_probabilities:probs(events),state_unchanged:hash(memory)===original};
    }
    if(command==='train-agent'){
      if(values.length)fail('train-agent no admite argumentos.');
      const r=registers(run('qrl2-train',memory,'trained.rvp'));
      fs.renameSync(path.join(job,'trained.rvp'),memory);
      return {ok:true,action:command,engine:'XI QRL2',epochs:r[0],steps_per_episode:2,state_sha256:hash(memory)};
    }
    if(command==='plan'){
      if(values.length!==2)fail('Uso: plan OBJETIVO ESTADO_INICIAL.');
      const target=bit(values[0],'OBJETIVO'),initial=bit(values[1],'ESTADO_INICIAL');
      invoke(configFile(job,[[5005,target],[5006,initial]]),memory,path.join(job,'configured.rvp'));
      const events=run('qrl2-act',path.join(job,'configured.rvp'),'planned.rvp');
      const r=registers(events);
      return {ok:true,action:command,engine:'XI QRL2',target,initial,actions:[r[0],r[2]],intermediate:r[1],final:r[3],success:r[4]===1,bell_zz_expectation:matches(events)[0]?.value,bell_xx_expectation:matches(events)[1]?.value,qubit_one_probabilities:probs(events),state_unchanged:hash(memory)===original};
    }
    fail('Comando desconocido: '+command);
  }finally{fs.rmSync(job,{recursive:true,force:true});}
}
