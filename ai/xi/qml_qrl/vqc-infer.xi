#!reverse-pc-machine-v1
# C02 inferencia XI: reporta p1 analitica + Born real simulado y deshace circuito.
load8 r0 8100000000000000000
cmp r0 81
jne invalid
load8 r0 8100000000000001000
cmp r0 86
jne invalid
load8 r0 8100000000000001003
cmp r0 1
jne invalid
load8 r8 8100000000000001002
cmp r8 7
jgt invalid
load8 r9 8100000000000001500
cmp r9 1
jgt invalid
mov r10 r8
mul r10 2
add r10 8100000000000000100
load8 r7 $r10
add r10 1
load8 r11 $r10
mul r11 256
add r7 r11
sub r7 10000
mov r12 r9
mul r12 2
set r13 1
sub r13 r12
mul r13 r7
set r12 10000
sub r12 r13
div r12 2
print r8
print r12
load8 r14 8100000000000001501
cmp r9 1
jne mapped
x $r14
label mapped
h $r14
set r15 0
label forward_t
cmp r15 r8
jge forward_done
t $r14
add r15 1
jmp forward_t
label forward_done
h $r14
expect Z:$r14
probz $r14
# Uncompute sin medicion: H*Tdg^k*H*X^x = U^-1.
h $r14
set r15 0
label reverse_t
cmp r15 r8
jge reverse_done
tdg $r14
add r15 1
jmp reverse_t
label reverse_done
h $r14
cmp r9 1
jne unmapped
x $r14
label unmapped
probz $r14
halt
label invalid
div r0 0
