import fs from 'node:fs';
import path from 'node:path';
import assert from 'node:assert/strict';
import {initialize,transact,inspect} from '../../../ai/personal/x10/session.mjs';

const [buildArg,pristineArg,outArg]=process.argv.slice(2);if(!outArg)throw Error('Usage: edge-cases.mjs X10_BUILD PRISTINE_SESSION NEW_EVIDENCE_DIRECTORY');
const build=path.resolve(buildArg),base=path.join(build,'native'),runtime=path.join(build,'runtime/reverse_pc'),pristine=path.resolve(pristineArg),out=path.resolve(outArg);
if(fs.existsSync(out))throw Error('Choose a fresh directory');fs.mkdirSync(out,{recursive:true});const observations=[];
const clone=name=>{const root=path.join(out,name);fs.mkdirSync(root);fs.copyFileSync(path.join(pristine,'memory.sqlite'),path.join(root,'memory.sqlite'));return root;};
function check(name,fn){const t=performance.now();fn();observations.push({name,ok:true,milliseconds:performance.now()-t});console.log('PASS '+name);}
check('invalid-imported-state-leaves-no-session',()=>{
 const bad=path.join(out,'invalid.rvp'),target=path.join(out,'failed');fs.writeFileSync(bad,'invalid');assert.throws(()=>initialize(target,base,bad));assert.equal(fs.existsSync(target),false);assert.equal(fs.readdirSync(out).some(n=>n.startsWith('.x10-init-')),false);
});
check('failed-initial-publication-cleans-staging',()=>{
 const target=path.join(out,'failed-publication'),original=fs.renameSync;try{fs.renameSync=(from,to)=>{if(to===target)throw Error('Injected publication failure');return original(from,to);};assert.throws(()=>initialize(target,base),/Injected publication/);}finally{fs.renameSync=original;}
 assert.equal(fs.existsSync(target),false);assert.equal(fs.readdirSync(out).some(n=>n.startsWith('.x10-init-')),false);
});
check('document-import-still-reaches-original-context',()=>{
 const session=clone('document'),result=transact(runtime,base,session,'import','Aurora es una prueba de contexto. Su etiqueta es violeta.',{operation:'import',title:'X10-documento'});assert.equal(result.ok,true,JSON.stringify(result));
 const status=transact(runtime,base,session,'context','@ctx status');assert.equal(status.ok,true,JSON.stringify(status));assert.match(status.response,/n=001/);
});
check('cleanup-failure-keeps-a-truthful-committed-receipt',()=>{
 const session=clone('cleanup'),original=fs.rmSync;let orphan;
 try{fs.rmSync=(target,options)=>{if(path.basename(target).startsWith('.x10-turn-')){orphan=target;throw Error('Injected cleanup failure');}return original(target,options);};const result=transact(runtime,base,session,'cleanup','@learn status');assert.equal(result.ok,true);assert.equal(result.committed,true);assert.equal(result.cleanup.ok,false);assert.equal(inspect(session).operations,1);}finally{fs.rmSync=original;if(orphan)fs.rmSync(orphan,{recursive:true,force:true});}
 const replay=transact(runtime,base,session,'cleanup','@learn status');assert.equal(replay.replayed,true);assert.equal(replay.generation,1);
});
check('generated-XI-and-execution-evidence-survive-job-cleanup',()=>{
 const session=clone('code'),message='Escribe y ejecuta en XI un programa que sume 637 y 284.',result=transact(runtime,base,session,'code',message);
 assert.equal(result.ok,true,JSON.stringify(result));assert.equal(result.executed,true);assert.equal(result.verified,true);assert.deepEqual(result.result.values,[921]);assert.ok(Buffer.from(result.attachments['program.xi'],'base64').toString().startsWith('#!reverse-pc-machine-v1'));
 assert.equal(fs.readdirSync(session).some(n=>n.startsWith('.x10-turn-')),false);assert.deepEqual(transact(runtime,base,session,'code',message).attachments,result.attachments);
});
const result={ok:true,checks:observations.length,observations};fs.writeFileSync(path.join(out,'results.json'),JSON.stringify(result,null,2)+'\n');console.log(JSON.stringify({ok:true,checks:result.checks}));
