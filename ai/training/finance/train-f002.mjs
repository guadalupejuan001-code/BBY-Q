#!/usr/bin/env node
// External curriculum, build, transport and independent assertions only.
// Runtime inference and persistent knowledge remain in the existing XI/Ether agent.
import fs from 'node:fs';
import path from 'node:path';
import assert from 'node:assert/strict';
import {execFileSync} from 'node:child_process';
import {createHash} from 'node:crypto';
import {gzipSync} from 'node:zlib';
import {fileURLToPath} from 'node:url';
import {rows as oldRows,sources,dialogues} from './curriculum.mjs';
import {additionalRows,fillers,prefixes,intentAliases,extraSources} from './extension.mjs';
const HERE=path.dirname(fileURLToPath(import.meta.url));
const sha=b=>createHash('sha256').update(b).digest('hex');
const save=(p,x)=>fs.writeFileSync(p,JSON.stringify(x,null,2)+'\n');
const jsonl=(p,x)=>fs.writeFileSync(p,x.map(r=>JSON.stringify(r)).join('\n')+'\n');
const all=[...oldRows,...additionalRows];
const money=n=>{const x=BigInt(n),a=x<0n?-x:x;return `${x<0n?'-':''}${a/100n}.${String(a%100n).padStart(2,'0')}`;};
function exportCorpus(out){
 fs.mkdirSync(out,{recursive:true});
 assert.equal(new Set(all.map(x=>x.term)).size,all.length);
 for(const r of all)for(const [rel,value] of [['es',r.definition],['requiere',r.requirement]])assert.ok(Buffer.byteLength(`${r.term} ${rel} ${value}`)<=224);
 const concepts=additionalRows.flatMap(r=>[
  {id:r.id+'-def',group:r.id,kind:'definition',messages:[{role:'user',content:'que es '+r.term},{role:'assistant',content:`${r.term} es ${r.definition}.`}]},
  {id:r.id+'-req',group:r.id,kind:'requirement',messages:[{role:'user',content:'que requiere '+r.term},{role:'assistant',content:`${r.term} requiere ${r.requirement}.`}]}
 ]);
 const styles=all.flatMap(r=>['oye, explicame ','pz hablame de ','mira necesito entender ','esk no entiendo '].map((p,i)=>({id:r.id+'-f002-style-'+i,group:r.id,kind:'style',messages:[{role:'user',content:p+r.term},{role:'assistant',content:`${r.term} es ${r.definition}.`}]})));
 const numeric=[];
 for(let i=1;i<=640;i++){
  const q=BigInt(i%41+1),p=BigInt(100+i*7),c=BigInt(40+i*3),fixed=BigInt(i*11+1);
  const train=i<=512, split=train?'train':'eval';
  const scenarios=[
   {family:'contribution',question:`Ejemplo ficticio: precio ${money(p)} USD y coste variable ${money(c)} USD por unidad. ¿Contribucion por unidad?`,answer:`${money(p-c)} USD por unidad, antes de costes fijos y otros gastos.`,result:String(p-c)},
   {family:'break_even',question:`Ejemplo ficticio: coste fijo ${money(fixed)} USD, precio ${money(p)} USD, coste variable ${money(c)} USD. ¿Unidades enteras para cubrir estos costes?`,answer:`${(fixed+(p-c)-1n)/(p-c)} unidades; se redondea hacia arriba porque las unidades son enteras.`,result:String((fixed+(p-c)-1n)/(p-c))},
   {family:'cash',question:`Ejemplo ficticio: caja inicial ${money(fixed)} USD, cobros ${money(p*q)} USD y pagos ${money(c*q)} USD. ¿Caja final?`,answer:`${money(fixed+p*q-c*q)} USD. Es caja del ejemplo, no beneficio contable.`,result:String(fixed+p*q-c*q)},
   {family:'incremental',question:`Ejemplo ficticio: ${q} ventas adicionales a ${money(p)} USD, coste variable ${money(c)} USD por venta, sin costes fijos adicionales. ¿Contribucion adicional?`,answer:`${money(q*(p-c))} USD, bajo los supuestos indicados.`,result:String(q*(p-c))}
  ];
  for(const s of scenarios)numeric.push({id:`f002-${s.family}-${i}`,group:`f002-scenario-${i}`,split,kind:'synthetic_arithmetic',family:s.family,consumed_by_native_model:false,exact_result:s.result,messages:[{role:'user',content:s.question},{role:'assistant',content:s.answer}]});
 }
 const training=[...concepts,...styles,...numeric.filter(r=>r.split==='train')];
 const evaluation=numeric.filter(r=>r.split==='eval');
 const prompts=new Set(training.map(x=>x.messages[0].content));assert.equal(prompts.size,training.length);
 for(const x of evaluation)assert.ok(!prompts.has(x.messages[0].content));
 jsonl(path.join(out,'f002-conversations.train.jsonl'),training);
 jsonl(path.join(out,'f002-arithmetic.eval.jsonl'),evaluation);
 jsonl(path.join(out,'f002-native-facts.jsonl'),additionalRows.flatMap(r=>[['es',r.definition],['requiere',r.requirement]].map(([rel,v])=>({group:r.id,text:`${r.term} ${rel} ${v.toLowerCase()}`}))));
 save(path.join(out,'sources.json'),[...sources,...extraSources]);
 const report={new_concepts:additionalRows.length,total_concepts:all.length,new_native_facts:additionalRows.length*2,new_corpus_examples:training.length,new_numeric_train:numeric.filter(r=>r.split==='train').length,new_numeric_eval:evaluation.length,synthetic:true,contains_private_financial_data:false,numeric_corpus_consumed:false,split_scope:'Disjoint scenarios and prompts; templates remain shared. This export is not a model score.'};
 save(path.join(out,'manifest.json'),report);return report;
}
function run(runtime,prior,out){
 runtime=path.resolve(runtime);prior=path.resolve(prior);out=path.resolve(out);fs.mkdirSync(out,{recursive:true});
 const prevApp=path.join(prior,'native/BBY-Q-E034-F001.rxe'),prevState=path.join(prior,'native/finance-f001.rvp');
 const expectedApp='a0edbe6122beb5ab57d0e2dbd60c26524bc946737806eb71f2ed133fde068a28';
 const expectedState='da99260c3a773b3a42e40bc09f1f6e67990dd9f4ed6c96ec030e0f2e692498ca';
 assert.equal(sha(fs.readFileSync(prevApp)),expectedApp);assert.equal(sha(fs.readFileSync(prevState)),expectedState);
 const corpus=exportCorpus(path.join(out,'corpus'));
 const inherited=JSON.parse(fs.readFileSync(path.join(prior,'native/results.json'),'utf8'));
 const appBytes=fs.readFileSync(prevApp),offset=appBytes.indexOf(Buffer.from('RXE1\r\n\x1a\n','binary'));
 assert.equal(offset,158);const oldCode=path.join(out,'base-code.rxe'),oldXi=path.join(out,'base-source.xi');
 fs.writeFileSync(oldCode,appBytes.subarray(offset,offset+appBytes.readUInt32LE(32)));
 const exec=(...args)=>execFileSync(runtime,args,{encoding:'utf8',timeout:30000,maxBuffer:2**22}).trimEnd();
 exec('disassemble',oldCode,oldXi);
 const original=fs.readFileSync(oldXi,'utf8');assert.ok(!original.includes('8800000000000000'),'reserved scratch namespace already used');
 const normalizer=path.join(out,'query-normalizer.xi');execFileSync(process.execPath,[path.join(HERE,'build-normalizer.mjs'),normalizer]);
 const combined=path.join(out,'combined.xi'),code=path.join(out,'f002-code.rxe');
 fs.writeFileSync(combined,fs.readFileSync(normalizer,'utf8')+original.replace(/^#!reverse-pc-machine-v1\s*/,''));
 exec('compile',combined,code,'BBY Q F002 native economic knowledge');
 const sourceDigest=sha(fs.readFileSync(combined));
 const preApp=path.join(out,'pretraining.rxe');exec('pack-app',code,prevState,preApp,'org.reverse.bbyq','BBY Q','F002-1',sourceDigest.slice(0,40));
 const candidate=path.join(out,'finance-f002.rvp');fs.copyFileSync(prevState,candidate);
 let checks=0;const stats={};const transcripts=path.join(out,'transcripts.jsonl');fs.writeFileSync(transcripts,'');
 const eq=(a,b,label)=>{assert.equal(a,b,label);checks++;if(checks%25===0)console.log('PASS '+checks+' '+label);};
 function ask(text,state,app=preApp,phase='test',lang='es'){
  assert.ok(Buffer.byteLength(text)<=255,'input too long '+text);
  const start=performance.now();const answer=exec('app-turn',app,state,state,lang,text);
  fs.appendFileSync(transcripts,JSON.stringify({phase,input:text,output:answer,ms:Math.round((performance.now()-start)*100)/100})+'\n');return answer;
 }
 const count=(state,app=preApp)=>{const m=ask('@ctx status',state,app,'archive-audit').match(/^CTX n=(\d+)/);assert.ok(m);return Number(m[1]);};
 eq(count(candidate),160,'requires the exact F001 archive, not a private populated state');
 const baseline=path.join(out,'baseline-copy.rvp');fs.copyFileSync(prevState,baseline);
 stats.style_before=[];
 for(const q of ['oye que es ingreso','pz que es beneficio','mira que es farmear dinero'])stats.style_before.push({input:q,output:ask(q,baseline,prevApp,'baseline-style')});
 stats.baseline_new_definitions_exact=0;
 for(const [j,r] of additionalRows.entries()){
  const expected=`${r.term} es ${r.definition.toLowerCase()} [#${String(160+2*j).padStart(3,'0')}].`;
  stats.baseline_new_definitions_exact+=Number(ask('que es '+r.term,baseline,prevApp,'baseline-new')===expected);
 }
 const teachingStart=performance.now();
 for(const [j,r] of additionalRows.entries())for(const [k,rel,value] of [[0,'es',r.definition],[1,'requiere',r.requirement]]){
  const id=160+2*j+k;
  eq(ask('@ctx add '+r.term+' '+rel+' '+value.toLowerCase(),candidate,preApp,'ingestion'),'CTX guardado #'+String(id).padStart(3,'0'),'ingest '+id);
 }
 stats.ingestion_ms=Math.round(performance.now()-teachingStart);eq(count(candidate),320,'all facts present');
 const candidateHash=sha(fs.readFileSync(candidate));
 const evaluation=path.join(out,'evaluation-copy.rvp');fs.copyFileSync(candidate,evaluation);
 const atom=(r,i,type)=>`${r.term} ${type==='definition'?'es':'requiere'} ${r[type].toLowerCase()} [#${String(2*i+(type==='definition'?0:1)).padStart(3,'0')}].`;
 stats.old_fact_retention=0;stats.new_fact_dialogue=0;stats.operator_style=0;
 for(const [i,r] of all.entries()){
  eq(ask('que es '+r.term,evaluation),atom(r,i,'definition'),'definition '+r.term);
  eq(ask('que requiere '+r.term,evaluation),atom(r,i,'requirement'),'requirement '+r.term);
  if(i<oldRows.length)stats.old_fact_retention+=2;else{
   eq(ask('que es '+r.term+' y que requiere',evaluation),atom(r,i,'definition')+' '+atom(r,i,'requirement'),'composition '+r.term);
   eq(ask('y que requiere',evaluation),atom(r,i,'requirement'),'followup '+r.term);stats.new_fact_dialogue+=4;
  }
  const p=['oye, explicame ','pz hablame de ','mira necesito entender ','esk no entiendo '][i%4];
  eq(ask(p+r.term,evaluation),atom(r,i,'definition'),'style '+r.term);stats.operator_style++;
 }
 const reserves=[5,36,87,132];
 for(const [from,to] of prefixes)for(const i of reserves){
  const r=all[i],type=to==='que requiere '?'requirement':'definition';
  eq(ask('¿OYE, '+from.replaceAll('que ','qué ')+r.term+'?',evaluation),atom(r,i,type),'prefix heldout '+from+r.term);stats.operator_style++;
 }
 for(const f of fillers)for(const i of reserves){
  const r=all[i];eq(ask(f+'mira que es '+r.term,evaluation),atom(r,i,'definition'),'filler combination');stats.operator_style++;
 }
 for(const [question,canonical] of intentAliases){
  const term=canonical.replace(/^que requiere /,'');const i=all.findIndex(r=>r.term===term);assert.ok(i>=0);
  eq(ask('pz '+question,evaluation),atom(all[i],i,'requirement'),'intent '+question);stats.operator_style++;
 }
 stats.negative_controls=0;
 for(const q of ['que es conceptoinexistente y que requiere','oye que es conceptoinexistente y que requiere']){
  eq(ask(q,evaluation),'Falta evidencia para combinar ambas propiedades.','unknown evidence');stats.negative_controls++;
 }
 const oldControl=path.join(out,'old-control.rvp'),newControl=path.join(out,'new-control.rvp');
 fs.copyFileSync(candidate,oldControl);fs.copyFileSync(candidate,newControl);
 for(const q of ['hola','hello','no quiero farmear dinero','compra bitcoin','invierte todo','no autorice ninguna compra','que es calculadora','calcula 2 mas 3','@ctx status']){
  const lang=q==='hello'?'en':'es';eq(ask(q,newControl,preApp,'regression',lang),ask(q,oldControl,prevApp,'regression-reference',lang),'unmodified path '+q);stats.negative_controls++;
 }
 eq(count(evaluation),320,'queries must not become new factual statements');
 // A new state from the packed app must already include the trained knowledge.
 const app=path.join(out,'BBY-Q-F002.rxe');exec('pack-app',code,candidate,app,'org.reverse.bbyq','BBY Q','F002-1',sourceDigest.slice(0,40));
 const reopened=path.join(out,'fresh-from-app.rvp');exec('app-init',app,reopened);
 eq(ask('¿Oye, qué es economía unitaria?',reopened,app,'fresh-seed'),atom(all[80],80,'definition'),'packed learned seed');
 eq(ask('pz como monetizo reverse',reopened,app,'fresh-seed'),atom(all.find(r=>r.term==='monetizar reverse'),all.findIndex(r=>r.term==='monetizar reverse'),'requirement'),'packed prior knowledge');
 eq(count(reopened,app),320,'packed archive preserved');
 eq(sha(fs.readFileSync(candidate)),candidateHash,'evaluation did not change published candidate');
 eq(sha(fs.readFileSync(prevState)),expectedState,'original F001 preserved');eq(sha(fs.readFileSync(prevApp)),expectedApp,'original E034 preserved');
 const compressed=gzipSync(fs.readFileSync(candidate),{level:9});fs.writeFileSync(path.join(out,'finance-f002.rvp.gz'),compressed);fs.writeFileSync(path.join(out,'finance-f002.rvp.gz.b64'),compressed.toString('base64')+'\n');
 const report={version:'F002-1',checks,...stats,total_concepts:all.length,new_native_facts_ingested:160,total_native_facts:320,
  earlier_corpus_examples:inherited.corpus_training_examples,new_corpus_examples:corpus.new_corpus_examples,total_corpus_examples:inherited.corpus_training_examples+corpus.new_corpus_examples,
  earlier_numeric_eval_examples:512,new_numeric_eval_examples:corpus.new_numeric_eval,total_numeric_eval_examples:512+corpus.new_numeric_eval,
  arithmetic_corpus_consumed:false,native_scope:'Persistent contextual knowledge acquisition plus designed XI query normalization; not neural fine-tuning, induced syntax or open economic reasoning.',
  source_sha256:sourceDigest,app_sha256:sha(fs.readFileSync(app)),checkpoint_sha256:candidateHash,checkpoint_bytes:fs.statSync(candidate).size,checkpoint_gzip_bytes:compressed.length,
  original_f001_sha256:expectedState,original_e034_app_sha256:expectedApp,originals_preserved:true,production_deployed:false,android_tested:false,financial_execution_enabled:false,
  limitations:['255 input bytes inherited from ABI','512 contextual entries inherited; 320 used','Up to four leading discourse fillers','Designed prefix/intent mappings, not unrestricted language understanding','F002 candidate derives from E034/F001; no overwrite of REVERSE E038/X04 or operator memory','Numeric corpus generated and checked, not learned by the native agent']};
 save(path.join(out,'results.json'),report);console.log(JSON.stringify(report,null,2));
}
const args=process.argv.slice(2);
if(args[0]==='export'&&args.length===2)console.log(JSON.stringify(exportCorpus(path.resolve(args[1])),null,2));
else if(args[0]==='train'&&args.length===4)run(...args.slice(1));
else throw Error('Usage: node train-f002.mjs export OUTPUT | train RUNTIME F001_ARTIFACT_DIR OUTPUT');
