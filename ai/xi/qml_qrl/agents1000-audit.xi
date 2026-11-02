#!reverse-pc-machine-v1
# Both processors are native 1000-qubit entangled GHZ components.
load8 r0 8120000000000000000
cmp r0 166
jne invalid
load8 r0 8100000000000006000
cmp r0 113
jne invalid
expect Z:100 Z:1099
expect Z:1200 Z:2199
probz 100
probz 1200
stats
load8 r0 8120000000000000006
load8 r1 8120000000000000007
mul r1 256
add r0 r1
print r0
load8 r0 8120000000000000008
load8 r1 8120000000000000009
mul r1 256
add r0 r1
print r0
halt
label invalid
div r0 0
