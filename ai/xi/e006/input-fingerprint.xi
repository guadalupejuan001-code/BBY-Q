#!reverse-pc-machine-v1
# E005: XI-only read-only digest over source observations, NOT labels.
# Compare the two world feeders on the same exact starting RVPC2.
load8 r0 7000000000000000002
cmp r0 6
je valid_schema
div r0 0
label valid_schema
set r0 0
set r4 7
label next_pair
set r12 7000000000000010000
add r12 r0
load8 r2 $r12
set r12 7000000000000011000
add r12 r0
load8 r3 $r12
mul r4 131
add r4 r2
mod r4 2147483647
mul r4 131
add r4 r3
mod r4 2147483647
add r0 1
cmp r0 200
jlt next_pair
print r0
print r4
