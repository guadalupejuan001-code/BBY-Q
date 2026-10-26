#!reverse-pc-machine-v1
# E007 Ether Vault: archive the first approved hypothesis inside ONE RVPC2.
# Does not use an external model/file for its state. Does not change prediction.
load8 r0 7000000000000000002
cmp r0 6
je schema_ok
div r0 0
label schema_ok
load8 r0 7000000000000000031
cmp r0 1
je approved
div r0 0
label approved
load8 r0 7000000000000000500
cmp r0 0
je vault_unused
div r0 0
label vault_unused
load8 r0 7000000000000000040
cmp r0 0
je no_training_pending
div r0 0
label no_training_pending
load8 r0 7000000000000000041
cmp r0 0
je no_validation_pending
div r0 0
label no_validation_pending
# Copy only compact knowledge (3 base weights, 4 descriptors, 4 weights).
# A bank inside Inverse Ether Memory is an archived hypothesis, not a
# second persistence authority.
set r0 0
label copy_base
set r12 7000000000000000064
add r12 r0
load8 r2 $r12
set r13 7000000000000000401
add r13 r0
store8 $r13 r2
add r0 1
cmp r0 3
jlt copy_base
set r0 0
label copy_relations
set r12 7000000000000000200
add r12 r0
load8 r2 $r12
set r13 7000000000000000420
add r13 r0
store8 $r13 r2
set r12 7000000000000000220
add r12 r0
load8 r2 $r12
set r13 7000000000000000440
add r13 r0
store8 $r13 r2
add r0 1
cmp r0 4
jlt copy_relations
load8 r2 7000000000000000030
store8 7000000000000000404 r2
store8 7000000000000000503 1
store8 7000000000000000504 1
store8 7000000000000000500 1
print r2
mem_stats
