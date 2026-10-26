#!reverse-pc-machine-v1
# Language preference is a local property of the same persistent Ether state.
load8 r0 7200000000000000000
cmp r0 83
je classroom_valid
div r0 0
label classroom_valid
load8 r1 7200000000000000080
cmp r1 1
je valid_language
cmp r1 2
je valid_language
div r1 0
label valid_language
store8 7200000000000000004 r1
store8 7200000000000000080 0
print r1
mem_stats
