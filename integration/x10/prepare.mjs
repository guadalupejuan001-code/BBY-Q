// Build a capacity extension around the unchanged, verified X09 training seed.
import fs from 'node:fs';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {prepare as prepareX09} from '../x09/prepare.mjs';
import {validatorSource,routerSource,recordSource,streamSource} from '../../ai/personal/x10/native.mjs';
import {LIMITS,VERSION} from '../../ai/personal/x10/schema.mjs';
import {run,sha} from '../../ai/personal/x10/pages.mjs';

export function prepare(destination,{archive}={}){
 destination=path.resolve(destination);if(fs.existsSync(destination))throw Error('Choose a new build directory');
 const parent=path.dirname(destination);fs.mkdirSync(parent,{recursive:true});const staging=fs.mkdtempSync(path.join(parent,'.x10-build-'));
 try{
  const original=prepareX09(path.join(staging,'release'),{archive}),release=original.directory;
  const capacity=path.join(release,'capacity');fs.mkdirSync(capacity);
  const roles={};
  for(const[name,source]of [['validate',validatorSource()],['route',routerSource()],['record',recordSource()],['stream',streamSource()]]){
   const text=path.join(capacity,name+'.xi'),binary=path.join(capacity,name+'.rxe');fs.writeFileSync(text,source);run(original.runtime,['compile',text,binary,'BBY Q X10 '+name]);roles[name+'.xi']=sha(fs.readFileSync(text));roles[name+'.rxe']=sha(fs.readFileSync(binary));
  }
  const manifest={version:VERSION,parent:'X09-All-Training-1',runtime_sha256:sha(fs.readFileSync(original.runtime)),seed_sha256:original.model_sha256,limits:LIMITS,roles,storage:'SQLite opaque 640-byte Ether record pages; XI selects and changes records',long_text_operations:['exact echo','extractive summary'],legacy_input_bytes:16384,original_training_preserved:true,android_validated:false};
  fs.writeFileSync(path.join(capacity,'build.json'),JSON.stringify(manifest,null,2)+'\n');
  fs.renameSync(release,destination);return {ok:true,version:VERSION,directory:destination,limits:LIMITS,seed_sha256:manifest.seed_sha256,original_training_preserved:true};
 }finally{fs.rmSync(staging,{recursive:true,force:true});}
}
if(process.argv[1]&&path.resolve(process.argv[1])===fileURLToPath(import.meta.url))console.log(JSON.stringify(prepare(process.argv[2],{archive:process.argv[3]})));
