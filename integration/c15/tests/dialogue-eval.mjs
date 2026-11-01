// Empirical C15 dialogue probes with real X10 native XI roles and bounded
// independent answer oracles. This is NOT a real-world sampled corpus, not
// a professional human evaluation, and NOT the owner's recovered X09 model.
import fs from 'node:fs';
import path from 'node:path';
import zlib from 'node:zlib';
import crypto from 'node:crypto';
import assert from 'node:assert/strict';
import {spawnSync} from 'node:child_process';
import {DatabaseSync} from 'node:sqlite';
import {fileURLToPath} from 'node:url';
import {transact,inspect} from '../../ai/personal/x10/session.mjs';
import {VERSION} from '../../ai/personal/x10/schema.mjs';

const [runtimeArg,outArg]=process.argv.slice(2);
if(!runtimeArg||!outArg)throw Error('Usage: dialogue-eval.mjs /path/reverse_pc FRESH_EVIDENCE_DIR');
const runtime=path.resolve(runtimeArg),out=path.resolve(outArg);
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'../..');
if(fs.existsSync(out))throw Error('Provide a new directory for evidence.');
fs.mkdirSync(out,{recursive:true});
const fixture=path.join(out,'verified-fixture');
const boot=spawnSync(process.execPath,[path.join(root,'integration/qml_qrl/tests/native-chat.mjs'),runtime,fixture],
 {encoding:'utf8',timeout:160000,maxBuffer:16*1024*1024});
if(boot.status!==0)throw Error('Original X10 fixture integration failed: '+(boot.stderr||boot.stdout||boot.error?.message));
const built=path.join(fixture,'build'),base=path.join(built,'native');
const fixtureResult=JSON.parse(fs.readFileSync(path.join(fixture,'results.json')));
assert.equal(fixtureResult.ok,true);
const digest=bytes=>crypto.createHash('sha256').update(bytes).digest('hex');
const prefix='SYNTHETIC-X09-TRAINING-NOT-PRESENT';
let sessionCount=0;
function cleanSession(label){
 const dest=path.join(out,'sessions',String(sessionCount++).padStart(3,'0')+'-'+label);
 fs.mkdirSync(dest,{recursive:true});
 const db=new DatabaseSync(path.join(dest,'memory.sqlite'));
 db.exec('PRAGMA synchronous=FULL;'+
  'CREATE TABLE metadata(key TEXT PRIMARY KEY,value TEXT NOT NULL) STRICT;'+
  'CREATE TABLE state(id INTEGER PRIMARY KEY CHECK(id=1),data BLOB NOT NULL,digest TEXT NOT NULL) STRICT;'+
  'CREATE TABLE receipts(id TEXT PRIMARY KEY,digest TEXT NOT NULL,generation INTEGER NOT NULL,result BLOB NOT NULL) STRICT;'+
  'CREATE TABLE relational_state(id INTEGER PRIMARY KEY CHECK(id=1),data BLOB NOT NULL,digest TEXT NOT NULL) STRICT;');
 for(const [key,value]of Object.entries({
   version:VERSION,generation:'0',operations:'0',count:'0',revision:'0',source_sha256:'synthetic'}))
  db.prepare('INSERT INTO metadata VALUES(?,?)').run(key,value);
 const state=Buffer.from(prefix),relational=Buffer.from('P02-E034-PRESERVED');
 db.prepare('INSERT INTO state VALUES(1,?,?)').run(zlib.deflateRawSync(state),digest(state));
 db.prepare('INSERT INTO relational_state VALUES(1,?,?)').run(relational,digest(relational));
 db.close();
 return dest;
}
const tasks=[
 {id:'poem-comet',group:'creative',kind:'poem',text:'haz un poema de tres versos sobre un cometa.',topic:'cometa',units:3,expectedRoute:3},
 {id:'poem-compass',group:'creative',kind:'poem',text:'crea un poema de cuatro versos sobre una brújula.',topic:'brújula',units:4,expectedRoute:3},
 {id:'story-lighthouse',group:'creative',kind:'story',text:'escribe un cuento de tres frases sobre el faro.',topic:'faro',units:3,expectedRoute:3},
 {id:'story-clock',group:'creative',kind:'story',text:'inventa una historia sobre un reloj.',topic:'reloj',units:3,expectedRoute:3},
 {id:'proof-engine',group:'reasoning',kind:'proof',text:'Todos los motores son máquinas. Delta es un motor. ¿Delta es máquina?',mode:1,pattern:/delta -> motor -> maquinas/i,expectedRoute:2},
 {id:'proof-cat',group:'reasoning',kind:'proof',text:'Todos los gatos son mamíferos. Roco es un gato. ¿Roco es mamífero?',mode:1,pattern:/roco -> gato -> mamiferos/i,expectedRoute:2},
 {id:'proof-order',group:'reasoning',kind:'proof',text:'X es mayor que Y. Y es mayor que Z. ¿X es mayor que Z?',mode:1,pattern:/x -> y -> z/i,expectedRoute:2},
 {id:'proof-denial',group:'reasoning',kind:'proof',text:'Vega no es gato. ¿Vega es gato?',mode:4,pattern:/niega expresamente/i,expectedRoute:2},
 {id:'memory-vega',group:'memory',kind:'recall',seed:'Vega es un satélite.',text:'¿Qué dije de Vega?',expectedRoute:1},
 {id:'memory-nube',group:'memory',kind:'recall',seed:'Nube tiene un telescopio.',text:'¿Qué dije sobre Nube?',expectedRoute:1},
 {id:'memory-titan',group:'memory',kind:'recall',seed:'Titan es un robot.',text:'¿Qué dije sobre Titan?',expectedRoute:1},
 {id:'memory-negative',group:'memory',kind:'abstain',seed:'Anabel es astronauta.',text:'¿Qué dije de Ana?',expectedRoute:1}
];
const routeModules=[{key:'automatic',module:undefined},{key:'memory',module:'p05'},
 {key:'reasoning',module:'p03'},{key:'creative',module:'p04'}];
const now=()=>performance.now();
function call(session,id,message,options={}){
 const started=now(),result=transact(runtime,base,session,id,message,options);
 return {result,elapsed_ms:Math.round(100*(now()-started))/100};
}
const actualAction=result=>{
 const ext=result?.extension;
 if(ext==='P05-context-XI')return 1;
 if(ext==='P03-native-XI')return 2;
 if(ext==='P04-native-XI')return 3;
 if(ext==='X10-paged-lessons'||ext==='X10-streamed-text'||ext==='X09-preserved')return 0;
 return null;
};
function oracle(test,r){
 const criteria={returned_success:r?.ok===true};
 if(!criteria.returned_success)return {pass:false,criteria,error:r?.error||null};
 const answer=r.response||'';
 const folded=answer.toLocaleLowerCase('es');
 if(test.kind==='poem'){
  const lines=answer.trim().split('\n');
  criteria.real_composition=r.extension==='P04-native-XI'&&r.composition_mode===1;
  criteria.requested_verses=r.composition_units===test.units&&lines.length===test.units;
  criteria.topic_present=folded.includes(test.topic.toLocaleLowerCase('es'));
  criteria.complete_lines=lines.every(line=>line.trim().endsWith('.'));
 }else if(test.kind==='story'){
  criteria.real_composition=r.extension==='P04-native-XI'&&r.composition_mode===2;
  criteria.requested_sentences=r.composition_units===test.units&&
    (answer.match(/\./g)||[]).length===test.units;
  criteria.topic_present=folded.includes(test.topic.toLocaleLowerCase('es'));
 }else if(test.kind==='proof'){
  criteria.native_reasoning=r.extension==='P03-native-XI'&&r.reasoning_mode===test.mode;
  criteria.proof_matches=Boolean(test.pattern.test(answer));
  criteria.no_unparsed_fragments=r.reasoning_unparsed===0;
 }else if(test.kind==='recall'){
  criteria.native_memory=r.extension==='P05-context-XI'&&r.context_mode===1;
  criteria.real_reference=r.context_resolved===true&&answer.includes(test.seed);
  criteria.known_turn_provenance=/En el turno \d+/.test(answer);
 }else if(test.kind==='abstain'){
  criteria.native_memory=r.extension==='P05-context-XI'&&r.context_mode===3;
  criteria.no_fabricated_recall=/No encontré/.test(answer)&&
    !/En el turno \d+/.test(answer);
 }else throw Error('Unknown evaluation rubric');
 return {pass:Object.values(criteria).every(Boolean),criteria};
}
const results=[],beforeAll=inspect(cleanSession('control-initial'));
for(const test of tasks){
 const routes=[];
 for(const {key,module} of routeModules){
  const sess=cleanSession(test.id+'-'+key);
  const before=inspect(sess);
  if(test.seed){
   const seeded=call(sess,'seed',test.seed,{module:'p05'});
   if(!seeded.result.ok)throw Error('Cannot establish P05 conversational context: '+JSON.stringify(seeded.result.error));
  }
  const evaluated=call(sess,'evaluate',test.text,{
   ...(module?{module}:{}),
   ...(key==='automatic'?{shadowC15:true}:{})
  });
  const graded=oracle(test,evaluated.result);
  const after=inspect(sess);
  assert.equal(after.state_sha256,before.state_sha256,'X09 synthetic main state changed on read-only dialogue: '+test.id);
  const reward=graded.pass?100:0;
  routes.push({route:key,requested_module:module??'automatic',ok:evaluated.result.ok,
   extension:evaluated.result.extension??null,actual_route:actualAction(evaluated.result),
   response:evaluated.result.response??null,error:evaluated.result.error??null,
   oracle:graded,reward_proxy:reward,elapsed_ms:evaluated.elapsed_ms,
   shadow:key==='automatic'?evaluated.result.c15_shadow??null:undefined});
 }
 const auto=routes[0],desired=routes.find(x=>x.actual_route===test.expectedRoute&&x.route!=='automatic'&&x.oracle.pass);
 results.push({id:test.id,category:test.group,kind:test.kind,request:test.text,seed:test.seed??null,
  intended_executable_route:test.expectedRoute,automatic_pass:auto.oracle.pass,
  best_route_pass:Boolean(desired),c15_suggested_route:auto.shadow?.suggested_action??null,
  c15_eligible:auto.shadow?.admitted??false,notes:[],
  routes});
}
// Learning on actually observed poem responses; never train on the withheld 12.
const learned=cleanSession('reward-learning');
const beforeLearn=inspect(learned);
const heldout=tasks[0];
const start=call(learned,'heldout-before',heldout.text,{module:'p04',shadowC15:true});
assert.equal(start.result.ok,true,'heldout pre-reward response missing');
const oldSuggestion=start.result.c15_shadow;
const calibrations=[
 {id:'desierto',text:'escribe un poema sobre el desierto.',topic:'desierto',units:4,kind:'poem'},
 {id:'ceniza',text:'escribe un poema sobre la ceniza.',topic:'ceniza',units:4,kind:'poem'},
 {id:'cascada',text:'escribe un poema sobre la cascada.',topic:'cascada',units:4,kind:'poem'}
];
const episodes=[];
for(const [i,item]of calibrations.entries()){
 for(const [k,module] of [['positive','p04'],['negative','p03']]){
  const requestId='training-'+i+'-'+k;
  const answered=call(learned,requestId,item.text,{module,shadowC15:true});
  assert.equal(answered.result.ok,true,JSON.stringify({requestId,error:answered.result.error}));
  const measured=oracle(item,answered.result);
  const objectiveReward=measured.pass?100:0;
  const rewarded=call(learned,'rating-'+i+'-'+k,'calificación',{module:'c15',
    rlFeedback:{targetId:requestId,reward:objectiveReward}});
  assert.equal(rewarded.result.ok,true,JSON.stringify({requestId,error:rewarded.result.error}));
  assert.equal(rewarded.result.c15_training.trained_action,module==='p04'?3:2);
  episodes.push({requestId,module,actual_extension:answered.result.extension,
   response:answered.result.response,objective_reward:objectiveReward,
   rubric:measured,rewarded_q:rewarded.result.c15_training.q_value_q10000,
   total_feedback:rewarded.result.c15_training.total_feedback});
 }
}
const end=call(learned,'heldout-after',heldout.text,{module:'p04',shadowC15:true});
assert.equal(end.result.ok,true,'heldout post-reward response missing');
const afterLearn=inspect(learned);
assert.equal(afterLearn.state_sha256,beforeLearn.state_sha256,'Training changed original X09');
assert.equal(afterLearn.c15_feedback_events,6,'Missing outcome feedback events');
assert.equal(afterLearn.c15_policy_sha256?.length,64,'Missing persistent XI model');
assert.equal(end.result.c15_shadow?.applied,false,'Proposed path was incorrectly applied');
const beforeOracle=oracle(heldout,start.result),afterOracle=oracle(heldout,end.result);
const qualityGain=Number(afterOracle.pass)-Number(beforeOracle.pass);
const report={
 ok:true,scope:'native-XI execution, manually authored bounded Spanish test prompts',
 limitations:[
  'The X09 release and its 480 real historical lessons are NOT present in this synthetic fixture.',
  '12 human-authored prompts; none were collected from real user conversations. This is not a statistical generalization guarantee.',
  'Creative rubrics inspect structure/topic, not literary quality or social usefulness.',
  'Feedback comes from an explicit deterministic test oracle, NOT real human ratings.',
  'Q-learning here is a one-step classical terminal reward update written in XI, not the quantum Bell QRL2 agent.',
  'C15 was never allowed to choose a route automatically; improvements in live reply quality cannot be concluded.'
 ],
 seed_sha256:beforeAll.state_sha256,
 fixture_previous_integration:{checks:fixtureResult.checks,turns:fixtureResult.conversational_turns},
 sample_size:tasks.length,domain_count:3,
 routes_tested:routeModules.map(x=>x.key),
 metric_definition:'fraction of responses satisfying task-specific exact, limited observables',
 route_scores:routeModules.map(({key})=>{
  const rows=results.map(x=>x.routes.find(r=>r.route===key));
  return {route:key,pass:rows.filter(r=>r.oracle.pass).length,total:rows.length};
 }),
 c15_prior:{
  proposal_matches_intended:results.filter(x=>x.c15_suggested_route===x.intended_executable_route).length,
  admitted:results.filter(x=>x.c15_eligible).length,
  total:results.length,
  note:'Recommendations are observed, never executed'
 },
 learning_probe:{
  calibration_cases:calibrations.length,reward_events:episodes.length,
  heldout_request:heldout.text,prior_source:oldSuggestion?.source,
  after_source:end.result.c15_shadow?.source,
  before_proposal:oldSuggestion?.suggested_action,after_proposal:end.result.c15_shadow?.suggested_action,
  before_answer:start.result.response,after_answer:end.result.response,
  before_rubric:beforeOracle,after_rubric:afterOracle,quality_gain_on_heldout:qualityGain,
  answer_text_unchanged:start.result.response===end.result.response,
  policy_sha256:afterLearn.c15_policy_sha256,episodes
 },
 tasks:results
};
fs.writeFileSync(path.join(out,'dialogue-evaluation.json'),JSON.stringify(report,null,2)+'\n');
fs.writeFileSync(path.join(out,'summary.json'),JSON.stringify({
 ok:true,sample_size:report.sample_size,route_scores:report.route_scores,
 c15_prior:report.c15_prior,learning_probe:{
  calibration_cases:report.learning_probe.calibration_cases,
  reward_events:report.learning_probe.reward_events,
  prior_source:report.learning_probe.prior_source,
  after_source:report.learning_probe.after_source,
  before_proposal:report.learning_probe.before_proposal,
  after_proposal:report.learning_probe.after_proposal,
  quality_gain_on_heldout:report.learning_probe.quality_gain_on_heldout,
  answer_text_unchanged:report.learning_probe.answer_text_unchanged
 },scope:report.scope,limitations:report.limitations
},null,2)+'\n');
console.log(JSON.stringify(JSON.parse(fs.readFileSync(path.join(out,'summary.json'),'utf8'))));
