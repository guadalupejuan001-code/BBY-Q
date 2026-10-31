// Build a capacity extension around the unchanged, verified X09 training seed.
import fs from 'node:fs';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {prepare as prepareX09} from '../x09/prepare.mjs';
import {validatorSource,routerSource,recordSource,streamSource} from '../../ai/personal/x10/native.mjs';
import {intentSource} from '../../ai/personal/p01/intent.mjs';
import {reasonSource,REASON_SHA256} from '../../ai/personal/p03/reason.mjs';
import {composeSource,COMPOSE_MODES,COMPOSE_LIMIT} from '../../ai/personal/p04/compose.mjs';
import {contextSource,CONTEXT_MAX_CANDIDATES,CONTEXT_MAX_ENTRY_BYTES} from '../../ai/personal/p05/context.mjs';
import {paraphraseSource,PARAPHRASE_RULES,PARAPHRASE_MAX_INPUT} from '../../ai/personal/p06/paraphrase.mjs';
import {LIMITS,VERSION} from '../../ai/personal/x10/schema.mjs';
import {run,sha} from '../../ai/personal/x10/pages.mjs';

export function prepare(destination,{archive}={}){
 destination=path.resolve(destination);if(fs.existsSync(destination))throw Error('Choose a new build directory');
 const parent=path.dirname(destination);fs.mkdirSync(parent,{recursive:true});const staging=fs.mkdtempSync(path.join(parent,'.x10-build-'));
 try{
  const original=prepareX09(path.join(staging,'release'),{archive}),release=original.directory;
  const capacity=path.join(release,'capacity');fs.mkdirSync(capacity);
  const roles={};
  for(const[name,source]of [['validate',validatorSource()],['route',routerSource()],['record',recordSource()],['stream',streamSource()],['intent',intentSource()],['reason',reasonSource()],['compose',composeSource()],['context',contextSource()],['paraphrase',paraphraseSource()]]){
   const text=path.join(capacity,name+'.xi'),binary=path.join(capacity,name+'.rxe');fs.writeFileSync(text,source);run(original.runtime,['compile',text,binary,'BBY Q X10 '+name]);roles[name+'.xi']=sha(fs.readFileSync(text));roles[name+'.rxe']=sha(fs.readFileSync(binary));
  }
  const manifest={version:VERSION,parent:'X09-All-Training-1',runtime_sha256:sha(fs.readFileSync(original.runtime)),seed_sha256:original.model_sha256,limits:LIMITS,roles,storage:'SQLite opaque 640-byte Ether record pages; XI selects and changes records',long_text_operations:['exact echo','extractive summary'],legacy_input_bytes:16384,intent_gate:{stage:'P01',engine:'native XI',default:'read-only',checkpoint:'unchanged'},reasoning:{stage:'P03',mode:'native XI',scope:'bounded textual premises',read_only:true,source_sha256:REASON_SHA256},composition:{stage:'P04',engine:'native XI',kind:Object.keys(COMPOSE_MODES),input_limit_bytes:COMPOSE_LIMIT,read_only:true},conversation_context:{stage:'P05',engine:'native XI',recent_turns:CONTEXT_MAX_CANDIDATES,entry_bytes:CONTEXT_MAX_ENTRY_BYTES,storage:'bounded transactional SQLite index',not_training:true},language_generalization:{stage:'P06',engine:'native XI',grammatical_paraphrases:PARAPHRASE_RULES.length,input_bytes:PARAPHRASE_MAX_INPUT,mode:'read-only canonical forms'},original_training_preserved:true,android_validated:false};
  fs.writeFileSync(path.join(capacity,'build.json'),JSON.stringify(manifest,null,2)+'\n');
  fs.renameSync(release,destination);return {ok:true,version:VERSION,directory:destination,limits:LIMITS,seed_sha256:manifest.seed_sha256,original_training_preserved:true};
 }finally{fs.rmSync(staging,{recursive:true,force:true});}
}
if(process.argv[1]&&path.resolve(process.argv[1])===fileURLToPath(import.meta.url))console.log(JSON.stringify(prepare(process.argv[2],{archive:process.argv[3]})));
