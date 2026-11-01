// C12: native XI policy scored in shadow mode, never substituted for the actual X10 answer.
// No data-dependent decisions or reward updates occur in JavaScript.
import fs from 'node:fs';
import path from 'node:path';
import zlib from 'node:zlib';
import {fileURLToPath} from 'node:url';
import {NativePages,sha,fail,cells,run} from '../../ai/personal/x10/pages.mjs';
import {history} from '../../ai/personal/p05/store.mjs';

const project=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'../..');
const C=8250000000000000000n;
const program=name=>path.join(project,'ai/xi/cognitive',name+'.xi');
const actions=Object.freeze(['X10 original','P05 memoria','P03 razonamiento','P04 composición']);
const output=jsonl=>jsonl.split('\n').filter(line=>line.startsWith('{'))
 .map(line=>JSON.parse(line)).filter(row=>row.type==='register').map(row=>row.value);
function quantumStore(db){
 db.exec('CREATE TABLE IF NOT EXISTS cognitive_policy ('+
  'id INTEGER PRIMARY KEY CHECK(id=1),'+
  'data BLOB NOT NULL,digest TEXT NOT NULL CHECK(length(digest)=64)) STRICT;');
 return db.prepare('SELECT data,digest FROM cognitive_policy WHERE id=1').get();
}
function persist(db,file){
 cells(file);
 const bytes=fs.readFileSync(file),digest=sha(bytes);
 db.prepare('INSERT INTO cognitive_policy VALUES(1,?,?) '+
  'ON CONFLICT(id) DO UPDATE SET data=excluded.data,digest=excluded.digest')
  .run(zlib.deflateRawSync(bytes),digest);
 return digest;
}
function openModel(db,runtime,dir){
 const stored=quantumStore(db),state=path.join(dir,'policy.rvp');
 if(stored){
  const bytes=zlib.inflateRawSync(stored.data,{maxOutputLength:32*1024*1024});
  if(sha(bytes)!==stored.digest)throw fail('E_COGNITIVE_INTEGRITY','La política XI no coincide con su huella.');
  fs.writeFileSync(state,bytes,{mode:0o600});
  cells(state);
 }else{
  const blank=path.join(dir,'blank.rvp');
  run(runtime,['init',blank]);
  run(runtime,['run',program('policy-birth'),blank,state]);
  persist(db,state);
 }
 return {state,stored};
}
function configure(runtime,dir,state,values){
 const source=path.join(dir,'policy-frame.xi'),framed=path.join(dir,'policy-frame.rvp');
 const writes=values.map(([offset,value])=>{
  if(!Number.isInteger(value)||value<0||value>255)throw fail('E_COGNITIVE_FRAME','Byte de entrenamiento inválido.');
  return 'store8 '+(C+BigInt(offset))+' '+value;
 });
 fs.writeFileSync(source,'#!reverse-pc-machine-v1\n'+writes.join('\n')+'\nhalt\n',{mode:0o600});
 run(runtime,['run',source,state,framed]);
 return framed;
}
function features(db,{runtime,roles,dir,raw}){
 const frames=path.join(dir,'frames');fs.mkdirSync(frames,{mode:0o700});
 const pages=new NativePages(runtime,roles,frames);
 pages.validate(raw);
 const intent=pages.intent(raw);
 const previous=history(db);
 const reference=roles['context.rxe']?pages.context(raw,previous.map(row=>row.utterance)):null;
 // Never consider a malformed/ambiguous reference as an actual reference.
 const refers=reference!==null&&[1,2,5,9].includes(reference.mode);
 if(intent.id<0||intent.id>8)throw fail('E_COGNITIVE_INTENT','Intento XI no admitido.');
 return {intent,context:2*intent.id+Number(refers),memory_reference:refers,
  history_mode:reference?.mode??0};
}
export function cognitiveDecision(db,{runtime,roles,job,raw,feedback=null}){
 const dir=path.join(job,'cognitive-policy');fs.mkdirSync(dir,{mode:0o700});
 const {intent,context,memory_reference,history_mode}=features(db,{runtime,roles,dir,raw});
 const {state}=openModel(db,runtime,dir);
 let current=state,training=null;
 if(feedback!==null){
  if(!Number.isInteger(feedback.action)||feedback.action<0||feedback.action>3||
     !Number.isInteger(feedback.reward)||feedback.reward<0||feedback.reward>100)
   throw fail('E_COGNITIVE_FEEDBACK','La retroalimentación debe especificar ruta 0..3 y recompensa 0..100.');
  const reward=feedback.reward*100;
  const frame=configure(runtime,dir,current,[[1,context],[2,feedback.action],[3,reward%256],[4,Math.floor(reward/256)]]);
  const next=path.join(dir,'trained.rvp'),registered=output(run(runtime,['run',program('policy-update'),frame,next]));
  if(registered.length!==4)throw fail('E_COGNITIVE_RESULT','XI no devolvió el entrenamiento completo.');
  persist(db,next);current=next;
  training={context,action:registered[1],action_name:actions[registered[1]],
   q_value_q10000:registered[2],updates:registered[3],explicit:true};
 }
 const frame=configure(runtime,dir,current,[[1,context]]);
 const inferred=path.join(dir,'decision.rvp');
 const values=output(run(runtime,['run',program('policy-decide'),frame,inferred]));
 if(values.length!==4||values[0]!==context||values[1]<0||values[1]>3||values[2]<0||
    values[2]>10000||values[3]<0)throw fail('E_COGNITIVE_RESULT','XI devolvió una política incompatible.');
 return {
  engine:'XI contextual Q-learning (bandit, not quantum hardware)',
  intent:intent.name,p01_confidence:intent.confidence,context,memory_reference,history_mode,
  suggested_action:values[1],suggested_route:actions[values[1]],
  score_q10000:values[2],feedback_updates:values[3],
  training,applied:false,read_only:feedback===null
 };
}
export function cognitiveTurn(db,{runtime,roles,job,raw,feedback=null,language='es'}){
 const decision=cognitiveDecision(db,{runtime,roles,job,raw,feedback});
 const response=feedback===null
  ?(language==='en'?'Shadow policy (no effect on reply): ':'Política en observación (sin alterar respuestas): ')+
    decision.suggested_route+', puntuación Q='+decision.score_q10000+'/10000, '+
    (language==='en'?'annotated examples=':'ejemplos anotados=')+decision.feedback_updates+'.'
  :(language==='en'?'XI policy feedback saved: ':'Retroalimentación guardada por XI: ')+
    decision.training.action_name+', Q='+decision.training.q_value_q10000+
    '/10000, '+(language==='en'?'updates=':'actualizaciones=')+decision.training.updates+'.';
 return {ok:true,response,extension:'C12-cognitive-policy-XI',cognitive_shadow:decision,
  knowledge_read_only:feedback===null,original_training_preserved:true};
}
