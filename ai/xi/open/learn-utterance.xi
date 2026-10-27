#!reverse-pc-machine-v1
# Explicit structured surface lesson, no inference or ready exam answers.
load8 r0 7800000000000000002
cmp r0 1
jne invalid
load8 r0 7800000000000000304
cmp r0 1
jlt invalid
cmp r0 15
jgt invalid
sub r0 1
mul r0 512
set r7 7800000000000500000
add r7 r0
load8 r0 7400000000000000003
sub r0 1
mul r0 256
add r7 r0
load8 r6 7400000000000000017
cmp r6 1
jlt invalid
load8 r0 $r7
cmp r0 0
je write
cmp r0 r6
jne invalid
set r0 0
label compare
cmp r0 r6
jge done
mov r8 r7
add r8 1
add r8 r0
load8 r1 $r8
set r8 7400000000000000128
add r8 r0
load8 r2 $r8
cmp r1 r2
jne invalid
add r0 1
jmp compare
label write
store8 $r7 r6
set r0 0
label copy
cmp r0 r6
jge done
set r8 7400000000000000128
add r8 r0
load8 r1 $r8
mov r8 r7
add r8 1
add r8 r0
store8 $r8 r1
add r0 1
jmp copy
label done
halt
label invalid
div r0 0
