#!reverse-pc-machine-v1
# Query training progress of the actual 1000-qubit QRL3 circuit.
load8 r0 8350000000000000000
cmp r0 114
jne invalid
load8 r1 8350000000000000010
cmp r1 232
jne invalid
load8 r1 8350000000000000011
cmp r1 3
jne invalid
load8 r1 8350000000000000012
cmp r1 111
jne invalid
load8 r1 8350000000000000013
cmp r1 9
jne invalid
load8 r1 8350000000000000030
load8 r2 8350000000000000031
mul r2 256
add r1 r2
expect Z:3000 Z:3999
stats
set r0 1000
print r0
print r1
halt
label invalid
div r0 0
