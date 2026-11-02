import {test} from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'../../..');
const xi=name=>fs.readFileSync(path.join(root,'ai/xi/qml_qrl',name+'.xi'),'utf8');
test('1000-qubit GHZ uses the original native XI instruction grammar',()=>{
 for(const name of ['q1000-birth','q1000-audit','q1000-uncompute','q1000-stats','q1000-bad-marker']){
  const code=xi(name),lines=code.split('\n');
  assert.ok(code.startsWith('#!reverse-pc-machine-v1\n'),name);
  assert.doesNotMatch(code,/\bpython\b|\bqiskit\b|\bpytorch\b|\bnumpy\b/i);
  const labels=lines.filter(s=>s.startsWith('label ')).map(s=>s.slice(6));
  assert.equal(new Set(labels).size,labels.length);
  for(const jump of lines.filter(s=>/^(jmp|je|jne|jlt|jgt|jle|jge) /.test(s)))
   assert.ok(labels.includes(jump.split(' ').at(-1)),jump);
 }
});
test('all 1000 entangled qubits stay disjoint from both legacy engines',()=>{
 const preparation=xi('q1000-birth');
 assert.match(preparation,/set r0 100\nh \$r0/);
 assert.match(preparation,/set r1 101/);
 assert.match(preparation,/cmp r1 1100/);
 assert.match(preparation,/cx \$r0 \$r1/);
 assert.match(preparation,/expect Z:100 Z:1099/);
 assert.match(preparation,/expect Z:100 Z:600/);
 assert.match(preparation,/probz 1099/);
 for(const p of ['vqc2-infer','qrl2-act']){
  const local=xi(p);
  assert.ok(!local.includes('cx 100')&&!local.includes('h 100'));
 }
 const CLI=fs.readFileSync(path.join(root,'integration/qml_qrl/cli.mjs'),'utf8');
 assert.match(CLI,/enable-1000/);
 assert.match(CLI,/init-1000/);
 assert.match(CLI,/audit-1000/);
 assert.match(CLI,/largest_component!==1000/);
 assert.match(CLI,/fs.renameSync\(path.join\(job,'q1000-attached.rvp'\),memory\)/);
});
test('scratch inverse and invalid-marker paths are separate from durable checkpoint',()=>{
 const inverse=xi('q1000-uncompute');
 assert.match(inverse,/set r0 1098/);
 assert.match(inverse,/set r1 1099/);
 assert.match(inverse,/h 100/);
 assert.match(inverse,/probz 600/);
 const invalid=xi('q1000-bad-marker');
 assert.match(invalid,/store8 8100000000000006000 255/);
 const audit=xi('q1000-audit');
 assert.match(audit,/cmp r0 113/);
});
