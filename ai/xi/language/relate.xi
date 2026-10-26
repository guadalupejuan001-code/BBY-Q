#!reverse-pc-machine-v1
# E009: learn affirmed/refuted semantic triples from grounded word forms.
# Nothing in this program names the entities or an oracle target.
load8 r14 7100000000000000002
cmp r14 1
je schema_ok
div r14 0
label schema_ok
load8 r14 7100000000000000175
cmp r14 2
je event_ready
div r14 0
label event_ready
load8 r14 7100000000000000170
cmp r14 0
je valid_truth
cmp r14 1
je valid_truth
div r14 0
label valid_truth
# Resolve three words (subject/predicate/object) through persisted lexicon.
set r15 0
label resolve_next_word
set r7 7100000000000000140
mov r8 r15
mul r8 10
add r7 r8
load8 r2 $r7
cmp r2 1
jge length_low
div r2 0
label length_low
cmp r2 8
jle length_high
div r2 0
label length_high
load8 r6 7100000000000000016
set r0 0
label inspect_dictionary
cmp r0 r6
jge unknown_word
set r4 7100000000000001000
mov r8 r0
mul r8 16
add r4 r8
load8 r5 $r4
cmp r5 r2
jne next_candidate_word
set r1 0
label compare_token
cmp r1 r2
jge candidate_identified
mov r8 r7
add r8 1
add r8 r1
load8 r9 $r8
mov r10 r4
add r10 2
add r10 r1
load8 r11 $r10
cmp r9 r11
jne next_candidate_word
add r1 1
jmp compare_token
label candidate_identified
mov r8 r4
add r8 1
load8 r3 $r8
set r8 7100000000000000180
add r8 r15
store8 $r8 r3
add r15 1
cmp r15 3
jlt resolve_next_word
jmp all_grounded
label next_candidate_word
add r0 1
jmp inspect_dictionary
label unknown_word
# Cannot learn relationships whose words have no grounded concept.
div r0 0
label all_grounded
load8 r2 7100000000000000180
load8 r3 7100000000000000181
load8 r4 7100000000000000182
# Scan the structural graph for an exact triple.
load8 r6 7100000000000000018
set r0 0
label lookup_fact
cmp r0 r6
jge create_fact
set r7 7100000000000003000
mov r8 r0
mul r8 8
add r7 r8
load8 r9 $r7
cmp r9 r2
jne next_fact
mov r8 r7
add r8 1
load8 r9 $r8
cmp r9 r3
jne next_fact
mov r8 r7
add r8 2
load8 r9 $r8
cmp r9 r4
jne next_fact
jmp reinforce_fact
label next_fact
add r0 1
jmp lookup_fact
label create_fact
cmp r6 48
jlt fact_capacity
div r6 0
label fact_capacity
set r7 7100000000000003000
mov r8 r6
mul r8 8
add r7 r8
store8 $r7 r2
mov r8 r7
add r8 1
store8 $r8 r3
mov r8 r7
add r8 2
store8 $r8 r4
add r6 1
store8 7100000000000000018 r6
label reinforce_fact
# Positive and negative evidence are distinct and bounded. Contradiction
# is tracked rather than silently overwriting a stored relation.
mov r8 r7
add r8 3
load8 r9 7100000000000000170
cmp r9 1
je support_positive
add r8 1
label support_positive
load8 r10 $r8
cmp r10 200
jge evidence_capped
add r10 1
store8 $r8 r10
label evidence_capped
# New evidence invalidates cached composition until recalibrated.
set r0 1
label invalidate_transitivity_cache
set r8 7100000000000002100
add r8 r0
store8 $r8 0
set r8 7100000000000002150
add r8 r0
store8 $r8 0
set r8 7100000000000002000
add r8 r0
store8 $r8 0
add r0 1
load8 r12 7100000000000000017
cmp r0 r12
jle invalidate_transitivity_cache
# Clear all three input text forms and derived temporary concept IDs.
set r0 0
label clear_text_intake
set r7 7100000000000000140
add r7 r0
store8 $r7 0
add r0 1
cmp r0 29
jlt clear_text_intake
store8 7100000000000000170 0
store8 7100000000000000175 0
set r0 0
label clear_resolved
set r7 7100000000000000180
add r7 r0
store8 $r7 0
add r0 1
cmp r0 3
jlt clear_resolved
# Return fact count and last evidence level.
print r6
print r10
mem_stats
stats
