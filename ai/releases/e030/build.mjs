#!/usr/bin/env node
// Packaging only. Frame induction, matching, rewriting and responses execute in XI.
import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import {execFileSync} from 'node:child_process';
const [runtimeArg,outArg]=process.argv.slice(2);
if(!runtimeArg||!outArg)throw Error('usage: node build.mjs RUNTIME OUT');
const runtime=path.resolve(runtimeArg),out=path.resolve(outArg);
fs.mkdirSync(out,{recursive:true});
execFileSync('node',['ai/releases/e029/build.mjs',runtime,out],{stdio:'inherit'});
const header='#!reverse-pc-machine-v1';
const parent=fs.readFileSync(path.join(out,'natural-linked.xi'),'utf8');
const prefix=fs.readFileSync('ai/releases/e030/normalize.xi','utf8');
if(!parent.startsWith(header)||!prefix.startsWith(header))throw Error('link contract changed');
const source=prefix+parent.replace(header,'label lf_parent_entry');
fs.copyFileSync(path.join(out,'natural.rxe'),path.join(out,'e029-baseline.rxe'));
fs.writeFileSync(path.join(out,'learned-linked.xi'),source);
const run=(...args)=>execFileSync(runtime,args,{encoding:'utf8',maxBuffer:16*1024*1024});
run('compile',path.join(out,'learned-linked.xi'),path.join(out,'e030-code.rxe'),'BBY Q learned single-subject question frames');
run('pack-app',path.join(out,'e030-code.rxe'),path.join(out,'controller.rvp'),
 path.join(out,'learned.rxe'),'org.reverse.bbyq','BBY Q','E030-Learned-Frames-1-dev','beea73210fb3e6375a6bd90f3b88b476a4c175d2');
fs.copyFileSync(path.join(out,'learned.rxe'),path.join(out,'natural.rxe'));
const sha=p=>crypto.createHash('sha256').update(fs.readFileSync(p)).digest('hex');
const report={version:'E030-Learned-Frames-1-dev',source_parent:'beea73210fb3e6375a6bd90f3b88b476a4c175d2',
 seed_sha256:sha(path.join(out,'controller.rvp')),parent_sha256:sha(path.join(out,'e029-baseline.rxe')),
 candidate_sha256:sha(path.join(out,'learned.rxe')),
 learning:'XI supervised raw query + labeled subject + language + intent; two distinct subjects required',
 records:8,subject_bytes:31,literal_bytes_per_side:80,
 scope:'One subject slot; fixed definition-and-requirement intent, not unconstrained grammar induction',
 android_deployed:false};
fs.writeFileSync(path.join(out,'learned.json'),JSON.stringify(report,null,2)+'\n');
console.log(JSON.stringify(report,null,2));
