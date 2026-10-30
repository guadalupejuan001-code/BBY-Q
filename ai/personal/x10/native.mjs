// Offline source generation. UTF-8 validation, routing, field parsing, key
// normalization, record decisions and streamed text processing execute in XI.
import {B,INPUT,KEY,RECORD,STAGE,LENGTH,TOTAL,OFFSET,COUNT,REVISION,EXISTS,STATUS,KEY_LENGTH,OP,CAPACITY,MODE,START,SENTENCES,SEEN,ENDED,PREVIOUS,BEFORE,PENDING,LIMITS} from './schema.mjs';

function assembler(){
 const lines=['#!reverse-pc-machine-v1'];let serial=0;
 const w=(...x)=>lines.push(...x),L=x=>w('label '+x),uid=x=>x+'_'+serial++;
 const ld=(r,p)=>w(`load8 r${r} ${p}`),st=(p,v)=>w(`store8 ${p} ${v}`);
 const get=(r,p,n=4)=>{ld(r,p);for(let i=1;i<n;i++){ld(15,p+BigInt(i));w(`mul r15 ${256n**BigInt(i)}`,`add r${r} r15`);}};
 const put=(p,r,n=4)=>{for(let i=0;i<n;i++){w(`mov r15 r${r}`);if(i)w(`div r15 ${256n**BigInt(i)}`);w('mod r15 256');st(p+BigInt(i),'r15');}};
 const say=t=>{for(const b of Buffer.from(t))w(`set r14 ${b}`,'print r14');};
 const emit=(base,length)=>{const loop=uid('emit'),done=uid('emit_end');w(`set r8 ${base}`,`set r1 ${length}`,'set r0 0');L(loop);w('cmp r0 r1','jge '+done,'mov r7 r8','add r7 r0','load8 r14 $r7','print r14','add r0 1','jmp '+loop);L(done);};
 const span=(base,off,lenoff)=>{ld(1,base+BigInt(lenoff));w(`set r8 ${base+BigInt(off)}`,'set r0 0');const loop=uid('span'),done=uid('span_end');L(loop);w('cmp r0 r1','jge '+done,'mov r7 r8','add r7 r0','load8 r14 $r7','print r14','add r0 1','jmp '+loop);L(done);};
 const uint=r=>{w(`mov r10 r${r}`,'set r11 1000000000','set r12 0');const loop=uid('uint'),print=uid('digit'),skip=uid('skip');L(loop);w('mov r14 r10','div r14 r11','cmp r14 0','jne '+print,'cmp r12 0','jne '+print,'cmp r11 1','jne '+skip);L(print);w('add r14 48','print r14','set r12 1');L(skip);w('mod r10 r11','div r11 10','cmp r11 0','jgt '+loop);};
 const prefix=(text,hit,fail,exact=false)=>{const bytes=Buffer.from(text);get(9,LENGTH);w(`cmp r9 ${bytes.length}`,`jlt ${fail}`);if(exact){get(0,TOTAL);w(`cmp r0 ${bytes.length}`,'jne '+fail);}let prior;for(const[i,b]of bytes.entries()){ld(3,INPUT+BigInt(i));if((b>=97&&b<=122)||(prior===195&&b>=160&&b<=190&&b!==183)){const yes=uid('case');w(`cmp r3 ${b}`,'je '+yes,`cmp r3 ${b-32}`,'jne '+fail);L(yes);}else w(`cmp r3 ${b}`,'jne '+fail);prior=b;}w(`set r4 ${bytes.length}`,'jmp '+hit);};
 return {lines,w,L,uid,ld,st,get,put,say,emit,span,uint,prefix,source:()=>lines.join('\n')+'\n'};
}

export function validatorSource(){
 const a=assembler(),{w,L,ld,st,get}=a;
 st(STATUS,0);get(9,LENGTH);w('cmp r9 1','jlt bad',`cmp r9 ${LIMITS.page_bytes}`,'jgt bad','set r4 0');
 L('next');w('cmp r4 r9','jge done',`set r7 ${INPUT}`,'add r7 r4','load8 r3 $r7','add r4 1');ld(5,B+48n);w('cmp r5 0','jne continuation','cmp r3 128','jge lead','cmp r3 127','je bad','cmp r3 32','jge next','cmp r3 9','je next','cmp r3 10','je next','cmp r3 13','je next','jmp bad');
 L('lead');w('cmp r3 194','jlt bad','cmp r3 223','jle two','cmp r3 239','jle three','cmp r3 244','jle four','jmp bad');
 L('two');st(B+48n,1);st(B+49n,128);st(B+50n,191);w('jmp next');
 L('three');st(B+48n,2);st(B+49n,128);st(B+50n,191);w('cmp r3 224','jne not_e0');st(B+49n,160);L('not_e0');w('cmp r3 237','jne next');st(B+50n,159);w('jmp next');
 L('four');st(B+48n,3);st(B+49n,128);st(B+50n,191);w('cmp r3 240','jne not_f0');st(B+49n,144);L('not_f0');w('cmp r3 244','jne next');st(B+50n,143);w('jmp next');
 L('continuation');ld(6,B+49n);w('cmp r3 r6','jlt bad');ld(6,B+50n);w('cmp r3 r6','jgt bad','sub r5 1');st(B+48n,'r5');st(B+49n,128);st(B+50n,191);w('jmp next');
 L('done');w('halt');L('bad');st(STATUS,1);w('halt');return a.source();
}

export function routerSource(){
 const a=assembler(),{w,L,uid,ld,st,get,put,prefix}=a;
 st(OP,0);st(MODE,0);st(STATUS,0);
 const routes=[
  [['aprende: '],1,'teach'],[['corrige lección: ','corrige leccion: '],2,'teach'],[['olvida lección: ','olvida leccion: '],3,'key'],
  [['que es ','qué es ','¿qué es ','¿que es ','oye que es ','pz que es ','explícame ','explicame '],4,'key'],
  [['que requiere ','qué requiere ','¿qué requiere ','¿que requiere '],5,'key'],[['de dónde sabes ','de donde sabes ','¿de dónde sabes '],6,'key']
 ];
 for(const[texts,op,target]of routes)for(const text of texts){const hit=uid('route'),miss=uid('miss');prefix(text,hit,miss);L(hit);st(OP,op);st(MODE,1);w('jmp '+target);L(miss);}
 {const miss=uid('miss');prefix('@learn status','status',miss,true);L(miss);}
 for(const text of ['repite exactamente:\r\n','repite exactamente:\n','responde exactamente:\r\n','responde exactamente:\n']){const miss=uid('miss');prefix(text,'echo',miss);L(miss);}
 for(const text of ['resume:\r\n','resume:\n']){const miss=uid('miss');prefix(text,'summary',miss);L(miss);}
 {const miss=uid('miss');prefix('resume en ','summary_count',miss);L(miss);}w('halt');
 L('echo');st(MODE,2);put(START,4);get(0,TOTAL);w('cmp r0 r4','jle bad','halt');
 L('summary');st(SENTENCES,3);w('jmp summary_ready');
 L('summary_count');get(9,LENGTH);w('mov r7 r4',`add r7 ${INPUT}`,'load8 r3 $r7','cmp r3 49','jlt bad','cmp r3 56','jgt bad','sub r3 48');st(SENTENCES,'r3');w('add r4 1');const marker=Buffer.from(' frases:');for(const[i,b]of marker.entries()){w('mov r7 r4',`add r7 ${INPUT+BigInt(i)}`,'load8 r3 $r7',`cmp r3 ${b}`,'jne bad');}w(`add r4 ${marker.length}`,'mov r7 r4',`add r7 ${INPUT}`,'load8 r3 $r7','cmp r3 13','jne summary_lf','add r4 1','add r7 1','load8 r3 $r7');L('summary_lf');w('cmp r3 10','jne bad','add r4 1');
 L('summary_ready');st(MODE,3);put(START,4);get(0,TOTAL);w('cmp r0 r4','jle bad','halt');
 L('status');st(MODE,1);st(OP,8);w('halt');
 // Records fit one page; the complete request must be present. No truncation.
 L('teach');get(0,TOTAL);get(9,LENGTH);w('cmp r0 r9','jne bad');put(B+96n,4);L('teach_key_scan');w('cmp r4 r9','jge bad','mov r7 r4',`add r7 ${INPUT}`,'load8 r3 $r7','cmp r3 10','je teach_key_end','add r4 1','jmp teach_key_scan');
 L('teach_key_end');get(5,B+96n);w('mov r6 r4','sub r6 r5');w('cmp r6 1','jlt bad','sub r7 1','load8 r3 $r7','cmp r3 13','jne teach_key_no_cr','sub r6 1');L('teach_key_no_cr');put(B+100n,6);w('add r4 1');put(B+104n,4);w('jmp normalize_key');
 L('key');get(0,TOTAL);get(9,LENGTH);w('cmp r0 r9','jne unhandled');put(B+96n,4);w('mov r6 r9');L('trim');w('cmp r6 r4','jle unhandled','mov r7 r6','sub r7 1',`add r7 ${INPUT}`,'load8 r3 $r7','cmp r3 32','je trim_one','cmp r3 46','je trim_one','cmp r3 63','jne trimmed');L('trim_one');w('sub r6 1','jmp trim');
 L('trimmed');ld(0,OP);w('cmp r0 4','jne key_size');
 for(const text of [' y que requiere',' y qué requiere']){const bytes=Buffer.from(text),miss=uid('suffix_miss');w('mov r5 r6',`sub r5 ${bytes.length}`,'cmp r5 r4','jlt '+miss);for(const[i,b]of bytes.entries())w('mov r7 r5',`add r7 ${INPUT+BigInt(i)}`,'load8 r3 $r7',`cmp r3 ${b}`,'jne '+miss);w('mov r6 r5');st(OP,7);w('jmp key_size');L(miss);}
 L('key_size');w('sub r6 r4');put(B+100n,6);w('mov r5 r4');
 L('normalize_key');get(6,B+100n);get(5,B+96n);w('cmp r6 1','jlt invalid_key','cmp r6 64','jgt invalid_key');st(KEY_LENGTH,'r6');st(STAGE+1n,'r6');w('set r0 0');L('key_byte');w('cmp r0 r6','jge key_ready','mov r7 r5','add r7 r0',`add r7 ${INPUT}`,'load8 r3 $r7','cmp r3 65','jlt key_store','cmp r3 90','jgt key_store','add r3 32');L('key_store');w(`set r7 ${KEY}`,'add r7 r0','store8 $r7 r3',`set r7 ${STAGE+16n}`,'add r7 r0','store8 $r7 r3','add r0 1','jmp key_byte');
 L('key_ready');ld(0,OP);w('cmp r0 2','jle fields','halt');
 L('fields');get(4,B+104n);ld(0,OP);w('cmp r0 2','jne definition');literal(['revisión: ','revision: ']);w('set r0 0','set r5 0');L('revision_digit');w('cmp r4 r9','jge bad','mov r7 r4',`add r7 ${INPUT}`,'load8 r3 $r7','cmp r3 48','jlt revision_end','cmp r3 57','jgt revision_end','sub r3 48','mul r0 10','add r0 r3','cmp r0 4294967295','jgt bad','add r4 1','add r5 1','cmp r5 10','jgt bad','jmp revision_digit');L('revision_end');w('cmp r5 1','jlt bad');put(B+108n,0);newline();
 L('definition');literal(['definición: ','definicion: ']);field(2,80,224,false);literal(['requiere: ']);field(3,304,224,false);literal(['fuente: ']);field(4,528,32,false);literal(['páginas: ','paginas: ']);field(5,560,32,true);st(STAGE,1);st(STAGE+6n,5);w('halt');
 L('invalid_key');ld(0,OP);w('cmp r0 4','jge unhandled');L('bad');st(STATUS,1);w('halt');L('unhandled');st(MODE,0);st(OP,0);w('halt');return a.source();
 function literal(texts){const done=uid('literal_done');for(const text of texts){const fail=uid('literal_miss'),bytes=Buffer.from(text);w('mov r0 r4',`add r0 ${bytes.length}`,'cmp r0 r9','jgt '+fail);let prior;for(const[i,b]of bytes.entries()){w('mov r7 r4',`add r7 ${INPUT+BigInt(i)}`,'load8 r3 $r7');if((b>=97&&b<=122)||(prior===195&&b>=160&&b<=190&&b!==183)){const good=uid('literal_case');w(`cmp r3 ${b}`,'je '+good,`cmp r3 ${b-32}`,'jne '+fail);L(good);}else w(`cmp r3 ${b}`,'jne '+fail);prior=b;}w(`add r4 ${bytes.length}`,'jmp '+done);L(fail);}w('jmp bad');L(done);}
 function newline(){const lf=uid('newline_lf');w('cmp r4 r9','jge bad','mov r7 r4',`add r7 ${INPUT}`,'load8 r3 $r7','cmp r3 13','jne '+lf,'add r4 1','cmp r4 r9','jge bad','add r7 1','load8 r3 $r7');L(lf);w('cmp r3 10','jne bad','add r4 1');}
 function field(lenoff,start,max,last){const scan=uid('field'),end=uid('field_end'),copy=uid('field_copy'),copied=uid('field_copied'),noCR=uid('field_no_cr');w('mov r5 r4');L(scan);w('cmp r4 r9','jge '+(last?end:'bad'),'mov r7 r4',`add r7 ${INPUT}`,'load8 r3 $r7','cmp r3 10','je '+end,'add r4 1','jmp '+scan);L(end);w('mov r6 r4','sub r6 r5','cmp r6 1','jlt bad','mov r7 r4','sub r7 1',`add r7 ${INPUT}`,'load8 r3 $r7','cmp r3 13','jne '+noCR,'sub r6 1');L(noCR);w('cmp r6 1','jlt bad',`cmp r6 ${max}`,'jgt bad');st(STAGE+BigInt(lenoff),'r6');w('set r0 0');L(copy);w('cmp r0 r6','jge '+copied,'mov r7 r5','add r7 r0',`add r7 ${INPUT}`,'load8 r3 $r7','cmp r3 32','jlt bad','cmp r3 127','je bad',`set r7 ${STAGE+BigInt(start)}`,'add r7 r0','store8 $r7 r3','add r0 1','jmp '+copy);L(copied);if(last){const finished=uid('last_field');w('cmp r4 r9','je '+finished,'add r4 1','cmp r4 r9','jne bad');L(finished);}else w('add r4 1');}
}

export function recordSource(){
 const a=assembler(),{w,L,uid,ld,st,get,put,say,span,uint}=a;
 st(STATUS,0);ld(0,OP);w('cmp r0 8','je status','cmp r0 1','je learn','cmp r0 2','je correct','cmp r0 3','je forget','jmp query');
 L('learn');ld(0,EXISTS);w('cmp r0 1','jne insert','set r4 1');L('same');w('cmp r4 8','je same_payload','cmp r4 592','jge unchanged',`set r7 ${RECORD}`,'add r7 r4','load8 r2 $r7',`set r7 ${STAGE}`,'add r7 r4','load8 r3 $r7','cmp r2 r3','jne conflict','add r4 1','jmp same');L('same_payload');w('set r4 16','jmp same');
 L('insert');get(0,COUNT);get(1,CAPACITY);w('cmp r0 r1','jge full','jmp write');
 L('correct');ld(0,EXISTS);w('cmp r0 1','jne missing');get(0,B+108n);get(1,RECORD+8n);w('cmp r0 r1','jne revision','jmp write');
 L('forget');ld(0,EXISTS);w('cmp r0 0','je unchanged');get(0,REVISION);w('cmp r0 4294967295','jge revision','add r0 1');put(REVISION,0);w('set r4 0');L('erase');w(`set r7 ${RECORD}`,'add r7 r4','store8 $r7 0','add r4 1','cmp r4 640','jlt erase');st(EXISTS,0);get(0,COUNT);w('sub r0 1');put(COUNT,0);say('Lección olvidada.');w('halt');
 L('write');get(0,REVISION);w('cmp r0 4294967295','jge revision','add r0 1');put(REVISION,0);put(STAGE+8n,0);w('set r4 0');L('copy');w(`set r7 ${STAGE}`,'add r7 r4','load8 r3 $r7',`set r7 ${RECORD}`,'add r7 r4','store8 $r7 r3','add r4 1','cmp r4 640','jlt copy');ld(0,EXISTS);w('cmp r0 1','je saved');get(0,COUNT);w('add r0 1');put(COUNT,0);L('saved');st(EXISTS,1);L('unchanged');ld(0,OP);w('cmp r0 3','jne learned');say('Lección olvidada.');w('halt');L('learned');say('Lección incorporada; queda disponible al reabrir esta memoria.');w('halt');
 L('query');ld(0,EXISTS);w('cmp r0 1','jne missing');ld(0,OP);w('cmp r0 6','je source','cmp r0 5','je requirement');span(RECORD,16,1);say(' es ');span(RECORD,80,2);cite();ld(0,OP);w('cmp r0 7','jne done');say(' ');L('requirement');span(RECORD,16,1);say(' requiere ');span(RECORD,304,3);cite();w('halt');
 L('source');say('Fuente enseñada: ');span(RECORD,528,4);say('. Páginas: ');span(RECORD,560,5);say('.');cite();w('halt');
 L('status');say('Banco de entrenamiento paginado: ');get(0,COUNT);uint(0);say(' conceptos, ');get(0,COUNT);w('mul r0 2');uint(0);say(' relaciones. Capacidad: ');get(0,CAPACITY);uint(0);say('. Revisión ');get(0,REVISION);uint(0);say('.');L('done');w('halt');
 for(const[label,code,text]of [['conflict',2,'No cambié el banco: ya existe otra lección para esa clave.'],['missing',3,'No encontré una lección enseñada con esa clave.'],['full',4,'No cambié el banco: se alcanzó la capacidad configurada.'],['revision',5,'No cambié el banco: revisión incompatible o agotada.']]){L(label);st(STATUS,code);say(text);w('halt');}return a.source();
 function cite(){say(' [revisión ');get(0,RECORD+8n);uint(0);say('].');}
}

export function streamSource(){
 const a=assembler(),{w,L,ld,st,get,put}=a;
 get(9,LENGTH);get(8,OFFSET);get(6,START);w('set r4 0');
 L('next');w('cmp r4 r9','jge done','mov r0 r8','add r0 r4','cmp r0 r6','jlt skip');ld(0,ENDED);w('cmp r0 1','je skip',`set r7 ${INPUT}`,'add r7 r4','load8 r3 $r7');ld(0,MODE);w('cmp r0 2','je emit');
 ld(0,PENDING);w('cmp r0 1','jne check_punctuation','cmp r3 32','jle boundary');st(PENDING,0);w('jmp check_punctuation');
 L('boundary');st(PENDING,0);get(0,SEEN);w('add r0 1');put(SEEN,0);ld(1,SENTENCES);w('cmp r0 r1','jlt check_punctuation');st(ENDED,1);w('jmp skip');
 L('check_punctuation');w('cmp r3 33','je punctuation','cmp r3 63','je punctuation','cmp r3 46','jne clear_pending');L('punctuation');st(PENDING,1);w('jmp emit');L('clear_pending');st(PENDING,0);
 L('emit');w('mov r14 r3','print r14');st(PREVIOUS,'r3');L('skip');w('add r4 1','jmp next');L('done');w('halt');return a.source();
}
