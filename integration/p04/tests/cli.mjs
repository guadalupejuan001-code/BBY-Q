// Exercise actual X10 session transactions and bbyq.mjs command with P04
// while preserving X09 and E034 states. Synthetic seed, not X09 production.
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
import {composeSource,COMPOSE_MODES} from '../../../ai/personal/p04/compose.mjs';
import {LIMITS,VERSION} from '../../../ai/personal/x10/schema.mjs';
import {transact,inspect} from '../../../ai/personal/x10/session.mjs';

const [runtimeArg,outputArg]=process.argv.slice(2);
if(!outputArg)throw Error('Usage: cli.mjs REVERSE_PC NEW_OUTPUT_DIR');
const runtime=path.resolve(runtimeArg),out=path.resolve(outputArg),repo=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'../../..');
if(fs.existsSync(out))throw Error('P04 CLI evidence directory must be new.');
const build=path.join(out,'build'),session=path.join(out,'session');
for(const part of [path.join(build,'capacity'),path.join(build,'native'),path.join(build,'runtime'),session])fs.mkdirSync(part,{recursive:true});
const sha=bytes=>crypto.createHash('sha256').update(bytes).digest('hex');
function native(...args){
 const p=spawnSync(runtime,args,{encoding:'utf8',timeout:40000,maxBuffer:4*1024*1024});
 if(p.status!==0)throw Error('Native compiler '+(p.stderr||p.error?.message||p.stdout));
}
const roles={};
for(const [name,code]of [['validate',validatorSource()],['route',routerSource()],['record',recordSource()],['stream',streamSource()],['intent',intentSource()],['reason',reasonSource()],['compose',composeSource()]]){
 const src=path.join(build,'capacity',name+'.xi'),compiled=path.join(build,'capacity',name+'.rxe');
 fs.writeFileSync(src,code);native('compile',src,compiled,'BBY Q P04 '+name);
 roles[name+'.xi']=sha(fs.readFileSync(src));roles[name+'.rxe']=sha(fs.readFileSync(compiled));
}
fs.copyFileSync(runtime,path.join(build,'runtime','reverse_pc'));
fs.writeFileSync(path.join(build,'capacity','build.json'),JSON.stringify({version:VERSION,limits:LIMITS,runtime_sha256:sha(fs.readFileSync(runtime)),roles},null,2)+'\n');
fs.writeFileSync(path.join(build,'native','build.json'),'{"version":"X09-All-Training-1","fixture":"synthetic-invalid"}\n');
const db=new DatabaseSync(path.join(session,'memory.sqlite'));
db.exec("PRAGMA synchronous=FULL;"+
 'CREATE TABLE metadata(key TEXT PRIMARY KEY,value TEXT NOT NULL) STRICT;'+
 'CREATE TABLE state(id INTEGER PRIMARY KEY CHECK(id=1),data BLOB NOT NULL,digest TEXT NOT NULL) STRICT;'+
 'CREATE TABLE receipts(id TEXT PRIMARY KEY,digest TEXT NOT NULL,generation INTEGER NOT NULL,result BLOB NOT NULL) STRICT;'+
 'CREATE TABLE relational_state(id INTEGER PRIMARY KEY CHECK(id=1),data BLOB NOT NULL,digest TEXT NOT NULL) STRICT;');
for(const[k,v]of Object.entries({version:VERSION,generation:'0',operations:'0',count:'0',revision:'0',source_sha256:'synthetic'}))
 db.prepare('INSERT INTO metadata VALUES(?,?)').run(k,v);
const initial=Buffer.from('SYNTHETIC-NOT-TRAINED-X09'),related=Buffer.from('E034-DATA-PRESERVE');
db.prepare('INSERT INTO state VALUES(1,?,?)').run(zlib.deflateRawSync(initial),sha(initial));
db.prepare('INSERT INTO relational_state VALUES(1,?,?)').run(related,sha(related));
db.close();
const before=inspect(session),base=path.join(build,'native');
const ask=(id,text,options={})=>transact(runtime,base,session,id,text,{language:'es',...options});
let checks=0;
function eq(actual,expected){assert.equal(actual,expected);checks++;}
const poem='Escribe un poema de cuatro versos sobre una guitarra.';
const generated=ask('auto-poem',poem);
eq(generated.ok,true);
eq(generated.extension,'P04-native-XI');
eq(generated.composition_mode,COMPOSE_MODES.poem);
eq(generated.response.split('\n').length,4);
eq(generated.knowledge_read_only,true);
eq(ask('auto-poem',poem).replayed,true);
eq(ask('auto-poem',poem,{module:'p04'}).error.code,'E_REPLAY_MISMATCH');
const story=ask('story','Escribe un cuento de tres frases sobre una estrella.',{module:'p04'});
eq(story.composition_mode,COMPOSE_MODES.story);
eq(story.response.split('.').length-1,3);
const factual=ask('explain','Explica con datos:\nhecho: la lámpara se apagó\ncausa: faltó corriente\nefecto: quedó a oscuras');
eq(factual.extension,'P04-native-XI');
eq(factual.composition_mode,COMPOSE_MODES.grounded_explanation);
assert.match(factual.response,/La causa indicada es faltó corriente/);checks++;
const prior=inspect(session);
eq(ask('bad','Explica un misterio sin información',{module:'p04'}).error.code,'E_P04_FORMAT');
assert.deepEqual(inspect(session),prior);checks++;
eq(ask('long','a'.repeat(769),{module:'p04'}).error.code,'E_P04_SIZE');
assert.deepEqual(inspect(session),prior);checks++;
eq(ask('not-allowed',poem,{module:'p04',learn:true}).error.code,'E_LEARN');
assert.deepEqual(inspect(session),prior);checks++;
eq(ask('fault',poem,{module:'p04',testFault:'before_commit'}).error.code,'E_INJECTED');
assert.deepEqual(inspect(session),prior);checks++;
const cli=spawnSync(process.execPath,[path.join(repo,'bbyq.mjs'),'--build',build,'turn',session,'cli-new','--module=p04','escribe un poema de dos versos sobre la nieve'],{encoding:'utf8',timeout:40000,maxBuffer:1024*1024});
eq(cli.status,0);
const c=JSON.parse(cli.stdout);
eq(c.ok,true);eq(c.composition_mode,1);eq(c.response.split('\n').length,2);
const after=inspect(session);
eq(after.state_sha256,before.state_sha256);
eq(after.relational_state_sha256,before.relational_state_sha256);
eq(after.integrity,'ok');
const report={ok:true,checks,scope:'real X10 API, P01 intent, P04 XI and bbyq CLI; synthetic untrained X09 state',automatic:true,explicit:true,replay:true,rollback:true,read_only:true,p01_p02_p03_preserved:true,android_validated:false,full_x09_restoration_tested:false};
fs.writeFileSync(path.join(out,'results.json'),JSON.stringify(report,null,2)+'\n');
console.log(JSON.stringify(report));
