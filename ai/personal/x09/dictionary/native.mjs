// Offline XI assembly. Routing, case folding, hashing and lexical matching run in XI.
export const F=9100000000000200000n,C=F+256n;
export const B=8700000000000000000n,D=9131000000000000000n;
export const MAX_PAGE_BYTES=16984,KEY_SPACE=131072;

function assembler(){
 const lines=['#!reverse-pc-machine-v1'];let serial=0;
 const w=(...xs)=>lines.push(...xs),L=x=>w('label '+x),fresh=x=>'x09d_'+x+'_'+serial++;
 const load=(r,p)=>w(`load8 r${r} ${p}`),store=(p,v)=>w(`store8 ${p} ${v}`);
 const read=(r,p,n)=>{load(r,p);for(let i=1;i<n;i++)w(`load8 r15 ${p+BigInt(i)}`,`mul r15 ${256**i}`,`add r${r} r15`);};
 const put=(p,r,n)=>{for(let i=0;i<n;i++){w(`mov r15 r${r}`);if(i)w(`div r15 ${256**i}`);w('mod r15 256',`store8 ${p+BigInt(i)} r15`);}};
 const say=s=>{for(const byte of Buffer.from(s))w(`set r14 ${byte}`,'print r14');};
 function compareBytes(text,baseRegister,fail){
  let prev;
  for(const[i,b]of Buffer.from(text).entries()){
   w(`set r7 ${C}`,`add r7 r${baseRegister}`,`add r7 ${i}`,'load8 r3 $r7',`cmp r3 ${b}`);
   if((b>=97&&b<=122)||(prev===195&&b>=160&&b<=190&&b!==183)){
    const ok=fresh('fold');w('je '+ok,`cmp r3 ${b-32}`,'jne '+fail);L(ok);
   }else w('jne '+fail);
   prev=b;
  }
 }
 return{lines,w,L,fresh,load,store,read,put,say,compareBytes,text:()=>lines.join('\n')+'\n'};
}

export function routeSource(){
 const a=assembler(),{w,L,fresh,load,store,read,put,say,compareBytes}=a;
 // BASE X08 front has already validated the complete UTF-8 frame. No write is
 // made before this role recognizes a dictionary request and validates its span.
 for(const[p,v]of [[F,86],[F+1n,2],[F+2n,1],[F+3n,1]]){load(0,p);w(`cmp r0 ${v}`,'jne x09d_protocol');}
 load(8,F+4n);w('cmp r8 1','je x09d_language_ok','cmp r8 2','jne x09d_protocol');L('x09d_language_ok');
 read(9,F+8n,2);w('cmp r9 1','jlt x09d_protocol','cmp r9 16384','jgt x09d_protocol','set r4 0','mov r6 r9');
 L('x09d_trim_start');w('cmp r4 r6','jge x09d_unhandled',`set r7 ${C}`,'add r7 r4','load8 r3 $r7');
 for(const n of [32,9,10,13])w(`cmp r3 ${n}`,'je x09d_start_space');w('jmp x09d_trim_end');L('x09d_start_space');w('add r4 1','jmp x09d_trim_start');
 L('x09d_trim_end');w('cmp r4 r6','jge x09d_unhandled','mov r7 r6','sub r7 1',`add r7 ${C}`,'load8 r3 $r7');
 for(const n of [32,9,10,13])w(`cmp r3 ${n}`,'je x09d_end_space');w('jmp x09d_patterns');L('x09d_end_space');w('sub r6 1','jmp x09d_trim_end');
 L('x09d_patterns');
 const patterns=[
  ['@lex',0,0,true,false],['diccionario:',1,1,false,false],['definición de ',1,1],['definicion de ',1,1],
  ['¿qué significa ',1,1],['¿que significa ',1,1],['qué significa ',1,1],['que significa ',1,1],
  ['dictionary:',2,1,false,false],['meaning of ',2,1],['definition of ',2,1],['what does ',2,2],['define ',0,1]
 ];
 for(const[text,language,mode,boundary=false,natural=true]of patterns){
  const next=fresh('prefix_next'),ready=fresh('prefix_ready'),n=Buffer.byteLength(text);
  w('mov r5 r4',`add r5 ${n}`,'cmp r5 r6','jgt '+next);compareBytes(text,4,next);
  if(boundary){w('cmp r5 r6','je '+ready,`set r7 ${C}`,'add r7 r5','load8 r3 $r7');for(const c of [32,9,10,13])w(`cmp r3 ${c}`,'je '+ready);w('jmp '+next);}
  L(ready);w('mov r10 r5','mov r11 r6',language?`set r12 ${language}`:'mov r12 r8',`set r13 ${mode}`,`set r14 ${natural?1:0}`,'jmp x09d_query_trim_start');L(next);
 }
 w('jmp x09d_unhandled');
 L('x09d_query_trim_start');w('cmp r10 r11','jge x09d_format',`set r7 ${C}`,'add r7 r10','load8 r3 $r7');
 for(const c of [32,9,10,13])w(`cmp r3 ${c}`,'je x09d_query_start_space');w('jmp x09d_query_trim_end');L('x09d_query_start_space');w('add r10 1','jmp x09d_query_trim_start');
 L('x09d_query_trim_end');w('cmp r10 r11','jge x09d_format','mov r7 r11','sub r7 1',`add r7 ${C}`,'load8 r3 $r7');
 for(const c of [32,9,10,13])w(`cmp r3 ${c}`,'je x09d_query_end_space');
 w('cmp r13 1','je x09d_optional_question','cmp r13 2','je x09d_optional_question','jmp x09d_query_suffix');
 L('x09d_optional_question');w('cmp r3 63','je x09d_query_end_space','jmp x09d_query_suffix');
 L('x09d_query_end_space');w('sub r11 1','jmp x09d_query_trim_end');
 L('x09d_query_suffix');w('cmp r13 2','jne x09d_query_language','mov r5 r11','sub r5 5','cmp r5 r10','jlt x09d_unhandled');compareBytes(' mean',5,'x09d_unhandled');w('mov r11 r5','set r13 1','jmp x09d_query_trim_start');
 L('x09d_query_language');w('cmp r13 0','jne x09d_query_ready');
 for(const[marker,language]of [['en:',2],['es:',1]]){
  const next=fresh('query_language_next');w('mov r5 r10','add r5 3','cmp r5 r11','jgt '+next);compareBytes(marker,10,next);w(`set r12 ${language}`,'add r10 3','set r13 3','jmp x09d_query_trim_start');L(next);
 }
 L('x09d_query_ready');w('mov r9 r11','sub r9 r10','cmp r9 1','jlt x09d_format','cmp r9 250','jgt x09d_format','set r0 0');
 L('x09d_control_guard');w(`set r7 ${D}`,'add r7 r0','load8 r3 $r7','cmp r3 0','jne x09d_protocol','add r0 1','cmp r0 512','jlt x09d_control_guard');
 store(D,1);store(D+1n,'r12');store(D+16n,1);store(D+17n,'r14');put(D+5n,9,2);store(B+1n,'r9');store(B+2n,'r12');w('set r0 0','set r1 0');
 L('x09d_hash_loop');w('cmp r0 r9','jge x09d_hash_done',`set r7 ${C}`,'add r7 r10','add r7 r0','load8 r3 $r7','cmp r3 65','jlt x09d_query_folded','cmp r3 90','jgt x09d_query_folded','add r3 32');
 L('x09d_query_folded');w('cmp r3 95','jne x09d_query_copy','set r3 32');L('x09d_query_copy');w(`set r7 ${B+128n}`,'add r7 r0','store8 $r7 r3','mul r1 131','add r1 r3','mod r1 65536','add r0 1','jmp x09d_hash_loop');
 L('x09d_hash_done');w('cmp r12 2','jne x09d_hash_store','add r1 65536');L('x09d_hash_store');put(D+2n,1,3);w('set r0 1','mov r2 r9','print r0','print r1','print r2','halt');
 L('x09d_format');store(F+2n,0);store(F+3n,1);store(F+10n,0);w('set r0 2','print r0','cmp r12 2','je x09d_format_en');say('Consulta de diccionario incompleta: escribe una palabra o expresión de hasta 250 bytes.');w('halt');L('x09d_format_en');say('Incomplete dictionary query: enter a word or expression of up to 250 bytes.');w('halt');
 L('x09d_unhandled');w('set r0 0','print r0','halt');L('x09d_protocol');w('set r0 3','print r0','halt');
 return a.text();
}

export function lookupSource(originalLookup){
 if(typeof originalLookup!=='string'||originalLookup.split('label lex_finish\n').length!==2||originalLookup.split('label lex_missing\n').length!==2||!originalLookup.startsWith('label lex_lookup\n'))throw Error('Exact E031 lookup source shape required');
 const a=assembler(),{w,L,load,store,read}=a;
 for(const[p,v]of [[D,1],[D+16n,1],[F,86],[F+1n,2],[F+2n,1],[F+3n,1]]){load(0,p);w(`cmp r0 ${v}`,'jne x09d_lookup_protocol');}
 read(0,D+2n,3);w('cmp r0 0','jlt x09d_lookup_protocol',`cmp r0 ${KEY_SPACE}`,'jge x09d_lookup_protocol');
 read(2,D+5n,2);load(3,B+1n);w('cmp r2 r3','jne x09d_lookup_protocol','cmp r2 1','jlt x09d_lookup_protocol','cmp r2 250','jgt x09d_lookup_protocol');load(2,D+1n);load(3,B+2n);w('cmp r2 r3','jne x09d_lookup_protocol');read(2,B+16n,3);w(`cmp r2 ${MAX_PAGE_BYTES}`,'jgt x09d_lookup_protocol','jmp lex_lookup');
 const lookup=originalLookup.slice(0,originalLookup.indexOf('label lex_finish\n')).replace('label lex_missing\n',`label lex_missing\nload8 r3 ${D+17n}\ncmp r3 1\nje x09d_natural_missing\n`);w(lookup.trimEnd());
 L('lex_finish');store(D,2);store(F+2n,0);store(F+3n,1);store(F+10n,0);w('set r0 2','print r0','halt');
 L('x09d_natural_missing');w('set r0 4','print r0','halt');
 L('x09d_lookup_protocol');w('set r0 3','print r0','halt');return a.text();
}

export function clearSource(){
 const a=assembler(),{w,L,load,read}=a;
 for(const[p,v]of [[D,2],[D+16n,1],[F+2n,0],[F+3n,1]]){load(0,p);w(`cmp r0 ${v}`,'jne x09d_clear_protocol');}
 read(9,B+16n,3);w(`cmp r9 ${MAX_PAGE_BYTES}`,'jgt x09d_clear_protocol','add r9 1024','set r0 0');
 L('x09d_clear_bank');w('cmp r0 r9','jge x09d_clear_control_start',`set r7 ${B}`,'add r7 r0','store8 $r7 0','add r0 1','jmp x09d_clear_bank');
 L('x09d_clear_control_start');w('set r0 0');L('x09d_clear_control');w(`set r7 ${D}`,'add r7 r0','store8 $r7 0','add r0 1','cmp r0 512','jlt x09d_clear_control','set r0 0','print r0','halt');
 L('x09d_clear_protocol');w('set r0 3','print r0','halt');return a.text();
}
