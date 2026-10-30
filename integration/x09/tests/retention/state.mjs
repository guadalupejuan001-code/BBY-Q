import fs from 'node:fs';
import crypto from 'node:crypto';
import zlib from 'node:zlib';

export const sha256 = value => crypto.createHash('sha256').update(value).digest('hex');
export const gitBlobSha = value => crypto.createHash('sha1').update(Buffer.concat([Buffer.from(`blob ${value.length}\0`),value])).digest('hex');
export function decodedBytes(file) {
  let bytes = fs.readFileSync(file);
  if (file.endsWith('.b64')) bytes = Buffer.from(bytes.toString(), 'base64');
  if (file.endsWith('.gz') || file.endsWith('.gz.b64')) bytes = zlib.gunzipSync(bytes);
  return bytes;
}
export function parseState(bytes) {
  if (bytes.length < 29 || bytes.subarray(0, 5).toString() !== 'RVPC2') throw Error('Invalid RVPC2 header');
  const kernelLength = bytes.readBigUInt64LE(5), payloadLength = bytes.readBigUInt64LE(13);
  if (kernelLength > BigInt(bytes.length - 29) || payloadLength !== BigInt(bytes.length - 29) - kernelLength) throw Error('RVPC2 length mismatch');
  const offset = 29 + Number(kernelLength), cells = new Map(), other = [], counters = new Map();
  for (const line of bytes.subarray(offset).toString().split('\n')) {
    if (!line) continue;
    const match = /^O ([0-9]+) ([0-9]+)$/.exec(line);
    if (match) {
      const address = BigInt(match[1]), value = Number(match[2]);
      if (value > 255 || cells.has(address)) throw Error('Invalid or duplicate RVPC2 override: ' + match[1]);
      cells.set(address, value);
    } else {
      if (line.startsWith('O ')) throw Error('Malformed RVPC2 override');
      const counter = /^MXIM2 ([0-9]+)$/.exec(line);
      if (counter) {
        if (counters.has('MXIM2')) throw Error('Duplicate MXIM2 metadata');
        counters.set('MXIM2', BigInt(counter[1]));
      } else other.push(line);
    }
  }
  return {bytes, cells, kernel: bytes.subarray(29, offset), other, counters};
}
export const readState = file => parseState(decodedBytes(file));
function ranges(rows = []) {
  const parsed = rows.map(row => {
    const start = BigInt(row.start), end = BigInt(row.end_exclusive);
    if (start < 0n || end <= start || end > 9223372036854775808n) throw Error('Invalid signed XI address range: ' + row.name);
    return {...row, start, end};
  }).sort((a,b) => a.start < b.start ? -1 : a.start > b.start ? 1 : 0);
  for (let i = 1; i < parsed.length; i++) if (parsed[i].start < parsed[i-1].end) throw Error('Overlapping address ranges');
  return parsed;
}
const inside = (address, range) => address >= range.start && address < range.end;
export function sparseDigest(state, start, end) {
  const rows = [...state.cells].filter(([address,value]) => value !== 0 && address >= start && address < end).sort((a,b) => a[0] < b[0] ? -1 : 1);
  return sha256(Buffer.from(rows.map(([address,value]) => `${address} ${value}\n`).join('')));
}
export function comparePreservation(baseline, candidate, contract) {
  const additions = ranges(contract.allowed_additions), zeroRanges = ranges(contract.must_be_zero), errors = [], changes = [];
  if (!baseline.kernel.equals(candidate.kernel)) errors.push({kind:'kernel_changed'});
  if (JSON.stringify(baseline.other) !== JSON.stringify(candidate.other)) errors.push({kind:'non_override_records_changed'});
  const allowedCounters = new Set(contract.allowed_serializer_counters || []);
  for (const key of new Set([...baseline.counters.keys(), ...candidate.counters.keys()])) {
    const old = baseline.counters.get(key), now = candidate.counters.get(key);
    if (old !== now && (!allowedCounters.has(key) || old === undefined || now === undefined || now < old)) errors.push({kind:'serializer_counter_changed',counter:key,before:old?.toString(),after:now?.toString()});
  }
  const rangeReports = additions.map(range => {
    const prior = [...baseline.cells].filter(([address]) => inside(address, range));
    const current = [...candidate.cells].filter(([address,value]) => value !== 0 && inside(address, range));
    if (range.requires_empty_baseline !== false && prior.length) errors.push({kind:'new_region_already_occupied',range:range.name,cells:prior.length});
    if (range.requires_nonempty_candidate && !current.length) errors.push({kind:'new_region_not_installed',range:range.name});
    const digest = sparseDigest(candidate, range.start, range.end);
    if (range.expected_sparse_sha256 && digest !== range.expected_sparse_sha256) errors.push({kind:'new_region_digest_mismatch',range:range.name,actual:digest,expected:range.expected_sparse_sha256});
    return {name:range.name,start:String(range.start),end_exclusive:String(range.end),baseline_overrides:prior.length,candidate_nonzero_cells:current.length,sparse_sha256:digest};
  });
  for (const range of zeroRanges) {
    const dirty = [...candidate.cells].filter(([address,value]) => value !== 0 && inside(address, range));
    if (dirty.length) errors.push({kind:'dirty_scratch',range:range.name,cells:dirty.length,first_addresses:dirty.slice(0,8).map(([address]) => String(address))});
  }
  for (const address of new Set([...baseline.cells.keys(), ...candidate.cells.keys()])) {
    const before = baseline.cells.get(address), after = candidate.cells.get(address);
    if (before === after) continue;
    const allowed = additions.find(range => inside(address, range));
    const row = {address:String(address),before:before ?? null,after:after ?? null,range:allowed?.name || null};
    changes.push(row);
    if (!allowed) errors.push({kind:'historical_state_changed',...row});
  }
  for (const check of contract.expected_cells || []) {
    const observed = candidate.cells.get(BigInt(check.address)) || 0;
    if (observed !== check.value) errors.push({kind:'expected_cell_mismatch',address:check.address,expected:check.value,observed});
  }
  return {ok:errors.length === 0,baseline_sha256:sha256(baseline.bytes),candidate_sha256:sha256(candidate.bytes),kernel_sha256:sha256(candidate.kernel),baseline_overrides:baseline.cells.size,candidate_overrides:candidate.cells.size,changed_cells:changes.length,changes_outside_allowed_ranges:changes.filter(row => !row.range).length,first_changes:changes.slice(0,24),ranges:rangeReports,serializer_counters:[...candidate.counters].map(([key,value]) => ({key,before:baseline.counters.get(key)?.toString(),after:String(value)})),errors};
}
