#!reverse-pc-machine-v1
# E007: Ether Vault context recall. Compare current and archived sealed models
# with consequences not seen during either training; swap ONLY after evidence.
# No externally supplied context label, no replay training, no second state file.
load8 r12 7000000000000000002
cmp r12 6
je schema_ok
div r12 0
label schema_ok
load8 r12 7000000000000000031
cmp r12 1
je active_sealed
div r12 0
label active_sealed
load8 r12 7000000000000000500
cmp r12 1
je archive_ready
div r12 0
label archive_ready
load8 r12 7000000000000000404
cmp r12 0
jgt archive_nonempty
div r12 0
label archive_nonempty
load8 r12 7000000000000000040
cmp r12 0
je training_finished
div r12 0
label training_finished
load8 r12 7000000000000000016
add r12 1
load8 r14 7000000000000000041
cmp r12 r14
je probe_ready
div r14 0
label probe_ready
load8 r12 7000000000000000503
load8 r14 7000000000000000504
cmp r12 r14
jne distinct_contexts
div r12 0
label distinct_contexts
set r0 0
set r11 0
set r15 0
label evaluate_external_consequence
set r12 7000000000000010000
add r12 r0
load8 r2 $r12
sub r2 100
cmp r2 0
jlt negative_x
set r2 1
jmp observed_x
label negative_x
set r2 -1
label observed_x
set r12 7000000000000011000
add r12 r0
load8 r3 $r12
sub r3 100
cmp r3 0
jlt negative_p
set r3 1
jmp observed_p
label negative_p
set r3 -1
label observed_p
set r4 1
cmp r2 0
jlt x_desc_done
add r4 2
label x_desc_done
cmp r3 0
jlt p_desc_done
add r4 1
label p_desc_done
# Active and archived base relations: both scored before reading the label.
load8 r8 7000000000000000064
sub r8 128
load8 r12 7000000000000000065
sub r12 128
mul r12 r2
add r8 r12
load8 r12 7000000000000000066
sub r12 128
mul r12 r3
add r8 r12
load8 r9 7000000000000000401
sub r9 128
load8 r12 7000000000000000402
sub r12 128
mul r12 r2
add r9 r12
load8 r12 7000000000000000403
sub r12 128
mul r12 r3
add r9 r12
set r13 0
label score_both_relation_banks
set r12 7000000000000000200
add r12 r13
load8 r14 $r12
cmp r14 r4
jne active_nonmatch
set r12 7000000000000000220
add r12 r13
load8 r14 $r12
sub r14 128
add r8 r14
label active_nonmatch
set r12 7000000000000000420
add r12 r13
load8 r14 $r12
cmp r14 r4
jne archived_nonmatch
set r12 7000000000000000440
add r12 r13
load8 r14 $r12
sub r14 128
add r9 r14
label archived_nonmatch
add r13 1
cmp r13 4
jlt score_both_relation_banks
set r12 0
cmp r8 0
jlt active_prediction_ready
set r12 1
label active_prediction_ready
set r13 0
cmp r9 0
jlt archive_prediction_ready
set r13 1
label archive_prediction_ready
# Consequence is consulted only after BOTH predictions are frozen.
set r14 7000000000000012000
add r14 r0
load8 r10 $r14
cmp r10 0
je feedback_is_binary
cmp r10 1
je feedback_is_binary
div r10 0
label feedback_is_binary
cmp r12 r10
jne active_wrong
add r11 1
label active_wrong
cmp r13 r10
jne archive_wrong
add r15 1
label archive_wrong
add r0 1
cmp r0 240
jlt evaluate_external_consequence
store8 7000000000000000507 r11
store8 7000000000000000508 r15
load8 r12 7000000000000000506
add r12 1
store8 7000000000000000506 r12
# Evidence gate: use a high-precision ordinary path OR a strict
# comparative advantage path when feedback is noisy (no regime labels).
# Ordinary: archive >=205/240 and improvement >=30/240.
# Noise-tolerant: archive >=156/240 AND improvement >=80/240.
# Independent random feedback cannot ordinarily reach that margin.
mov r12 r15
sub r12 r11
cmp r12 30
jlt retain_current
cmp r15 205
jge context_evidence_accepted
cmp r12 80
jlt retain_current
cmp r15 156
jlt retain_current
label context_evidence_accepted
# Atomically swap current and archived knowledge; leave their identities.
set r0 0
label swap_three_base_weights
set r12 7000000000000000064
add r12 r0
load8 r2 $r12
set r13 7000000000000000401
add r13 r0
load8 r3 $r13
store8 $r12 r3
store8 $r13 r2
add r0 1
cmp r0 3
jlt swap_three_base_weights
set r0 0
label swap_four_descriptors_and_weights
set r12 7000000000000000200
add r12 r0
load8 r2 $r12
set r13 7000000000000000420
add r13 r0
load8 r3 $r13
store8 $r12 r3
store8 $r13 r2
set r12 7000000000000000220
add r12 r0
load8 r2 $r12
set r13 7000000000000000440
add r13 r0
load8 r3 $r13
store8 $r12 r3
store8 $r13 r2
add r0 1
cmp r0 4
jlt swap_four_descriptors_and_weights
load8 r2 7000000000000000030
load8 r3 7000000000000000404
store8 7000000000000000030 r3
store8 7000000000000000404 r2
load8 r2 7000000000000000503
load8 r3 7000000000000000504
store8 7000000000000000503 r3
store8 7000000000000000504 r2
load8 r2 7000000000000000505
add r2 1
store8 7000000000000000505 r2
store8 7000000000000000509 1
jmp context_decided
label retain_current
store8 7000000000000000509 0
label context_decided
# All 240 validation examples are erased in the SAME XI transaction.
set r0 0
label forget_probe_material
set r12 7000000000000010000
add r12 r0
store8 $r12 0
set r12 7000000000000011000
add r12 r0
store8 $r12 0
set r12 7000000000000012000
add r12 r0
store8 $r12 0
add r0 1
cmp r0 240
jlt forget_probe_material
store8 7000000000000000041 0
store8 7000000000000000042 0
print r11
print r15
load8 r14 7000000000000000509
print r14
load8 r14 7000000000000000503
print r14
load8 r14 7000000000000000505
print r14
mem_stats
stats
