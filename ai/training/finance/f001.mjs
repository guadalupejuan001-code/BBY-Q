#!/usr/bin/env node
// Dataset construction and black-box transport/oracles only.
// Learning, retrieval and answer production execute in the unchanged XI capsule.
import fs from 'node:fs';
import path from 'node:path';
import assert from 'node:assert/strict';
import {createHash} from 'node:crypto';
import {gzipSync,gunzipSync} from 'node:zlib';
import {execFileSync} from 'node:child_process';
import {rows,dialogues,sources,version} from './curriculum.mjs';
const hash=x=>createHash('sha256').update(x).digest('hex');
const save=(file,x)=>fs.writeFileSync(file,JSON.stringify(x,null,2)+'\n');
const jsonl=(file,x)=>fs.writeFileSync(file,x.map(v=>JSON.stringify(v)).join('\n')+'\n');
const cents=x=>{const n=BigInt(x),a=n<0n?-n:n;return `${n<0n?'-':''}${a/100n}.${String(a%100n).padStart(2,'0')}`;};
const facts=rows.flatMap(r=>[
 {id:r.id+'-definition',term:r.term,relation:'es',value:r.definition.toLowerCase()},
 {id:r.id+'-requirement',term:r.term,relation:'requiere',value:r.requirement.toLowerCase()}
]).map(r=>({...r,text:`${r.term} ${r.relation} ${r.value}`}));
function exportData(out){
 fs.mkdirSync(out,{recursive:true});
 assert.equal(new Set(rows.map(r=>r.term)).size,rows.length);
 for(const r of facts){assert.ok(r.term && r.value);assert.ok(Buffer.byteLength(r.text)<=224);assert.ok(Buffer.byteLength('@ctx add '+r.text)<=255);}
 assert.ok(facts.length<=512);
 const canonical=rows.flatMap(r=>['que es ','que requiere '].map((p,i)=>({id:r.id+'-canonical-'+i,group:r.id,kind:'concept',messages:[{role:'user',content:p+r.term},{role:'assistant',content:r.term+(i?' requiere '+r.requirement:' es '+r.definition)+'.'}]})));
 const styled=rows.flatMap(r=>['oye que es ','pz que es ','mira que es ','explicame ','que significa ','esk no entiendo '].map((p,i)=>({id:r.id+'-style-'+i,group:r.id,kind:'operator_style',consumed_by_f001:false,messages:[{role:'user',content:p+r.term},{role:'assistant',content:r.term+' significa '+r.definition+'. Para analizarlo hace falta '+r.requirement+'.'}]})));
 const math=[];
 for(let i=1;i<=4608;i++){
  const p=500n+BigInt(i%997),c=200n+BigInt(i%211),q=BigInt(1+i%37),f=100n+3n*BigInt(i);
  const revenue=p*q,variable=c*q,result=revenue-variable-f;
  assert.equal(result+variable+f,revenue);
  const split=i<=4096?'train':'eval';
  math.push({id:'arith-'+String(i).padStart(5,'0'),group:'scenario-'+i,split,kind:'synthetic_arithmetic',consumed_by_f001:false,
   variables:{price_cents:String(p),unit_cost_cents:String(c),units:String(q),fixed_cents:String(f),profit_cents:String(result)},
   messages:[{role:'user',content:`Ejemplo ficticio: vendo ${q} unidades a ${cents(p)} USD; coste unitario ${cents(c)} USD y fijo ${cents(f)} USD. ¿Cuanto queda?`},
    {role:'assistant',content:`Ingresos: ${cents(revenue)} USD. Coste variable: ${cents(variable)} USD. Resultado: ${cents(result)} USD, antes de gastos o impuestos no incluidos.`}]});
 }
 const training=[...canonical,...styled,...dialogues.map(d=>({...d,group:d.id,kind:'curated_dialogue',consumed_by_f001:false})),...math.filter(r=>r.split==='train')];
 const evaluation=math.filter(r=>r.split==='eval');
 const trainPrompts=new Set(training.map(x=>x.messages[0].content));
 assert.equal(trainPrompts.size,training.length,'duplicate training prompts');
 for(const x of evaluation)assert.ok(!trainPrompts.has(x.messages[0].content),'train/eval prompt leakage');
 assert.equal(new Set(math.map(x=>JSON.stringify(x.variables))).size,math.length,'duplicate numeric scenarios');
 jsonl(path.join(out,'native-facts.jsonl'),facts);
 jsonl(path.join(out,'conversations.train.jsonl'),training);
 jsonl(path.join(out,'arithmetic.eval.jsonl'),evaluation);
 save(path.join(out,'sources.json'),sources);
 const manifest={version,concepts:rows.length,native_facts_available:facts.length,canonical_conversation_examples:canonical.length,
  templated_style_examples:styled.length,handwritten_dialogues:dialogues.length,synthetic_arithmetic_training:4096,
  corpus_training_examples:training.length,arithmetic_evaluation_examples:evaluation.length,
  advanced_corpus_consumed_by_native_model:false,contains_personal_financial_data:false,
  evaluation_scope:'The arithmetic split separates scenarios and exact prompts, not reasoning templates. It is an educational corpus, not a model score.',
  files:Object.fromEntries(['native-facts.jsonl','conversations.train.jsonl','arithmetic.eval.jsonl','sources.json'].map(f=>[f,{bytes:fs.statSync(path.join(out,f)).size,sha256:hash(fs.readFileSync(path.join(out,f)))}]))};
 save(path.join(out,'manifest.json'),manifest);return manifest;
}
function train(runtime,app,encoded,out){
 for(const f of [runtime,app,encoded])assert.ok(fs.existsSync(f),'missing '+f);
 const manifest=exportData(path.join(out,'corpus'));
 const expectedApp='a0edbe6122beb5ab57d0e2dbd60c26524bc946737806eb71f2ed133fde068a28';
 const expectedBase='876d3f2a82698e9582f17043028d9a75b454e4b5ebaf7cc5949b65a5bac58a10';
 const encodedHash=hash(fs.readFileSync(encoded));
 const base=gunzipSync(Buffer.from(fs.readFileSync(encoded,'utf8').trim(),'base64'));
 assert.equal(hash(base),expectedBase,'different E034 checkpoint: migration required');
 assert.equal(hash(fs.readFileSync(app)),expectedApp,'different E034 capsule: migration required');
 const baseFile=path.join(out,'base-e034.rvp'),candidate=path.join(out,'finance-f001.rvp');
 fs.writeFileSync(baseFile,base);fs.writeFileSync(candidate,base);
 const transcripts=[];let checks=0;const eq=(a,b,label)=>{assert.equal(a,b,label);checks++;};
 function ask(text,state=candidate,language='es',phase='test'){
  assert.ok(Buffer.byteLength(text)<=255);
  const start=performance.now();
  const answer=execFileSync(runtime,['app-turn',app,state,state,language,text],{encoding:'utf8',timeout:30000,maxBuffer:1024*1024}).trimEnd();
  const event={phase,input:text,language,output:answer,milliseconds:Math.round((performance.now()-start)*100)/100};
  transcripts.push(event);fs.appendFileSync(path.join(out,'transcripts.jsonl'),JSON.stringify(event)+'\n');return answer;
 }
 const cite=i=>'[#'+String(i).padStart(3,'0')+']';
 const atom=(r,i,rel)=>`${r.term} ${rel==='definition'?'es':'requiere'} ${r[rel].toLowerCase()} ${cite(2*i+(rel==='definition'?0:1))}.`;
 const baselineState=path.join(out,'baseline-eval.rvp');fs.copyFileSync(baseFile,baselineState);
 const status=ask('@ctx status',baselineState,'es','baseline');
 assert.match(status,/CTX n=0(?:\D|$)/,'do not overwrite a populated private archive');
 let baseline=0;
 for(const [i,r] of rows.entries())baseline+=Number(ask('que es '+r.term,baselineState,'es','baseline')===atom(r,i,'definition'));
 const teachingStart=performance.now();
 for(const [i,f] of facts.entries())eq(ask('@ctx add '+f.text,candidate,'es','ingestion'),'CTX guardado #'+String(i).padStart(3,'0'),'fact '+i);
 const ingestionMilliseconds=performance.now()-teachingStart;
 const trainedHash=hash(fs.readFileSync(candidate));
 const evalState=path.join(out,'evaluation-only.rvp');fs.copyFileSync(candidate,evalState);
 let definitions=0,requirements=0,compositions=0,followups=0;
 for(const [i,r] of rows.entries()){
  eq(ask('que es '+r.term,evalState),atom(r,i,'definition'),'definition '+r.term);definitions++;
  eq(ask('que requiere '+r.term,evalState),atom(r,i,'requirement'),'requirement '+r.term);requirements++;
  eq(ask('que es '+r.term+' y que requiere',evalState),atom(r,i,'definition')+' '+atom(r,i,'requirement'),'composition '+r.term);compositions++;
  eq(ask('y que requiere',evalState),atom(r,i,'requirement'),'followup '+r.term);followups++;
 }
 eq(ask('hola',evalState),'Hola. Soy BBY Q.','Spanish greeting retained');
 assert.ok(ask('hello',evalState,'en').includes('BBY Q'));checks++;
 assert.ok(ask('que es calculadora',evalState).toLowerCase().includes('herramienta'));checks++;
 eq(ask('que es sinregistro y que requiere',evalState),'Falta evidencia para combinar ambas propiedades.','unknown term');
 const diagnostic=[];
 for(const q of ['oye que es ingreso','pz que es beneficio','mira que es farmear dinero','explicame farmear dinero','esk quiero farmear dinero','como monetizo reverse','quiero poner mi dinero a trabajar','vendi mil cuanto gane','eso significa que ya puedes invertir solo','cuanto esta bitcoin ahorita']){
  diagnostic.push({input:q,output:ask(q,evalState,'es','open-language-diagnostic'),scored_as_general_competence:false});
 }
 save(path.join(out,'open-language-diagnostic.json'),diagnostic);
 eq(hash(fs.readFileSync(candidate)),trainedHash,'evaluation never changes published candidate');
 eq(hash(fs.readFileSync(encoded)),encodedHash,'repository checkpoint unchanged');
 eq(hash(fs.readFileSync(app)),expectedApp,'no replacement inference engine');
 const restarted=path.join(out,'reopened.rvp');fs.copyFileSync(candidate,restarted);
 eq(ask('que es farmear dinero',restarted),atom(rows[0],0,'definition'),'checkpoint reopened without re-teaching');
 const compressed=gzipSync(fs.readFileSync(candidate),{level:9});
 fs.writeFileSync(path.join(out,'finance-f001.rvp.gz'),compressed);
 fs.copyFileSync(app,path.join(out,'BBY-Q-E034-F001.rxe'));
 const report={version,checks,base_checkpoint_sha256:expectedBase,app_sha256:expectedApp,checkpoint_sha256:trainedHash,
  native_facts_ingested:facts.length,concepts:rows.length,baseline_definitions_exact:baseline,
  exact_native_results:{definitions,requirements,compositions,followups,total:definitions+requirements+compositions+followups},
  native_scope:'Persistent contextual knowledge acquisition and constrained factual dialogue in existing XI/Ether. NOT generative fine-tuning or general economic reasoning.',
  corpus_training_examples:manifest.corpus_training_examples,advanced_corpus_consumed:false,
  raw_checkpoint_bytes:fs.statSync(candidate).size,gzip_checkpoint_bytes:compressed.length,
  ingestion_milliseconds:Math.round(ingestionMilliseconds),production_deployed:false,android_tested:false,can_execute_financial_transactions:false};
 save(path.join(out,'results.json'),report);console.log(JSON.stringify(report,null,2));
}
const args=process.argv.slice(2);
if(args[0]==='export'&&args.length===2)console.log(JSON.stringify(exportData(path.resolve(args[1])),null,2));
else if(args[0]==='train'&&args.length===5)train(...args.slice(1).map(x=>path.resolve(x)));
else throw Error('Usage: node f001.mjs export OUTPUT | train RUNTIME E034_RXE BASE64_CHECKPOINT OUTPUT');
