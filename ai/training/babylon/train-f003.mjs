#!/usr/bin/env node
// Preparation, transport and independent assertions only. All model responses
// and persistent knowledge are executed by the unchanged F002 XI/Ether program.
import fs from 'node:fs';
import path from 'node:path';
import assert from 'node:assert/strict';
import {execFileSync} from 'node:child_process';
import {createHash} from 'node:crypto';
import {gzipSync,gunzipSync} from 'node:zlib';
import {lessons,facts,source} from './lessons.mjs';
const sha=b=>createHash('sha256').update(b).digest('hex');
const save=(p,x)=>fs.writeFileSync(p,JSON.stringify(x,null,2)+'\n');
const jsonl=(p,x)=>fs.writeFileSync(p,x.map(r=>JSON.stringify(r)).join('\n')+'\n');
const APP_HASH='02edd2efc162e61a98b55d24b17301a6a2d909e32109401afd8c9ad9b62b5e41';
const STATE_HASH='80e10341872a93d5a9ca648958c7b1ebd38212209503f9cb558d6d1e7e5b0215';
const RUNTIME_HASH='ef0c3a709121b8fd3cf4c996808ecfef8b60a7065d3f9c802280c58dc9370d84';
export function exportData(out){
 fs.mkdirSync(out,{recursive:true});
 assert.equal(lessons.length,64);assert.equal(new Set(lessons.map(x=>x.term)).size,64);
 const native=facts();for(const f of native)assert.ok(Buffer.byteLength('@ctx add '+f.text)<=255);
 const corpus=lessons.flatMap(r=>[
  ['definition','que es '+r.term,`${r.term} es ${r.definition}.`],
  ['requirement','que requiere '+r.term,`${r.term} requiere ${r.requirement}.`],
  ['operator','oye, explicame '+r.term,`${r.term} es ${r.definition}.`],
  ['operator','pz hablame de '+r.term,`${r.term} es ${r.definition}.`],
  ['operator','mira necesito entender '+r.term,`${r.term} es ${r.definition}.`],
  ['operator','esk no entiendo '+r.term,`${r.term} es ${r.definition}.`],
  ['composition','que es '+r.term+' y que requiere',`${r.term} es ${r.definition}. ${r.term} requiere ${r.requirement}.`]
 ].map(([kind,q,a],i)=>({id:r.id+'-'+i,group:r.id,kind,source_pages:r.pages,origin:r.origin,consumed_as_dialogue_training:false,messages:[{role:'user',content:q},{role:'assistant',content:a}]})));
 assert.equal(new Set(corpus.map(x=>x.messages[0].content)).size,corpus.length);
 const exam=[];
 // Synthetic numbers never taught to the model. This is an exam oracle, not inference.
 for(let i=0;i<64;i++){
  const n=1000+37*i;
  exam.push({id:`f003-exam-save-${i}`,kind:'unseen_numeric_scenario',input:`Ejemplo ficticio: ingreso ${n}.00 USD y reserva del 10 por ciento. Cuanto se reserva`,expected_cents:n*10,consumed:false});
  exam.push({id:`f003-exam-plan-${i}`,kind:'unseen_numeric_scenario',input:`Ejemplo ficticio: repartir ${n}.00 USD segun el plan narrativo 10 70 20 de Dabasir`,expected_cents:{reserve:n*10,living:n*70,debt:n*20},consumed:false});
 }
 jsonl(path.join(out,'native-facts.jsonl'),native);jsonl(path.join(out,'conversations.prepared.jsonl'),corpus);jsonl(path.join(out,'numeric.eval.jsonl'),exam);
 save(path.join(out,'source.json'),source);save(path.join(out,'lessons.json'),lessons);
 const manifest={concepts:64,native_facts:128,prepared_dialogues:corpus.length,reserved_numeric_scenarios:exam.length,book_lessons:56,modern_applications:3,critical_distinctions:5,full_book_verbatim_ingested:false,dialogue_corpus_consumed:false,numeric_corpus_consumed:false,contains_private_financial_data:false};
 save(path.join(out,'manifest.json'),manifest);return manifest;
}
function train(runtime,prior,pdf,out){
 runtime=path.resolve(runtime);prior=path.resolve(prior);pdf=path.resolve(pdf);out=path.resolve(out);fs.mkdirSync(out,{recursive:true});
 const oldApp=path.join(prior,'modelo/BBY-Q-F002.rxe'),oldZip=path.join(prior,'modelo/finance-f002.rvp.gz');
 assert.equal(sha(fs.readFileSync(runtime)),RUNTIME_HASH,'exact verified runtime');assert.equal(sha(fs.readFileSync(pdf)),source.sha256,'source PDF changed');
 const oldBytes=fs.readFileSync(oldApp),original=gunzipSync(fs.readFileSync(oldZip));
 assert.equal(sha(oldBytes),APP_HASH,'exact F002 capsule');assert.equal(sha(original),STATE_HASH,'exact F002 seed');
 const oldFacts=fs.readFileSync(path.join(prior,'datos/hechos-nativos.jsonl'),'utf8').trim().split('\n').map(JSON.parse);
 assert.equal(oldFacts.length,320);for(const f of facts())assert.ok(!oldFacts.some(x=>x.text===f.text),'duplicate prior fact');
 const corpus=exportData(path.join(out,'corpus'));
 const codeOffset=oldBytes.indexOf(Buffer.from('RXE1\r\n\x1a\n','binary'));assert.ok(codeOffset>=64 && codeOffset<4096,'valid variable-length capsule header');
 const code=path.join(out,'unchanged-f002-code.rxe'),xi=path.join(out,'unchanged-f002-code.xi');
 const codeLength=oldBytes.readUInt32LE(32);assert.ok(codeLength>0 && codeOffset+codeLength+original.length<=oldBytes.length,'valid code/seed bounds');const oldCode=oldBytes.subarray(codeOffset,codeOffset+codeLength);fs.writeFileSync(code,oldCode);
 const exec=(...args)=>execFileSync(runtime,args,{encoding:'utf8',timeout:30000,maxBuffer:2**22}).trimEnd();
 exec('disassemble',code,xi);
 const candidate=path.join(out,'finance-f003.rvp');fs.writeFileSync(candidate,original);
 const transcript=path.join(out,'transcripts.jsonl');fs.writeFileSync(transcript,'');
 let checks=0;const started=Date.now();const stats={};
 const eq=(a,b,label)=>{assert.equal(a,b,label);checks++;if(checks%32===0)console.log(`PASS ${checks} ${label}`);};
 function ask(input,state,phase,app=oldApp){
  assert.ok(Buffer.byteLength(input)<=255,'input size');const t=performance.now();const output=exec('app-turn',app,state,state,'es',input);
  fs.appendFileSync(transcript,JSON.stringify({phase,input,output,ms:Math.round((performance.now()-t)*100)/100})+'\n');return output;
 }
 const count=(state,app=oldApp)=>{const s=ask('@ctx status',state,'archive',app);const m=s.match(/^CTX n=(\d+)/);assert.ok(m,s);return Number(m[1]);};
 const atom=(f,i)=>`${f.text} [#${String(i).padStart(3,'0')}].`;
 eq(count(candidate),320,'exact previous archive');
 const baseline=path.join(out,'baseline.rvp');fs.writeFileSync(baseline,original);stats.baseline_exact_new_definitions=0;
 const ff=facts();
 for(const [i,r] of lessons.entries())stats.baseline_exact_new_definitions+=Number(ask('que es '+r.term,baseline,'before')===atom(ff[2*i],320+2*i));
 eq(count(baseline),320,'baseline queries do not teach');
 const t=performance.now();
 for(const f of ff)eq(ask('@ctx add '+f.text,candidate,'learning'),'CTX guardado #'+String(f.expected_archive_id).padStart(3,'0'),'learn '+f.id);
 stats.learning_ms=Math.round(performance.now()-t);eq(count(candidate),448,'128 added facts');
 const trainedHash=sha(fs.readFileSync(candidate));const evaluate=path.join(out,'evaluation.rvp');fs.copyFileSync(candidate,evaluate);
 stats.previous_facts_retained=0;
 for(const [i,f] of oldFacts.entries()){
  const [term,relation]=f.term?[f.term,f.relation]:f.text.includes(' requiere ')?[f.text.split(' requiere ')[0],'requiere']:[f.text.split(' es ')[0],'es'];
  eq(ask((relation==='es'?'que es ':'que requiere ')+term,evaluate,'retention'),atom(f,i),'retain '+i);stats.previous_facts_retained++;
 }
 stats.new_atomic_answers=0;stats.compositions=0;stats.followups=0;stats.operator_variants=0;
 for(const [i,r] of lessons.entries()){
  const d=atom(ff[2*i],320+2*i),q=atom(ff[2*i+1],321+2*i);
  eq(ask('que es '+r.term,evaluate,'new-definition'),d,'definition '+i);
  eq(ask('que requiere '+r.term,evaluate,'new-requirement'),q,'requirement '+i);stats.new_atomic_answers+=2;
  eq(ask('que es '+r.term+' y que requiere',evaluate,'composition'),d+' '+q,'composition '+i);stats.compositions++;
  eq(ask('y que requiere',evaluate,'followup'),q,'followup '+i);stats.followups++;
  const prefix=['oye, explicame ','pz hablame de ','mira necesito entender ','esk no entiendo '][i%4];
  eq(ask(prefix+r.term,evaluate,'operator'),d,'operator '+i);stats.operator_variants++;
 }
 eq(count(evaluate),448,'queries preserve archive size');stats.unknowns=0;
 for(const term of ['rendimiento garantizado de babilonia','precio futuro infalible','cura numero ocho inexistente','ganancia exacta del proximo mes']){
  eq(ask('que es '+term+' y que requiere',evaluate,'unknown'),'Falta evidencia para combinar ambas propiedades.','unknown '+term);stats.unknowns++;
 }
 const app=path.join(out,'BBY-Q-F003.rxe');exec('pack-app',code,candidate,app,'org.reverse.bbyq','BBY Q','F003-Babylon',sha(fs.readFileSync(xi)).slice(0,40));
 const packed=fs.readFileSync(app),offset=packed.indexOf(Buffer.from('RXE1\r\n\x1a\n','binary'));
 eq(sha(packed.subarray(offset,offset+packed.readUInt32LE(32))),sha(oldCode),'XI executable instructions unchanged');
 const fresh=path.join(out,'reopened.rvp');exec('app-init',app,fresh);eq(count(fresh,app),448,'reopen seed');stats.reopened_answers=0;
 for(const i of [0,1,2,8,12,15,24,25,31,32,37,45,48,55,56,57,58,59,60,61,62,63]){
  eq(ask('¿Oye, qué es '+lessons[i].term+'?',fresh,'reopen',app),atom(ff[2*i],320+2*i),'reopen '+i);stats.reopened_answers++;
 }
 eq(ask('pz como monetizo reverse',fresh,'prior-operator',app),atom(oldFacts[7],7),'prior economic intent');eq(count(fresh,app),448,'fresh queries preserve facts');
 // Exploratory failures remain visible; these are not added to the pass count.
 const probe=path.join(out,'exploratory.rvp');exec('app-init',app,probe);
 const probes=[['Si gano 2000 dolares cuanto es el diez por ciento','200'],['Tengo 1000 dolares divide en ahorro gastos y deuda como Dabasir','100, 700, 200'],['como aplico el libro a mi proyecto reverse','open application, not exact keyword lookup'],['explicame por que ahorrar no garantiza riqueza','open reasoning, not exact keyword lookup']];
 stats.exploratory=probes.map(([input,expected])=>({input,expected,actual:ask(input,probe,'exploratory-not-scored',app)}));
 eq(sha(fs.readFileSync(candidate)),trainedHash,'exams do not mutate release seed');eq(sha(fs.readFileSync(oldApp)),APP_HASH,'F002 capsule untouched');eq(sha(gunzipSync(fs.readFileSync(oldZip))),STATE_HASH,'F002 state untouched');
 const zipped=gzipSync(fs.readFileSync(candidate),{level:9});fs.writeFileSync(path.join(out,'finance-f003.rvp.gz'),zipped);
 const report={campaign:'F003-Babylon',completed:true,checks,...stats,total_concepts:224,total_facts:448,new_concepts:64,new_facts:128,corpus,source,runtime_sha256:RUNTIME_HASH,prior_app_sha256:APP_HASH,prior_checkpoint_sha256:STATE_HASH,source_code_sha256:sha(fs.readFileSync(xi)),code_sha256:sha(oldCode),code_unchanged:true,app_sha256:sha(packed),checkpoint_sha256:trainedHash,checkpoint_bytes:fs.statSync(candidate).size,checkpoint_gzip_bytes:zipped.length,elapsed_ms:Date.now()-started,native_scope:'Persistent structured knowledge acquisition in XI/Ether, not neural weight tuning or full-book memorization.',evaluation_scope:'Recall of taught facts, designed query forms, composition of two stored properties, followup, retention and seed reopening. Not heldout semantic generalization.',financial_execution_enabled:false,android_updated:false,operator_memory_touched:false,newest_agent_replaced:false,limits:['255 input bytes inherited','512 contextual entries inherited, 448 occupied','Only supported query grammar','Numeric exam prepared, not taught or scored as successful','F003 derives from E034/F001/F002, not a replacement for the newer production agent']};
 save(path.join(out,'results.json'),report);console.log(JSON.stringify(report,null,2));
}
const a=process.argv.slice(2);
if(a[0]==='export'&&a.length===2)console.log(JSON.stringify(exportData(path.resolve(a[1])),null,2));
else if(a[0]==='train'&&a.length===5)train(...a.slice(1));
else throw Error('Usage: node train-f003.mjs export OUT | train RUNTIME F002_PACKAGE PDF OUT');
