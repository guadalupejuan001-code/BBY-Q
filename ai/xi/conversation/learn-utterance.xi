#!reverse-pc-machine-v1
# Supervised fixed dialogue acts, not a claim of generative learning.
# 7700000000000000016=1,7700000000000000017=act(1..8), K raw bytes and language. Repeats must agree.
load8 r0 7700000000000000002
cmp r0 1
jne invalid
load8 r0 7700000000000000016
cmp r0 1
jne invalid
load8 r0 7400000000000000016
cmp r0 1
jne invalid
load8 r0 7700000000000000017
cmp r0 1
jlt invalid
cmp r0 8
jgt invalid
load8 r1 7400000000000000003
cmp r1 1
jlt invalid
cmp r1 2
jgt invalid
load8 r15 7400000000000000017
cmp r15 1
jlt invalid
set r7 7700000000000002000
sub r0 1
mul r0 512
add r7 r0
sub r1 1
mul r1 256
add r7 r1
load8 r2 $r7
cmp r2 0
je write
cmp r2 r15
jne invalid
set r0 0
label compare
cmp r0 r15
jge done
mov r8 r7
add r8 1
add r8 r0
load8 r2 $r8
set r8 7400000000000000128
add r8 r0
load8 r3 $r8
cmp r2 r3
jne invalid
add r0 1
jmp compare
label write
store8 $r7 r15
set r0 0
label copy
cmp r0 r15
jge done
set r8 7400000000000000128
add r8 r0
load8 r2 $r8
mov r8 r7
add r8 1
add r8 r0
store8 $r8 r2
add r0 1
jmp copy
label done
halt
label invalid
div r0 0
