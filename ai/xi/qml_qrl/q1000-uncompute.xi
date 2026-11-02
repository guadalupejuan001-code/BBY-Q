#!reverse-pc-machine-v1
# RESEARCH SCRATCH ONLY: inverse chain, not for persistent shared engine state.
# Demonstrates coherent invertibility of the 1000-qubit Clifford preparation.
load8 r0 8100000000000006000
cmp r0 113
jne invalid
set r0 1098
set r1 1099
label inverse_chain
cx $r0 $r1
sub r0 1
sub r1 1
cmp r0 99
jgt inverse_chain
h 100
probz 100
probz 600
probz 1099
stats
set r0 1000
print r0
halt
label invalid
div r0 0
