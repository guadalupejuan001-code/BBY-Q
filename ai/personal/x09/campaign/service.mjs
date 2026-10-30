import fs from 'node:fs';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {spawnSync} from 'node:child_process';
import {SCRATCH,SCRATCH_BYTES,HANDLED,PROOF,F} from './schema.mjs';
import {readState,byte,sha256} from './state.mjs';
export function service(runtime,assetDir,liveState){
 const manifest=JSON.parse(fs.readFileSync(path.join(assetDir,'campaign-build.json'))),role=path.join(assetDir,'campaign-role.rxe');
 if(manifest.format!==1||sha256(fs.readFileSync(role))!==manifest.roles?.['campaign-role.rxe'])throw Error('Campaign query role differs from its bound build');
 const before=readState(liveState),job=fs.mkdtempSync(path.join(path.dirname(path.resolve(liveState)),'.x09-campaign-')),candidate=path.join(job,'candidate.rvp');
 try{
  const result=spawnSync(runtime,['run',role,liveState,candidate],{encoding:'utf8',timeout:30000,maxBuffer:8*1024*1024});
  if(result.status!==0)throw Error('Campaign XI role refused: '+(result.stderr||result.error?.message));
  const after=readState(candidate);
  if(byte(after,HANDLED)===0)return{handled:false};
  if(byte(after,HANDLED)!==1||byte(after,F+2n)!==0||byte(after,F+3n)!==1)throw Error('Campaign role returned an invalid text result');
  for(let i=0;i<SCRATCH_BYTES;i++)if(byte(after,SCRATCH+BigInt(i)))throw Error('Campaign XI scratch was not erased');
  // Querying is read-only for all learned data, source archive and old state.
  // Only the five result controls and the shared text receipt may differ.
  const allowed=a=>(a>=HANDLED&&a<=PROOF)||a===F+2n||a===F+3n;
  for(const[a,v]of before.cells)if(!allowed(a)&&byte(after,a)!==v)throw Error('Campaign query changed learned or foreign state');
  for(const[a,v]of after.cells)if(!allowed(a)&&byte(before,a)!==v)throw Error('Campaign query wrote learned or foreign state');
  if(sha256(fs.readFileSync(liveState))!==before.sha256)throw Error('Campaign state changed concurrently');
  fs.renameSync(candidate,liveState);
  return{handled:true,jsonl:result.stdout};
 }finally{fs.rmSync(job,{recursive:true,force:true});}
}
if(process.argv[1]&&path.resolve(process.argv[1])===fileURLToPath(import.meta.url)){const[runtime,assetDir,state]=process.argv.slice(2);if(!state)throw Error('Usage: service.mjs RUNTIME ASSET_DIR LIVE_STATE.rvp');console.log(JSON.stringify(service(runtime,assetDir,state)));}
