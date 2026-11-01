import {test} from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {corpus} from './corpus.mjs';
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'../..');
test('C14 has exactly 1000 balanced synthetic Spanish examples',()=>{
 const {train,holdout,meta}=corpus();
 assert.equal(train.length,800);assert.equal(holdout.length,200);
 assert.equal(meta.real_conversations,false);
 for(let route=0;route<4;route++){
  assert.equal(train.filter(x=>x.label===route).length,200);
  assert.equal(holdout.filter(x=>x.label===route).length,50);
 }
 assert.equal(new Set([...train,...holdout].map(x=>x.text)).size,1000);
});
test('C14 holdout shares neither topic nor phrasing template with train',()=>{
 const {train,holdout}=corpus(),trainTopics=new Set(train.map(x=>x.topic)),
  trainTemplates=new Set(train.map(x=>x.family+':'+x.template));
 for(const sample of holdout){
  assert.ok(!trainTopics.has(sample.topic),'Topic leakage');
  assert.ok(!trainTemplates.has(sample.family+':'+sample.template),'Template leakage');
 }
});
test('C14 uses only native XI files for feature parsing, counters, policy decisions',()=>{
 const p=path.join(root,'ai/xi/cognitive14');
 for(const name of ['birth','train-batch','features','decide']){
  const text=fs.readFileSync(path.join(p,name+'.xi'),'utf8'),lines=text.split('\n');
  assert.ok(text.startsWith('#!reverse-pc-machine-v1\n'));
  const labels=lines.filter(x=>x.startsWith('label ')).map(x=>x.slice(6));
  assert.equal(labels.length,new Set(labels).size);
  for(const line of lines.filter(x=>/^(?:jmp|je|jne|jgt|jlt|jge|jle) /.test(x)))
   assert.ok(labels.includes(line.split(' ').at(-1)),'Missing native label '+line);
  assert.doesNotMatch(text,/\bpython\b|\bqiskit\b|\bnode\b|pytorch/i);
 }
 const policy=fs.readFileSync(path.join(p,'decide.xi'),'utf8');
 assert.match(policy,/cmp r5 3/);assert.match(policy,/cmp r10 4/);
 assert.match(policy,/cmp r10 7/);assert.match(policy,/set r6 0/);
});
