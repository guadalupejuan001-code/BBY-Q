// Export only the verified educational seed and its native runtime, never a session.
import fs from 'node:fs';
import path from 'node:path';
import zlib from 'node:zlib';
import crypto from 'node:crypto';
import {execFileSync} from 'node:child_process';
import {fileURLToPath} from 'node:url';

const here=path.dirname(fileURLToPath(import.meta.url));
const sha=b=>crypto.createHash('sha256').update(b).digest('hex');
const canonical='71ba9704e279c08160a8af882a8628b77e938a30befa450e95a522315a39f995';
const [nativeArg,runtimeArg]=process.argv.slice(2);
if(!runtimeArg)throw Error('Usage: package-repository.mjs VERIFIED_X09_NATIVE RUNTIME');
const native=path.resolve(nativeArg),runtime=path.resolve(runtimeArg);
const build=JSON.parse(fs.readFileSync(path.join(native,'build.json')));
const model=zlib.gunzipSync(fs.readFileSync(path.join(native,'model.rvp.gz')));
if(build.version!=='X09-All-Training-1'||build.model_sha256!==canonical||sha(model)!==canonical)throw Error('Only the canonical X09 seed can be exported');
const runtimeBytes=fs.readFileSync(runtime);
if(sha(runtimeBytes)!==build.runtime_sha256)throw Error('Runtime does not match the verified seed');
const output=path.join(here,'release');
if(fs.existsSync(output))throw Error('Choose a fresh release directory');
const temporary=fs.mkdtempSync(path.join(here,'.package-'));
try{
 const files={};
 function copy(dir,relative=''){
  fs.mkdirSync(path.join(temporary,'native',relative),{recursive:true});
  for(const name of fs.readdirSync(dir).sort()){
   if(!/^[a-zA-Z0-9][a-zA-Z0-9.-]*$/.test(name))throw Error('Unexpected native asset name');
   const from=path.join(dir,name),entry=fs.lstatSync(from),key=relative+name;
   if(entry.isDirectory())copy(from,key+'/');
   else if(entry.isFile()){
    if(key==='model.rvp')continue;
    const bytes=fs.readFileSync(from);files[key]={bytes:bytes.length,sha256:sha(bytes)};
    fs.writeFileSync(path.join(temporary,'native',key),bytes,{mode:0o644});
   }else throw Error('Native release inputs must be regular files');
  }
 }
 copy(native);fs.mkdirSync(output);
 const archive=path.join(output,'native.tar.gz');
 execFileSync('tar',['--sort=name','--mtime=@0','--owner=0','--group=0','--numeric-owner','-czf',archive,'-C',temporary,'native']);
 const packedRuntime=zlib.gzipSync(runtimeBytes,{level:9});
 fs.writeFileSync(path.join(output,'reverse_pc.gz'),packedRuntime);
 const archiveBytes=fs.readFileSync(archive);
 const manifest={format:'BBYQ-X09-Repository-Release-1',version:build.version,platform:'Linux x86-64',node:'24+',model_sha256:canonical,parent_model_sha256:build.parent_model_sha256,
  archive:{file:'native.tar.gz',bytes:archiveBytes.length,sha256:sha(archiveBytes),files},
  runtime:{file:'reverse_pc.gz',bytes:packedRuntime.length,sha256:sha(packedRuntime),unpacked_sha256:sha(runtimeBytes)},
  dictionary_entries:236256,source_dictionary_archive_sha256:build.integration.dictionary_original_sha256,
  source_campaign_sha256:build.integration.campaign_source_sha256,scope:'Canonical training fixture and native XI assets; no personal session; Android not validated'};
 fs.writeFileSync(path.join(output,'manifest.json'),JSON.stringify(manifest,null,2)+'\n');
 console.log(JSON.stringify({ok:true,archive_bytes:archiveBytes.length,files:Object.keys(files).length,model_sha256:canonical}));
}finally{fs.rmSync(temporary,{recursive:true,force:true});}
