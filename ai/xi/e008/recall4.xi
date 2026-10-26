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
jne exam_supplied
div r1 0
label exam_supplied
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
# Four bank integrity checks completed BEFORE considering any consequences.
load8 r12 7000000000000000040
cmp r12 0
je no_training_pending
div r12 0
label no_training_pending
load8 r12 7000000000000000041
load8 r11 7000000000000000016
add r11 1
cmp r12 r11
je fresh_probe_ready
div r12 0
label fresh_probe_ready
# Scores and per-sign-cell error counts are temporary within one transaction.
set r0 0
label initialize_scores
set r12 7000000000000002000
add r12 r0
store8 $r12 0
set r12 7000000000000002050
add r12 r0
store8 $r12 0
add r0 1
cmp r0 4
jlt initialize_scores
set r0 0
label initialize_errors
set r12 7000000000000002100
add r12 r0
store8 $r12 0
add r0 1
cmp r0 32
jlt initialize_errors
set r0 0
label initialize_visits
set r12 7000000000000002200
add r12 r0
store8 $r12 0
add r0 1
cmp r0 4
jlt initialize_visits
set r0 0
label independent_case
# Read observable signals and determine which sign pair was observed.
set r12 7000000000000010000
add r12 r0
load8 r2 $r12
sub r2 100
cmp r2 0
jlt x_is_negative
set r2 1
jmp x_ready
label x_is_negative
set r2 -1
label x_ready
set r12 7000000000000011000
add r12 r0
load8 r3 $r12
sub r3 100
cmp r3 0
jlt p_is_negative
set r3 1
jmp p_ready
label p_is_negative
set r3 -1
label p_ready
set r4 1
cmp r2 0
jlt x_index_done
add r4 2
label x_index_done
cmp r3 0
jlt p_index_done
add r4 1
label p_index_done
# A descriptor's sample count is needed to reject plausible global averages
# that hide a catastrophic failure in one area of the input space.
mov r5 r4
sub r5 1
set r12 7000000000000002200
add r12 r5
load8 r13 $r12
add r13 1
store8 $r12 r13
# Predict with every archived model BEFORE reading feedback from the world.
set r1 0
label predict_all_banks
set r6 7000000000000000700
mov r5 r1
mul r5 64
add r6 r5
mov r12 r6
add r12 2
load8 r7 $r12
sub r7 128
mov r12 r6
add r12 3
load8 r8 $r12
sub r8 128
mul r8 r2
add r7 r8
mov r12 r6
add r12 4
load8 r8 $r12
sub r8 128
mul r8 r3
add r7 r8
set r9 0
label predict_compositions
mov r12 r6
add r12 r9
add r12 8
load8 r13 $r12
cmp r13 r4
jne not_matching_composition
mov r12 r6
add r12 r9
add r12 16
load8 r13 $r12
sub r13 128
add r7 r13
label not_matching_composition
add r9 1
cmp r9 4
jlt predict_compositions
set r13 0
cmp r7 0
jlt predictive_score_negative
set r13 1
label predictive_score_negative
set r12 7000000000000002050
add r12 r1
store8 $r12 r13
add r1 1
cmp r1 4
jlt predict_all_banks
# Only now is it legal to consult the environmental consequence.
set r12 7000000000000012000
add r12 r0
load8 r10 $r12
cmp r10 0
je consequence_valid
cmp r10 1
je consequence_valid
div r10 0
label consequence_valid
set r1 0
label compare_predictions
set r12 7000000000000002050
add r12 r1
load8 r11 $r12
cmp r11 r10
jne prediction_incorrect
set r12 7000000000000002000
add r12 r1
load8 r13 $r12
add r13 1
store8 $r12 r13
jmp bank_evaluated
label prediction_incorrect
# Error indexed by both hypothesis and the observed sign-pair cell.
set r12 7000000000000002100
mov r13 r1
mul r13 8
add r12 r13
mov r13 r4
sub r13 1
add r12 r13
load8 r11 $r12
add r11 1
store8 $r12 r11
label bank_evaluated
add r1 1
cmp r1 4
jlt compare_predictions
add r0 1
cmp r0 240
jlt independent_case
# Compare every sealed model's held-out predictive accuracy.
set r8 -1
set r9 -1
set r7 0
set r0 0
label rank_bank_scores
set r12 7000000000000002000
add r12 r0
load8 r11 $r12
cmp r11 r8
jle not_best_bank
mov r9 r8
mov r8 r11
mov r7 r0
jmp ranked_bank
label not_best_bank
cmp r11 r9
jle ranked_bank
mov r9 r11
label ranked_bank
add r0 1
cmp r0 4
jlt rank_bank_scores
# Inspect worst local disagreement; prevent OOD models with 75% overall
# accuracy from masquerading as verified universal knowledge.
set r0 0
set r5 0
set r6 1
set r15 0
label inspect_worst_cell
set r12 7000000000000002100
mov r13 r7
mul r13 8
add r12 r13
add r12 r0
load8 r11 $r12
cmp r11 r5
jle no_worst_update
mov r5 r11
mov r6 r0
add r6 1
label no_worst_update
mov r12 r11
mul r12 5
set r13 7000000000000002200
add r13 r0
load8 r14 $r13
mul r14 2
cmp r12 r14
jle local_rate_allowed
set r15 1
label local_rate_allowed
add r0 1
cmp r0 4
jlt inspect_worst_cell
# Record measured evidence, including an informative next region to probe.
store8 7000000000000000615 r6
store8 7000000000000000617 r8
store8 7000000000000000618 r9
load8 r12 7000000000000000612
add r12 1
store8 7000000000000000612 r12
# First path: clean validated model. Second: noisy but dominant model.
mov r12 r8
sub r12 r9
cmp r15 0
jne abstain_and_learn
cmp r12 30
jlt uncertain_evidence
cmp r8 208
jge accept_best
cmp r8 156
jlt uncertain_evidence
cmp r12 18
jlt uncertain_evidence
jmp accept_best
label abstain_and_learn
# Accuracy high but sharply wrong in one category means likely novelty.
cmp r8 155
jlt uncertain_evidence
store8 7000000000000000616 2
jmp abstain
label uncertain_evidence
store8 7000000000000000616 1
label abstain
store8 7000000000000000613 1
load8 r12 7000000000000000614
add r12 1
store8 7000000000000000614 r12
jmp verdict_done
label accept_best
store8 7000000000000000611 r7
store8 7000000000000000613 0
store8 7000000000000000616 0
label verdict_done
# Do not retain labels, predictions or temporary score/error counters.
set r0 0
label erase_observations
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
jlt erase_observations
set r0 0
label erase_scores
set r12 7000000000000002000
add r12 r0
store8 $r12 0
set r12 7000000000000002050
add r12 r0
store8 $r12 0
add r0 1
cmp r0 4
jlt erase_scores
set r0 0
label erase_errors
set r12 7000000000000002100
add r12 r0
store8 $r12 0
add r0 1
cmp r0 32
jlt erase_errors
set r0 0
label erase_visit_counts
set r12 7000000000000002200
add r12 r0
store8 $r12 0
add r0 1
cmp r0 4
jlt erase_visit_counts
store8 7000000000000000041 0
store8 7000000000000000042 0
# Display scored evidence and the next learning decision.
print r7
print r8
print r9
load8 r14 7000000000000000613
print r14
load8 r14 7000000000000000611
print r14
load8 r14 7000000000000000615
print r14
load8 r14 7000000000000000616
print r14
mem_stats
stats
