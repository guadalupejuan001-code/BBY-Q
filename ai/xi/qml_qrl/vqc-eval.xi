#!reverse-pc-machine-v1
# C02 evaluacion estrictamente holdout; no altera modelo ni muestras.
load8 r0 8100000000000000000
cmp r0 81
jne invalid
load8 r0 8100000000000001000
cmp r0 86
jne invalid
load8 r0 8100000000000001003
cmp r0 1
jne invalid
load8 r1 8100000000000001007
cmp r1 1
jlt invalid
cmp r1 16
jgt invalid
load8 r2 8100000000000001002
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
add r14 8100000000000001300
load8 r9 $r14
cmp r9 1
jgt invalid
mov r10 r9
mul r10 2
set r12 1
sub r12 r10
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
add r12 8100000000000001400
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
