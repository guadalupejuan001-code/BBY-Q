#!/usr/bin/env node
// Local launcher for the integrated native agent; no language inference here.
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {initialize,transact} from './source/ai/personal/x09/session.mjs';
import {migrateState} from './source/ai/personal/x09/migrate.mjs';
const root=path.dirname(fileURLToPath(import.meta.url));
const runtime=path.join(root,'runtime','reverse_pc'),base=path.join(root,'native');
const [command,...args]=process.argv.slice(2);
let result;
if(command==='init') {
  if(args.length!==1)throw Error('Usage: node bbyq.mjs init NEW_SESSION_DIRECTORY');
  result=initialize(args[0],base);
} else if(command==='turn') {
  const [session,id,...words]=args;
  let language='es';if(words[0]?.startsWith('--language='))language=words.shift().slice(11);
  if(!session||!id||!words.length)throw Error('Usage: node bbyq.mjs turn SESSION REQUEST_ID [--language=en] MESSAGE');
  result=transact(runtime,base,session,id,words.join(' '),{language});
} else if(command==='migrate-session') {
  const [session,id]=args;
  if(!session||!id)throw Error('Usage: node bbyq.mjs migrate-session SESSION REQUEST_ID');
  result=transact(runtime,base,session,id,'integrar X09',{operation:'migrate'});
} else if(command==='migrate-state') {
  if(args.length!==2)throw Error('Usage: node bbyq.mjs migrate-state X08_INPUT.rvp NEW_OUTPUT.rvp');
  result=migrateState(runtime,base,...args);
} else throw Error('Commands: init, turn, migrate-session, migrate-state. Node.js 24+ and Linux x86-64 are required.');
console.log(JSON.stringify(result,null,2));
if(!result.ok)process.exitCode=1;
