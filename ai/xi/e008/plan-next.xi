#!reverse-pc-machine-v1
# BBY Q E008: native XI epistemic planner.
# No external task labels or AI libraries. Knowledge-bank predictions only.
# Actions: 0=use current knowledge; 1=ask a discriminating query;
# 2=study the worst unexplained cell; 3=expand representation.
load8 r12 7000000000000000002
cmp r12 6
je schema_ok
div r12 0
label schema_ok
load8 r12 7000000000000000610
cmp r12 4
je capacity_ready
div r12 0
label capacity_ready
load8 r12 7000000000000000041
cmp r12 0
je no_outstanding_exam
div r12 0
label no_outstanding_exam
load8 r12 7000000000000000613
cmp r12 1
je requires_inquiry
store8 7000000000000000621 0
store8 7000000000000000622 0
store8 7000000000000000624 0
jmp learning_decision_finished
label requires_inquiry
load8 r12 7000000000000000616
cmp r12 2
jne choose_disagreement
# Novelty: the last exam found a locally catastrophic contradiction;
# prioritize the sign-pair category with maximal unexpected error.
load8 r13 7000000000000000615
cmp r13 1
jge novelty_region_bounded_low
div r13 0
label novelty_region_bounded_low
cmp r13 4
jle novelty_region_bounded_high
div r13 0
label novelty_region_bounded_high
store8 7000000000000000621 2
store8 7000000000000000622 r13
store8 7000000000000000624 0
jmp learning_decision_finished
label choose_disagreement
# Select the input cell that maximizes balanced disagreement across 4
# independently learned archived models; it depends on model PREDICTIONS.
# No hypothetical feedback is read, and no labels are available here.
set r0 1
set r14 -1
set r15 1
label candidate_input_cell
set r2 -1
cmp r0 3
jlt assigned_x
set r2 1
label assigned_x
set r3 -1
mov r11 r0
mod r11 2
cmp r11 1
je assigned_p
set r3 1
label assigned_p
set r4 0
set r1 0
label vote_all_banks
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
label score_descriptors
mov r12 r6
add r12 r9
add r12 8
load8 r10 $r12
cmp r10 r0
jne relation_unmatched
mov r12 r6
add r12 r9
add r12 16
load8 r10 $r12
sub r10 128
add r7 r10
label relation_unmatched
add r9 1
cmp r9 4
jlt score_descriptors
cmp r7 0
jlt no_positive_vote
add r4 1
label no_positive_vote
add r1 1
cmp r1 4
jlt vote_all_banks
# Balance = min(positive votes, negative votes), maximal at 2-to-2.
mov r12 r4
set r13 4
sub r13 r4
cmp r12 r13
jle split_measured
mov r12 r13
label split_measured
cmp r12 r14
jle no_better_cell
mov r14 r12
mov r15 r0
label no_better_cell
add r0 1
cmp r0 5
jlt candidate_input_cell
cmp r14 0
jne useful_disagreement_exists
store8 7000000000000000621 3
jmp record_question
label useful_disagreement_exists
store8 7000000000000000621 1
label record_question
store8 7000000000000000622 r15
store8 7000000000000000624 r14
label learning_decision_finished
load8 r14 7000000000000000621
print r14
load8 r14 7000000000000000622
print r14
load8 r14 7000000000000000624
print r14
mem_stats
