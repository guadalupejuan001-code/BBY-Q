#!reverse-pc-machine-v1
# Test independiente: los 8 angulos discretos pasan por H T^k H sobre |0>.
# Cada trayectoria es deshecha sin observacion proyectiva; solo consultas Born.
load8 r0 8100000000000000000
cmp r0 81
jne invalid
set r8 0
set r14 0
label angle
print r8
h $r14
set r15 0
label t_forward
cmp r15 r8
jge observe
t $r14
add r15 1
jmp t_forward
label observe
h $r14
probz $r14
h $r14
set r15 0
label t_inverse
cmp r15 r8
jge reset
tdg $r14
add r15 1
jmp t_inverse
label reset
h $r14
probz $r14
add r8 1
cmp r8 8
jlt angle
halt
label invalid
div r0 0
