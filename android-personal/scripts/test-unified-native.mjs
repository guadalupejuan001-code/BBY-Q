// Independent native contracts before the Android/JNI transport is exercised.
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import assert from 'node:assert/strict';
import {NativePages,readNumber,readBytes} from '../../ai/personal/x10/pages.mjs';
const root=path.resolve(import.meta.dirname,'../..');
const assets=path.join(root,'android-personal/app/src/main/assets/engine'),runtime=path.join(root,'deps/reverse-pc/build/reverse_pc');
const dir=fs.mkdtempSync(path.join(root,'build/mobile-native-'));
const roles=Object.fromEntries(fs.readdirSync(assets).filter(n=>n.endsWith('.rxe')).map(n=>[n,path.join(assets,n)]));
const pages=new NativePages(runtime,roles,dir),B=9190000000000000000n,checks=[];
function check(name,fn){fn();checks.push(name);}
check('strict UTF-8 across native pages',()=>pages.validate(Buffer.from('á🎸'.repeat(2000))));
check('paginated text is returned without truncation',()=>{const text=Buffer.from('repite exactamente:\n'+'á🎸'.repeat(2000));assert.equal(pages.route(text).mode,2);assert.equal(pages.stream(text,2),'á🎸'.repeat(2000));});
const teaching=Buffer.from('aprende: faro\ndefinición: una luz\nrequiere: energía\nfuente: X\npáginas: 1');let record;
check('intent staging preserves pending X10 teaching record',()=>{
 assert.equal(pages.route(teaching).operation,1);assert.equal(pages.intent(teaching).name,'teaching');
 const result=pages.record(null,{count:480,revision:482});assert.equal(result.status,0);assert.equal(result.count,481);record=result.record;
});
check('native learned lesson is queried from its opaque page',()=>{
 assert.equal(pages.route(Buffer.from('que es faro')).operation,4);const result=pages.record(record,{count:481,revision:483});assert.equal(result.status,0);assert.match(result.response,/una luz/);
});
check('correction requires the exact prior revision and preserves the record on mismatch',()=>{
 assert.throws(()=>pages.route(Buffer.from('corrige lección: faro\ndefinición: otra luz\nrequiere: energía\nfuente: X\npáginas: 1')));
 pages.route(Buffer.from('corrige lección: faro\nrevisión: 483\ndefinición: otra luz\nrequiere: energía\nfuente: X\npáginas: 1'));
 const corrected=pages.record(record,{count:481,revision:483});assert.equal(corrected.status,0);assert.equal(corrected.revision,484);
 pages.route(Buffer.from('corrige lección: faro\nrevisión: 483\ndefinición: sobrescribir\nrequiere: energía\nfuente: X\npáginas: 1'));
 const stale=pages.record(corrected.record,{count:481,revision:484});assert.equal(stale.status,5);assert.deepEqual(stale.record,corrected.record);
});
check('native named context resolves a prior user turn',()=>{
 const result=pages.context(Buffer.from('¿qué dije sobre Neral?'),[Buffer.from('Mi proyecto se llama Neral.')]);assert.equal(result.mode,1);assert.equal(result.slot,1);
});
check('grounded native syllogism',()=>{const result=pages.reason(Buffer.from('Todos los motores son máquinas. Alpha es un motor. ¿Alpha es máquina?'));assert.equal(result.mode,1);assert.match(result.response,/alpha -> motor -> maquinas/);});
check('native creative composition',()=>{const result=pages.compose(Buffer.from('Escribe un poema de cuatro versos sobre una guitarra.'));assert.equal(result.mode,1);assert.equal(result.response.split('\n').length,4);});
check('productive paraphrase preserves the topic',()=>{const result=pages.paraphrase(Buffer.from('hazme un poema sobre una guitarra'));assert.equal(result.handled,true);assert.equal(result.canonical,'escribe un poema sobre una guitarra');});
for(const [text,operation,key,bit]of [['memoria guarda faro 1',1,'faro',1],['memoria consulta faro',3,'faro',null],['memoria corrige faro 0',2,'faro',0],['memoria estado',4,null,null],['qchat hola',5,null,null],['memoria guarda faro 3',254,null,null],['mision {"memoria":"faro","posicion":3}',6,null,null],['evaluar {"tarea":"ejemplo","resultado":1}',7,null,null]]){
 check('mobile XI grammar: '+text,()=>{
  const raw=Buffer.from(text);pages.stage({data:raw,total:raw.length});pages.role('mobile-route.rxe');const m=pages.map();assert.equal(readNumber(m,B+512n,1),operation);
  if(key!==null)assert.equal(readBytes(m,B+544n,readNumber(m,B+514n,1)).toString(),key);
  if(bit!==null)assert.equal(readNumber(m,B+515n,1),bit);
 });
}
check('V3 completed-goal command grammar',()=>{const d=pages.quantum3Route(Buffer.from('quantum v3 planea 6 6'));assert.equal(d.action,4);assert.equal(d.first,6);assert.equal(d.second,6);});
check('native generator context is restricted to follow-up requests',()=>{
 for(const[text,expected]of [['dime mas',1],['repitelo !',1],['explicalo otra vez',1],['cuentalo otra vez',1],['hola',0],['que es memoria',0],['dime mas sobre circuito',0],['',0]]){
  const raw=Buffer.from(text);pages.stage({data:raw,total:raw.length});pages.role('qchat-context.rxe');assert.equal(readNumber(pages.map(),B+516n,1),expected,text);
 }
});
const result={ok:true,native_checks:checks.length,checks};fs.writeFileSync(path.join(root,'build/unified-native-checks.json'),JSON.stringify(result,null,2)+'\n');console.log(JSON.stringify(result));
