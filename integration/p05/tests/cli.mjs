// Exercise actual X10 sessions with a bounded P05 conversation index.
// Synthetic X09 state: verifies transport, not a production restored X09 model.
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
import {LIMITS,VERSION} from '../../../ai/personal/x10/schema.mjs';
import {transact,inspect} from '../../../ai/personal/x10/session.mjs';

const [runtimeArg,outArg]=process.argv.slice(2);
if(!outArg)throw Error('Usage: cli.mjs REVERSE_PC NEW_OUTPUT');
const runtime=path.resolve(runtimeArg),out=path.resolve(outArg);
if(fs.existsSync(out))throw Error('Use a new evidence directory.');
const repo=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'../../..'),build=path.join(out,'build'),session=path.join(out,'session');
for(const dir of [path.join(build,'capacity'),path.join(build,'native'),path.join(build,'runtime'),session])fs.mkdirSync(dir,{recursive:true});
const sha=b=>crypto.createHash('sha256').update(b).digest('hex');
function native(...args){const p=spawnSync(runtime,args,{encoding:'utf8',timeout:40000,maxBuffer:4*1024*1024});if(p.status!==0)throw Error('Native XI error '+(p.stderr||p.stdout||p.error?.message));}
const roles={};
for(const[name,code]of [['validate',validatorSource()],['route',routerSource()],['record',recordSource()],['stream',streamSource()],['intent',intentSource()],['reason',reasonSource()],['compose',composeSource()],['context',contextSource()]]){
 const xi=path.join(build,'capacity',name+'.xi'),rx=path.join(build,'capacity',name+'.rxe');
 fs.writeFileSync(xi,code);native('compile',xi,rx,'BBY Q P05 '+name);
 roles[name+'.xi']=sha(fs.readFileSync(xi));roles[name+'.rxe']=sha(fs.readFileSync(rx));
}
fs.copyFileSync(runtime,path.join(build,'runtime','reverse_pc'));
fs.writeFileSync(path.join(build,'capacity','build.json'),JSON.stringify({version:VERSION,limits:LIMITS,runtime_sha256:sha(fs.readFileSync(runtime)),roles},null,2)+'\n');
fs.writeFileSync(path.join(build,'native','build.json'),'{"version":"X09-All-Training-1","fixture":"untrained-X09-state"}\n');
const db=new DatabaseSync(path.join(session,'memory.sqlite'));
db.exec('PRAGMA synchronous=FULL;'+
 'CREATE TABLE metadata(key TEXT PRIMARY KEY,value TEXT NOT NULL) STRICT;'+
 'CREATE TABLE state(id INTEGER PRIMARY KEY CHECK(id=1),data BLOB NOT NULL,digest TEXT NOT NULL) STRICT;'+
 'CREATE TABLE receipts(id TEXT PRIMARY KEY,digest TEXT NOT NULL,generation INTEGER NOT NULL,result BLOB NOT NULL) STRICT;'+
 'CREATE TABLE relational_state(id INTEGER PRIMARY KEY CHECK(id=1),data BLOB NOT NULL,digest TEXT NOT NULL) STRICT;');
for(const[k,v]of Object.entries({version:VERSION,generation:'0',operations:'0',count:'0',revision:'0',source_sha256:'synthetic'}))
 db.prepare('INSERT INTO metadata VALUES(?,?)').run(k,v);
const original=Buffer.from('SYNTHETIC-X09-NOT-A-TRAINED-MODEL'),related=Buffer.from('P02-PRESERVED-SIDECAR');
db.prepare('INSERT INTO state VALUES(1,?,?)').run(zlib.deflateRawSync(original),sha(original));
db.prepare('INSERT INTO relational_state VALUES(1,?,?)').run(related,sha(related));
db.close();
const initial=inspect(session),base=path.join(build,'native'),ask=(id,text,options={})=>transact(runtime,base,session,id,text,options);
let checks=0,observations=[];
function ok(condition,label){assert.ok(condition,label);checks++;}
function eq(a,b,label){assert.equal(a,b,label);checks++;}
function askOk(id,text,options={}){const r=ask(id,text,options);assert.equal(r.ok,true,JSON.stringify({id,error:r.error}));observations.push({id,input:text,output:r.response,mode:r.context_mode,extension:r.extension,source:r.context_source_generation});return r;}
eq(inspect(session).conversation_index_turns,0,'empty index');
const greeting=askOk('luna','Luna es un gato.',{module:'p05'});
eq(greeting.extension,'P05-context-XI','context fixture recorded');
eq(inspect(session).conversation_index_turns,1,'durable user text');
const fromName=askOk('named','¿Qué dije sobre Luna?');
eq(fromName.context_mode,1,'named XI lookup');eq(fromName.context_source_generation,1,'provenance');
ok(fromName.response.includes('Luna es un gato.'),'exact user quote');
const fromPronoun=askOk('pronoun','¿Y qué dije de ella?');
eq(fromPronoun.context_mode,2,'immediate pronoun admitted');eq(fromPronoun.context_source_generation,1);
const answer=askOk('answer','@context answer');
ok(answer.response.includes('Mensaje incorporado'),'previous assistant answer available');
const latest=askOk('latest','@context last');
ok(latest.response.includes('Luna es un gato.'),'last statement');
const creative=askOk('poem','Escribe un poema de cuatro versos sobre una guitarra.');
eq(creative.extension,'P04-native-XI','legacy P04 still runs');
eq(inspect(session).conversation_index_turns,2,'normal creative turn indexed');
const theme=askOk('theme','Aurora es un proyecto.',{module:'p05'});
eq(inspect(session).conversation_index_turns,3);
const ref=askOk('context-ref','¿Qué dije de eso?');
eq(ref.context_mode,2);ok(ref.response.includes('Aurora es un proyecto.'),'fresh topic');
const switchTopic=askOk('switch-topic','Cambiemos de tema.',{module:'p05'});
const ambiguous=askOk('ambiguous','¿Qué dije de ella?');
eq(ambiguous.context_mode,4);eq(ambiguous.context_resolved,false);
const oldNamed=askOk('older-named','¿Qué dije sobre Luna?');
ok(oldNamed.response.includes('Luna es un gato.'),'named recall crosses topic switch');
const list=askOk('recent','@context recent');
ok(list.response.includes('Aurora es un proyecto.'),'recent context view');
const status=askOk('status','@context status');
ok(status.response.includes('4 turnos'),'status tracks index');
const old=inspect(session);
const bad=ask('failed','Nina es una artista.',{module:'p05',testFault:'before_commit'});
eq(bad.ok,false);eq(bad.error.code,'E_INJECTED');assert.deepEqual(inspect(session),old);checks++;
const duplicate=ask('theme','Aurora es un proyecto.',{module:'p05'});
eq(duplicate.replayed,true);
eq(inspect(session).conversation_index_turns,4);
const mismatch=ask('theme','Aurora es un proyecto. Cambié.',{module:'p05'});
eq(mismatch.error.code,'E_REPLAY_MISMATCH');
const cli=spawnSync(process.execPath,[path.join(repo,'bbyq.mjs'),'--build',build,'turn',session,'cli-read','--module=p05','¿Qué dije sobre Aurora?'],
 {encoding:'utf8',timeout:30000,maxBuffer:1024*1024});
eq(cli.status,0,'CLI exit');const cliOut=JSON.parse(cli.stdout);
eq(cliOut.ok,true);ok(cliOut.response.includes('Aurora es un proyecto.'),'CLI exact recall');
const cleared=askOk('clear','@context clear');
eq(cleared.context_cleared,4);
eq(inspect(session).conversation_index_turns,0,'conversation index cleared');
ok(cleared.response.includes('comprobantes históricos'),'clear leaves receipts');
const afterClear=askOk('after-clear','¿Qué dije antes?');
eq(afterClear.context_mode,3,'does not invent deleted index content');
eq(afterClear.context_resolved,false);
const replayClear=ask('clear','@context clear');eq(replayClear.replayed,true);
eq(inspect(session).conversation_index_turns,0,'replay cannot erase or add anything');
for(let i=0;i<40;i++)askOk('bounded-'+i,'Orion'+String(i)+' es un módulo.',{module:'p05'});
eq(inspect(session).conversation_index_turns,32,'bounded retention');
const window=askOk('recent-window','@context recent');
ok(window.response.includes('Orion39'),'newest retained');
const beyond=askOk('outside-window','¿Qué dije de Orion0?');
eq(beyond.context_mode,3,'oldest outside index is unavailable');
eq(inspect(session).state_sha256,initial.state_sha256,'X09 untouched');
eq(inspect(session).relational_state_sha256,initial.relational_state_sha256,'E034 untouched');
eq(inspect(session).integrity,'ok','SQLite remains consistent');
const report={ok:true,checks,turns:observations.length,original_x09_training_used:false,
 source:'native XI context selector + actual X10 transactor and bbyq.mjs with synthetic X09 state',
 automatic_recall:true,explicit_archive:true,bounded_32:true,source_turns:true,
 no_unrequested_learning:true,rollback:true,replay:true,clear_index_only:true,android_validated:false,
 rows:observations};
fs.writeFileSync(path.join(out,'results.json'),JSON.stringify(report,null,2)+'\n');
console.log(JSON.stringify({ok:true,checks,turns:observations.length,rollback:true,replay:true,max_turns:32,main_state_untouched:true}));
