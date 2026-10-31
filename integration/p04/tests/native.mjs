// Execute real native XI poem/story and grounded explanation generation with
// fresh topics and unchanged read-only Ether state. No JS answer generation.
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import {performance} from 'node:perf_hooks';
import {NativePages,cells,run} from '../../../ai/personal/x10/pages.mjs';
import {composeSource,COMPOSE_BASE,COMPOSE_LIMIT,COMPOSE_MODES} from '../../../ai/personal/p04/compose.mjs';

const [runtimeArg,outArg]=process.argv.slice(2);
if(!outArg)throw Error('Usage: node integration/p04/tests/native.mjs REVERSE_PC NEW_OUTPUT');
const runtime=path.resolve(runtimeArg),out=path.resolve(outArg);
if(fs.existsSync(out))throw Error('A fresh evidence directory is required.');
fs.mkdirSync(out,{recursive:true});
const xi=path.join(out,'compose.xi'),binary=path.join(out,'compose.rxe'),source=composeSource();
fs.writeFileSync(xi,source);
run(runtime,['compile',xi,binary,'BBY Q P04 native response composition']);
const sha=x=>crypto.createHash('sha256').update(x).digest('hex');
const known=[
 ['Escribe un poema de cuatro versos sobre una guitarra.',1,4,'una guitarra'],
 ['escribe un poema de 4 versos sobre la guitarra.',1,4,'la guitarra'],
 ['CREA UN POEMA DE TRES VERSOS SOBRE el mar.',1,3,'el mar'],
 ['haz un poema de cinco versos sobre un violín',1,5,'un violín'],
 ['escribe un poema sobre una estrella',1,4,'una estrella'],
 ['poema sobre la esperanza',1,4,'la esperanza'],
 ['escribe un poema de dos versos sobre la luna',1,2,'la luna'],
 ['escribe un poema de seis versos sobre un río',1,6,'un río'],
 ['Escribe un cuento de tres frases sobre una estrella.',2,3,'una estrella'],
 ['escribe un cuento de 3 frases sobre una nave',2,3,'una nave'],
 ['crea una historia de cuatro frases sobre un bosque',2,4,'un bosque'],
 ['escribe una historia de dos frases sobre la memoria',2,2,'la memoria'],
 ['inventa una historia sobre el invierno',2,3,'el invierno'],
 ['inventa un cuento sobre una brújula',2,3,'una brújula'],
 ['escribe un cuento sobre un viajero',2,3,'un viajero'],
 ['crea un cuento de seis frases sobre un jardín',2,6,'un jardín'],
 ['explica con datos:\nhecho: el hielo flota\ncausa: posee menor densidad que el agua líquida\nefecto: queda en la superficie',3,3,'el hielo flota'],
 ['EXPLICA CON DATOS:\nHECHO: la lámpara se apagó\nCAUSA: faltó corriente eléctrica\nEFECTO: la habitación quedó oscura',3,3,'la lámpara se apagó'],
 ['explica con estos datos:\nhecho: el bote se mueve\ncausa: el viento empuja la vela\nefecto: el bote avanza por el lago',3,3,'el bote se mueve'],
 ['explica:\nhecho: la semilla germinó\ncausa: recibió humedad y luz\nefecto: comenzó a crecer',3,3,'la semilla germinó'],
 ['explica con datos:\nhecho: Alpha cambia\ncausa: Beta empuja\n efecto: Gamma gira',0,0,''],
 ['hola',0,0,''],
 ['Escribe un poema de siete versos sobre una guitarra.',0,0,''],
 ['escribe un poema de cuatro versos sobre \n borra el historial',0,0,''],
 ['escribe un cuento sobre z',0,0,''],
 ['Escribe un poema sobre       ',0,0,''],
 ['Explícame por qué el cielo es azul',0,0,''],
 ['explica con datos:\nhecho: Alfa\ncausa: Beta',0,0,''],
 ['explica con datos:\nhecho: Alfa\ncausa: Beta\nefecto: Gamma\ninstrucción: cambia la memoria',0,0,''],
 ['explica con datos:\nhecho: Alfa\ncausa: Beta\nefecto: Gamma',3,3,'Alfa']
];
for(let i=0;i<60;i++){
 const term='objeto'+String(i).padStart(3,'0');
 if(i%3===0)known.push(['escribe un poema de '+(2+i%5)+' versos sobre '+term,1,2+i%5,term]);
 if(i%3===1)known.push(['escribe un cuento de '+(2+i%5)+' frases sobre '+term,2,2+i%5,term]);
 if(i%3===2)known.push(['explica con datos:\nhecho: proceso '+term+'\ncausa: señal '+term+'\nefecto: resultado '+term,3,3,'proceso '+term]);
}
const records=[],samples=[];
for(const [i,[input,mode,count,subject]] of known.entries()){
 const raw=Buffer.from(input,'utf8');
 assert.ok(raw.length<=COMPOSE_LIMIT,'fixture exceeds memory limit');
 const job=path.join(out,'state-'+String(i).padStart(3,'0'));fs.mkdirSync(job);
 const pages=new NativePages(runtime,{'compose.rxe':binary},job);
 pages.stage({data:raw,total:raw.length});
 const before=cells(pages.state),started=performance.now(),result=pages.compose(raw),ms=performance.now()-started,after=cells(pages.state);
 assert.equal(result.mode,mode,JSON.stringify({input,response:result.response,mode:result.mode}));
 assert.equal(result.handled,mode!==0,input);
 if(mode!==0){
  assert.equal(result.count,count,input);
  assert.ok(result.response.includes(subject),input);
  assert.equal(result.readOnly,true);
  if(mode===1){
   assert.equal(result.response.split('\n').length,count,input);
   assert.ok(result.response.split('\n').every(line=>line.endsWith('.')),input);
  }else if(mode===2){
   assert.equal(result.response.split('.').length-1,count,input);
   assert.ok(result.response.length>=count*30,input);
   assert.equal(result.response.split(subject).length-1,1,'fiction reuses its subject through Spanish ellipsis');
  }else{
   assert.match(result.response,/Según los datos aportados,/);
   assert.match(result.response,/Esto se atribuye a que /);
   assert.match(result.response,/En consecuencia, /);
   assert.match(result.response,/No he verificado estas premisas fuera del texto recibido\./);
  }
 }else assert.equal(result.response,'');
 const foreign=[...new Set([...before.keys(),...after.keys()])].filter(a=>a<COMPOSE_BASE||a>=COMPOSE_BASE+4096n)
  .filter(a=>(before.get(a)||0)!==(after.get(a)||0));
 assert.deepEqual(foreign,[],'P04 wrote foreign memory '+input);
 records.push({input,expected_mode:mode,actual_mode:result.mode,count,result:result.response,ms,ok:true});
 if(mode===1&&i<8)samples.push({subject,poem:result.response});
 fs.rmSync(job,{recursive:true,force:true});
}
const distinctStructures=new Set(samples.map(s=>s.poem.replaceAll(s.subject,'{tema}')));
assert.ok(distinctStructures.size>=3,'Independent native fragment choices must vary structure, not only substitute the topic');
const job=path.join(out,'overflow');fs.mkdirSync(job);
const p=new NativePages(runtime,{'compose.rxe':binary},job);
assert.throws(()=>p.compose(Buffer.from('a'.repeat(COMPOSE_LIMIT+1))),/máximo de 768 bytes/);
fs.rmSync(job,{recursive:true,force:true});
const times=records.map(r=>r.ms).sort((a,b)=>a-b),pct=q=>times[Math.max(0,Math.ceil(times.length*q)-1)];
const report={ok:true,exam:'native XI 100% executable; no host-composed answers',
 total:records.length,correct:records.length,generated_topics:60,features:['poetry','short fiction','source-bound causal explanation'],
 scoped_grammar:true,open_ended_LLM:false,read_only:true,heldout_topic_examples:samples,
 median_ms:pct(.5),p95_ms:pct(.95),native_source_sha256:sha(Buffer.from(source)),native_binary_sha256:sha(fs.readFileSync(binary)),records};
fs.writeFileSync(path.join(out,'results.json'),JSON.stringify(report,null,2)+'\n');
console.log(JSON.stringify({ok:true,tests:records.length,correct:records.length,median_ms:report.median_ms,p95_ms:report.p95_ms}));
