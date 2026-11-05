// Transport and immutable sessions for the existing XI VQC3/QRL3 agents.
// No learning, quantum simulator, response generation or policy is implemented here.
import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import zlib from 'node:zlib';
import {execFileSync} from 'node:child_process';
import {evaluationEvidence} from './evidence.mjs';

const digest=b=>crypto.createHash('sha256').update(b).digest('hex');
const hash=p=>digest(fs.readFileSync(p));
const error=(code,message)=>{const e=Error(message);e.code=code;throw e;};
const requireThat=(v,message)=>{if(!v)error('E_QUANTUM3',message);};
const MAX_RECEIPTS=4096;
const idPattern=/^[A-Za-z0-9_.-]{1,96}$/;
const usage='quantum v3 prepare SESSION --runtime=REVERSE_PC_DIRECTORY | status SESSION | results SESSION | classify SESSION INPUTS.json | act SESSION POSITION GOAL [--greedy] | learn-class SESSION REQUEST_ID INPUTS.json LABEL | learn-episode SESSION REQUEST_ID [--slip=0.15] [--horizon=12] | export SESSION NEW_FILE.rvp';
const sourceFiles=['integration/quantum3/cli.py','integration/quantum3/campaign.py','ai/xi/quantum3/birth.xi','ai/xi/quantum3/common.xi','ai/xi/quantum3/benchmarks.xi','ai/xi/quantum3/qrl3.xi','ai/xi/quantum3/encode-input.xi','ai/xi/quantum3/vqc3-infer.xi','ai/xi/quantum3/qrl3-act.xi'];
const extensionFiles=['integration/quantum3/step.py','ai/xi/quantum3/step.xi'];

function atomicJson(file,value){
 const pending=file+'.'+crypto.randomUUID()+'.pending';
 const fd=fs.openSync(pending,'wx',0o600);
 try{fs.writeFileSync(fd,JSON.stringify(value,null,2)+'\n');fs.fsyncSync(fd);}finally{fs.closeSync(fd);}
 try{fs.renameSync(pending,file);}finally{if(fs.existsSync(pending))fs.unlinkSync(pending);}
}
function pins(root){return Object.fromEntries(sourceFiles.map(f=>[f,hash(path.join(root,f))]));}
function extensionPins(root){return Object.fromEntries(extensionFiles.map(f=>[f,hash(path.join(root,f))]));}
function native(root,config,state,args,script='cli.py'){
 const result=execFileSync(config.python,[path.join(root,'integration/quantum3',script),'--runtime',config.runtime,'--state',state,...args],
  {encoding:'utf8',timeout:120000,maxBuffer:4*1024*1024});
 return JSON.parse(result);
}
function load(root,session){
 const config=JSON.parse(fs.readFileSync(path.join(session,'agent.json'),'utf8'));
 requireThat(config.schema===1&&config.model_identifier===173&&config.qubits_per_agent===1000,'Unsupported quantum session schema');
 requireThat(hash(path.join(config.runtime,'build/xi_session'))===config.session_sha256,'XI runtime changed; use the original runtime or prepare a separate session');
 requireThat(hash(path.join(config.runtime,'build/reverse_pc'))===config.cli_sha256,'XI CLI changed');
 requireThat(JSON.stringify(pins(root))===JSON.stringify(config.source_sha256),'XI/Python implementation changed; existing session was preserved');
 // Old sessions keep their original source pins and remain usable.
 if(config.extension_source_sha256)requireThat(JSON.stringify(extensionPins(root))===JSON.stringify(config.extension_source_sha256),'V3 policy step implementation changed; existing session was preserved');
 const head=JSON.parse(fs.readFileSync(path.join(session,'HEAD.json'),'utf8'));
 requireThat(Number.isSafeInteger(head.revision)&&head.revision>=0&&/^versions\/[0-9]+-[a-f0-9-]+\.rvp$/.test(head.file),'Invalid quantum session head');
 requireThat(head.receipts&&typeof head.receipts==='object'&&!Array.isArray(head.receipts),'Invalid quantum request receipts');
 const state=path.resolve(session,head.file);
 requireThat(hash(state)===head.sha256,'Quantum checkpoint hash mismatch');
 return {config,head,state};
}
function info(root,config,state){
 const result=native(root,config,state,['info']);
 requireThat(result.vqc.training_episodes_in_checkpoint>=10000&&result.qrl.training_episodes_in_checkpoint>=10000,'Incomplete V3 checkpoint');
 return {backend:'XI / original Ether native reduced and factorized states; no MPS',model_identifier:173,qubits_per_agent:1000,topology:'250 independent entangled groups of 4 per agent; no global 1000-wire entanglement',...result};
}
function withLock(session,fn){
 const lock=path.join(session,'.write-lock');let fd;
 try{fd=fs.openSync(lock,'wx',0o600);}catch(e){if(e.code==='EEXIST')error('E_BUSY','Another quantum update is active; retry the same request ID');throw e;}
 try{fs.writeFileSync(fd,String(process.pid));return fn();}finally{fs.closeSync(fd);fs.unlinkSync(lock);}
}

export function quantum3Command({root,argv}){
 const args=[],flags={};
 for(const arg of argv){
  if(arg.startsWith('--runtime='))flags.runtime=arg.slice(10);
  else if(arg.startsWith('--python='))flags.python=arg.slice(9);
  else if(arg==='--greedy')flags.greedy=true;
  else if(arg.startsWith('--slip='))flags.slip=arg.slice(7);
  else if(arg.startsWith('--horizon='))flags.horizon=arg.slice(10);
  else if(arg.startsWith('--'))error('E_ARGUMENT','Unknown quantum V3 option: '+arg);
  else args.push(arg);
 }
 const [command,directory,...values]=args;
 requireThat(command&&directory,usage);
 requireThat(['prepare','status','results','classify','act','learn-class','learn-episode','export'].includes(command),usage);
 if(command!=='prepare')requireThat(!flags.runtime&&!flags.python,'Runtime selection belongs to prepare');
 if(flags.greedy)requireThat(command==='act','--greedy belongs to act');
 if(flags.slip!==undefined||flags.horizon!==undefined)requireThat(command==='learn-episode','Episode options belong to learn-episode');
 const session=path.resolve(directory);
 if(command==='prepare'){
  requireThat(!values.length&&flags.runtime,usage);
  requireThat(!fs.existsSync(session),'Choose a new session directory; previous models are preserved');
  const runtime=path.resolve(flags.runtime),python=flags.python||process.env.BBYQ_PYTHON||'python3';
  for(const f of ['build/reverse_pc','build/xi_session'])requireThat(fs.existsSync(path.join(runtime,f)),'Compile the current XI runtime first: missing '+f);
  const release=path.join(root,'integration/quantum3/release'),manifest=JSON.parse(fs.readFileSync(path.join(release,'manifest.json'),'utf8'));
  const compressed=fs.readFileSync(path.join(release,manifest.file));
  requireThat(digest(compressed)===manifest.gzip_sha256,'Bundled V3 archive hash mismatch');
  const bytes=zlib.gunzipSync(compressed,{maxOutputLength:16*1024*1024});
  requireThat(digest(bytes)===manifest.checkpoint_sha256,'Bundled V3 checkpoint hash mismatch');
  fs.mkdirSync(path.dirname(session),{recursive:true});
  const staging=fs.mkdtempSync(path.join(path.dirname(session),'.bbyq-v3-'));
  try{
   fs.mkdirSync(path.join(staging,'versions'));
   const file='versions/0-'+crypto.randomUUID()+'.rvp',state=path.join(staging,file);
   fs.writeFileSync(state,bytes,{flag:'wx',mode:0o600});
   const config={schema:1,model_identifier:173,qubits_per_agent:1000,runtime,python,session_sha256:hash(path.join(runtime,'build/xi_session')),cli_sha256:hash(path.join(runtime,'build/reverse_pc')),source_sha256:pins(root),extension_source_sha256:extensionPins(root),seed_sha256:manifest.checkpoint_sha256};
   const model=info(root,config,state);
   atomicJson(path.join(staging,'agent.json'),config);
   atomicJson(path.join(staging,'HEAD.json'),{revision:0,file,sha256:hash(state),receipts:{}});
   requireThat(!fs.existsSync(session),'Session destination appeared; refusing overwrite');
   fs.renameSync(staging,session);
   return {ok:true,action:'prepare-v3',session,revision:0,checkpoint_sha256:manifest.checkpoint_sha256,original_training_preserved:true,model};
  }finally{if(fs.existsSync(staging))fs.rmSync(staging,{recursive:true,force:true});}
 }
 requireThat(fs.statSync(session).isDirectory(),'Quantum session directory required');
 if(command==='status'){
  requireThat(!values.length,usage);const {config,head,state}=load(root,session);
  return {ok:true,action:'status-v3',revision:head.revision,checkpoint_sha256:head.sha256,learning_requests:Object.keys(head.receipts).length,model:info(root,config,state),evaluation:evaluationEvidence(root,head.sha256)};
 }
 if(command==='results'){
  requireThat(!values.length,usage);const {head}=load(root,session);
  return {ok:true,action:'results-v3',revision:head.revision,evaluation:evaluationEvidence(root,head.sha256)};
 }
 if(command==='classify'||command==='act'){
  const {config,head,state}=load(root,session);let pass;
  if(command==='classify'){requireThat(values.length===1,usage);pass=['classify','--inputs',path.resolve(values[0])];}
  else{requireThat(values.length===2,usage);pass=['act','--position',values[0],'--goal',values[1],...(flags.greedy?['--greedy']:[])];}
  const result=native(root,config,state,pass,command==='act'?'step.py':'cli.py');
  requireThat(hash(state)===head.sha256,'Read-only inference changed the checkpoint');
  return {ok:true,action:command,revision:head.revision,backend:'native XI; no MPS',checkpoint_unchanged:true,...result};
 }
 if(command==='export'){
  requireThat(values.length===1,usage);const {head,state}=load(root,session),destination=path.resolve(values[0]);
  fs.copyFileSync(state,destination,fs.constants.COPYFILE_EXCL);
  requireThat(hash(destination)===head.sha256,'Export hash mismatch');
  return {ok:true,action:'export-v3',file:destination,revision:head.revision,sha256:head.sha256};
 }
 const [requestId,...parameters]=values;
 requireThat(idPattern.test(requestId||''),'A stable request ID is required');
 let pass,fingerprint,inputBytes;
 if(command==='learn-class'){
  requireThat(parameters.length===2&&['0','1'].includes(parameters[1]),usage);
  const input=path.resolve(parameters[0]),content=fs.readFileSync(input);
  requireThat(content.length<=256*1024,'Input JSON exceeds 256 KiB');
  inputBytes=content;
  pass=['learn-class','--inputs',input,'--label',parameters[1]];
  fingerprint=digest(JSON.stringify([command,parameters[1],digest(content)]));
 }else{
  requireThat(!parameters.length,usage);
  const slip=Number(flags.slip??'.15'),horizon=Number(flags.horizon??'12');
  requireThat(Number.isFinite(slip)&&slip>=0&&slip<=1&&Number.isSafeInteger(horizon)&&horizon>0&&horizon<=100,'Invalid slip or horizon');
  pass=['learn-episode','--slip',String(slip),'--horizon',String(horizon)];
  fingerprint=digest(JSON.stringify([command,slip,horizon]));
 }
 return withLock(session,()=>{
  const {config,head,state}=load(root,session);
  const previous=Object.hasOwn(head.receipts,requestId)?head.receipts[requestId]:null;
  if(previous){
   requireThat(previous.fingerprint===fingerprint,'Request ID already used with different input');
   return {...previous.result,replayed:true};
  }
  requireThat(Object.keys(head.receipts).length<MAX_RECEIPTS,'Session receipt capacity reached; export this model before preparing a new workspace');
  const revision=head.revision+1,file='versions/'+revision+'-'+crypto.randomUUID()+'.rvp',output=path.join(session,file);
  let published=false,inputSnapshot;
  try{
   if(inputBytes){
    inputSnapshot=path.join(session,'.input-'+crypto.randomUUID()+'.json');
    fs.writeFileSync(inputSnapshot,inputBytes,{flag:'wx',mode:0o600});
    pass=[...pass];pass[2]=inputSnapshot;
   }
   const result=native(root,config,state,[...pass,'--output',output]);
   requireThat(hash(state)===head.sha256,'Learning changed the input checkpoint');
   const sha256=hash(output),response={ok:true,action:command,request_id:requestId,revision,backend:'native XI; no MPS',replayed:false,parent_checkpoint_sha256:head.sha256,checkpoint_sha256:sha256,...result};
   // Keep portable session identity, not the ephemeral Python output path.
   delete response.checkpoint;
   const receipts={...head.receipts,[requestId]:{fingerprint,result:response}};
   atomicJson(path.join(session,'HEAD.json'),{revision,file,sha256,receipts});published=true;
   return response;
  }finally{
   if(!published&&fs.existsSync(output))fs.unlinkSync(output);
   if(inputSnapshot&&fs.existsSync(inputSnapshot))fs.unlinkSync(inputSnapshot);
  }
 });
}
