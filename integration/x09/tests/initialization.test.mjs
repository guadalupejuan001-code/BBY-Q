import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import crypto from 'node:crypto';
import zlib from 'node:zlib';
import assert from 'node:assert/strict';
import {test} from 'node:test';
import {initialize} from '../../../ai/personal/x09/session.mjs';

const sha=b=>crypto.createHash('sha256').update(b).digest('hex');
function fixture(t){
 const directory=fs.mkdtempSync(path.join(os.tmpdir(),'bbyq-x09-init-'));
 t.after(()=>fs.rmSync(directory,{recursive:true,force:true}));
 const base=path.join(directory,'base'),session=path.join(directory,'session');fs.mkdirSync(base);
 const bytes=Buffer.alloc(29);bytes.write('RVPC2');
 fs.writeFileSync(path.join(base,'model.rvp.gz'),zlib.gzipSync(bytes));
 fs.writeFileSync(path.join(base,'build.json'),JSON.stringify({model_sha256:sha(bytes)}));
 return {directory,base,session,bytes};
}
test('a damaged seed leaves no incomplete session and can be retried',t=>{
 const {directory,base,session,bytes}=fixture(t);
 fs.writeFileSync(path.join(base,'build.json'),JSON.stringify({model_sha256:'0'.repeat(64)}));
 assert.throws(()=>initialize(session,base),/digest mismatch/);
 assert.deepEqual(fs.readdirSync(directory),['base']);
 fs.writeFileSync(path.join(base,'build.json'),JSON.stringify({model_sha256:sha(bytes)}));
 assert.equal(initialize(session,base).ok,true);
 const head=JSON.parse(fs.readFileSync(path.join(session,'HEAD.json')));
 assert.equal(head.state_sha256,sha(bytes));
 assert.deepEqual(fs.readFileSync(path.join(session,'versions',head.directory,'state.rvp')),bytes);
});
test('a failed publication cleans staging and preserves the destination',t=>{
 const {directory,base,session}=fixture(t);
 const original=fs.renameSync;
 const mocked=t.mock.method(fs,'renameSync',(from,to)=>{if(to===session)throw Error('Injected publication failure');return original(from,to);});
 assert.throws(()=>initialize(session,base),/Injected publication failure/);
 assert.deepEqual(fs.readdirSync(directory),['base']);
 mocked.mock.restore();
 assert.equal(initialize(session,base).ok,true);
 const head=fs.readFileSync(path.join(session,'HEAD.json'));
 assert.throws(()=>initialize(session,base),/new session directory/);
 assert.deepEqual(fs.readFileSync(path.join(session,'HEAD.json')),head);
});
test('an invalid imported state is rejected before creating a session',t=>{
 const {directory,base,session}=fixture(t),bad=path.join(directory,'bad.rvp');
 fs.writeFileSync(bad,'not a state');
 assert.throws(()=>initialize(session,base,bad),/RVPC2/);
 assert.equal(fs.existsSync(session),false);
 assert.equal(fs.readdirSync(directory).some(n=>n.startsWith('.x09-init-')),false);
});
