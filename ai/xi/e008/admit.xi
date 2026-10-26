#!reverse-pc-machine-v1
# BBY Q E006: BLIND SHADOW JURY, written entirely in native XI.
# Predict with base and composed shadow BEFORE reading each held-out label.
# Neither model changes during evaluation. Promote or prune ONLY afterward.
# All data, verdict and archive counters live in one Ether RVPC2 authority.
load8 r12 7000000000000000002
cmp r12 6
je schema_ok
div r12 0
label schema_ok
load8 r12 7000000000000000031
cmp r12 0
je not_yet_promoted
div r12 0
label not_yet_promoted
load8 r12 7000000000000000040
cmp r12 0
je no_training_feed_pending
div r12 0
label no_training_feed_pending
load8 r12 7000000000000000016
add r12 1
load8 r14 7000000000000000041
cmp r12 r14
je independent_validation_ready
div r14 0
label independent_validation_ready
load8 r5 7000000000000000064
sub r5 128
load8 r6 7000000000000000065
sub r6 128
load8 r7 7000000000000000066
sub r7 128
set r0 0
set r11 0
set r15 0
label evaluate_unseen
set r12 7000000000000010000
add r12 r0
load8 r2 $r12
sub r2 100
cmp r2 0
jlt x_negative
set r2 1
jmp x_done
label x_negative
set r2 -1
label x_done
set r12 7000000000000011000
add r12 r0
load8 r3 $r12
sub r3 100
cmp r3 0
jlt p_negative
set r3 1
jmp p_done
label p_negative
set r3 -1
label p_done
# Build observed conjunction descriptor without consulting the label.
set r4 1
cmp r2 0
jlt x_descriptor_done
add r4 2
label x_descriptor_done
cmp r3 0
jlt p_descriptor_done
add r4 1
label p_descriptor_done
# Reference hypothesis: the same learner with composed relations ablated.
mov r8 r5
mov r12 r6
mul r12 r2
add r8 r12
mov r12 r7
mul r12 r3
add r8 r12
# Challenger starts with reference score and consults candidate relations.
mov r9 r8
set r13 0
label candidate_slots
set r12 7000000000000000200
add r12 r13
load8 r14 $r12
cmp r14 r4
jne candidate_no_match
set r12 7000000000000000220
add r12 r13
load8 r14 $r12
sub r14 128
add r9 r14
label candidate_no_match
add r13 1
cmp r13 4
jlt candidate_slots
# Two predictions are fixed before the evaluator looks at the feedback.
set r12 0
cmp r8 0
jlt baseline_prediction_ready
set r12 1
label baseline_prediction_ready
set r13 0
cmp r9 0
jlt shadow_prediction_ready
set r13 1
label shadow_prediction_ready
set r14 7000000000000012000
add r14 r0
load8 r10 $r14
cmp r10 0
je valid_feedback
cmp r10 1
je valid_feedback
div r10 0
label valid_feedback
cmp r12 r10
jne baseline_missed
add r15 1
label baseline_missed
cmp r13 r10
jne shadow_missed
add r11 1
label shadow_missed
add r0 1
cmp r0 240
jlt evaluate_unseen
# Evaluate generalization, not mere increase in relation slots.
# Compute majority-class baseline from heldout labels AFTER predictions.
set r0 0
set r13 0
label count_observed_ones
set r12 7000000000000012000
add r12 r0
load8 r10 $r12
cmp r10 1
jne no_one
add r13 1
label no_one
add r0 1
cmp r0 240
jlt count_observed_ones
set r12 240
sub r12 r13
cmp r12 r13
jge max_majority
mov r12 r13
label max_majority
mov r14 r11
sub r14 r12
cmp r14 15
jlt reject_candidate
cmp r11 214
jlt reject_candidate
# Successful acceptance requires never seeing the answer during prediction.
# PROBATION PASSED. Commit a frozen model only after independent holdout.
store8 7000000000000000031 1
load8 r12 7000000000000000032
add r12 1
store8 7000000000000000032 r12
store8 7000000000000000043 1
jmp verdict_finished
label reject_candidate
# Fail closed: remove all unvalidated compositions and accumulated evidence.
# Do not erase the identity, generation, or the three base hypotheses.
set r13 0
label erase_spurious_relations
set r12 7000000000000000200
add r12 r13
store8 $r12 0
set r12 7000000000000000220
add r12 r13
store8 $r12 0
set r12 7000000000000000120
add r12 r13
store8 $r12 0
add r13 1
cmp r13 4
jlt erase_spurious_relations
store8 7000000000000000030 0
store8 7000000000000000031 0
load8 r12 7000000000000000033
add r12 1
store8 7000000000000000033 r12
store8 7000000000000000043 2
label verdict_finished
# Hard erasure of independent validation labels and observations inside
# the SAME XI transaction as verdict, without changing candidate metrics.
set r0 0
label erase_holdout
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
jlt erase_holdout
store8 7000000000000000041 0
store8 7000000000000000042 0
print r11
print r15
load8 r14 7000000000000000031
print r14
load8 r14 7000000000000000030
print r14
load8 r14 7000000000000000032
print r14
load8 r14 7000000000000000033
print r14
mem_stats
stats
