#!reverse-pc-machine-v1
# E007 vault invariants, read-only XI.
load8 r0 7000000000000000002
cmp r0 6
je schema_ok
div r0 0
label schema_ok
load8 r0 7000000000000000500
cmp r0 1
je archive_exists
div r0 0
label archive_exists
load8 r0 7000000000000000031
cmp r0 1
je active_sealed
div r0 0
label active_sealed
load8 r2 7000000000000000503
load8 r3 7000000000000000504
cmp r2 r3
jne different_contexts
div r2 0
label different_contexts
load8 r0 7000000000000000030
cmp r0 0
jgt active_has_compositions
div r0 0
label active_has_compositions
load8 r0 7000000000000000404
cmp r0 0
jgt archive_has_compositions
div r0 0
label archive_has_compositions
load8 r0 7000000000000000040
cmp r0 0
je no_training_pending
div r0 0
label no_training_pending
load8 r0 7000000000000000041
cmp r0 0
je no_probe_pending
div r0 0
label no_probe_pending
# No raw training/holdout labels survive (240 slots, 3 arrays).
set r0 0
label validate_empty_buffers
set r12 7000000000000010000
add r12 r0
load8 r4 $r12
cmp r4 0
je signal_x_clear
div r4 0
label signal_x_clear
set r12 7000000000000011000
add r12 r0
load8 r4 $r12
cmp r4 0
je signal_p_clear
div r4 0
label signal_p_clear
set r12 7000000000000012000
add r12 r0
load8 r4 $r12
cmp r4 0
je feedback_clear
div r4 0
label feedback_clear
add r0 1
cmp r0 240
jlt validate_empty_buffers
print r2
print r3
load8 r4 7000000000000000505
print r4
load8 r4 7000000000000000506
print r4
mem_stats
stats
