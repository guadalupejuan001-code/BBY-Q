#!reverse-pc-machine-v1
# C03 Ejecutor de la politica QRL. Reporta fidelidad analitica y test Born nativo.
load8 r0 8100000000000000000
cmp r0 81
jne invalid
load8 r0 8100000000000002000
cmp r0 82
jne invalid
load8 r0 8100000000000002004
cmp r0 1
jne invalid
load8 r9 8100000000000002003
cmp r9 1
jgt invalid
cmp r9 0
jne objective_one
load8 r8 8100000000000002005
jmp chosen
label objective_one
load8 r8 8100000000000002006
label chosen
cmp r8 7
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
set r5 10000
cmp r9 0
je wanted_zero
sub r5 r7
jmp fid_ready
label wanted_zero
add r5 r7
label fid_ready
div r5 2
mov r4 r5
add r4 2000
load8 r12 8100000000000002002
mov r13 r8
mul r13 r12
sub r4 r13
print r8
print r5
print r4
load8 r14 8100000000000002007
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
# Uncompute para devolver a |0> sin colapso.
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
probz $r14
halt
label invalid
div r0 0
