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

# Verify no transient score, prediction, error, or visit history survives.
set r0 0
label audit_score_scratch
set r12 7000000000000002000
add r12 r0
load8 r13 $r12
cmp r13 0
je scores_clear
div r13 0
label scores_clear
set r12 7000000000000002050
add r12 r0
load8 r13 $r12
cmp r13 0
je predictions_clear
div r13 0
label predictions_clear
add r0 1
cmp r0 4
jlt audit_score_scratch
set r0 0
label audit_error_scratch
set r12 7000000000000002100
add r12 r0
load8 r13 $r12
cmp r13 0
je error_clear
div r13 0
label error_clear
add r0 1
cmp r0 32
jlt audit_error_scratch
set r0 0
label audit_visits
set r12 7000000000000002200
add r12 r0
load8 r13 $r12
cmp r13 0
je visits_clear
div r13 0
label visits_clear
add r0 1
cmp r0 4
jlt audit_visits
set r0 0
label audit_full_observation_memory
set r12 7000000000000010000
add r12 r0
load8 r13 $r12
cmp r13 0
je x_erased
div r13 0
label x_erased
set r12 7000000000000011000
add r12 r0
load8 r13 $r12
cmp r13 0
je p_erased
div r13 0
label p_erased
set r12 7000000000000012000
add r12 r0
load8 r13 $r12
cmp r13 0
je y_erased
div r13 0
label y_erased
add r0 1
cmp r0 240
jlt audit_full_observation_memory
print r0
mem_stats
stats
