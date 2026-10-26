#!reverse-pc-machine-v1
# E010 read-only audit: coexistence, grounded prototypes, no raw lessons.
load8 r12 7000000000000000610
cmp r12 4
je original_models_present
div r12 0
label original_models_present
load8 r12 7100000000000000000
cmp r12 76
je original_language_present
div r12 0
label original_language_present
load8 r12 7200000000000000000
cmp r12 83
je school_identity
div r12 0
label school_identity
load8 r12 7200000000000000001
cmp r12 67
je school_magic
div r12 0
label school_magic
load8 r12 7200000000000000002
cmp r12 1
je school_schema
div r12 0
label school_schema
load8 r12 7200000000000000004
cmp r12 1
je spanish
cmp r12 2
je english
div r12 0
label spanish
label english
load8 r6 7200000000000000010
cmp r6 32
jle bounded_memory
div r6 0
label bounded_memory
set r0 0
label check_all_exemplars
cmp r0 r6
jge inspect_scratch
set r8 7200000000000001000
mov r9 r0
mul r9 32
add r8 r9
load8 r9 $r8
cmp r9 1
jge domain_low
div r9 0
label domain_low
cmp r9 4
jle domain_high
div r9 0
label domain_high
mov r12 r8
add r12 4
load8 r10 $r12
cmp r10 1
jge evidence_present
div r10 0
label evidence_present
mov r12 r8
add r12 5
load8 r10 $r12
cmp r10 1
jge spanish_len_low
div r10 0
label spanish_len_low
cmp r10 8
jle spanish_len_high
div r10 0
label spanish_len_high
mov r12 r8
add r12 14
load8 r11 $r12
cmp r11 1
jge english_len_low
div r11 0
label english_len_low
cmp r11 8
jle english_len_high
div r11 0
label english_len_high
set r1 0
label spanish_letters
cmp r1 r10
jge start_english_letters
mov r12 r8
add r12 r1
add r12 6
load8 r13 $r12
cmp r13 97
jge good_es_letter_low
div r13 0
label good_es_letter_low
cmp r13 122
jle good_es_letter_high
div r13 0
label good_es_letter_high
add r1 1
jmp spanish_letters
label start_english_letters
set r1 0
label english_letters
cmp r1 r11
jge next_exemplar
mov r12 r8
add r12 r1
add r12 15
load8 r13 $r12
cmp r13 97
jge good_en_letter_low
div r13 0
label good_en_letter_low
cmp r13 122
jle good_en_letter_high
div r13 0
label good_en_letter_high
add r1 1
jmp english_letters
label next_exemplar
add r0 1
jmp check_all_exemplars
label inspect_scratch
# Raw teaching examples (+100..123) and teacher feedback (+300..301)
# must never remain in a validated committed state.
set r0 0
label erase_assert_training
set r12 7200000000000000100
add r12 r0
load8 r13 $r12
cmp r13 0
je training_cleared
div r13 0
label training_cleared
add r0 1
cmp r0 24
jlt erase_assert_training
set r0 0
label check_operator_lessons
set r12 7200000000000000340
add r12 r0
load8 r13 $r12
cmp r13 0
je operation_sample_erased
div r13 0
label operation_sample_erased
add r0 1
cmp r0 5
jlt check_operator_lessons
set r0 0
label check_math_queries
set r12 7200000000000000320
add r12 r0
load8 r13 $r12
cmp r13 0
je math_query_erased
div r13 0
label math_query_erased
add r0 1
cmp r0 4
jlt check_math_queries
load8 r12 7200000000000000300
cmp r12 0
je grading_marker_erased
div r12 0
label grading_marker_erased
load8 r12 7200000000000000301
cmp r12 0
je grade_label_erased
div r12 0
label grade_label_erased
print r6
load8 r14 7200000000000000011
print r14
load8 r14 7200000000000000003
print r14
mem_stats
stats
