import fs from 'node:fs';
import path from 'node:path';
import {spawnSync} from 'node:child_process';
import {B, D, MAX_PAGE_BYTES} from './native.mjs';
import {fileHash, loadStorePage, failure} from './store.mjs';

function registers(jsonl) {
  const rows = [];
  for (const line of jsonl.split('\n')) {
    if (!line.startsWith('{')) continue;
    let row; try { row = JSON.parse(line); } catch (error) { throw failure('E_DICT_NATIVE', 'Invalid dictionary native event', error); }
    if (row.type === 'register') rows.push(row);
  }
  return rows;
}
function speech(jsonl) {
  const bytes = registers(jsonl).filter(row => row.register === 'r14').map(row => row.value);
  if (!bytes.length || bytes.some(value => !Number.isInteger(value) || value < 0 || value > 255)) throw failure('E_DICT_NATIVE', 'Dictionary emitted an invalid response byte stream');
  try { return new TextDecoder('utf-8', {fatal: true}).decode(Uint8Array.from(bytes)); }
  catch (error) { throw failure('E_DICT_NATIVE', 'Dictionary response is not UTF-8', error); }
}
function native(runtime, role, state) {
  const result = spawnSync(runtime, ['run', role, state, state], {encoding: 'utf8', timeout: 30000, maxBuffer: 4 * 1024 * 1024});
  if (result.status !== 0) throw failure('E_DICT_NATIVE', 'Native dictionary role failed: ' + (result.stderr || result.error?.message || result.status), result.error);
  return result.stdout;
}
function trusted(dir, descriptor, name) {
  const entry = descriptor.files?.[name], file = path.join(dir, name);
  try { if (!entry || fs.statSync(file).size !== entry.bytes || fileHash(file) !== entry.sha256) throw Error('Checksum mismatch'); }
  catch (error) { throw failure('E_DICT_CORPUS', 'Dictionary asset integrity failed: ' + name, error); }
  return file;
}

// Capture only the opaque cache range that this transport will overwrite.
// No lemma, definition, payload, or request text is interpreted in the host.
function bankSnapshot(file) {
  const bytes = fs.readFileSync(file);
  if (bytes.length < 29 || bytes.subarray(0, 5).toString() !== 'RVPC2') throw failure('E_DICT_NATIVE', 'Unsupported dictionary state container');
  const prefix = Number(bytes.readBigUInt64LE(5));
  if (!Number.isSafeInteger(prefix) || 29 + prefix > bytes.length) throw failure('E_DICT_NATIVE', 'Invalid state container bounds');
  const low = String(B), high = String(B + BigInt(1024 + MAX_PAGE_BYTES)), cells = [];
  for (const line of bytes.subarray(29 + prefix).toString().split('\n')) {
    if (!line.startsWith('O ')) continue;
    const space = line.indexOf(' ', 2), address = line.slice(2, space);
    if (address.length !== low.length || address < low || address >= high) continue;
    const value = Number(line.slice(space + 1));
    if (!Number.isInteger(value) || value < 0 || value > 255) throw failure('E_DICT_NATIVE', 'Invalid dictionary cache byte');
    if (value) cells.push([address, value]);
  }
  return cells;
}
function stage(runtime, state, directory, name, body) {
  const file = path.join(directory, name + '.xi');
  fs.writeFileSync(file, '#!reverse-pc-machine-v1\n' + body + 'halt\n');
  return native(runtime, file, state);
}

// Caller owns its unpublished working state. This service never publishes or
// replaces the X08 seed. Request recognition and exact record lookup run in XI.
export function service(runtime, assetDir, liveState) {
  runtime = path.resolve(runtime); assetDir = path.resolve(assetDir); liveState = path.resolve(liveState);
  let descriptor;
  try { descriptor = JSON.parse(fs.readFileSync(path.join(assetDir, 'build.json'))); }
  catch (error) { throw failure('E_DICT_CORPUS', 'Dictionary build descriptor is unavailable', error); }
  if (descriptor.version !== 'X09-E031-dictionary-1' || descriptor.runtime_sha256 !== fileHash(runtime)) throw failure('E_DICT_NATIVE', 'Dictionary runtime differs from the verified build');
  const route = trusted(assetDir, descriptor, 'route.rxe'), lookup = trusted(assetDir, descriptor, 'lookup.rxe'), clear = trusted(assetDir, descriptor, 'clear.rxe');
  const storePath = trusted(assetDir, descriptor, 'store.json');
  let store; try { store = JSON.parse(fs.readFileSync(storePath)); } catch (error) { throw failure('E_DICT_CORPUS', 'Invalid dictionary store descriptor', error); }
  const job = fs.mkdtempSync(path.join(path.dirname(liveState), '.x09-dict-')), backup = path.join(job, 'before.rvp');
  fs.copyFileSync(liveState, backup);
  try {
    const priorBank = bankSnapshot(liveState), dispatch = native(runtime, route, liveState), events = registers(dispatch);
    const status = events.filter(row => row.register === 'r0').at(-1)?.value;
    if (status === 0) { fs.copyFileSync(backup, liveState); return {handled: false}; }
    if (status === 2) return {handled: true, status: 'ok', jsonl: dispatch, response: speech(dispatch), pageKey: null};
    if (status !== 1) throw failure('E_DICT_NATIVE', 'Native dictionary frame or namespace is unavailable');
    const pageKey = events.filter(row => row.register === 'r1').at(-1)?.value;
    const page = loadStorePage(assetDir, pageKey, store);
    let frame = '';
    for (let i = 0; i < 3; i++) frame += `store8 ${B + 8n + BigInt(i)} ${(pageKey >>> (i * 8)) & 255}\nstore8 ${B + 16n + BigInt(i)} ${(page.length >>> (i * 8)) & 255}\n`;
    for (let i = 0; i < page.length; i++) frame += `store8 ${B + 1024n + BigInt(i)} ${page[i]}\n`;
    stage(runtime, liveState, job, 'page', frame);
    const jsonl = native(runtime, lookup, liveState);
    const lookupStatus = registers(jsonl).filter(row => row.register === 'r0').at(-1)?.value;
    if (lookupStatus === 4) {
      fs.copyFileSync(backup, liveState);
      return {handled: false, nativeFallback: true, pageKey};
    }
    if (lookupStatus !== 2) throw failure('E_DICT_NATIVE', 'Native dictionary lookup did not consume its request');
    const response = speech(jsonl);
    const cleared = native(runtime, clear, liveState);
    if (registers(cleared).filter(row => row.register === 'r0').at(-1)?.value !== 0) throw failure('E_DICT_NATIVE', 'Native dictionary scratch erasure failed');
    if (priorBank.length) stage(runtime, liveState, job, 'restore-cache', priorBank.map(([address, value]) => `store8 ${address} ${value}\n`).join(''));
    return {handled: true, status: 'ok', jsonl, response, pageKey, pageBytes: page.length, corpusEntries: descriptor.entries};
  } catch (error) {
    fs.copyFileSync(backup, liveState);
    if (!error.code) error.code = 'E_DICT_NATIVE';
    throw error;
  } finally {
    for (const entry of fs.readdirSync(job)) fs.unlinkSync(path.join(job, entry));
    fs.rmdirSync(job);
  }
}
