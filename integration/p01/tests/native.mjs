// Native XI examination. This is a real executable role test, not a JS
// reimplementation of the classifier. Run with the pinned reverse_pc binary.
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import {spawnSync} from 'node:child_process';
import {performance} from 'node:perf_hooks';
import {intentSource,INTENT_ADDRESS,INTENT_NAMES} from '../../../ai/personal/p01/intent.mjs';
import {B,INPUT,LENGTH,TOTAL} from '../../../ai/personal/x10/schema.mjs';
import {cells,readNumber} from '../../../ai/personal/x10/pages.mjs';

const [runtimeArg,outputArg]=process.argv.slice(2);
if(!outputArg)throw Error('Usage: node integration/p01/tests/native.mjs REVERSE_PC NEW_OUTPUT_DIR');
const runtime=path.resolve(runtimeArg),output=path.resolve(outputArg);
if(fs.existsSync(output))throw Error('P01 evidence directory must be new.');
fs.mkdirSync(output,{recursive:true});

function native(...args){
 const p=spawnSync(runtime,args,{encoding:'utf8',timeout:60000,maxBuffer:8*1024*1024});
 if(p.status!==0)throw Error('XI '+args[0]+' failed: '+(p.stderr||p.error?.message||p.stdout));
 return p.stdout;
}
const source=intentSource(),sourceFile=path.join(output,'intent.xi'),code=path.join(output,'intent.rxe');
fs.writeFileSync(sourceFile,source);
native('compile',sourceFile,code,'BBY Q P01 - explicit intent classifier');
const S=B+999999n; // Foreign state sentinel; must never be touched by P01.
const sha=s=>crypto.createHash('sha256').update(s).digest('hex');
const samples=[
 ['hola','greeting'],['Buenas tardes','greeting'],['hello','greeting'],
 ['hey, buenos días','greeting'],['¿Qué tal?','greeting'],
 ['Explícame por qué el cielo es azul.','explanation'],
 ['Explica qué sucede con el agua.','explanation'],
 ['¿Por qué el hielo flota?','explanation'],
 ['¿Cómo funciona Ether?','explanation'],
 ['Oye, ¿por qué cambia el precio?','explanation'],
 ['Dime por qué cae la lluvia.','explanation'],
 ['Why is the sky blue?','explanation'],
 ['Quiero entender cómo funciona el sistema','explanation'],
 ['¿Qué es la memoria?','question'],['¿Quién construyó esto?','question'],
 ['¿Dónde está el archivo?','question'],['¿Cuándo empieza la prueba?','question'],
 ['¿Cuánto es 17 + 25?','question'],['What is a qubit?','question'],
 ['¿Es cierto lo que dijiste?','question'],
 ['Escribe un poema de cuatro versos sobre una guitarra.','creation'],
 ['Escribe un cuento sobre una estrella.','creation'],
 ['Crea un cuento pequeño','creation'],['Crea una historia nueva','creation'],
 ['Inventa un relato original','creation'],['Redacta un cuento','creation'],
 ['Escribe y ejecuta en XI un programa que sume 637 y 284.','instruction'],
 ['Genera y ejecuta un programa','instruction'],
 ['Calcula 17 + 25','instruction'],['Traduce al inglés: hola','instruction'],
 ['Resume este texto','instruction'],['Busca información','instruction'],
 ['Revisa el sistema','instruction'],['Quiero que analices esto','instruction'],
 ['Recuerda que el proyecto se llama Aurora.','teaching'],
 ['Oye, recuerda que Aurora es una nave.','teaching'],
 ['Aprende: nueva regla','teaching'],
 ['Enseña traducción: casa | home','teaching'],
 ['Guarda que la revisión es dos','teaching'],['Anota que el dato cambió','teaching'],
 ['Corrige: el dato anterior es incorrecto','correction'],
 ['Corrige lección: ahorro','correction'],
 ['Quise decir jueves, no martes','correction'],
 ['No, me equivoqué. Era otra persona.','correction'],
 ['Atena es una nave.','statement'],['Tengo dos motores.','statement'],
 ['Mi vecino es astronauta.','statement'],['Soy humano.','statement'],
 ['Estoy hablando del proyecto.','statement'],
 ['¿Recuerda que este sistema es nuevo?','question'],
 ['El texto literal dice "recuerda que", no se lo estoy ordenando.','statement'],
 ['Un nombre inventado sin palabras de activación','unknown'],
 ['¿Esto debería memorizarse?','question'],
 ['Antes de seguir: ¿quién lo construyó?','question'],
 ['hey, explain how it works','explanation']
];
const counter={passed:0,failed:0},rows=[];
function test(text,expected,index){
 const key=String(index).padStart(3,'0'),state=path.join(output,key+'.rvp'),
       frame=path.join(output,key+'.xi'),raw=Buffer.from(text);
 native('init',state);
 let w=['#!reverse-pc-machine-v1','store8 '+S+' 173'];
 for(const [a,n]of [[LENGTH,raw.length],[TOTAL,raw.length]])for(let i=0;i<4;i++)
  w.push('store8 '+(a+BigInt(i))+' '+(Math.floor(n/256**i)%256));
 for(const[i,b]of raw.entries())w.push('store8 '+(INPUT+BigInt(i))+' '+b);
 w.push('halt');fs.writeFileSync(frame,w.join('\n')+'\n');
 native('run',frame,state,state);
 const before=cells(state),start=performance.now();native('run',code,state,state);
 const ms=performance.now()-start,after=cells(state),id=readNumber(after,INTENT_ADDRESS,1);
 const name=INTENT_NAMES[id]||'invalid',readonly=readNumber(after,INTENT_ADDRESS+2n,1)===1;
 const allowed=a=>(a>=INTENT_ADDRESS&&a<INTENT_ADDRESS+16n)||
   (a>=B+1024n&&a<B+1280n)||(a>=B+32768n&&a<B+36864n);
 const modified=[...new Set([...before.keys(),...after.keys()])].filter(a=>
  before.get(a)!==after.get(a)&&!allowed(a));
 assert.deepEqual(modified,[],'P01 altered foreign state: '+text);
 assert.equal(after.get(S),173,'P01 touched foreign sentinel');
 assert.equal(readonly,!['teaching','correction'].includes(name),'wrong read-only policy: '+text);
 const ok=name===expected;
 rows.push({id:key,input:text,expected,actual:name,readonly,confidence:readNumber(after,INTENT_ADDRESS+1n,1),matched_rule:readNumber(after,INTENT_ADDRESS+4n,1),ms,ok});
 if(ok)counter.passed++;else counter.failed++;
 fs.unlinkSync(frame);fs.unlinkSync(state);
}
for(const [i,[text,expected]]of samples.entries())test(text,expected,i);
const times=rows.map(x=>x.ms).sort((a,b)=>a-b),pick=p=>times[Math.min(times.length-1,Math.ceil(times.length*p)-1)];
const report={ok:counter.failed===0,examination:'native XI / fixed P01 curriculum',not_neural_training:true,
 notes:'Fixtures cover supported patterns and some negative controls; no general-language score is claimed.',
  samples:rows.length,correct:counter.passed,failed:counter.failed,
  median_ms:pick(.5),p95_ms:pick(.95),
  source_sha256:sha(source),native_code_sha256:sha(fs.readFileSync(code)),cases:rows};
fs.writeFileSync(path.join(output,'results.json'),JSON.stringify(report,null,2)+'\n');
console.log(JSON.stringify({ok:report.ok,samples:rows.length,correct:counter.passed,failed:counter.failed,median_ms:report.median_ms,p95_ms:report.p95_ms}));
for(const row of rows.filter(x=>!x.ok))console.error('FAIL '+JSON.stringify({input:row.input,expected:row.expected,actual:row.actual,rule:row.matched_rule}));
assert.equal(counter.failed,0,'Native P01 intent classification errors');
