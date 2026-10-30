import fs from 'node:fs';
import path from 'node:path';
import {execFileSync, spawn} from 'node:child_process';
import {fileURLToPath} from 'node:url';
import {packStore, fileHash} from './store.mjs';
import {routeSource, lookupSource, clearSource, B, D, MAX_PAGE_BYTES} from './native.mjs';

export const ORIGINAL_ARCHIVE_SHA256 = '70a9d7036f370f8328f22c7f29c3c9832ac7a875876f8992be03bc8e44ceb488';
const here = path.dirname(fileURLToPath(import.meta.url));
export async function buildDictionary(runtime, {archive, outDir}) {
  runtime = path.resolve(runtime); archive = path.resolve(archive); outDir = path.resolve(outDir);
  if (fileHash(archive) !== ORIGINAL_ARCHIVE_SHA256) throw Error('The verified complete E031 archive is required');
  fs.mkdirSync(outDir, {recursive: true});
  if (fs.readdirSync(outDir).length) throw Error('Dictionary build requires a new or empty output directory');
  const sourceManifest = JSON.parse(execFileSync('unzip', ['-p', archive, 'dictionary/manifest.json'], {encoding: 'utf8', maxBuffer: 1024 * 1024}));
  fs.writeFileSync(path.join(outDir, 'source-manifest.json'), JSON.stringify(sourceManifest, null, 2) + '\n', {flag: 'wx'});
  const licenses = ['LICENSE-Princeton-WordNet.txt', 'LICENSE-en.txt', 'LICENSE-es.txt'];
  for (const name of licenses) fs.writeFileSync(path.join(outDir, name), execFileSync('unzip', ['-p', archive, 'dictionary/' + name], {maxBuffer: 1024 * 1024}), {flag: 'wx'});
  const child = spawn('unzip', ['-p', archive, 'dictionary/dictionary-pages.jsonl.gz'], {stdio: ['ignore', 'pipe', 'pipe']});
  let stderr = ''; child.stderr.on('data', bytes => { if (stderr.length < 4096) stderr += bytes; });
  const completed = new Promise((resolve, reject) => { child.once('error', reject); child.once('close', code => code === 0 ? resolve() : reject(Error('E031 export extraction failed: ' + stderr))); });
  completed.catch(() => {});
  let store;
  try { store = await packStore(child.stdout, sourceManifest, outDir); await completed; }
  catch (error) { child.kill(); throw error; }
  const originalLookup = fs.readFileSync(path.join(here, 'original-lookup.xi'), 'utf8');
  const roles = {route: routeSource(), lookup: lookupSource(originalLookup), clear: clearSource()};
  for (const [name, source] of Object.entries(roles)) {
    fs.writeFileSync(path.join(outDir, name + '.xi'), source, {flag: 'wx'});
    execFileSync(runtime, ['compile', path.join(outDir, name + '.xi'), path.join(outDir, name + '.rxe'), 'BBY Q X09 E031 dictionary ' + name], {encoding: 'utf8', timeout: 30000, maxBuffer: 1024 * 1024});
  }
  const files = {};
  for (const name of ['route.xi', 'route.rxe', 'lookup.xi', 'lookup.rxe', 'clear.xi', 'clear.rxe', 'store.json', 'source-manifest.json', ...licenses]) files[name] = {bytes: fs.statSync(path.join(outDir, name)).size, sha256: fileHash(path.join(outDir, name))};
  const descriptor = {
    version: 'X09-E031-dictionary-1', runtime_sha256: fileHash(runtime), original_archive_sha256: ORIGINAL_ARCHIVE_SHA256,
    original_lookup_source_sha256: fileHash(path.join(here, 'original-lookup.xi')),
    source: {repository: sourceManifest.source_repository, commit: sourceManifest.source_commit, wordnet_repository: sourceManifest.wordnet_data_repository, wordnet_commit: sourceManifest.wordnet_data_commit},
    entries: store.entries, language_entries: store.language_entries, pages: store.pages, max_page_bytes: MAX_PAGE_BYTES,
    corpus: {index: store.index, data: store.data, source_export_sha256: store.source_export_sha256},
    protocol: {entry: 'validated X06 frame after X08 front fallback', status_register: 'r0', page_register: 'r1', request_bytes: 250, control: String(D), control_bytes: 512, bank: String(B), bank_restore_bytes: 1024 + MAX_PAGE_BYTES, preserve_prior_bank: true},
    files
  };
  fs.writeFileSync(path.join(outDir, 'build.json'), JSON.stringify(descriptor, null, 2) + '\n', {flag: 'wx'});
  return descriptor;
}

if (process.argv[1] && path.resolve(process.argv[1]) === fileURLToPath(import.meta.url)) {
  const [runtime, archive, outDir] = process.argv.slice(2);
  if (!outDir) throw Error('Usage: node build.mjs RUNTIME COMPLETE_E031_ARCHIVE OUT_DIR');
  console.log(JSON.stringify(await buildDictionary(runtime, {archive, outDir}), null, 2));
}
