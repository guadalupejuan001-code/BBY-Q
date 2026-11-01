// C14 native XI supervised policy observation inside genuine X10 turns.
// NEVER changes the chosen response, route, old C12 weights, or lesson banks.
// Every semantic feature and the 800-example learned checkpoint is native XI.
import fs from 'node:fs';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {NativePages,run,fail} from '../../ai/personal/x10/pages.mjs';
import {history} from '../../ai/personal/p05/store.mjs';

const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'../..');
const engine=path.join(root,'ai/xi/cognitive14');
const F=8270000000000000000n;
const actions=['X10 original','P05 memoria','P03 razonamiento','P04 composición'];
const prints=events=>events.split('\n').filter(s=>s.startsWith('{'))
 .map(s=>JSON.parse(s)).filter(x=>x.type==='register').map(x=>x.value);
function frame(file,writes){
 fs.writeFileSync(file,'#!reverse-pc-machine-v1\n'+
  writes.map(([address,value])=>{
   if(!Number.isInteger(value)||value<0||value>255)
    throw fail('E_C14_FRAME','Campo de configuración XI fuera de rango.');
   return 'store8 '+address+' '+value;
  }).join('\n')+'\nhalt\n',{mode:0o600});
 return file;
}
export function c14Shadow(db,{runtime,roles,job,raw}){
 const base={engine:'C14 native XI supervised routing',mode:'shadow',applied:false,
  trained_examples:800,holdout_examples:200,synthetic_training:true,
  real_dialogue_quality_validated:false,
  source_model_sha256:'aa182b00b5748bbf647f671c48175316253cae45904c997782a04474333fe3f0'};
 if(raw.length>190)
  return {...base,available:false,reason:'La extracción P01 XI admite hasta 190 bytes por mensaje.'};
 const dir=path.join(job,'c14-isolated');fs.mkdirSync(dir,{recursive:true,mode:0o700});
 const pages=new NativePages(runtime,roles,path.join(dir,'frames'));
 pages.validate(raw);
 let memoryReference=false,historyMode=0;
 if(roles['context.rxe']){
  const rows=history(db),selection=pages.context(raw,rows.map(row=>row.utterance));
  historyMode=selection.mode;
  memoryReference=[1,2,5,9].includes(selection.mode);
 }
 const intent=pages.intent(raw);
 const configured=frame(path.join(dir,'features-frame.xi'),[[F+17n,Number(memoryReference)]]);
 run(runtime,['run',configured,pages.state,pages.state]);
 const feature=prints(run(runtime,['run',path.join(engine,'features.xi'),pages.state,pages.state]));
 if(feature.length!==3||feature[0]!==intent.id||feature[1]<0||feature[1]>7||
    feature[2]<0||feature[2]>=144)throw fail('E_C14_FEATURE','La clasificación XI es incompatible.');
 const init=path.join(dir,'blank.rvp'),born=path.join(dir,'born.rvp'),
  trained=path.join(dir,'trained.rvp'),staged=path.join(dir,'staged.rvp'),inferred=path.join(dir,'inferred.rvp');
 run(runtime,['init',init]);
 run(runtime,['run',path.join(engine,'birth.xi'),init,born]);
 const seeded=prints(run(runtime,['run',path.join(engine,'supervised-seed.xi'),born,trained]));
 if(seeded.length!==1||seeded[0]!==800)throw fail('E_C14_SEED','Pesos supervisados XI no restaurados.');
 const context=feature[2];
 run(runtime,['run',frame(path.join(dir,'context-frame.xi'),[[F+1n,context]]),trained,staged]);
 const selected=prints(run(runtime,['run',path.join(engine,'decide.xi'),staged,inferred]));
 if(selected.length!==6||selected[0]!==context||selected[1]<0||selected[1]>3||
    selected[2]<0||selected[3]<0||![0,1].includes(selected[4])||
    selected[5]<0||selected[5]>100)
  throw fail('E_C14_RESULT','Resultado de decisión XI incompatible.');
 return {...base,available:true,context,p01_intent:intent.name,
  memory_reference:memoryReference,history_mode:historyMode,
  semantic_class:feature[1],suggested_action:selected[1],
  suggested_route:actions[selected[1]],abstained:selected[4]!==1,
  support:selected[3],training_purity_percent:selected[5],
  note:'Purity is synthetic routing agreement, not calibrated confidence or reply correctness'};
}
