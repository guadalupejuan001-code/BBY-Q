// P06: bounded productive paraphrases for P05 recall, P04 composition,
// grounded explanation and P03 deductive reasoning. Compiled into native XI.
// Node authors the grammar at build time; XI alone recognizes and rewrites.
import {B,INPUT,LENGTH} from '../x10/schema.mjs';

export const PARAPHRASE_BASE=B+262144n;
export const PARAPHRASE_MAX_INPUT=512;
export const PARAPHRASE_MAX_OUTPUT=768;
export const PARAPHRASE_MODES=Object.freeze({unsupported:0,recall:1,poem:2,story:3,explanation:4,reasoning:5});
const RULES=[];
const add=(source,target,mode)=>RULES.push(Object.freeze({source,target,mode}));
for(const [source,target] of [
 ['¿me recuerdas qué dije de ','¿Qué dije de '],
 ['¿me recuerdas qué dije sobre ','¿Qué dije sobre '],
 ['me recuerdas qué dije de ','¿Qué dije de '],
 ['me recuerdas qué dije sobre ','¿Qué dije sobre '],
 ['recuérdame qué dije de ','¿Qué dije de '],
 ['recuérdame qué dije sobre ','¿Qué dije sobre '],
 ['recuerdame qué dije de ','¿Qué dije de '],
 ['¿te hablé de ','¿Qué dije de '],
 ['¿te hablé sobre ','¿Qué dije sobre '],
 ['¿qué te comenté de ','¿Qué dije de '],
 ['¿qué comenté sobre ','¿Qué dije sobre '],
 ['¿qué fue lo que dije de ','¿Qué dije de '],
 ['¿cuál fue mi mensaje sobre ','¿Qué dije sobre '],
 ['¿qué te conté de ','¿Qué dije de '],
 ['¿qué mencioné de ','¿Qué dije de '],
 ['¿me puedes recordar qué dije de ','¿Qué dije de '],
 ['¿me puedes recordar qué dije sobre ','¿Qué dije sobre '],
 ['¿podrías recordarme qué dije sobre ','¿Qué dije sobre '],
 ['oye, ¿qué te comenté sobre ','¿Qué dije sobre '],
 ['por favor, recuérdame qué dije de ','¿Qué dije de '],
 ['could you remind me what i said about ','¿Qué dije de '],
 ['remind me what i said about ','¿Qué dije de ']
])add(source,target,1);

for(const [source,target,mode] of [
 ['hazme un poema sobre ','escribe un poema sobre ',2],
 ['hazme un poema acerca de ','escribe un poema sobre ',2],
 ['escríbeme un poema sobre ','escribe un poema sobre ',2],
 ['escribeme un poema sobre ','escribe un poema sobre ',2],
 ['inventa un poema sobre ','escribe un poema sobre ',2],
 ['quiero un poema sobre ','escribe un poema sobre ',2],
 ['¿me escribes un poema sobre ','escribe un poema sobre ',2],
 ['¿podrías escribir un poema sobre ','escribe un poema sobre ',2],
 ['¿puedes hacer un poema acerca de ','escribe un poema sobre ',2],
 ['hazme un cuento sobre ','escribe un cuento sobre ',3],
 ['hazme una historia acerca de ','escribe un cuento sobre ',3],
 ['quiero un cuento sobre ','escribe un cuento sobre ',3],
 ['quiero una historia sobre ','escribe un cuento sobre ',3],
 ['cuéntame una historia sobre ','escribe un cuento sobre ',3],
 ['cuentame una historia sobre ','escribe un cuento sobre ',3],
 ['cuenta un cuento sobre ','escribe un cuento sobre ',3],
 ['inventa una historia acerca de ','escribe un cuento sobre ',3],
 ['¿me cuentas un cuento sobre ','escribe un cuento sobre ',3],
 ['¿puedes contarme una historia sobre ','escribe un cuento sobre ',3],
 ['por favor, inventa una historia sobre ','escribe un cuento sobre ',3]
])add(source,target,mode);

for(const[n,i]of [['dos',2],['tres',3],['cuatro',4],['cinco',5],['seis',6],['2',2],['3',3],['4',4],['5',5],['6',6]]){
 for(const source of ['hazme ','inventa ','escribe ','quiero ','¿me escribes ']){
  add(source+n+' versos sobre ','escribe un poema de '+i+' versos sobre ',2);
 }
 for(const source of ['cuéntame ','inventa ','quiero ','¿me cuentas ']){
  add(source+n+' frases sobre ','escribe un cuento de '+i+' frases sobre ',3);
 }
}
for(const [source,target] of [
 ['explícame con los datos:\nhecho: ','explica con datos:\nhecho: '],
 ['explicame con los datos:\nhecho: ','explica con datos:\nhecho: '],
 ['¿puedes explicar estos datos?\nhecho: ','explica con datos:\nhecho: '],
 ['¿podrías explicar estos hechos?\nhecho: ','explica con datos:\nhecho: '],
 ['dame una explicación con datos:\nhecho: ','explica con datos:\nhecho: '],
 ['explica la relación usando:\nhecho: ','explica con datos:\nhecho: ']
])add(source,target,4);
for(const source of [
 'deduce a partir de estas premisas: ',
 'razona sobre las siguientes premisas: ',
 'razona usando estas premisas: ',
 '¿puedes deducirlo con estas premisas? ',
 'deduce lo siguiente: ',
 'utiliza estas premisas para razonar: '
])add(source,'',5);

export const PARAPHRASE_RULES=Object.freeze(RULES);
export function paraphraseSource(){
 const P=PARAPHRASE_BASE,lines=['#!reverse-pc-machine-v1'],w=(...items)=>lines.push(...items),L=name=>w('label '+name);
 const st=(at,value)=>w('store8 '+at+' '+value);
 function say(text){
  for(const b of Buffer.from(text,'utf8'))w('set r14 '+b,'print r14','add r11 1');
 }
 // +0 handled; +1 target mode; +2 rule ID; +3..4 emitted length;
 // +5 read-only. No persistent memory is read or modified.
 st(P,0);st(P+1n,0);st(P+2n,0);st(P+3n,0);st(P+4n,0);st(P+5n,1);
 w('load8 r9 '+LENGTH,'load8 r3 '+(LENGTH+1n),'mul r3 256','add r9 r3',
   'cmp r9 1','jlt p06_done','cmp r9 '+PARAPHRASE_MAX_INPUT,'jgt p06_done');

 if(RULES.length>255)throw Error('P06 native rule count exceeds one byte.');
 for(const [i,rule] of RULES.entries()){
  const id=i+1,bytes=Buffer.from(rule.source,'utf8'),tag='p06_rule_'+id,miss=tag+'_miss';
  L(tag);w('cmp r9 '+bytes.length,'jle '+miss);
  for(const[j,byte]of bytes.entries()){
   const good=tag+'_fold_'+j;
   w('load8 r3 '+(INPUT+BigInt(j)),
     'cmp r3 65','jlt '+good,'cmp r3 90','jgt '+good,'add r3 32');
   L(good);w('cmp r3 '+byte,'jne '+miss);
  }
  w('set r5 '+bytes.length,'set r6 '+rule.mode,'set r8 '+id,'jmp p06_capture');L(miss);
 }
 w('jmp p06_done');
 L('p06_capture');
 w('mov r12 r9','sub r12 r5','cmp r12 2','jlt p06_done');
 // Recall, poetry and fiction use one bounded topic; explanation and
 // reasoning may contain multiple sentences/lines, but P04/P03 validate
 // their full downstream semantics before the replacement is accepted.
 for(const mode of [1,2,3])w('cmp r6 '+mode,'je p06_topic_limit');
 w('cmp r12 '+PARAPHRASE_MAX_INPUT,'jgt p06_done','jmp p06_validate_setup');
 L('p06_topic_limit');w('cmp r12 80','jgt p06_done');
 L('p06_validate_setup');w('mov r0 r5');
 L('p06_validate');
 w('cmp r0 r9','jge p06_dispatch','set r7 '+INPUT,'add r7 r0','load8 r3 $r7',
   'cmp r3 0','je p06_done','cmp r3 127','je p06_done',
   'cmp r3 34','je p06_done','cmp r3 39','je p06_done',
   'cmp r3 96','je p06_done','cmp r3 59','je p06_done',
   'cmp r3 32','jge p06_next_byte',
   'cmp r6 4','je p06_multiline',
   'cmp r6 5','je p06_multiline','jmp p06_done');
 L('p06_multiline');w('cmp r3 10','je p06_next_byte','cmp r3 13','je p06_next_byte','jmp p06_done');
 L('p06_next_byte');
 // Do not reinterpret a second conjoined instruction as part of the topic.
 // A bounded false negative is safer than silently dropping an imperative.
 w('cmp r6 3','jgt p06_advance','cmp r3 32','jne p06_advance',
   'mov r7 r0','add r7 2','cmp r7 r9','jge p06_advance',
   'set r7 '+INPUT,'add r7 r0','add r7 1','load8 r4 $r7',
   'cmp r4 89','jne p06_lower_y','set r4 121');
 L('p06_lower_y');
 w('cmp r4 121','jne p06_advance','add r7 1','load8 r4 $r7',
   'cmp r4 32','je p06_done');
 L('p06_advance');w('add r0 1','jmp p06_validate');
 L('p06_dispatch');w('set r11 0');
 for(const [i,rule]of RULES.entries()){
  const label='p06_output_'+(i+1);
  w('cmp r8 '+(i+1),'je '+label);
 }
 w('jmp p06_done');
 for(const [i,rule]of RULES.entries()){
  L('p06_output_'+(i+1));say(rule.target);
  w('jmp p06_copy_tail');
 }
 L('p06_copy_tail');
 w('mov r0 r5');
 L('p06_copy_next');
 w('cmp r0 r9','jge p06_finish','set r7 '+INPUT,'add r7 r0',
   'load8 r14 $r7','print r14','add r11 1','add r0 1','jmp p06_copy_next');
 L('p06_finish');
 w('cmp r11 '+PARAPHRASE_MAX_OUTPUT,'jgt p06_done');
 st(P,1);st(P+1n,'r6');st(P+2n,'r8');
 w('mov r3 r11','mod r3 256');st(P+3n,'r3');
 w('mov r3 r11','div r3 256');st(P+4n,'r3');
 L('p06_done');w('halt');
 return lines.join('\n')+'\n';
}
