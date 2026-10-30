// Text framing, hashing, immutable files and native invocation only.
// Request interpretation, validation of text and scheduling execute in XI.
import fs from 'node:fs';import path from 'node:path';import crypto from 'node:crypto';import {spawnSync} from 'node:child_process';import {snapshot as fullSnapshot,source,executeTask} from '../x05/io.mjs';import {B,F,C,INPUT_BYTES,OUTPUT_BYTES} from '../x06/schema.mjs';
import {service as dictionaryService} from './dictionary/service.mjs';
import {service as campaignService} from './campaign/service.mjs';
import {BASE as CAMPAIGN,SCHEMA as CAMPAIGN_SCHEMA} from './campaign/schema.mjs';
// Only protocol addresses are needed here. Book/index payloads remain opaque bytes.
function snapshot(file){const b=fs.readFileSync(file),n=Number(b.readBigUInt64LE(5)),m=new Map();for(const line of b.subarray(29+n).toString().split('\n')){if(!line.startsWith('O '))continue;const end=line.indexOf(' ',2);if(end-2<19)continue;const value=Number(line.slice(end+1));if(value)m.set(BigInt(line.slice(2,end)),value);}return m;}
export {snapshot};
const hash=b=>crypto.createHash('sha256').update(b).digest('hex'),byte=(m,p)=>m.get(p)||0;
const errors={1:['E_EMPTY','El mensaje está vacío.'],2:['E_SIZE','El mensaje supera 16384 bytes.'],3:['E_UTF8','El mensaje no es UTF-8 canónico válido.'],4:['E_CONTROL','El mensaje contiene un control no permitido.'],5:['E_VERSION','Versión del contrato de texto no compatible.'],6:['E_LANGUAGE','Idioma de salida no válido.'],7:['E_UNSUPPORTED_TEXT','El texto se recibió completo, pero este formato no es compatible con el módulo solicitado.']};
class Failure extends Error{constructor(code,message,phase){super(message);this.code=code;this.phase=phase;}}
function native(rt,args){const p=spawnSync(rt,args,{encoding:'utf8',timeout:30000,maxBuffer:16*1024*1024});if(p.status!==0)throw new Failure('E_NATIVE',p.stderr||p.error?.message||'Fallo nativo','native');return p.stdout;}
export function speech(jsonl){const out=[];for(const line of jsonl.split('\n')){if(!line.startsWith('{'))continue;const event=JSON.parse(line);if(event.type!=='register'||!['r14','r9'].includes(event.register))continue;if(!Number.isInteger(event.value)||event.value<0||event.value>255)throw new Failure('E_OUTPUT_BYTE','Byte de salida no válido.','output');if((event.value<32&&![9,10,13].includes(event.value))||event.value===127)throw new Failure('E_OUTPUT_CONTROL','Control de salida no permitido.','output');if(out.length>=OUTPUT_BYTES)throw new Failure('E_OUTPUT_SIZE','La respuesta supera 65536 bytes.','output');out.push(event.value);}if(!out.length)throw new Failure('E_OUTPUT_EMPTY','No se produjo una respuesta.','output');try{return new TextDecoder('utf-8',{fatal:true,ignoreBOM:true}).decode(Uint8Array.from(out));}catch{throw new Failure('E_OUTPUT_UTF8','La salida no es UTF-8 válido.','output');}}
function discard(dir){for(const f of fs.readdirSync(dir,{withFileTypes:true})){if(!f.isFile())throw Error('Unexpected directory in private X06 job');fs.unlinkSync(path.join(dir,f.name));}fs.rmdirSync(dir);}
export function chat(runtime,base,input,output,message,options={}){
 let job,outcome,attachmentCreated=false;try{
  if(fs.existsSync(output)||fs.existsSync(output+'.files'))throw new Failure('E_DESTINATION','El destino ya existe. Elige un archivo nuevo.','publication');
  let raw;if(Buffer.isBuffer(message)||message instanceof Uint8Array)raw=Buffer.from(message);else if(typeof message==='string'){if(!message.isWellFormed())throw new Failure('E_UTF16','El texto contiene un sustituto Unicode sin pareja.','encoding');raw=Buffer.from(message,'utf8');}else throw new Failure('E_INPUT_TYPE','Se requiere texto o bytes UTF-8.','encoding');
  if(raw.length>INPUT_BYTES)throw new Failure(...errors[2],'framing');
  const manifest=JSON.parse(fs.readFileSync(path.join(base,'build.json'))),trusted=(name,sha)=>{const p=path.join(base,name);if(!sha||hash(fs.readFileSync(p))!==sha)throw new Failure('E_BUILD','El archivo no corresponde a la versión comprobada: '+name,'integrity');return p;};
  if(manifest.standalone_capsule!==false)trusted('BBY-Q.rxe',manifest.app_sha256);const code=trusted('code.rxe',manifest.code_sha256),guard=trusted('guard.xi',manifest.roles_sha256?.['guard.xi']),finish=trusted('text-finish.xi',manifest.roles_sha256?.['text-finish.xi']);
  job=fs.mkdtempSync(path.join(path.dirname(path.resolve(output)),'.x09-chat-'));const live=path.join(job,'working.rvp');fs.copyFileSync(input,live);let initial=snapshot(live);if(byte(initial,B)!==86||byte(initial,B+1n)!==1||byte(initial,F)!==86||byte(initial,F+1n)!==2)throw new Failure('E_SCHEMA','Primero migra la sesión al esquema X06.','preflight');if(byte(initial,CAMPAIGN)!==76||byte(initial,CAMPAIGN+1n)!==71||byte(initial,CAMPAIGN+2n)!==CAMPAIGN_SCHEMA)throw new Failure('E_X09_MIGRATION','Primero integra los entrenamientos mediante la migración X09.','preflight');native(runtime,['run',guard,live,live]);
  let stage='#!reverse-pc-machine-v1\n';const put=(p,v)=>{stage+=`store8 ${p} ${v}\n`;};put(F+2n,1);put(F+3n,0);put(F+4n,options.language===undefined||options.language==='es'?1:options.language==='en'?2:0);put(F+8n,raw.length&255);put(F+9n,raw.length>>>8);put(F+10n,0);for(let i=0;i<raw.length;i++)put(C+BigInt(i),raw[i]);stage+='halt\n';const frame=path.join(job,'input.xi');fs.writeFileSync(frame,stage);native(runtime,['run',frame,live,live]);
  let jsonl=native(runtime,['run',trusted('front.rxe',manifest.front_sha256),live,live]);
  let m=snapshot(live),extension;
  // X08 validates the entire frame and cancels stale execution requests before
  // either new XI role sees it. The host never interprets words or chooses facts.
  if(byte(m,F+3n)===3){const[code,text]=errors[byte(m,F+10n)]||['E_PROTOCOL','Error de contrato de texto.'];throw new Failure(code,text,'input');}
  if(byte(m,9120000000000000002n)===0){
    const invoke=(name,service)=>{
      const descriptor=manifest.extensions?.[name];
      if(!descriptor||descriptor.directory!==name)throw new Failure('E_EXTENSION','Falta una extensión integrada de X09.','integrity');
      const manifestFile=name==='campaign'?'campaign-build.json':'build.json';
      if(descriptor.manifest_file!==manifestFile)throw new Failure('E_EXTENSION','Descriptor de extensión incompatible.','integrity');
      trusted(name+'/'+manifestFile,descriptor.manifest_sha256);
      const result=service(runtime,path.join(base,name),live);
      if(!result||typeof result.handled!=='boolean')throw new Failure('E_EXTENSION_PROTOCOL','Respuesta de extensión no válida.','native');
      return result;
    };
    const dictionary=invoke('dictionary',dictionaryService);
    const result=dictionary.handled?dictionary:invoke('campaign',campaignService);
    if(result.handled){jsonl=result.jsonl;extension=dictionary.handled?'dictionary':'campaign';}
    else jsonl=native(runtime,['run',code,live,live]);
    m=snapshot(live);
  }
  if(byte(m,F+3n)===3){const[code,text]=errors[byte(m,F+10n)]||['E_PROTOCOL','Error de contrato de texto.'];throw new Failure(code,text,'input');}if(byte(m,F+2n)!==0||![1,2].includes(byte(m,F+3n)))throw new Failure('E_PROTOCOL','La entrada no fue consumida por el contrato esperado.','input');
  let response=speech(jsonl),execution={executed:false};if(byte(m,9090000000000000002n)===2){execution=executeTask(runtime,base,live,job,options);if(execution.response)response=execution.response;else if(!execution.executed)response='w4U rechazó la ejecución. No se ejecutó el programa.';}
  if(Buffer.byteLength(response)>OUTPUT_BYTES)throw new Failure('E_OUTPUT_SIZE','La respuesta supera 65536 bytes.','output');native(runtime,['run',finish,live,live]);
  const text=(byte(m,9090000000000000008n)||byte(m,9090000000000000009n))?source(live):'';if(text){fs.mkdirSync(output+'.files');attachmentCreated=true;fs.writeFileSync(path.join(output+'.files','program.xi'),text);for(const name of['program.rxe','dispatched.rvp'])if(fs.existsSync(path.join(job,name)))fs.copyFileSync(path.join(job,name),path.join(output+'.files',name));fs.writeFileSync(path.join(output+'.files','trace.json'),JSON.stringify(execution,null,2)+'\n');}
  fs.linkSync(live,output);attachmentCreated=false;return outcome={ok:true,committed:true,response,...execution,...(extension?{extension}:{}),output:path.resolve(output),transport:{version:2,input_bytes:raw.length,output_bytes:Buffer.byteLength(response),normalization:'none'}};
 }catch(error){if(attachmentCreated){for(const name of fs.readdirSync(output+'.files'))fs.unlinkSync(path.join(output+'.files',name));fs.rmdirSync(output+'.files');}return outcome={ok:false,committed:false,error:{code:error.code==='EEXIST'?'E_DESTINATION':error.code||'E_HOST',message:error.message,phase:error.phase||'host'},output:null};}
 // Post-publication file cleanup must never change a truthful committed result
 // into a failed turn. Native transient erasure already preceded publication.
 finally{if(job)try{discard(job);}catch(error){if(outcome)outcome.cleanup={ok:false,message:error.message,private_job:job};else throw error;}}
}
