// Original lossless per-page LZ byte codec. Offline encoding, native XI decoding.
import {S,OUT,BOOK,PAGES,TEXT} from './schema.mjs';
export function makeDictionary(pages,limit=3500){
 const counts=new Map();for(const p of pages){const words=p.text.match(/\S+\s*/g)||[];for(let i=0;i<words.length;i++)for(let n=1;n<=5&&i+n<=words.length;n++){const text=words.slice(i,i+n).join('');if(Buffer.byteLength(text)>80)break;counts.set(text,(counts.get(text)||0)+1);}}
 const ranked=[...counts].map(([text,count])=>({text,score:count*(Buffer.byteLength(text)-3)-Buffer.byteLength(text)})).filter(x=>x.score>0).sort((a,b)=>b.score-a.score||a.text.localeCompare(b.text,'en'));let result='';for(const r of ranked)if(!result.includes(r.text)&&Buffer.byteLength(result+r.text)<=limit)result+=r.text;return Buffer.from(result);
}
export function encode(bytes,dictionary=Buffer.alloc(0)){
 const data=Buffer.concat([Buffer.from(dictionary),Buffer.from(bytes)]),out=[],positions=new Map();let literal=[];
 const flush=()=>{if(literal.length){out.push(literal.length-1,...literal);literal=[];}};
 for(let p=0;p<dictionary.length;p++){if(p+4>data.length)break;const k=data.subarray(p,p+4).toString('latin1'),list=positions.get(k)||[];list.push(p);if(list.length>32)list.shift();positions.set(k,list);}
 for(let i=dictionary.length;i<data.length;){let best=0,distance=0;const key=i+4<=data.length?data.subarray(i,i+4).toString('latin1'):null;
  if(key)for(const p of (positions.get(key)||[]).slice(-24)){const d=i-p;if(d<1||d>65535)continue;let n=0;while(n<131&&i+n<data.length&&data[p+n]===data[i+n])n++;if(n>best){best=n;distance=d;}}
  const count=best>=4?best:1;if(best>=4){flush();out.push(128+best-4,distance&255,distance>>>8);}else{literal.push(data[i]);if(literal.length===128)flush();}
  for(let j=0;j<count;j++){const p=i+j;if(p+4>data.length)continue;const k=data.subarray(p,p+4).toString('latin1'),list=positions.get(k)||[];list.push(p);if(list.length>32)list.shift();positions.set(k,list);}i+=count;
 }flush();return Buffer.from(out);
}
export function decoder(a){
 const {w,L,get,put,dg,ret}=a;
 L('x8_read_page');get(13,S+300n);w('cmp r13 1','jlt x8_corrupt','cmp r13 122','jgt x8_corrupt','sub r13 1','mul r13 8',`add r13 ${PAGES}`);dg(8,13,0,4);dg(10,13,4,2);dg(9,13,6,2);get(0,BOOK+8n,4);w('mov r1 r8','add r1 r9','cmp r1 r0','jgt x8_corrupt','cmp r10 16384','jgt x8_corrupt',`add r8 ${TEXT}`,'set r4 0');get(2,BOOK+14n);w('cmp r2 3500','jgt x8_corrupt','set r6 0');L('x8_lz_dictionary');w('cmp r6 r2','jge x8_lz_dictionary_ready',`set r7 ${BOOK+128n}`,'add r7 r6','load8 r3 $r7',`set r7 ${OUT}`,'add r7 r6','store8 $r7 r3','add r6 1','jmp x8_lz_dictionary');L('x8_lz_dictionary_ready');w('add r10 r2');
 L('x8_lz_token');w('cmp r4 r9','jge x8_lz_done','mov r7 r8','add r7 r4','load8 r3 $r7','add r4 1','cmp r3 128','jge x8_lz_match','mov r11 r3','add r11 1','mov r0 r4','add r0 r11','cmp r0 r9','jgt x8_corrupt','mov r0 r6','add r0 r11','cmp r0 r10','jgt x8_corrupt');
 L('x8_lz_literal');w('cmp r11 0','je x8_lz_token','mov r7 r8','add r7 r4','load8 r3 $r7',`set r7 ${OUT}`,'add r7 r6','store8 $r7 r3','add r4 1','add r6 1','sub r11 1','jmp x8_lz_literal');
 L('x8_lz_match');w('mov r11 r3','sub r11 124','mov r0 r4','add r0 2','cmp r0 r9','jgt x8_corrupt','mov r7 r8','add r7 r4','load8 r5 $r7','add r7 1','load8 r3 $r7','mul r3 256','add r5 r3','add r4 2','cmp r5 1','jlt x8_corrupt','cmp r5 r6','jgt x8_corrupt','mov r0 r6','add r0 r11','cmp r0 r10','jgt x8_corrupt');
 L('x8_lz_copy');w('cmp r11 0','je x8_lz_token',`set r7 ${OUT}`,'add r7 r6','sub r7 r5','load8 r3 $r7','add r7 r5','store8 $r7 r3','add r6 1','sub r11 1','jmp x8_lz_copy');
 L('x8_lz_done');w('cmp r6 r10','jne x8_corrupt');put(S+202n,6);w(`set r8 ${OUT}`,'add r8 r2','mov r1 r6','sub r1 r2');ret();
}
