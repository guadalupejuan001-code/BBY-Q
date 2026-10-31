// Native XI history-search examination. No JS language inference or mock answers.
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import {performance} from 'node:perf_hooks';
import {NativePages,cells,run} from '../../../ai/personal/x10/pages.mjs';
import {contextSource,CONTEXT_BASE,CONTEXT_MAX_CANDIDATES,CONTEXT_MAX_QUERY_BYTES} from '../../../ai/personal/p05/context.mjs';

const [runtimeArg,outArg]=process.argv.slice(2);
if(!outArg)throw Error('Usage: node integration/p05/tests/native.mjs REVERSE_PC NEW_OUTPUT');
const runtime=path.resolve(runtimeArg),out=path.resolve(outArg);
if(fs.existsSync(out))throw Error('P05 evidence directory must not exist.');
fs.mkdirSync(out,{recursive:true});
const source=contextSource(),xi=path.join(out,'context.xi'),rxe=path.join(out,'context.rxe');
fs.writeFileSync(xi,source);run(runtime,['compile',xi,rxe,'BBY Q P05 conversational reference matching']);
const cases=[
 ['¿Qué dije sobre Luna?',['Luna es un gato.'],1,1],
 ['¿Qué dije de luna?',['LUNA es gato.'],1,1],
 ['¿Qué dije de ella?',['Luna es un gato.'],2,1],
 ['¿Y qué dije de ella?',['Luna es un gato.'],2,1],
 ['¿Qué dije de él?',['Pablo tiene un automóvil.'],2,1],
 ['¿Qué dije de eso?',['Aurora es una nave.'],2,1],
 ['¿Qué dije de ese tema?',['Aurora es un proyecto.'],2,1],
 ['¿Qué dije de Ana?',['Anabel es astronauta.'],3,0],
 ['¿Qué dije de Luna?',['Ana es atleta.','Luna es un gato.'],1,2],
 ['¿Qué dije de Luna?',['Luna es una estrella.','Luna es un gato.'],1,1],
 ['¿Qué dije sobre Aurora?',['Mi proyecto Aurora es una IA.'],1,1],
 ['¿Qué dije sobre mi proyecto?',['Mi proyecto Aurora es una IA.'],1,1],
 ['¿Qué dije de ella?',['Luna y Ana son amigas.'],4,0],
 ['¿Qué dije de ella?',['Cambiemos de tema.','Luna es un gato.'],4,0],
 ['¿Qué dije sobre Luna?',['Cambiemos de tema.','Luna es un gato.'],1,2],
 ['¿Qué dije de ella?',['Luna no es gato.'],4,0],
 ['¿Qué dije de ella?',['Hola'],4,0],
 ['¿Qué dije antes?',['Luna es un gato.'],5,1],
 ['@context last',['Luna es un gato.'],5,1],
 ['@context recent',['Luna es un gato.'],8,0],
 ['@context clear',['Luna es un gato.'],6,0],
 ['@context status',['Luna es un gato.'],7,0],
 ['@CONTEXT STATUS',[],7,0],
 ['@context answer',['Luna es un gato.'],9,1],
 ['¿Qué me respondiste antes?',['Luna es un gato.'],9,1],
 ['@context last',[],3,0],
 ['¿Qué dije antes?',[],3,0],
 ['¿Qué dije de ella?',[],3,0],
 ['¿Qué dije sobre Pixel?',['Luna es un gato.'],3,0],
 ['¿Te acuerdas de Luna?',['Luna es un gato.'],1,1],
 ['¿Qué te dije de Luna?',['Luna es un gato.'],1,1],
 ['¿Qué mencioné sobre Luna?',['Luna es un gato.'],1,1],
 ['¿Qué dije acerca de Luna?',['Luna es un gato.'],1,1],
 ['qué dije de LUNA?',['Luna es un gato.'],1,1],
 ['¿Qué dije de ella?',['Ana tiene un perro.','Luna es gato.'],2,1],
 ['¿Qué dije de él?',['El perro de Ana está cansado.'],4,0],
 ['hola',['Luna es gato.'],0,0],
 ['¿Quién es Luna?',['Luna es gato.'],0,0],
 ['@context delete',['Luna es gato.'],0,0],
 ['@context clear accidental',['Luna es gato.'],0,0],
 ['Dime qué dije de Luna',['Luna es gato.'],0,0],
 ['¿Qué dije sobre Luna?',['Luna es un gato','Ana es cantante'],1,1]
];
for(let n=0;n<48;n++){
 const topic='tema'+String(n).padStart(3,'0'),others='tema'+String(n+1).padStart(3,'0');
 cases.push(['¿Qué dije sobre '+topic+'?',[others+' es azul.',topic+' tiene una forma nueva.'],1,2]);
}
const report=[],times=[];
for(let i=0;i<cases.length;i++){
 const [q,history,expectedMode,expectedSlot]=cases[i],raw=Buffer.from(q);
 assert.ok(history.length<=CONTEXT_MAX_CANDIDATES);
 const job=path.join(out,'case-'+String(i).padStart(3,'0'));fs.mkdirSync(job);
 const pages=new NativePages(runtime,{'context.rxe':rxe},job);
 const entries=history.map(s=>Buffer.from(s));
 pages.stage({data:raw,total:raw.length,numbers:[[CONTEXT_BASE+3n,entries.length,1],
   ...entries.map((v,j)=>[CONTEXT_BASE+32n+BigInt(2*j),v.length,2])],
   bytes:entries.map((v,j)=>[CONTEXT_BASE+4096n+BigInt(j*512),v])});
 const before=cells(pages.state),start=performance.now(),result=pages.context(raw,entries),ms=performance.now()-start,after=cells(pages.state);
 assert.equal(result.mode,expectedMode,JSON.stringify({q,history,result}));
 assert.equal(result.slot,expectedSlot,JSON.stringify({q,history,result}));
 assert.equal(result.handled,expectedMode!==0,q);
 const foreign=[...new Set([...before.keys(),...after.keys()])].filter(a=>a<CONTEXT_BASE||a>=CONTEXT_BASE+8n)
  .filter(a=>(before.get(a)||0)!==(after.get(a)||0));
 assert.deepEqual(foreign,[],'XI P05 changed foreign memory: '+q);
 times.push(ms);report.push({question:q,history,expectedMode,mode:result.mode,slot:result.slot,ms,ok:true});
 fs.rmSync(job,{recursive:true,force:true});
}
const p=new NativePages(runtime,{'context.rxe':rxe},path.join(out,'overflow'));
assert.equal(p.context(Buffer.alloc(CONTEXT_MAX_QUERY_BYTES+1,65),[]).mode,0);
const sorted=times.sort((a,b)=>a-b),pct=p=>sorted[Math.max(0,Math.ceil(p*sorted.length)-1)];
const sha=x=>crypto.createHash('sha256').update(x).digest('hex');
const results={ok:true,exam:'real native XI context lookup on bounded prior user utterances',
 cases:report.length,correct:report.length,novel_topics:48,overflow_abstained:true,
 mean_ms:times.reduce((a,b)=>a+b,0)/times.length,median_ms:pct(.5),p95_ms:pct(.95),
 source_sha256:sha(Buffer.from(source)),binary_sha256:sha(fs.readFileSync(rxe)),
 scope:'explicit named recall, immediate single-subject pronoun, last/recent/status/clear, no general coreference',
 no_neural_weights:true,records:report};
fs.writeFileSync(path.join(out,'results.json'),JSON.stringify(results,null,2)+'\n');
console.log(JSON.stringify({ok:true,cases:results.cases,correct:results.correct,novel_topics:48,median_ms:results.median_ms,p95_ms:results.p95_ms}));
