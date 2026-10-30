// Offline asset assembly. Queries, dictionary selection and campaign reasoning are XI.
import fs from 'node:fs';
import path from 'node:path';
import zlib from 'node:zlib';
import crypto from 'node:crypto';
import {execFileSync} from 'node:child_process';
import {fileURLToPath} from 'node:url';
import {buildDictionary} from './dictionary/build.mjs';
import {buildCampaign} from './campaign/build.mjs';
import {migrateState} from './migrate.mjs';

const sha=b=>crypto.createHash('sha256').update(b).digest('hex');
const EXPECTED_X08='6f205595fe2f0032f76991205101f6c9f15d04ef1d10af77d7d87e6d12b3aef9';

export async function build(runtime,{base,dictionaryArchive,alternateState,outDir,dictionaryBuild,campaignBuild}) {
  [runtime,base,dictionaryArchive,alternateState,outDir]=[runtime,base,dictionaryArchive,alternateState,outDir].map(p=>path.resolve(p));
  if(fs.existsSync(outDir))throw Error('Choose a new build directory.');
  const old=JSON.parse(fs.readFileSync(path.join(base,'build.json')));
  if(old.version!=='X08-Training-Language-1'||old.model_sha256!==EXPECTED_X08)throw Error('Pinned canonical X08 build required.');
  const seed=zlib.gunzipSync(fs.readFileSync(path.join(base,'model.rvp.gz')));
  if(sha(seed)!==EXPECTED_X08)throw Error('The X08 training seed differs from the verified release.');
  for(const[name,expected]of [['code.rxe',old.code_sha256],['front.rxe',old.front_sha256],...Object.entries(old.roles_sha256)]) {
    if(sha(fs.readFileSync(path.join(base,name)))!==expected)throw Error('X08 asset differs: '+name);
  }
  fs.mkdirSync(path.dirname(outDir),{recursive:true});
  const stage=fs.mkdtempSync(path.join(path.dirname(outDir),'.x09-build-'));
  try {
    for(const item of fs.readdirSync(base,{withFileTypes:true})) {
      if(!item.isFile())throw Error('Canonical X08 native directory must contain only regular files.');
      if(item.name!=='model.rvp')fs.copyFileSync(path.join(base,item.name),path.join(stage,item.name));
    }
    if(dictionaryBuild)fs.cpSync(path.resolve(dictionaryBuild),path.join(stage,'dictionary'),{recursive:true,errorOnExist:true});
    else await buildDictionary(runtime,{archive:dictionaryArchive,outDir:path.join(stage,'dictionary')});
    if(campaignBuild)fs.cpSync(path.resolve(campaignBuild),path.join(stage,'campaign'),{recursive:true,errorOnExist:true});
    else await buildCampaign(runtime,{alternateState,outDir:path.join(stage,'campaign')});
    const extensions={};
    for(const[name,manifest_file]of [['dictionary','build.json'],['campaign','campaign-build.json']]) {
      const bytes=fs.readFileSync(path.join(stage,name,manifest_file));
      extensions[name]={directory:name,manifest_file,manifest_sha256:sha(bytes)};
    }
    const manifest={...old,version:'X09-All-Training-1',parent:'X08-Training-Language-1',runtime_sha256:sha(fs.readFileSync(runtime)),parent_model_sha256:EXPECTED_X08,extensions};
    fs.writeFileSync(path.join(stage,'build.json'),JSON.stringify(manifest,null,2)+'\n');
    const original=path.join(stage,'.x08-seed.rvp');fs.writeFileSync(original,seed);
    const result=migrateState(runtime,stage,original,path.join(stage,'model.rvp'));
    fs.unlinkSync(original);
    const model=fs.readFileSync(path.join(stage,'model.rvp'));
    manifest.model_sha256=sha(model);manifest.model_bytes=model.length;
    manifest.integration={campaign_source_sha256:sha(fs.readFileSync(alternateState)),dictionary_original_sha256:sha(fs.readFileSync(dictionaryArchive)),previous_training_preserved:result.previous_training_preserved,changed_campaign_cells:result.changed_campaign_cells};
    fs.writeFileSync(path.join(stage,'model.rvp.gz'),zlib.gzipSync(model,{level:9}));
    // The existing document importer consumes XI source. Recover that source
    // from the exact preserved code, rather than requiring an external checkout.
    execFileSync(runtime,['disassemble',path.join(stage,'code.rxe'),path.join(stage,'conversation.xi')],{encoding:'utf8',timeout:60000,maxBuffer:1024*1024});
    manifest.conversation_source_sha256=sha(fs.readFileSync(path.join(stage,'conversation.xi')));
    fs.writeFileSync(path.join(stage,'build.json'),JSON.stringify(manifest,null,2)+'\n');
    fs.renameSync(stage,outDir);
    return {ok:true,directory:outDir,version:manifest.version,model_sha256:manifest.model_sha256,extensions,previous_training_preserved:true};
  } finally {if(fs.existsSync(stage))fs.rmSync(stage,{recursive:true});}
}

if(process.argv[1]&&path.resolve(process.argv[1])===fileURLToPath(import.meta.url)) {
  const[r,base,dictionaryArchive,alternateState,outDir]=process.argv.slice(2);
  if(!outDir)throw Error('Usage: build.mjs RUNTIME X08_NATIVE ORIGINAL_DICTIONARY.zip ALTERNATE_E009.rvp NEW_OUTPUT');
  console.log(JSON.stringify(await build(r,{base,dictionaryArchive,alternateState,outDir})));
}
