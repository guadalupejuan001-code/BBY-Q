#!reverse-pc-machine-v1
# E008 archive checksum and one-authority invariant. Read only.
load8 r0 7000000000000000002
cmp r0 6
je schema_ok
div r0 0
label schema_ok
load8 r1 7000000000000000610
cmp r1 4
je exactly_four
div r1 0
label exactly_four
load8 r1 7000000000000000031
cmp r1 1
je sealed
div r1 0
label sealed
load8 r1 7000000000000000040
cmp r1 0
je feed_erased
div r1 0
label feed_erased
load8 r1 7000000000000000041
cmp r1 0
je exam_erased
div r1 0
label exam_erased
set r0 0
label inspect_bank
set r6 7000000000000000700
mov r7 r0
mul r7 64
add r6 r7
load8 r8 $r6
cmp r8 88
je bank_magic
div r8 0
label bank_magic
set r9 88
mov r11 r6
add r11 1
load8 r10 $r11
add r9 r10
set r1 0
label checksum_base
mov r11 r6
add r11 r1
add r11 2
load8 r10 $r11
add r9 r10
add r1 1
cmp r1 3
jlt checksum_base
set r1 0
label checksum_relations
mov r11 r6
add r11 r1
add r11 8
load8 r10 $r11
add r9 r10
mov r11 r6
add r11 r1
add r11 16
load8 r10 $r11
add r9 r10
add r1 1
cmp r1 4
jlt checksum_relations
mod r9 251
mov r11 r6
add r11 32
load8 r10 $r11
cmp r9 r10
je bank_checksum_valid
div r9 0
label bank_checksum_valid
add r0 1
cmp r0 4
jlt inspect_bank
print r0
mem_stats
stats
