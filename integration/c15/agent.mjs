// C15: feedback-bound route learning, in native XI and the existing X10 transaction.
// The original C14 supervised prior is consulted, but its weights are never edited.
// This is a terminal contextual Q/bandit update (not the synthetic Bell QRL2,
// not measured quantum feedback, and not a claim of improved dialogue quality).
import fs from 'node:fs';
import path from 'node:path';
import zlib from 'node:zlib';
import {fileURLToPath} from 'node:url';
import {c14Shadow} from '../c14/shadow.mjs';
import {sha,fail,run,cells} from '../../ai/personal/x10/pages.mjs';

const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'../..');
const program=name=>path.join(root,'ai/xi/cognitive15',name+'.xi');
const Q=8280000000000000000n;
const routeNames=['X10 original','P05 memoria','P03 razonamiento','P04 composición'];
const readRegisters=output=>output.split('\n').filter(x=>x.startsWith('{'))
 .map(x=>JSON.parse(x)).filter(x=>x.type==='register').map(x=>x.value);
const qTables=db=>{
 db.exec('CREATE TABLE IF NOT EXISTS c15_policy ('+
  'id INTEGER PRIMARY KEY CHECK(id=1),data BLOB NOT NULL,digest TEXT NOT NULL CHECK(length(digest)=64)) STRICT;'+
  'CREATE TABLE IF NOT EXISTS c15_feedback ('+
  'target_id TEXT PRIMARY KEY,context INTEGER NOT NULL,action INTEGER NOT NULL,'+
  'reward INTEGER NOT NULL,response_sha256 TEXT NOT NULL,policy_sha256 TEXT NOT NULL) STRICT;');
};
const exists=(db,name)=>!!db.prepare("SELECT 1 FROM sqlite_master WHERE type='table' AND name=?").get(name);
function openPolicy(db,{runtime,dir}){
 const target=path.join(dir,'policy.rvp');
 const row=exists(db,'c15_policy')?db.prepare('SELECT data,digest FROM c15_policy WHERE id=1').get():null;
 if(row){
  const bytes=zlib.inflateRawSync(row.data,{maxOutputLength:8*1024*1024});
  if(sha(bytes)!==row.digest)throw fail('E_C15_INTEGRITY','El aprendizaje QRL de C15 no coincide con su huella.');
  fs.writeFileSync(target,bytes,{mode:0o600});
  cells(target);
 }else{
  const blank=path.join(dir,'blank.rvp');
  run(runtime,['init',blank]);
  const birth=readRegisters(run(runtime,['run',program('birth'),blank,target]));
  if(birth.length!==1||birth[0]!==15)throw fail('E_C15_BIRTH','Firma inicial QRL XI incompatible.');
 }
 return {target,trained:!!row,digest:row?.digest??null};
}
function encodeFrame(file,fields){
 const lines=['#!reverse-pc-machine-v1'];
 for(const [offset,value] of fields){
  if(!Number.isInteger(value)||value<0||value>255)throw fail('E_C15_FRAME','Parámetro del agente XI fuera del contrato.');
  lines.push('store8 '+(Q+BigInt(offset))+' '+value);
 }
 fs.writeFileSync(file,lines.join('\n')+'\nhalt\n',{mode:0o600});
 return file;
}
function observe(db,{runtime,job,features}){
 const directory=path.join(job,'c15-state');fs.mkdirSync(directory,{recursive:true,mode:0o700});
 const {target,digest}=openPolicy(db,{runtime,dir:directory});
 const frame=encodeFrame(path.join(directory,'observe-frame.xi'),[
  [1,features.context],[4,features.suggested_action],
  [5,features.abstained?0:1],[6,features.semantic_class]
 ]);
 const staged=path.join(directory,'input.rvp'),out=path.join(directory,'inference.rvp');
 run(runtime,['run',frame,target,staged]);
 const values=readRegisters(run(runtime,['run',program('observe'),staged,out]));
 if(values.length!==7||values[0]!==features.context||
  !Number.isInteger(values[1])||values[1]<0||values[1]>3||
  ![0,1].includes(values[2])||values[3]<0||values[3]>2||
  values[4]<0||values[4]>10000||values[5]<0||values[5]>65535||
  values[6]<0||values[6]>65535)
  throw fail('E_C15_OBSERVE','La política XI devolvió una decisión inválida.');
 // The model file must remain immutable on an observation-only turn.
 if(digest!==null&&sha(fs.readFileSync(target))!==digest)
  throw fail('E_C15_READONLY','La observación modificó el estado persistente del agente.');
 return {action:values[1],admitted:values[2]===1,
  source:['guard','C14-supervised-prior','C15-outcome-Q'][values[3]],
  value_q10000:values[4],samples_for_action:values[5],
  total_feedback:values[6],policy_sha256:digest};
}
export function executedRoute(result){
 // Provenance is metadata from X10, not an inferred quality label or C14 recommendation.
 const ext=result?.extension;
 if(ext==='X09-preserved'||ext==='X10-streamed-text'||ext==='X10-paged-lessons')return 0;
 if(ext==='P05-context-XI'&&result.context_mode!==0&&result.context_mode!==6&&
    result.context_mode!==7&&result.context_mode!==8)return 1;
 if(ext==='P03-native-XI')return 2;
 if(ext==='P04-native-XI')return 3;
 return null; // P06, E034, QUANTUM and other modules cannot be mislabelled.
}
export function c15Shadow(db,{runtime,roles,job,raw,result}){
 const base={engine:'C15 native XI outcome-learning',mode:'shadow',applied:false,
  quantum_hardware:false,auto_training:false,
  learns_from:'one explicitly rated actual X10 response; not the proposed alternative',
  real_reply_improvement_proven:false};
 const prior=c14Shadow(db,{runtime,roles,job:path.join(job,'c14'),raw});
 if(!prior.available)
  return {...base,available:false,reason:prior.reason,actual_action:executedRoute(result)};
 const measured=observe(db,{runtime,job,features:prior});
 const actual=executedRoute(result);
 return {...base,available:true,c14_prior_action:prior.suggested_action,
  context:prior.context,semantic_class:prior.semantic_class,p01_intent:prior.p01_intent,
  suggested_action:measured.action,suggested_route:routeNames[measured.action],
  source:measured.source,admitted:measured.admitted,training_q10000:measured.value_q10000,
  samples_for_action:measured.samples_for_action,total_feedback:measured.total_feedback,
  policy_sha256:measured.policy_sha256,
  actual_action:actual,actual_route:actual===null?null:routeNames[actual],
  actual_response_sha256:sha(Buffer.from(result.response,'utf8')),
  feedback_eligible:actual!==null&&prior.context>=0&&prior.context<144};
}
export function recordFeedback(db,{runtime,job,feedback,language='es'}){
 const {targetId,reward}=feedback??{};
 if(typeof targetId!=='string'||!/^[A-Za-z0-9_.-]{1,96}$/.test(targetId)||
    !Number.isInteger(reward)||reward<0||reward>100)
  throw fail('E_C15_FEEDBACK','Indica ID original y recompensa explícita entre 0 y 100.');
 if(!exists(db,'receipts'))throw fail('E_C15_RECEIPT','No hay comprobantes X10.');
 const target=db.prepare('SELECT result FROM receipts WHERE id=?').get(targetId);
 if(!target)throw fail('E_C15_TARGET','La respuesta evaluada no pertenece a esta sesión.');
 let previous;
 try{previous=JSON.parse(zlib.inflateRawSync(target.result,{maxOutputLength:16*1024*1024}));}
 catch{throw fail('E_C15_RECEIPT','No se puede verificar el comprobante anterior.');}
 const shadow=previous?.c15_shadow;
 if(previous?.ok!==true||previous?.committed!==true||!shadow?.available||
    shadow?.feedback_eligible!==true||shadow?.actual_action===null||
    shadow?.actual_action===undefined||!Number.isInteger(shadow.context)||
    shadow.context<0||shadow.context>143||shadow?.applied!==false||
    ![0,1,2,3].includes(shadow.actual_action)||
    sha(Buffer.from(previous.response||'','utf8'))!==shadow.actual_response_sha256)
  throw fail('E_C15_PROVENANCE','Solo se califican respuestas reales previamente observadas, con procedencia verificable.');
 // Rating uniqueness and XI state replacement happen in ONE X10 SQLite transaction.
 qTables(db);
 if(db.prepare('SELECT 1 FROM c15_feedback WHERE target_id=?').get(targetId))
  throw fail('E_C15_DUPLICATE','Este resultado ya recibió una calificación y no puede contarse dos veces.');
 const dir=path.join(job,'c15-feedback');fs.mkdirSync(dir,{recursive:true,mode:0o700});
 const {target:policyState}=openPolicy(db,{runtime,dir});
 const frame=encodeFrame(path.join(dir,'feedback-frame.xi'),[
  [1,shadow.context],[2,shadow.actual_action],[3,reward]
 ]);
 const prepared=path.join(dir,'prepared.rvp'),trained=path.join(dir,'trained.rvp');
 run(runtime,['run',frame,policyState,prepared]);
 const values=readRegisters(run(runtime,['run',program('update'),prepared,trained]));
 if(values.length!==5||values[0]!==shadow.context||values[1]!==shadow.actual_action||
    values[2]<0||values[2]>10000||values[3]<1||values[3]>65535||
    values[4]<1||values[4]>65535)
  throw fail('E_C15_UPDATE','XI no confirmó el aprendizaje en una ruta ejecutada.');
 cells(trained);
 const bytes=fs.readFileSync(trained),digest=sha(bytes);
 db.prepare('INSERT INTO c15_policy(id,data,digest) VALUES(1,?,?) '+
  'ON CONFLICT(id) DO UPDATE SET data=excluded.data,digest=excluded.digest')
  .run(zlib.deflateRawSync(bytes),digest);
 db.prepare('INSERT INTO c15_feedback(target_id,context,action,reward,response_sha256,policy_sha256) '+
  'VALUES(?,?,?,?,?,?)')
  .run(targetId,shadow.context,shadow.actual_action,reward,shadow.actual_response_sha256,digest);
 const route=routeNames[shadow.actual_action];
 const response=(language==='en'?'Native XI reward saved for the route that ACTUALLY replied: ':
   'Aprendizaje XI guardado para la ruta que REALMENTE respondió: ')+
  route+'. Q='+values[2]+'/10000, registros de esta ruta='+values[3]+
  ', evaluaciones totales='+values[4]+'. La política sigue en observación.';
 return {ok:true,response,extension:'C15-native-XI-explicit-outcome-feedback',
  context_skip_record:true,knowledge_read_only:true,original_training_preserved:true,
  c15_training:{target_id:targetId,context:shadow.context,
   trained_action:shadow.actual_action,executed_route:route,reward,
   q_value_q10000:values[2],action_feedback_count:values[3],
   total_feedback:values[4],policy_sha256:digest,
   original_response_sha256:shadow.actual_response_sha256,
   observed_reply_only:true,auto_applied:false}};
}
