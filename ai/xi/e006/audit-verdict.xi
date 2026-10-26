#!reverse-pc-machine-v1
# E006 post-jury invariant: raw experiences are not part of the durable agent.
load8 r2 7000000000000000002
cmp r2 6
je schema_ok
div r2 0
label schema_ok
load8 r2 7000000000000000040
cmp r2 0
je training_feed_empty
div r2 0
label training_feed_empty
load8 r2 7000000000000000041
cmp r2 0
je jury_feed_empty
div r2 0
label jury_feed_empty
load8 r2 7000000000000000042
cmp r2 0
je jury_kind_erased
div r2 0
label jury_kind_erased
load8 r2 7000000000000000043
cmp r2 1
je valid_verdict
cmp r2 2
je valid_verdict
div r2 0
label valid_verdict
set r0 0
label every_buffer_location
set r12 7000000000000010000
add r12 r0
load8 r2 $r12
cmp r2 0
je signal_x_erased
div r2 0
label signal_x_erased
set r12 7000000000000011000
add r12 r0
load8 r2 $r12
cmp r2 0
je signal_p_erased
div r2 0
label signal_p_erased
set r12 7000000000000012000
add r12 r0
load8 r2 $r12
cmp r2 0
je label_erased
div r2 0
label label_erased
add r0 1
cmp r0 240
jlt every_buffer_location
load8 r2 7000000000000000031
cmp r2 0
je inactive_no_descriptors
cmp r2 1
je active_descriptors
div r2 0
label inactive_no_descriptors
load8 r2 7000000000000000030
cmp r2 0
je verified
div r2 0
label active_descriptors
load8 r2 7000000000000000030
cmp r2 0
jgt verified
div r2 0
label verified
print r0
load8 r2 7000000000000000031
print r2
mem_stats
stats
