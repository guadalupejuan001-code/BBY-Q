import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import {intentSource,CURRICULUM,INTENT_NAMES,INTENT_ADDRESS} from '../../../ai/personal/p01/intent.mjs';
import {B,INPUT} from '../../../ai/personal/x10/schema.mjs';

test('P01 curriculum uses an explicit bounded native vocabulary',()=>{
 assert.equal(INTENT_NAMES.length,9);
 assert.ok(CURRICULUM.length>=50);
 assert.ok(CURRICULUM.length<=255);
 assert.equal(new Set(CURRICULUM.map(([id,,anchored,cue])=>id+':'+anchored+':'+cue)).size,CURRICULUM.length);
 for(const [id,confidence,anchored,cue] of CURRICULUM){
  assert.ok(Number.isInteger(id)&&id>=1&&id<INTENT_NAMES.length);
  assert.ok(Number.isInteger(confidence)&&confidence>=1&&confidence<=100);
  assert.equal(typeof anchored,'boolean');
  assert.match(cue,/^[a-z0-9 ]+$/u);
  if(id===5||id===6)assert.equal(anchored,true,'teaching/correction must be anchored');
 }
 const source=intentSource();
 assert.match(source,/label p01_norm/);
 assert.match(source,/label p01_c3/);
 assert.match(source,/label p01_question/);
 assert.match(source,/label p01_unknown/);
 assert.ok(source.startsWith('#!reverse-pc-machine-v1\n'));
 assert.ok(source.includes('store8 '+(INTENT_ADDRESS+2n)+' 1'),'read-only default must be native');
 assert.ok(source.includes('set r7 '+INPUT),'input must be read by XI');
 assert.ok(source.includes('label p01_rule_0_found'));
 assert.ok(source.length>5000);
 assert.ok(source.length<200000,'keep native code bounded');
 assert.ok(INTENT_ADDRESS>=B+128n&&INTENT_ADDRESS<B+256n);
});

test('X10 calls P01 after routing and preserves explicit X10 instructions',()=>{
 const s=fs.readFileSync(new URL('../../../ai/personal/x10/session.mjs',import.meta.url),'utf8');
 const prep=fs.readFileSync(new URL('../../../integration/x10/prepare.mjs',import.meta.url),'utf8');
 const pages=fs.readFileSync(new URL('../../../ai/personal/x10/pages.mjs',import.meta.url),'utf8');
 assert.match(prep,/\['intent',intentSource\(\)\]/);
 assert.match(prep,/original_training_preserved:true/);
 assert.match(pages,/intent\(raw\)\{/);
 assert.match(pages,/this\.role\('intent\.rxe'\)/);
 assert.match(s,/const route=pages\.route\(raw\),intent=pages\.intent\(raw\)/);
 assert.match(s,/if\(route\.mode===2\|\|route\.mode===3\)/);
 assert.match(s,/if\(route\.mode!==1\)/);
 assert.match(s,/synchronizeLegacy\(db,runtime,input,job,readOnly\)/);
 assert.match(s,/if\(!keepDirty\)db\.exec\('DELETE FROM dirty_slots'\)/);
 assert.match(s,/if\(!readOnly\)\{/);
 assert.match(s,/legacyChat\(runtime,base,input,output,raw/);
 assert.match(s,/intent_confidence/);
});
