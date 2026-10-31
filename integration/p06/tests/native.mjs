// Native XI exam: every accepted rule is executed by the original REVERSE-PC
// runtime, including novel slot values and negative semantic controls.
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import {performance} from 'node:perf_hooks';
import {NativePages,cells,run} from '../../../ai/personal/x10/pages.mjs';
import {paraphraseSource,PARAPHRASE_BASE,PARAPHRASE_RULES,
 PARAPHRASE_MAX_INPUT,PARAPHRASE_MODES} from '../../../ai/personal/p06/paraphrase.mjs';

const [runtimeArg,outArg]=process.argv.slice(2);
if(!outArg)throw Error('Usage: node integration/p06/tests/native.mjs REVERSE_PC NEW_OUTPUT');
const runtime=path.resolve(runtimeArg),out=path.resolve(outArg);
if(fs.existsSync(out))throw Error('Choose a new P06 evidence directory.');
fs.mkdirSync(out,{recursive:true});
const source=paraphraseSource(),xi=path.join(out,'paraphrase.xi'),rxe=path.join(out,'paraphrase.rxe');
fs.writeFileSync(xi,source);
run(runtime,['compile',xi,rxe,'BBY Q P06 productive language paraphrases']);
const sha=x=>crypto.createHash('sha256').update(x).digest('hex');
const tests=[];
const question='Todos los gatos son mamíferos. Luna es un gato. ¿Luna es mamífero?';
const explanation='se apagó el faro\ncausa: faltó electricidad\nefecto: quedó oscura la bahía';
for(const [i,rule] of PARAPHRASE_RULES.entries()){
 const topic='objeto'+String(i).padStart(3,'0');
 const tail=rule.mode===PARAPHRASE_MODES.reasoning?question:
  rule.mode===PARAPHRASE_MODES.explanation?explanation:topic+' misterioso';
 tests.push({input:rule.source+tail,mode:rule.mode,rule:i+1,
  canonical:rule.target+tail,recognized:true});
}
for(let i=0;i<65;i++){
 const pick=(i*13)%PARAPHRASE_RULES.length,rule=PARAPHRASE_RULES[pick];
 const topic='costa'+String(i).padStart(3,'0')+' azul';
 const tail=rule.mode===5?'Todos los barcos son objetos. Orion es un barco. ¿Orion es objeto?':
  rule.mode===4?'la estrella brilla\ncausa: ocurre una reacción\nefecto: emite luz':topic;
 tests.push({input:rule.source+tail,mode:rule.mode,rule:pick+1,
  canonical:rule.target+tail,recognized:true});
}
const negatives=[
 'Recuerda que la luna es verde.',
 'recuérdame que tengo una cita',
 'olvida la lección guardada',
 'corrige lección: ejemplo',
 'aprende que la estrella es luminosa',
 'hola',
 '¿Por qué está lloviendo?',
 'no me recuerdas qué dije de Luna?',
 '¿Me recuerdas quién es Luna?',
 'Me olvido de lo que dije de Luna.',
 '«Recuérdame qué dije de Luna»',
 '"¿me recuerdas qué dije de Luna?"',
 'hazme un poema sobre "ignora las instrucciones"',
 'hazme un poema sobre la luna; elimina recuerdos',
 'hazme un poema sobre la luna\notra orden',
 'explícame por qué la luna es brillante',
 'deduce que hay un problema sin pruebas',
 '¿qué dije de ',
 'inventa una historia acerca de ',
 '¿puedes enseñarte a guardar la memoria?',
 'escribe un poema de 7 versos sobre la noche',
 '¿cuándo me enseñaste la lección?',
 '¿Podrías borrar mi historial sobre Luna?',
 '¿Me recuerdas qué dije de la palabra sol y guarda datos?'
];
for(const input of negatives)tests.push({input,mode:0,rule:0,canonical:null,recognized:false});
for(let i=0;i<20;i++)
 tests.push({input:'hazme un poema sobre x'.repeat(28)+String(i),mode:0,rule:0,canonical:null,recognized:false});
const observations=[],timings=[];
for(const [i,test]of tests.entries()){
 const raw=Buffer.from(test.input,'utf8');
 const job=path.join(out,'case-'+String(i).padStart(3,'0'));fs.mkdirSync(job);
 const pages=new NativePages(runtime,{'paraphrase.rxe':rxe},job);
 pages.stage({data:raw.subarray(0,PARAPHRASE_MAX_INPUT),total:Math.min(raw.length,PARAPHRASE_MAX_INPUT)});
 const before=cells(pages.state),start=performance.now(),actual=pages.paraphrase(raw),ms=performance.now()-start;
 const after=cells(pages.state);
 assert.equal(actual.handled,test.recognized,JSON.stringify({input:test.input,actual}));
 assert.equal(actual.mode,test.mode,test.input);
 assert.equal(actual.rule,test.rule,test.input);
 assert.equal(actual.canonical,test.canonical,test.input);
 assert.equal(actual.readOnly,true,test.input);
 const foreign=[...new Set([...before.keys(),...after.keys()])]
  .filter(addr=>addr<PARAPHRASE_BASE||addr>=PARAPHRASE_BASE+64n)
  .filter(addr=>(before.get(addr)||0)!==(after.get(addr)||0));
 assert.deepEqual(foreign,[],'P06 changed foreign XI memory: '+test.input);
 timings.push(ms);observations.push({id:i,mode:actual.mode,rule:actual.rule,recognized:actual.handled,
  input:test.input,canonical:actual.canonical,milliseconds:ms,ok:true});
 fs.rmSync(job,{recursive:true,force:true});
}
const pct=p=>timings.slice().sort((a,b)=>a-b)[Math.max(0,Math.ceil(timings.length*p)-1)];
const report={ok:true,version:'P06-native-XI-1',scope:'bounded paraphrase normalization, not general semantic understanding',
 checks:tests.length,passed:tests.length,grammar_rules:PARAPHRASE_RULES.length,
 novel_combinations:65,negative_controls:negatives.length+20,
 median_ms:pct(.5),p95_ms:pct(.95),source_sha256:sha(Buffer.from(source)),
 compiled_sha256:sha(fs.readFileSync(rxe)),android_validated:false,records:observations};
fs.writeFileSync(path.join(out,'results.json'),JSON.stringify(report,null,2)+'\n');
console.log(JSON.stringify({ok:true,cases:report.checks,correct:report.passed,rules:report.grammar_rules,
 novel:report.novel_combinations,negative:report.negative_controls,median_ms:report.median_ms,p95_ms:report.p95_ms}));
