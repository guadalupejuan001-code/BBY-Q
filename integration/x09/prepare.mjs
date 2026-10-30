// Restore verified release bytes offline. All request interpretation remains in XI.
import fs from 'node:fs';
import path from 'node:path';
import zlib from 'node:zlib';
import crypto from 'node:crypto';
import {execFileSync} from 'node:child_process';
import {fileURLToPath} from 'node:url';

const here=path.dirname(fileURLToPath(import.meta.url));
export const RECOVERED_ARCHIVE_SHA256='1bf1b1abbd39a6e268c451d27fd23a6c051a3a0e0801d27acae5914d69398ebe';
export const sha=bytes=>crypto.createHash('sha256').update(bytes).digest('hex');
export function verifyRelease(release=path.join(here,'release'),{archive}={}){
 const manifest=JSON.parse(fs.readFileSync(path.join(release,'manifest.json')));
 if(manifest.format!=='BBYQ-X09-Repository-Release-1'||manifest.version!=='X09-All-Training-1')throw Error('Unsupported X09 release');
 if(archive){
  if(sha(fs.readFileSync(archive))!==RECOVERED_ARCHIVE_SHA256)throw Error('Recovered X09 archive integrity mismatch');
  return manifest;
 }
 if(!fs.existsSync(path.join(release,'native.tar.gz'))||!fs.existsSync(path.join(release,'reverse_pc.gz')))throw Error('Local X09 data required. Use: node bbyq.mjs prepare --archive /path/BBY-Q-X09-Entrenamientos-Integrados.zip');
 for(const [key,name]of [['archive','native.tar.gz'],['runtime','reverse_pc.gz']]){
  const item=manifest[key];
  if(item?.file!==name)throw Error('Unexpected release filename');
  const bytes=fs.readFileSync(path.join(release,name));
  if(bytes.length!==item.bytes||sha(bytes)!==item.sha256)throw Error('Release integrity mismatch: '+name);
 }
 const names=execFileSync('tar',['-tzf',path.join(release,'native.tar.gz')],{encoding:'utf8',maxBuffer:1024*1024}).trim().split('\n');
 for(const name of names){
  if(name==='native/'||name==='native')continue;
  const segments=name.replace(/\/$/,'').split('/');
  if(segments.shift()!=='native'||segments.some(s=>!/^[a-zA-Z0-9][a-zA-Z0-9.-]*$/.test(s)))throw Error('Unexpected release path');
  if(!name.endsWith('/')&&!Object.hasOwn(manifest.archive.files,segments.join('/')))throw Error('Unlisted release asset');
 }
 return manifest;
}
export function prepare(destination,{release=path.join(here,'release'),archive}={}){
 destination=path.resolve(destination);release=path.resolve(release);
 if(archive)archive=path.resolve(archive);
 if(fs.existsSync(destination))throw Error('Choose a new destination; existing builds and sessions are preserved');
 const manifest=verifyRelease(release,{archive}),parent=path.dirname(destination);
 fs.mkdirSync(parent,{recursive:true});
 const staging=fs.mkdtempSync(path.join(parent,'.x09-release-'));
 try{
  if(archive){
   execFileSync('unzip',['-q',archive,'BBY-Q-X09/native/*','BBY-Q-X09/runtime/reverse_pc','BBY-Q-X09/training-sources/alternate-e009.rvp','-d',staging]);
   const recovered=path.join(staging,'BBY-Q-X09');
   for(const name of ['native','runtime','training-sources'])fs.renameSync(path.join(recovered,name),path.join(staging,name));
   fs.rmdirSync(recovered);
  }else execFileSync('tar',['-xzf',path.join(release,'native.tar.gz'),'-C',staging]);
  const native=path.join(staging,'native'),seen=new Set();
  function verify(dir,relative=''){
   for(const item of fs.readdirSync(dir,{withFileTypes:true})){
    const key=relative+item.name,file=path.join(dir,item.name);
    if(item.isDirectory())verify(file,key+'/');
    else if(item.isFile()){
     if(key==='model.rvp'&&archive){if(sha(fs.readFileSync(file))!==manifest.model_sha256)throw Error('Recovered model digest mismatch');continue;}
     const expected=manifest.archive.files[key],bytes=fs.readFileSync(file);
     if(!expected||bytes.length!==expected.bytes||sha(bytes)!==expected.sha256)throw Error('Native asset integrity mismatch: '+key);
     seen.add(key);
    }else throw Error('Native release contains a nonregular asset');
   }
  }
  verify(native);
  if(seen.size!==Object.keys(manifest.archive.files).length)throw Error('Native release is incomplete');
  const build=JSON.parse(fs.readFileSync(path.join(native,'build.json')));
  const model=zlib.gunzipSync(fs.readFileSync(path.join(native,'model.rvp.gz')),{maxOutputLength:64*1024*1024});
  if(sha(model)!==manifest.model_sha256||build.model_sha256!==manifest.model_sha256)throw Error('Model digest mismatch');
  if(!archive)fs.writeFileSync(path.join(native,'model.rvp'),model,{flag:'wx',mode:0o600});
  const runtime=archive?fs.readFileSync(path.join(staging,'runtime/reverse_pc')):zlib.gunzipSync(fs.readFileSync(path.join(release,'reverse_pc.gz')),{maxOutputLength:16*1024*1024});
  if(sha(runtime)!==manifest.runtime.unpacked_sha256||sha(runtime)!==build.runtime_sha256)throw Error('Runtime digest mismatch');
  if(archive){
   const alternate=fs.readFileSync(path.join(staging,'training-sources/alternate-e009.rvp'));
   if(sha(alternate)!==manifest.source_campaign_sha256)throw Error('Recovered campaign digest mismatch');
  }else{
   fs.mkdirSync(path.join(staging,'runtime'));
   fs.writeFileSync(path.join(staging,'runtime','reverse_pc'),runtime,{flag:'wx',mode:0o755});
  }
  fs.chmodSync(path.join(staging,'runtime','reverse_pc'),0o755);
  if(fs.existsSync(destination))throw Error('Choose a new destination');
  fs.renameSync(staging,destination);
  return {ok:true,version:manifest.version,directory:destination,native:path.join(destination,'native'),runtime:path.join(destination,'runtime','reverse_pc'),model_sha256:manifest.model_sha256,dictionary_entries:manifest.dictionary_entries};
 }finally{if(fs.existsSync(staging))fs.rmSync(staging,{recursive:true});}
}
if(process.argv[1]&&path.resolve(process.argv[1])===fileURLToPath(import.meta.url)){
 if(process.argv.length<3||process.argv.length>4)throw Error('Usage: node integration/x09/prepare.mjs NEW_BUILD_DIRECTORY [RECOVERED_X09.zip]');
 console.log(JSON.stringify(prepare(process.argv[2],{archive:process.argv[3]})));
}
