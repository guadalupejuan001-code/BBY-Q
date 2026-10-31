import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import {contextSource,CONTEXT_BASE,CONTEXT_MODES,CONTEXT_MAX_CANDIDATES,CONTEXT_MAX_ENTRY_BYTES} from '../../../ai/personal/p05/context.mjs';
import {B} from '../../../ai/personal/x10/schema.mjs';
test('P05 compiles a bounded XI-only candidate and pronoun grammar',()=>{
 const code=contextSource(),lines=code.split('\n');
 assert.ok(code.startsWith('#!reverse-pc-machine-v1\n'));
 assert.equal(CONTEXT_MAX_CANDIDATES,8);
 assert.equal(CONTEXT_MAX_ENTRY_BYTES,384);
 assert.ok(CONTEXT_BASE>B+100000n);
 assert.ok(lines.length>250&&lines.length<7000);
 const labels=lines.filter(s=>s.startsWith('label ')).map(x=>x.slice(6));
 assert.equal(new Set(labels).size,labels.length,'duplicate XI labels');
 const jumps=lines.filter(l=>/^(jmp|je|jne|jgt|jlt|jge|jle) /.test(l)).map(l=>l.split(' ').at(-1));
 for(const label of jumps)assert.ok(labels.includes(label),'Missing XI target '+label);
 for(const line of lines.filter(l=>/^store8 [0-9]/.test(l))){
  const address=BigInt(line.split(' ')[1]);
  assert.ok(address>=CONTEXT_BASE&&address<CONTEXT_BASE+4096n,'XI writes outside P05 result region');
 }
 assert.equal(CONTEXT_MODES.clear,6);
 assert.equal(CONTEXT_MODES.named,1);
 assert.equal(CONTEXT_MODES.pronoun,2);
});
test('X10 prepares P05 native role and retains existing modules',()=>{
 const prepare=fs.readFileSync(new URL('../../../integration/x10/prepare.mjs',import.meta.url),'utf8');
 const pages=fs.readFileSync(new URL('../../../ai/personal/x10/pages.mjs',import.meta.url),'utf8');
 const session=fs.readFileSync(new URL('../../../ai/personal/x10/session.mjs',import.meta.url),'utf8');
 const cli=fs.readFileSync(new URL('../../../bbyq.mjs',import.meta.url),'utf8');
 assert.match(prepare,/\['context',contextSource\(\)\]/);
 assert.match(prepare,/original_training_preserved:true/);
 assert.match(pages,/context\(raw,entries=\[\]\)/);
 assert.match(pages,/this\.role\('context\.rxe'\)/);
 assert.match(session,/contextTurn\(db,decision,rows/);
 assert.match(session,/saveConversation\(db,raw,result,requestId,generation\+1\)/);
 assert.match(session,/options\.module==='p03'/);
 assert.match(session,/options\.module==='p04'/);
 assert.match(session,/options\.module==='e034'/);
 assert.match(cli,/--module=e034\|p03\|p04\|p05/);
});
test('Context index has exact evidence, bounded retention and does not modify training',()=>{
 const source=fs.readFileSync(new URL('../../../ai/personal/p05/store.mjs',import.meta.url),'utf8');
 assert.match(source,/CREATE TABLE IF NOT EXISTS conversation_turns/);
 assert.match(source,/MAX_INDEXED_TURNS=32/);
 assert.match(source,/sha\(Buffer\.from\(row\.utterance\)\)/);
 assert.match(source,/knowledge_read_only:true/);
 assert.match(source,/DELETE FROM conversation_turns/);
 assert.doesNotMatch(source,/UPDATE state SET|UPDATE lessons SET|DELETE FROM lessons/);
});
