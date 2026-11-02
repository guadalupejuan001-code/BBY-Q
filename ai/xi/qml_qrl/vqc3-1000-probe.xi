#!reverse-pc-machine-v1
# Single-observation native XI policy/classifier output, tied to real 1000-qubit circuit.
# Input group 0..110 at +1, site 0..8 at +2, probe token 242 at +6.
load8 r0 8340000000000000000
cmp r0 103
jne invalid
load8 r1 8340000000000000001
cmp r1 110
jgt invalid
load8 r2 8340000000000000002
cmp r2 8
jgt invalid
load8 r3 8340000000000000006
cmp r3 242
jne invalid
mov r4 r1
add r4 8340000000000000256
load8 r5 $r4
cmp r5 1
jgt invalid
mov r6 r1
mul r6 9
add r6 r2
add r6 2001
expect Z:2000 Z:$r6
print r1
print r2
print r5
print r6
halt
label invalid
div r0 0
