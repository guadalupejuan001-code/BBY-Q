#!reverse-pc-machine-v1
# Query training progress of the actual 1000-qubit VQC3 circuit.
load8 r0 8340000000000000000
cmp r0 103
jne invalid
load8 r1 8340000000000000010
cmp r1 232
jne invalid
load8 r1 8340000000000000011
cmp r1 3
jne invalid
load8 r1 8340000000000000012
cmp r1 111
jne invalid
load8 r1 8340000000000000013
cmp r1 9
jne invalid
load8 r1 8340000000000000030
load8 r2 8340000000000000031
mul r2 256
add r1 r2
expect Z:2000 Z:2999
stats
set r0 1000
print r0
print r1
halt
label invalid
div r0 0
