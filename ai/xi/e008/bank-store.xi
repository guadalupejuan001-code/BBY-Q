#!reverse-pc-machine-v1
# E008: seal a validated XI model in one of four bounded Ether knowledge banks.
# Addresses and stored bytes live INSIDE the same REVERSE-PC RVPC2.
load8 r0 7000000000000000002
cmp r0 6
je schema_ok
div r0 0
label schema_ok
load8 r0 7000000000000000031
cmp r0 1
je validated
div r0 0
label validated
load8 r0 7000000000000000040
cmp r0 0
je no_pending_training
div r0 0
label no_pending_training
load8 r0 7000000000000000041
cmp r0 0
je no_pending_exam
div r0 0
label no_pending_exam
load8 r1 7000000000000000610
cmp r1 4
jlt space_exists
div r1 0
label space_exists
load8 r2 7000000000000000611
cmp r2 r1
je correct_next_bank
div r2 0
label correct_next_bank
# Compute logical bank base = 7000000000000000700 + 64 * slot.
set r6 7000000000000000700
mov r7 r1
mul r7 64
add r6 r7
set r8 0
mov r9 r6
store8 $r9 88
add r8 88
mov r9 r6
add r9 1
load8 r10 7000000000000000030
store8 $r9 r10
add r8 r10
set r0 0
label store_base
set r11 7000000000000000064
add r11 r0
load8 r10 $r11
mov r9 r6
add r9 r0
add r9 2
store8 $r9 r10
add r8 r10
add r0 1
cmp r0 3
jlt store_base
set r0 0
label store_structures
set r11 7000000000000000200
add r11 r0
load8 r10 $r11
mov r9 r6
add r9 r0
add r9 8
store8 $r9 r10
add r8 r10
set r11 7000000000000000220
add r11 r0
load8 r10 $r11
mov r9 r6
add r9 r0
add r9 16
store8 $r9 r10
add r8 r10
add r0 1
cmp r0 4
jlt store_structures
mod r8 251
mov r9 r6
add r9 32
store8 $r9 r8
add r1 1
store8 7000000000000000610 r1
print r1
print r8
mem_stats
