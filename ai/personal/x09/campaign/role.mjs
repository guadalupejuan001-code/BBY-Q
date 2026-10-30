import{BASE as B,SCRATCH as S,SCRATCH_BYTES,PRIMARY,HANDLED,STATUS,BANK,WITNESS,PROOF,F,C,SCHEMA}from'./schema.mjs';

export function roleSource(){
 const lines=['#!reverse-pc-machine-v1'];const w=(...x)=>lines.push(...x),L=x=>w('label '+x),st=(a,v)=>w('store8 '+a+' '+v),ld=(r,a)=>w('load8 r'+r+' '+a);
 const say=t=>{for(const b of Buffer.from(t))w('set r14 '+b,'print r14');};
 const Q=S+128n;
 function word(prefix,base,target){
  ld(10,target);ld(5,base+16n);w('set r0 0');L(prefix+'_find');w('cmp r0 r5','jge campaign_corrupt','mov r13 r0','mul r13 16','add r13 '+(base+1000n),'mov r7 r13','add r7 1','load8 r9 $r7','cmp r9 r10','je '+prefix+'_found','add r0 1','jmp '+prefix+'_find');
  L(prefix+'_found');w('load8 r9 $r13','set r1 0');L(prefix+'_bytes');w('cmp r1 r9','jge '+prefix+'_end','mov r7 r13','add r7 2','add r7 r1','load8 r14 $r7','print r14','add r1 1','jmp '+prefix+'_bytes');L(prefix+'_end');
 }
 function bank(prefix,base,selector,next){
  st(S+7n,0);st(S+8n,0);st(S+4n,0);st(S+5n,0);st(S+6n,0);
  for(let token=0;token<3;token++){
   const p=prefix+'_t'+token;ld(6,Q+BigInt(token*16));ld(5,base+16n);w('set r0 0');L(p+'_scan');w('cmp r0 r5','jge '+p+'_done','mov r13 r0','mul r13 16','add r13 '+(base+1000n),'load8 r9 $r13','cmp r9 r6','jne '+p+'_next','set r1 0');L(p+'_compare');w('cmp r1 r6','jge '+p+'_match','set r7 '+(Q+BigInt(token*16)+2n),'add r7 r1','load8 r8 $r7','mov r7 r13','add r7 2','add r7 r1','load8 r9 $r7','cmp r8 r9','jne '+p+'_next','add r1 1','jmp '+p+'_compare');L(p+'_match');w('mov r7 r13','add r7 1','load8 r2 $r7');st(S+4n+BigInt(token),'r2');ld(2,S+7n);w('add r2 1');st(S+7n,'r2');if(token===1)st(S+8n,1);w('jmp '+p+'_done');L(p+'_next');w('add r0 1','jmp '+p+'_scan');L(p+'_done');
  }
  ld(0,S+7n);w('cmp r0 3','je '+prefix+'_infer');ld(1,S+8n);w('cmp r1 1','jne '+prefix+'_unresolved','cmp r0 2','jlt '+prefix+'_unresolved');st(S+9n,1);L(prefix+'_unresolved');w('jmp '+next);
  L(prefix+'_infer');st(S+13n,selector);st(S+10n,0);st(S+11n,0);st(S+12n,0);ld(2,S+4n);ld(3,S+5n);ld(4,S+6n);ld(5,base+18n);w('set r0 0');
  L(prefix+'_direct');w('cmp r0 r5','jge '+prefix+'_compose','mov r7 r0','mul r7 8','add r7 '+(base+3000n),'load8 r8 $r7','cmp r8 r2','jne '+prefix+'_direct_next','add r7 1','load8 r8 $r7','cmp r8 r3','jne '+prefix+'_direct_next','add r7 1','load8 r8 $r7','cmp r8 r4','jne '+prefix+'_direct_next','add r7 1','load8 r12 $r7','add r7 1','load8 r13 $r7','cmp r13 2','jlt '+prefix+'_positive','cmp r13 r12','jlt '+prefix+'_positive');st(S+10n,2);st(S+12n,1);w('jmp '+prefix+'_emit');
  L(prefix+'_positive');w('cmp r12 2','jlt '+prefix+'_emit','cmp r12 r13','jle '+prefix+'_emit');st(S+10n,1);st(S+12n,1);w('jmp '+prefix+'_emit');
  L(prefix+'_direct_next');w('add r0 1','jmp '+prefix+'_direct');
  L(prefix+'_compose');w('set r7 '+(base+2000n),'add r7 r3','load8 r8 $r7','cmp r8 1','jne '+prefix+'_emit','set r0 0');
  L(prefix+'_first');w('cmp r0 r5','jge '+prefix+'_emit','mov r7 r0','mul r7 8','add r7 '+(base+3000n),'load8 r8 $r7','cmp r8 r2','jne '+prefix+'_first_next','add r7 1','load8 r8 $r7','cmp r8 r3','jne '+prefix+'_first_next','add r7 1','load8 r6 $r7','add r7 1','load8 r12 $r7','add r7 1','load8 r13 $r7','cmp r12 2','jlt '+prefix+'_first_next','cmp r12 r13','jle '+prefix+'_first_next','set r1 0');
  L(prefix+'_second');w('cmp r1 r5','jge '+prefix+'_first_next','mov r7 r1','mul r7 8','add r7 '+(base+3000n),'load8 r8 $r7','cmp r8 r6','jne '+prefix+'_second_next','add r7 1','load8 r8 $r7','cmp r8 r3','jne '+prefix+'_second_next','add r7 1','load8 r8 $r7','cmp r8 r4','jne '+prefix+'_second_next','add r7 1','load8 r12 $r7','add r7 1','load8 r13 $r7','cmp r12 2','jlt '+prefix+'_second_next','cmp r12 r13','jle '+prefix+'_second_next');st(S+10n,1);st(S+11n,'r6');st(S+12n,2);w('jmp '+prefix+'_emit');
  L(prefix+'_second_next');w('add r1 1','jmp '+prefix+'_second');L(prefix+'_first_next');w('add r0 1','jmp '+prefix+'_first');
  L(prefix+'_emit');st(HANDLED,1);ld(0,S+10n);w('cmp r0 0','jne '+prefix+'_status');w('set r0 3');L(prefix+'_status');st(STATUS,'r0');st(BANK,selector);ld(0,S+11n);st(WITNESS,'r0');ld(0,S+12n);st(PROOF,'r0');st(F+2n,0);st(F+3n,1);ld(0,S+10n);w('cmp r0 0','je campaign_unknown','cmp r0 2','je '+prefix+'_negative');say('Sí: ');w('jmp '+prefix+'_sentence');L(prefix+'_negative');say('No: ');L(prefix+'_sentence');word(prefix+'_word_s',base,S+4n);say(' ');word(prefix+'_word_p',base,S+5n);say(' ');word(prefix+'_word_o',base,S+6n);ld(0,S+11n);w('cmp r0 0','je '+prefix+'_period');say(' (vía ');word(prefix+'_word_w',base,S+11n);say(')');L(prefix+'_period');say('.');w('jmp campaign_cleanup');
 }
 ld(0,B);w('cmp r0 76','jne campaign_corrupt');ld(0,B+1n);w('cmp r0 71','jne campaign_corrupt');ld(0,B+2n);w('cmp r0 '+SCHEMA,'jne campaign_corrupt');
 for(const base of[PRIMARY,B]){ld(0,base+16n);w('cmp r0 1','jlt campaign_corrupt','cmp r0 32','jgt campaign_corrupt');ld(0,base+18n);w('cmp r0 24','jgt campaign_corrupt');}
 w('set r0 0');L('campaign_scratch_guard');w('cmp r0 '+SCRATCH_BYTES,'jge campaign_ready','set r7 '+S,'add r7 r0','load8 r8 $r7','cmp r8 0','jne campaign_corrupt','add r0 1','jmp campaign_scratch_guard');
 L('campaign_ready');for(const a of[HANDLED,STATUS,BANK,WITNESS,PROOF])st(a,0);ld(0,F+8n);ld(1,F+9n);w('mul r1 256','add r0 r1','cmp r0 1','jlt campaign_cleanup','cmp r0 64','jgt campaign_cleanup');st(S,'r0');w('set r0 0','set r4 0','set r6 0');
 L('campaign_parse');ld(5,S);w('cmp r0 r5','jge campaign_parse_end','set r7 '+C,'add r7 r0','load8 r2 $r7','add r0 1','cmp r2 194','je campaign_open_question','cmp r2 63','je campaign_separator','cmp r2 32','je campaign_separator','cmp r2 9','je campaign_separator','cmp r2 10','je campaign_separator','cmp r2 13','je campaign_separator','cmp r2 65','jlt campaign_cleanup','cmp r2 90','jgt campaign_lower','add r2 32');L('campaign_lower');w('cmp r2 97','jlt campaign_cleanup','cmp r2 122','jgt campaign_cleanup','cmp r4 3','jge campaign_cleanup','cmp r6 8','jge campaign_cleanup','mov r7 r4','mul r7 16','add r7 '+Q,'mov r8 r7','add r8 2','add r8 r6','store8 $r8 r2','add r6 1','store8 $r7 r6','jmp campaign_parse');
 L('campaign_open_question');ld(5,S);w('cmp r0 r5','jge campaign_cleanup','set r7 '+C,'add r7 r0','load8 r2 $r7','cmp r2 191','jne campaign_cleanup','add r0 1','jmp campaign_separator');
 L('campaign_separator');w('cmp r6 0','je campaign_parse','add r4 1','set r6 0','jmp campaign_parse');L('campaign_parse_end');w('cmp r6 0','je campaign_count_ready','add r4 1');L('campaign_count_ready');w('cmp r4 3','jne campaign_cleanup');
 bank('campaign_primary',PRIMARY,0,'campaign_alternative');L('campaign_alternative');bank('campaign_alternate',B,1,'campaign_unresolved');
 L('campaign_unresolved');ld(0,S+9n);w('cmp r0 1','jne campaign_cleanup');st(HANDLED,1);st(STATUS,3);st(F+2n,0);st(F+3n,1);
 L('campaign_unknown');say('No tengo evidencia suficiente para esa microoración.');
 L('campaign_cleanup');w('set r0 0');L('campaign_erase');w('cmp r0 '+SCRATCH_BYTES,'jge campaign_done','set r7 '+S,'add r7 r0','store8 $r7 0','add r0 1','jmp campaign_erase');L('campaign_done');w('halt');L('campaign_corrupt');w('set r0 0','div r0 0');
 return lines.join('\n')+'\n';
}
