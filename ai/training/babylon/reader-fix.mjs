// Reparacion del lector XI: sus valores se emiten directamente desde el archivo.
// No cambia el limite de 224 bytes del hecho ni el ABI de entrada de 255 bytes.
import fs from 'node:fs';
import path from 'node:path';
import assert from 'node:assert/strict';
import {createHash} from 'node:crypto';
const sha=b=>createHash('sha256').update(b).digest('hex');
export function fixReader(exec, oldCode, out) {
 const original=path.join(out,'base-reader.xi');exec('disassemble',oldCode,original);
 const codeMeta=JSON.parse(exec('inspect-rxe',oldCode));
 const roundtrip=path.join(out,'roundtrip-code.rxe');
 exec('compile',original,roundtrip,codeMeta.title);
 assert.equal(sha(fs.readFileSync(roundtrip)),sha(fs.readFileSync(oldCode)),'disassembly roundtrip must be byte-identical');
 const text=fs.readFileSync(original,'utf8'),start=text.indexOf('label e28_fact_value\n'),end=text.indexOf('label e28_value_validate\n',start);
 assert.ok(start>=0&&end>start);const region=text.slice(start,end);
 assert.equal(region.split('cmp r10 81\n').length,2);assert.equal(region.split('cmp r10 80\n').length,2);
 const replacement=region.replace('cmp r10 81\n','cmp r10 225\n').replace('cmp r10 80\n','cmp r10 224\n');
 const patched=text.slice(0,start)+replacement+text.slice(end),source=path.join(out,'f003-reader.xi'),code=path.join(out,'f003-code.rxe');
 fs.writeFileSync(source,patched);exec('compile',source,code,codeMeta.title);
 const before=text.split('\n'),after=patched.split('\n');assert.equal(before.length,after.length);
 const changed=before.flatMap((line,i)=>line===after[i]?[]:[{line:i+1,before:line,after:after[i]}]);assert.equal(changed.length,2);
 const report={roundtrip_byte_identical:true,changed_instructions:changed,old_value_limit:80,new_value_limit:224,record_limit_unchanged:224,input_abi_unchanged:255,original_code_sha256:sha(fs.readFileSync(oldCode)),patched_code_sha256:sha(fs.readFileSync(code)),source_sha256:sha(Buffer.from(patched)),explanation:'El archivo ya guardaba hechos de hasta 224 bytes; el lector descartaba valores de mas de 80. Emite desde el archivo por offset/longitud, sin buffer de valor de 80 bytes. Se conservan filtros de sintaxis y contradicciones.'};
 fs.writeFileSync(path.join(out,'reader-fix.json'),JSON.stringify(report,null,2)+'\n');
 return {source,code,digest:report.source_sha256,report};
}
