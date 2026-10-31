import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import zlib from 'node:zlib';
import crypto from 'node:crypto';
import {CAPSULE_SHA,LEARNED_SHA,E034_VERSION,learnedSeed,MAX_E034_TEXT} from '../../../ai/personal/p02/relational.mjs';

test('E034 checkpoint is exactly the audited learned model',()=>{
 const seed=learnedSeed();
 assert.equal(seed.raw.subarray(0,5).toString(),'RVPC2');
 assert.ok(seed.raw.length>800000);
 assert.equal(LEARNED_SHA,'876d3f2a82698e9582f17043028d9a75b454e4b5ebaf7cc5949b65a5bac58a10');
 assert.equal(CAPSULE_SHA,'a0edbe6122beb5ab57d0e2dbd60c26524bc946737806eb71f2ed133fde068a28');
 assert.equal(E034_VERSION,'E034-Relational-Composition-1-dev');
 assert.equal(MAX_E034_TEXT,240);
 const bundled=fs.readFileSync(new URL('../../../ai/releases/e034/composed.rxe.gz.b64',import.meta.url),'utf8').trim();
 const packed=Buffer.from(bundled,'base64'),binary=zlib.gunzipSync(packed,{maxOutputLength:3*1024*1024});
 assert.equal(packed.toString('base64'),bundled);
 assert.equal(crypto.createHash('sha256').update(binary).digest('hex'),CAPSULE_SHA);
 assert.equal(binary.length,1346841);
});
test('X10 retains old runtime and only dispatches explicitly requested E034',()=>{
 const session=fs.readFileSync(new URL('../../../ai/personal/x10/session.mjs',import.meta.url),'utf8');
 const cli=fs.readFileSync(new URL('../../../bbyq.mjs',import.meta.url),'utf8');
 assert.match(session,/if\(options\.module==='e034'\)/);
 assert.match(session,/relationalTurn\(db,/);
 assert.match(session,/options\.learn===true/);
 assert.match(session,/moduleTag=options\.module==='e034'/);
 assert.match(session,/if\(route\.mode!==1\)/);
 assert.match(session,/synchronizeLegacy\(db,runtime,input,job,readOnly\)/);
 assert.match(cli,/install-e034/);
 assert.match(cli,/--module=e034/);
 assert.match(cli,/--learn/);
});
test('Legacy modules and source releases are not replaced',()=>{
 for(const path of ['e027','e028','e029','e030','e031','e032','e033','e034'])
  assert.ok(fs.existsSync(new URL('../../../ai/releases/'+path+'/',import.meta.url)));
 const bridge=fs.readFileSync(new URL('../../../ai/personal/p02/relational.mjs',import.meta.url),'utf8');
 assert.match(bridge,/projectReadOnly/);
 assert.match(bridge,/E034-isolated-XI/);
 assert.match(bridge,/CREATE TABLE IF NOT EXISTS relational_state/);
 assert.match(bridge,/INSERT OR IGNORE INTO relational_state/);
 assert.match(bridge,/app-turn/);
 assert.match(bridge,/CAPSULE_SHA/);
});
