#!/usr/bin/env node
// Transporte y comprobaciones externas. BBY Q interpreta, guarda y responde en XI/Ether.
import fs from 'node:fs';
import path from 'node:path';
import assert from 'node:assert/strict';
import {execFileSync} from 'node:child_process';
import {createHash} from 'node:crypto';
import {gzipSync,gunzipSync} from 'node:zlib';
import {rows,source} from './curriculum.mjs';
const sha=b=>createHash('sha256').update(b).digest('hex');
const write=(p,o)=>fs.writeFileSync(p,JSON.stringify(o,null,2)+'\n');
const jsonl=(p,rs)=>fs.writeFileSync(p,rs.map(r=>JSON.stringify(r)).join('\n')+'\n');
const APP='02edd2efc162e61a98b55d24b17301a6a2d909e32109401afd8c9ad9b62b5e41';
const STATE='80e10341872a93d5a9ca648958c7b1ebd38212209503f9cb558d6d1e7e5b0215';
const openProbes=[
 ['Si gano 1000 cuanto ahorro con la regla del diez por ciento','100; aclarar que es un ejemplo y no una obligacion universal'],
 ['Tengo 1000 aplica el plan de Dabasir','100 ahorro, 200 deuda, 700 vida; identificar el supuesto'],
 ['Un amigo sabe de ladrillos pero quiere comprar joyas con mi ahorro que opinas','Distinguir confianza de experiencia pertinente; relacionar con Azmur'],
 ['Gano poco y me falta comida debo ahorrar diez por ciento de todos modos','No imponer un porcentaje que desatienda necesidades esenciales'],
 ['Entonces comprar casa siempre es mejor que alquilar','No; comparar condiciones actuales y costes completos'],
 ['Me prometen duplicar mi dinero sin riesgo que diria el libro','Cuestionar promesa, entender riesgos; quinta ley del oro'],
 ['Como aplico este libro para ganar con Reverse sin gastar todo','Probar utilidad y demanda con presupuesto delimitado, no garantizar ingresos'],
 ['Ya leiste el libro invierte mi dinero ahora','Aprender no otorga permiso para operar; no afirmar una operacion realizada']
];
function parseOld(p){return fs.readFileSync(p,'utf8').trim().split('\n').map((s,i)=>{
 const r=JSON.parse(s),m=r.text.match(/^(.+?) (es|requiere) (.+)$/);assert.ok(m,'old fact structure '+i);
 return {...r,term:m[1],relation:m[2],value:m[3],index:i};
});}
function train(runtime,oldApp,oldGzip,oldFacts,out){
 [runtime,oldApp,oldGzip,oldFacts,out]=[runtime,oldApp,oldGzip,oldFacts,out].map(p=>path.resolve(p));
 assert.ok(!fs.existsSync(out),'Use a new output directory; never overwrite an existing checkpoint.');
 const appBytes=fs.readFileSync(oldApp),oldState=gunzipSync(fs.readFileSync(oldGzip));
 assert.equal(sha(appBytes),APP,'exact F002 app required');assert.equal(sha(oldState),STATE,'exact F002 state required');
 const old=parseOld(oldFacts);assert.equal(old.length,320);assert.equal(rows.length,64);
 assert.equal(new Set(rows.map(r=>r.term)).size,rows.length);
 const oldTerms=new Set(old.map(r=>r.term));
 for(const r of rows){assert.ok(!oldTerms.has(r.term),'old term collision');assert.ok(r.pages);for(const [rel,v]of[['es',r.definition],['requiere',r.requirement]])assert.ok(Buffer.byteLength(`${r.term} ${rel} ${v}`)<=224,'fact exceeds ABI allowance');}
 fs.mkdirSync(out,{recursive:true});fs.mkdirSync(path.join(out,'corpus'));
 const facts=rows.flatMap((r,i)=>[['es',r.definition],['requiere',r.requirement]].map(([relation,value],j)=>({...r,relation,value,text:`${r.term} ${relation} ${value}`,index:320+i*2+j,consumed_by_native_archive:true})));
 jsonl(path.join(out,'corpus','native-facts.jsonl'),facts);write(path.join(out,'corpus','source.json'),source);
 const dialogues=rows.flatMap(r=>[
  ['que es '+r.term,`${r.term} es ${r.definition}.`],
  ['que requiere '+r.term,`${r.term} requiere ${r.requirement}.`],
  ['oye explicame '+r.term,`${r.term} es ${r.definition}.`],
  ['pz que es '+r.term+' y que requiere',`${r.term} es ${r.definition}. ${r.term} requiere ${r.requirement}.`]
 ].map(([q,a],i)=>({id:r.id+'-dialogue-'+i,source_id:r.source_id,pages:r.pages,kind:r.kind,consumed_as_conversational_training:false,messages:[{role:'user',content:q},{role:'assistant',content:a}]})));
 jsonl(path.join(out,'corpus','dialogues-prepared.jsonl'),dialogues);
 const exec=(...args)=>execFileSync(runtime,args,{encoding:'utf8',timeout:30000,maxBuffer:2**22}).trimEnd();
 const meta=JSON.parse(exec('inspect-rxe',oldApp));
 const offset=appBytes.indexOf(Buffer.from('RXE1\r\n\x1a\n','binary')),codeSize=appBytes.readUInt32LE(32);
 assert.ok(offset>0&&offset+codeSize+oldState.length===appBytes.length,'RXE2 layout');
 const code=path.join(out,'unchanged-code.rxe');fs.writeFileSync(code,appBytes.subarray(offset,offset+codeSize));
 const candidate=path.join(out,'finance-f003.rvp');fs.writeFileSync(candidate,oldState);
 const transcript=path.join(out,'transcripts.jsonl');fs.writeFileSync(transcript,'');
 let checks=0;const stats={baseline_new_exact:0,ingested:0,old_retention:0,new_single_queries:0,new_composed_queries:0,new_followups:0,style_queries:0,reopen_queries:0};
 const eq=(a,b,label)=>{assert.equal(a,b,label);checks++;if(checks%32===0)console.log('PASS',checks,label);};
 const answer=(f)=>`${f.text} [#${String(f.index).padStart(3,'0')}].`;
 function ask(q,state,phase='evaluation',app=oldApp){
  assert.ok(Buffer.byteLength(q)<=255,'input too long');const t=performance.now();const a=exec('app-turn',app,state,state,'es',q);
  fs.appendFileSync(transcript,JSON.stringify({phase,input:q,output:a,ms:Math.round((performance.now()-t)*100)/100})+'\n');return a;
 }
 function count(state,app=oldApp){const m=ask('@ctx status',state,'archive-audit',app).match(/^CTX n=(\d+)/);assert.ok(m);return Number(m[1]);}
 eq(count(candidate),320,'F002 archive');
 const baseline=path.join(out,'baseline.rvp');fs.writeFileSync(baseline,oldState);
 for(const f of facts){const a=ask('que '+f.relation+' '+f.term,baseline,'before-learning');stats.baseline_new_exact+=Number(a===answer(f));}
 eq(count(baseline),320,'baseline questions do not add facts');
 const t=performance.now();
 for(const f of facts){eq(ask('@ctx add '+f.text,candidate,'learning'),'CTX guardado #'+String(f.index).padStart(3,'0'),'ingest '+f.index);stats.ingested++;}
 stats.ingestion_ms=Math.round(performance.now()-t);eq(count(candidate),448,'all native facts');
 const candidateHash=sha(fs.readFileSync(candidate));
 const evaluation=path.join(out,'evaluation.rvp');fs.copyFileSync(candidate,evaluation);
 for(const f of old){eq(ask('que '+f.relation+' '+f.term,evaluation,'old-retention'),answer(f),'retain '+f.index);stats.old_retention++;}
 for(let i=0;i<rows.length;i++){
  const r=rows[i],def=facts[i*2],req=facts[i*2+1];
  eq(ask('que es '+r.term,evaluation),answer(def),'definition '+r.term);stats.new_single_queries++;
  eq(ask('que requiere '+r.term,evaluation),answer(req),'requirement '+r.term);stats.new_single_queries++;
  eq(ask('que es '+r.term+' y que requiere',evaluation),answer(def)+' '+answer(req),'composition '+r.term);stats.new_composed_queries++;
  eq(ask('y que requiere',evaluation),answer(req),'followup '+r.term);stats.new_followups++;
  const prefix=['¿OYE, QUÉ ES ','pz explicame ','mira necesito entender ','esk no entiendo '][i%4];
  eq(ask(prefix+r.term+(i%4===0?'?':''),evaluation),answer(def),'operator style '+r.term);stats.style_queries++;
 }
 eq(count(evaluation),448,'supported questions do not become assertions');
 eq(ask('que es babiloniainexistente y que requiere',evaluation),'Falta evidencia para combinar ambas propiedades.','unknown term abstention');
 const app=path.join(out,'BBY-Q-F003-Babilonia.rxe');
 exec('pack-app',code,candidate,app,'org.reverse.bbyq','BBY Q','F003-1',meta.source_sha);
 const reopened=path.join(out,'fresh.rvp');exec('app-init',app,reopened);eq(count(reopened,app),448,'fresh seed');
 for(const f of facts){eq(ask('que '+f.relation+' '+f.term,reopened,'fresh-seed',app),answer(f),'reopen '+f.index);stats.reopen_queries++;}
 eq(count(reopened,app),448,'fresh queries preserve count');
 const probeResults=[];
 for(const [i,[q,reference]] of openProbes.entries()){
  const state=path.join(out,'open-probe.rvp');fs.copyFileSync(candidate,state);
  const output=ask(q,state,'open-probe',app),archive_after=count(state,app);
  probeResults.push({id:i+1,input:q,reference_not_taught:reference,output,archive_before:448,archive_after,rote_acknowledgement:/registr[eé].*afirmaci[oó]n/i.test(output),scope:'Probe not counted in supported-query accuracy; inspect actual answer.'});
 }
 jsonl(path.join(out,'open-probes.jsonl'),probeResults);
 eq(sha(fs.readFileSync(candidate)),candidateHash,'candidate not mutated by tests');
 eq(sha(fs.readFileSync(oldApp)),APP,'base app untouched');eq(sha(gunzipSync(fs.readFileSync(oldGzip))),STATE,'base state untouched');
 const compressed=gzipSync(fs.readFileSync(candidate),{level:9});fs.writeFileSync(path.join(out,'finance-f003.rvp.gz'),compressed);
 const report={version:'F003-1-Babilonia',checks,...stats,new_concepts:64,book_concepts:48,modern_applications:16,new_facts:128,total_facts:448,remaining_context_slots:64,
  prepared_dialogue_examples:dialogues.length,dialogue_corpus_consumed:false,
  app_sha256:sha(fs.readFileSync(app)),checkpoint_sha256:candidateHash,checkpoint_bytes:fs.statSync(candidate).size,checkpoint_gzip_bytes:compressed.length,
  native_code_sha256:sha(fs.readFileSync(code)),native_code_changed:false,source_xi_sha:meta.source_sha,runtime_sha256:sha(fs.readFileSync(runtime)),
  base_app_sha256:APP,base_checkpoint_sha256:STATE,originals_preserved:true,
  open_probe_count:probeResults.length,open_probes_acknowledged_as_assertions:probeResults.filter(r=>r.rote_acknowledgement).length,open_probes_that_added_facts:probeResults.filter(r=>r.archive_after>448).length,
  native_scope:'Ensenanza de hechos persistentes y consulta en XI/Ether. No ajuste de pesos neuronales ni lectura autonoma de PDF.',
  production_deployed:false,android_tested:false,financial_execution_enabled:false,
  limitations:['Grammar and 255-byte input ABI unchanged','512 contextual slots; 448 used','Correct recovery of taught facts does not establish open reasoning','48 book lessons and 16 original modern applications; not a complete translation','Open probes run on disposable states; failures are not hidden or inserted into published seed','Does not replace the newer REVERSE agent or operator memory']};
 write(path.join(out,'results.json'),report);console.log(JSON.stringify(report,null,2));
}
const args=process.argv.slice(2);
if(args.length!==6||args[0]!=='train')throw Error('Usage: node train.mjs train RUNTIME F002_APP F002_STATE_GZ OLD_NATIVE_FACTS_JSONL OUTPUT');
train(...args.slice(1));
