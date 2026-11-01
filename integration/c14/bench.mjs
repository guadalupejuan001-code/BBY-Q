// C14 end-to-end: 800 synthetic annotated training messages and 200 holdout,
// completely disjoint in topic AND template. Supervised weights/decisions are XI.
// The benchmark evaluates routing labels, NOT answer quality or quantum advantage.
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import {fileURLToPath} from 'node:url';
import {execFileSync,spawnSync} from 'node:child_process';
import {corpus} from './corpus.mjs';
import {intentSource} from '../../ai/personal/p01/intent.mjs';
import {NativePages,sha,readNumber,run,cells} from '../../ai/personal/x10/pages.mjs';

const [runtimeArg,outArg]=process.argv.slice(2);
if(!runtimeArg||!outArg)throw Error('Usage: node integration/c14/bench.mjs /path/reverse_pc FRESH_OUTPUT');
const runtime=path.resolve(runtimeArg),out=path.resolve(outArg);
if(fs.existsSync(out))throw Error('New evidence directory required');
const repo=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'../..');
const src=path.join(repo,'ai/xi/cognitive14');
const F=8270000000000000000n,A=n=>F+BigInt(n);
const {train,holdout,meta}=corpus();
fs.mkdirSync(out,{recursive:true});
function native(args,timeout=120000){
 const r=spawnSync(runtime,args,{encoding:'utf8',timeout,maxBuffer:32*1024*1024});
 if(r.status!==0)throw Error('XI command '+args.slice(0,3).join(' ')+' failed: '+(r.stderr||r.error?.message||r.stdout));
 return r.stdout;
}
function registers(text){
 const values=[];
 for(const line of text.split('\n'))if(line.startsWith('{')){
  const event=JSON.parse(line);
  if(event.type==='register')values.push(event.value);
 }
 return values;
}
function execute(program,input,output){return registers(native(['run',program,input,output]));}
const role=path.join(out,'intent.rxe');
const source=path.join(out,'intent.xi');
fs.writeFileSync(source,intentSource());
native(['compile',source,role,'C14 P01 native']);
const frames=path.join(out,'frames');
fs.mkdirSync(frames);
const pages=new NativePages(runtime,{'intent.rxe':role},frames);
const featureProgram=path.join(src,'features.xi');
const features=(text,contextFlag=0)=>{
 const raw=Buffer.from(text,'utf8');
 if(raw.length>190)throw Error('C14 corpus example too long: '+text);
 pages.validate(raw);
 const intent=pages.intent(raw);
 // Input flag is owner-controlled contextual evidence, never guessed from the text.
 const status=run(runtime,['run',featureProgram,pages.state,pages.state]);
 const recorded=registers(status);
 if(recorded.length!==3||recorded[0]!==intent.id||
    !Number.isInteger(recorded[1])||recorded[1]<0||recorded[1]>7||
    !Number.isInteger(recorded[2])||recorded[2]<0||recorded[2]>=144)
    throw Error('Invalid C14 native XI features: '+JSON.stringify({text,intent,recorded}));
 return {intent:intent.id,semantic:recorded[1],context:recorded[2],old_context:2*intent.id+contextFlag,
  text,read_only:intent.readOnly};
};
const records=(set)=>set.map((example,index)=>{
 const coded=features(example.text);
 return {...example,intent:coded.intent,semantic:coded.semantic,context:coded.context,
  old_context:coded.old_context};
});
const start=Date.now();
const trainEncoded=records(train),holdoutEncoded=records(holdout);
const durationFeatures=Date.now()-start;
const original=path.join(out,'blank.rvp'),model=path.join(out,'model.rvp'),staged=path.join(out,'staged.rvp'),
 trained=path.join(out,'trained.rvp');
native(['init',original]);
const startBirth=execute(path.join(src,'birth.xi'),original,model);
assert.deepEqual(startBirth,[14],'C14 XI schema signature');
const stagePath=path.join(out,'training-frame.xi');
const stage=['#!reverse-pc-machine-v1'];
function put(address,value) {
 if(!Number.isInteger(value)||value<0||value>255)throw Error('Invalid frame byte');
 stage.push('store8 '+address+' '+value);
}
put(A(4),trainEncoded.length%256);put(A(5),Math.floor(trainEncoded.length/256));
for(const [i,item]of trainEncoded.entries()){
 put(A(3000+2*i),item.context);
 put(A(3001+2*i),item.label);
}
stage.push('halt');
fs.writeFileSync(stagePath,stage.join('\n')+'\n');
native(['run',stagePath,model,staged]);
const learned=execute(path.join(src,'train-batch.xi'),staged,trained);
assert.deepEqual(learned,[800,800],'All 800 labels processed natively in XI');
const learnedCells=cells(trained);
assert.equal(readNumber(learnedCells,A(4),1),0);
assert.equal(readNumber(learnedCells,A(5),1),0);
for(let i=0;i<trainEncoded.length*2;i++)assert.equal(readNumber(learnedCells,A(3000+i),1),0,'Batch staging must be cleared');
let sum=0;for(let c=0;c<144;c++)for(let a=0;a<4;a++)sum+=readNumber(learnedCells,A(100+2*(4*c+a)),2);
assert.equal(sum,800,'Actual XI counters, not host-side inferred weights');
const baseline=new Map();
for(const item of trainEncoded){
 const n=baseline.get(item.old_context)||[0,0,0,0];n[item.label]++;baseline.set(item.old_context,n);
}
const stageInference=path.join(out,'infer-frame.xi'),temp=path.join(out,'infer-framed.rvp'),after=path.join(out,'infer-result.rvp');
const beforeHash=sha(fs.readFileSync(trained));
let correct=0,coarseCorrect=0,defaultCorrect=0,abstained=0,confusion=Array.from({length:4},()=>[0,0,0,0]);
const byLabel=Array.from({length:4},()=>({correct:0,total:0,abstained:0,coarse_correct:0}));
const observations=[],sampledCues={};
for(const item of holdoutEncoded){
 fs.writeFileSync(stageInference,'#!reverse-pc-machine-v1\nstore8 '+A(1)+' '+item.context+'\nhalt\n');
 native(['run',stageInference,trained,temp]);
 const decision=execute(path.join(src,'decide.xi'),temp,after);
 if(decision.length!==6||decision[0]!==item.context||
    decision[1]<0||decision[1]>3||decision[2]<0||decision[3]<0||
    ![0,1].includes(decision[4])||decision[5]<0||decision[5]>100)
   throw Error('Invalid XI prediction '+item.id+': '+JSON.stringify(decision));
 const predicted=decision[1],admitted=decision[4]===1;
 const counts=baseline.get(item.old_context)||[0,0,0,0];
 const max=Math.max(...counts),coarse=counts.indexOf(max);
 const success=predicted===item.label;
 if(success)correct++;
 if(coarse===item.label)coarseCorrect++;
 if(item.label===0)defaultCorrect++;
 if(!admitted)abstained++;
 const label=byLabel[item.label];label.total++;if(success)label.correct++;if(!admitted)label.abstained++;
 if(coarse===item.label)label.coarse_correct++;
 confusion[item.label][predicted]++;
 const key=item.intent+':'+item.semantic;sampledCues[key]=(sampledCues[key]||0)+1;
 observations.push({id:item.id,expected:item.label,predicted,admitted,context:item.context,
  p01:item.intent,semantic:item.semantic,support:decision[3],purity_pct:decision[5],
  coarse_baseline:coarse,correct:success});
}
// Native XI inference must never alter the trained model.
assert.equal(sha(fs.readFileSync(trained)),beforeHash,'Read-only predictions preserve original XI weights');
// Safety controls intentionally withheld from the supervised corpus.
const guards=[
 {text:'Recuerda que mañana revisaré Aurora.',safe:true,reason:'explicit teaching'},
 {text:'Escribe y ejecuta un programa para Aurora.',safe:true,reason:'multiple conflicting cues'},
 {text:'Escribe un cuento de razonamiento lógico sobre Aurora.',safe:true,reason:'ambiguous creative+logic'},
 {text:'Explica el funcionamiento de tu memoria.',safe:true,reason:'not a memory recall'}
];
for(const guard of guards){
 const f=features(guard.text);
 fs.writeFileSync(stageInference,'#!reverse-pc-machine-v1\nstore8 '+A(1)+' '+f.context+'\nhalt\n');
 native(['run',stageInference,trained,temp]);
 const d=execute(path.join(src,'decide.xi'),temp,after);
 assert.equal(d[1],0,'Unsafe/ambiguous instructions must abstain to legacy: '+guard.text);
 assert.equal(d[4],0,'Guard must not admit uncertain route: '+guard.text);
}
const invalidPath=path.join(out,'invalid-frame.xi'),badState=path.join(out,'bad-staged.rvp'),badOut=path.join(out,'invalid-output.rvp');
fs.writeFileSync(invalidPath,'#!reverse-pc-machine-v1\nstore8 '+A(4)+' 1\nstore8 '+A(3000)+' 0\nstore8 '+A(3001)+' 4\nhalt\n');
native(['run',invalidPath,model,badState]);
const reject=spawnSync(runtime,['run',path.join(src,'train-batch.xi'),badState,badOut],{encoding:'utf8',timeout:60000});
assert.notEqual(reject.status,0,'Invalid supervised labels must abort in XI');
assert.equal(sha(fs.readFileSync(trained)),beforeHash,'Adversarial malformed training never changes trained checkpoint');
const rate=n=>Math.round(10000*n/holdoutEncoded.length)/100;
const report={
 ok:true,cycle:'C14',kind:'synthetic_route_classification_only',
 notes:['No real-world conversation quality measured','No actual automatic X10 route execution','No external LLM/ML model; all semantic features and supervised weights are native XI','Coarse baseline is supervised P01 intent only, not actual X10 response quality'],
 corpus:meta,
 model:{engine:'native XI',context_count:144,semantic_classes:8,routes:4,stage_records_cleared:true,
  train_examples:trainEncoded.length,weights_counter_sum:sum,sha256:beforeHash,
  feature_runtime_ms:durationFeatures},
 holdout:{total:holdoutEncoded.length,correct,accuracy_percent:rate(correct),
  abstained,abstained_percent:rate(abstained),selective_accuracy_percent:
  Math.round(10000*(correct-observations.filter(x=>!x.admitted&&x.correct).length)/
  Math.max(1,holdoutEncoded.length-abstained))/100,
  confusion,by_label:byLabel},
 baselines:{p01_only_supervised_accuracy_percent:rate(coarseCorrect),
  constant_x10_route_accuracy_percent:rate(defaultCorrect),
  p01_only_correct:coarseCorrect,constant_x10_correct:defaultCorrect},
 safety:{guarded_cases:guards.length,blocked:true,malformed_label_rejected:true,sha_unchanged:true},
 observed_contexts:Object.keys(sampledCues).length,
 withheld_examples:observations
};
fs.writeFileSync(path.join(out,'report.json'),JSON.stringify(report,null,2)+'\n');
fs.writeFileSync(path.join(out,'corpus-manifest.json'),JSON.stringify(meta,null,2)+'\n');
console.log(JSON.stringify({ok:true,training:meta.training,holdout:meta.holdout,
 accuracy:report.holdout.accuracy_percent,p01_baseline:report.baselines.p01_only_supervised_accuracy_percent,
 abstained_pct:report.holdout.abstained_percent,guarded:report.safety.blocked,
 xi_count:sum,sha256:beforeHash,features_ms:durationFeatures}));
