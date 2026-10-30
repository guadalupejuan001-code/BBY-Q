// File integrity and native-role transport. Language interpretation stays in XI.
import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import {chat as framedChat} from './transport.mjs';
export {snapshot,speech} from './transport.mjs';
const sha=b=>crypto.createHash('sha256').update(b).digest('hex');
export function chat(runtime,base,input,output,message,options={}) {
  try {
    const m=JSON.parse(fs.readFileSync(path.join(base,'build.json')));
    if(m.version!=='X09-All-Training-1'||!m.extensions?.dictionary||!m.extensions?.campaign)throw Error('Se requiere una entrega X09 completa.');
    if(m.runtime_sha256&&sha(fs.readFileSync(runtime))!==m.runtime_sha256)throw Error('El ejecutor no coincide con la entrega X09.');
    return framedChat(runtime,base,input,output,message,options);
  } catch(error) {
    return {ok:false,committed:false,error:{code:'E_X09_BUILD',message:error.message,phase:'preflight'},output:null};
  }
}
