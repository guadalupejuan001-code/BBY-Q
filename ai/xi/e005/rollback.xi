#!reverse-pc-machine-v1
# Deliberately fail after a native memory mutation. No new RVPC2 is legal.
load8 r0 7000000000000000000
cmp r0 66
je present
div r0 0
label present
load8 r0 7000000000000000064
add r0 1
store8 7000000000000000064 r0
set r1 0
div r0 r1
