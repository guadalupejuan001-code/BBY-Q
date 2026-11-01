import {test} from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {executedRoute} from '../agent.mjs';
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'../../..');
test('C15 outcome training has three complete, portable XI-only programs',()=>{
 for(const name of ['birth','update','observe']){
  const text=fs.readFileSync(path.join(root,'ai/xi/cognitive15',name+'.xi'),'utf8');
  assert.ok(text.startsWith('#!reverse-pc-machine-v1\n'));
  assert.doesNotMatch(text,/\bPython\b|\bPyTorch\b|\bQiskit\b|\bnode\b/);
  const lines=text.split('\n'),labels=lines.filter(l=>l.startsWith('label ')).map(l=>l.slice(6));
  assert.equal(labels.length,new Set(labels).size);
  for(const jump of lines.filter(l=>/^(?:jmp|je|jne|jge|jle|jlt|jgt) /.test(l))){
   const label=jump.split(' ').at(-1);
   assert.ok(labels.includes(label),'Missing XI native label '+label);
  }
 }
});
test('C15 observes only actually executed, known original X10 route metadata',()=>{
 const cases=[
  ['X09-preserved',0],['X10-paged-lessons',0],['X10-streamed-text',0],
  ['P03-native-XI',2],['P04-native-XI',3],['quantum',null],
  ['E034-native-XI',null],['P06-native-XI',null]
 ];
 for(const [extension,route]of cases)assert.equal(executedRoute({extension}),route);
 for(const mode of [1,2,3,4,5,9])assert.equal(executedRoute({extension:'P05-context-XI',context_mode:mode}),1);
 for(const mode of [0,6,7,8])assert.equal(executedRoute({extension:'P05-context-XI',context_mode:mode}),null);
 assert.equal(executedRoute({}),null);
});
test('C15 requires provenance-bound real reply rewards; no silent policy control',()=>{
 const agent=fs.readFileSync(path.join(root,'integration/c15/agent.mjs'),'utf8');
 const session=fs.readFileSync(path.join(root,'ai/personal/x10/session.mjs'),'utf8');
 assert.match(agent,/feedback_eligible/);
 assert.match(agent,/SELECT result FROM receipts WHERE id=\?/);
 assert.match(agent,/SELECT 1 FROM c15_feedback WHERE target_id=\?/);
 assert.match(agent,/previous.response/);
 assert.match(agent,/shadow.actual_action/);
 assert.match(agent,/recordFeedback/);
 assert.match(agent,/await|run\(runtime/);
 assert.match(session,/if\(options.shadowC15/);
 assert.match(session,/result.c15_shadow=c15Shadow/);
 assert.match(session,/E_C15_FEEDBACK/);
 assert.match(session,/rl-feedback:/);
 const xi=fs.readFileSync(path.join(root,'ai/xi/cognitive15/observe.xi'),'utf8');
 assert.match(xi,/cmp r8 3/);assert.match(xi,/cmp r12 7000/);
 assert.match(xi,/cmp r4 4/);assert.match(xi,/cmp r4 7/);
 assert.match(xi,/set r14 0/);
});
