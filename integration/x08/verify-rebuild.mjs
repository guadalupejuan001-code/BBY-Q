import fs from 'node:fs';
import path from 'node:path';
import assert from 'node:assert/strict';
import {sha} from './prepare.mjs';
const [reference,rebuilt]=process.argv.slice(2);
if(!rebuilt)throw Error('Usage: verify-rebuild.mjs REFERENCE_NATIVE REBUILT_NATIVE');
const expected=JSON.parse(fs.readFileSync(path.join(reference,'build.json')));
for(const [file,key]of [['model.rvp','model_sha256'],['code.rxe','code_sha256'],['front.rxe','front_sha256']])assert.equal(sha(fs.readFileSync(path.join(rebuilt,file))),expected[key],file+' reconstruction differs');
console.log(JSON.stringify({ok:true,exact_model:true,exact_code:true,exact_front:true}));
