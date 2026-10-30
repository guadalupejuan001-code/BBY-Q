import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import assert from 'node:assert/strict';
import {test} from 'node:test';
import {prepare} from '../prepare.mjs';

function fixture(t){const dir=fs.mkdtempSync(path.join(os.tmpdir(),'bbyq-x09-prepare-'));t.after(()=>fs.rmSync(dir,{recursive:true,force:true}));return dir;}
test('an invalid recovered archive leaves no incomplete build',t=>{
 const dir=fixture(t),zip=path.join(dir,'invalid.zip'),output=path.join(dir,'output');fs.writeFileSync(zip,'invalid');
 assert.throws(()=>prepare(output,{archive:zip}),/archive integrity mismatch/);
 assert.equal(fs.existsSync(output),false);assert.equal(fs.readdirSync(dir).some(n=>n.startsWith('.x09-release-')),false);
});
test('a checkout without local data gives an explicit preparation instruction',t=>{
 const dir=fixture(t),release=path.join(dir,'release'),output=path.join(dir,'output');fs.mkdirSync(release);
 fs.writeFileSync(path.join(release,'manifest.json'),JSON.stringify({format:'BBYQ-X09-Repository-Release-1',version:'X09-All-Training-1'}));
 assert.throws(()=>prepare(output,{release}),/Local X09 data required.*--archive/);
 assert.equal(fs.existsSync(output),false);
});
test('preparation preserves an existing directory',t=>{
 const dir=fixture(t),output=path.join(dir,'output');fs.mkdirSync(output);fs.writeFileSync(path.join(output,'keep.txt'),'keep');
 assert.throws(()=>prepare(output,{archive:path.join(dir,'missing.zip')}),/existing builds and sessions are preserved/);
 assert.equal(fs.readFileSync(path.join(output,'keep.txt'),'utf8'),'keep');
});
