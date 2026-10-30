// F004: dos etapas secuenciales, memoria XI y examenes separados de la semilla.
import fs from 'node:fs';
import path from 'node:path';
import assert from 'node:assert/strict';
import {execFileSync} from 'node:child_process';
import {fileURLToPath} from 'node:url';
import {gzipSync,gunzipSync} from 'node:zlib';
import {expandArchive,sha,CAPACITY,DATA_BYTES} from './archive.mjs';
import {nativeBatch} from './batch.mjs';
import {withPageReader} from './pages.mjs';
import {bookSource,PDF_SHA} from './source.mjs';
import {lessons} from './lessons.mjs';
const root=path.resolve(process.argv[2]||path.join(path.dirname(fileURLToPath(import.meta.url)),'..'));
const out=path.resolve(process.argv[3]||path.join(root,'evidencia/campana'));
assert.ok(!fs.existsSync(out),'Use un directorio nuevo para no sobrescribir evidencia');
fs.mkdirSync(out,{recursive:true});
const runtime=path.join(root,'runtime-linux/reverse_pc'),oldApp=path.join(root,'base-f003/BBY-Q-F003-Babilonia.rxe');
const base=fs.readFileSync(path.join(root,'base-f003/f003-reader.xi'),'utf8');
const seed=gunzipSync(fs.readFileSync(path.join(root,'base-f003/finance-f003.rvp.gz')));
assert.equal(sha(seed),'dfdf19b32905a11b4ff43f0106bc298434941796001c6b1e05d25d6dc8ed7883');
assert.equal(sha(fs.readFileSync(runtime)),'ef0c3a709121b8fd3cf4c996808ecfef8b60a7065d3f9c802280c58dc9370d84');
assert.equal(sha(fs.readFileSync(oldApp)),'2458e999acbb72dcaf81219b44b7187244df7abaa22a465f59fc8ffcefc6300b');
const expanded=expandArchive(base),source=withPageReader(expanded.text);
const src=path.join(out,'bbyq-f004.xi');fs.writeFileSync(src,source);
const code=path.join(out,'bbyq-f004-code.rxe');
const ex=(args)=>execFileSync(runtime,args,{encoding:'utf8',timeout:120000,maxBuffer:32*1024*1024});
ex(['compile',src,code,'BBY Q F004 dos mitades']);
const originalSeed=path.join(out,'initial.rvp');fs.writeFileSync(originalSeed,seed);
const data=bookSource(fs.readFileSync(path.join(root,'libro/texto-extraido.txt'),'utf8'),fs.readFileSync(path.join(root,'libro/El-hombre-mas-rico-de-Babilonia-original-ingles.pdf')));
const json=(f,v)=>fs.writeFileSync(path.join(out,f),JSON.stringify(v,null,2)+'\n');
const jsonl=(f,rows)=>fs.writeFileSync(path.join(out,f),rows.map(x=>JSON.stringify(x)).join('\n')+'\n');
const oldLines=fs.readFileSync(path.join(root,'base-f003/hechos-previos.jsonl'),'utf8').trim().split('\n').map(s=>JSON.parse(s));
const oldFacts=oldLines.map((x,index)=>{const text=x.text||x.fact;assert.equal(typeof text,'string');const m=/^(.+?) (es|requiere) (.+)$/.exec(text);assert.ok(m,text);return{...x,index,text,term:m[1],relation:m[2],value:m[3]};});
assert.equal(oldFacts.length,448);assert.equal(lessons.length,64);
const oldTerms=new Set(oldFacts.map(f=>f.term));assert.equal(new Set(lessons.map(l=>l.term)).size,64);assert.ok(lessons.every(l=>!oldTerms.has(l.term)));
const training=[];let next=448;
for(const half of ['A','B']){
 for(const l of lessons.filter(x=>x.half===half))for(const [relation,value] of [['es',l.definition],['requiere',l.requirement]])training.push({...l,id:l.id+'-'+relation,index:next++,relation,value,text:`${l.term} ${relation} ${value}`,kind:'lesson_es'});
 for(const r of data.records.filter(x=>x.half===half))training.push({...r,index:next++});
}
assert.ok(next<=CAPACITY);for(const r of training)assert.ok(Buffer.byteLength(r.text)<=224);
jsonl('native-training-records.jsonl',training);jsonl('pages.jsonl',data.pages);json('coverage.json',data.coverage);json('archive-patch.json',expanded.report);
let checks=0,batchId=0;
function ck(condition,label,details={}){if(!condition){json('failure.json',{checks,label,...details});throw new Error(label+' '+JSON.stringify(details));}checks++;}
function asks(queries,state,phase,size=4){const outputs=[];for(let i=0;i<queries.length;i+=size){const qs=queries.slice(i,i+size),id=++batchId;const result=nativeBatch({runtime,source,inputState:state,outputState:state,queries:qs,work:path.join(out,'tmp'),tag:'batch-'+id});qs.forEach((q,j)=>fs.appendFileSync(path.join(out,'turns.jsonl'),JSON.stringify({phase,batch:id,input:q,output:result.outputs[j]})+'\n'));fs.appendFileSync(path.join(out,'batches.jsonl'),JSON.stringify({phase,batch:id,turns:qs.length,ms:result.ms,budget_splits:result.budget_splits||0})+'\n');outputs.push(...result.outputs);if(id%15===0)console.log(JSON.stringify({event:'progress',phase,batches:id,checks,turns:i+qs.length,total:queries.length}));}return outputs;}
function count(state,expected,phase){const o=asks(['@ctx status'],state,phase)[0];const m=/^CTX n=(\d+) bytes=(\d+) limite=(\d+)$/.exec(o);ck(!!m,'status syntax',{o});ck(Number(m[1])===expected,'record count',{expected,o});ck(Number(m[3])===DATA_BYTES,'archive byte limit',{o});return Number(m[2]);}
const expected=f=>`${f.text} [#${String(f.index).padStart(3,'0')}].`;
const query=f=>`que ${f.relation} ${f.term}`;
const copy=(from,name)=>{const p=path.join(out,name);fs.copyFileSync(from,p);return p;};
const stageReports=[];let current=originalSeed;let nativeFacts=[...oldFacts],knownRecords=[];
count(current,448,'baseline-count');
const started=performance.now();
for(const half of ['A','B']){
 const stageStart=performance.now(),incoming=training.filter(r=>r.half===half),newFacts=incoming.filter(r=>r.kind==='lesson_es');
 const baseline=copy(current,'baseline-'+half+'.rvp');
 const before=asks(newFacts.map(query),baseline,half+'-before-knowledge');
 const beforeExact=before.filter((o,i)=>o===expected(newFacts[i])).length;ck(beforeExact===0,'new lesson baseline',{half,beforeExact});
 count(baseline,448+knownRecords.length,half+'-baseline-unchanged');
 if(half==='A')ck(asks(['@libro pagina 62'],baseline,'A-before-page')[0]==='No se ha incorporado esa pagina.','second half not previously ingested');
 current=copy(current,'training-'+half+'.rvp');
 const t=performance.now(),acks=asks(incoming.map(r=>'@ctx add '+r.text),current,half+'-ingest',32),ingestionMs=performance.now()-t;
 acks.forEach((o,i)=>ck(o===`CTX guardado #${String(incoming[i].index).padStart(3,'0')}`,'native ingestion',{half,index:incoming[i].index,output:o}));
 knownRecords.push(...incoming);nativeFacts.push(...newFacts);
 const archiveCount=448+knownRecords.length,bytes=count(current,archiveCount,half+'-count-after');
 const candidateHash=sha(fs.readFileSync(current)),evalState=copy(current,'evaluation-'+half+'.rvp');
 const outputs=asks(nativeFacts.map(query),evalState,half+'-semantic-retention');
 outputs.forEach((o,i)=>ck(o===expected(nativeFacts[i]),'semantic fact retention',{half,index:nativeFacts[i].index,expected:expected(nativeFacts[i]),output:o}));
 const raw=asks(knownRecords.map(r=>'@ctx get '+r.index),evalState,half+'-raw-retention',32);
 raw.forEach((o,i)=>ck(o===`#${String(knownRecords[i].index).padStart(3,'0')} ${knownRecords[i].text}`,'raw record retention',{half,index:knownRecords[i].index,output:o}));
 const pages=data.pages.filter(p=>half==='B'||p.half==='A');
 const pageOutputs=asks(pages.map(p=>'@libro pagina '+p.page),evalState,half+'-pages',4);
 pageOutputs.forEach((o,i)=>ck(o===pages[i].text,'full page reconstruction',{half,page:pages[i].page,expected_sha256:pages[i].sha256,actual_sha256:sha(Buffer.from(o)),output:o.slice(0,100)}));
 const learnedLessons=lessons.filter(l=>half==='B'||l.half==='A'),prefixes=['oye explicame ','pz que es ','mira necesito entender ','esk no entiendo '];
 const styleQueries=learnedLessons.map((l,i)=>prefixes[i%4]+l.term);
 const styleOutputs=asks(styleQueries,evalState,half+'-operator-style');
 styleOutputs.forEach((o,i)=>{const fact=nativeFacts.find(f=>f.term===learnedLessons[i].term&&f.relation==='es');ck(o===expected(fact),'operator variant',{half,query:styleQueries[i],output:o,expected:expected(fact)});});
 count(evalState,archiveCount,half+'-evaluation-not-ingestion');
 if(half==='A')ck(asks(['@libro pagina 62'],evalState,'A-second-half-absent')[0]==='No se ha incorporado esa pagina.','half B absent after half A');
 ck(sha(fs.readFileSync(current))===candidateHash,'tests isolated from seed',{half});
 const checkpoint=copy(current,'checkpoint-'+half+'.rvp'),app=path.join(out,'BBY-Q-F004-'+half+'.rxe');
 ex(['pack-app',code,checkpoint,app,'org.reverse.bbyq','BBY Q','F004-'+half,sha(Buffer.from(source)).slice(0,40)]);
 const reopened=path.join(out,'reopened-'+half+'.rvp');ex(['app-init',app,reopened]);count(reopened,archiveCount,half+'-fresh-count');
 const reopenedPages=asks(pages.map(p=>'@libro pagina '+p.page),reopened,half+'-fresh-pages',4);
 reopenedPages.forEach((o,i)=>ck(o===pages[i].text,'page persistence from app seed',{half,page:pages[i].page}));
 const zipped=gzipSync(fs.readFileSync(checkpoint),{level:9});fs.writeFileSync(checkpoint+'.gz',zipped);
 const report={half,pages:half==='A'?[1,61]:[62,122],added_source_fragments:incoming.filter(r=>r.kind==='source_text_en').length,added_spanish_concepts:newFacts.length/2,added_spanish_facts:newFacts.length,archive_records:archiveCount,structured_facts:nativeFacts.length,source_records:knownRecords.filter(r=>r.kind==='source_text_en').length,old_and_new_fact_queries_correct:outputs.length,raw_record_queries_correct:raw.length,complete_pages_reconstructed:pages.length,pages_reconstructed_from_fresh_seed:reopenedPages.length,operator_style_queries_correct:styleOutputs.length,new_exact_before:beforeExact,ingestion_ms:ingestionMs,stage_ms:performance.now()-stageStart,archive_text_bytes:bytes,checkpoint_bytes:fs.statSync(checkpoint).size,checkpoint_gzip_bytes:zipped.length,app_bytes:fs.statSync(app).size,checkpoint_sha256:candidateHash,app_sha256:sha(fs.readFileSync(app)),checks_cumulative:checks};
 stageReports.push(report);json('stage-'+half+'.json',report);console.log(JSON.stringify({event:'STAGE_'+half+'_COMPLETE',...report}));
}
const finalHash=sha(fs.readFileSync(current));
const openQuestions=['Si gano 1000 cuanto ahorro con la regla del diez por ciento','Tengo 1000 aplica el plan de Dabasir','Un amigo sabe de ladrillos pero quiere comprar joyas con mi ahorro que opinas','Gano poco y me falta comida debo ahorrar diez por ciento de todos modos','Entonces comprar casa siempre es mejor que alquilar','Me prometen duplicar mi dinero sin riesgo que diria el libro','Como aplico este libro para ganar con Reverse sin gastar todo','Ya leiste el libro invierte mi dinero ahora'];
const probes=[];
for(let i=0;i<openQuestions.length;i++){
 const state=copy(current,'probe-'+i+'.rvp');
 const answer=asks([openQuestions[i]],state,'open-probe-'+i)[0],status=asks(['@ctx status'],state,'open-probe-status-'+i)[0];
 const countMatch=/CTX n=(\d+)/.exec(status);probes.push({question:openQuestions[i],answer,records_after:Number(countMatch?.[1]),records_before:448+knownRecords.length,scored_as_pass:false});fs.unlinkSync(state);
}
ck(sha(fs.readFileSync(current))===finalHash,'open probes never change delivered seed');
ck(sha(gunzipSync(fs.readFileSync(path.join(root,'base-f003/finance-f003.rvp.gz'))))===sha(seed),'original seed preserved');
json('open-probes.json',probes);
const result={version:'F004-dos-mitades',completed:true,checks,stage_reports:stageReports,elapsed_ms:performance.now()-started,archive_records:448+knownRecords.length,structured_facts:nativeFacts.length,new_spanish_concepts:64,new_spanish_facts:128,source_fragments:1171,source_pages:122,remaining_slots:CAPACITY-(448+knownRecords.length),capacity:CAPACITY,source_pdf_sha256:PDF_SHA,source_xi_sha256:sha(Buffer.from(source)),runtime_sha256:sha(fs.readFileSync(runtime)),full_text_reconstruction_verified:true,neural_weight_training:false,open_probe_count:probes.length,open_probes:probes,production_deployed:false,android_tested:false,financial_execution_enabled:false,limitations:['Native contextual acquisition, not neural weight tuning or autonomous PDF reading','Complete normalized extracted text stored in English; not a complete Spanish translation','64 additional Spanish lessons are an authored educational synthesis, not all possible conclusions','Retrieval and page reconstruction do not establish open reasoning or numerical generalization','4096 records, 224 bytes per record, 255-byte input ABI: finite implementation limits','No APK replacement, no access to personal financial accounts']};
json('results.json',result);console.log(JSON.stringify({event:'F004_COMPLETE',checks,archive_records:result.archive_records,elapsed_ms:result.elapsed_ms}));
