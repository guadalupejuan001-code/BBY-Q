// C09: X10 conversational bridge to original XI-only QML/QRL engines.
// JavaScript is only durable byte transport and presentation. XI parses,
// trains, evaluates, classifies, propagates rewards and selects actions.
import fs from 'node:fs';
import path from 'node:path';
import zlib from 'node:zlib';
import {fileURLToPath} from 'node:url';
import {quantumCommand} from './cli.mjs';
import {sha,fail,cells} from '../../ai/personal/x10/pages.mjs';

const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'../..');
const help={
 es:'Comandos XI: quantum estado; quantum entrena xor; quantum entrena xnor; quantum evalua; quantum clasifica 0 1; quantum entrena agente; quantum planea 1 0. Solo son problemas de laboratorio.',
 en:'XI commands: quantum status; quantum train xor; quantum train xnor; quantum eval; quantum classify 0 1; quantum train agent; quantum plan 1 0. These are laboratory tasks only.'
};
function slot(db){
 db.exec('CREATE TABLE IF NOT EXISTS quantum_state ('+
  'id INTEGER PRIMARY KEY CHECK(id=1),'+
  'data BLOB NOT NULL,digest TEXT NOT NULL CHECK(length(digest)=64)) STRICT;');
 return db.prepare('SELECT data,digest FROM quantum_state WHERE id=1').get();
}
function workspace(db,{runtime,base,job}){
 const dir=path.join(job,'quantum-rvpc2'),stored=slot(db);
 if(stored){
  fs.mkdirSync(dir,{mode:0o700});
  const data=zlib.inflateRawSync(stored.data,{maxOutputLength:32*1024*1024});
  if(sha(data)!==stored.digest)throw fail('E_QUANTUM_INTEGRITY','Huella cuántica incorrecta.');
  const destination=path.join(dir,'memory.rvp');
  fs.writeFileSync(destination,data,{mode:0o600});
  cells(destination);
 }else{
  quantumCommand({root,build:path.resolve(base,'..'),
   argv:['--runtime='+runtime,'--state='+dir,'init']});
 }
 return {dir,stored};
}
function save(db,dir){
 const file=path.join(dir,'memory.rvp'),data=fs.readFileSync(file);
 cells(file);
 const digest=sha(data);
 db.prepare('INSERT INTO quantum_state VALUES(1,?,?) ON CONFLICT(id) DO UPDATE SET data=excluded.data,digest=excluded.digest')
  .run(zlib.deflateRawSync(data),digest);
 return digest;
}
export function quantumConversation(db,{runtime,base,job,decision,language='es'}){
 const en=language==='en',action=decision.action,helpText=help[en?'en':'es'];
 const meta={extension:'QML-QRL-native-XI-X10',quantum_action:action,
  quantum_source:'native XI',quantum_problem:'synthetic-two-qubit',
  original_training_preserved:true,knowledge_read_only:![2,3,6].includes(action)};
 if(action===0||action===254||action===8){
  return {ok:true,...meta,quantum_connected:false,context_skip_record:true,
   response:action===8?helpText:(en?'Unrecognized quantum request. ':'Orden cuántica no reconocida. ')+helpText};
 }
 const {dir,stored}=workspace(db,{runtime,base,job});
 const run=(cmd,...params)=>quantumCommand({root,build:path.resolve(base,'..'),
  argv:['--runtime='+runtime,'--state='+dir,cmd,...params.map(String)]});
 const current=run('status');
 let result,response;
 if(action===1){
  result=current;
  response=en
   ?'XI state: VQC2 '+(current.vqc2_trained?'trained (k='+current.vqc2_k+')':'not trained')+
    '; QRL2 '+(current.qrl2_trained?'trained ('+current.qrl2_epochs+' rounds)':'not trained')+'.'
   :'Estado XI: VQC2 '+(current.vqc2_trained?'entrenado (k='+current.vqc2_k+')':'sin entrenar')+
    '; QRL2 '+(current.qrl2_trained?'entrenado ('+current.qrl2_epochs+' rondas)':'sin entrenar')+'.';
 }else if(action===2||action===3){
  result=run(action===2?'train-xor':'train-xnor');
  response=(en?'VQC2 trained on ':'VQC2 entrenado con ')+(action===2?'XOR':'XNOR')+
   ': k='+result.k+', Brier='+result.brier_penalized_q10000+'/10000.';
 }else if(action===4||action===5){
  if(!current.vqc2_trained){
   response=en?'VQC2 is not trained. Use "quantum train xor" or "quantum train xnor".':
    'VQC2 aún no está entrenado. Usa «quantum entrena xor» o «quantum entrena xnor».';
  }else if(action===4){
   result=run('eval');
   response=(en?'VQC2 holdout: ':'Evaluación VQC2: ')+result.correct+'/'+result.holdout+
    (en?' correct.':' aciertos.')+' Brier='+result.brier_q10000+'/10000.';
  }else{
   result=run('classify',decision.first,decision.second);
   response=(en?'VQC2 Bell classification ':'Clasificación VQC2 Bell ')+
    '['+decision.first+','+decision.second+']: '+(en?'prediction=':'predicción=')+
    result.predicted+', P(paridad=1)='+result.p_parity_one_q10000+'/10000, k='+result.k+'.';
  }
 }else if(action===6){
  result=run('train-agent');
  response=(en?'QRL2 trained: ':'QRL2 entrenado: ')+result.epochs+
   (en?' rounds, ':' rondas, ')+result.steps_per_episode+
   (en?' steps per episode.':' decisiones por episodio.');
 }else if(action===7){
  if(!current.qrl2_trained){
   response=en?'QRL2 is not trained. Use "quantum train agent".':
    'QRL2 aún no está entrenado. Usa «quantum entrena agente».';
  }else{
   result=run('plan',decision.first,decision.second);
   response=(en?'QRL2 plan: ':'Plan QRL2: ')+(en?'target=':'objetivo=')+decision.first+
    ', '+(en?'start=':'inicio=')+decision.second+
    ', '+(en?'actions=':'acciones=')+'['+result.actions.join(',')+']'+
    ', final='+result.final+', '+(en?'success=':'éxito=')+(result.success?'sí':'no')+'.';
  }
 }else throw fail('E_QUANTUM_ROUTE','Acción XI no reconocida.');
 const stateDigest=(!stored||[2,3,6].includes(action))?save(db,dir):sha(fs.readFileSync(path.join(dir,'memory.rvp')));
 return {ok:true,...meta,quantum_connected:true,response,
  quantum_data:{state_sha256:stateDigest,
   ...(action===5&&result?{prediction:result.predicted,probability_q10000:result.p_parity_one_q10000,
    zz:result.bell_zz_expectation,xx:result.bell_xx_expectation}:{}),
   ...(action===7&&result?{actions:result.actions,final:result.final,success:result.success,
    zz:result.bell_zz_expectation,xx:result.bell_xx_expectation}:{}),
   ...(action===4&&result?{correct:result.correct,holdout:result.holdout}:{}),
   ...([2,3,6].includes(action)?{training:result}:{})}};
}
