// Filesystem integrity and typed native protocol only; no live language processing.
import fs from 'node:fs';import path from 'node:path';import crypto from 'node:crypto';import {spawnSync} from 'node:child_process';
import {chat as textChat} from './transport.mjs';import {snapshot} from '../x05/io.mjs';
export {snapshot};export {speech} from './transport.mjs';
const hash=b=>crypto.createHash('sha256').update(b).digest('hex');
export function chat(runtime,base,input,output,message,options={}){
 try{const manifest=JSON.parse(fs.readFileSync(path.join(base,'build.json')));for(const [name,key]of [['front.rxe','front_sha256'],['code.rxe','code_sha256']])if(hash(fs.readFileSync(path.join(base,name)))!==manifest[key])throw Error('El motor no coincide con la versión comprobada: '+name);return textChat(runtime,base,input,output,message,options);}catch(e){return {ok:false,committed:false,error:{code:'E_X08_SCHEMA',message:e.message,phase:'preflight'},output:null};}
}
