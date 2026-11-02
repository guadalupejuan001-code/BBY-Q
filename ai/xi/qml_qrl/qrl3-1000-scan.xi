#!reverse-pc-machine-v1
# qrl3: 999 actual Pauli ZZ expectations, on all trainable/readout qubits.
# Output order maps index i=0..998 to group=floor(i/9), site=i%9.
load8 r0 8350000000000000000
cmp r0 114
jne invalid
set r1 3001
label scan
expect Z:3000 Z:$r1
add r1 1
cmp r1 4000
jlt scan
stats
set r0 999
print r0
halt
label invalid
div r0 0
