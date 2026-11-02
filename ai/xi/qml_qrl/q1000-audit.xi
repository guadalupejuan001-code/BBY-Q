#!reverse-pc-machine-v1
# Q02 read-only: GHZ correlation across nonadjacent qubits, persisted Ether.
load8 r0 8100000000000006000
cmp r0 113
jne invalid
load8 r0 8100000000000006001
cmp r0 232
jne invalid
load8 r0 8100000000000006002
cmp r0 3
jne invalid
load8 r0 8100000000000006003
cmp r0 1
jne invalid
expect Z:100 Z:1099
expect Z:100 Z:600
expect X:100 X:1099
probz 100
probz 1099
stats
set r0 1000
print r0
halt
label invalid
div r0 0
