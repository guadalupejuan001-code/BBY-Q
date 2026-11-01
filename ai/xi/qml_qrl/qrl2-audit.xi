#!reverse-pc-machine-v1
# C06: volcado de los 16 Q de la politica de dos pasos (solo lectura).
load8 r0 8100000000000005000
cmp r0 83
jne invalid
set r1 0
label record
mov r2 r1
mul r2 2
add r2 8100000000000005100
load8 r5 $r2
add r2 1
load8 r6 $r2
mul r6 256
add r5 r6
print r5
add r1 1
cmp r1 16
jlt record
halt
label invalid
div r0 0
