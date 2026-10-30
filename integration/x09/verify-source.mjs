// Independently compile all six XI extension roles and reconstruct the exact seed.
import fs from 'node:fs';
import path from 'node:path';
import assert from 'node:assert/strict';
import {execFileSync} from 'node:child_process';
import {fileURLToPath} from 'node:url';
import {routeSource,lookupSource,clearSource} from '../../ai/personal/x09/dictionary/native.mjs';
import {buildCampaign} from '../../ai/personal/x09/campaign/build.mjs';
import {migrateState} from '../../ai/personal/x09/migrate.mjs';
import {sha} from './prepare.mjs';

const here=path.dirname(fileURLToPath(import.meta.url));
const [runtimeArg,baseArg,oldArg,outArg]=process.argv.slice(2);
if(!outArg)throw Error('Usage: verify-source.mjs RUNTIME X09_NATIVE X08_STATE NEW_OUTPUT');
const [runtime,base,old,out]=[runtimeArg,baseArg,oldArg,outArg].map(p=>path.resolve(p));
if(fs.existsSync(out))throw Error('Choose a new source verification directory');
fs.mkdirSync(out,{recursive:true});
const dictionary=JSON.parse(fs.readFileSync(path.join(base,'dictionary/build.json')));
const original=fs.readFileSync(path.resolve(here,'../../ai/personal/x09/dictionary/original-lookup.xi'),'utf8');
assert.equal(sha(Buffer.from(original)),dictionary.original_lookup_source_sha256);
const roles={route:routeSource(),lookup:lookupSource(original),clear:clearSource()};
for(const [name,source]of Object.entries(roles)){
 const xi=path.join(out,name+'.xi'),rxe=path.join(out,name+'.rxe');fs.writeFileSync(xi,source);
 execFileSync(runtime,['compile',xi,rxe,'BBY Q X09 E031 dictionary '+name],{encoding:'utf8',timeout:30000});
 assert.equal(sha(fs.readFileSync(xi)),dictionary.files[name+'.xi'].sha256);
 assert.equal(sha(fs.readFileSync(rxe)),dictionary.files[name+'.rxe'].sha256);
}
const alternate=path.resolve(base,'../training-sources/alternate-e009.rvp');
const campaign=buildCampaign(runtime,{alternateState:alternate,outDir:path.join(out,'campaign')});
const expected=JSON.parse(fs.readFileSync(path.join(base,'campaign/campaign-build.json')));
assert.deepEqual(campaign.roles,expected.roles);assert.deepEqual(campaign.source_sha256,expected.source_sha256);
const migrated=migrateState(runtime,base,old,path.join(out,'model.rvp'));
const manifest=JSON.parse(fs.readFileSync(path.join(base,'build.json')));
assert.equal(migrated.state_sha256,manifest.model_sha256);
const result={ok:true,xi_roles_recompiled:6,exact_native_binaries:true,exact_model_rebuilt_from_x08:true,model_sha256:manifest.model_sha256,previous_training_preserved:migrated.previous_training_preserved};
fs.writeFileSync(path.join(out,'results.json'),JSON.stringify(result,null,2)+'\n');console.log(JSON.stringify(result));
