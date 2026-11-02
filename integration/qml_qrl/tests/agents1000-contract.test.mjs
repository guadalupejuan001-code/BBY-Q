import {test} from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'../../..');
const xi=name=>fs.readFileSync(path.join(root,'ai/xi/qml_qrl',name+'.xi'),'utf8');
test('Both 1000-qubit agents and their reward/measurement algorithms are native XI',()=>{
 for(const name of ['agents1000-birth','agents1000-stage','agents1000-infer',
   'agents1000-update','agents1000-reward','agents1000-audit','agents1000-ablate']){
  const s=xi(name),lines=s.split('\n');
  assert.ok(s.startsWith('#!reverse-pc-machine-v1\n'));
  assert.doesNotMatch(s,/\bqiskit\b|\btorch\b|\bnumpy\b|\bpytorch\b|\bjavascript\b/i);
  const labels=lines.filter(l=>l.startsWith('label ')).map(x=>x.slice(6));
  assert.equal(new Set(labels).size,labels.length);
  for(const jump of lines.filter(x=>/^(?:jmp|je|jne|jgt|jlt|jge|jle) /.test(x)))
   assert.ok(labels.includes(jump.split(' ').at(-1)),'missing native XI target '+jump);
 }
});
test('QRL owns a SECOND real 1000-qubit component separate from VQC GHZ',()=>{
 const birth=xi('agents1000-birth'),infer=xi('agents1000-infer');
 assert.match(birth,/set r0 1200/);
 assert.match(birth,/set r1 1201/);
 assert.match(birth,/cmp r1 2200/);
 assert.match(birth,/cx \$r0 \$r1/);
 assert.match(birth,/expect Z:1200 Z:2199/);
 assert.match(infer,/set r13 100/);
 assert.match(infer,/set r13 1200/);
 assert.match(infer,/probz \$r13/);
 assert.match(infer,/cmp r11 1000/);
 assert.match(infer,/load8 r5 \$r1/);
 assert.match(infer,/load8 r6 \$r2/);
 assert.match(infer,/z \$r0/);
 assert.match(infer,/label inverse_cx/);
 assert.match(infer,/label restore_cx/);
});
test('Actual measurement is input to native XI reward, not a host-calculated proxy',()=>{
 const host=fs.readFileSync(path.join(root,'integration/qml_qrl/agents1000.mjs'),'utf8');
 const cli=fs.readFileSync(path.join(root,'integration/qml_qrl/cli.mjs'),'utf8');
 assert.match(host,/const readout=resultOf\(call\('agents1000-infer'/);
 assert.match(host,/frame\(job,\[\[4,readout.measured_action\]\]\)/);
 assert.match(host,/call\('agents1000-reward'/);
 assert.match(host,/call\('agents1000-update'/);
 assert.doesNotMatch(host,/Math\.random\(/);
 assert.match(host,/quantum_measurement_used:true/);
 assert.match(cli,/quantumAgents1000/);
 for(const cmd of ['init-agents-1000','enable-agents-1000','vqc1000-train','vqc1000-infer','qrl1000-train','qrl1000-act'])
  assert.ok(cli.includes("'"+cmd+"'"),cmd);
 const reward=xi('agents1000-reward'),update=xi('agents1000-update');
 assert.match(reward,/print r4/);
 assert.match(update,/store8 \$r8 r10/);
 assert.match(update,/cmp r7 100/);
});
