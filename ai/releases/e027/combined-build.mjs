#!/usr/bin/env node
// Packaging and transport only. Language inference and context operations remain XI.
import { execFileSync } from 'node:child_process';
import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';

const [runtimeArg, outputArg] = process.argv.slice(2);
if (!runtimeArg || !outputArg) throw Error('usage: node build.mjs RUNTIME OUTPUT_DIR');
const runtime = path.resolve(runtimeArg);
const out = path.resolve(outputArg);
fs.mkdirSync(out, { recursive: true });
function run(...args) {
  return execFileSync(runtime, args, { encoding: 'utf8', maxBuffer: 12 * 1024 * 1024 });
}
execFileSync('python3', ['ai/releases/e025/build.py', runtime, out], { stdio: 'inherit' });
const source = fs.readFileSync('ai/releases/e025/conversation-linked.xi', 'utf8');
const header = '#!reverse-pc-machine-v1';
if (!source.startsWith(header) || source.split(header).length !== 2) {
  throw Error('unexpected E025 XI entry point');
}
const prefix = fs.readFileSync('ai/releases/e027/context-prefix.xi', 'utf8');
// Compose the two existing XI modules, without reimplementing their inference.
const composition = fs.readFileSync('ai/releases/e026/prefix.xi', 'utf8')
  .replace(header, 'label lctx_original');
const continuation = fs.readFileSync('ai/releases/e026/suffix.xi', 'utf8');
let body = source.replace(header, 'label c26_base_entry');
for (const exit of ['label finish\\nhalt', 'label ui_finish\\nhalt']) {
  const marker = exit.replace('\\n', '\n');
  if (body.split(marker).length !== 2) throw Error('E025 exit contract changed');
  body = body.replace(marker, marker.split('\n')[0] + '\njmp c26_finish');
}
const candidate = prefix + composition + body + continuation;
fs.writeFileSync(path.join(out, 'candidate.xi'), candidate);
run('compile', path.join(out, 'candidate.xi'), path.join(out, 'candidate-code.rxe'), 'BBY Q E027 context and composition');
run('pack-app', path.join(out, 'candidate-code.rxe'), path.join(out, 'controller.rvp'),
    path.join(out, 'candidate.rxe'), 'org.reverse.bbyq', 'BBY Q',
    'E027-CtxCompose-2-dev', '496afe3ae9c4bf31472cbada5145d64e5b94ed2a');
const sha = p => crypto.createHash('sha256').update(fs.readFileSync(p)).digest('hex');
const report = {
  version: 'E027-CtxCompose-2-dev',
  original_e025_sha256: sha(path.join(out, 'BBY-Q.rxe')),
  seed_sha256: sha(path.join(out, 'controller.rvp')),
  candidate_sha256: sha(path.join(out, 'candidate.rxe')),
  xi_context: { segments: 512, max_bytes_per_segment: 224, total_max_bytes: 114688,
    features: ['append', 'get', 'find', 'status', 'clear'],
    storage: 'persistent RVPC2; byte-accurate, contiguous segments' },
  composition: { forms: 4, intelligence: 'XI; native atomic responses reused' },
  limitation: 'Indexed retrieval, not automatic semantic integration into every E025 answer.'
};
fs.writeFileSync(path.join(out, 'candidate.json'), JSON.stringify(report, null, 2) + '\n');
console.log(JSON.stringify(report, null, 2));
