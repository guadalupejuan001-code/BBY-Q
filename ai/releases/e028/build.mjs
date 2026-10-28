#!/usr/bin/env node
// Source linking, verification and packaging only. Runtime parsing, matching,
// evidence selection, composition and final text are implemented in XI.
import { execFileSync } from 'node:child_process';
import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';

const [runtimeArg, outArg] = process.argv.slice(2);
if (!runtimeArg || !outArg) throw Error('usage: node build.mjs PINNED_RUNTIME OUT_DIR');
const runtime = path.resolve(runtimeArg), out = path.resolve(outArg);
fs.mkdirSync(out, {recursive:true});
function run(...args) {
  return execFileSync(runtime, args, {encoding:'utf8', maxBuffer:16*1024*1024});
}
execFileSync('python3', ['ai/releases/e025/build.py', runtime, out], {stdio:'inherit'});
const header='#!reverse-pc-machine-v1';
const e025=fs.readFileSync('ai/releases/e025/conversation-linked.xi','utf8');
let e027=fs.readFileSync('ai/releases/e027/context-prefix.xi','utf8');
const e028=fs.readFileSync('ai/releases/e028/question-prefix.xi','utf8');
if (![e025,e027,e028].every(s=>s.startsWith(header))) throw Error('Invalid XI source entry');
const clear='label lctx_clear_done\n';
if (e027.split(clear).length!==2) throw Error('E027 clear contract changed');
// Context clear invalidates the E028 conversational referent, not E025 facts.
e027=e027.replace(clear, clear+'store8 9000000000000000032 0\n');
const source=e028+e027.replace(header,'label e28_e027_entry')+
  e025.replace(header,'label lctx_original');
fs.writeFileSync(path.join(out,'candidate.xi'),source);
run('compile',path.join(out,'candidate.xi'),path.join(out,'candidate-code.rxe'),'BBY Q E028 grounded context');
run('pack-app',path.join(out,'candidate-code.rxe'),path.join(out,'controller.rvp'),
  path.join(out,'candidate.rxe'),'org.reverse.bbyq','BBY Q',
  'E028-Context-Reason-1-dev','ed36544e19ace288e75c5a1395f7e81ed21c35ab');
const sha=p=>crypto.createHash('sha256').update(fs.readFileSync(p)).digest('hex');
const report={
  version:'E028-Context-Reason-1-dev',
  original_e025_sha256:sha(path.join(out,'BBY-Q.rxe')),
  seed_sha256:sha(path.join(out,'controller.rvp')),
  candidate_sha256:sha(path.join(out,'candidate.rxe')),
  implemented_in:'XI instructions',
  context:'E027 archive, max 512 fragments and 112 KiB text',
  features:['question intent ES/EN', 'anchored entity and predicate recognition',
    'atomic grounded answers', 'two-relation composition', 'source #fragment IDs',
    'pronoun and followup focus', 'contradiction/negative abstention',
    'preserved E025 fallback and E027 commands'],
  limitations:'Deterministic narrow syntax and ASCII casefold; no general paragraph reading, arbitrary pronoun resolution or generative language model.',
  android_deployed:false
};
fs.writeFileSync(path.join(out,'candidate.json'),JSON.stringify(report,null,2)+'\n');
console.log(JSON.stringify(report,null,2));
