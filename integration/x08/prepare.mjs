// Release bytes and digests only. Interpretation and responses stay in XI.
import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import zlib from 'node:zlib';
import {execFileSync} from 'node:child_process';
import {fileURLToPath} from 'node:url';

const here=path.dirname(fileURLToPath(import.meta.url));
export const sha=bytes=>crypto.createHash('sha256').update(bytes).digest('hex');

export function verifyRelease(release=path.join(here,'release')) {
  const manifest=JSON.parse(fs.readFileSync(path.join(release,'manifest.json')));
  if(manifest.version!=='X08-Training-Language-1'||manifest.format!==1)throw Error('Unsupported X08 release');
  for(const kind of ['parent','native']) {
    const item=manifest.archives[kind];
    if(item.file!==kind+'.tar.gz'||sha(fs.readFileSync(path.join(release,item.file)))!==item.sha256)throw Error('Release digest mismatch: '+kind);
    const names=execFileSync('tar',['-tzf',path.join(release,item.file)],{encoding:'utf8'}).trim().split('\n');
    if(names.some(n=>!new RegExp('^'+kind+'/(?:[a-zA-Z0-9][a-zA-Z0-9.-]*)?$').test(n)))throw Error('Unexpected release path');
  }
  return manifest;
}

export function prepare(destination,release=path.join(here,'release')) {
  destination=path.resolve(destination);
  if(fs.existsSync(destination))throw Error('Choose a new destination; existing builds and sessions are preserved');
  const manifest=verifyRelease(release);
  fs.mkdirSync(path.dirname(destination),{recursive:true});
  const staging=fs.mkdtempSync(path.join(path.dirname(destination),'.x08-release-'));
  try {
    for(const kind of ['parent','native']) {
      execFileSync('tar',['-xzf',path.resolve(release,manifest.archives[kind].file),'-C',staging]);
      const root=path.join(staging,kind);
      for(const entry of fs.readdirSync(root,{withFileTypes:true})) {
        if(!entry.isFile())throw Error('Release contains a nonregular file');
        const expected=manifest.archives[kind].files[entry.name];
        if(!expected||sha(fs.readFileSync(path.join(root,entry.name)))!==expected)throw Error('Release file mismatch: '+entry.name);
      }
      for(const name of Object.keys(manifest.archives[kind].files))if(!fs.existsSync(path.join(root,name)))throw Error('Missing release file: '+name);
    }
    const native=path.join(staging,'native'),build=JSON.parse(fs.readFileSync(path.join(native,'build.json')));
    const model=zlib.gunzipSync(fs.readFileSync(path.join(native,'model.rvp.gz')));
    if(sha(model)!==build.model_sha256||build.model_sha256!==manifest.model_sha256)throw Error('Model digest mismatch');
    if(build.code_sha256!==manifest.code_sha256||build.front_sha256!==manifest.front_sha256)throw Error('Native role identity mismatch');
    fs.writeFileSync(path.join(native,'model.rvp'),model,{flag:'wx'});
    fs.writeFileSync(path.join(staging,'release.json'),JSON.stringify(manifest,null,2)+'\n');
    fs.renameSync(staging,destination);
    return {ok:true,version:manifest.version,directory:destination,native:path.join(destination,'native'),parent:path.join(destination,'parent'),model_sha256:manifest.model_sha256};
  } finally {
    if(fs.existsSync(staging))fs.rmSync(staging,{recursive:true});
  }
}

if(process.argv[1]&&path.resolve(process.argv[1])===fileURLToPath(import.meta.url)) {
  if(process.argv.length!==3)throw Error('Usage: node integration/x08/prepare.mjs NEW_BUILD_DIRECTORY');
  console.log(JSON.stringify(prepare(process.argv[2])));
}
