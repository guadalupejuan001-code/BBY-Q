// Transactional byte transport for the existing trained V3 agents.
// XI authorizes commands and selects policy actions. This is not a language model.
import fs from 'node:fs';
import path from 'node:path';
import zlib from 'node:zlib';
import {fileURLToPath} from 'node:url';
import {quantum3Command} from './launcher.mjs';
import {sha,fail} from '../../ai/personal/x10/pages.mjs';

const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'../..');
const help={
 es:'VQC3/QRL3: quantum v3 estado; quantum v3 resultados; quantum v3 planea POSICIÓN OBJETIVO (0–6); quantum v3 clasifica [1000 números]. Son tareas numéricas, no conversación generada por estos agentes.',
 en:'VQC3/QRL3: quantum v3 status; quantum v3 results; quantum v3 plan POSITION GOAL (0–6); quantum v3 classify [1000 numbers]. These agents perform numeric tasks; they do not generate conversation.'
};
const identity=config=>Object.fromEntries(['model_identifier','qubits_per_agent','session_sha256','cli_sha256','source_sha256','extension_source_sha256'].map(k=>[k,config[k]]));
const percent=x=>(100*x).toFixed(1);

function nativeRuntime(runtime){
 const selected=process.env.BBYQ_QUANTUM_RUNTIME||path.resolve(path.dirname(runtime),'..');
 for(const name of ['build/reverse_pc','build/xi_session']){
  if(!fs.existsSync(path.join(selected,name)))throw fail('E_QUANTUM3_RUNTIME',
   'VQC3/QRL3 requieren el runtime XI compilado. Configura BBYQ_QUANTUM_RUNTIME con su directorio; no se sustituirán por otro modelo.');
 }
 return path.resolve(selected);
}

function workspace(db,runtime,job){
 db.exec('CREATE TABLE IF NOT EXISTS quantum3_state ('+
  'id INTEGER PRIMARY KEY CHECK(id=1), data BLOB NOT NULL,'+
  'digest TEXT NOT NULL CHECK(length(digest)=64), identity TEXT NOT NULL) STRICT;');
 const stored=db.prepare('SELECT data,digest,identity FROM quantum3_state WHERE id=1').get();
 const dir=path.join(job,'quantum3-session');
 quantum3Command({root,argv:['prepare',dir,'--runtime='+nativeRuntime(runtime)]});
 const config=JSON.parse(fs.readFileSync(path.join(dir,'agent.json'),'utf8'));
 if(stored){
  if(JSON.stringify(identity(config))!==stored.identity)throw fail('E_QUANTUM3_BUILD','El runtime o las fuentes V3 cambiaron. Se conservó el modelo de esta sesión.');
  const bytes=zlib.inflateRawSync(stored.data,{maxOutputLength:16*1024*1024});
  if(sha(bytes)!==stored.digest)throw fail('E_QUANTUM3_INTEGRITY','El checkpoint V3 no coincide con su huella.');
  const headFile=path.join(dir,'HEAD.json'),head=JSON.parse(fs.readFileSync(headFile,'utf8'));
  fs.writeFileSync(path.join(dir,head.file),bytes,{mode:0o600});
  head.sha256=stored.digest;fs.writeFileSync(headFile,JSON.stringify(head));
 }
 return {dir,stored,config};
}

function save(db,dir,config){
 const head=JSON.parse(fs.readFileSync(path.join(dir,'HEAD.json'),'utf8'));
 const bytes=fs.readFileSync(path.join(dir,head.file));
 if(sha(bytes)!==head.sha256)throw fail('E_QUANTUM3_INTEGRITY','La inferencia alteró su checkpoint.');
 db.prepare('INSERT INTO quantum3_state VALUES(1,?,?,?) ON CONFLICT(id) DO UPDATE SET data=excluded.data,digest=excluded.digest,identity=excluded.identity')
  .run(zlib.deflateRawSync(bytes),head.sha256,JSON.stringify(identity(config)));
 return head.sha256;
}

export function quantum3Conversation(db,{runtime,job,raw,decision,language='es'}){
 const en=language==='en',meta={extension:'VQC3-QRL3-native-XI-X10',
  quantum_action:decision.action,quantum_source:'native XI',quantum_model:'VQC3/QRL3',
  quantum_problem:'synthetic-numeric-classification-and-line-navigation',
  original_training_preserved:true,knowledge_read_only:true,context_skip_record:true};
 if(decision.action===5||decision.action===254)return {ok:true,...meta,
  quantum_connected:false,response:help[en?'en':'es']};
 let input;
 if(decision.action===3){
  const bytes=raw.subarray(decision.payloadOffset);
  if(bytes.length>256*1024)throw fail('E_QUANTUM3_INPUT','La entrada numérica supera 256 KiB.');
  try{input=JSON.parse(bytes.toString('utf8'));}catch{throw fail('E_QUANTUM3_INPUT','Se requiere un arreglo JSON de 1000 números.');}
  if(!Array.isArray(input)||input.length!==1000||input.some(v=>typeof v!=='number'||!Number.isFinite(v)))
   throw fail('E_QUANTUM3_INPUT','Se requieren exactamente 1000 números finitos.');
 }
 const {dir,stored,config}=workspace(db,runtime,job);
 const call=(...argv)=>quantum3Command({root,argv:[argv[0],dir,...argv.slice(1)]});
 let result,response;
 if(decision.action===1){
  result=call('status');
  const m=result.model;
  response=`VQC3: ${m.vqc.training_episodes_in_checkpoint} ${en?'training episodes':'episodios entrenados'}; QRL3: ${m.qrl.training_episodes_in_checkpoint}. `+
   (en?'1000 qubits per agent. Numeric classification and movement decisions.':'1000 cúbits por agente. Clasificación numérica y decisiones de movimiento.');
 }else if(decision.action===2){
  result=call('results');
  if(!result.evaluation.applicable)response=en?'This checkpoint has not received the published evaluation.':'Este checkpoint no tiene una evaluación publicada que corresponda a sus parámetros.';
  else{
   const measured=result.evaluation.results;
   response=`VQC3: ${measured.main.vqc.correct}/${measured.main.vqc.examples} (${percent(measured.main.vqc.rate)}%). QRL3: ${measured.main.qrl.correct}/${measured.main.qrl.examples} (${percent(measured.main.qrl.rate)}%). `+
    (en?'These are saved results on specific synthetic tasks. Resetting circuit angles did not reduce correct answers in the 128-case controls. Arbitrary-goal direction decisions: ':'Son resultados guardados de tareas sintéticas específicas. Reiniciar los ángulos no redujo aciertos en los controles de 128 casos. Direcciones con objetivos variados: ')+
    `${measured.qrl_all_distinct_position_goal_pairs.correct}/${measured.qrl_all_distinct_position_goal_pairs.examples}.`;
  }
 }else if(decision.action===3){
  const file=path.join(job,'vqc3-input.json');fs.writeFileSync(file,JSON.stringify(input),{flag:'wx',mode:0o600});
  result=call('classify',file);
  response=(en?'VQC3 predicted class ':'VQC3 predijo la clase ')+result.prediction+
   (en?' for the 1000 numeric inputs.':' para las 1000 entradas numéricas.');
 }else if(decision.action===4){
  result=call('act',String(decision.first),String(decision.second),'--greedy');
  if(result.terminal)response=en?'The goal is already reached. No movement is pending.':'El objetivo ya está alcanzado. No hay movimiento pendiente.';
  else{
   const direction=result.action===1?(en?'right':'derecha'):(en?'left':'izquierda');
   response=(en?'QRL3 proposes moving ':'QRL3 propone moverse a la ')+direction+
    (en?' from ':' desde ')+decision.first+(en?' toward goal ':' hacia el objetivo ')+decision.second+'.';
   if(!result.training_scope.goal_seen_in_training)response+=en?' This goal was outside its original training; the action can fail.':' Este objetivo quedó fuera de su entrenamiento original; la acción puede fallar.';
  }
 }else throw fail('E_QUANTUM3_ROUTE','Acción V3 no válida.');
 const head=JSON.parse(fs.readFileSync(path.join(dir,'HEAD.json'),'utf8'));
 if(stored&&head.sha256!==stored.digest)throw fail('E_QUANTUM3_INTEGRITY','La consulta cambió el modelo guardado.');
 const digest=stored?stored.digest:save(db,dir,config);
 return {ok:true,...meta,quantum_connected:true,response,
  quantum_data:{model_identifier:173,qubits_per_agent:1000,state_sha256:digest,result}};
}
