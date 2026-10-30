// Transports one explicit label. No matching, normalization or learned writes here.
import fs from 'node:fs';
import path from 'node:path';
import {execFileSync} from 'node:child_process';
const [r,learner,input,output,text,id,ctx='0',kindArg='1',oldId,oldCtx]=process.argv.slice(2);
if(!id)throw Error('usage: teach.mjs RUNTIME LEARN_XI INPUT_RVP NEW_OUTPUT_RVP TEXT INTENT CONTEXT_0_1 [KIND_1_4 [EXPECTED_OLD_INTENT EXPECTED_OLD_CONTEXT]]');
const intent=Number(id),kind=Number(kindArg),needsContext=Number(ctx),bytes=Buffer.from(text),P=9050000000000000000n;
if(!Number.isInteger(intent)||!Number.isInteger(kind)||!Number.isInteger(needsContext)||bytes.length<1||bytes.length>255||
 kind<1||kind>4||needsContext<0||needsContext>1||(kind===1?(intent<1||intent>17):(intent!==0||needsContext!==0)))throw Error('Invalid explicit lesson');
const dest=path.resolve(output);
if(fs.existsSync(dest))throw Error('Output exists; keep the original state');
const lesson=dest+'.lesson.xi';
const guard=fs.readFileSync(path.join(path.dirname(path.resolve(learner)),'guard.xi'),'utf8').split('\n').filter(l=>!l.startsWith('#!')).join('\n').replaceAll('\nhalt','\njmp teacher_apply');
let source=`#!reverse-pc-machine-v1\n${guard}\nlabel teacher_apply\nstore8 ${P+16n} ${kind}\nstore8 ${P+17n} ${intent}\nstore8 ${P+18n} ${needsContext}\nstore8 ${P+19n} ${bytes.length}\n`;
const correcting=oldId!==undefined;
if(correcting&&(!Number.isInteger(Number(oldId))||Number(oldId)<1||Number(oldId)>17||!['0','1'].includes(oldCtx)||kind!==1))throw Error('Explicit previous intent and context are required');
source+=`store8 ${P+20n} ${correcting?1:0}\nstore8 ${P+21n} ${correcting?Number(oldId):0}\nstore8 ${P+22n} ${correcting?Number(oldCtx):0}\n`;
for(const [i,v]of bytes.entries())source+=`store8 ${P+272n+BigInt(i)} ${v}\n`;
source+=fs.readFileSync(learner,'utf8').split('\n').filter(l=>!l.startsWith('#!')).join('\n');
fs.writeFileSync(lesson,source);
execFileSync(path.resolve(r),['run',lesson,path.resolve(input),dest],{encoding:'utf8',timeout:30000,stdio:['ignore','pipe','pipe']});
console.log(JSON.stringify({output:dest,raw:text,intent,context:needsContext,kind,explicit_correction:correcting,learning:'XI',replaced_original:false}));
