// Maintainer-only export of the exact canonical training seed, never a live session.
import fs from 'node:fs';
import path from 'node:path';
import {execFileSync} from 'node:child_process';
import {fileURLToPath} from 'node:url';
import {snapshot} from '../../ai/personal/x05/io.mjs';
import {sha} from './prepare.mjs';

const [parentArg,nativeArg]=process.argv.slice(2);
if(!nativeArg)throw Error('Usage: package.mjs CANONICAL_X07 CANONICAL_X08');
const parent=path.resolve(parentArg),native=path.resolve(nativeArg),out=path.join(path.dirname(fileURLToPath(import.meta.url)),'release');
const expectedParent='d9800e677553c8f0abb909821c9a0845329a41da229da415ebbd082ac1afb40e';
const expectedModel='6f205595fe2f0032f76991205101f6c9f15d04ef1d10af77d7d87e6d12b3aef9';
if(sha(fs.readFileSync(path.join(parent,'model.rvp')))!==expectedParent||sha(fs.readFileSync(path.join(native,'model.rvp')))!==expectedModel)throw Error('Only the pinned canonical training fixtures can be published');
for(const folder of [parent,native]) {
  const cells=snapshot(path.join(folder,'model.rvp'));
  if([...cells].some(([p])=>p>=8900000000000000000n&&p<8900000000000200000n))throw Error('Personal memory is populated; refuse publication');
  if(cells.get(9100000000000200002n))throw Error('Active text request; refuse publication');
}
const parentNames=['BBY-Q.rxe','code.rxe','conversation.xi','model.rvp','build.json','guard.xi','guard-x07.xi','text-finish.xi','dispatch.xi','review.xi','result.xi','qdu-plan.xi','qdu-dispatch.xi','learn.xi','learn-bank.xi',...fs.readdirSync(parent).filter(n=>/^upgrade-parent-.*\.xi$/.test(n))];
const nativeNames=fs.readdirSync(native).filter(n=>/^[a-zA-Z0-9][a-zA-Z0-9.-]*$/.test(n)&&n!=='model.rvp'&&fs.statSync(path.join(native,n)).isFile());
fs.mkdirSync(out,{recursive:true});
const staging=fs.mkdtempSync(path.join(path.dirname(out),'.package-'));
try {
  const archives={};
  for(const [kind,source,names] of [['parent',parent,parentNames],['native',native,nativeNames]]) {
    fs.mkdirSync(path.join(staging,kind));
    const files={};
    for(const name of names.sort()) {
      const bytes=fs.readFileSync(path.join(source,name));
      fs.writeFileSync(path.join(staging,kind,name),bytes);
      files[name]=sha(bytes);
    }
    const file=kind+'.tar.gz';
    execFileSync('tar',['--sort=name','--mtime=@0','--owner=0','--group=0','--numeric-owner','-czf',path.join(out,file),'-C',staging,kind]);
    archives[kind]={file,sha256:sha(fs.readFileSync(path.join(out,file))),files};
  }
  const m=JSON.parse(fs.readFileSync(path.join(native,'build.json')));
  const manifest={format:1,version:m.version,model_sha256:m.model_sha256,code_sha256:m.code_sha256,front_sha256:m.front_sha256,concepts:m.concepts,relations:m.relations,book_pages:m.book_pages,archives,seed_scope:'Pinned canonical educational training fixture; personal memory empty; no user session or transcript',excluded:['P13','P14']};
  fs.writeFileSync(path.join(out,'manifest.json'),JSON.stringify(manifest,null,2)+'\n');
  console.log(JSON.stringify({ok:true,version:m.version,archives:Object.fromEntries(Object.entries(archives).map(([k,v])=>[k,v.sha256]))}));
} finally {fs.rmSync(staging,{recursive:true});}
