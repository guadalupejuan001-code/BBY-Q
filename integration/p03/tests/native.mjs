// Fixed and withheld-case native XI inference exam. The examiner does not
// choose answers: it calls the real original reverse_pc runtime.
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import {performance} from 'node:perf_hooks';
import {NativePages,cells,run} from '../../../ai/personal/x10/pages.mjs';
import {reasonSource,REASON_BASE,REASON_MAX_BYTES,REASON_MODE,REASON_SHA256} from '../../../ai/personal/p03/reason.mjs';
const [runtimeArg,outArg]=process.argv.slice(2);
if(!outArg)throw Error('Usage: node integration/p03/tests/native.mjs REVERSE_PC NEW_OUTPUT_DIR');
const runtime=path.resolve(runtimeArg),out=path.resolve(outArg);
if(fs.existsSync(out))throw Error('P03 exam requires an empty output destination.');
fs.mkdirSync(out,{recursive:true});
const file=path.join(out,'reason.xi'),compiled=path.join(out,'reason.rxe'),source=reasonSource();
fs.writeFileSync(file,source);
const sha=x=>crypto.createHash('sha256').update(x).digest('hex');
assert.equal(sha(Buffer.from(source)),REASON_SHA256);
run(runtime,['compile',file,compiled,'BBY Q P03 grounded native deduction']);
const examples=[
 ['Todos los gatos son mamíferos. Luna es un gato. ¿Luna es mamífero?',1,/luna -> gato -> mamiferos/],
 ['Todos los gatos son mamíferos. Todos los mamíferos son animales. Luna es un gato. ¿Luna es animal?',1,/luna -> gato -> mamiferos -> animales/],
 ['Luna no es gato. ¿Luna es gato?',4,/niega expresamente/],
 ['Luna es un gato. Luna no es gato. ¿Luna es gato?',3,/incompatibles/],
 ['Todos los gatos son mamíferos. Luna es gato. ¿Luna es reptil?',2,/No se puede deducir ni refutar/],
 ['A es mayor que B. B es mayor que C. ¿A es mayor que C?',1,/a -> b -> c/],
 ['A es mayor que B. B es mayor que C. ¿C es mayor que A?',4,/orden inverso: a -> b -> c/],
 ['A es mayor que B. B es mayor que A. ¿A es mayor que B?',3,/incompatibles/],
 ['Si A es mayor que B y B es mayor que C, ¿A es mayor que C?',1,/a -> b -> c/],
 ['A es mayor que B y B es mayor que C, ¿A es mayor que C?',1,/a -> b -> c/],
 ['Todas las aves son animales. Nina es una ave. ¿Nina es animal?',1,/nina -> ave -> animales/],
 ['Todos los motores son máquinas. Alpha es un motor. ¿Alpha es máquina?',1,/alpha -> motor -> maquinas/],
 ['Los gatos son mamíferos. Luna es un gato. ¿Luna es mamífero?',1,/luna -> gato -> mamiferos/],
 ['Gato es mamífero. ¿Mamífero es gato?',2,/No se puede deducir ni refutar/],
 ['Todos los gatos son mamíferos. Luna no es mamífero. Luna es un gato. ¿Luna es mamífero?',3,/incompatibles/],
 ['Razona: Lara es robot. ¿Lara es robot?',1,/lara -> robot/],
 ['Luna es gato. ¿Luna es mamífero?',2,/No se puede deducir ni refutar/],
 ['Hola',0,/P03 requiere premisas/],
 ['Luna es gato. Pero Luna no es gato. ¿Luna es gato?',5,/fuera de la gramática/],
 ['Todos los gatos son mamíferos. Luna es un gato. ¿Qué canción canta Luna?',0,/P03 requiere premisas/],
 ['Todos los gatos son mamíferos. Luna es un gato. ¿Luna es un reptil?',2,/No se puede deducir ni refutar/],
 ['Una premisa que no reconozco. Luna es gato. ¿Luna es gato?',5,/no inferí una conclusión parcial/],
 ['Luna es un gato. ¿Luna es gato? ¿Luna es reptil?',5,/no inferí una conclusión parcial/]
];
for(let i=0;i<80;i++){
 const stem='r'+String(i).padStart(3,'0');
 const a=stem+'fla',b=stem+'ver',c=stem+'sol',subject=stem+'uni';
 const msg='Todos los '+a+' son '+b+'. Todos los '+b+' son '+c+'. '+subject+' es un '+a+'. ¿'+subject+' es '+c+'?';
 examples.push([msg,1,new RegExp(subject+' -> '+a+' -> '+b+' -> '+c)]);
 if(i%8===0)examples.push(['Todos los '+a+' son '+b+'. '+subject+' es '+a+'. ¿'+subject+' es '+c+'?',2,/No se puede deducir ni refutar/]);
}
const records=[];
for(let i=0;i<examples.length;i++){
 const [msg,mode,pattern]=examples[i],raw=Buffer.from(msg,'utf8');
 assert.ok(raw.length<=REASON_MAX_BYTES,'Fixture beyond P03 limit');
 const root=path.join(out,'case-'+String(i).padStart(3,'0'));
 fs.mkdirSync(root);
 const p=new NativePages(runtime,{'reason.rxe':compiled},root);
 p.stage({data:raw,total:raw.length});
 const before=cells(p.state),started=performance.now(),result=p.reason(raw),ms=performance.now()-started,after=cells(p.state);
 assert.equal(result.mode,mode,msg+': '+result.response);
 assert.match(result.response,pattern,msg);
 if([1,2,3,4].includes(mode))assert.equal(result.unparsed,0,msg);
 assert.equal(result.eligible,![REASON_MODE.partial,REASON_MODE.unsupported].includes(mode),msg);
 assert.equal(result.readOnly,true);
 const foreign=[...new Set([...before.keys(),...after.keys()])].filter(addr=>addr<REASON_BASE||addr>=REASON_BASE+18000n)
  .filter(addr=>(before.get(addr)||0)!==(after.get(addr)||0));
 assert.deepEqual(foreign,[],'P03 wrote outside its scratch: '+msg);
 records.push({test:i,input:msg,expected:mode,actual:result.mode,output:result.response,premises:result.premises,proof_nodes:result.proof_nodes,ms,ok:true});
 fs.rmSync(root,{recursive:true,force:true});
}
const long='Luna es gato. ¿Luna es gato? '+'x'.repeat(REASON_MAX_BYTES);
const root=path.join(out,'overflow'),p=new NativePages(runtime,{'reason.rxe':compiled},root);
assert.throws(()=>p.reason(Buffer.from(long)),/640 bytes/);
fs.rmSync(root,{recursive:true,force:true});
const times=records.map(t=>t.ms).sort((a,b)=>a-b),pct=p=>times[Math.max(0,Math.ceil(p*times.length)-1)];
const results={ok:true,language_scope:'bounded ES universal/is/strict-greater premises',
 open_dialogue_achieved:false,new_training_weights:false,native_xi:true,
 cases:records.length,correct:records.length,heldout_generated:90,extra_overflow_check:1,
 median_ms:pct(.5),p95_ms:pct(.95),sha256:REASON_SHA256,compiled_sha256:sha(fs.readFileSync(compiled)),records};
fs.writeFileSync(path.join(out,'results.json'),JSON.stringify(results,null,2)+'\n');
console.log(JSON.stringify({ok:true,cases:results.cases,correct:results.correct,overflow_rejected:true,median_ms:results.median_ms,p95_ms:results.p95_ms}));
