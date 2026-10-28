#!/usr/bin/env node
// Black-box evaluation. The evaluator transports strings and compares results;
// it does not interpret or generate the agent's answers.
import fs from 'node:fs';
import path from 'node:path';
import assert from 'node:assert/strict';
import {execFileSync} from 'node:child_process';
const [runtimeArg, e028DirArg, legacyDirArg, outArg]=process.argv.slice(2);
if (![runtimeArg,e028DirArg,legacyDirArg,outArg].every(Boolean))
  throw Error('usage: node test.mjs RUNTIME E028_BUILD E027_BUILD OUTPUT_DIR');
const runtime=path.resolve(runtimeArg), build=path.resolve(e028DirArg), legacy=path.resolve(legacyDirArg);
const out=path.resolve(outArg);fs.mkdirSync(out,{recursive:true});
const state=path.join(out,'state.rvp');
fs.copyFileSync(path.join(build,'controller.rvp'),state);
const app=path.join(build,'candidate.rxe'), oldApp=path.join(legacy,'candidate.rxe');
const scores={baseline:0,development:{composed:0,total:0,atomic:0,atomic_total:0},
  transfer:{composed:0,total:0,atomic:0,atomic_total:0},controls:0};
let calls=0, checks=0, cursor=0;
function ask(text,lang='es',usedApp=app) {
  calls++;
  assert.ok(Buffer.byteLength(text,'utf8')<=255,'app-turn input >255 bytes');
  return execFileSync(runtime,['app-turn',usedApp,state,state,lang,text],
    {encoding:'utf8',maxBuffer:1024*1024}).trimEnd();
}
function eq(actual,expected,name){assert.equal(actual,expected,name);checks++;}
function ok(value,name){assert.ok(value,name);checks++;}
function add(text,usedApp=app){
  const id=cursor++;
  eq(ask('@ctx add '+text,'es',usedApp),'CTX guardado #'+String(id).padStart(3,'0'),'append '+id);
  return id;
}
function cited(id){return '[#'+String(id).padStart(3,'0')+']';}
function answer(subject,klass,need,definitionId,needId,lang){
  const pred1=lang==='es'?'es':'is',pred2=lang==='es'?'requiere':'needs';
  return subject+' '+pred1+' '+klass+' '+cited(definitionId)+'. '+
    subject+' '+pred2+' '+need+' '+cited(needId)+'.';
}
eq(ask('hola'),'Hola. Soy BBY Q.','E025 greeting');
ok(ask('aprende que tatuy es animal').includes('Aprendí'),'E025 learning');
ok(ask('que es tatuy').includes('animal'),'original factual memory');
const baseA=add('motor solar es dispositivo',oldApp);
const baseB=add('motor solar requiere energia',oldApp);
eq(ask('que es motor solar y que requiere'),
   answer('motor solar','dispositivo','energia',baseA,baseB,'es'),
   'E027 old-state migration: ES composition without reindex or manual find');
scores.baseline++;
eq(ask('¿qué es el motor solar y qué necesita?'),
   answer('motor solar','dispositivo','energia',baseA,baseB,'es'),
   'Spanish accents and entity article');
eq(ask('what is motor solar and what does it need','en'),
   answer('motor solar','dispositivo','energia',baseA,baseB,'en'),
   'English composition with same indexed E027 bytes');
eq(ask('what does it require?','en'),
   'motor solar needs energia '+cited(baseB)+'.','referential English pronoun');
eq(ask('y qué requiere?'),
   'motor solar requiere energia '+cited(baseB)+'.','Spanish contextual followup');
eq(ask('que es tatuy').includes('animal'),true,'E025 fallback without E027 fact');
eq(ask('@ctx find motor solar'), '#001 motor solar requiere energia','legacy explicit search preserved');

const gram='saludable';
const cl=add('velosa es orbe');
const re=add('velosa necesita luz solar');
eq(ask('que es velosa y que necesita'),
   answer('velosa','orbe','luz solar',cl,re,'es'),'multiword predicate value');
const negId=add('velosa no requiere agua');
eq(ask('que requiere velosa'),
   'Evidencia negativa o contradictoria; no puedo afirmar esa propiedad.',
   'conservative negative evidence abstention');
eq(ask('que es velosa'),
   'velosa es orbe '+cited(cl)+'.','contradiction scoped to matching property');

const neg1=add('gorka es maquina');
const neg2=add('gorka es estrella');
eq(ask('que es gorka'),'Evidencia negativa o contradictoria; no puedo afirmar esa propiedad.',
  'contradictory definitions do not silently choose a winner');
add('xentria es galaxia; xentria requiere fuego');
ok(!ask('que es xentria y que requiere').includes(cited(cursor-1)),
  'untrusted multi-clause sentence not misindexed as an atomic fact');
add('quotera no es mineral');
eq(ask('que es quotera'),'Evidencia negativa o contradictoria; no puedo afirmar esa propiedad.',
  'negative alone cannot be asserted positive');

const vals=['rotor','cristal','nube','puente','orbita','archivo'];
const needs=['agua','aire','energia','cobre','luz','tiempo'];
let subjects=[];
for (const [split,prefix] of [['development','devc'],['transfer','zolv']]){
  for(let i=0;i<24;i++){
    const subject=prefix+String(i).padStart(3,'0');
    const klass=vals[(i*7+3)%vals.length]+'x'+String(i);
    const need=needs[(i*5+2)%needs.length]+'x'+String(i);
    const first=add(subject+' es '+klass);
    const second=add(subject+' requiere '+need);
    subjects.push({subject,klass,need,first,second,split});
  }
}
// Fill archive with unrelated long fragments to require contextual selection.
const extra=140;
for (let i=0;i<extra;i++){
  const text=('Fragmento historico irrelevante ref'+String(i).padStart(3,'0')+
   ' con sucesos narrativos no factuales. ').padEnd(203,'z');
  add(text);
}
const durationStart=process.hrtime.bigint();
for (const row of subjects){
  const {subject,klass,need,first,second,split}=row;
  const expES=answer(subject,klass,need,first,second,'es');
  const expEN=answer(subject,klass,need,first,second,'en');
  const spanish=ask('que es '+subject+' y que requiere','es');
  eq(spanish,expES,'grounded ES composition '+subject);
  scores[split].total++;scores[split].composed++;
  eq(ask('what is '+subject+' and what does it need','en'),
    expEN,'grounded EN composition '+subject);
  scores[split].total++;scores[split].composed++;
  eq(ask('que requiere '+subject,'es'),subject+' requiere '+need+' '+cited(second)+'.',
    'single property needs '+subject);
  scores[split].atomic_total++;scores[split].atomic++;
  eq(ask('what is '+subject,'en'),subject+' is '+klass+' '+cited(first)+'.',
    'single property class '+subject);
  scores[split].atomic_total++;scores[split].atomic++;
}
const queryMilliseconds=Number(process.hrtime.bigint()-durationStart)/1e6;
eq(ask('que es devc000 y que requiere'),
  answer('devc000',subjects[0].klass,subjects[0].need,subjects[0].first,subjects[0].second,'es'),
  'early entity retrievable after >200 subsequent segments');
scores.controls+=1;
eq(ask('que es ausente999 y que requiere'),
 'Falta evidencia para combinar ambas propiedades.','unseen subject: refuse fabrication');
scores.controls++;
ok(!ask('que es devc000 y que requiere zolv000').includes(cited(subjects[0].first)),
  'mixed-subject request cannot fabricate a combined statement');
scores.controls++;
// Confirm raw archive is unchanged, and the native program retains the prior factual knowledge.
ok(ask('que es tatuy').includes('animal'),'E025 memory preserved after >200 context writes');
eq(ask('@ctx status').startsWith('CTX n='),true,'E027 status retained');
eq(ask('@ctx clear'),'CTX vaciado.','E027 physical archive deletion');
cursor=0;
eq(ask('y que requiere'),'Necesito una entidad o referencia anterior.',
  'clear invalidates last conversational entity');
eq(ask('que es devc000 y que requiere'),'Falta evidencia para combinar ambas propiedades.',
  'cleared archive cannot leak contextual facts');
const cleanClass=add('devc000 es nuevo');
eq(ask('que es devc000'),'devc000 es nuevo '+cited(cleanClass)+'.',
  'reused source index does not resurrect earlier contradictory evidence');
ok(ask('que es tatuy').includes('animal'),'clear leaves original E025 learned facts');

const report={version:'E028-Context-Reason-1-dev',checks,app_turns:calls,
  validated_subjects:subjects.length,unrelated_long_fragments:extra,
  scores,query_elapsed_ms:Math.round(queryMilliseconds),
  measured_state_bytes:fs.statSync(state).size,
  tests:['E027 state migration without conversion','entity recognition',
    'two-sourced-fact composition ES/EN','single-relation retrieval ES/EN',
    'multiword entities and values','context followups','pronouns',
    'conflicting and negated evidence abstention','unknown and mixed subjects',
    'large-context retrieval','old E025 knowledge','archive clear/reuse'],
  scope:'Narrow deterministic assertion and question grammar in XI; no general semantic extraction or generative responses'};
fs.writeFileSync(path.join(out,'results.json'),JSON.stringify(report,null,2)+'\n');
console.log(JSON.stringify(report,null,2));
