// I/O only: fixed byte framing and output decoding. No fact selection or ranking.
import fs from'node:fs';import path from'node:path';import{spawnSync}from'node:child_process';
export const X3=9070000000000000000n;
function discardFile(file){try{fs.unlinkSync(file);}catch(e){if(e.code!=='ENOENT')throw e;}}
function discardJob(dir){
 for(const entry of fs.readdirSync(dir,{withFileTypes:true})){const p=path.join(dir,entry.name);if(entry.isDirectory()){if(!entry.name.startsWith('.x03-turn-'))throw Error('Unexpected directory in private job');discardJob(p);}else discardFile(p);}fs.rmdirSync(dir);
}
export function cell(state,address){const b=fs.readFileSync(state),n=Number(b.readBigUInt64LE(5));const line=b.subarray(29+n).toString().split('\n').find(s=>s.startsWith('O '+address+' '));return Number(line?.split(' ')[2]||0);}
export function nativeTurn(runtime,source,state,message,language='es'){
 const bytes=Buffer.from(message);if(bytes.length<1||bytes.length>255)throw Error('Native mailbox requires 1..255 UTF-8 bytes');const dir=fs.mkdtempSync(path.join(path.dirname(path.resolve(state)),'.x03-turn-')),program=path.join(dir,'turn.xi'),next=path.join(dir,'next.rvp');
 const lock=path.resolve(state)+'.x03-lock';let acquired=false;
 try{try{fs.mkdirSync(lock);acquired=true;}catch(e){if(e.code==='EEXIST')throw Error('E_BUSY: another writer owns this native state; use X08 serialized sessions');throw e;}const code=fs.readFileSync(source,'utf8');if(!code.startsWith('#!reverse-pc-machine-v1\n'))throw Error('Native XI source header required');let head='#!reverse-pc-machine-v1\nstore8 7400000000000000016 1\nstore8 7400000000000000017 '+bytes.length+'\nstore8 7400000000000000003 '+(language==='en'?2:1)+'\n';for(const[i,b]of bytes.entries())head+='store8 '+(7400000000000000128n+BigInt(i))+' '+b+'\n';fs.writeFileSync(program,head+code.split('\n').slice(1).join('\n'));
 const t=performance.now(),p=spawnSync(runtime,['run',program,state,next],{encoding:'utf8',timeout:15000,maxBuffer:8*1024*1024});if(p.status!==0)throw Error('Native XI failed: '+p.stderr);const output=[];for(const line of p.stdout.split('\n'))if(line.startsWith('{')){const item=JSON.parse(line);if(item.register==='r14'||item.register==='r9'){if(!Number.isInteger(item.value)||item.value<0||item.value>255)throw Error('Output byte outside text ABI');output.push(item.value);}}const response=new TextDecoder('utf-8',{fatal:true}).decode(Buffer.from(output));if(!response||output.length>4096)throw Error('Invalid or empty native response');fs.renameSync(next,state);return {response,milliseconds:performance.now()-t};
 }finally{try{discardJob(dir);}finally{if(acquired)fs.rmdirSync(lock);}}
}
export function importDocument(runtime,source,input,output,title,bytes){
 if(fs.existsSync(output))throw Error('Output already exists; choose a new file');new TextDecoder('utf-8',{fatal:true}).decode(bytes);if([...bytes].some(b=>b<32&&![9,10,13].includes(b)))throw Error('Plain UTF-8 text required');if(Buffer.byteLength(title)>80||!title.trim())throw Error('Title must contain 1..80 UTF-8 bytes');const dir=fs.mkdtempSync(path.join(path.dirname(path.resolve(output)),'.x03-import-')),working=path.join(dir,'working.rvp'),trace=[];fs.copyFileSync(input,working);
 try{const ask=q=>{const result=nativeTurn(runtime,source,working,q);trace.push({input_bytes:Buffer.byteLength(q),output:result.response,milliseconds:result.milliseconds});return result.response;};if(ask('@doc begin '+title)!=='Documento abierto.')throw Error('Document start was refused');let offset=0,parts=0;
 while(offset<bytes.length){let end=Math.min(bytes.length,offset+224);while(end>offset&&end<bytes.length&&(bytes[end]&192)===128)end--;if(end===offset)throw Error('Cannot frame UTF-8 bytes');const text=new TextDecoder('utf-8',{fatal:true}).decode(bytes.subarray(offset,end));if(!ask('@doc append '+text).startsWith('CTX guardado #'))throw Error('Document append was refused');offset=end;parts++;}
 if(ask('@doc end')!=='Documento guardado.')throw Error('Document finalization was refused');fs.linkSync(working,output);return {parts,bytes:bytes.length,trace,output:path.resolve(output)};
 }finally{discardJob(dir);}
}
export function askDocument(runtime,source,input,output,question,language='es'){
 if(fs.existsSync(output))throw Error('Output already exists; choose a new file');const dir=fs.mkdtempSync(path.join(path.dirname(path.resolve(output)),'.x03-ask-')),working=path.join(dir,'working.rvp'),trace=[];fs.copyFileSync(input,working);
 try{let turn=nativeTurn(runtime,source,working,question,language);trace.push(turn);for(let i=0;cell(working,X3+30000n)===1;i++){if(i>=130)throw Error('Native search exceeded its declared step count');turn=nativeTurn(runtime,source,working,'@read next',language);trace.push(turn);}fs.linkSync(working,output);return {response:turn.response,steps:trace.length,trace,output:path.resolve(output)};
 }finally{discardJob(dir);}
}
