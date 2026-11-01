#!reverse-pc-machine-v1
# C05: busqueda discreta k=0..7 en pares x0,x1, costo Brier y regularizacion.
load8 r0 8100000000000000000
cmp r0 81
jne invalid
load8 r0 8100000000000004000
cmp r0 87
jne invalid
load8 r1 8100000000000004001
cmp r1 1
jlt invalid
cmp r1 16
jgt invalid
set r2 0
set r3 9223372036854775807
set r4 0
label candidate
mov r14 r2
mul r14 2
add r14 8100000000000000100
load8 r7 $r14
add r14 1
load8 r8 $r14
mul r8 256
add r7 r8
sub r7 10000
set r5 0
set r6 0
label sample
mov r14 r6
add r14 8100000000000004100
load8 r9 $r14
cmp r9 1
jgt invalid
mov r14 r6
add r14 8100000000000004200
load8 r10 $r14
cmp r10 1
jgt invalid
add r9 r10
mod r9 2
mov r11 r9
mul r11 2
set r12 1
sub r12 r11
mul r12 r7
set r13 10000
sub r13 r12
div r13 2
mov r14 r6
add r14 8100000000000004300
load8 r10 $r14
cmp r10 1
jgt invalid
mul r10 10000
sub r13 r10
mul r13 r13
div r13 10000
add r5 r13
add r6 1
cmp r6 r1
jlt sample
mov r15 r2
mul r15 10
add r5 r15
cmp r5 r3
jge next_candidate
mov r3 r5
mov r4 r2
label next_candidate
add r2 1
cmp r2 8
jlt candidate
store8 8100000000000004002 r4
mov r15 r3
mod r15 256
store8 8100000000000004004 r15
mov r15 r3
div r15 256
mod r15 256
store8 8100000000000004005 r15
mov r15 r3
div r15 65536
store8 8100000000000004006 r15
store8 8100000000000004003 1
print r4
print r3
halt
label invalid
div r0 0
