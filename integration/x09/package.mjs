// Assemble a runnable native release. No live user session is exported.
import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import {fileURLToPath} from 'node:url';
const here=path.dirname(fileURLToPath(import.meta.url)),sourceRoot=path.resolve(here,'../..');
const sha=b=>crypto.createHash('sha256').update(b).digest('hex');
function copy(from,to,{jsonOnly=false}={}) {
  const item=fs.lstatSync(from);
  if(item.isSymbolicLink())throw Error('Release inputs must not contain symbolic links.');
  if(item.isDirectory()) {
    fs.mkdirSync(to,{recursive:true});
    for(const name of fs.readdirSync(from).sort())copy(path.join(from,name),path.join(to,name),{jsonOnly});
  } else if(item.isFile()&&(!jsonOnly||from.endsWith('.json'))) {
    fs.mkdirSync(path.dirname(to),{recursive:true});fs.copyFileSync(from,to);fs.chmodSync(to,item.mode&0o777);
  } else if(!item.isFile())throw Error('Unsupported release input.');
}
export function packageRelease({native,runtime,evidence,outDir,patch,commit,alternate}) {
  [native,runtime,evidence,outDir]=[native,runtime,evidence,outDir].map(p=>path.resolve(p));
  if(fs.existsSync(outDir))throw Error('Choose a fresh release directory.');
  const build=JSON.parse(fs.readFileSync(path.join(native,'build.json')));
  const model=fs.readFileSync(path.join(native,'model.rvp'));
  if(build.version!=='X09-All-Training-1'||sha(model)!==build.model_sha256)throw Error('Unverified X09 training seed.');
  // Canonical releases have no personal-memory records or pending text request.
  const prefix=Number(model.readBigUInt64LE(5));
  for(const line of model.subarray(29+prefix).toString().split('\n'))if(line.startsWith('O ')) {
    const [,address,value]=line.split(' '),p=BigInt(address);
    if(Number(value)&&p>=8900000000000000000n&&p<8900000000000200000n)throw Error('Refuse export of personal memory.');
    if(Number(value)&&p===9100000000000200002n)throw Error('Refuse export of a pending request.');
  }
  fs.mkdirSync(path.dirname(outDir),{recursive:true});
  const staging=fs.mkdtempSync(path.join(path.dirname(outDir),'.x09-release-'));
  try {
    copy(native,path.join(staging,'native'));copy(runtime,path.join(staging,'runtime','reverse_pc'));
    copy(path.join(sourceRoot,'ai/personal/x09'),path.join(staging,'source/ai/personal/x09'));
    for(const relative of ['ai/personal/x05/io.mjs','ai/personal/x05/schema.mjs','ai/personal/x06/schema.mjs','ai/personal/x03/io.mjs'])copy(path.join(sourceRoot,relative),path.join(staging,'source',relative));
    copy(path.join(here,'launcher.mjs'),path.join(staging,'bbyq.mjs'));
    copy(evidence,path.join(staging,'evidence'),{jsonOnly:true});
    if(patch)copy(path.resolve(patch),path.join(staging,'X09.patch'));
    if(commit)copy(path.resolve(commit),path.join(staging,'commit.json'));
    if(alternate)copy(path.resolve(alternate),path.join(staging,'training-sources','alternate-e009.rvp'));
    const files={};
    function inventory(dir,prefix='') {for(const name of fs.readdirSync(dir).sort()){const file=path.join(dir,name),relative=prefix+name;if(fs.statSync(file).isDirectory())inventory(file,relative+'/');else{const bytes=fs.readFileSync(file);files[relative]={bytes:bytes.length,sha256:sha(bytes)};}}}
    inventory(staging);
    const manifest={format:1,version:build.version,platform:'Linux x86-64',node:'24+',runtime_sha256:build.runtime_sha256,model_sha256:build.model_sha256,parent_model_sha256:build.parent_model_sha256,dictionary_entries:236256,one_shared_RVPC2_state:true,source_commit:commit?JSON.parse(fs.readFileSync(commit)).commit:null,files};
    fs.writeFileSync(path.join(staging,'release.json'),JSON.stringify(manifest,null,2)+'\n');
    fs.renameSync(staging,outDir);
    return {ok:true,directory:outDir,files:Object.keys(files).length,version:build.version,model_sha256:build.model_sha256};
  } finally {if(fs.existsSync(staging))fs.rmSync(staging,{recursive:true});}
}
if(process.argv[1]&&path.resolve(process.argv[1])===fileURLToPath(import.meta.url)) {
  const [native,runtime,evidence,outDir,patch,commit,alternate]=process.argv.slice(2);
  if(!outDir)throw Error('Usage: package.mjs X09_NATIVE RUNTIME JSON_EVIDENCE NEW_OUTPUT [PATCH COMMIT_JSON ALTERNATE.rvp]');
  console.log(JSON.stringify(packageRelease({native,runtime,evidence,outDir,patch,commit,alternate})));
}
