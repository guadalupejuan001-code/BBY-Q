// Pruebas destructivas SOLO sobre copias: capacidad, ids, busqueda y transporte.
import fs from 'node:fs';import path from 'node:path';import assert from 'node:assert/strict';
import {execFileSync} from 'node:child_process';import {nativeBatch} from './batch.mjs';import {sha} from './archive.mjs';
const root=path.resolve(process.argv[2]),campaign=path.resolve(process.argv[3]),out=path.resolve(process.argv[4]);
assert.ok(!fs.existsSync(out));fs.mkdirSync(out,{recursive:true});
const runtime=path.join(root,'runtime-linux/reverse_pc'),source=fs.readFileSync(path.join(campaign,'bbyq-f004.xi'),'utf8');
const seed=path.join(campaign,'checkpoint-B.rvp'),app=path.join(campaign,'BBY-Q-F004-B.rxe'),seedHash=sha(fs.readFileSync(seed));
const state=path.join(out,'boundary.rvp');fs.copyFileSync(seed,state);let id=0,checks=0;
const ck=(x,label)=>{assert.ok(x,label);checks++;};
function ask(qs,file=state){const all=[];for(let i=0;i<qs.length;i+=32){const q=qs.slice(i,i+32),r=nativeBatch({runtime,source,inputState:file,outputState:file,queries:q,work:path.join(out,'tmp'),tag:'test-'+(++id)});q.forEach((input,j)=>fs.appendFileSync(path.join(out,'turns.jsonl'),JSON.stringify({input,output:r.outputs[j]})+'\n'));all.push(...r.outputs);}return all;}
// La tabla de busqueda no debe alterar metadatos en 994..1057.
const ids=[0,447,448,511,512,767,768,993,994,999,1000,1057,1074,1137,1746];
const rawBefore=ask(ids.map(i=>'@ctx get '+i));
const searchProbes=[];
for(const query of ['@ctx find bbl p122 s','@ctx find babilonia trabajo y relaciones']){
 try{searchProbes.push({query,completed:true,output:ask([query])[0]});}
 catch(error){searchProbes.push({query,completed:false,error:String(error.stderr||error.message).trim(),counted_as_pass:false});}
}
fs.writeFileSync(path.join(out,'full-archive-search-probes.json'),JSON.stringify(searchProbes,null,2)+'\n');
const rawAfter=ask(ids.map(i=>'@ctx get '+i));rawAfter.forEach((x,i)=>ck(x===rawBefore[i],'metadata unchanged '+ids[i]));
const record224='limite de longitud es '+ 'a'.repeat(224-Buffer.byteLength('limite de longitud es '));
ck(ask(['@ctx add '+record224])[0]==='CTX guardado #1747','224-byte record accepted');
const rejected=ask(['@ctx add '+'b'.repeat(225)])[0];ck(!rejected.startsWith('CTX guardado #'),'225-byte record rejected');
ck(ask(['@ctx status'])[0].startsWith('CTX n=1748 '),'rejection does not increment count');
ck(ask(['@ctx get 1747'])[0]==='#1747 '+record224,'224-byte record recoverable');
const filler=[];for(let n=1748;n<4096;n++)filler.push(`@ctx add prueba${n} es valor${n}`);
const acks=ask(filler);acks.forEach((s,i)=>ck(s===`CTX guardado #${1748+i}`,'capacity ingestion '+(1748+i)));
ck(ask(['@ctx status'])[0].startsWith('CTX n=4096 '),'full capacity count');
ck(ask(['que es prueba4095'])[0]==='prueba4095 es valor4095 [#4095].','four-digit final semantic citation');
ck(ask(['@ctx get 4095'])[0]==='#4095 prueba4095 es valor4095','four-digit raw lookup');
const overflow=ask(['@ctx add fuera de capacidad es rechazo'])[0];ck(!overflow.startsWith('CTX guardado #'),'capacity overflow refused');
ck(ask(['@ctx status'])[0].startsWith('CTX n=4096 '),'overflow preserves count');
const afterFull=ask(ids.map(i=>'@ctx get '+i));afterFull.forEach((x,i)=>ck(x===rawBefore[i],'older records survive full capacity '+ids[i]));
// Id 512 no debe confundirse con el antiguo sentinel; fixture independiente.
const sentinel=path.join(out,'sentinel.rvp');fs.copyFileSync(seed,sentinel);
ask(['@ctx clear'],sentinel);ck(ask(['@ctx status'],sentinel)[0].startsWith('CTX n=000 '),'clear on disposable fixture');
const sentFacts=[];for(let n=0;n<1100;n++)sentFacts.push(`@ctx add indice${n} es dato${n}`);
ask(sentFacts,sentinel);
for(const n of [511,512,513,767,768])ck(ask(['que es indice'+n],sentinel)[0]===`indice${n} es dato${n} [#${n}].`,'sentinel/index boundary '+n);
const metaIds=[993,994,999,1000,1057,1099];
const metaBefore=ask(metaIds.map(n=>'@ctx get '+n),sentinel);
ck(ask(['@ctx find indice1099'],sentinel)[0]==='#1099 indice1099 es dato1099','search beyond old metadata overlap');
const metaAfter=ask(metaIds.map(n=>'@ctx get '+n),sentinel);metaAfter.forEach((x,i)=>ck(x===metaBefore[i],'search metadata preservation '+metaIds[i]));
// Las salidas por lote deben coincidir con app-turn consecutivos reales.
const batchState=path.join(out,'batch-parity.rvp'),directState=path.join(out,'direct-parity.rvp');fs.copyFileSync(seed,batchState);fs.copyFileSync(seed,directState);
const qs=['@ctx status','@ctx get 1000','@libro pagina 62','oye que es babilonia ahorro como semilla','@ctx add control de paridad es persistencia nativa','que es control de paridad','@ctx get 1747','@ctx status'];
const batch=ask(qs,batchState);const direct=qs.map(q=>execFileSync(runtime,['app-turn',app,directState,directState,'es',q],{encoding:'utf8',timeout:120000,maxBuffer:4*1024*1024}).trimEnd());
direct.forEach((x,i)=>ck(x===batch[i],'batch/direct output parity '+i));
ck(sha(fs.readFileSync(seed))===seedHash,'published seed remains unchanged');
const result={completed:true,checks,full_archive_search_probes:searchProbes,search_probes_are_not_passed_tests:true,search_preserved_records:metaIds.length,capacity_tested:4096,rejected_4097th:true,record_max_bytes:224,rejected_225_bytes:true,sentinel_indices:[511,512,513,767,768],direct_batch_parity:direct.length,seed_unchanged:true,seed_sha256:seedHash,tests_use_disposable_states:true};
fs.writeFileSync(path.join(out,'results.json'),JSON.stringify(result,null,2)+'\n');console.log(JSON.stringify(result));
for(const f of [state,sentinel,batchState,directState])fs.unlinkSync(f);
