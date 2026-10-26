#!reverse-pc-machine-v1
# Post-training invariant, written ONLY in XI. No residual training labels.
load8 r2 7000000000000000002
cmp r2 5
je valid_schema
div r2 0
label valid_schema
load8 r2 7000000000000000040
cmp r2 0
je inactive_batch
div r2 0
label inactive_batch
set r0 0
label check_all
set r12 7000000000000010000
add r12 r0
load8 r2 $r12
cmp r2 0
je x_clean
div r2 0
label x_clean
set r12 7000000000000011000
add r12 r0
load8 r2 $r12
cmp r2 0
je p_clean
div r2 0
label p_clean
set r12 7000000000000012000
add r12 r0
load8 r2 $r12
cmp r2 0
je outcome_clean
div r2 0
label outcome_clean
add r0 1
cmp r0 200
jlt check_all
print r0
mem_stats
