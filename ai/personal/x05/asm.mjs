// Offline XI assembler conveniences. No message-dependent execution in JavaScript.
export const B=9090000000000000000n,S=B+100000n,I=7400000000000000128n,C=S+512n,T=S+2048n,V=S+2560n,O=S+4352n,H=S+4480n,PS=S+1024n,PE=S+1984n,G=S+6144n,RS=S+7500n;
export const LIMIT=1000000000;
export function assembler(){
 const lines=[],returns=[];let serial=0;
 const w=(...s)=>lines.push(...s),L=s=>w('label '+s),uid=s=>'x5_'+s+'_'+serial++,ld=(r,p)=>w(`load8 r${r} ${p}`),st=(p,v)=>w(`store8 ${p} ${v}`),say=s=>{for(const b of Buffer.from(s))w(`set r14 ${b}`,'print r14');};
 function get(r,p,n=2){ld(r,p);for(let i=1;i<n;i++){ld(14,p+BigInt(i));w(`mul r14 ${256**i}`,`add r${r} r14`);}}
 function put(p,r,n=2){for(let i=0;i<n;i++){w(`mov r14 r${r}`);if(i)w(`div r14 ${256**i}`);w('mod r14 256');st(p+BigInt(i),'r14');}}
 function dg(r,base,off,n=1){w(`mov r7 r${base}`,`add r7 ${off}`,`load8 r${r} $r7`);for(let i=1;i<n;i++)w('add r7 1','load8 r14 $r7',`mul r14 ${256**i}`,`add r${r} r14`);}
 function dp(base,off,r,n=1){for(let i=0;i<n;i++){w(`mov r7 r${base}`,`add r7 ${off+i}`,`mov r14 r${r}`);if(i)w(`div r14 ${256**i}`);w('mod r14 256','store8 $r7 r14');}}
 function sg(r,base,off){const ok=uid('sg');dg(r,base,off+1,4);dg(14,base,off);w('cmp r14 0','je '+ok,`mul r${r} -1`);L(ok);}
 function sp(base,off,r){const pos=uid('sp'),done=uid('sp_done');w(`mov r15 r${r}`,`mov r7 r${base}`,`add r7 ${off}`,'store8 $r7 0','cmp r15 0','jge '+pos,'store8 $r7 1','mul r15 -1');L(pos);dp(base,off+1,15,4);L(done);}
 function zero(base,n,tag='zero'){const loop=uid(tag);w('set r0 0');L(loop);w(`set r7 ${base}`,'add r7 r0','store8 $r7 0','add r0 1',`cmp r0 ${n}`,'jlt '+loop);}
 function copy(src,dst,n){const loop=uid('copy');w('set r0 0');L(loop);w(`set r7 ${src}`,'add r7 r0','load8 r3 $r7',`set r7 ${dst}`,'add r7 r0','store8 $r7 r3','add r0 1',`cmp r0 ${n}`,'jlt '+loop);}
 function call(name){const id=returns.length+1,label=uid('return');returns.push({id,label});ld(12,S+100n);w('cmp r12 16','jge x5_corrupt','mov r7 r12','mul r7 2',`add r7 ${RS}`,`store8 $r7 ${id%256}`,'add r7 1',`store8 $r7 ${Math.floor(id/256)}`,'add r12 1');st(S+100n,'r12');w('jmp '+name);L(label);}
 function ret(){w('jmp x5_return');}
 function dispatch(){L('x5_return');ld(12,S+100n);w('cmp r12 1','jlt x5_corrupt','sub r12 1');st(S+100n,'r12');w('mov r7 r12','mul r7 2',`add r7 ${RS}`,'load8 r12 $r7','add r7 1','load8 r14 $r7','mul r14 256','add r12 r14');for(const {id,label}of returns)w(`cmp r12 ${id}`,'je '+label);w('jmp x5_corrupt');}
 function match(text,pos,end,yes,no,{exact=false}={}){const bytes=Buffer.from(text);ld(8,pos);ld(9,end);w('mov r0 r8',`add r0 ${bytes.length}`,'cmp r0 r9',`${exact?'jne':'jgt'} ${no}`);for(const[i,b]of bytes.entries())w(`set r7 ${C}`,'add r7 r8',`add r7 ${i}`,'load8 r3 $r7',`cmp r3 ${b}`,'jne '+no);st(S+104n,'r0');w('jmp '+yes);}
 function alts(texts,pos,end,yes,no,exact=false){for(const text of texts){const miss=uid('match_miss');match(text,pos,end,yes,miss,{exact});L(miss);}w('jmp '+no);}
 function emit(){const loop=uid('emit'),end=uid('emit_end');w('set r0 0');L(loop);w('cmp r0 r1','jge '+end,'mov r7 r8','add r7 r0','load8 r14 $r7','print r14','add r0 1','jmp '+loop);L(end);}
 return {lines,w,L,uid,ld,st,say,get,put,dg,dp,sg,sp,zero,copy,call,ret,dispatch,match,alts,emit};
}
