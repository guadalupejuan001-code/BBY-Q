// Build-time grammar generation only. All mobile command decisions run in XI.
import fs from 'node:fs';
import path from 'node:path';
import {execFileSync} from 'node:child_process';
import {validatorSource,routerSource,recordSource,streamSource} from '../../ai/personal/x10/native.mjs';
import {intentSource} from '../../ai/personal/p01/intent.mjs';
import {reasonSource} from '../../ai/personal/p03/reason.mjs';
import {composeSource} from '../../ai/personal/p04/compose.mjs';
import {contextSource} from '../../ai/personal/p05/context.mjs';
import {paraphraseSource} from '../../ai/personal/p06/paraphrase.mjs';
const root=path.resolve(import.meta.dirname,'../..'),dest=path.join(root,'android-personal/app/src/main/assets/engine');
const runtime=path.join(root,'deps/reverse-pc/build/reverse_pc');
fs.mkdirSync(dest,{recursive:true});
const B=9190000000000000000n,I=B+4096n,R=B+512n;
function qchatContextSource(){
 // Inputs use the same lowercase/accent-folded byte codec as QChat100.
 // Only the curriculum's follow-up forms consume the generator's own context.
 const lines=['#!reverse-pc-machine-v1',`store8 ${B+516n} 0`];
 const w=(...x)=>lines.push(...x),L=x=>w('label '+x);
 for(const [index,cue]of ['explicalo otra vez','dime mas','repitelo','cuentalo otra vez'].entries()){
  const bytes=Buffer.from(cue),miss='qc_miss_'+index,tail='qc_tail_'+index,ok='qc_ok_'+index;
  w(`load8 r1 ${B+8n}`,`load8 r2 ${B+9n}`,'mul r2 256','add r1 r2','cmp r1 '+bytes.length,'jlt '+miss);
  for(const[i,b]of bytes.entries())w(`load8 r0 ${I+BigInt(i)}`,'cmp r0 '+b,'jne '+miss);
  w('set r2 '+bytes.length);L(tail);w('cmp r2 r1','jge '+ok,`set r7 ${I}`,'add r7 r2','load8 r0 $r7');
  for(const b of [32,46,33,63])w('cmp r0 '+b,'je '+tail+'_next');
  w('jmp '+miss);L(tail+'_next');w('add r2 1','jmp '+tail);L(ok);w(`store8 ${B+516n} 1`,'halt');L(miss);
 }
 w('halt');return lines.join('\n')+'\n';
}
function mobileRouteSource(){
 const lines=['#!reverse-pc-machine-v1',`store8 ${R} 0`];let id=0;
 const w=(...x)=>lines.push(...x),L=x=>w('label '+x);
 const routes=[['memoria guarda ',1],['memoria corrige ',2],['memoria consulta ',3],['memoria estado',4],['qchat ',5],['mision ',6],['evaluar ',7]];
 for(const [prefix,op]of routes){const bytes=Buffer.from(prefix),miss='miss_'+id++;
  for(const[i,b]of bytes.entries()){const fold='fold_'+id++;w(`load8 r0 ${I+BigInt(i)}`,'cmp r0 65','jlt '+fold,'cmp r0 90','jgt '+fold,'add r0 32');L(fold);w('cmp r0 '+b,'jne '+miss);}
  w(`store8 ${R} ${op}`,`store8 ${R+1n} ${bytes.length}`,'jmp '+(op>=6?'entity':op===4?'exact':op===5?'qchat':'key'));L(miss);
 }
 w('halt');L('exact');w(`load8 r0 ${B+12n}`,'cmp r0 14','jne bad');for(let i=1;i<4;i++)w(`load8 r0 ${B+12n+BigInt(i)}`,'cmp r0 0','jne bad');w('halt');
 L('qchat');w(`load8 r0 ${B+12n}`,`load8 r1 ${B+13n}`,'mul r1 256','add r0 r1','cmp r0 518','jgt bad');for(let i=2;i<4;i++)w(`load8 r1 ${B+12n+BigInt(i)}`,'cmp r1 0','jne bad');w(`load8 r1 ${R+1n}`,'cmp r0 r1','jle bad','halt');
 L('entity');w(`load8 r0 ${B+14n}`,'cmp r0 4','jgt bad',`load8 r0 ${B+15n}`,'cmp r0 0','jne bad','halt');
 L('key');w(`load8 r0 ${B+8n}`,`load8 r1 ${B+9n}`,'mul r1 256','add r0 r1',`load8 r2 ${R+1n}`,'mov r3 r0','sub r3 r2','cmp r3 1','jlt bad','cmp r3 66','jgt bad',`load8 r1 ${R}`,'cmp r1 3','je key_size','sub r0 1',`set r7 ${I}`,'add r7 r0','load8 r4 $r7','cmp r4 48','jlt bad','cmp r4 49','jgt bad','sub r4 48',`store8 ${R+3n} r4`,'sub r0 1','sub r7 1','load8 r4 $r7','cmp r4 32','jne bad');
 L('key_size');w('sub r0 r2','cmp r0 1','jlt bad','cmp r0 64','jgt bad',`store8 ${R+2n} r0`,'set r3 0');
 L('copy');w('cmp r3 r0','jge done',`set r7 ${I}`,'add r7 r2','add r7 r3','load8 r4 $r7',`set r7 ${R+32n}`,'add r7 r3','store8 $r7 r4','add r3 1','jmp copy');L('done');w('halt');L('bad');w(`store8 ${R} 254`,'halt');return lines.join('\n')+'\n';
}
const roles={validate:validatorSource(),route:routerSource(),record:recordSource(),stream:streamSource(),intent:intentSource(),reason:reasonSource(),compose:composeSource(),context:contextSource(),paraphrase:paraphraseSource(),'mobile-route':mobileRouteSource(),'qchat-context':qchatContextSource(),'v3-route':fs.readFileSync(path.join(root,'ai/xi/quantum3/conversation-route.xi'),'utf8')};
for(const [name,source]of Object.entries(roles)){
 const file=path.join(dest,name+'.xi');fs.writeFileSync(file,source);
 execFileSync(runtime,['compile',file,path.join(dest,name+'.rxe'),'BBY Q Android X10 '+name]);
}
console.log(JSON.stringify({ok:true,native_roles:Object.keys(roles)}));
