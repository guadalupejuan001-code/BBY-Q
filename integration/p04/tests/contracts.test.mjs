import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import {composeSource,COMPOSE_BASE,COMPOSE_LIMIT,COMPOSE_MODES} from '../../../ai/personal/p04/compose.mjs';
import {B} from '../../../ai/personal/x10/schema.mjs';

test('P04 emits a native XI role with bounded scratch, no inferred knowledge or weights',()=>{
 const code=composeSource(),lines=code.split('\n');
 assert.ok(code.startsWith('#!reverse-pc-machine-v1\n'));
 assert.equal(COMPOSE_LIMIT,768);
 assert.equal(COMPOSE_MODES.poem,1);
 assert.equal(COMPOSE_MODES.story,2);
 assert.equal(COMPOSE_MODES.grounded_explanation,3);
 assert.ok(COMPOSE_BASE>B+83536n);
 assert.ok(lines.some(l=>l==='label p04_creative'));
 assert.ok(lines.some(l=>l==='label p04_explain_parse'));
 assert.ok(lines.some(l=>l==='label p04_fields_done'));
 assert.ok(lines.some(l=>l==='label p04_unhandled'));
 assert.ok(lines.some(l=>l.includes('print r14')));
 const labels=lines.filter(x=>x.startsWith('label ')).map(x=>x.slice(6));
 assert.equal(labels.length,new Set(labels).size);
 const jumps=lines.filter(l=>/^(jmp|je|jne|jgt|jlt|jge|jle) /.test(l)).map(l=>l.split(' ').at(-1));
 for(const label of jumps)assert.ok(labels.includes(label),'Unresolved XI jump: '+label);
 const staticWrites=lines.filter(l=>/^store8 [0-9]/.test(l));
 for(const line of staticWrites){
  const address=BigInt(line.split(' ')[1]);
  assert.ok(address>=COMPOSE_BASE&&address<COMPOSE_BASE+4096n,'Foreign direct write: '+line);
 }
 assert.ok(code.length>15000&&code.length<300000,'native source must be bounded');
});

test('P04 is compiled in the preserved X10 delivery and routes safely',()=>{
 const prepare=fs.readFileSync(new URL('../../../integration/x10/prepare.mjs',import.meta.url),'utf8');
 const pages=fs.readFileSync(new URL('../../../ai/personal/x10/pages.mjs',import.meta.url),'utf8');
 const session=fs.readFileSync(new URL('../../../ai/personal/x10/session.mjs',import.meta.url),'utf8');
 const cli=fs.readFileSync(new URL('../../../bbyq.mjs',import.meta.url),'utf8');
 assert.match(prepare,/\['compose',composeSource\(\)\]/);
 assert.match(prepare,/original_training_preserved:true/);
 assert.match(pages,/compose\(raw\)\{/);
 assert.match(pages,/this\.role\('compose\.rxe'\)/);
 assert.match(session,/options\.module==='p04'/);
 assert.match(session,/intent\.name==='creation'/);
 assert.match(session,/intent\.name==='explanation'/);
 assert.match(session,/P04-native-XI/);
 assert.match(session,/if\(route\.mode!==1\)/);
 assert.match(session,/reasoning\?\.eligible/);
 assert.match(session,/if\(options\.module==='e034'\)/);
 assert.match(session,/options\.learn===true&&options\.module!=='e034'/);
 assert.match(cli,/--module=e034\|p03\|p04/);
});
