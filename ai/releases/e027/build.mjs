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
const candidate = prefix + source.replace(header, 'label lctx_original');
fs.writeFileSync(path.join(out, 'candidate.xi'), candidate);
run('compile', path.join(out, 'candidate.xi'), path.join(out, 'candidate-code.rxe'), 'BBY Q E027 long context');
run('pack-app', path.join(out, 'candidate-code.rxe'), path.join(out, 'controller.rvp'),
    path.join(out, 'candidate.rxe'), 'org.reverse.bbyq', 'BBY Q',
    'E027-Context-1-dev', 'a8f6bb1a2ddb819e8a3173144325564d2460954c');
const sha = p => crypto.createHash('sha256').update(fs.readFileSync(p)).digest('hex');
const report = {
  version: 'E027-Context-1-dev',
  original_e025_sha256: sha(path.join(out, 'BBY-Q.rxe')),
  seed_sha256: sha(path.join(out, 'controller.rvp')),
  candidate_sha256: sha(path.join(out, 'candidate.rxe')),
  xi_context: { segments: 512, max_bytes_per_segment: 224, total_max_bytes: 114688,
    features: ['append', 'get', 'find', 'status', 'clear'],
    storage: 'persistent RVPC2; byte-accurate, contiguous segments' },
  limitation: 'Indexed retrieval, not automatic semantic integration into every E025 answer.'
};
fs.writeFileSync(path.join(out, 'candidate.json'), JSON.stringify(report, null, 2) + '\n');
console.log(JSON.stringify(report, null, 2));
