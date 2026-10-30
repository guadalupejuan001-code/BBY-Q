import fs from 'node:fs';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import assert from 'node:assert/strict';
import {test} from 'node:test';
import {decodedBytes,sha256,gitBlobSha} from './state.mjs';

const here=path.dirname(fileURLToPath(import.meta.url)),repo=path.resolve(here,'../../../..');
const manifest=JSON.parse(fs.readFileSync(path.join(here,'historical-states.json')));
for(const item of manifest.states.filter(s=>s.kind==='versioned_checkpoint')){
 test('original repository checkpoint: '+item.path,()=>{
  const file=path.join(repo,item.path.replace(/^checkpoints\//,''));
  assert.equal(gitBlobSha(fs.readFileSync(file)),item.git_blob_sha);
  assert.equal(sha256(decodedBytes(file)),item.state_sha256);
 });
}
