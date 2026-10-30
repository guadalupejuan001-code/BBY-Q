import path from 'node:path';import {chat} from './io.mjs';
const[r,b,i,o,q]=process.argv.slice(2);if(q===undefined)throw Error('usage: run.mjs RUNTIME X05_BUILD INPUT.rvp NEW_OUTPUT.rvp MESSAGE');console.log(JSON.stringify(chat(...[r,b,i,o].map(p=>path.resolve(p)),q),null,2));
