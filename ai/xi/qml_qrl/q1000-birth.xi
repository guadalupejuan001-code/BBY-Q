#!reverse-pc-machine-v1
# Q01-Q02: 1000 ACTUAL simulated qubits, one stabilizer GHZ component.
# Addresses 100..1099 do not intersect VQC2 2/3 or QRL2 4/5.
# This is Clifford H/CX; it is NOT a 2^1000 dense statevector or
# a 1000-qubit trained VQC/QRL variational policy.
load8 r0 8100000000000000000
cmp r0 81
jne invalid
load8 r0 8100000000000004000
cmp r0 87
jne invalid
load8 r0 8100000000000005000
cmp r0 83
jne invalid
load8 r0 8100000000000006000
cmp r0 0
jne invalid
set r0 100
h $r0
set r1 101
label q1000_chain
cx $r0 $r1
add r0 1
add r1 1
cmp r1 1100
jlt q1000_chain
expect Z:100 Z:1099
expect Z:100 Z:600
expect X:100 X:1099
probz 100
probz 1099
stats
store8 8100000000000006000 113
store8 8100000000000006001 232
store8 8100000000000006002 3
store8 8100000000000006003 1
set r0 1000
print r0
halt
label invalid
div r0 0
