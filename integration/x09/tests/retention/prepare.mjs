import fs from 'node:fs';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {sha256,gitBlobSha,decodedBytes} from './state.mjs';

const here=path.dirname(fileURLToPath(import.meta.url)),repo=path.resolve(here,'../../../..');
export function prepareHistory(destination,{historicalDirectory=path.join(here,'fixtures/historical-library')}={}){
 destination=path.resolve(destination);
 historicalDirectory=path.resolve(historicalDirectory);
 if(fs.existsSync(destination))throw Error('Choose a new history directory');
 const manifest=JSON.parse(fs.readFileSync(path.join(here,'historical-states.json')));
 const parent=path.dirname(destination);fs.mkdirSync(parent,{recursive:true});
 const stage=fs.mkdtempSync(path.join(parent,'.x09-history-'));
 try{
  fs.mkdirSync(path.join(stage,'checkpoints'),{recursive:true});
  for(const name of ['audit_retention.mjs','source_metadata.json'])fs.copyFileSync(path.join(here,'fixtures/checkpoints',name),path.join(stage,'checkpoints',name));
  for(const item of manifest.states){
   const relative=item.path,target=path.resolve(stage,relative);
   if(path.relative(stage,target).startsWith('..'))throw Error('Historical path escapes its fixture');
   let bytes;
   if(item.kind==='versioned_checkpoint'){
    const source=path.resolve(repo,relative.replace(/^checkpoints\//,''));
    if(path.relative(repo,source).startsWith('..'))throw Error('Checkpoint path escapes the repository');
    bytes=fs.readFileSync(source);
    if(gitBlobSha(bytes)!==item.git_blob_sha)throw Error('Repository checkpoint changed: '+relative);
    bytes=Buffer.concat([bytes,Buffer.alloc(item.transport_extra_final_lf||0,10)]);
   }else bytes=fs.readFileSync(path.join(historicalDirectory,path.basename(relative)));
   if(sha256(bytes)!==item.raw_sha256)throw Error('Historical source changed: '+relative);
   fs.mkdirSync(path.dirname(target),{recursive:true});fs.writeFileSync(target,bytes,{flag:'wx'});
   if(sha256(decodedBytes(target))!==item.state_sha256)throw Error('Historical state changed: '+relative);
  }
  if(sha256(fs.readFileSync(path.join(stage,'checkpoints/audit_retention.mjs')))!==manifest.audit_script_sha256)throw Error('Historical audit source changed');
  fs.renameSync(stage,destination);
  return {ok:true,directory:destination,historical_payloads_verified:manifest.states.length};
 }finally{if(fs.existsSync(stage))fs.rmSync(stage,{recursive:true});}
}
if(process.argv[1]&&path.resolve(process.argv[1])===fileURLToPath(import.meta.url)){
 if(process.argv.length<3||process.argv.length>4)throw Error('Usage: prepare.mjs NEW_HISTORY_DIRECTORY [HISTORICAL_STATE_DIRECTORY]');
 console.log(JSON.stringify(prepareHistory(process.argv[2],{historicalDirectory:process.argv[3]})));
}
