import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import zlib from 'node:zlib';

const root = path.dirname(new URL(import.meta.url).pathname);
const targetPath = path.resolve(process.argv[2] || path.join(root, '../latest/prepared/native/model.rvp.gz'));
const outputPath = path.resolve(process.argv[3] || path.join(root, 'training_retention_audit.json'));
const meta = JSON.parse(fs.readFileSync(path.join(root, 'source_metadata.json')));
const hash = b => crypto.createHash('sha256').update(b).digest('hex');
const nsBase = n => BigInt(n) * 10000000000000000n;
function parse(bytes) {
  if (bytes.subarray(0, 5).toString() !== 'RVPC2') throw Error('Unexpected state format');
  const n = Number(bytes.readBigUInt64LE(5));
  const cells = new Map();
  const other = [];
  for (const line of bytes.subarray(29 + n).toString().split('\n')) {
    const [t, a, v] = line.split(' ');
    if (t === 'O' && Number(v)) cells.set(BigInt(a), Number(v));
    else if (line && t !== 'O') other.push(line);
  }
  return { bytes, cells, kernel: bytes.subarray(29, 29 + n), other };
}
function state(file) {
  let bytes = fs.readFileSync(file);
  if (file.endsWith('.b64')) bytes = Buffer.from(bytes.toString(), 'base64');
  if (file.endsWith('.gz') || file.endsWith('.gz.b64')) bytes = zlib.gunzipSync(bytes);
  return parse(bytes);
}
const byte = (s, a) => s.cells.get(a) || 0;
const uint = (s, a, n = 2) => Array.from({ length: n }, (_, i) => byte(s, a + BigInt(i)) * 256 ** i).reduce((a, b) => a + b, 0);
const bytes = (s, a, n) => Buffer.from(Array.from({ length: n }, (_, i) => byte(s, a + BigInt(i))));
const target = state(targetPath);
const byNamespace = s => {
  const rows = new Map();
  for (const [a, v] of s.cells) {
    const ns = a.toString().slice(0, 3);
    if (!rows.has(ns)) rows.set(ns, new Map());
    rows.get(ns).set(a, v);
  }
  return rows;
};
const targetNamespaces = byNamespace(target);
const table = (name, ns, offset, stride, countOffset, countBytes, capacity, code) => ({ name, ns, offset, stride, countOffset, countBytes, capacity, code });
const sparse = (name, ns, offset, stride, capacity, code) => ({ name, ns, offset, stride, capacity, sparse: true, code });
// All layouts below come from pointer arithmetic in the cited XI sources.
const layouts = [
  table('E009 vocabulary', '710', 1000, 16, 16, 1, 32, 'ai/xi/language/ground.xi'),
  table('E009 concept fingerprints', '710', 601, 1, 17, 1, 16, 'ai/xi/language/ground.xi'),
  table('E009 assertions', '710', 3000, 8, 18, 1, 24, 'ai/xi/language/relate.xi'),
  table('E010 bilingual prototypes', '720', 1000, 32, 10, 1, 32, 'ai/xi/school/learn.xi'),
  table('E011 operator vocabulary', '730', 1000, 32, 4, 1, 32, 'ai/xi/dialogue/learn.xi'),
  table('E012 knowledge vocabulary', '740', 10000, 40, 4, 2, 512, 'ai/xi/knowledge/learn-word.xi'),
  table('E012 knowledge assertions', '740', 80000, 3, 6, 2, 512, 'ai/xi/knowledge/learn-fact.xi'),
  sparse('E012 graph evidence', '740', 1000000, 4, 16777216, 'ai/xi/knowledge/learn-fact.xi'),
  sparse('E014 learned verb effects', '750', 10000, 24, 256, 'ai/xi/stories/learn-effect.xi'),
  table('E015 grammar patterns', '760', 1000, 64, 3, 1, 16, 'ai/xi/grammar/learn-pattern.xi'),
  sparse('E016 utterance orders', '770', 1000, 32, 2, 'ai/xi/conversation/learn-order.xi'),
  sparse('E016 nominal forms', '770', 100000, 112, 512, 'ai/xi/conversation/learn-nominal.xi'),
  table('E017 extended vocabulary', '780', 100000, 40, 6, 2, 2048, 'ai/xi/open/intern.xi'),
  table('E017 induced patterns', '780', 10000, 96, 10, 1, 96, 'ai/xi/open/learn-pattern.xi'),
  table('E017 extended assertions', '780', 200000, 6, 8, 2, 65535, 'ai/xi/open/mutate.xi'),
  sparse('E017 predicate rule records', '780', 2000000, 64, 65536, 'ai/xi/open/learn-rule.xi'),
  sparse('E017 sparse graph evidence', '780', 10000000000, 4, 281474976710656, 'ai/xi/open/edge.xi'),
  table('E020 arithmetic vocabulary', '790', 1000, 32, 4, 1, 256, 'ai/xi/scale/learn-word.xi'),
  table('E021 language patterns', '800', 10000, 96, 4, 1, 128, 'ai/xi/lingua/learn-pattern.xi'),
  table('E021 cues', '800', 1000, 40, 5, 1, 16, 'ai/xi/lingua/learn-cue.xi'),
  table('E022 request patterns', '810', 10000, 96, 4, 1, 64, 'ai/xi/rephrase/induce.xi'),
  table('E022 canonical patterns', '810', 20000, 96, 4, 1, 64, 'ai/xi/rephrase/induce.xi'),
  sparse('E030 preserved personalized patterns', '920', 1024, 256, 8, 'ai/releases/e030/learn.xi'),
  sparse('E032 temporal frames', '865', 4096, 256, 64, 'ai/releases/e032/learn.xi'),
  sparse('E033/E034 relational frames', '840', 4096, 256, 32, 'ai/releases/e034/learn.xi')
];
function slots(s, spec) {
  const start = nsBase(spec.ns) + BigInt(spec.offset);
  if (!spec.sparse) {
    const count = uint(s, nsBase(spec.ns) + BigInt(spec.countOffset), spec.countBytes);
    if (count > spec.capacity) throw Error('Table count exceeds code capacity: ' + spec.name + ' ' + count);
    return Array.from({ length: count }, (_, i) => i);
  }
  const end = start + BigInt(spec.stride) * BigInt(spec.capacity);
  return [...new Set([...s.cells.keys()].filter(a => a >= start && a < end).map(a => Number((a - start) / BigInt(spec.stride))))].sort((a, b) => a - b);
}
function compareTable(source, spec) {
  const ids = slots(source, spec), targetIds = slots(target, spec), differences = [], oldBuffers = [], newBuffers = [];
  const start = nsBase(spec.ns) + BigInt(spec.offset);
  for (const id of ids) {
    const address = start + BigInt(id) * BigInt(spec.stride);
    const old = bytes(source, address, spec.stride), now = bytes(target, address, spec.stride);
    oldBuffers.push(old); newBuffers.push(now);
    if (!old.equals(now)) differences.push({ slot: id, address: String(address), source_sha256: hash(old), target_sha256: hash(now) });
  }
  const result = { module: spec.name, namespace: spec.ns, code: spec.code, source_records: ids.length, target_records: targetIds.length, equal_full_records: ids.length - differences.length, differences, original_records_sha256: hash(Buffer.concat(oldBuffers)), target_same_slots_sha256: hash(Buffer.concat(newBuffers)), includes_implicit_zero_bytes: true, status: differences.length ? 'changed_requires_review' : 'all_original_records_exact' };
  if (spec.name === 'E016 nominal forms') {
    // XI learns independently named segments at 0,34,68 and 102; +101 is a plural bitmask.
    // A new segment in an old record extends learning instead of replacing its old strings.
    const oldFields = [], nowFields = [], changedFields = []; let sourceFields = 0, targetFields = 0;
    for (const id of ids) {
      const address = start + BigInt(id) * BigInt(spec.stride);
      for (const [offset, capacity] of [[0,33],[34,33],[68,33],[102,9]]) {
        if (byte(target, address + BigInt(offset))) targetFields++;
        if (!byte(source, address + BigInt(offset))) continue;
        sourceFields++;
        const old = bytes(source, address + BigInt(offset), capacity), now = bytes(target, address + BigInt(offset), capacity);
        oldFields.push(old); nowFields.push(now);
        if (!old.equals(now)) changedFields.push({slot:id, field_offset:offset});
      }
      const oldMask = byte(source, address+101n), nowMask = byte(target, address+101n);
      if ((oldMask & nowMask) !== oldMask) changedFields.push({slot:id, field:'plural_mask_lost_bits'});
    }
    result.learned_fields = {source:sourceFields,target_in_original_records:targetFields,changed:changedFields,source_sha256:hash(Buffer.concat(oldFields)),target_original_fields_sha256:hash(Buffer.concat(nowFields))};
    if (!changedFields.length) result.status = differences.length ? 'original_fields_preserved_with_additional_learned_fields' : 'all_original_records_exact';
  }
  return result;
}
const counterMeanings = {
  '7400000000000000004': 'low byte of u16 knowledge lexicon count at +4/+5; XI learn-word.xi',
  '7800000000000000004': 'low byte of next u16 concept ID at +4/+5; XI open/intern.xi',
  '7800000000000000006': 'low byte of u16 extended vocabulary count at +6/+7; XI open/intern.xi',
  '7800000000000000008': 'low byte of u16 assertion count at +8/+9; XI open/mutate.xi',
  '7800000000000000010': 'induced pattern count; XI open/learn-pattern.xi',
  '7900000000000000004': 'arithmetic word count; XI scale/learn-word.xi',
  '8100000000000000004': 'request pattern count; XI rephrase/induce.xi',
  '8100000000000000008': 'low byte of u32 paired-presentation count at +8..+11; XI rephrase/finish-teach.xi total_count loop'
};
function compareNamespace(source, ns, original) {
  const current = targetNamespaces.get(ns) || new Map();
  const removed = [], changed = [];
  for (const [a, v] of original) {
    const now = current.get(a) || 0;
    if (now === v) continue;
    const row = { address: String(a), source: v, target: now, interpretation: counterMeanings[String(a)] || 'unclassified' };
    (now ? changed : removed).push(row);
  }
  const additions = [...current].filter(([a]) => !original.has(a));
  const classified = changed.every(x => counterMeanings[x.address]);
  return { namespace: ns, source_nonzero_cells: original.size, target_nonzero_cells: current.size, preserved_nonzero_cells: original.size - changed.length - removed.length, removed, changed, added_nonzero_cells: additions.length, status: !removed.length && !changed.length && !additions.length ? 'whole_namespace_byte_exact' : !removed.length && classified ? 'original_nonzero_bytes_preserved_except_growth_counters' : 'requires_review', semantic_layout_decoded: layouts.some(x => x.ns === ns) };
}
const checkpoints = [];
for (const item of meta.files) {
  const file = path.join(root, item.path), source = state(file), namespaces = byNamespace(source);
  const tables = layouts.filter(x => namespaces.has(x.ns)).map(x => compareTable(source, x));
  const namespaceComparisons = [...namespaces].map(([ns, values]) => compareNamespace(source, ns, values));
  checkpoints.push({ source: { repository: meta.repository, commit: meta.commit, path: item.path, git_blob_sha: item.git_blob_sha, state_sha256: hash(source.bytes), state_bytes: source.bytes.length }, kernel_exact_equal: source.kernel.equals(target.kernel), non_override_records_equal: JSON.stringify(source.other) === JSON.stringify(target.other), total_original_nonzero_cells: source.cells.size, namespaces: namespaceComparisons, learned_tables: tables, status: tables.every(x => ['all_original_records_exact','original_fields_preserved_with_additional_learned_fields'].includes(x.status)) && namespaceComparisons.every(x => !x.removed.length && x.changed.every(y => counterMeanings[y.address])) ? 'original_learned_records_preserved_static_check' : 'requires_review' });
}
function words(s) {
  const B = 7100000000000000000n, count = byte(s, B + 16n), rows = [];
  for (let i = 0; i < count; i++) {
    const p = B + 1000n + BigInt(i * 16), id = byte(s, p + 1n), len = byte(s, p);
    rows.push({ slot: i, word: bytes(s, p + 2n, len).toString(), concept_id: id, sensor_fingerprint: byte(s, B + 600n + BigInt(id)), support: byte(s, p + 10n) });
  }
  return rows;
}
function weightModel(s, base, descriptors, weights, count) {
  return { base_weights: Array.from({length:3},(_,i)=>byte(s,base+BigInt(i))-128), relations: Array.from({length:4},(_,i)=>({descriptor:byte(s,descriptors+BigInt(i)),weight:byte(s,weights+BigInt(i))-128})).filter(x=>x.descriptor).sort((a,b)=>a.descriptor-b.descriptor), relation_count:byte(s,count) };
}
const coreBase=7000000000000000000n;
const bankModels=s=>Array.from({length:byte(s,coreBase+610n)},(_,i)=>{const a=coreBase+700n+64n*BigInt(i);return weightModel(s,a+2n,a+8n,a+16n,a+1n);});
const currentBanks=bankModels(target);
function historicalWeights(s) {
  const active=weightModel(s,coreBase+64n,coreBase+200n,coreBase+220n,coreBase+30n);
  const archived=byte(s,coreBase+500n)===1?weightModel(s,coreBase+401n,coreBase+420n,coreBase+440n,coreBase+404n):null;
  const match=x=>currentBanks.findIndex(y=>JSON.stringify(x)===JSON.stringify(y));
  return {code_layout_sources:['ai/xi/e005/learn.xi','ai/xi/e007/checkpoint.xi','ai/xi/e008/bank-store.xi'],active,active_exact_current_bank_match:match(active),archived,archived_exact_current_bank_match:archived?match(archived):null,banks:bankModels(s).map(x=>({...x,exact_current_bank_match:match(x)}))};
}
const historicalRoot = path.resolve(root, '../historical-library');
const historical = fs.existsSync(historicalRoot) ? fs.readdirSync(historicalRoot).filter(x => x.endsWith('.rvp')).map(name => {
  const source = state(path.join(historicalRoot, name)), nss = byNamespace(source);
  const comparisons = [...nss].map(([ns, values]) => compareNamespace(source, ns, values));
  const lexical = words(source), currentWords = words(target), absentWords = lexical.filter(w => !currentWords.some(t => t.word === w.word && t.sensor_fingerprint === w.sensor_fingerprint));
  const weights=historicalWeights(source);
  let classification=absentWords.length ? 'alternate_E009_campaign_not_merged_into_active_E009_bank' : comparisons.every(n => !n.removed.length && !n.changed.length) ? 'all_original_bytes_preserved' : 'historical_revision_or_active_model_changed_compare_banks_before_merging';
  if (/E005/.test(name)&&weights.active_exact_current_bank_match>=0)classification='historical_trained_model_preserved_in_current_bank';
  if (/E007/.test(name)&&weights.active_exact_current_bank_match>=0&&weights.archived_exact_current_bank_match>=0)classification='both_historical_models_preserved_in_current_banks';
  if (/E008/.test(name)&&weights.banks.length===4&&weights.banks.every(x=>x.exact_current_bank_match>=0))classification='all_four_historical_banks_preserved';
  return { name, source_sha256: hash(source.bytes), state_bytes: source.bytes.length, source_core_schema: byte(source, coreBase+2n), current_core_schema: byte(target, coreBase+2n), kernel_exact_equal: source.kernel.equals(target.kernel), namespaces: comparisons, e009_vocabulary: lexical, words_absent_from_current_active_E009_bank: absentWords, weights, classification, execution_performed: false };
}) : [];
const report = { format: 'BBYQ-Checkpoint-Retention-Audit-1', target: { path: targetPath, state_sha256: hash(target.bytes), state_bytes: target.bytes.length, kernel_sha256: hash(target.kernel) }, method: 'Code-derived logical table layouts; compare every byte including implicit zeros in occupied historical records. Separately compare all historical nonzero overrides and complete unchanged namespaces. No README content used.', execution_scope: 'Static state/code audit only; does not establish that chat dispatch reaches every preserved module.', checkpoints, historical, limitations: ['No historical seed was overwritten or blindly merged.', 'Opaque namespaces marked semantic_layout_decoded=false have byte preservation checks but no semantic record decoder.', 'Distinct synthetic E009 campaigns with conflicting IDs are alternatives; absent words are not automatically evidence of accidental deletion.', 'This audit covers resolved checkpoints, not every checkpoint ever created in every private conversation.'] };
fs.writeFileSync(outputPath, JSON.stringify(report, null, 2) + '\n');
console.log(JSON.stringify({ output: outputPath, target_sha256: report.target.state_sha256, checkpoints: checkpoints.length, statuses: checkpoints.map(x => ({ path: x.source.path, status: x.status, extended_tables: x.learned_tables.filter(t => t.status==='original_fields_preserved_with_additional_learned_fields').map(t => ({ name: t.module, extended_records: t.differences.length, source_fields:t.learned_fields.source,target_fields:t.learned_fields.target_in_original_records })) })), historical: historical.map(x => ({ name: x.name, classification: x.classification, words_not_merged_into_E009_bank: x.words_absent_from_current_active_E009_bank.map(x => x.word) })) }, null, 2));
