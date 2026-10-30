import fs from 'node:fs';
import path from 'node:path';
import zlib from 'node:zlib';
import assert from 'node:assert/strict';
import {execFileSync,spawnSync} from 'node:child_process';
import {service} from './service.mjs';
import {decodeCampaign} from './build.mjs';
import {readState,byte,readBytes,sha256} from './state.mjs';
import {BASE as B,PRIMARY,SCRATCH,SCRATCH_BYTES,SOURCE_ARCHIVE,REGION_END,HANDLED,STATUS,WITNESS,PROOF,F,C,ID_OFFSET} from './schema.mjs';

const[runtimeArg,baselineArg,alternateArg,assetsArg,outArg]=process.argv.slice(2);
if(!outArg)throw Error('Usage: test.mjs RUNTIME BASELINE.rvp[.gz] ALTERNATE.rvp ASSETS NEW_OUTPUT_DIR');
const[runtime,baseline,alternate,assets,out]=[runtimeArg,baselineArg,alternateArg,assetsArg,outArg].map(x=>path.resolve(x));
if(fs.existsSync(out))throw Error('Choose a new evidence directory');fs.mkdirSync(out,{recursive:true});
const manifest=JSON.parse(fs.readFileSync(path.join(assets,'campaign-build.json'))),fixture=decodeCampaign(alternate),results=[];
const run=(program,input,output)=>execFileSync(runtime,['run',program,input,output],{encoding:'utf8',timeout:30000,maxBuffer:8*1024*1024});
const foreignEqual=(a,b,allowText=false)=>{const allowed=p=>(p>=B&&p<REGION_END)||(allowText&&(p===F+2n||p===F+3n));for(const[p,v]of a.cells)if(!allowed(p))assert.equal(byte(b,p),v,'foreign original cell '+p);for(const[p,v]of b.cells)if(!allowed(p))assert.equal(byte(a,p),v,'foreign new cell '+p);};
const stdoutText=text=>new TextDecoder('utf-8',{fatal:true}).decode(Buffer.from(text.split('\n').filter(x=>x.startsWith('{')).map(JSON.parse).filter(x=>x.type==='register'&&x.register==='r14').map(x=>x.value)));
function stage(input,output,writes,name){const file=path.join(out,name+'.xi');fs.writeFileSync(file,'#!reverse-pc-machine-v1\n'+writes.map(([a,v])=>'store8 '+a+' '+v).join('\n')+'\nhalt\n');run(file,input,output);}
function inputFor(message,number){const p=path.join(out,'query-'+number+'.rvp'),raw=Buffer.from(message),writes=[[F+2n,1],[F+3n,0],[F+4n,1],[F+8n,raw.length&255],[F+9n,raw.length>>>8]];for(const[i,v]of raw.entries())writes.push([C+BigInt(i),v]);stage(installed,p,writes,'input-'+number);return p;}

const baselineFile=path.join(out,'before.rvp');let baselineBytes=fs.readFileSync(baseline);if(baseline.endsWith('.gz'))baselineBytes=zlib.gunzipSync(baselineBytes);fs.writeFileSync(baselineFile,baselineBytes);
const baselineHash=sha256(fs.readFileSync(baseline)),alternateHash=sha256(fs.readFileSync(alternate));
const installed=path.join(out,'installed.rvp'),installOut=run(path.join(assets,'campaign-migrate.rxe'),baselineFile,installed),before=readState(baselineFile),after=readState(installed);
assert.deepEqual(installOut.split('\n').filter(x=>x.startsWith('{')).map(JSON.parse).filter(x=>x.type==='register').map(x=>[x.register,x.value]),[['r0',0]]);
foreignEqual(before,after);assert.equal(byte(after,B+17n),fixture.concepts+ID_OFFSET);
for(const record of fixture.vocabulary){const expected=Buffer.from(record.bytes);expected[1]=record.new_id;assert.deepEqual(readBytes(after,B+1000n+BigInt(record.slot*16),16),expected);}
for(const record of fixture.assertions)assert.deepEqual([...readBytes(after,B+3000n+BigInt(record.slot*8),8)],record.remapped);
for(let i=0;i<4096;i++)assert.equal(byte(after,SOURCE_ARCHIVE+BigInt(i)),byte(fixture.s,PRIMARY+BigInt(i)),'archived original E009 byte '+i);
results.push({name:'native_install_complete_and_foreign_state_preserved',ok:true,word_records:fixture.words,concept_records:fixture.concepts,fact_records:fixture.facts,raw_E009_image_bytes_compared:4096,before_sha256:before.sha256,after_sha256:after.sha256});
const second=path.join(out,'idempotent.rvp');run(path.join(assets,'campaign-migrate.rxe'),installed,second);assert.equal(sha256(fs.readFileSync(second)),after.sha256);results.push({name:'idempotent_install_byte_exact',ok:true});

// A guard failure must not overwrite an existing destination or the supplied source.
const occupied=path.join(out,'occupied.rvp');stage(baselineFile,occupied,[[B+1000n,99]],'occupy');const occupiedHash=sha256(fs.readFileSync(occupied)),refused=path.join(out,'refused-existing.rvp');fs.copyFileSync(baselineFile,refused);const refusedHash=sha256(fs.readFileSync(refused)),failure=spawnSync(runtime,['run',path.join(assets,'campaign-migrate.rxe'),occupied,refused],{encoding:'utf8',timeout:30000});assert.notEqual(failure.status,0);assert.equal(sha256(fs.readFileSync(occupied)),occupiedHash);assert.equal(sha256(fs.readFileSync(refused)),refusedHash);results.push({name:'occupied_region_refusal_preserves_input_and_existing_destination',ok:true,error:failure.stderr.trim()});

// Remove only derived flags in a private state, then recompute with the original XI induction.
const reset=path.join(out,'reset-policy.rvp'),policyWrites=[];for(const row of fixture.entities)for(const offset of[2000n,2100n,2150n])policyWrites.push([B+offset+BigInt(row.new_id),0]);stage(installed,reset,policyWrites,'reset-policy');const recalibrated=path.join(out,'recalibrated.rvp');run(path.join(assets,'campaign-calibrate.rxe'),reset,recalibrated);const calibrated=readState(recalibrated);for(const row of fixture.entities){assert.equal(byte(calibrated,B+2000n+BigInt(row.new_id)),row.transitive);assert.equal(byte(calibrated,B+2100n+BigInt(row.new_id)),row.supporting_paths);assert.equal(byte(calibrated,B+2150n+BigInt(row.new_id)),row.contradicting_paths);}foreignEqual(after,calibrated);results.push({name:'XI_calibration_reconstructs_generalization_and_counterexample_veto',ok:true,concepts:fixture.entities});

assert.equal(fixture.assertions.some(x=>x.original[0]===4&&x.original[1]===6&&x.original[2]===2),false,'held-out building-to-cabinet answer must not be a stored direct fact');
const cases=[
 {message:'edificio incluye armario',expected:'Sí: edificio incluye armario (vía sala).',status:1,proof:2,witness:33,held_out:true},
 {message:'¿EDIFICIO alberga LIBRO?',expected:'Sí: edificio incluye libro (vía sala).',status:1,proof:2,witness:33,held_out:true},
 {message:'recinto incluye armario',expected:'Sí: sala incluye armario.',status:1,proof:1,witness:0},
 {message:'cuarto contiene llave',expected:'Sí: cuarto contiene llave (vía caja).',status:1,proof:2,witness:1},
 {message:'ojo mira armario',expected:'No: ojo mira armario.',status:2,proof:1,witness:0},
 {message:'edificio mira armario',expected:'No tengo evidencia suficiente para esa microoración.',status:3,proof:0,witness:0},
 {message:'cuarto incluye libro',expected:'No tengo evidencia suficiente para esa microoración.',status:3,proof:0,witness:0},
 {message:'hazme una pizza',handled:false}
];
for(const[i,test]of cases.entries()){
 const input=inputFor(test.message,i),initial=readState(input),sourceHash=initial.sha256,start=performance.now();const outcome=service(runtime,assets,input);if(test.handled===false){assert.equal(outcome.handled,false);assert.equal(sha256(fs.readFileSync(input)),sourceHash);results.push({name:'unhandled_falls_back_without_mutation',ok:true,message:test.message,milliseconds:performance.now()-start});}
 else{assert.equal(outcome.handled,true);const text=stdoutText(outcome.jsonl),current=readState(input);assert.equal(text,test.expected);assert.equal(byte(current,HANDLED),1);assert.equal(byte(current,STATUS),test.status);assert.equal(byte(current,PROOF),test.proof);assert.equal(byte(current,WITNESS),test.witness);foreignEqual(initial,current,true);for(let j=0;j<SCRATCH_BYTES;j++)assert.equal(byte(current,SCRATCH+BigInt(j)),0);results.push({name:'native_microquery_after_persisted_reload',ok:true,...test,response:text,new_native_process:true,milliseconds:performance.now()-start,original_state_sha256:sourceHash,result_state_sha256:current.sha256});}
 console.log(JSON.stringify({completed:i+1,total:cases.length,message:test.message,ok:true}));
}
assert.equal(sha256(fs.readFileSync(baseline)),baselineHash);assert.equal(sha256(fs.readFileSync(alternate)),alternateHash);
const evidence={version:'X09-E009-Campaign-Test-1',ok:true,scope:'Native XI migration, generic data-driven microquery dispatch and calibration; Linux only. Each native run loads a persisted RVPC2 state in a fresh process. No arbitrary conversation claim.',baseline_state_sha256:before.sha256,source_campaign_sha256:fixture.s.sha256,installed_state_sha256:after.sha256,roles:manifest.roles,results};fs.writeFileSync(path.join(out,'results.json'),JSON.stringify(evidence,null,2)+'\n');console.log(JSON.stringify({ok:true,checks:results.length,evidence:path.join(out,'results.json')}));
