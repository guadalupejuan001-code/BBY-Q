import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import {paraphraseSource,PARAPHRASE_BASE,PARAPHRASE_MAX_INPUT,PARAPHRASE_MAX_OUTPUT,
 PARAPHRASE_RULES,PARAPHRASE_MODES} from '../../../ai/personal/p06/paraphrase.mjs';
import {B} from '../../../ai/personal/x10/schema.mjs';

test('P06 has productive but strictly bounded XI rewrite grammar',()=>{
 assert.ok(PARAPHRASE_RULES.length>=120&&PARAPHRASE_RULES.length<=255);
 assert.equal(PARAPHRASE_MAX_INPUT,512);
 assert.equal(PARAPHRASE_MAX_OUTPUT,768);
 assert.ok(PARAPHRASE_BASE>B+250000n);
 const seen=new Set();
 const counts=new Map();
 for(const r of PARAPHRASE_RULES){
  assert.equal(typeof r.source,'string');
  assert.equal(typeof r.target,'string');
  assert.ok(r.source.endsWith(' ')||r.source.endsWith('hecho: '));
  assert.ok(!seen.has(r.source),'repeated source: '+r.source);
  seen.add(r.source);
  assert.ok(Number.isInteger(r.mode)&&r.mode>=1&&r.mode<=5);
  counts.set(r.mode,(counts.get(r.mode)||0)+1);
 }
 for(let mode=1;mode<=5;mode++)assert.ok(counts.get(mode)>=5,'insufficient scoped patterns '+mode);
 assert.ok(PARAPHRASE_RULES.some(r=>r.source.includes('cuatro versos')&&r.target.includes('4 versos')));
 assert.ok(PARAPHRASE_RULES.some(r=>r.source.includes('cuéntame')&&r.mode===PARAPHRASE_MODES.story));
 assert.ok(PARAPHRASE_RULES.some(r=>r.source.includes('remind me')&&r.mode===PARAPHRASE_MODES.recall));
 const xi=paraphraseSource(),lines=xi.split('\n');
 assert.ok(xi.startsWith('#!reverse-pc-machine-v1\n'));
 assert.ok(lines.length>5000&&lines.length<55000);
 const labels=lines.filter(l=>l.startsWith('label ')).map(l=>l.slice(6));
 assert.equal(labels.length,new Set(labels).size,'repeated XI labels');
 for(const line of lines.filter(l=>/^(jmp|je|jne|jgt|jlt|jge|jle) /.test(l)))
  assert.ok(labels.includes(line.split(' ').at(-1)),'Unresolved jump: '+line);
 for(const line of lines.filter(l=>/^store8 [0-9]/.test(l))){
  const a=BigInt(line.split(' ')[1]);
  assert.ok(a>=PARAPHRASE_BASE&&a<PARAPHRASE_BASE+64n,'XI memory outside P06: '+line);
 }
 assert.match(xi,/label p06_copy_tail/);
 assert.match(xi,/label p06_capture/);
 assert.match(xi,/label p06_validate/);
 assert.match(xi,/label p06_topic_limit/);
});

test('P06 is compiled, read-only and routed only through validating skills',()=>{
 const prep=fs.readFileSync(new URL('../../../integration/x10/prepare.mjs',import.meta.url),'utf8');
 const pages=fs.readFileSync(new URL('../../../ai/personal/x10/pages.mjs',import.meta.url),'utf8');
 const session=fs.readFileSync(new URL('../../../ai/personal/x10/session.mjs',import.meta.url),'utf8');
 const cli=fs.readFileSync(new URL('../../../bbyq.mjs',import.meta.url),'utf8');
 assert.match(prep,/\['paraphrase',paraphraseSource\(\)\]/);
 assert.match(prep,/original_training_preserved:true/);
 assert.match(pages,/paraphrase\(raw\)\{/);
 assert.match(pages,/this\.role\('paraphrase\.rxe'\)/);
 assert.match(session,/function generalized\(/);
 assert.match(session,/pages\.paraphrase\(raw\)/);
 assert.match(session,/pages\.context\(canonical/);
 assert.match(session,/pages\.compose\(canonical\)/);
 assert.match(session,/pages\.reason\(canonical\)/);
 assert.match(session,/paraphrase_engine:'P06-native-XI'/);
 assert.match(session,/!.*\['teaching','correction'\]/);
 assert.match(session,/options\.module==='p06'/);
 assert.match(session,/options\.learn===true&&options\.module!=='e034'/);
 assert.match(cli,/--module=e034\|p03\|p04\|p05\|p06/);
 assert.match(session,/saveConversation\(db,raw,result,requestId,generation\+1\)/);
});
