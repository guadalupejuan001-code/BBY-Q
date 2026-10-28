#!/usr/bin/env node
// Independent external oracle; it sends messages only. All extraction,
// language decisions, memory writes and response composition execute in XI.
import fs from 'node:fs';
import path from 'node:path';
import assert from 'node:assert/strict';
import {execFileSync} from 'node:child_process';

const [runtimeArg, buildDirArg, outArg]=process.argv.slice(2);
if(!runtimeArg||!buildDirArg||!outArg)throw Error('usage: node test.mjs RUNTIME BUILD_DIR OUT_DIR');
const runtime=path.resolve(runtimeArg),build=path.resolve(buildDirArg),out=path.resolve(outArg);
fs.mkdirSync(out,{recursive:true});
const live=path.join(out,'state.rvp'),baseline=path.join(out,'baseline.rvp');
const natural=path.join(build,'natural.rxe'),old=path.join(build,'candidate.rxe');
fs.copyFileSync(path.join(build,'controller.rvp'),live);
fs.copyFileSync(path.join(build,'controller.rvp'),baseline);
let checks=0,turns=0,autoSaved=0,abstained=0;
function ask(message,lang='es',app=natural,state=live){
  turns++;
  if(Buffer.byteLength(message,'utf8')>255)throw Error('message too long');
  return execFileSync(runtime,['app-turn',app,state,state,lang,message],
    {encoding:'utf8',maxBuffer:1024*1024}).trimEnd();
}
function eq(a,b,name){assert.equal(a,b,name);checks++}
function ok(v,name){assert.ok(v,name);checks++}
const cite=id=>'[#'+String(id).padStart(3,'0')+']';
const spanish=(s,cl,req,c0,c1)=>s+' es '+cl+' '+cite(c0)+'. '+s+' requiere '+req+' '+cite(c1)+'.';
const english=(s,cl,req,c0,c1)=>s+' is '+cl+' '+cite(c0)+'. '+s+' needs '+req+' '+cite(c1)+'.';
const ackEs='Registré esa afirmación.',ackEn='I recorded that statement.';
function status(state=live,app=natural){return ask('@ctx status','es',app,state)}
function auto(sentence,id,language='es'){
  eq(ask(sentence,language),language==='es'?ackEs:ackEn,'natural XI admission '+sentence);
  const expected='CTX n='+String(id+1).padStart(3,'0');
  ok(status().startsWith(expected),'stored exactly one new fragment '+id);
  autoSaved++;
}
eq(ask('hola'),'Hola. Soy BBY Q.','original greeting');
ok(ask('aprende que tatuy es animal').includes('Aprendí'),'E025 training command unchanged');
ok(ask('que es tatuy').toLowerCase().includes('animal'),'original factual knowledge');
eq(status(),'CTX n=000 bytes=000000 limite=114688','unmodified initial archive');
eq(status(baseline,old),'CTX n=000 bytes=000000 limite=114688','E028 baseline archive');
ask('el motor solar es dispositivo.','es',old,baseline);
eq(status(baseline,old),'CTX n=000 bytes=000000 limite=114688',
  'baseline E028 does not ingest free conversational assertion');
eq(ask('@ctx add orion es constelacion'),'CTX guardado #000','E027 explicit command preserved');
auto('El motor solar es dispositivo.',1);
auto('EL MOTOR SOLAR REQUIERE ENERGIA.',2);
eq(ask('@ctx get 1'),'#001 motor solar es dispositivo','article and ASCII casefold');
eq(ask('@ctx get 2'),'#002 motor solar requiere energia','predicate and final period normalized');
eq(ask('que es motor solar y que requiere'),
  spanish('motor solar','dispositivo','energia',1,2),'grounded composition from natural sentences');
eq(ask('what is motor solar and what does it need','en'),
  english('motor solar','dispositivo','energia',1,2),'reuse ES evidence in EN answer');
eq(ask('y qué requiere?'),
  'motor solar requiere energia '+cite(2)+'.','contextual reference follows natural facts');
auto('Recuerda que el puerto azul es refugio.',3);
auto('te cuento que el puerto azul necesita agua.',4);
eq(ask('que es puerto azul y que necesita'),
  spanish('puerto azul','refugio','agua',3,4),'explicit conversational introduction in Spanish');
auto('Remember that the project gamma is prototype.',5,'en');
auto('The project gamma needs silicon.',6,'en');
eq(ask('what is project gamma and what does it need','en'),
  english('project gamma','prototype','silicon',5,6),'English fact memory and generation');
auto('vilo no requiere agua.',7);
eq(ask('que requiere vilo'),
  'Evidencia negativa o contradictoria; no puedo afirmar esa propiedad.',
  'negative fact cannot be treated as positive evidence');
const forbidden=[
  'Creo que solira es planeta.',
  'tal vez solira requiere energia.',
  'maybe solira is planet.',
  'quizás solira es planeta.',
  'what is solira',
  'que es solira',
  'solira es planeta?',
  'solira es planeta; solira requiere agua',
  'solira es planeta y requiere agua',
  'solira es planeta, seguramente',
  'X: solira es planeta',
  'aprende que zirin es animal'
];
const n0='CTX n=008';
for(const q of forbidden){
  ask(q);
  ok(status().startsWith(n0),'ambiguous or unsupported statement rejected: '+q);
  abstained++;
}
ok(ask('que es zirin').toLowerCase().includes('animal'),'E025 explicit training still works');
eq(ask('que es solira y que requiere'),'Falta evidencia para combinar ambas propiedades.',
  'unsupported statements not silently admitted');
auto('gorka es maquina.',8);
auto('gorka es estrella.',9);
eq(ask('que es gorka'),
  'Evidencia negativa o contradictoria; no puedo afirmar esa propiedad.',
  'conflicting natural statements trigger abstention');
// Cross-language transfer on subjects absent from all examples.
let subjects=[];let id=10;const count=24;
for(let i=0;i<count;i++){
  const subject=(i<12?'ense':'hold')+String(i).padStart(3,'0');
  const klass='clase'+String(i),req='recurso'+String(i);
  const c0=id++;auto((i%2?'Remember that ':'')+subject+(i%2?' is ':' es ')+klass+'.',c0,i%2?'en':'es');
  const c1=id++;auto(subject+(i%2?' requires ':' necesita ')+req+'.',c1,i%2?'en':'es');
  subjects.push({subject,klass,req,c0,c1,split:i<12?'development':'transfer'});
}
// Add unrelated long history; the matcher must preserve entity identity and source IDs.
for(let i=0;i<84;i++){
  const filler='Registro narrativo '+String(i).padStart(3,'0')+
    ' no contiene afirmaciones nuevas y sirve como contexto historico. ';
  eq(ask('@ctx add '+filler),'CTX guardado #'+String(id++).padStart(3,'0'),'filler '+i);
}
const results={development:{correct:0,total:0},transfer:{correct:0,total:0}};
const start=process.hrtime.bigint();
for(const row of subjects){
  const es=ask('que es '+row.subject+' y que requiere');
  eq(es,spanish(row.subject,row.klass,row.req,row.c0,row.c1),'ES composition '+row.subject);
  results[row.split].total++;results[row.split].correct++;
  const en=ask('what is '+row.subject+' and what does it need','en');
  eq(en,english(row.subject,row.klass,row.req,row.c0,row.c1),'EN composition '+row.subject);
  results[row.split].total++;results[row.split].correct++;
}
const query_ms=Math.round(Number(process.hrtime.bigint()-start)/1e6);
eq(ask('que es ense000 y que requiere'),
 spanish(subjects[0].subject,subjects[0].klass,subjects[0].req,
 subjects[0].c0,subjects[0].c1),'first entity survives long history');
eq(ask('@ctx get 1'),'#001 motor solar es dispositivo','stored bytes remain inspectable');
eq(ask('@ctx clear'),'CTX vaciado.','E027 delete preserved');
eq(ask('que es motor solar y que requiere'),'Falta evidencia para combinar ambas propiedades.',
  'deleted conversational facts are inaccessible');
eq(ask('y que requiere'),'Necesito una entidad o referencia anterior.','reference invalidated by clear');
ok(ask('que es tatuy').toLowerCase().includes('animal'),'E025 fact retained after context reset');
auto('el motor solar es nuevo.',0);
eq(ask('que es motor solar'),'motor solar es nuevo '+cite(0)+'.','new state does not reuse stale entity');

const report={version:'E029-Natural-Facts-1-dev',checks,turns,autoSaved,
  rejected_ambiguous_messages:abstained,
  natural_vs_previous:{previous_free_intake:0,new_free_intake:autoSaved},
  results,query_elapsed_ms:query_ms,
  categories:['natural ES and EN assertions','conversational introduction and articles',
    'recovery with citations','cross-language composition','old E025 memory',
    'negation and contradictory claims','uncertain language veto','no implicit learning from questions',
    'multi-clause rejection','long history and source integrity',
    'E027 commands and clear','no lost E025 facts'],
  scope:'Narrow supervised-by-syntax factual extraction in XI, not free-form language understanding.',
  production_deployed:false};
fs.writeFileSync(path.join(out,'results.json'),JSON.stringify(report,null,2)+'\n');
console.log(JSON.stringify(report,null,2));
