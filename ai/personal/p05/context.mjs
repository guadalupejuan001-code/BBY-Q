// P05: bounded, explainable conversational reference lookup in native XI.
// The host stages prior user messages as byte frames; XI owns request grammar,
// topic matching, pronoun admission and candidate selection.
import {B,INPUT,LENGTH} from '../x10/schema.mjs';
export const CONTEXT_BASE=B+196608n;
export const CONTEXT_SLOT_BASE=CONTEXT_BASE+4096n;
export const CONTEXT_SLOT_STRIDE=512;
export const CONTEXT_MAX_CANDIDATES=8;
export const CONTEXT_MAX_ENTRY_BYTES=384;
export const CONTEXT_MAX_QUERY_BYTES=256;
export const CONTEXT_MODES=Object.freeze({
 unsupported:0,named:1,pronoun:2,not_found:3,ambiguous:4,last:5,
 clear:6,status:7,recent:8,answer:9
});
const prefixes=[
 '¿qué dije sobre ','¿qué dije de ','qué dije sobre ','qué dije de ',
 '¿y qué dije sobre ','¿y qué dije de ','¿qué te dije sobre ',
 '¿qué te dije de ','¿te acuerdas de ','¿qué mencioné sobre ',
 '¿qué dije acerca de ','qué dije acerca de '
];
const exact=[
 ['@context clear',6],['@context status',7],['@context recent',8],
 ['@context last',5],['@context answer',9],
 ['¿qué dije antes?',5],['qué dije antes?',5],
 ['¿qué me respondiste antes?',9],['¿qué contestaste antes?',9]
];
const pronouns=['ella','él','eso','ese tema','aquello','ello'];
function token(code,put,name,bytes,lengthCheck=true){
 const miss=name+'_miss';
 if(lengthCheck)put('cmp r9 '+bytes.length,'jne '+miss);
 for(let i=0;i<bytes.length;i++){
  const done=name+'_fold_'+i;
  put('load8 r3 '+(INPUT+BigInt(i)),
      'cmp r3 65','jlt '+done,'cmp r3 90','jgt '+done,'add r3 32');
  code(done);put('cmp r3 '+bytes[i],'jne '+miss);
 }
 return miss;
}
export function contextSource(){
 const lines=['#!reverse-pc-machine-v1'],w=(...a)=>lines.push(...a),L=t=>w('label '+t);
 const st=(a,v)=>w('store8 '+a+' '+v);
 // P+0 selected mode, P+1 chosen slot (1-based), P+2 query type,
 // P+3 supplied record count, P+4 normalized target byte count.
 st(CONTEXT_BASE,0);st(CONTEXT_BASE+1n,0);st(CONTEXT_BASE+2n,0);st(CONTEXT_BASE+4n,0);
 w('load8 r9 '+LENGTH,'load8 r4 '+(LENGTH+1n),'mul r4 256','add r9 r4',
   'cmp r9 1','jlt p05_done','cmp r9 '+CONTEXT_MAX_QUERY_BYTES,'jgt p05_done');
 for(let k=0;k<exact.length;k++){
  const [value,mode]=exact[k],tag='p05_exact_'+k,bytes=Buffer.from(value,'utf8');
  L(tag);const miss=token(L,w,tag,bytes); // generated comparators fold uppercase ASCII in native XI
  if(mode===5||mode===9){
   w('load8 r13 '+(CONTEXT_BASE+3n),'cmp r13 0','jle p05_not_found');st(CONTEXT_BASE+1n,1);
  }
  st(CONTEXT_BASE,mode);w('jmp p05_done');L(miss);
 }
 for(let k=0;k<prefixes.length;k++){
  const bytes=Buffer.from(prefixes[k],'utf8'),tag='p05_prefix_'+k;
  L(tag);w('cmp r9 '+bytes.length,'jle '+tag+'_miss');
  const miss=token(L,w,tag,bytes,false);
  w('set r5 '+bytes.length,'jmp p05_target');L(miss);
 }
 w('jmp p05_done');
 L('p05_target');
 // Strip only trailing ASCII question marks, full stops, exclamation marks and spaces.
 w('mov r8 r9');
 L('p05_trim');
 w('cmp r8 r5','jle p05_invalid_target','mov r7 r8','sub r7 1','add r7 '+INPUT,'load8 r3 $r7',
   'cmp r3 32','je p05_strip','cmp r3 63','je p05_strip',
   'cmp r3 46','je p05_strip','cmp r3 33','je p05_strip','jmp p05_trimmed');
 L('p05_strip');w('sub r8 1','jmp p05_trim');
 L('p05_trimmed');
 w('mov r10 r8','sub r10 r5','cmp r10 1','jlt p05_invalid_target','cmp r10 60','jgt p05_invalid_target');
 st(CONTEXT_BASE+4n,'r10');
 // Interpret a small, closed set of pronouns. Never guess a named referent
 // from a different topic or from a complex/unsupported last utterance.
 for(let k=0;k<pronouns.length;k++){
  const bytes=Buffer.from(pronouns[k],'utf8'),tag='p05_pronoun_'+k;
  L(tag);w('cmp r10 '+bytes.length,'jne '+tag+'_miss');
  for(let i=0;i<bytes.length;i++){
   const fold=tag+'_fold_'+i;
   w('set r7 '+INPUT,'add r7 r5','add r7 '+i,'load8 r3 $r7',
     'cmp r3 65','jlt '+fold,'cmp r3 90','jgt '+fold,'add r3 32');
   L(fold);w('cmp r3 '+bytes[i],'jne '+tag+'_miss');
  }
  w('jmp p05_resolve_pronoun');L(tag+'_miss');
 }
 // Explicit topic search through up to eight previous user utterances.
 w('load8 r13 '+(CONTEXT_BASE+3n),'set r1 0');
 L('p05_record');
 w('cmp r1 r13','jge p05_not_found','set r6 '+CONTEXT_SLOT_BASE,
   'mov r7 r1','mul r7 '+CONTEXT_SLOT_STRIDE,'add r6 r7',
   'set r7 '+(CONTEXT_BASE+32n),'mov r8 r1','mul r8 2','add r7 r8',
   'load8 r12 $r7','add r7 1','load8 r4 $r7','mul r4 256','add r12 r4',
   'set r2 0');
 L('p05_search_pos');
 w('mov r7 r2','add r7 r10','cmp r7 r12','jgt p05_next_record',
   'cmp r2 0','je p05_compare');
 // Whole-word or whole-phrase comparison: do not match "Ana" inside "Anabel".
 w('mov r7 r6','add r7 r2','sub r7 1','load8 r4 $r7',
   'cmp r4 65','jlt p05_boundary_before_digit','cmp r4 90','jle p05_next_pos');
 L('p05_boundary_before_digit');
 w('cmp r4 97','jlt p05_boundary_before_number','cmp r4 122','jle p05_next_pos');
 L('p05_boundary_before_number');
 w('cmp r4 48','jlt p05_compare','cmp r4 57','jle p05_next_pos');
 L('p05_compare');w('set r3 0');
 L('p05_compare_next');
 w('cmp r3 r10','jge p05_boundary_after',
   'mov r7 r6','add r7 r2','add r7 r3','load8 r4 $r7',
   'cmp r4 65','jlt p05_fold_candidate_done','cmp r4 90','jgt p05_fold_candidate_done','add r4 32');
 L('p05_fold_candidate_done');
 w('set r7 '+INPUT,'add r7 r5','add r7 r3','load8 r11 $r7',
   'cmp r11 65','jlt p05_fold_query_done','cmp r11 90','jgt p05_fold_query_done','add r11 32');
 L('p05_fold_query_done');w('cmp r4 r11','jne p05_next_pos','add r3 1','jmp p05_compare_next');
 L('p05_boundary_after');
 w('mov r7 r2','add r7 r10','cmp r7 r12','jge p05_found_named',
   'add r7 r6','load8 r4 $r7',
   'cmp r4 65','jlt p05_after_digit','cmp r4 90','jle p05_next_pos');
 L('p05_after_digit');w('cmp r4 97','jlt p05_after_number','cmp r4 122','jle p05_next_pos');
 L('p05_after_number');w('cmp r4 48','jlt p05_found_named','cmp r4 57','jle p05_next_pos');
 L('p05_found_named');st(CONTEXT_BASE,1);
 w('mov r8 r1','add r8 1');st(CONTEXT_BASE+1n,'r8');w('jmp p05_done');
 L('p05_next_pos');w('add r2 1','jmp p05_search_pos');
 L('p05_next_record');w('add r1 1','jmp p05_record');
 L('p05_resolve_pronoun');
 w('load8 r13 '+(CONTEXT_BASE+3n),'cmp r13 0','jle p05_not_found');
 // A pronoun is admitted only for a single-token subject at the beginning
 // of the immediately previous recorded user utterance and a supported verb.
 w('set r6 '+CONTEXT_SLOT_BASE,'load8 r12 '+(CONTEXT_BASE+32n),
   'load8 r4 '+(CONTEXT_BASE+33n),'mul r4 256','add r12 r4',
   'cmp r12 6','jlt p05_ambiguous','set r2 0');
 L('p05_subject');
 w('cmp r2 40','jge p05_ambiguous','cmp r2 r12','jge p05_ambiguous',
   'mov r7 r6','add r7 r2','load8 r4 $r7',
   'cmp r4 32','je p05_subject_verb',
   'cmp r4 65','jlt p05_ambiguous','cmp r4 90','jle p05_subject_next',
   'cmp r4 97','jlt p05_ambiguous','cmp r4 122','jgt p05_ambiguous');
 L('p05_subject_next');w('add r2 1','jmp p05_subject');
 L('p05_subject_verb');
 w('cmp r2 1','jlt p05_ambiguous','add r2 1');
 for(let k=0;k<4;k++){
  const word=['es ','tiene ','esta ','está '][k], bytes=Buffer.from(word,'utf8'),tag='p05_verb_'+k;
  L(tag);w('mov r7 r2','add r7 '+bytes.length,'cmp r7 r12','jgt '+tag+'_miss');
  for(let i=0;i<bytes.length;i++){
   const fold=tag+'_fold_'+i;
   w('mov r7 r6','add r7 r2','add r7 '+i,'load8 r4 $r7',
     'cmp r4 65','jlt '+fold,'cmp r4 90','jgt '+fold,'add r4 32');
   L(fold);w('cmp r4 '+bytes[i],'jne '+tag+'_miss');
  }
  st(CONTEXT_BASE,2);st(CONTEXT_BASE+1n,1);w('jmp p05_done');L(tag+'_miss');
 }
 w('jmp p05_ambiguous');
 L('p05_not_found');st(CONTEXT_BASE,3);w('jmp p05_done');
 L('p05_ambiguous');st(CONTEXT_BASE,4);w('jmp p05_done');
 L('p05_invalid_target');st(CONTEXT_BASE,4);w('jmp p05_done');
 L('p05_done');w('halt');
 return lines.join('\n')+'\n';
}
