#!/usr/bin/env node
// Build-time XI source linking. Runtime interpretation and mutation are all XI.
import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import {execFileSync} from 'node:child_process';

const [runtimeArg, outputArg] = process.argv.slice(2);
if (!runtimeArg || !outputArg) throw Error('usage: node build.mjs PINNED_RUNTIME OUT');
const runtime=path.resolve(runtimeArg),out=path.resolve(outputArg);
fs.mkdirSync(out,{recursive:true});
execFileSync('node',['ai/releases/e028/build.mjs',runtime,out],{stdio:'inherit'});
const sha=p=>crypto.createHash('sha256').update(fs.readFileSync(p)).digest('hex');
const header='#!reverse-pc-machine-v1';
const e029=fs.readFileSync('ai/releases/e029/natural-intake.xi','utf8');
if (!e029.startsWith(header)) throw Error('E029 header missing');
let linked=fs.readFileSync(path.join(out,'candidate.xi'),'utf8');
if (!linked.startsWith(header)) throw Error('E028 linker contract changed');
function replaceOnce(from,to) {
  if(linked.split(from).length!==2) throw Error('XI linkage marker changed: '+from);
  linked=linked.replace(from,to);
}
replaceOnce(header,'label e29_question_entry');
replaceOnce('label e28_e027_entry\n',
  'label e29_e027_entry\nlabel e28_e027_entry\n');
replaceOnce('label lctx_add_complete\n',
  'label lctx_add_complete\nload8 r3 9100000000000000000\ncmp r3 1\nje e29_native_ack\n');
replaceOnce('mod r0 1\nadd r4 1\n',
  'mod r0 1\nlabel e29_after_ack\nadd r4 1\n');
replaceOnce('label lctx_finish\n',
  'label lctx_finish\nstore8 9100000000000000000 0\n');
const combined=e029+linked+"label e29_native_ack\nload8 r3 7400000000000000003\ncmp r3 2\nje e29_native_ack_en\nset r14 82\nprint r14\nset r14 101\nprint r14\nset r14 103\nprint r14\nset r14 105\nprint r14\nset r14 115\nprint r14\nset r14 116\nprint r14\nset r14 114\nprint r14\nset r14 195\nprint r14\nset r14 169\nprint r14\nset r14 32\nprint r14\nset r14 101\nprint r14\nset r14 115\nprint r14\nset r14 97\nprint r14\nset r14 32\nprint r14\nset r14 97\nprint r14\nset r14 102\nprint r14\nset r14 105\nprint r14\nset r14 114\nprint r14\nset r14 109\nprint r14\nset r14 97\nprint r14\nset r14 99\nprint r14\nset r14 105\nprint r14\nset r14 195\nprint r14\nset r14 179\nprint r14\nset r14 110\nprint r14\nset r14 46\nprint r14\njmp e29_after_ack\nlabel e29_native_ack_en\nset r14 73\nprint r14\nset r14 32\nprint r14\nset r14 114\nprint r14\nset r14 101\nprint r14\nset r14 99\nprint r14\nset r14 111\nprint r14\nset r14 114\nprint r14\nset r14 100\nprint r14\nset r14 101\nprint r14\nset r14 100\nprint r14\nset r14 32\nprint r14\nset r14 116\nprint r14\nset r14 104\nprint r14\nset r14 97\nprint r14\nset r14 116\nprint r14\nset r14 32\nprint r14\nset r14 115\nprint r14\nset r14 116\nprint r14\nset r14 97\nprint r14\nset r14 116\nprint r14\nset r14 101\nprint r14\nset r14 109\nprint r14\nset r14 101\nprint r14\nset r14 110\nprint r14\nset r14 116\nprint r14\nset r14 46\nprint r14\njmp e29_after_ack\n";
fs.writeFileSync(path.join(out,'natural-linked.xi'),combined);
function run(...args) {return execFileSync(runtime,args,{encoding:'utf8',maxBuffer:16*1024*1024});}
run('compile',path.join(out,'natural-linked.xi'),path.join(out,'e029-code.rxe'),
  'BBY Q E029 natural evidence intake');
run('pack-app',path.join(out,'e029-code.rxe'),path.join(out,'controller.rvp'),
  path.join(out,'natural.rxe'),'org.reverse.bbyq','BBY Q',
  'E029-Natural-Facts-1-dev','0a44ffa7a8f7c92a0386beb92f38fd00c7a03aa2');
const report={
  version:'E029-Natural-Facts-1-dev',
  source:'XI-only automatic fact admission, preserving E028/E027/E025',
  original_e025_sha256:sha(path.join(out,'BBY-Q.rxe')),
  seed_sha256:sha(path.join(out,'controller.rvp')),
  e028_candidate_sha256:sha(path.join(out,'candidate.rxe')),
  e029_candidate_sha256:sha(path.join(out,'natural.rxe')),
  context_capacity_bytes:114688,
  guarantees:['no syntax conversion by host','atomic E027 storage','original knowledge fallback',
   'no auto-write for questions or uncertainty indicators','original archive commands'],
  limitations:'One explicitly asserted simple relation per turn, supported relation vocab only; no semantic parsing of free paragraphs, no Android deployment.'
};
fs.writeFileSync(path.join(out,'natural.json'),JSON.stringify(report,null,2)+'\n');
console.log(JSON.stringify(report,null,2));
