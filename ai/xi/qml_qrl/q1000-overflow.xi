#!reverse-pc-machine-v1
# Negative Q01 experiment: GHZ component 1000 -> 1025 must exceed 1024 budget.
# Execute only on an isolated candidate, never on persistent memory.rvp.
load8 r0 8100000000000006000
cmp r0 113
jne invalid
set r0 1099
set r1 1100
label overflow
cx $r0 $r1
add r0 1
add r1 1
cmp r1 1125
jlt overflow
halt
label invalid
div r0 0
