import fs from 'node:fs';
import path from 'node:path';
import {zeroSource,schema} from '../../ai/personal/zero/model.mjs';
const root=path.resolve(import.meta.dirname,'../..'),out=path.resolve(process.argv[2]||path.join(root,'build/zero'));
fs.mkdirSync(out,{recursive:true});
const source=path.join(out,'zero.xi');fs.writeFileSync(source,zeroSource());fs.writeFileSync(path.join(out,'schema.json'),JSON.stringify(schema,null,2)+'\n');
// This program uses the native numeric XI profile; RXE v1 does not encode it.
// It executes directly through the same pinned persistent XI interpreter.
console.log(JSON.stringify({ok:true,directory:out}));
