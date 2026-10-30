// Original guard assertions; version pins identify X02 and teaching remains the original X01 tool.
// Supplemental test for the final read-only preflight and teaching transport.
import fs from'node:fs';import path from'node:path';import crypto from'node:crypto';import assert from'node:assert/strict';import{execFileSync,spawnSync}from'node:child_process';
const[r,b,c,o]=process.argv.slice(2);if(!o)throw Error('usage: guard-test.mjs RUNTIME E038 FINAL_X01 NEW_OUTPUT');
const[runtime,base,caps,out]=[r,b,c,o].map(x=>path.resolve(x));if(fs.existsSync(out))throw Error('Use a fresh output');fs.mkdirSync(out,{recursive:true});
const here=path.resolve(path.dirname(new URL(import.meta.url).pathname),'../x01'),P=9050000000000000000n,hash=p=>crypto.createHash('sha256').update(fs.readFileSync(p)).digest('hex'),live=path.join(out,'live.rvp');let checks=0;
const eq=(a,b,l)=>{assert.deepEqual(a,b,l);checks++;};
eq(hash(path.join(caps,'BBY-Q.rxe')),'a660365e1216890ce859cf39eb21d376fc025f8ced10dbec4df17dcf11930691','final inference capsule identical to full-suite capsule');
eq(hash(path.join(caps,'model.rvp')),'028b035b9d8776e97cc3adaaae58f675b7fb7a3eab73039927f41ae13562f4e4','final seed identical to full-suite seed');
for(const dir of [base,caps]){fs.copyFileSync(path.join(dir,'model.rvp'),live);const prior=hash(live);execFileSync(runtime,['run',path.join(caps,'guard.xi'),live,live],{stdio:'pipe'});eq(hash(live),prior,'preflight read-only '+dir);}
const rows=[];
for(const offset of [0,16,17,272,600,3000,16383]){fs.copyFileSync(path.join(base,'model.rvp'),live);const setup=path.join(out,'setup.xi');fs.writeFileSync(setup,`#!reverse-pc-machine-v1\nstore8 ${P+BigInt(offset)} 77\nhalt\n`);execFileSync(runtime,['run',setup,live,live],{stdio:'pipe'});const prior=hash(live),target=path.join(out,`denied-${offset}.rvp`);
let p=spawnSync(runtime,['run',path.join(caps,'upgrade.xi'),live,target],{encoding:'utf8',timeout:30000});eq(p.status!==0,true,'occupied namespace refuses upgrade '+offset);eq(fs.existsSync(target),false,'upgrade publishes no file');eq(hash(live),prior,'original collision state retained');
p=spawnSync(process.execPath,[path.join(here,'teach.mjs'),runtime,path.join(caps,'learn.xi'),live,target,'vamos al paso que sigue','2','1'],{encoding:'utf8',timeout:30000});eq(p.status!==0,true,'occupied namespace refuses lesson BEFORE transport '+offset);eq(fs.existsSync(target),false,'lesson publishes no file');eq(hash(live),prior,'lesson retains occupied namespace');rows.push({offset,upgrade_rejected:true,teaching_rejected:true});}
fs.copyFileSync(path.join(caps,'model.rvp'),live);const a=path.join(out,'learned.rvp'),b2=path.join(out,'corrected.rvp');
execFileSync(process.execPath,[path.join(here,'teach.mjs'),runtime,path.join(caps,'learn.xi'),live,a,'dale al próximo paso','2','1'],{stdio:'pipe'});
execFileSync(process.execPath,[path.join(here,'teach.mjs'),runtime,path.join(caps,'learn.xi'),a,b2,'dale al próximo paso','3','1','1','2','1'],{stdio:'pipe'});
execFileSync(runtime,['app-turn',path.join(caps,'BBY-Q.rxe'),b2,b2,'es','@x tarea BBY Q'],{stdio:'pipe'});
const answer=execFileSync(runtime,['app-turn',path.join(caps,'BBY-Q.rxe'),b2,b2,'es','dale al próximo paso'],{encoding:'utf8'});eq(answer.includes('Quieres un resumen de BBY Q.'),true,'final guarded teaching and feedback affect native interpretation');
const report={checks,rows,final_app_and_seed_identical_to_full_suite:true,namespace_collision_rejected_before_transport:true,read_only_preflight:true,explicit_correction_verified:true};fs.writeFileSync(path.join(out,'results.json'),JSON.stringify(report,null,2)+'\n');console.log(JSON.stringify(report));
