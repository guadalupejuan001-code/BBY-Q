#!/usr/bin/env node
// Build-time XI source emitter only. No JavaScript runs when BBY Q answers.
import fs from 'node:fs';
import {fillers,prefixes,intentAliases} from './extension.mjs';
const N=8800000000000000000n, I=7400000000000000128n, L=7400000000000000017n;
const buf=N+256n, out=N+512n;
const code=[]; const emit=(...s)=>code.push(...s);
emit('#!reverse-pc-machine-v1','# F002: bounded query normalization. Original non-query input is preserved.',
 `load8 r0 ${L}`,'set r1 0','set r2 0','label f002_norm',
 'cmp r1 r0','jge f002_trim',`set r7 ${I}`,'add r7 r1','load8 r3 $r7',
 'cmp r3 194','je f002_inverted','cmp r3 195','je f002_accent','jmp f002_ascii',
 'label f002_inverted','mov r7 r1','add r7 1','cmp r7 r0','jge f002_ascii',`add r7 ${I}`,'load8 r4 $r7','cmp r4 191','jne f002_ascii','add r1 2','jmp f002_norm',
 'label f002_accent','mov r7 r1','add r7 1','cmp r7 r0','jge f002_ascii',`add r7 ${I}`,'load8 r4 $r7');
for(const [v,bytes] of [['a',[129,161]],['e',[137,169]],['i',[141,173]],['o',[147,179]],['u',[154,186,156,188]]]){
 for(const b of bytes)emit(`cmp r4 ${b}`,`je f002_accent_${v}`);
}
emit('jmp f002_ascii');
for(const v of ['a','e','i','o','u'])emit(`label f002_accent_${v}`,`set r3 ${v.charCodeAt(0)}`,'add r1 1','jmp f002_ascii');
emit('label f002_ascii','cmp r3 65','jlt f002_punctuation','cmp r3 90','jgt f002_punctuation','add r3 32',
 'label f002_punctuation','cmp r3 63','je f002_skip','cmp r3 44','jne f002_space','set r3 32',
 'label f002_space','cmp r3 32','jne f002_store','cmp r2 0','je f002_skip',`set r7 ${buf}`,'add r7 r2','sub r7 1','load8 r4 $r7','cmp r4 32','je f002_skip',
 'label f002_store',`set r7 ${buf}`,'add r7 r2','store8 $r7 r3','add r2 1',
 'label f002_skip','add r1 1','jmp f002_norm',
 'label f002_trim','cmp r2 0','je f002_cleanup',`set r7 ${buf}`,'add r7 r2','sub r7 1','load8 r3 $r7','cmp r3 32','jne f002_start','sub r2 1',
 'label f002_start','set r6 0','set r8 0','label f002_fillers','cmp r8 4','jge f002_alias_0');
function match(text,next,exact=false){
 const a=Buffer.from(text);emit('mov r7 r2','sub r7 r6',`cmp r7 ${a.length}`,`${exact?'jne':'jlt'} ${next}`);
 for(const [i,b] of a.entries())emit(`set r7 ${buf+BigInt(i)}`,'add r7 r6','load8 r3 $r7',`cmp r3 ${b}`,`jne ${next}`);
}
for(const [i,f] of fillers.entries()){
 emit(`label f002_filler_${i}`);match(f,i===fillers.length-1?'f002_alias_0':`f002_filler_${i+1}`);
 emit(`add r6 ${Buffer.byteLength(f)}`,'add r8 1','jmp f002_fillers');
}
for(const [i,[from,to]] of intentAliases.entries()){
 emit(`label f002_alias_${i}`);match(from,i===intentAliases.length-1?'f002_pattern_0':`f002_alias_${i+1}`,true);
 for(const [j,b] of Buffer.from(to).entries())emit(`store8 ${out+BigInt(j)} ${b}`);
 emit(`set r12 ${Buffer.byteLength(to)}`,'jmp f002_commit');
}
for(const [i,[from,to]] of prefixes.entries()){
 emit(`label f002_pattern_${i}`);match(from,i===prefixes.length-1?'f002_cleanup':`f002_pattern_${i+1}`);
 emit('mov r10 r6',`add r10 ${Buffer.byteLength(from)}`,'cmp r10 r2','jge f002_cleanup','mov r12 r2','sub r12 r10',`add r12 ${Buffer.byteLength(to)}`,'cmp r12 255','jgt f002_cleanup');
 for(const [j,b] of Buffer.from(to).entries())emit(`store8 ${out+BigInt(j)} ${b}`);
 emit(`set r11 ${Buffer.byteLength(to)}`,'jmp f002_copy_tail');
}
emit('label f002_copy_tail','cmp r10 r2','jge f002_commit',`set r7 ${buf}`,'add r7 r10','load8 r3 $r7',`set r7 ${out}`,'add r7 r11','store8 $r7 r3','add r10 1','add r11 1','jmp f002_copy_tail',
 'label f002_commit','set r0 0','label f002_commit_loop','cmp r0 r12','jge f002_commit_length',`set r7 ${out}`,'add r7 r0','load8 r3 $r7',`set r7 ${I}`,'add r7 r0','store8 $r7 r3','add r0 1','jmp f002_commit_loop',
 'label f002_commit_length',`store8 ${L} r12`,'label f002_clear_tail','cmp r0 256','jge f002_cleanup',`set r7 ${I}`,'add r7 r0','store8 $r7 0','add r0 1','jmp f002_clear_tail',
 'label f002_cleanup','set r0 0','label f002_cleanup_loop','cmp r0 768','jge f002_delegate',`set r7 ${N+256n}`,'add r7 r0','store8 $r7 0','add r0 1','jmp f002_cleanup_loop','label f002_delegate');
for(let r=0;r<16;r++)emit(`set r${r} 0`);
const target=process.argv[2];if(!target)throw Error('Usage: node build-normalizer.mjs OUTPUT.xi');fs.writeFileSync(target,code.join('\n')+'\n');
