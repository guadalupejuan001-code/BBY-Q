#!reverse-pc-machine-v1
# E009 native XI audit: words, semantic edges, original E008 authority,
# and zero surviving raw teaching events. NO store8 allowed.
load8 r0 7000000000000000610
cmp r0 4
je original_four_banks_preserved
div r0 0
label original_four_banks_preserved
load8 r0 7100000000000000000
cmp r0 76
je language_signature
div r0 0
label language_signature
load8 r0 7100000000000000001
cmp r0 71
je language_component
div r0 0
label language_component
load8 r0 7100000000000000002
cmp r0 1
je language_schema
div r0 0
label language_schema
load8 r5 7100000000000000016
cmp r5 1
jge vocabulary_started
div r5 0
label vocabulary_started
cmp r5 32
jle vocabulary_bounded
div r5 0
label vocabulary_bounded
load8 r6 7100000000000000017
cmp r6 1
jge concepts_exist
div r6 0
label concepts_exist
cmp r6 16
jle concepts_bounded
div r6 0
label concepts_bounded
load8 r7 7100000000000000018
cmp r7 24
jlt graph_bounded
div r7 0
label graph_bounded
set r0 0
label inspect_words
cmp r0 r5
jge inspect_graph
set r8 7100000000000001000
mov r9 r0
mul r9 16
add r8 r9
load8 r10 $r8
cmp r10 1
jge word_length_positive
div r10 0
label word_length_positive
cmp r10 8
jle word_length_bounded
div r10 0
label word_length_bounded
mov r11 r8
add r11 1
load8 r12 $r11
cmp r12 1
jge word_has_concept
div r12 0
label word_has_concept
cmp r12 r6
jle word_concept_valid
div r12 0
label word_concept_valid
set r11 7100000000000000600
add r11 r12
load8 r13 $r11
cmp r13 1
jge feature_present
div r13 0
label feature_present
set r1 0
label inspect_spelling_bytes
cmp r1 r10
jge next_word
mov r11 r8
add r11 r1
add r11 2
load8 r13 $r11
cmp r13 97
jge ascii_low
div r13 0
label ascii_low
cmp r13 122
jle ascii_high
div r13 0
label ascii_high
add r1 1
jmp inspect_spelling_bytes
label next_word
add r0 1
jmp inspect_words
label inspect_graph
set r0 0
label inspect_triple
cmp r0 r7
jge check_no_incoming_data
set r8 7100000000000003000
mov r9 r0
mul r9 8
add r8 r9
set r1 0
label inspect_fact_words
cmp r1 3
jge inspect_fact_counts
mov r11 r8
add r11 r1
load8 r12 $r11
cmp r12 1
jge fact_concept_positive
div r12 0
label fact_concept_positive
cmp r12 r6
jle fact_concept_bounded
div r12 0
label fact_concept_bounded
add r1 1
jmp inspect_fact_words
label inspect_fact_counts
mov r11 r8
add r11 3
load8 r12 $r11
add r11 1
load8 r13 $r11
add r12 r13
cmp r12 1
jge fact_has_evidence
div r12 0
label fact_has_evidence
add r0 1
jmp inspect_triple
label check_no_incoming_data
load8 r13 7100000000000000100
cmp r13 0
je word_length_cleared
div r13 0
label word_length_cleared
load8 r13 7100000000000000125
cmp r13 0
je grounding_marker_cleared
div r13 0
label grounding_marker_cleared
set r0 0
label check_grounding_buffer
set r11 7100000000000000101
add r11 r0
load8 r13 $r11
cmp r13 0
je character_cleared
div r13 0
label character_cleared
add r0 1
cmp r0 8
jlt check_grounding_buffer
set r0 0
label check_sensor_bytes
set r11 7100000000000000120
add r11 r0
load8 r13 $r11
cmp r13 0
je sensor_cleared
div r13 0
label sensor_cleared
add r0 1
cmp r0 3
jlt check_sensor_bytes
set r0 0
label check_triple_intake
set r11 7100000000000000140
add r11 r0
load8 r13 $r11
cmp r13 0
je triple_byte_cleared
div r13 0
label triple_byte_cleared
add r0 1
cmp r0 29
jlt check_triple_intake
load8 r13 7100000000000000170
cmp r13 0
je truth_byte_cleared
div r13 0
label truth_byte_cleared
load8 r13 7100000000000000175
cmp r13 0
je event_marker_cleared
div r13 0
label event_marker_cleared
set r0 0
label check_derived_ids
set r11 7100000000000000180
add r11 r0
load8 r13 $r11
cmp r13 0
je derived_id_cleared
div r13 0
label derived_id_cleared
add r0 1
cmp r0 3
jlt check_derived_ids
# Raw text input was consumed by the XI tokenizer, never persisted.
load8 r13 7100000000000000400
cmp r13 0
je source_line_length_cleared
div r13 0
label source_line_length_cleared
set r0 0
label check_unsegmented_text_erasure
set r11 7100000000000000401
add r11 r0
load8 r13 $r11
cmp r13 0
je raw_text_byte_erased
div r13 0
label raw_text_byte_erased
add r0 1
cmp r0 32
jlt check_unsegmented_text_erasure
# The last inferred response is allowed to remain as a compact utterance plan.
print r5
print r6
print r7
mem_stats
stats
