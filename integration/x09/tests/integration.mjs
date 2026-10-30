import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import assert from 'node:assert/strict';
import {chat} from '../../../ai/personal/x09/io.mjs';
import {initialize,transact} from '../../../ai/personal/x09/session.mjs';
import {migrateState} from '../../../ai/personal/x09/migrate.mjs';

const [rtArg,baseArg,oldArg,outArg]=process.argv.slice(2);
if(!outArg)throw Error('Usage: integration.mjs RUNTIME X09_NATIVE X08_STATE NEW_EVIDENCE_DIR');
const [runtime,base,old,out]=[rtArg,baseArg,oldArg,outArg].map(p=>path.resolve(p));
if(fs.existsSync(out))throw Error('Choose fresh evidence output.');
fs.mkdirSync(out,{recursive:true});
const seed=path.join(base,'model.rvp'),sha=p=>crypto.createHash('sha256').update(fs.readFileSync(p)).digest('hex');
const seedBefore=sha(seed),oldBefore=sha(old),rows=[];
function save(){fs.writeFileSync(path.join(out,'transcripts.json'),JSON.stringify(rows,null,2)+'\n');}
function ask(name,input,{language,extension,contains,exact,executed}={}){
  const file=path.join(out,name+'.rvp'),t=performance.now(),result=chat(runtime,base,seed,file,input,{language});
  rows.push({name,input:typeof input==='string'?input:input.toString('hex'),...result,milliseconds:performance.now()-t});save();
  assert.equal(result.ok,true,JSON.stringify(result.error));
  if(extension)assert.equal(result.extension,extension,name);
  if(contains)for(const term of contains)assert.ok(result.response.includes(term),name+': '+result.response);
  if(exact)assert.equal(result.response,exact);
  if(executed){assert.equal(result.executed,true);assert.equal(result.verified,true);assert.deepEqual(result.result.values,executed);}
  console.log(JSON.stringify({name,ok:true,extension:result.extension,response:result.response.slice(0,200)}));
  return result;
}
ask('dictionary-en','@lex money',{language:'en',extension:'dictionary',contains:['money','13250542-n']});
ask('dictionary-es','@lex dinero',{language:'es',extension:'dictionary',contains:['dinero']});
ask('campaign-alternative','edificio incluye libro?',{extension:'campaign',contains:['edificio','libro']});
ask('campaign-primary','cuarto contiene llave?',{extension:'campaign',contains:['cuarto','llave']});
ask('arithmetic','calcula 17 + 25',{exact:'El resultado es 42.'});
ask('babylon','consulta: nomasir caballo',{contains:['viajeros asociados','clason-F004-B']});
ask('tools','Escribe y ejecuta en XI un programa que sume 637 y 284.',{executed:[921]});

const malformed=chat(runtime,base,seed,path.join(out,'invalid.rvp'),Buffer.from([0xc3,0x28]));
assert.equal(malformed.ok,false);assert.equal(malformed.error.code,'E_UTF8');assert.equal(fs.existsSync(path.join(out,'invalid.rvp')),false);
rows.push({name:'invalid-utf8',...malformed});save();

const migrated=path.join(out,'migrated.rvp'),migration=migrateState(runtime,base,old,migrated);
assert.equal(migration.previous_training_preserved,true);
const repeated=migrateState(runtime,base,migrated,path.join(out,'migrated-again.rvp'));
assert.equal(repeated.idempotent,true);
rows.push({name:'migration',...migration},{name:'migration-idempotent',...repeated});save();

const session=path.join(out,'session');initialize(session,base,old);
const upgrade=transact(runtime,base,session,'upgrade-x09','',{operation:'migrate'});assert.equal(upgrade.ok,true,JSON.stringify(upgrade));
const one=transact(runtime,base,session,'query-1','@lex money',{language:'en'});assert.equal(one.ok,true,JSON.stringify(one));
assert.equal(one.extension,'dictionary');
const again=transact(runtime,base,session,'query-1','@lex money',{language:'en'});assert.equal(again.replayed,true);assert.equal(again.generation,one.generation);assert.equal(again.response,one.response);
const changedLanguage=transact(runtime,base,session,'query-1','@lex money',{language:'es'});assert.equal(changedLanguage.ok,false);assert.equal(changedLanguage.error.code,'E_REPLAY_MISMATCH');
const campaign=transact(runtime,base,session,'query-2','recinto incluye armario?');assert.equal(campaign.ok,true,JSON.stringify(campaign));assert.equal(campaign.extension,'campaign');
rows.push({name:'session-upgrade',...upgrade},{name:'session-dictionary',...one},{name:'session-replay',...again},{name:'session-language-binding',...changedLanguage},{name:'session-campaign',...campaign});save();
assert.equal(sha(seed),seedBefore,'canonical seed unchanged');assert.equal(sha(old),oldBefore,'original X08 state unchanged');
const summary={ok:true,chat_cases:7,invalid_utf8_rejected:true,migration_previous_training_preserved:true,migration_idempotent:true,session_upgrade:true,replay_idempotent:true,request_language_bound:true,both_extensions_in_same_session:true,seed_preserved:true,original_x08_preserved:true,observations:rows.length};
fs.writeFileSync(path.join(out,'results.json'),JSON.stringify(summary,null,2)+'\n');
console.log(JSON.stringify(summary));
