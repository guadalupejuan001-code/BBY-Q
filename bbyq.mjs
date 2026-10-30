#!/usr/bin/env node
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {prepare} from './integration/x09/prepare.mjs';
import {initialize,transact} from './ai/personal/x09/session.mjs';
import {migrateState} from './ai/personal/x09/migrate.mjs';

const root=path.dirname(fileURLToPath(import.meta.url)),args=process.argv.slice(2);
let build=path.join(root,'build/x09');
if(args[0]==='--build'){args.shift();if(!args[0])throw Error('--build requires a directory');build=path.resolve(args.shift());}
const [command,...rest]=args,base=path.join(build,'native'),runtime=path.join(build,'runtime/reverse_pc');
try{
 let result;
 if(command==='prepare'){
  let archive;const at=rest.indexOf('--archive');
  if(at>=0){if(!rest[at+1])throw Error('--archive requires a ZIP file');archive=rest[at+1];rest.splice(at,2);}
  if(rest.length>1)throw Error('Usage: node bbyq.mjs prepare [NEW_BUILD_DIRECTORY] --archive RECOVERED_X09.zip');
  result=prepare(rest[0]||build,{archive});
 }else if(command==='init'){
  if(rest.length!==1)throw Error('Usage: node bbyq.mjs init NEW_SESSION_DIRECTORY');
  result=initialize(rest[0],base);
 }else if(command==='turn'){
  const [session,id,...words]=rest;let language='es';
  if(words[0]?.startsWith('--language='))language=words.shift().slice(11);
  if(!session||!id||!words.length)throw Error('Usage: node bbyq.mjs turn SESSION REQUEST_ID [--language=en] MESSAGE');
  result=transact(runtime,base,session,id,words.join(' '),{language});
 }else if(command==='migrate-session'){
  if(rest.length!==2)throw Error('Usage: node bbyq.mjs migrate-session SESSION REQUEST_ID');
  result=transact(runtime,base,rest[0],rest[1],'integrar X09',{operation:'migrate'});
 }else if(command==='migrate-state'){
  if(rest.length!==2)throw Error('Usage: node bbyq.mjs migrate-state X08_INPUT.rvp NEW_OUTPUT.rvp');
  result=migrateState(runtime,base,...rest);
 }else throw Error('Commands: prepare, init, turn, migrate-session, migrate-state. Linux x86-64 and Node 24+. Optional prefix: --build DIRECTORY.');
 console.log(JSON.stringify(result,null,2));if(!result.ok)process.exitCode=1;
}catch(error){console.error(JSON.stringify({ok:false,error:{code:error.code||'E_X09',message:error.message}}));process.exitCode=1;}
