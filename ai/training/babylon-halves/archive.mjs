// F004: expande el archivo XI conservando el formato de sus registros.
// Node solo emite/verifica codigo; no genera respuestas del agente.
import fs from 'node:fs';
import assert from 'node:assert/strict';
import {createHash} from 'node:crypto';
export const sha = b => createHash('sha256').update(b).digest('hex');
export const CAPACITY = 4096, DATA_BYTES = CAPACITY * 224;
export function expandArchive(base) {
  assert.equal(sha(Buffer.from(base)), '72b4ab38bd4b6cf589d6eb3fbe5fdbe8bfd73e6363dfa4a6ddfdf4b2089e86a2', 'F003 exacto');
  let text=base; const changes=[];
  function replace(a,b,n=1){const count=text.split(a).length-1;assert.equal(count,n,'patch occurrence '+a);text=text.split(a).join(b);changes.push({from:a,to:b,occurrences:n});}
  // La tabla transitoria de busqueda estaba en 5000: chocaria con el registro 994.
  replace('8900000000000005000','8900000000000090000',4);
  replace('cmp r4 512\n',`cmp r4 ${CAPACITY}\n`,2);
  replace('cmp r8 512\n','cmp r8 65535\n',2);
  for(const o of [400,402]){
    replace(`store8 9000000000000000${o} 0\nstore8 9000000000000000${o+1} 2\n`, `store8 9000000000000000${o} 255\nstore8 9000000000000000${o+1} 255\n`);
  }
  for(const o of [401,403])replace(`load8 r3 9000000000000000${o}\ncmp r3 2\n`,`load8 r3 9000000000000000${o}\ncmp r3 255\n`,2);
  replace('cmp r10 114688\n',`cmp r10 ${DATA_BYTES}\n`);
  replace('set r5 114688\n',`set r5 ${DATA_BYTES}\n`);
  replace('cmp r5 114688\n',`cmp r5 ${DATA_BYTES}\n`);
  replace('label lctx_get\nset r4 0\nset r0 9\ncmp r9 12\n','label lctx_get\nset r4 0\nset r0 9\ncmp r9 13\n');
  const literal = s => [...Buffer.from(s)].map(b=>`set r14 ${b}\nprint r14\n`).join('');
  replace(literal('114688'),literal(String(DATA_BYTES)));
  // Compatibilidad: ids 0..999 conservan sus tres digitos; los superiores tienen cuatro.
  for (const [label,end] of [['e28_emit_citation','label e28_missing'],['lctx_status','label lctx_clear'],['lctx_add_complete','label e29_after_ack'],['lctx_emit_segment','label lctx_emit_byte']]){
    const start=text.indexOf('label '+label+'\n'),stop=text.indexOf(end,start);
    assert.ok(start>=0&&stop>start);let region=text.slice(start,stop);
    const needle='mov r0 r4\nmov r8 r0\ndiv r8 100\n';assert.equal(region.split(needle).length,2);
    region=region.replace(needle,`mov r0 r4\ncmp r0 1000\njlt f004_digits_${label}\nmov r8 r0\ndiv r8 1000\nadd r8 48\nmov r14 r8\nprint r14\nmod r0 1000\nlabel f004_digits_${label}\nmov r8 r0\ndiv r8 100\n`);
    text=text.slice(0,start)+region+text.slice(stop);changes.push({region:label,change:'ids y conteos de cuatro digitos sin romper formato anterior'});
  }
  // Verificaciones de disposicion: encabezado, metadatos, scratch y texto separados.
  assert.ok(1024+4*CAPACITY<90000&&90000+256<100000);
  assert.ok(DATA_BYTES<2**24&&CAPACITY<65535);
  return {text,report:{capacity:CAPACITY,data_bytes:DATA_BYTES,index_bits:16,offset_bits:24,record_bytes:224,input_bytes:255,sentinel:65535,search_scratch:90000,metadata_start:1024,data_start:100000,changes,base_sha256:sha(Buffer.from(base)),source_sha256:sha(Buffer.from(text))}};
}
