#!reverse-pc-machine-v1
# Infer one of two DESIGNED rule families from witnessed consequences.
# At inference time every stored witness is re-read; stale witnesses cannot
# preserve an enabled rule. A duplicate witness never supplies new support.
load8 r10 7800000000000000248
cmp r10 1
jlt invalid
load8 r0 7800000000000000074
load8 r14 7800000000000000075
mul r14 256
add r0 r14
set r12 7800000000002000000
mul r0 64
add r12 r0
load8 r11 $r12
load8 r2 7800000000000000240
load8 r14 7800000000000000241
mul r14 256
add r2 r14
load8 r3 7800000000000000242
load8 r14 7800000000000000243
mul r14 256
add r3 r14
load8 r4 7800000000000000244
load8 r14 7800000000000000245
mul r14 256
add r4 r14
set r0 0
label duplicate
cmp r0 r11
jge append
mov r7 r12
add r7 4
mov r1 r0
mul r1 6
add r7 r1
mov r15 r7
load8 r1 $r15
add r15 1
load8 r14 $r15
mul r14 256
add r1 r14
cmp r1 r2
jne next
add r7 2
mov r15 r7
load8 r1 $r15
add r15 1
load8 r14 $r15
mul r14 256
add r1 r14
cmp r1 r3
jne next
add r7 2
mov r15 r7
load8 r1 $r15
add r15 1
load8 r14 $r15
mul r14 256
add r1 r14
cmp r1 r4
je done
label next
add r0 1
jmp duplicate
label append
cmp r11 6
jge invalid
mov r7 r12
add r7 1
load8 r1 $r7
cmp r11 0
je candidate_ready
set r5 0
mov r0 r10
mod r0 2
cmp r0 0
je second
mov r0 r1
mod r0 2
cmp r0 0
je second
add r5 1
label second
cmp r10 2
jlt candidate
cmp r1 2
jlt candidate
add r5 2
label candidate
mov r10 r5
cmp r10 0
je invalid
label candidate_ready
store8 $r7 r10
mov r7 r12
add r7 4
mov r0 r11
mul r0 6
add r7 r0
mov r15 r7
mov r14 r2
mod r14 256
store8 $r15 r14
add r15 1
mov r14 r2
div r14 256
store8 $r15 r14
add r7 2
mov r15 r7
mov r14 r3
mod r14 256
store8 $r15 r14
add r15 1
mov r14 r3
div r14 256
store8 $r15 r14
add r7 2
mov r15 r7
mov r14 r4
mod r14 256
store8 $r15 r14
add r15 1
mov r14 r4
div r14 256
store8 $r15 r14
add r11 1
store8 $r12 r11
label done
halt
label invalid
div r0 0
