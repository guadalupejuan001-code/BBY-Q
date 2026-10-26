#!reverse-pc-machine-v1
# E007: open a fresh shadow context, while retaining context A in Ether.
# After jury approval context B and archive A co-exist in ONE RVPC2.
load8 r0 7000000000000000002
cmp r0 6
je schema_ok
div r0 0
label schema_ok
load8 r0 7000000000000000500
cmp r0 1
je archive_ready
div r0 0
label archive_ready
load8 r0 7000000000000000031
cmp r0 1
je source_sealed
div r0 0
label source_sealed
load8 r0 7000000000000000503
cmp r0 1
je first_context
div r0 0
label first_context
load8 r0 7000000000000000040
cmp r0 0
je no_training
div r0 0
label no_training
load8 r0 7000000000000000041
cmp r0 0
je no_validation
div r0 0
label no_validation
# New context starts without old weights; old context stays archived.
store8 7000000000000000064 128
store8 7000000000000000065 128
store8 7000000000000000066 128
set r0 0
label clear_shadow
set r12 7000000000000000120
add r12 r0
store8 $r12 0
set r12 7000000000000000200
add r12 r0
store8 $r12 0
set r12 7000000000000000220
add r12 r0
store8 $r12 0
add r0 1
cmp r0 4
jlt clear_shadow
store8 7000000000000000030 0
store8 7000000000000000031 0
store8 7000000000000000043 0
store8 7000000000000000503 2
load8 r2 7000000000000000504
print r2
mem_stats
