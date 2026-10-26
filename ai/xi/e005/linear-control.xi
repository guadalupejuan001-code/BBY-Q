#!reverse-pc-machine-v1
# Comparator profile: disable relation creation, preserve the same learner.
load8 r0 7000000000000000000
cmp r0 66
je present
div r0 0
label present
load8 r0 7000000000000000002
cmp r0 5
je version_ok
div r0 0
label version_ok
store8 7000000000000000003 0
mem_stats
