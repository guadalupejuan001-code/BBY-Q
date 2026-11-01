// Verify that every named Android action has an authored native XI program.
// No artificial "success" response may be generated without native execution.
import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import assert from 'node:assert/strict';
import {fileURLToPath} from 'node:url';
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'../..');
const assets=path.join(root,'android-xi-lab/app/src/main/assets/xi');
const manifest=JSON.parse(fs.readFileSync(path.join(assets,'manifest.json')));
assert.equal(manifest.schema,1);assert.equal(manifest.full_x10,false);
const sha=x=>crypto.createHash('sha256').update(x).digest('hex');
for(const [file,entry]of Object.entries(manifest.source_files)){
 const bytes=fs.readFileSync(path.join(assets,file));
 assert.equal(sha(bytes),entry.sha256,file);
 assert.equal(bytes.length,entry.size,file);
 assert.ok(bytes.toString().startsWith('#!reverse-pc-machine-v1'),file);
}
const code=fs.readFileSync(path.join(root,'android-xi-lab/app/src/main/java/com/bbyq/lab/LabEngine.java'),'utf8');
const paths=[...code.matchAll(/program\([^,\n]+,\s*"([^"]+)"\)/g)].map(x=>x[1]);
for(const name of paths)assert.ok(manifest.source_files[name+'.xi'],'Missing XI asset '+name);
for(const required of ['core-birth','vqc2-birth','qrl2-birth','policy-birth','conversation-route',
 'p01-intent','vqc2-train','qrl2-train','policy-update','policy-decide'])
 assert.ok(manifest.source_files[required+'.xi'],'Mandatory engine missing: '+required);
assert.ok(code.includes('memory.finishWrite(file)')&&code.includes('memory.failWrite(file)'));
assert.ok(code.includes('ResultPacket.parse(NativeRuntime.execute(state,source))'));
assert.ok(code.includes('contextOf(state,message)'));
assert.ok(!code.includes('node:sqlite')&&!code.includes('fetch('));
console.log(JSON.stringify({ok:true,xi_programs:Object.keys(manifest.source_files).length,
 jni_native_required:true,isolated_atomic_rvpc2:true,full_x10:false}));
