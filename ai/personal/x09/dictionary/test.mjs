import fs from 'node:fs';
import path from 'node:path';
import assert from 'node:assert/strict';
import {execFileSync} from 'node:child_process';
import {service} from './service.mjs';
import {fileHash, loadStorePage} from './store.mjs';
import {F, C, B, D, MAX_PAGE_BYTES} from './native.mjs';

const [runtimeArg, baseArg, assetsArg, seedArg, outArg, ...flags] = process.argv.slice(2);
if (!outArg) throw Error('Usage: node test.mjs RUNTIME X08_NATIVE DICTIONARY_ASSETS SEED NEW_OUTPUT');
const [runtime, base, assets, seed, out] = [runtimeArg, baseArg, assetsArg, seedArg, outArg].map(x => path.resolve(x));
if (fs.existsSync(out)) throw Error('Use a new test output directory');
fs.mkdirSync(out, {recursive: true});
const seedHash = fileHash(seed), assetManifestHash = fileHash(path.join(assets, 'build.json'));
const records = []; let checks = 0, sequence = 0;
function remember(record) { records.push(record); fs.writeFileSync(path.join(out, 'progress.json'), JSON.stringify({checks, records}, null, 2) + '\n'); }
process.on('uncaughtExceptionMonitor', error => {
  fs.writeFileSync(path.join(out, 'failure.json'), JSON.stringify({ok: false, checks, records, code: error.code, message: error.message, cause: error.cause?.code, stack: error.stack}, null, 2) + '\n');
});
function check(condition, name) { assert.ok(condition, name); checks++; }
function run(role, state) { return execFileSync(runtime, ['run', role, state, state], {encoding: 'utf8', timeout: 30000, maxBuffer: 8 * 1024 * 1024}); }
function cells(file) {
  const bytes = fs.readFileSync(file), offset = 29 + Number(bytes.readBigUInt64LE(5)), result = new Map();
  for (const line of bytes.subarray(offset).toString().split('\n')) { const [kind, address, value] = line.split(' '); if (kind === 'O' && Number(value)) result.set(BigInt(address), Number(value)); }
  return result;
}
function frame(text, language = 'es', bankSentinel = false) {
  const id = String(sequence++).padStart(3, '0'), state = path.join(out, id + '-state.rvp'), program = path.join(out, id + '-frame.xi');
  fs.copyFileSync(seed, state); const raw = Buffer.from(text);
  let body = '#!reverse-pc-machine-v1\n', put = (p, value) => { body += `store8 ${p} ${value}\n`; };
  put(F + 2n, 1); put(F + 3n, 0); put(F + 4n, language === 'en' ? 2 : 1); put(F + 8n, raw.length & 255); put(F + 9n, raw.length >>> 8);
  for (let i = 0; i < raw.length; i++) put(C + BigInt(i), raw[i]);
  if (bankSentinel) { put(B + 8n, 37); put(B + 16n, 5); for (let i = 0; i < 5; i++) put(B + 1024n + BigInt(i), 201 + i); }
  body += 'halt\n'; fs.writeFileSync(program, body); run(program, state); run(path.join(base, 'front.rxe'), state);
  const initial = cells(state);
  check((initial.get(9120000000000000002n) || 0) === 0, 'Base front delegates this request');
  check(initial.get(F + 2n) === 1 && initial.get(F + 3n) === 1, 'Base front validated frame');
  return {id, state, before: initial, hash: fileHash(state)};
}
function conserved(before, after, label) {
  const allowed = new Set([F + 2n, F + 3n, F + 10n]);
  const keys = new Set([...before.keys(), ...after.keys()]);
  for (const key of keys) if (!allowed.has(key)) assert.equal(after.get(key) || 0, before.get(key) || 0, label + ' address ' + key);
  checks++;
  check([...after.keys()].every(key => key < D || key >= D + 512n), label + ' control scratch erased');
}
function query(text, language, expectedWord, options = {}) {
  const prepared = frame(text, language, options.bankSentinel), start = performance.now();
  const result = service(runtime, assets, prepared.state);
  check(result.handled === true && result.status === 'ok', text + ' native handled');
  const response = JSON.parse(result.response);
  check(response.word === expectedWord && response.language === language, text + ' exact record identity');
  check(Array.isArray(response.senses) && response.senses.length > 0, text + ' retained senses');
  const after = cells(prepared.state); conserved(prepared.before, after, text);
  check((after.get(F + 2n) || 0) === 0 && after.get(F + 3n) === 1, text + ' native consumed');
  remember({input: text, language, expectedWord, result, milliseconds: performance.now() - start, prior_memory_exact: true});
  console.log(JSON.stringify({event: 'dictionary-query', input: text, word: response.word, senses: response.senses.length, pageKey: result.pageKey}));
}

if (!flags.includes('--remaining-only')) {
  query('@lex money', 'en', 'money', {bankSentinel: true});
  query('@lex es: dinero', 'es', 'dinero');
  query('@lex electric_guitar', 'en', 'electric guitar');
  query('¿Qué significa árbol?', 'es', 'árbol');
  query('What does quasar mean?', 'en', 'quasar');
  query('definition of hyperbola', 'en', 'hyperbola');
}

{
  const prepared = frame('@lex zzzx09nopalabraqvxyz', 'es', true);
  const result = service(runtime, assets, prepared.state);
  check(result.handled && result.response === 'No consta en este diccionario.', 'Absent explicit word rejected natively');
  conserved(prepared.before, cells(prepared.state), 'Absent explicit word');
  remember({input: '@lex zzzx09nopalabraqvxyz', result, prior_memory_exact: true});
}
for (const text of ['hola', 'qué significa zzzx09conceptopropioqvxyz']) {
  const prepared = frame(text, 'es'), result = service(runtime, assets, prepared.state);
  check(result.handled === false, text + ' delegates');
  check(fileHash(prepared.state) === prepared.hash, text + ' byte-exact rollback/delegation');
  remember({input: text, result, state_bytes_exact: true});
}
{
  const prepared = frame('@lex', 'es'), result = service(runtime, assets, prepared.state);
  check(result.handled && result.response.includes('incompleta'), 'Empty explicit request diagnosed natively');
  conserved(prepared.before, cells(prepared.state), 'Empty explicit request');
  remember({input: '@lex', result, prior_memory_exact: true});
}

const store = JSON.parse(fs.readFileSync(path.join(assets, 'store.json')));
{
  // A legitimately absent bucket is distinct from corrupt/missing corpus bytes.
  const index = fs.readFileSync(path.join(assets, 'pages.index'));
  let absent = -1;
  for (let key = 0; key < 131072; key++) if (index.subarray(64 + key * 48, 64 + (key + 1) * 48).every(byte => byte === 0)) { absent = key; break; }
  check(absent >= 0 && loadStorePage(assets, absent, store).length === 0, 'Valid absent page transports an empty page');
}

function damagedAssets(name, damage) {
  const destination = path.join(out, name); fs.mkdirSync(destination);
  for (const file of fs.readdirSync(assets)) fs.symlinkSync(path.join(assets, file), path.join(destination, file));
  damage(destination);
  const prepared = frame('@lex money', 'en'); let error;
  try { service(runtime, destination, prepared.state); } catch (caught) { error = caught; }
  check(error?.code === 'E_DICT_CORPUS', name + ' produces a corpus integrity error');
  check(fileHash(prepared.state) === prepared.hash, name + ' restores exact prior state');
  remember({case: name, code: error.code, message: error.message, state_bytes_exact: true});
}
damagedAssets('missing-corpus', destination => fs.unlinkSync(path.join(destination, 'pages.data')));
damagedAssets('corrupt-corpus', destination => {
  const file = path.join(destination, 'pages.data'); fs.unlinkSync(file); fs.copyFileSync(path.join(assets, 'pages.data'), file);
  const fd = fs.openSync(file, 'r+'), byte = Buffer.alloc(1); fs.readSync(fd, byte, 0, 1, 100); byte[0] ^= 1; fs.writeSync(fd, byte, 0, 1, 100); fs.closeSync(fd);
});
damagedAssets('corrupt-index', destination => {
  const file = path.join(destination, 'pages.index'); fs.unlinkSync(file); fs.copyFileSync(path.join(assets, 'pages.index'), file);
  const fd = fs.openSync(file, 'r+'); fs.writeSync(fd, Buffer.from([255]), 0, 1, 20); fs.closeSync(fd);
});
check(fileHash(seed) === seedHash, 'Original X08 model unchanged');
check(fileHash(path.join(assets, 'build.json')) === assetManifestHash, 'Built assets unchanged by tests');
const result = {ok: true, scope: flags.includes('--remaining-only') ? 'Targeted quiet-window retry: absence, prior cache preservation, delegation, invalid request and corrupt/missing corpus. Prior six successful queries were not repeated.' : 'Complete dictionary service suite', checks, records, seed_sha256: seedHash, dictionary_manifest_sha256: assetManifestHash, corpus_entries: store.entries, pages: store.pages, input_namespace: {F: String(F), C: String(C)}, transient_namespace: {B: String(B), D: String(D), bank_restore_bytes: 1024 + MAX_PAGE_BYTES}, original_model_unchanged: true, no_old_checkpoint_replacement: true};
fs.writeFileSync(path.join(out, 'results.json'), JSON.stringify(result, null, 2) + '\n');
console.log(JSON.stringify({event: 'dictionary-tests-complete', ok: true, checks, out}));
