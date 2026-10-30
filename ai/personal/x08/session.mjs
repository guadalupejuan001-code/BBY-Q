// Durable serialized session commits. The process lock protects the entire read/turn/commit.
import fs from 'node:fs';import path from 'node:path';import crypto from 'node:crypto';import zlib from 'node:zlib';import {spawnSync} from 'node:child_process';import {fileURLToPath} from 'node:url';
import {chat} from './io.mjs';import {importDocument} from '../x03/io.mjs';
const sha=b=>crypto.createHash('sha256').update(b).digest('hex'),self=fileURLToPath(import.meta.url);
function syncFile(p){const f=fs.openSync(p,'r');try{fs.fsyncSync(f);}finally{fs.closeSync(f);}}
function syncDirectory(p){const f=fs.openSync(p,'r');try{fs.fsyncSync(f);}finally{fs.closeSync(f);}}
function putJSON(p,v){fs.writeFileSync(p,JSON.stringify(v)+'\n',{flag:'wx',mode:0o600});syncFile(p);}
function head(root){return JSON.parse(fs.readFileSync(path.join(root,'HEAD.json')));}
export function initialize(root,base,initial){root=path.resolve(root);if(fs.existsSync(root))throw Error('Choose a new session directory');fs.mkdirSync(root,{recursive:true,mode:0o700});fs.mkdirSync(path.join(root,'versions'));const name=crypto.randomUUID(),dir=path.join(root,'versions',name);fs.mkdirSync(dir);const bytes=initial?fs.readFileSync(initial):zlib.gunzipSync(fs.readFileSync(path.join(base,'model.rvp.gz'))),m=JSON.parse(fs.readFileSync(path.join(base,'build.json')));if(!initial&&sha(bytes)!==m.model_sha256)throw Error('Model digest mismatch');fs.writeFileSync(path.join(dir,'state.rvp'),bytes,{flag:'wx',mode:0o600});syncFile(path.join(dir,'state.rvp'));putJSON(path.join(root,'HEAD.json'),{version:1,generation:0,directory:name,state_sha256:sha(bytes),requests:{}});syncDirectory(dir);syncDirectory(path.join(root,'versions'));syncDirectory(root);return {ok:true,generation:0,session:root};}
export function transact(runtime,base,root,requestId,message,options={}){
 if(typeof message==='string'&&!message.isWellFormed())return {ok:false,committed:false,error:{code:'E_UTF16',message:'El texto contiene un sustituto Unicode sin pareja.'}};
 if(!(typeof message==='string'||Buffer.isBuffer(message)||message instanceof Uint8Array))return {ok:false,committed:false,error:{code:'E_INPUT_TYPE',message:'Se requiere texto o bytes UTF-8.'}};
 root=path.resolve(root);if(!fs.existsSync(path.join(root,'HEAD.json')))return {ok:false,committed:false,error:{code:'E_SESSION',message:'Sesión no inicializada.'}};
 const raw=Buffer.isBuffer(message)?message:Buffer.from(message),request={requestId,body:raw.toString('base64'),operation:options.operation||'chat',title:options.title,expectedGeneration:options.expectedGeneration,fault:options.testFault};
 const p=spawnSync('flock',['-x','-w','60',path.join(root,'session.lock'),process.execPath,self,'--worker',path.resolve(runtime),path.resolve(base),root],{input:JSON.stringify(request),encoding:'utf8',timeout:180000,maxBuffer:16*1024*1024});
 if(p.status!==0)return {ok:false,committed:null,status:'unknown',retryable:true,error:{code:'E_SESSION_WORKER',message:p.stderr||p.error?.message||'El proceso no confirmó la operación. Reintenta con el mismo identificador.'}};try{return JSON.parse(p.stdout);}catch{return {ok:false,committed:false,error:{code:'E_SESSION_PROTOCOL',message:'Respuesta de sesión no válida.'}};}
}
function work(runtime,base,root,request){
 const h=head(root),id=request.requestId;if(typeof id!=='string'||!/^[A-Za-z0-9_.-]{1,96}$/.test(id))throw Error('Invalid request id');const raw=Buffer.from(request.body,'base64'),digest=sha(Buffer.concat([Buffer.from(request.operation+'\0'+(request.title||'')+'\0'),raw]));
 if(Object.hasOwn(h.requests,id)){const old=h.requests[id];if(old.digest!==digest)return {ok:false,committed:false,error:{code:'E_REPLAY_MISMATCH',message:'El identificador ya corresponde a otro contenido.'}};return {...JSON.parse(fs.readFileSync(path.join(root,'versions',old.directory,'receipt.json'))),replayed:true};}
 if(request.expectedGeneration!==undefined&&request.expectedGeneration!==h.generation)return {ok:false,committed:false,error:{code:'E_STALE',message:'La sesión cambió; vuelve a leer su revisión.'},generation:h.generation};
 if(Object.keys(h.requests).length>=4096)throw Error('Receipt capacity reached; archive this session before continuing');
 const input=path.join(root,'versions',h.directory,'state.rvp');if(sha(fs.readFileSync(input))!==h.state_sha256)throw Error('Current session state failed its digest');
 const name=crypto.randomUUID(),staging=path.join(root,'versions','.pending-'+name),published=path.join(root,'versions',name);fs.mkdirSync(staging,{mode:0o700});let committed=false;
 try{const output=path.join(staging,'state.rvp');let result;if(request.operation==='chat')result=chat(runtime,base,input,output,raw);else if(request.operation==='import'){const r=importDocument(runtime,path.join(base,'conversation.xi'),input,output,request.title,raw);result={ok:true,committed:true,response:'Documento incorporado.',bytes:r.bytes,parts:r.parts};}else throw Error('Unsupported session operation');
 if(!result.ok)return result;const receipt={...result,output:undefined,ok:true,committed:true,generation:h.generation+1,requestId:id,replayed:false,state_sha256:sha(fs.readFileSync(output)),parent_sha256:h.state_sha256};syncFile(output);putJSON(path.join(staging,'receipt.json'),receipt);syncDirectory(staging);fs.renameSync(staging,published);syncDirectory(path.join(root,'versions'));
 if(request.fault==='before_head')throw Error('Injected failure before HEAD publication');
 const next={version:1,generation:h.generation+1,directory:name,state_sha256:receipt.state_sha256,requests:{...h.requests,[id]:{digest,directory:name}}},tmp=path.join(root,'.HEAD-'+name);putJSON(tmp,next);fs.renameSync(tmp,path.join(root,'HEAD.json'));committed=true;try{syncDirectory(root);return receipt;}catch(e){return {...receipt,durability:{ok:false,message:e.message}};}
 }finally{if(fs.existsSync(staging))fs.rmSync(staging,{recursive:true});/* An orphan immutable version after a crash is preserved for inspection; never replayed automatically. */}
}
const invoked=process.argv[1]&&path.resolve(process.argv[1])===self;
if(invoked&&process.argv[2]==='--worker'){try{console.log(JSON.stringify(work(...process.argv.slice(3,6),JSON.parse(fs.readFileSync(0,'utf8')))));}catch(e){console.log(JSON.stringify({ok:false,committed:false,error:{code:'E_SESSION_COMMIT',message:e.message}}));}}
else if(invoked&&process.argv[2]==='init'){const[r,b,root,initial]=process.argv.slice(3);console.log(JSON.stringify(initialize(root,b,initial)));}
else if(invoked&&process.argv[2]==='turn'){const[r,b,root,id,...message]=process.argv.slice(3);console.log(JSON.stringify(transact(r,b,root,id,message.join(' '))));}
