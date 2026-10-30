import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import readline from 'node:readline';
import {pipeline} from 'node:stream/promises';
import {createGunzip, deflateRawSync, inflateRawSync} from 'node:zlib';

// This store transports opaque, complete E031 byte pages. It never chooses a
// lemma, translates, searches definitions, or supplies a dictionary answer.
export const KEY_SPACE = 131072, HEADER_BYTES = 64, INDEX_STRIDE = 48;
const MAGIC = Buffer.from('BBYQ-DICT-X09');
export const sha256 = bytes => crypto.createHash('sha256').update(bytes).digest('hex');
export function failure(code, message, cause) {
  const error = new Error(message, cause ? {cause} : undefined);
  error.code = code;
  return error;
}
export function fileHash(file) {
  const hash = crypto.createHash('sha256'), fd = fs.openSync(file, 'r');
  const buffer = Buffer.allocUnsafe(64 * 1024);
  try { for (;;) { const n = fs.readSync(fd, buffer, 0, buffer.length, null); if (!n) break; hash.update(buffer.subarray(0, n)); } }
  finally { fs.closeSync(fd); }
  return hash.digest('hex');
}
function writeAll(fd, bytes) {
  for (let at = 0; at < bytes.length;) at += fs.writeSync(fd, bytes, at, bytes.length - at);
}
function countRecords(bytes) {
  let offset = 0, count = 0;
  while (offset < bytes.length) {
    if (offset + 6 > bytes.length) throw Error('Truncated original E031 record');
    const word = bytes.readUInt16LE(offset), payload = bytes.readUInt32LE(offset + 2);
    offset += 6 + word + payload;
    if (!word || !payload || offset > bytes.length) throw Error('Invalid original E031 record bounds');
    count++;
  }
  return count;
}

export async function packStore(gzipStream, sourceManifest, outDir) {
  const index = Buffer.alloc(HEADER_BYTES + KEY_SPACE * INDEX_STRIDE);
  MAGIC.copy(index); index.writeUInt32LE(1, 16); index.writeUInt32LE(KEY_SPACE, 20); index.writeUInt32LE(INDEX_STRIDE, 24);
  const gzipHash = crypto.createHash('sha256'), dataHash = crypto.createHash('sha256');
  const tempData = path.join(outDir, 'pages.data.part'), fd = fs.openSync(tempData, 'wx');
  let offset = 0, pages = 0, rawBytes = 0, entries = 0, maxPage = 0;
  const languageEntries = {es: 0, en: 0};
  gzipStream.on('data', bytes => gzipHash.update(bytes));
  const gunzip = createGunzip(), pumping = pipeline(gzipStream, gunzip);
  pumping.catch(() => {});
  const lines = readline.createInterface({input: gunzip, crlfDelay: Infinity});
  try {
    for await (const line of lines) {
      if (!line) continue;
      const row = JSON.parse(line), key = row.page;
      if (!Number.isInteger(key) || key < 0 || key >= KEY_SPACE || typeof row.bytes !== 'string') throw Error('Invalid E031 page identity');
      const at = HEADER_BYTES + key * INDEX_STRIDE;
      if (index.readUInt32LE(at + 8)) throw Error('Duplicate E031 page identity');
      const raw = Buffer.from(row.bytes, 'base64');
      if (!raw.length || raw.toString('base64') !== row.bytes || raw.length > sourceManifest.max_page_bytes) throw Error('Invalid original E031 page bytes');
      const records = countRecords(raw), packed = deflateRawSync(raw, {level: 9});
      index.writeBigUInt64LE(BigInt(offset), at); index.writeUInt32LE(packed.length, at + 8); index.writeUInt32LE(raw.length, at + 12);
      Buffer.from(sha256(raw), 'hex').copy(index, at + 16);
      writeAll(fd, packed); dataHash.update(packed); offset += packed.length;
      rawBytes += raw.length; maxPage = Math.max(maxPage, raw.length); pages++; entries += records;
      languageEntries[key < 65536 ? 'es' : 'en'] += records;
    }
    await pumping;
    const originalHash = gzipHash.digest('hex');
    if (originalHash !== sourceManifest.dictionary_gzip_sha256) throw Error('Original dictionary export SHA256 differs');
    if (pages !== sourceManifest.pages || rawBytes !== sourceManifest.stored_bytes || entries !== sourceManifest.entries || maxPage !== sourceManifest.max_page_bytes) throw Error('Original E031 corpus counts differ');
    if (languageEntries.es !== sourceManifest.languages.es.unique_forms || languageEntries.en !== sourceManifest.languages.en.unique_forms) throw Error('Original language entry counts differ');
    index.writeUInt32LE(pages, 28); index.writeBigUInt64LE(BigInt(rawBytes), 32); index.writeBigUInt64LE(BigInt(entries), 40);
    fs.fsyncSync(fd); fs.closeSync(fd); fs.renameSync(tempData, path.join(outDir, 'pages.data'));
    fs.writeFileSync(path.join(outDir, 'pages.index'), index, {flag: 'wx'});
    const descriptor = {
      version: 1, codec: 'deflate-raw-per-page', key_space: KEY_SPACE, header_bytes: HEADER_BYTES, index_stride: INDEX_STRIDE,
      pages, entries, language_entries: languageEntries, raw_page_bytes: rawBytes, max_page_bytes: maxPage,
      source_export_sha256: originalHash,
      index: {file: 'pages.index', bytes: index.length, sha256: sha256(index)},
      data: {file: 'pages.data', bytes: offset, sha256: dataHash.digest('hex')}
    };
    fs.writeFileSync(path.join(outDir, 'store.json'), JSON.stringify(descriptor, null, 2) + '\n', {flag: 'wx'});
    return descriptor;
  } catch (error) {
    gzipStream.destroy(); gunzip.destroy(); lines.close();
    try { fs.closeSync(fd); } catch {}
    try { fs.unlinkSync(tempData); } catch {}
    throw error;
  }
}

function verifyFile(dir, entry) {
  if (!entry || typeof entry.file !== 'string' || !/^[a-z0-9.-]+$/.test(entry.file) || !/^[a-f0-9]{64}$/.test(entry.sha256)) throw failure('E_DICT_CORPUS', 'Invalid dictionary store descriptor');
  const file = path.join(dir, entry.file);
  let size, hash;
  try { size = fs.statSync(file).size; hash = fileHash(file); }
  catch (error) { throw failure('E_DICT_CORPUS', 'Dictionary corpus file is unavailable: ' + entry.file, error); }
  if (size !== entry.bytes || hash !== entry.sha256) throw failure('E_DICT_CORPUS', 'Dictionary corpus integrity failed: ' + entry.file);
  return file;
}
function readExactly(fd, buffer, position) {
  let got = 0;
  while (got < buffer.length) { const n = fs.readSync(fd, buffer, got, buffer.length - got, position + got); if (!n) throw failure('E_DICT_CORPUS', 'Dictionary page is truncated'); got += n; }
}

export function loadStorePage(dir, key, manifest) {
  if (!Number.isInteger(key) || key < 0 || key >= KEY_SPACE) throw failure('E_DICT_NATIVE', 'Native dictionary page identity is outside its contract');
  if (manifest.version !== 1 || manifest.codec !== 'deflate-raw-per-page' || manifest.key_space !== KEY_SPACE || manifest.index_stride !== INDEX_STRIDE || manifest.header_bytes !== HEADER_BYTES) throw failure('E_DICT_CORPUS', 'Unsupported dictionary store format');
  const indexFile = verifyFile(dir, manifest.index), dataFile = verifyFile(dir, manifest.data);
  const indexFd = fs.openSync(indexFile, 'r');
  const header = Buffer.alloc(HEADER_BYTES), record = Buffer.alloc(INDEX_STRIDE);
  try { readExactly(indexFd, header, 0); readExactly(indexFd, record, HEADER_BYTES + key * INDEX_STRIDE); }
  finally { fs.closeSync(indexFd); }
  if (!header.subarray(0, MAGIC.length).equals(MAGIC) || header.readUInt32LE(16) !== 1 || header.readUInt32LE(20) !== KEY_SPACE || header.readUInt32LE(24) !== INDEX_STRIDE || manifest.index.bytes !== HEADER_BYTES + KEY_SPACE * INDEX_STRIDE) throw failure('E_DICT_CORPUS', 'Dictionary index header is invalid');
  const offset = Number(record.readBigUInt64LE()), packedLength = record.readUInt32LE(8), rawLength = record.readUInt32LE(12);
  if (!packedLength && !rawLength && record.equals(Buffer.alloc(INDEX_STRIDE))) return Buffer.alloc(0);
  if (!Number.isSafeInteger(offset) || !packedLength || !rawLength || rawLength > manifest.max_page_bytes || offset + packedLength > manifest.data.bytes) throw failure('E_DICT_CORPUS', 'Dictionary page bounds are invalid');
  const dataFd = fs.openSync(dataFile, 'r'), packed = Buffer.alloc(packedLength);
  try { readExactly(dataFd, packed, offset); } finally { fs.closeSync(dataFd); }
  let raw;
  try { raw = inflateRawSync(packed, {maxOutputLength: rawLength}); }
  catch (error) { throw failure('E_DICT_CORPUS', 'Dictionary page cannot be decompressed', error); }
  if (raw.length !== rawLength || sha256(raw) !== record.subarray(16).toString('hex')) throw failure('E_DICT_CORPUS', 'Dictionary page checksum differs');
  return raw;
}
