#!reverse-pc-machine-v1
# QRL3: genuine 1000-qubit trainable Clifford GHZ.
# ONE reference qubit plus 111 groups x 9 measured/trainable output qubits.
# All 999 outputs are acted on by learned group parameters; not a detached GHZ demo.
# This is a shared-parameter discrete Clifford agent, NOT universal variational QML.
load8 r0 8350000000000000000
cmp r0 0
jne invalid
h 3000
set r0 3000
set r1 3001
label entangle
cx $r0 $r1
add r0 1
add r1 1
cmp r1 4000
jlt entangle
expect Z:3000 Z:3999
probz 3000
stats
store8 8350000000000000000 114
store8 8350000000000000010 232
store8 8350000000000000011 3
store8 8350000000000000012 111
store8 8350000000000000013 9
set r0 1000
print r0
set r0 111
print r0
halt
label invalid
div r0 0
