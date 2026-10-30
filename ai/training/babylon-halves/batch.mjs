// Ejecuta turnos consecutivos dentro del mismo programa XI. El driver no responde:
// escribe entradas ABI, salta al agente y recoge su salida. Sin otro modelo.
import fs from 'node:fs';
import path from 'node:path';
import assert from 'node:assert/strict';
import {execFileSync} from 'node:child_process';
const SCRATCH='9300000000000000000';
export function nativeBatch({runtime,source,inputState,outputState,queries,work,tag='batch'}) {
  assert.ok(queries.length>0&&queries.length<=64);
  assert.ok(!source.includes(SCRATCH),'batch scratch namespace already in use');
  const lines=['#!reverse-pc-machine-v1',`store8 ${SCRATCH} 0`,'jmp f004_batch_dispatch'];
  // Todos los halts originales vuelven al driver; cada turno ejecuta el agente completo.
  lines.push('label f004_batch_agent',source.replace(/^#![^\n]*\n/,'').replace(/^halt\s*$/gm,'jmp f004_batch_return'));
  lines.push('label f004_batch_return',...Array.from(Buffer.from('~F004-END~')).flatMap(b=>['set r14 '+b,'print r14']),`load8 r0 ${SCRATCH}`,'add r0 1',`store8 ${SCRATCH} r0`,'jmp f004_batch_dispatch','label f004_batch_dispatch',`load8 r0 ${SCRATCH}`);
  for(let i=0;i<queries.length;i++)lines.push(`cmp r0 ${i}`,`je f004_batch_turn_${i}`);
  lines.push(`store8 ${SCRATCH} 0`,'halt');
  queries.forEach((q,i)=>{
    const b=Buffer.from(q);assert.ok(b.length>0&&b.length<=255,'ABI input bytes');
    lines.push(`label f004_batch_turn_${i}`,'store8 7400000000000000016 1',`store8 7400000000000000017 ${b.length}`);
    for(let j=0;j<b.length;j++)lines.push(`store8 ${7400000000000000128n+BigInt(j)} ${b[j]}`);
    for(let r=0;r<16;r++)lines.push(`set r${r} 0`);
    lines.push('jmp f004_batch_agent');
  });
  fs.mkdirSync(work,{recursive:true});const src=path.join(work,tag+'.xi');fs.writeFileSync(src,lines.join('\n')+'\n');
  const t=performance.now();
  const code=path.join(work,tag+'-code.rxe'),app=path.join(work,tag+'-app.rxe');
  const ex=(args)=>execFileSync(runtime,args,{encoding:'utf8',maxBuffer:32*1024*1024,timeout:120000});
  ex(['compile',src,code,'F004 driver']);
  ex(['pack-app',code,inputState,app,'org.reverse.bbyq','BBY Q','F004-batch','0000000000000000000000000000000000000000']);
  const temporary=path.join(work,tag+'-output.rvp');
  let raw;
  try {raw=ex(['app-turn',app,inputState,temporary,'es','@batch']);}
  catch(error){
    for(const f of [src,code,app,temporary])if(fs.existsSync(f))fs.unlinkSync(f);
    if(queries.length>1&&/instruction-step budget exceeded|respuesta supera 4096 bytes/.test(String(error.stderr))){
      const mid=Math.floor(queries.length/2);
      const left=nativeBatch({runtime,source,inputState,outputState,queries:queries.slice(0,mid),work,tag:tag+'a'});
      const right=nativeBatch({runtime,source,inputState:outputState,outputState,queries:queries.slice(mid),work,tag:tag+'b'});
      return {outputs:[...left.outputs,...right.outputs],ms:performance.now()-t,budget_splits:1+(left.budget_splits||0)+(right.budget_splits||0)};
    }
    throw error;
  }
  fs.renameSync(temporary,outputState);
  const outputs=raw.split('~F004-END~');const tail=outputs.pop();
  assert.equal(outputs.length,queries.length,'native batch output cardinality');
  assert.ok(!tail.trim(),'unexpected stdout after last turn '+tail);
  for(const f of [src,code,app])fs.unlinkSync(f);
  return {outputs,ms:performance.now()-t};
}
