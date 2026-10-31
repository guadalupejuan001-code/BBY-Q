// P02: verified, separate E034 XI/Ether skill installed beside the preserved X09/X10 state.
// This module transports bytes; it never infers relations, selects evidence, or generates answers.
import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import zlib from 'node:zlib';
import {spawnSync} from 'node:child_process';
import {fileURLToPath} from 'node:url';
import {cells,readNumber,run,fail} from '../x10/pages.mjs';

const here=path.dirname(fileURLToPath(import.meta.url));
const checkpoint=path.resolve(here,'../../checkpoints/e034/composition-model.rvp.gz.b64');
const B=8400000000000000000n;
export const CAPSULE_SHA='a0edbe6122beb5ab57d0e2dbd60c26524bc946737806eb71f2ed133fde068a28';
export const LEARNED_SHA='876d3f2a82698e9582f17043028d9a75b454e4b5ebaf7cc5949b65a5bac58a10';
export const E034_VERSION='E034-Relational-Composition-1-dev';
export const MAX_E034_TEXT=240; // Older E034 mailbox, independent of X10 1-MiB page limit.
const sha=bytes=>crypto.createHash('sha256').update(bytes).digest('hex');
const modelFile=build=>path.join(path.resolve(build),'relational','model.rvp.gz');
const capsuleFile=build=>path.join(path.resolve(build),'relational','composed.rxe');
const manifestFile=build=>path.join(path.resolve(build),'relational','manifest.json');

export function learnedSeed(){
 const text=fs.readFileSync(checkpoint,'utf8').trim();
 const zipped=Buffer.from(text,'base64');
 if(zipped.toString('base64')!==text)throw fail('E_E034_MODEL','Codificación E034 inválida.');
 const raw=zlib.gunzipSync(zipped,{maxOutputLength:4*1024*1024});
 if(sha(raw)!==LEARNED_SHA)throw fail('E_E034_MODEL','El modelo E034 no corresponde al checkpoint auditado.');
 if(raw.toString('ascii',0,5)!=='RVPC2')throw fail('E_E034_MODEL','Estado RVPC2 E034 incompatible.');
 return {raw,zipped};
}

function capsuleBytes(archive){
 const source=path.resolve(archive);
 if(!fs.existsSync(source))throw fail('E_E034_SOURCE','No existe el archivo E034 suministrado.');
 let bytes;
 if(source.endsWith('.zip')){
  const p=spawnSync('unzip',['-p',source,'composition/composed.rxe'],{encoding:null,maxBuffer:3*1024*1024,timeout:30000});
  if(p.status!==0)throw fail('E_E034_SOURCE','No se pudo recuperar composition/composed.rxe del archivo E034.');
  bytes=p.stdout;
 }else bytes=fs.readFileSync(source);
 if(sha(bytes)!==CAPSULE_SHA)throw fail('E_E034_CAPSULE','La cápsula E034 no corresponde al código probado.');
 return bytes;
}
export function verifyRelational(build){
 const manifest=JSON.parse(fs.readFileSync(manifestFile(build),'utf8'));
 if(manifest.version!==E034_VERSION||manifest.capsule_sha256!==CAPSULE_SHA||manifest.seed_sha256!==LEARNED_SHA)
  throw fail('E_E034_BUILD','Versión E034 incompatible.');
 if(sha(fs.readFileSync(capsuleFile(build)))!==CAPSULE_SHA)
  throw fail('E_E034_BUILD','La cápsula E034 instalada fue alterada.');
 const seed=zlib.gunzipSync(fs.readFileSync(modelFile(build)),{maxOutputLength:4*1024*1024});
 if(sha(seed)!==LEARNED_SHA)throw fail('E_E034_BUILD','La memoria original E034 fue alterada.');
 return {app:capsuleFile(build),seed,manifest};
}
export function installRelational(build,archive){
 build=path.resolve(build);
 if(!fs.existsSync(path.join(build,'capacity','build.json'))||!fs.existsSync(path.join(build,'native','build.json')))
  throw fail('E_E034_PARENT','Se necesita la entrega X10 verificada antes de habilitar E034.');
 const target=path.join(build,'relational');
 if(fs.existsSync(target))return {ok:true,alreadyInstalled:true,...verifyRelational(build).manifest};
 const capsule=capsuleBytes(archive),{raw,zipped}=learnedSeed();
 const stage=fs.mkdtempSync(path.join(build,'.p02-relational-'));
 try{
  fs.writeFileSync(path.join(stage,'composed.rxe'),capsule,{mode:0o600});
  fs.writeFileSync(path.join(stage,'model.rvp.gz'),zipped,{mode:0o600});
  const manifest={version:E034_VERSION,capsule_sha256:sha(capsule),seed_sha256:sha(raw),parent:'X10 + X09 unmodified',
   original_source:'ai/releases/e027..e034',seed_kind:'learned E034 prior to examination facts',
   isolation:'SQLite transactional sidecar; no RVPC2 overwrite',android_validated:false};
  fs.writeFileSync(path.join(stage,'manifest.json'),JSON.stringify(manifest,null,2)+'\n',{mode:0o600});
  fs.renameSync(stage,target);
  verifyRelational(build);
  return {ok:true,installed:true,...manifest};
 }finally{if(fs.existsSync(stage))fs.rmSync(stage,{recursive:true,force:true});}
}
function sameKnowledge(before,after){
 // A query's only persistent projection is E034's exact two-byte typed referent.
 // Everything else, including a possible automatic natural-language fact write,
 // is discarded. Compare the published map, not only event counters.
 const a=cells(before),b=cells(after);
 const allowed=new Set([B+12n,B+13n].map(String));
 for(const key of new Set([...a.keys(),...b.keys()]))
  if(!allowed.has(String(key))&&(a.get(key)||0)!==(b.get(key)||0))return false;
 return true;
}
function projectReadOnly(runtime,job,before,candidate){
 const fresh=cells(candidate),old=cells(before),focus=[B+12n,B+13n];
 if(focus.every(k=>(fresh.get(k)||0)===(old.get(k)||0)))return before;
 const source=path.join(job,'focus-only.xi'),published=path.join(job,'focus-only.rvp');
 fs.writeFileSync(source,'#!reverse-pc-machine-v1\n'+focus.map(a=>'store8 '+a+' '+(fresh.get(a)||0)).join('\n')+'\nhalt\n',{mode:0o600});
 run(runtime,['run',source,before,published]);
 if(!sameKnowledge(before,published))throw fail('E_E034_READ_ONLY','Una consulta intentó modificar memoria fuera de la referencia tipada.');
 return published;
}
export function relationalTurn(db,{runtime,build,job,raw,language='es',learn=false}){
 if(language!=='es'&&language!=='en')throw fail('E_LANGUAGE','Idioma E034 incompatible.');
 if(raw.length<1||raw.length>MAX_E034_TEXT)throw fail('E_E034_SIZE','El módulo E034 admite mensajes de hasta 240 bytes.');
 if(raw.includes(0))throw fail('E_E034_TEXT','E034 no permite bytes NUL.');
 const text=new TextDecoder('utf-8',{fatal:true}).decode(raw);
 const {app,seed}=verifyRelational(build);
 // CREATE/INSERT are inside the caller's BEGIN IMMEDIATE transaction and
 // therefore roll back if the turn does not finish.
 db.exec('CREATE TABLE IF NOT EXISTS relational_state(id INTEGER PRIMARY KEY CHECK(id=1),data BLOB NOT NULL,digest TEXT NOT NULL) STRICT');
 db.prepare('INSERT OR IGNORE INTO relational_state(id,data,digest) VALUES(1,?,?)')
   .run(zlib.gzipSync(seed,{level:6}),LEARNED_SHA);
 const stored=db.prepare('SELECT data,digest FROM relational_state WHERE id=1').get();
 const original=zlib.gunzipSync(stored.data,{maxOutputLength:4*1024*1024});
 if(sha(original)!==stored.digest)throw fail('E_E034_STATE','La memoria E034 no coincide con su hash.');
 const input=path.join(job,'e034-input.rvp'),next=path.join(job,'e034-output.rvp');
 fs.writeFileSync(input,original,{mode:0o600});
 const p=spawnSync(runtime,['app-turn',app,input,next,language,text],
   {encoding:'utf8',timeout:60000,maxBuffer:4*1024*1024});
 if(p.status!==0||!fs.existsSync(next))
  throw fail('E_E034_NATIVE','No se pudo completar la ejecución nativa E034: '+(p.stderr||p.error?.message||'sin estado publicado').slice(0,400));
 const candidate=fs.readFileSync(next);
 if(candidate.subarray(0,5).toString()!=='RVPC2')throw fail('E_E034_STATE','E034 generó un estado inválido.');
 const finalized=learn?next:projectReadOnly(runtime,job,input,next),written=fs.readFileSync(finalized);
 db.prepare('UPDATE relational_state SET data=?,digest=? WHERE id=1')
  .run(zlib.gzipSync(written,{level:6}),sha(written));
 let response=p.stdout.trimEnd();
 // A legacy acknowledgement must never claim a fact was saved when the
 // read-only projection discarded its writes.
 if(!learn&&/^(Registré esa relación\.|Registré esa afirmación\.|Recorded that relation\.|I recorded that statement\.|CTX guardado.*|CTX vaciado\.|Aprendí.*|I learned.*)$/u.test(response))
  response='Consulta de solo lectura: no se guardó ni borró información. Usa --learn para autorizar cambios.';
 return {ok:true,response,extension:'E034-isolated-XI',relational_checkpoint:LEARNED_SHA,
  relational_state_sha256:sha(written),learn_requested:learn,
  knowledge_write_enabled:learn,typed_focus_persisted:!learn,
  original_x09_x10_unchanged:true};
}
