#!reverse-pc-machine-v1
# VQC discreto U(k,x)=H*T^k*H*X^x; k=0..7, theta=k*pi/4.
# Entrenamiento Brier Q10000 por busqueda completa (XI), penalidad 10*k.
load8 r0 8100000000000000000
cmp r0 81
jne invalid
load8 r0 8100000000000001000
cmp r0 86
jne invalid
load8 r0 8100000000000001003
cmp r0 0
jne invalid
load8 r1 8100000000000001001
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
add r14 8100000000000001100
load8 r9 $r14
cmp r9 1
jgt invalid
mov r14 r6
add r14 8100000000000001200
load8 r10 $r14
cmp r10 1
jgt invalid
mov r11 r9
mul r11 2
set r12 1
sub r12 r11
mul r12 r7
set r13 10000
sub r13 r12
div r13 2
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
store8 8100000000000001002 r4
mov r15 r3
mod r15 256
store8 8100000000000001004 r15
mov r15 r3
div r15 256
mod r15 256
store8 8100000000000001005 r15
mov r15 r3
div r15 65536
store8 8100000000000001006 r15
store8 8100000000000001003 1
print r4
print r3
halt
label invalid
div r0 0
