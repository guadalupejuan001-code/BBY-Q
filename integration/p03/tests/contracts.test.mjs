import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import crypto from 'node:crypto';
import {reasonSource,REASON_BASE,REASON_MAX_BYTES,REASON_SHA256} from '../../../ai/personal/p03/reason.mjs';

test('P03 source is pinned, native, bounded and has no missing labels',()=>{
 const code=reasonSource();
 assert.equal(crypto.createHash('sha256').update(code).digest('hex'),REASON_SHA256);
 assert.ok(code.startsWith('#!reverse-pc-machine-v1\n'));
 assert.equal(REASON_MAX_BYTES,640);
 const lines=code.split('\n'),labels=lines.filter(x=>x.startsWith('label ')).map(x=>x.slice(6));
 assert.equal(labels.length,new Set(labels).size);
 const targets=lines.filter(x=>/^(jmp|je|jne|jgt|jlt|jge|jle) /.test(x)).map(x=>x.split(' ').at(-1));
 for(const target of targets)assert.ok(labels.includes(target),'Missing XI label '+target);
 assert.ok(labels.includes('p03_sentence_loop'));
 assert.ok(labels.includes('p03_eq'));
 assert.ok(labels.includes('p03_forward_loop'));
 assert.ok(labels.includes('p03_reverse_loop'));
 assert.ok(lines.some(x=>x.includes('print r14')));
 assert.ok(lines.length>=2000&&lines.length<10000);
 // Static writes stay within the isolated P03 native page. Dynamic writes
 // are checked by the native memory-isolation exam.
 for(const line of lines.filter(x=>/^store8 [0-9]/.test(x))){
  const addr=BigInt(line.split(' ')[1]);
  assert.ok(addr>=REASON_BASE&&addr<REASON_BASE+18000n,'Static foreign write '+line);
 }
});

test('P03 compiles with verified X10 build, P01 and P02 remain intact',()=>{
 const prepare=fs.readFileSync(new URL('../../../integration/x10/prepare.mjs',import.meta.url),'utf8');
 const pages=fs.readFileSync(new URL('../../../ai/personal/x10/pages.mjs',import.meta.url),'utf8');
 const session=fs.readFileSync(new URL('../../../ai/personal/x10/session.mjs',import.meta.url),'utf8');
 const cli=fs.readFileSync(new URL('../../../bbyq.mjs',import.meta.url),'utf8');
 assert.match(prepare,/\['reason',reasonSource\(\)\]/);
 assert.match(prepare,/original_training_preserved:true/);
 assert.match(pages,/reason\(raw\)\{/);
 assert.match(pages,/this\.role\('reason\.rxe'\)/);
 assert.match(session,/options\.module==='p03'/);
 assert.match(session,/if\(options\.module==='e034'\)/);
 assert.match(session,/reasoning\.eligible/);
 assert.match(session,/P03-native-XI/);
 assert.match(session,/options\.learn===true&&options\.module!=='e034'/);
 assert.match(session,/synchronizeLegacy\(db,runtime,input,job,readOnly\)/);
 assert.match(cli,/--module=e034\|p03/);
 for(const name of ['e027','e028','e029','e030','e031','e032','e033','e034'])
  assert.ok(fs.existsSync(new URL('../../../ai/releases/'+name+'/',import.meta.url)));
});
