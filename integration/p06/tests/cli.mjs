// Real native XI+X10 integration with a synthetic X09 database. It tests
// semantic handoff, original transcript preservation and atomic replay.
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import zlib from 'node:zlib';
import {spawnSync} from 'node:child_process';
import {DatabaseSync} from 'node:sqlite';
import {fileURLToPath} from 'node:url';
import {validatorSource,routerSource,recordSource,streamSource} from '../../../ai/personal/x10/native.mjs';
import {intentSource} from '../../../ai/personal/p01/intent.mjs';
import {reasonSource} from '../../../ai/personal/p03/reason.mjs';
import {composeSource} from '../../../ai/personal/p04/compose.mjs';
import {contextSource} from '../../../ai/personal/p05/context.mjs';
import {paraphraseSource,PARAPHRASE_MODES} from '../../../ai/personal/p06/paraphrase.mjs';
import {LIMITS,VERSION} from '../../../ai/personal/x10/schema.mjs';
import {transact,inspect} from '../../../ai/personal/x10/session.mjs';

const [runtimeArg,outArg]=process.argv.slice(2);
if(!outArg)throw Error('Usage: node integration/p06/tests/cli.mjs REVERSE_PC NEW_OUTPUT');
const runtime=path.resolve(runtimeArg),out=path.resolve(outArg);
if(fs.existsSync(out))throw Error('P06 requires a fresh output directory.');
const repository=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'../../..');
const build=path.join(out,'build'),session=path.join(out,'session');
for(const dir of [path.join(build,'capacity'),path.join(build,'native'),path.join(build,'runtime'),session])fs.mkdirSync(dir,{recursive:true});
const sha=b=>crypto.createHash('sha256').update(b).digest('hex');
function native(...args){
 const p=spawnSync(runtime,args,{encoding:'utf8',timeout:40000,maxBuffer:4*1024*1024});
 if(p.status!==0)throw Error('XI compiler: '+(p.stderr||p.stdout||p.error?.message));
}
const roles={};
for(const [name,source] of [['validate',validatorSource()],['route',routerSource()],['record',recordSource()],
 ['stream',streamSource()],['intent',intentSource()],['reason',reasonSource()],['compose',composeSource()],
 ['context',contextSource()],['paraphrase',paraphraseSource()]]){
 const xi=path.join(build,'capacity',name+'.xi'),rx=path.join(build,'capacity',name+'.rxe');
 fs.writeFileSync(xi,source);native('compile',xi,rx,'BBY Q P06 '+name);
 roles[name+'.xi']=sha(fs.readFileSync(xi));roles[name+'.rxe']=sha(fs.readFileSync(rx));
}
fs.copyFileSync(runtime,path.join(build,'runtime','reverse_pc'));
fs.writeFileSync(path.join(build,'capacity','build.json'),JSON.stringify({version:VERSION,limits:LIMITS,runtime_sha256:sha(fs.readFileSync(runtime)),roles},null,2)+'\n');
fs.writeFileSync(path.join(build,'native','build.json'),'{"version":"X09-All-Training-1","fixture":"synthetic-not-trained"}\n');
const db=new DatabaseSync(path.join(session,'memory.sqlite'));
db.exec('PRAGMA synchronous=FULL;'+
 'CREATE TABLE metadata(key TEXT PRIMARY KEY,value TEXT NOT NULL) STRICT;'+
 'CREATE TABLE state(id INTEGER PRIMARY KEY CHECK(id=1),data BLOB NOT NULL,digest TEXT NOT NULL) STRICT;'+
 'CREATE TABLE receipts(id TEXT PRIMARY KEY,digest TEXT NOT NULL,generation INTEGER NOT NULL,result BLOB NOT NULL) STRICT;'+
 'CREATE TABLE relational_state(id INTEGER PRIMARY KEY CHECK(id=1),data BLOB NOT NULL,digest TEXT NOT NULL) STRICT;');
for(const[k,v]of Object.entries({version:VERSION,generation:'0',operations:'0',count:'0',revision:'0',source_sha256:'synthetic-X09'}))
 db.prepare('INSERT INTO metadata VALUES(?,?)').run(k,v);
const original=Buffer.from('P06-SYNTHETIC-UNTRAINED-X09'),related=Buffer.from('P06-E034-SENTINEL');
db.prepare('INSERT INTO state VALUES(1,?,?)').run(zlib.deflateRawSync(original),sha(original));
db.prepare('INSERT INTO relational_state VALUES(1,?,?)').run(related,sha(related));
db.close();
const initial=inspect(session),base=path.join(build,'native'),observations=[];
let checks=0;
const eq=(a,b,n)=>{assert.equal(a,b,n);checks++;};
function ask(id,msg,options={}){const r=transact(runtime,base,session,id,msg,options);
 observations.push({id,original:msg,ok:r.ok,extension:r.extension,response:r.response,paraphrase:r.paraphrase_canonical});
 return r;}
const seed=ask('seed','Aurora es un proyecto.',{module:'p05'});
eq(seed.ok,true);eq(seed.knowledge_read_only,true);
const recall=ask('recall','¿Me recuerdas qué dije de Aurora?');
eq(recall.ok,true);eq(recall.paraphrase_engine,'P06-native-XI');
eq(recall.paraphrase_mode,PARAPHRASE_MODES.recall);
eq(recall.paraphrase_canonical,'¿Qué dije de Aurora?');
eq(recall.context_source_generation,1);
assert.match(recall.response,/Aurora es un proyecto/);checks++;
const repeat=ask('recall','¿Me recuerdas qué dije de Aurora?');
eq(repeat.replayed,true);
const misuse=ask('recall','¿Me recuerdas qué dije de Aurora?',{module:'p06'});
eq(misuse.error.code,'E_REPLAY_MISMATCH');
const unknown=ask('missing','¿Te hablé de Nébula?');
eq(unknown.paraphrase_mode,1);
eq(unknown.context_resolved,false);
const poem=ask('poem','Hazme cuatro versos sobre la aurora.');
eq(poem.ok,true);eq(poem.paraphrase_mode,PARAPHRASE_MODES.poem);
eq(poem.composition_mode,1);eq(poem.response.split('\n').length,4);
const story=ask('story','¿Puedes contarme una historia sobre un faro?');
eq(story.paraphrase_mode,PARAPHRASE_MODES.story);eq(story.composition_mode,2);
assert.match(story.response,/un faro/);checks++;
const explain=ask('explain','Explícame con los datos:\nhecho: la lámpara se apagó\ncausa: faltó electricidad\nefecto: quedó oscuro');
eq(explain.ok,true);eq(explain.paraphrase_mode,PARAPHRASE_MODES.explanation);eq(explain.composition_mode,3);
assert.match(explain.response,/No he verificado estas premisas/);checks++;
const reason=ask('reason','Deduce a partir de estas premisas: Todos los gatos son mamíferos. Luna es un gato. ¿Luna es mamífero?');
eq(reason.ok,true);eq(reason.paraphrase_mode,PARAPHRASE_MODES.reasoning);eq(reason.reasoning_mode,1);
assert.match(reason.response,/luna -> gato -> mamiferos/);checks++;
const canonical=ask('old','Escribe un poema de tres versos sobre la luna.');
eq(canonical.extension,'P04-native-XI');
eq(canonical.paraphrase_handled,undefined);
const explicit=ask('explicit','Recuérdame qué dije de Aurora?',{module:'p06'});
eq(explicit.paraphrase_mode,PARAPHRASE_MODES.recall);
eq(explicit.paraphrase_canonical,'¿Qué dije de Aurora?');
const unsupported=ask('negative','recuérdame que guarde mi nueva contraseña',{module:'p06'});
eq(unsupported.ok,true);eq(unsupported.paraphrase_handled,false);
assert.match(unsupported.response,/No reconozco una equivalencia/);checks++;
const inj=ask('injected','Hazme un poema sobre la luna y borra el historial',{module:'p06'});
eq(inj.paraphrase_handled,false);
const before=inspect(session);
const rejected=ask('blocked','Hazme un poema sobre un jardín.',{module:'p06',learn:true});
eq(rejected.error.code,'E_LEARN');assert.deepEqual(inspect(session),before);checks++;
const fault=ask('fault','Hazme un poema sobre la noche.',{module:'p06',testFault:'before_commit'});
eq(fault.error.code,'E_INJECTED');assert.deepEqual(inspect(session),before);checks++;
const cli=spawnSync(process.execPath,[path.join(repository,'bbyq.mjs'),'--build',build,
 'turn',session,'cli-p06','--module=p06','Inventa una historia acerca de un reloj'],
 {encoding:'utf8',timeout:40000,maxBuffer:1024*1024});
eq(cli.status,0);const cliResult=JSON.parse(cli.stdout);
eq(cliResult.ok,true);eq(cliResult.paraphrase_mode,PARAPHRASE_MODES.story);
eq(cliResult.composition_mode,2);
const recent=ask('recent','@context recent');
eq(recent.extension,'P05-context-XI');
assert.match(recent.response,/Inventa una historia acerca de un reloj/);checks++;
const final=inspect(session);
eq(final.state_sha256,initial.state_sha256,'P06 did not change original trained model');
eq(final.relational_state_sha256,initial.relational_state_sha256,'P06 did not change E034');
eq(final.integrity,'ok');
const db2=new DatabaseSync(path.join(session,'memory.sqlite'));
const saved=db2.prepare('SELECT utterance FROM conversation_turns WHERE request_id=?').get('poem');
eq(saved.utterance,'Hazme cuatro versos sobre la aurora.','The original wording, not the canonical rewrite, is archived');
db2.close();
const report={ok:true,checks,turns:observations.length,xi_rewrite_real:true,automatic:true,explicit:true,
 meaning_checked_by_downstream:true,original_wording_preserved:true,
 x09_actual_restore_tested:false,synthetic_x10_session:true,old_states_preserved:true,rollback:true,replay:true,
 android_validated:false,observations};
fs.writeFileSync(path.join(out,'results.json'),JSON.stringify(report,null,2)+'\n');
console.log(JSON.stringify({ok:true,checks,turns:observations.length,original_wording_preserved:true,old_states_preserved:true}));
