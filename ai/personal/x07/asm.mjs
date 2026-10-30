// Offline XI code assembly only. All live parsing and planning execute in XI.
import {S,P,E,RS,C} from './schema.mjs';
export function assembler(){
 const lines=[],returns=[];let serial=0;
 const w=(...v)=>lines.push(...v),L=l=>w('label '+l),uid=t=>'x7_'+t+'_'+serial++,ld=(r,p)=>w(`load8 r${r} ${p}`),st=(p,v)=>w(`store8 ${p} ${v}`);
 const say=text=>{for(const b of Buffer.from(text))w(`set r14 ${b}`,'print r14');};
 function get(r,p,n=2){ld(r,p);for(let i=1;i<n;i++){ld(14,p+BigInt(i));w(`mul r14 ${256n**BigInt(i)}`,`add r${r} r14`);}}
 function put(p,r,n=2){for(let i=0;i<n;i++){w(`mov r14 r${r}`);if(i)w(`div r14 ${256n**BigInt(i)}`);w('mod r14 256');st(p+BigInt(i),'r14');}}
 function dg(r,base,off,n=1){w(`mov r7 r${base}`,`add r7 ${off}`,`load8 r${r} $r7`);for(let i=1;i<n;i++)w('add r7 1','load8 r14 $r7',`mul r14 ${256n**BigInt(i)}`,`add r${r} r14`);}
 function dp(base,off,r,n=1){for(let i=0;i<n;i++){w(`mov r7 r${base}`,`add r7 ${off+i}`,`mov r14 r${r}`);if(i)w(`div r14 ${256n**BigInt(i)}`);w('mod r14 256','store8 $r7 r14');}}
 function zero(base,n,tag='zero'){const loop=uid(tag);w('set r0 0');L(loop);w(`set r7 ${base}`,'add r7 r0','store8 $r7 0','add r0 1',`cmp r0 ${n}`,'jlt '+loop);}
 function copy(src,dst,n){const loop=uid('copy');w('set r0 0');L(loop);w(`set r7 ${src}`,'add r7 r0','load8 r3 $r7',`set r7 ${dst}`,'add r7 r0','store8 $r7 r3','add r0 1',`cmp r0 ${n}`,'jlt '+loop);}
 function call(name){const id=returns.length+1,label=uid('return');returns.push({id,label});ld(12,S+100n);w('cmp r12 16','jge x7_corrupt','mov r7 r12','mul r7 2',`add r7 ${RS}`,`store8 $r7 ${id%256}`,'add r7 1',`store8 $r7 ${Math.floor(id/256)}`,'add r12 1');st(S+100n,'r12');w('jmp '+name);L(label);}
 function ret(){w('jmp x7_return');}
 function dispatch(){L('x7_return');ld(12,S+100n);w('cmp r12 1','jlt x7_corrupt','sub r12 1');st(S+100n,'r12');w('mov r7 r12','mul r7 2',`add r7 ${RS}`,'load8 r12 $r7','add r7 1','load8 r14 $r7','mul r14 256','add r12 r14');for(const{id,label}of returns)w(`cmp r12 ${id}`,'je '+label);w('jmp x7_corrupt');}
 function bytes(text,baseReg,positionReg,fail){let previous;for(const[i,b]of Buffer.from(text).entries()){w(`mov r7 r${baseReg}`,`add r7 r${positionReg}`,`add r7 ${i}`,'load8 r3 $r7',`cmp r3 ${b}`);if((b>=97&&b<=122)||(previous===195&&b>=160&&b<=190&&b!==183)){const good=uid('case');w('je '+good,`cmp r3 ${b-32}`,'jne '+fail);L(good);}else w('jne '+fail);previous=b;}}
 function match(text,yes,no,{exact=false,raw=false}={}){const n=Buffer.byteLength(text);if(raw)w('set r4 0');else get(4,P);if(!raw)get(9,E);w('mov r6 r4',`add r6 ${n}`,'cmp r6 r9',`${exact?'jne':'jgt'} ${no}`);if(!raw)w(`set r8 ${C}`);bytes(text,8,4,no);if(!raw)put(P,6);w('jmp '+yes);}
 function alts(texts,yes,no,options={}){for(const t of texts){const next=uid('miss');match(t,yes,next,options);L(next);}w('jmp '+no);}
 function consume(texts,fail='x7_format'){const yes=uid('consume');alts(Array.isArray(texts)?texts:[texts],yes,fail);L(yes);}
 function emit(){const loop=uid('emit'),done=uid('emitted');w('set r0 0');L(loop);w('cmp r0 r1','jge '+done,'mov r7 r8','add r7 r0','load8 r14 $r7','print r14','add r0 1','jmp '+loop);L(done);}
 return{lines,w,L,uid,ld,st,say,get,put,dg,dp,zero,copy,call,ret,dispatch,match,alts,consume,emit};
}
