// Test the W4u engine directly in XI, without the BBY Q language/frontend.
import fs from 'node:fs';
import path from 'node:path';
import assert from 'node:assert/strict';
import {execFileSync} from 'node:child_process';
import {fileURLToPath} from 'node:url';
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const [runtime,outArg]=process.argv.slice(2),out=path.resolve(outArg);
fs.mkdirSync(out,{recursive:true});
const state=path.join(out,'agent.rvp'),step=path.join(out,'observation.xi');
const A=8200000000000000000n,M=8300000000000000000n;
const run=(...args)=>execFileSync(runtime,args,{encoding:'utf8',stdio:['ignore','pipe','pipe']});
const put=(a,v)=>`store8 ${a} ${v}\n`;
let checks=0;
function execute(code){fs.writeFileSync(step,'#!reverse-pc-machine-v1\n'+code+'halt\n');run('run',step,state,state);}
function role(name){run('run',path.join(root,name+'.xi'),state,state);}
function at(a){const b=fs.readFileSync(state),n=Number(b.readBigUInt64LE(5));return Number(b.subarray(29+n).toString().split('\n').find(s=>s.startsWith('O '+a+' '))?.split(' ')[2]||0);}
function eq(a,b){assert.deepEqual(a,b);checks++;}
function begin(op,target,extra=''){
  run('init',state);
  execute(put(M,77)+put(M+1n,1)+put(A+16n,1)+put(A+17n,8)+put(A+18n,1)+put(A+40n,1)+put(A+64n,op)+put(A+65n,target)+put(A+67n,1)+extra);
  role('plan');role('explore');role('verify');
  return [at(A+64n),at(A+65n)];
}
function ack(extra){execute(put(M+80n,1)+extra);role('advance');role('verify');return [at(A+64n),at(A+65n)];}
eq(begin(4,2),[1,2]);eq([at(M+32n),at(M+33n),at(M+34n)],[1,1,1]);eq(at(M+19n),2);
eq(ack(put(A+34n,1)),[4,2]);
eq(ack(put(M+674n,1)),[0,0]);eq([at(M+16n),at(M+20n)],[3,2]);
eq(begin(10,16,put(M+528n,2)),[1,16]);
eq(ack(put(A+48n,1)),[10,16]);eq(ack(''),[0,0]);eq(at(M+16n),3);
eq(begin(4,2),[1,2]);eq(ack(''),[0,0]);eq(at(M+16n),4);
eq(begin(10,16),[0,0]);eq(begin(10,16,put(M+528n,1)),[0,0]);
eq(begin(4,2,put(A+18n,12)),[0,0]);
eq(begin(4,2,put(A+34n,2)),[0,0]);
eq(begin(4,2,put(A+16n,0)),[0,0]);
// Independently reject a corrupted proposal rather than trusting the explorer.
begin(4,2);execute(put(M+16n,1)+put(M+131n,1));role('verify');eq([at(A+64n),at(M+34n)],[0,2]);
begin(4,2);execute(put(M+16n,1)+put(M+19n,3));role('verify');eq(at(M+16n),4);
// A failed acknowledgement cannot issue a second action.
begin(10,16,put(M+528n,2));execute(put(M+80n,0));role('advance');role('verify');eq([at(A+64n),at(M+16n)],[0,4]);
const report={engine:'W4u',version:'0.1',checks,roles:3,max_steps:2,scope:'Typed-goal native XI tests; finite planning and verification, not language or general intelligence.'};
fs.writeFileSync(path.join(out,'results.json'),JSON.stringify(report,null,2)+'\n');
console.log('W4U_CORE_PASS',checks);
