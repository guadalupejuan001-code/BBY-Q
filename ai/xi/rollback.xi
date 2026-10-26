#!reverse-pc-machine-v1
# Intentional failure after touching a relation: no RVPC2 write may survive.
load8 r0 7000000000000000064
add r0 1
store8 7000000000000000064 r0
set r1 0
div r0 r1
