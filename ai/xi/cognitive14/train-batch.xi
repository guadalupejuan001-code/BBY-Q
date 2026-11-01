#!reverse-pc-machine-v1
# Batch training in XI; host stages context/action pairs, NEVER holdout examples.
load8 r0 8270000000000000000
cmp r0 14
jne c14_invalid
load8 r1 8270000000000000004
load8 r2 8270000000000000005
mul r2 256
add r1 r2
cmp r1 1
jlt c14_invalid
cmp r1 800
jgt c14_invalid
set r3 0
label c14_sample
mov r7 r3
mul r7 2
add r7 8270000000000003000
load8 r4 $r7
add r7 1
load8 r5 $r7
cmp r4 143
jgt c14_invalid
cmp r5 3
jgt c14_invalid
mov r8 r4
mul r8 4
add r8 r5
mul r8 2
add r8 8270000000000000100
load8 r9 $r8
add r8 1
load8 r10 $r8
mul r10 256
add r9 r10
cmp r9 65535
jge c14_invalid
add r9 1
mov r11 r9
mod r11 256
sub r8 1
store8 $r8 r11
mov r11 r9
div r11 256
add r8 1
store8 $r8 r11
store8 $r7 0
sub r7 1
store8 $r7 0
add r3 1
cmp r3 r1
jlt c14_sample
load8 r12 8270000000000000006
load8 r13 8270000000000000007
mul r13 256
add r12 r13
add r12 r1
cmp r12 65535
jgt c14_invalid
mov r11 r12
mod r11 256
store8 8270000000000000006 r11
mov r11 r12
div r11 256
store8 8270000000000000007 r11
store8 8270000000000000004 0
store8 8270000000000000005 0
print r1
print r12
halt
label c14_invalid
div r0 0
