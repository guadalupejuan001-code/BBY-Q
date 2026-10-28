#!/usr/bin/env node
// Interoperability expectations stay outside the native XI program.
import fs from 'node:fs';
import path from 'node:path';
import assert from 'node:assert/strict';
import {execFileSync} from 'node:child_process';
const [runtimeArg, capsulesArg, outArg]=process.argv.slice(2);
const runtime=path.resolve(runtimeArg),root=path.resolve(capsulesArg),out=path.resolve(outArg);
fs.mkdirSync(out,{recursive:true});
const state=path.join(out,'live.rvp');fs.copyFileSync(path.join(root,'controller.rvp'),state);
const app=path.join(root,'candidate.rxe');let checks=0;const transcript=[];
function ask(text,language='es'){
 const answer=execFileSync(runtime,['app-turn',app,state,state,language,text],{encoding:'utf8'}).trimEnd();
 transcript.push({input:text,language,output:answer});return answer;
}
function eq(actual,expected,label){assert.equal(actual,expected,label);checks++;}
function ok(condition,label){assert.ok(condition,label);checks++;}
eq(ask('@ctx add Registro alfa persistente'),'CTX guardado #000','context before compound turn');
eq(ask('@ctx add Segundo registro independiente'),'CTX guardado #001','second context fragment');
ok(ask('aprende que linora es animal').includes('Aprendí'),'original teaching survives');
ok(ask('aprende que linora requiere agua').includes('Aprendí'),'second fact survives');
for(const lang of ['es','en']){
 const first=ask((lang==='es'?'que es ':'what is ')+'linora',lang);
 const second=ask(lang==='es'?'que requiere linora':'what does linora require',lang);
 eq(ask(lang==='es'?'que es linora y que requiere':'what is linora and what does it require',lang),first+' '+second,'composition with archived context');
}
eq(ask('@ctx get 0'),'#000 Registro alfa persistente','compound preserves first archive');
eq(ask('@ctx find independiente'),'#001 Segundo registro independiente','compound preserves lexical search');
eq(ask('@ctx clear'),'CTX vaciado.','clear remains available');
eq(ask('@ctx status'),'CTX n=000 bytes=000000 limite=114688','archive cleared independently');
const first=ask('que es linora'),second=ask('que requiere linora');
eq(ask('que es linora y que requiere'),first+' '+second,'clearing archive preserves facts and composition');
const report={version:'E027-CtxCompose-2-dev',checks,native_process_per_turn:true,
scope:'Persistent archive and composition coexist in the same RVPC2; indexed/lexical retrieval remains explicit, not automatic semantic grounding.'};
fs.writeFileSync(path.join(out,'results.json'),JSON.stringify(report,null,2)+'\n');
fs.writeFileSync(path.join(out,'transcripts.jsonl'),transcript.map(x=>JSON.stringify(x)).join('\n')+'\n');
console.log(JSON.stringify(report,null,2));
