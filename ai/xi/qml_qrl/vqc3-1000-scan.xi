#!reverse-pc-machine-v1
# vqc3: 999 actual Pauli ZZ expectations, on all trainable/readout qubits.
# Output order maps index i=0..998 to group=floor(i/9), site=i%9.
load8 r0 8340000000000000000
cmp r0 103
jne invalid
set r1 2001
label scan
expect Z:2000 Z:$r1
add r1 1
cmp r1 3000
jlt scan
stats
set r0 999
print r0
halt
label invalid
div r0 0
