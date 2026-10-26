#!reverse-pc-machine-v1
# E009: learn a word-to-concept binding from a NONLINGUISTIC sensor triple.
# No concepts, lexical spellings or labels are present at birth.
load8 r15 7100000000000000000
cmp r15 76
je verify_version
div r15 0
label verify_version
load8 r15 7100000000000000002
cmp r15 1
je verify_event
div r15 0
label verify_event
load8 r15 7100000000000000125
cmp r15 1
je ground_event_ready
div r15 0
label ground_event_ready
load8 r6 7100000000000000100
cmp r6 1
jge length_lower
div r6 0
label length_lower
cmp r6 8
jle length_valid
div r6 0
label length_valid
# Fingerprint is independently computed from three categorical sensor axes.
load8 r2 7100000000000000120
load8 r3 7100000000000000121
load8 r4 7100000000000000122
cmp r2 0
jge sensor0_min
div r2 0
label sensor0_min
cmp r2 3
jle sensor0_max
div r2 0
label sensor0_max
cmp r3 3
jle sensor1_max
div r3 0
label sensor1_max
cmp r4 3
jle sensor2_max
div r4 0
label sensor2_max
mov r5 r2
mul r5 4
add r5 r3
mul r5 4
add r5 r4
add r5 1
# Existing spelling? Exact UTF-8-independent ASCII bytes 1..8.
load8 r7 7100000000000000016
set r0 0
label scan_lexemes
cmp r0 r7
jge new_word
set r8 7100000000000001000
mov r11 r0
mul r11 16
add r8 r11
load8 r9 $r8
cmp r9 r6
jne next_lexeme
set r1 0
label compare_letters
cmp r1 r6
jge existing_spelling
set r11 7100000000000000101
add r11 r1
load8 r12 $r11
mov r13 r8
add r13 r1
add r13 2
load8 r14 $r13
cmp r12 r14
jne next_lexeme
add r1 1
jmp compare_letters
label existing_spelling
mov r11 r8
add r11 1
load8 r9 $r11
set r11 7100000000000000600
add r11 r9
load8 r10 $r11
# Never silently remap an established word to a contradictory referent.
cmp r10 r5
je consistent_evidence
div r10 0
label consistent_evidence
mov r11 r8
add r11 10
load8 r12 $r11
cmp r12 200
jge confidence_capped
add r12 1
store8 $r11 r12
label confidence_capped
jmp erase_grounding
label next_lexeme
add r0 1
jmp scan_lexemes
label new_word
# Assign concept ID by SENSOR features, allowing synonyms without aliases.
load8 r7 7100000000000000017
set r0 1
label scan_grounded_concepts
cmp r0 r7
jgt concept_is_new
set r11 7100000000000000600
add r11 r0
load8 r12 $r11
cmp r12 r5
je reuse_concept
add r0 1
jmp scan_grounded_concepts
label reuse_concept
mov r9 r0
jmp bind_new_spelling
label concept_is_new
cmp r7 16
jlt concept_capacity_ok
div r7 0
label concept_capacity_ok
mov r9 r7
add r9 1
set r11 7100000000000000600
add r11 r9
store8 $r11 r5
store8 7100000000000000017 r9
label bind_new_spelling
load8 r7 7100000000000000016
cmp r7 32
jlt word_capacity_ok
div r7 0
label word_capacity_ok
set r8 7100000000000001000
mov r11 r7
mul r11 16
add r8 r11
store8 $r8 r6
mov r11 r8
add r11 1
store8 $r11 r9
set r1 0
label copy_native_letters
cmp r1 r6
jge lexeme_committed
set r11 7100000000000000101
add r11 r1
load8 r12 $r11
cmp r12 97
jge ascii_low
div r12 0
label ascii_low
cmp r12 122
jle ascii_high
div r12 0
label ascii_high
mov r13 r8
add r13 r1
add r13 2
store8 $r13 r12
add r1 1
jmp copy_native_letters
label lexeme_committed
mov r11 r8
add r11 10
store8 $r11 1
add r7 1
store8 7100000000000000016 r7
label erase_grounding
# A learned concept persists; the example itself is disposable.
set r1 0
label clear_word_intake
set r11 7100000000000000101
add r11 r1
store8 $r11 0
add r1 1
cmp r1 8
jlt clear_word_intake
store8 7100000000000000100 0
store8 7100000000000000120 0
store8 7100000000000000121 0
store8 7100000000000000122 0
store8 7100000000000000125 0
load8 r11 7100000000000000019
cmp r11 250
jge no_more_events
add r11 1
store8 7100000000000000019 r11
label no_more_events
# Output concept ID, number of learned words and concepts.
print r9
load8 r11 7100000000000000016
print r11
load8 r11 7100000000000000017
print r11
mem_stats
stats
