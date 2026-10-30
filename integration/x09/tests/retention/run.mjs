import fs from 'node:fs';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {spawnSync} from 'node:child_process';
import {decodedBytes,sha256,gitBlobSha,readState,comparePreservation} from './state.mjs';

const here = path.dirname(fileURLToPath(import.meta.url));
const flags = {};
for (let i = 2; i < process.argv.length; i += 2) {
  const name = process.argv[i];
  if (!name.startsWith('--') || !process.argv[i+1]) throw Error('Expected --name value');
  if (name in flags) throw Error('Duplicate option: ' + name);
  flags[name] = process.argv[i+1];
}
for (const name of Object.keys(flags)) if (!['--baseline','--candidate','--history-root','--audit-script','--contract','--manifest','--output'].includes(name)) throw Error('Unknown option: '+name);
if (!flags['--candidate'] || !flags['--output']) throw Error('Usage: node run.mjs --candidate STATE --output FRESH_DIR [--baseline STATE --history-root DIR --audit-script FILE --contract JSON --manifest JSON]');
const historyRoot = path.resolve(flags['--history-root'] || path.join(here,'../../../bbyq-training-retention'));
const auditScript = path.resolve(flags['--audit-script'] || path.join(historyRoot,'checkpoints/audit_retention.mjs'));
const baselinePath = path.resolve(flags['--baseline'] || path.join(historyRoot,'latest/prepared/native/model.rvp.gz'));
const candidatePath = path.resolve(flags['--candidate']), output = path.resolve(flags['--output']);
const contract = JSON.parse(fs.readFileSync(path.resolve(flags['--contract'] || path.join(here,'x09-contract.json'))));
const manifest = JSON.parse(fs.readFileSync(path.resolve(flags['--manifest'] || path.join(here,'historical-states.json'))));
if (fs.existsSync(output)) throw Error('Use a fresh output directory');
if (manifest.states.length !== 22) throw Error('Expected all 22 frozen historical states');
if (sha256(fs.readFileSync(auditScript)) !== manifest.audit_script_sha256) throw Error('Historical audit source changed; review before updating the pinned identity');
const identities = [];
for (const item of manifest.states) {
  const file = path.resolve(historyRoot,item.path), relative = path.relative(historyRoot,file);
  if (relative.startsWith('..') || path.isAbsolute(relative)) throw Error('Historical path escapes its archive');
  const raw = fs.readFileSync(file), decoded = decodedBytes(file);
  if (sha256(raw) !== item.raw_sha256 || sha256(decoded) !== item.state_sha256) throw Error('Historical payload changed: '+item.path);
  if (item.git_blob_sha) {
    const extra = item.transport_extra_final_lf || 0;
    if (extra > 0 && !raw.subarray(raw.length-extra).every(byte => byte === 10)) throw Error('Encoded checkpoint transport suffix changed: '+item.path);
    if (gitBlobSha(raw.subarray(0,raw.length-extra)) !== item.git_blob_sha) throw Error('Historical Git blob changed: '+item.path);
  }
  identities.push({path:item.path,raw_sha256:sha256(raw),state_sha256:sha256(decoded),bytes:decoded.length});
}
const baseline = readState(baselinePath), candidate = readState(candidatePath);
if (sha256(baseline.bytes) !== manifest.x08_baseline_sha256) throw Error('Exact audited X08 baseline required');
fs.mkdirSync(output,{recursive:true});
const comparison = comparePreservation(baseline,candidate,contract);
const auditOutput = path.join(output,'historical-audit.json');
const audit = spawnSync(process.execPath,[auditScript,candidatePath,auditOutput],{encoding:'utf8',timeout:120000,maxBuffer:4*1024*1024});
if (audit.status !== 0) throw Error('Historical audit failed: '+audit.stderr);
const historical = JSON.parse(fs.readFileSync(auditOutput));
if (historical.checkpoints.length !== 17 || historical.historical.length !== 5) throw Error('Incomplete historical audit coverage');
const regressions = historical.checkpoints.filter(row => row.status !== 'original_learned_records_preserved_static_check' || !row.kernel_exact_equal);
const inputsUnchanged = sha256(decodedBytes(baselinePath)) === comparison.baseline_sha256 && sha256(decodedBytes(candidatePath)) === comparison.candidate_sha256 && identities.every(item => sha256(fs.readFileSync(path.resolve(historyRoot,item.path))) === item.raw_sha256);
const report = {format:'BBYQ-X09-Retention-1',ok:comparison.ok && regressions.length === 0 && inputsUnchanged,historical_payloads_verified:identities.length,versioned_checkpoint_audits:historical.checkpoints.length,earlier_campaign_audits:historical.historical.length,input_files_unchanged:inputsUnchanged,identities,comparison,regressions:regressions.map(row => ({path:row.source.path,status:row.status})),historical_classifications:historical.historical.map(row => ({name:row.name,classification:row.classification})),scope:'Exact archived payload identities plus code-derived learned-record retention and strict X08-to-X09 state preservation. Separate route/campaign tests must demonstrate operational access to newly installed campaigns.'};
fs.writeFileSync(path.join(output,'result.json'),JSON.stringify(report,null,2)+'\n');
console.log(JSON.stringify({ok:report.ok,output:path.join(output,'result.json'),historical_payloads_verified:22,changed_cells:comparison.changed_cells,outside_allowed:comparison.changes_outside_allowed_ranges,regressions:regressions.length,errors:comparison.errors.length}));
if (!report.ok) process.exitCode = 1;
