#!reverse-pc-machine-v1
# C03 QRL de un paso: politica tabular contextual, objetivo |0> o |1>.
# Q(contexto,accion) en Ether (u16); reward=2000+fidelidad_Q10000-penalidad*k.
load8 r0 8100000000000000000
cmp r0 81
jne invalid
load8 r0 8100000000000002000
cmp r0 0
jne invalid
store8 8100000000000002000 82
store8 8100000000000002001 0
store8 8100000000000002002 40
store8 8100000000000002003 1
store8 8100000000000002004 0
store8 8100000000000002005 255
store8 8100000000000002006 255
store8 8100000000000002007 0
set r1 0
label clear_q
mov r2 r1
mul r2 2
add r2 8100000000000002100
store8 $r2 0
add r2 1
store8 $r2 0
add r1 1
cmp r1 16
jlt clear_q
set r0 82
print r0
halt
label invalid
div r0 0
