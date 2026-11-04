#!reverse-pc-machine-v1
# One connected 100-qubit GHZ state on the original exact Clifford core.
# Only integer/sign tableau operations. No continuous rotations or MPS.
h 10000
set r0 10000
set r1 10001
label connect_next
cx $r0 $r1
add r0 1
add r1 1
cmp r1 10100
jlt connect_next
stats
qstats
halt
