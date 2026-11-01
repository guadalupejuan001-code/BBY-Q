#!/usr/bin/env node
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import fs from 'node:fs';
import {prepare} from './integration/x10/prepare.mjs';
import {initialize,transact} from './ai/personal/x09/session.mjs';
import {initialize as initializeX10,transact as transactX10,upgradeSession,inspect} from './ai/personal/x10/session.mjs';
import {migrateState} from './ai/personal/x09/migrate.mjs';
import {installRelational} from './ai/personal/p02/relational.mjs';
import {quantumCommand} from './integration/qml_qrl/cli.mjs';

const root=path.dirname(fileURLToPath(import.meta.url)),args=process.argv.slice(2);
let build=path.join(root,'build/x10');
if(args[0]==='--build'){args.shift();if(!args[0])throw Error('--build requires a directory');build=path.resolve(args.shift());}
const [command,...rest]=args,base=path.join(build,'native'),runtime=path.join(build,'runtime/reverse_pc');
const capacity=fs.existsSync(path.join(build,'capacity/build.json'));
try{
 let result;
 if(command==='quantum'){
  result=quantumCommand({root,build,argv:rest});
 }else if(command==='prepare'){
  let archive;const at=rest.indexOf('--archive');
  if(at>=0){if(!rest[at+1])throw Error('--archive requires a ZIP file');archive=rest[at+1];rest.splice(at,2);}
  if(rest.length>1)throw Error('Usage: node bbyq.mjs prepare [NEW_BUILD_DIRECTORY] --archive RECOVERED_X09.zip');
  result=prepare(rest[0]||build,{archive});
 }else if(command==='install-e034'){
  if(rest.length>1||!capacity)throw Error('Usage: node bbyq.mjs install-e034 [VERIFIED_E034_ARTIFACT.zip | composed.rxe] (defaults to bundled verified capsule; requires X10 build)');
  result=installRelational(build,rest[0]);
 }else if(command==='init'){
  if(rest.length<1||rest.length>2)throw Error('Usage: node bbyq.mjs init NEW_SESSION_DIRECTORY [INITIAL_X09_STATE.rvp]');
  result=(capacity?initializeX10:initialize)(rest[0],base,rest[1]);
 }else if(command==='turn'){
  const [session,id,...words]=rest;let language='es',module,learn=false;
  while(words.length&&words[0].startsWith('--')){
   if(words[0].startsWith('--language='))language=words.shift().slice(11);
   else if(words[0].startsWith('--module='))module=words.shift().slice(9);
   else if(words[0]==='--learn'){learn=true;words.shift();}
   else break;
  }
  if(!session||!id||!words.length)throw Error('Usage: node bbyq.mjs turn SESSION REQUEST_ID [--language=en] [--module=e034|p03|p04|p05|p06|quantum] [--learn] MESSAGE | --file UTF8_FILE');
  if(!capacity&&(module||learn))throw Error('Los módulos E034/P03/P04/P05/P06/quantum requieren el motor X10.');
  let message=words.join(' ');if(words[0]==='--file'){if(words.length!==2)throw Error('--file requires exactly one UTF-8 file');message=fs.readFileSync(words[1]);}
  result=(capacity?transactX10:transact)(runtime,base,session,id,message,{language,...(module?{module}:{}),...(learn?{learn}: {})});
 }else if(command==='status'){
  if(rest.length!==1)throw Error('Usage: node bbyq.mjs status X10_SESSION');result=inspect(rest[0]);
 }else if(command==='upgrade-session'){
  if(rest.length!==2)throw Error('Usage: node bbyq.mjs upgrade-session OLD_X09_SESSION NEW_X10_SESSION');
  result=upgradeSession(runtime,base,rest[0],rest[1]);
 }else if(command==='migrate-session'){
  if(rest.length!==2)throw Error('Usage: node bbyq.mjs migrate-session SESSION REQUEST_ID');
  result=transact(runtime,base,rest[0],rest[1],'integrar X09',{operation:'migrate'});
 }else if(command==='migrate-state'){
  if(rest.length!==2)throw Error('Usage: node bbyq.mjs migrate-state X08_INPUT.rvp NEW_OUTPUT.rvp');
  result=migrateState(runtime,base,...rest);
 }else throw Error('Commands: quantum, prepare, install-e034, init, turn, status, upgrade-session, migrate-session, migrate-state. Linux x86-64 and Node 24+. Optional prefix: --build DIRECTORY.');
 console.log(JSON.stringify(result,null,2));if(!result.ok)process.exitCode=1;
}catch(error){console.error(JSON.stringify({ok:false,error:{code:error.code||'E_X09',message:error.message}}));process.exitCode=1;}
