#!reverse-pc-machine-v1
# New memory namespace and disjoint qubit ranges preserve every older model.
# Refuse to overwrite an existing V3 model.
load8 r0 8140000000000001000
cmp r0 0
jne birth_invalid
store8 8140000000000001000 174
store64 8140000000000000256 312771
store64 8140000000000000280 0
store64 8140000000000000000 0
label birth_agent
call select_agent
store64 $r12 0
mov r0 r12
add r0 8
store64 $r0 0
add r0 8
fstore $r0 0
add r0 8
fstore $r0 0.3
add r0 8
fstore $r0 0.002
add r0 8
fstore $r0 0
set r2 0
label birth_parameters
mov r0 r2
mul r0 8
add r0 r13
fstore $r0 0.31
add r0 10000
fstore $r0 0
add r0 10000
store64 $r0 0
add r2 1
cmp r2 1000
jlt birth_parameters
qmps $r15 1000
load64 r0 8140000000000000000
cmp r0 1
je birth_done
store64 8140000000000000000 1
jmp birth_agent
label birth_done
stats
halt
label birth_invalid
div r0 0
