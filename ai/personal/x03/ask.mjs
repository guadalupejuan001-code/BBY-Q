import path from'node:path';import{askDocument}from'./io.mjs';
const[r,b,input,output,question]=process.argv.slice(2);if(!question)throw Error('usage: ask.mjs RUNTIME X03_BUILD INPUT.rvp NEW_OUTPUT.rvp QUESTION');console.log(JSON.stringify(askDocument(path.resolve(r),path.resolve(b,'conversation.xi'),path.resolve(input),path.resolve(output),question),null,2));
