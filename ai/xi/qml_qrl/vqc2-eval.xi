#!reverse-pc-machine-v1
# C05: evaluacion holdout XOR/XNOR, estrictamente sin escrituras Ether.
load8 r0 8100000000000004000
cmp r0 87
jne invalid
load8 r0 8100000000000004003
cmp r0 1
jne invalid
load8 r1 8100000000000004007
cmp r1 1
jlt invalid
cmp r1 16
jgt invalid
load8 r2 8100000000000004002
cmp r2 7
jgt invalid
mul r2 2
add r2 8100000000000000100
load8 r7 $r2
add r2 1
load8 r8 $r2
mul r8 256
add r7 r8
sub r7 10000
set r6 0
set r11 0
set r5 0
label sample
mov r14 r6
add r14 8100000000000004400
load8 r9 $r14
cmp r9 1
jgt invalid
mov r14 r6
add r14 8100000000000004500
load8 r10 $r14
cmp r10 1
jgt invalid
add r9 r10
mod r9 2
mul r9 2
set r12 1
sub r12 r9
mul r12 r7
set r13 10000
sub r13 r12
div r13 2
set r14 0
cmp r13 5000
jlt predicted
set r14 1
label predicted
mov r12 r6
add r12 8100000000000004600
load8 r10 $r12
cmp r10 1
jgt invalid
cmp r14 r10
jne wrong
add r11 1
label wrong
mul r10 10000
sub r13 r10
mul r13 r13
div r13 10000
add r5 r13
add r6 1
cmp r6 r1
jlt sample
print r11
print r5
halt
label invalid
div r0 0
