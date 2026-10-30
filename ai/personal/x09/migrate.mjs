// Atomic file migration. The trained campaign is installed by its XI role.
import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import {spawnSync} from 'node:child_process';
import {fileURLToPath} from 'node:url';
import {B as X6,F} from '../x06/schema.mjs';

const sha=b=>crypto.createHash('sha256').update(b).digest('hex');
const START=9180000000000000000n,DATA_END=9180000000001000000n,SCRATCH_END=9180000000002000000n;

function state(file) {
  const bytes=fs.readFileSync(file);
  if(bytes.subarray(0,5).toString()!=='RVPC2')throw Error('Estado RVPC2 no compatible.');
  const size=Number(bytes.readBigUInt64LE(5));
  if(!Number.isSafeInteger(size)||size<0||29+size>bytes.length)throw Error('Cabecera de estado no válida.');
  const cells=new Map(),opaque=[];
  for(const line of bytes.subarray(29+size).toString().split('\n')) {
    if(!line)continue;
    if(line.startsWith('O ')) {
      const fields=line.split(' '),value=Number(fields[2]);
      if(value)cells.set(BigInt(fields[1]),value);
    } else if(!line.startsWith('MXIM2 '))opaque.push(line);
  }
  return {bytes,cells,core:bytes.subarray(29,29+size),opaque};
}

function run(runtime,program,working) {
  const p=spawnSync(runtime,['run',program,working,working],{encoding:'utf8',timeout:60000,maxBuffer:16*1024*1024});
  if(p.status!==0)throw Error(p.stderr||p.error?.message||'La migración XI no terminó.');
  return p.stdout.split('\n').filter(l=>l.startsWith('{')).map(JSON.parse).filter(e=>e.type==='register');
}

export function migrateState(runtime,base,input,output) {
  [runtime,base,input,output]=[runtime,base,input,output].map(p=>path.resolve(p));
  if(fs.existsSync(output))throw Error('Elige un destino nuevo; el original se conserva.');
  const manifest=JSON.parse(fs.readFileSync(path.join(base,'build.json')));
  if(manifest.version!=='X09-All-Training-1')throw Error('Se requiere una entrega X09 completa.');
  const trusted=(name,expected)=>{
    const file=path.join(base,name);
    if(!expected||sha(fs.readFileSync(file))!==expected)throw Error('Activo de migración alterado: '+name);
    return file;
  };
  if(sha(fs.readFileSync(runtime))!==manifest.runtime_sha256)throw Error('El ejecutor no coincide con la entrega X09.');
  const extension=manifest.extensions?.campaign;
  if(extension?.directory!=='campaign'||extension.manifest_file!=='campaign-build.json')throw Error('Falta la campaña integrada.');
  const descriptor=JSON.parse(fs.readFileSync(trusted('campaign/campaign-build.json',extension.manifest_sha256)));
  const program=trusted('campaign/campaign-migrate.rxe',descriptor.roles?.['campaign-migrate.rxe']);
  const guard=trusted('guard.xi',manifest.roles_sha256?.['guard.xi']);
  const knowledgeGuard=trusted('guard-x07.xi',manifest.roles_sha256?.['guard-x07.xi']);
  const before=state(input);
  const at=p=>before.cells.get(p)||0;
  if(at(X6)!==86||at(X6+1n)!==1||at(F)!==86||at(F+1n)!==2||at(9120000000000000000n)!==88||at(9120000000000000001n)!==1||at(9110000000000000000n)!==87||at(9110000000000000001n)!==2)throw Error('Migra primero este estado completo a X08.');
  if(at(7100000000000000000n)!==76||at(7100000000000000001n)!==71||at(7100000000000000002n)!==1)throw Error('Falta el banco de lenguaje E009 original.');
  if([...before.cells].some(([a])=>a>=DATA_END&&a<SCRATCH_END))throw Error('La región temporal de campaña está ocupada.');
  const temporary=fs.mkdtempSync(path.join(path.dirname(output),'.x09-migrate-'));
  const working=path.join(temporary,'state.rvp');
  try {
    fs.copyFileSync(input,working);
    run(runtime,guard,working);
    run(runtime,knowledgeGuard,working);
    const registers=run(runtime,program,working);
    if(registers.length!==1||registers[0].register!=='r0'||registers[0].value!==0)throw Error('La campaña no confirmó su instalación.');
    const after=state(working);
    if(!before.core.equals(after.core)||JSON.stringify(before.opaque)!==JSON.stringify(after.opaque))throw Error('La migración cambió memoria ajena a la campaña.');
    let changed=0;
    for(const address of new Set([...before.cells.keys(),...after.cells.keys()])) {
      if((before.cells.get(address)||0)===(after.cells.get(address)||0))continue;
      if(address<START||address>=DATA_END)throw Error('La migración alteró aprendizaje previo en '+address);
      changed++;
    }
    if([...after.cells].some(([a])=>a>=DATA_END&&a<SCRATCH_END))throw Error('La migración dejó datos temporales.');
    const fd=fs.openSync(working,'r');try{fs.fsyncSync(fd);}finally{fs.closeSync(fd);}
    fs.linkSync(working,output);
    return {ok:true,output,source_sha256:sha(before.bytes),state_sha256:sha(after.bytes),changed_campaign_cells:changed,previous_training_preserved:true,idempotent:changed===0};
  } finally {fs.rmSync(temporary,{recursive:true});}
}

if(process.argv[1]&&path.resolve(process.argv[1])===fileURLToPath(import.meta.url)) {
  const [runtime,base,input,output]=process.argv.slice(2);
  if(!output)throw Error('Usage: migrate.mjs RUNTIME X09_BUILD X08_INPUT.rvp NEW_OUTPUT.rvp');
  console.log(JSON.stringify(migrateState(runtime,base,input,output)));
}
