// Build-time only: copy authored XI programs to Android assets.
// The APK NEVER fetches executable programs or models over the network.
import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import {fileURLToPath} from 'node:url';
import {intentSource} from '../../ai/personal/p01/intent.mjs';

const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'../..');
const dest=path.join(root,'android-xi-lab/app/src/main/assets/xi');
fs.mkdirSync(dest,{recursive:true});
const chosen=[
 'qml_qrl/core-birth',
 'qml_qrl/vqc2-birth',
 'qml_qrl/vqc2-feed-xor',
 'qml_qrl/vqc2-feed-xnor',
 'qml_qrl/vqc2-train',
 'qml_qrl/vqc2-eval',
 'qml_qrl/vqc2-infer',
 'qml_qrl/vqc2-status',
 'qml_qrl/qrl2-birth',
 'qml_qrl/qrl2-train',
 'qml_qrl/qrl2-act',
 'qml_qrl/conversation-route',
 'cognitive/policy-birth',
 'cognitive/policy-update',
 'cognitive/policy-decide'
];
const sha=bytes=>crypto.createHash('sha256').update(bytes).digest('hex'),files={};
for(const name of chosen){
 const file=path.join(root,'ai/xi',name+'.xi');
 if(!fs.existsSync(file))throw Error('Missing original XI source '+name);
 const data=fs.readFileSync(file);
 if(!data.toString().startsWith('#!reverse-pc-machine-v1\n'))throw Error('Not native XI '+name);
 const destination=path.join(dest,path.basename(name)+'.xi');
 if(fs.existsSync(destination)&&!fs.readFileSync(destination).equals(data))fs.unlinkSync(destination);
 fs.writeFileSync(destination,data);
 files[path.basename(destination)]={sha256:sha(data),size:data.length,source:'ai/xi/'+name+'.xi'};
}
const p01=Buffer.from(intentSource(),'utf8');
if(!p01.toString().startsWith('#!reverse-pc-machine-v1'))throw Error('P01 not a native XI source');
fs.writeFileSync(path.join(dest,'p01-intent.xi'),p01);
files['p01-intent.xi']={sha256:sha(p01),size:p01.length,source:'generated from ai/personal/p01/intent.mjs'};
const manifest={schema:1,platform:'Android',engines:'XI+REVERSE-PC',conversation:'laboratory-only',
 full_x10:false,training_history_imported:false,source_files:files,
 reverse_pc_commit:'a1b935ae0adf38615996bac92727e95289ad7cc1',
 mundo_x_commit:'e2778d962af22f6f1a0794058dd4685fc2573966'};
fs.writeFileSync(path.join(dest,'manifest.json'),JSON.stringify(manifest,null,2)+'\n');
console.log(JSON.stringify({ok:true,xi_programs:Object.keys(files).length,source_bytes:Object.values(files).reduce((n,f)=>n+f.size,0),manifest:path.relative(root,path.join(dest,'manifest.json'))}));
