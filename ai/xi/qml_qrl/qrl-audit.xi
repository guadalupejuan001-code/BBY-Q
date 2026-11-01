#!reverse-pc-machine-v1
# Auditor XI de la tabla Q: 16 valores persistentes, en orden objetivo 0/1, k=0..7.
load8 r0 8100000000000002000
cmp r0 82
jne invalid
load8 r1 8100000000000002001
print r1
set r2 0
label action
mov r6 r2
mul r6 2
add r6 8100000000000002100
load8 r3 $r6
add r6 1
load8 r4 $r6
mul r4 256
add r3 r4
mov r5 r3
print r5
add r2 1
cmp r2 16
jlt action
halt
label invalid
div r0 0
