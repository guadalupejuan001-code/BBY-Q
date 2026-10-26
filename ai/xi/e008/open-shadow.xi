#!reverse-pc-machine-v1
# E008: create empty unapproved shadow while all prior banks remain in Ether.
load8 r0 7000000000000000002
cmp r0 6
je schema_ok
div r0 0
label schema_ok
load8 r0 7000000000000000610
cmp r0 1
jge bank_available
div r0 0
label bank_available
cmp r0 4
jlt capacity_ok
div r0 0
label capacity_ok
load8 r1 7000000000000000031
cmp r1 1
je old_sealed
div r1 0
label old_sealed
load8 r1 7000000000000000611
mov r2 r0
sub r2 1
cmp r1 r2
je last_bank_stored
div r1 0
label last_bank_stored
load8 r1 7000000000000000040
cmp r1 0
je no_training
div r1 0
label no_training
load8 r1 7000000000000000041
cmp r1 0
je no_exam
div r1 0
label no_exam
# Starting a fresh hypothesis is reversible; existing archived banks unchanged.
store8 7000000000000000064 128
store8 7000000000000000065 128
store8 7000000000000000066 128
set r1 0
label erase_candidate
set r12 7000000000000000120
add r12 r1
store8 $r12 0
set r12 7000000000000000200
add r12 r1
store8 $r12 0
set r12 7000000000000000220
add r12 r1
store8 $r12 0
add r1 1
cmp r1 4
jlt erase_candidate
store8 7000000000000000030 0
store8 7000000000000000031 0
store8 7000000000000000043 0
store8 7000000000000000611 r0
print r0
mem_stats
