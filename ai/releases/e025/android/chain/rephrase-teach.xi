#!reverse-pc-machine-v1
label m0_entry
# Tokenize real text in XI. A trained E022 reader also allows a single Spanish
# opening question mark at a word boundary after a preamble ("oye, ¿qué...").
# Intake +16=1, +17=byte length, +128..382=raw bytes. Max 15 words of 32 bytes.
# Tokens +512, stride 34; parse error +40. No semantic answers in this stage.
load8 r0 7400000000000000002
cmp r0 1
jne m0_invalid
load8 r0 7400000000000000016
cmp r0 1
jne m0_invalid
load8 r9 7400000000000000017
cmp r9 0
je m0_bad_text
set r0 0
set r1 0
set r2 0
set r10 0
set r11 0
store8 7400000000000000040 0
store8 7400000000000000047 0
label m0_char_loop
cmp r0 r9
jge m0_end_text
set r7 7400000000000000128
add r7 r0
load8 r3 $r7
cmp r3 44
jne m0_ordinary_separator
load8 r7 8100000000000000003
cmp r7 1
je m0_separator
label m0_ordinary_separator
cmp r3 32
je m0_separator
cmp r3 9
je m0_separator
cmp r10 1
je m0_bad_text
cmp r3 46
je m0_period_mark
cmp r3 63
je m0_question_mark
cmp r3 194
je m0_inverted_question
cmp r3 195
je m0_latin_character
cmp r3 95
je m0_write_char
cmp r3 65
jlt m0_check_digit
cmp r3 90
jgt m0_check_alpha
add r3 32
label m0_check_alpha
cmp r3 97
jlt m0_bad_text
cmp r3 122
jgt m0_bad_text
jmp m0_write_char
label m0_check_digit
cmp r3 48
jlt m0_bad_text
cmp r3 57
jgt m0_bad_text
label m0_write_char
cmp r1 15
jge m0_bad_text
cmp r2 32
jge m0_bad_text
set r7 7400000000000000513
mov r8 r1
mul r8 34
add r7 r8
add r7 r2
store8 $r7 r3
add r2 1
jmp m0_next_char
label m0_inverted_question
cmp r11 0
jne m0_bad_text
cmp r1 0
je m0_opening_question
load8 r7 8100000000000000003
cmp r7 1
jne m0_bad_text
label m0_opening_question
cmp r2 0
jne m0_bad_text
add r0 1
cmp r0 r9
jge m0_bad_text
set r7 7400000000000000128
add r7 r0
load8 r3 $r7
cmp r3 191
jne m0_bad_text
set r11 1
store8 7400000000000000047 1
jmp m0_next_char
label m0_latin_character
# Canonical Latin-1 UTF-8: Spanish accents and enye, including uppercase.
cmp r1 15
jge m0_bad_text
cmp r2 30
jgt m0_bad_text
set r7 7400000000000000513
mov r8 r1
mul r8 34
add r7 r8
add r7 r2
store8 $r7 195
add r2 1
add r0 1
cmp r0 r9
jge m0_bad_text
set r7 7400000000000000128
add r7 r0
load8 r3 $r7
cmp r3 128
jlt m0_bad_text
cmp r3 191
jgt m0_bad_text
cmp r3 159
jgt m0_write_char
cmp r3 151
je m0_bad_text
add r3 32
jmp m0_write_char
label m0_period_mark
# A final statement period is enabled only by the conversational XI surface.
load8 r7 7700000000000000016
cmp r7 1
jne m0_bad_text
load8 r7 7700000000000000002
cmp r7 1
jne m0_bad_text
cmp r11 0
jne m0_bad_text
cmp r2 0
jne m0_mark_terminal
cmp r1 0
je m0_bad_text
jmp m0_mark_terminal
label m0_question_mark
store8 7400000000000000047 1
cmp r2 0
jne m0_mark_terminal
cmp r1 0
je m0_bad_text
label m0_mark_terminal
set r10 1
jmp m0_next_char
label m0_separator
cmp r2 0
je m0_next_char
set r7 7400000000000000512
mov r8 r1
mul r8 34
add r7 r8
store8 $r7 r2
add r1 1
set r2 0
label m0_next_char
add r0 1
jmp m0_char_loop
label m0_end_text
cmp r2 0
je m0_finish_tokens
set r7 7400000000000000512
mov r8 r1
mul r8 34
add r7 r8
store8 $r7 r2
add r1 1
label m0_finish_tokens
cmp r1 0
je m0_bad_text
store8 7400000000000000032 r1
jmp m1_entry
label m0_bad_text
store8 7400000000000000040 1
store8 7400000000000000032 0
jmp m1_entry
label m0_invalid
div r0 0
label m1_entry
# Resolve words to SHARED concept IDs. No subject matter or dictionary in code.
# 1..22 use original E010 words directly; only new aliases occupy E012 memory.
# Token +512+i*34; resolved +1600+i*2 = ID, kind (entity/predicate/question).
load8 r0 7400000000000000002
cmp r0 1
jne m1_invalid
load8 r0 7400000000000000016
cmp r0 1
jne m1_invalid
load8 r0 7400000000000000040
cmp r0 0
jne m1_done
load8 r15 7400000000000000032
cmp r15 15
jgt m1_invalid
set r0 0
label m1_token
cmp r0 r15
jge m1_done
set r1 7400000000000000512
mov r2 r0
mul r2 34
add r1 r2
load8 r2 $r1
set r3 0
label m1_old_concept
cmp r3 22
jge m1_new_lexicon
set r4 7200000000000001000
mov r5 r3
mul r5 32
add r4 r5
mov r5 r4
add r5 4
load8 r6 $r5
cmp r6 2
jlt m1_next_old
set r7 5
label m1_old_language
mov r5 r4
add r5 r7
load8 r6 $r5
cmp r6 r2
jne m1_next_old_language
set r8 0
label m1_old_letters
cmp r8 r2
jge m1_old_match
mov r5 r1
add r5 1
add r5 r8
load8 r6 $r5
mov r5 r4
add r5 r7
add r5 1
add r5 r8
load8 r9 $r5
cmp r6 r9
jne m1_next_old_language
add r8 1
jmp m1_old_letters
label m1_old_match
mov r12 r3
add r12 1
set r13 1
jmp m1_save
label m1_next_old_language
cmp r7 5
jne m1_next_old
set r7 14
jmp m1_old_language
label m1_next_old
add r3 1
jmp m1_old_concept
label m1_new_lexicon
load8 r10 7400000000000000004
load8 r5 7400000000000000005
mul r5 256
add r10 r5
cmp r10 512
jgt m1_invalid
set r3 0
label m1_new_word
cmp r3 r10
jge m1_unknown
set r4 7400000000000010000
mov r5 r3
mul r5 40
add r4 r5
mov r5 r4
add r5 3
load8 r6 $r5
cmp r6 r2
jne m1_next_word
set r8 0
label m1_new_letters
cmp r8 r2
jge m1_new_match
mov r5 r1
add r5 1
add r5 r8
load8 r6 $r5
mov r5 r4
add r5 4
add r5 r8
load8 r9 $r5
cmp r6 r9
jne m1_next_word
add r8 1
jmp m1_new_letters
label m1_new_match
load8 r12 $r4
add r4 1
load8 r13 $r4
jmp m1_save
label m1_next_word
add r3 1
jmp m1_new_word
label m1_unknown
set r12 0
set r13 0
label m1_save
set r5 7400000000000001600
mov r6 r0
mul r6 2
add r5 r6
store8 $r5 r12
add r5 1
store8 $r5 r13
add r0 1
jmp m1_token
label m1_done
jmp m2_entry
label m1_invalid
div r0 0
label m2_entry
# Read the old lexicon in place, then the append-only u16 extension. Unknown
# questions never allocate. For old IDs, aliases also normalize old K slots.
load8 r0 7800000000000000002
cmp r0 1
jne m2_done
load8 r0 7400000000000000040
cmp r0 0
jne m2_done
load8 r13 7400000000000000032
load8 r12 7800000000000000006
load8 r14 7800000000000000007
mul r14 256
add r12 r14
cmp r12 8192
jgt m2_invalid
set r0 0
label m2_token
cmp r0 r13
jge m2_done
set r7 7400000000000001600
mov r1 r0
mul r1 2
add r7 r1
load8 r10 $r7
add r7 1
load8 r11 $r7
cmp r10 0
jne m2_save
set r1 7400000000000000512
mov r2 r0
mul r2 34
add r1 r2
load8 r2 $r1
set r3 0
label m2_word
cmp r3 r12
jge m2_save
set r4 8600000000000400000
mov r5 r3
mul r5 40
add r4 r5
mov r7 r4
add r7 4
load8 r5 $r7
cmp r5 r2
jne m2_next_word
set r6 0
label m2_letters
cmp r6 r2
jge m2_found
mov r7 r1
add r7 1
add r7 r6
load8 r8 $r7
mov r7 r4
add r7 5
add r7 r6
load8 r9 $r7
cmp r8 r9
jne m2_next_word
add r6 1
jmp m2_letters
label m2_found
mov r15 r4
load8 r10 $r15
add r15 1
load8 r14 $r15
mul r14 256
add r10 r14
mov r7 r4
add r7 2
load8 r11 $r7
jmp m2_save
label m2_next_word
add r3 1
jmp m2_word
label m2_save
set r7 7800000000000001024
mov r1 r0
mul r1 4
add r7 r1
mov r15 r7
mov r14 r10
mod r14 256
store8 $r15 r14
add r15 1
mov r14 r10
div r14 256
store8 $r15 r14
add r7 2
store8 $r7 r11
cmp r10 255
jgt m2_next_token
set r7 7400000000000001600
mov r1 r0
mul r1 2
add r7 r1
store8 $r7 r10
add r7 1
store8 $r7 r11
label m2_next_token
add r0 1
jmp m2_token
label m2_done
jmp m3_entry
label m2_invalid
div r0 0
label m3_entry
# Supervised construction ID/intent plus semantic labels; no slot ordering is
# supplied. Infer masks from two differently labeled examples, retaining a
# literal possibility until varying examples distinguish it from a variable.
# +176 rewrite bank entry(1..64),+177 intent(1..12),+178 alias token+1,
# +180/182/184 S/P/O u16. This teaches syntax, never answers or facts.
load8 r0 8100000000000000016
load8 r1 7800000000000000176
cmp r0 r1
jne m3_invalid
load8 r0 8100000000000000002
cmp r0 1
jne m3_invalid
load8 r0 8100000000000000003
cmp r0 0
jne m3_invalid
load8 r0 8100000000000000019
cmp r0 1
jne m3_normal_input
load8 r0 8100000000000000020
cmp r0 0
je m3_empty_target
label m3_normal_input
load8 r0 7800000000000000002
cmp r0 1
jne m3_invalid
load8 r0 7400000000000000040
cmp r0 0
jne m3_invalid
load8 r13 7400000000000000032
cmp r13 1
jlt m3_invalid
load8 r0 7800000000000000176
cmp r0 1
jlt m3_invalid
cmp r0 64
jgt m3_invalid
load8 r1 8100000000000000004
cmp r0 r1
jle m3_count_ok
store8 8100000000000000004 r0
label m3_count_ok
sub r0 1
mul r0 96
set r12 8100000000000010000
load8 r1 8100000000000000019
cmp r1 0
je m3_bank_ready
set r12 8100000000000020000
label m3_bank_ready
add r12 r0
load8 r11 7800000000000000177
cmp r11 1
jlt m3_invalid
cmp r11 12
jgt m3_invalid
set r0 7
cmp r11 9
jne m3_not_context_property
set r0 2
label m3_not_context_property
cmp r11 10
jne m3_not_context_verify
set r0 6
label m3_not_context_verify
cmp r11 11
jne m3_not_context_subject
set r0 1
label m3_not_context_subject
cmp r11 12
jne m3_not_context_definition
set r0 0
label m3_not_context_definition
cmp r11 8
jne m3_generic_required
set r0 1
label m3_generic_required
cmp r11 1
jne m3_not_property
set r0 3
label m3_not_property
cmp r11 6
jne m3_not_alias
set r0 9
label m3_not_alias
cmp r11 5
jne m3_required_ready
load8 r1 7800000000000000180
load8 r14 7800000000000000181
mul r14 256
add r1 r14
load8 r2 7800000000000000182
load8 r14 7800000000000000183
mul r14 256
add r2 r14
add r1 r2
load8 r2 7800000000000000184
load8 r14 7800000000000000185
mul r14 256
add r2 r14
add r1 r2
cmp r1 0
jne m3_required_ready
set r0 0
label m3_required_ready
store8 7800000000000000186 r0
set r0 0
label m3_token
cmp r0 r13
jge m3_compare_header
set r7 7800000000000001024
mov r1 r0
mul r1 4
add r7 r1
mov r15 r7
load8 r8 $r15
add r15 1
load8 r14 $r15
mul r14 256
add r8 r14
add r7 2
load8 r9 $r7
load8 r1 7800000000000000178
mov r2 r0
add r2 1
cmp r1 r2
je m3_alias
cmp r8 0
je m3_invalid
set r10 16
load8 r1 7800000000000000180
load8 r14 7800000000000000181
mul r14 256
add r1 r14
cmp r1 0
je m3_predicate
cmp r8 r1
jne m3_predicate
add r10 1
label m3_predicate
load8 r1 7800000000000000182
load8 r14 7800000000000000183
mul r14 256
add r1 r14
cmp r1 0
je m3_object
cmp r8 r1
jne m3_object
add r10 2
label m3_object
load8 r1 7800000000000000184
load8 r14 7800000000000000185
mul r14 256
add r1 r14
cmp r1 0
je m3_descriptor
cmp r8 r1
jne m3_descriptor
add r10 4
jmp m3_descriptor
label m3_alias
set r10 8
label m3_descriptor
set r7 7800000000000002048
mov r1 r0
mul r1 4
add r7 r1
store8 $r7 r10
add r7 1
mov r15 r7
mov r14 r8
mod r14 256
store8 $r15 r14
add r15 1
mov r14 r8
div r14 256
store8 $r15 r14
add r7 2
store8 $r7 r9
add r0 1
jmp m3_token
label m3_compare_header
load8 r0 $r12
cmp r0 0
je m3_allocate
cmp r0 r13
jne m3_invalid
mov r7 r12
add r7 1
load8 r0 $r7
cmp r0 r11
jne m3_invalid
set r0 0
label m3_intersect_slot
cmp r0 r13
jge m3_second_witness
mov r7 r12
add r7 16
mov r1 r0
mul r1 4
add r7 r1
load8 r2 $r7
set r8 7800000000000002048
add r8 r1
load8 r3 $r8
mov r9 r7
add r9 1
mov r15 r9
load8 r4 $r15
add r15 1
load8 r14 $r15
mul r14 256
add r4 r14
mov r9 r8
add r9 1
mov r15 r9
load8 r5 $r15
add r15 1
load8 r14 $r15
mul r14 256
add r5 r14
set r6 1
set r10 0
label m3_bit
cmp r6 32
jge m3_mask_ready
mov r1 r2
div r1 r6
mod r1 2
cmp r1 0
je m3_next_bit
mov r1 r3
div r1 r6
mod r1 2
cmp r1 0
je m3_next_bit
cmp r6 16
jne m3_keep_bit
cmp r4 r5
jne m3_next_bit
mov r9 r7
add r9 3
load8 r1 $r9
mov r9 r8
add r9 3
load8 r11 $r9
cmp r1 r11
jne m3_next_bit
label m3_keep_bit
add r10 r6
label m3_next_bit
mul r6 2
jmp m3_bit
label m3_mask_ready
cmp r10 0
je m3_invalid
store8 $r7 r10
add r0 1
jmp m3_intersect_slot
label m3_allocate
store8 $r12 r13
mov r7 r12
add r7 1
store8 $r7 r11
add r7 2
store8 $r7 1
add r7 1
load8 r0 7800000000000000180
load8 r14 7800000000000000181
mul r14 256
add r0 r14
mov r15 r7
mov r14 r0
mod r14 256
store8 $r15 r14
add r15 1
mov r14 r0
div r14 256
store8 $r15 r14
add r7 2
load8 r0 7800000000000000182
load8 r14 7800000000000000183
mul r14 256
add r0 r14
mov r15 r7
mov r14 r0
mod r14 256
store8 $r15 r14
add r15 1
mov r14 r0
div r14 256
store8 $r15 r14
add r7 2
load8 r0 7800000000000000184
load8 r14 7800000000000000185
mul r14 256
add r0 r14
mov r15 r7
mov r14 r0
mod r14 256
store8 $r15 r14
add r15 1
mov r14 r0
div r14 256
store8 $r15 r14
mov r1 r13
mul r1 4
set r0 0
label m3_copy_slots
cmp r0 r1
jge m3_promote
set r7 7800000000000002048
add r7 r0
load8 r2 $r7
mov r7 r12
add r7 16
add r7 r0
store8 $r7 r2
add r0 1
jmp m3_copy_slots
label m3_second_witness
load8 r0 7800000000000000186
cmp r0 0
je m3_promote
set r1 0
set r3 1
label m3_distinct_role
cmp r1 3
jge m3_witness_ready
# A supervised predicate role may remain the same across examples. A single
# occurrence can still be distinguished from literal positions below.
cmp r1 1
jne m3_varied_role
# A predicate-only contextual frame must also vary its one explicit role.
cmp r0 2
jne m3_next_role
label m3_varied_role
mov r2 r0
div r2 r3
mod r2 2
cmp r2 0
je m3_next_role
set r7 7800000000000000180
mov r2 r1
mul r2 2
add r7 r2
mov r15 r7
load8 r4 $r15
add r15 1
load8 r14 $r15
mul r14 256
add r4 r14
mov r7 r12
add r7 4
add r7 r2
mov r15 r7
load8 r5 $r15
add r15 1
load8 r14 $r15
mul r14 256
add r5 r14
cmp r4 r5
je m3_promote
label m3_next_role
add r1 1
mul r3 2
jmp m3_distinct_role
label m3_witness_ready
mov r7 r12
add r7 3
store8 $r7 2
add r7 7
load8 r0 7800000000000000180
load8 r14 7800000000000000181
mul r14 256
add r0 r14
mov r15 r7
mov r14 r0
mod r14 256
store8 $r15 r14
add r15 1
mov r14 r0
div r14 256
store8 $r15 r14
add r7 2
load8 r0 7800000000000000182
load8 r14 7800000000000000183
mul r14 256
add r0 r14
mov r15 r7
mov r14 r0
mod r14 256
store8 $r15 r14
add r15 1
mov r14 r0
div r14 256
store8 $r15 r14
add r7 2
load8 r0 7800000000000000184
load8 r14 7800000000000000185
mul r14 256
add r0 r14
mov r15 r7
mov r14 r0
mod r14 256
store8 $r15 r14
add r15 1
mov r14 r0
div r14 256
store8 $r15 r14
label m3_promote
mov r7 r12
add r7 2
store8 $r7 0
load8 r0 7800000000000000186
cmp r0 0
je m3_check_slots
add r7 1
load8 r1 $r7
cmp r1 2
jne m3_done
label m3_check_slots
# Force a supervised variable when it has exactly one compatible position.
# Multiple occurrences (e.g. two copies of "is") remain ambiguous until
# varying examples distinguish the literal prefix from the predicate slot.
set r3 1
label m3_force_role
cmp r3 16
jge m3_forced_ready
load8 r4 7800000000000000186
div r4 r3
mod r4 2
cmp r4 0
je m3_force_next
set r0 0
set r4 0
set r6 0
label m3_force_scan
cmp r0 r13
jge m3_force_found
mov r7 r12
add r7 16
mov r1 r0
mul r1 4
add r7 r1
load8 r2 $r7
div r2 r3
mod r2 2
cmp r2 0
je m3_force_scan_next
add r4 1
mov r6 r7
label m3_force_scan_next
add r0 1
jmp m3_force_scan
label m3_force_found
cmp r4 1
jne m3_force_next
store8 $r6 r3
label m3_force_next
mul r3 2
jmp m3_force_role
label m3_forced_ready
set r0 0
set r8 0
label m3_unique
cmp r0 r13
jge m3_unique_done
mov r7 r12
add r7 16
mov r1 r0
mul r1 4
add r7 r1
load8 r2 $r7
cmp r2 16
je m3_next_slot
cmp r2 1
je m3_variable
cmp r2 2
je m3_variable
cmp r2 4
je m3_variable
cmp r2 8
jne m3_done
label m3_variable
mov r1 r8
div r1 r2
mod r1 2
cmp r1 0
jne m3_invalid
add r8 r2
label m3_next_slot
add r0 1
jmp m3_unique
label m3_unique_done
load8 r0 7800000000000000186
cmp r8 r0
jne m3_done
mov r7 r12
add r7 2
store8 $r7 1
label m3_done
jmp m4_entry
label m3_empty_target
load8 r0 7800000000000000180
load8 r1 7800000000000000181
add r0 r1
load8 r1 7800000000000000182
add r0 r1
load8 r1 7800000000000000183
add r0 r1
load8 r1 7800000000000000184
add r0 r1
load8 r1 7800000000000000185
add r0 r1
cmp r0 0
jne m3_invalid
load8 r0 7800000000000000176
cmp r0 1
jlt m3_invalid
cmp r0 64
jgt m3_invalid
sub r0 1
mul r0 96
set r7 8100000000000020000
add r7 r0
load8 r0 $r7
cmp r0 0
jne m3_invalid
add r7 1
store8 $r7 5
add r7 1
store8 $r7 1
add r7 1
store8 $r7 1
jmp m4_entry
label m3_invalid
div r0 0
label m4_entry
load8 r0 8100000000000000002
cmp r0 1
jne m4_invalid
load8 r0 8100000000000000003
cmp r0 0
jne m4_invalid
store8 8100000000000000019 1
set r0 0
label m4_clear_raw
set r7 7400000000000000128
add r7 r0
store8 $r7 0
add r0 1
cmp r0 255
jlt m4_clear_raw
set r0 0
label m4_copy_target
load8 r1 8100000000000000020
cmp r0 r1
jge m4_clear_tokens
set r7 8100000000000000512
add r7 r0
load8 r2 $r7
set r7 7400000000000000128
add r7 r0
store8 $r7 r2
add r0 1
jmp m4_copy_target
label m4_clear_tokens
set r0 0
label m4_token_byte
set r7 7400000000000000512
add r7 r0
store8 $r7 0
add r0 1
cmp r0 510
jlt m4_token_byte
set r0 0
label m4_resolved_byte
set r7 7400000000000001600
add r7 r0
store8 $r7 0
add r0 1
cmp r0 30
jlt m4_resolved_byte
set r0 0
label m4_open_byte
set r7 7800000000000001024
add r7 r0
store8 $r7 0
set r7 7800000000000002048
add r7 r0
store8 $r7 0
add r0 1
cmp r0 60
jlt m4_open_byte
store8 7400000000000000016 1
load8 r0 8100000000000000020
store8 7400000000000000017 r0
store8 7400000000000000032 0
store8 7400000000000000040 0
store8 7400000000000000047 0
jmp m5_entry
label m4_invalid
div r0 0
label m5_entry
# Tokenize real text in XI. A trained E022 reader also allows a single Spanish
# opening question mark at a word boundary after a preamble ("oye, ¿qué...").
# Intake +16=1, +17=byte length, +128..382=raw bytes. Max 15 words of 32 bytes.
# Tokens +512, stride 34; parse error +40. No semantic answers in this stage.
load8 r0 7400000000000000002
cmp r0 1
jne m5_invalid
load8 r0 7400000000000000016
cmp r0 1
jne m5_invalid
load8 r9 7400000000000000017
cmp r9 0
je m5_bad_text
set r0 0
set r1 0
set r2 0
set r10 0
set r11 0
store8 7400000000000000040 0
store8 7400000000000000047 0
label m5_char_loop
cmp r0 r9
jge m5_end_text
set r7 7400000000000000128
add r7 r0
load8 r3 $r7
cmp r3 44
jne m5_ordinary_separator
load8 r7 8100000000000000003
cmp r7 1
je m5_separator
label m5_ordinary_separator
cmp r3 32
je m5_separator
cmp r3 9
je m5_separator
cmp r10 1
je m5_bad_text
cmp r3 46
je m5_period_mark
cmp r3 63
je m5_question_mark
cmp r3 194
je m5_inverted_question
cmp r3 195
je m5_latin_character
cmp r3 95
je m5_write_char
cmp r3 65
jlt m5_check_digit
cmp r3 90
jgt m5_check_alpha
add r3 32
label m5_check_alpha
cmp r3 97
jlt m5_bad_text
cmp r3 122
jgt m5_bad_text
jmp m5_write_char
label m5_check_digit
cmp r3 48
jlt m5_bad_text
cmp r3 57
jgt m5_bad_text
label m5_write_char
cmp r1 15
jge m5_bad_text
cmp r2 32
jge m5_bad_text
set r7 7400000000000000513
mov r8 r1
mul r8 34
add r7 r8
add r7 r2
store8 $r7 r3
add r2 1
jmp m5_next_char
label m5_inverted_question
cmp r11 0
jne m5_bad_text
cmp r1 0
je m5_opening_question
load8 r7 8100000000000000003
cmp r7 1
jne m5_bad_text
label m5_opening_question
cmp r2 0
jne m5_bad_text
add r0 1
cmp r0 r9
jge m5_bad_text
set r7 7400000000000000128
add r7 r0
load8 r3 $r7
cmp r3 191
jne m5_bad_text
set r11 1
store8 7400000000000000047 1
jmp m5_next_char
label m5_latin_character
# Canonical Latin-1 UTF-8: Spanish accents and enye, including uppercase.
cmp r1 15
jge m5_bad_text
cmp r2 30
jgt m5_bad_text
set r7 7400000000000000513
mov r8 r1
mul r8 34
add r7 r8
add r7 r2
store8 $r7 195
add r2 1
add r0 1
cmp r0 r9
jge m5_bad_text
set r7 7400000000000000128
add r7 r0
load8 r3 $r7
cmp r3 128
jlt m5_bad_text
cmp r3 191
jgt m5_bad_text
cmp r3 159
jgt m5_write_char
cmp r3 151
je m5_bad_text
add r3 32
jmp m5_write_char
label m5_period_mark
# A final statement period is enabled only by the conversational XI surface.
load8 r7 7700000000000000016
cmp r7 1
jne m5_bad_text
load8 r7 7700000000000000002
cmp r7 1
jne m5_bad_text
cmp r11 0
jne m5_bad_text
cmp r2 0
jne m5_mark_terminal
cmp r1 0
je m5_bad_text
jmp m5_mark_terminal
label m5_question_mark
store8 7400000000000000047 1
cmp r2 0
jne m5_mark_terminal
cmp r1 0
je m5_bad_text
label m5_mark_terminal
set r10 1
jmp m5_next_char
label m5_separator
cmp r2 0
je m5_next_char
set r7 7400000000000000512
mov r8 r1
mul r8 34
add r7 r8
store8 $r7 r2
add r1 1
set r2 0
label m5_next_char
add r0 1
jmp m5_char_loop
label m5_end_text
cmp r2 0
je m5_finish_tokens
set r7 7400000000000000512
mov r8 r1
mul r8 34
add r7 r8
store8 $r7 r2
add r1 1
label m5_finish_tokens
cmp r1 0
je m5_bad_text
store8 7400000000000000032 r1
jmp m6_entry
label m5_bad_text
store8 7400000000000000040 1
store8 7400000000000000032 0
jmp m6_entry
label m5_invalid
div r0 0
label m6_entry
# Resolve words to SHARED concept IDs. No subject matter or dictionary in code.
# 1..22 use original E010 words directly; only new aliases occupy E012 memory.
# Token +512+i*34; resolved +1600+i*2 = ID, kind (entity/predicate/question).
load8 r0 7400000000000000002
cmp r0 1
jne m6_invalid
load8 r0 7400000000000000016
cmp r0 1
jne m6_invalid
load8 r0 7400000000000000040
cmp r0 0
jne m6_done
load8 r15 7400000000000000032
cmp r15 15
jgt m6_invalid
set r0 0
label m6_token
cmp r0 r15
jge m6_done
set r1 7400000000000000512
mov r2 r0
mul r2 34
add r1 r2
load8 r2 $r1
set r3 0
label m6_old_concept
cmp r3 22
jge m6_new_lexicon
set r4 7200000000000001000
mov r5 r3
mul r5 32
add r4 r5
mov r5 r4
add r5 4
load8 r6 $r5
cmp r6 2
jlt m6_next_old
set r7 5
label m6_old_language
mov r5 r4
add r5 r7
load8 r6 $r5
cmp r6 r2
jne m6_next_old_language
set r8 0
label m6_old_letters
cmp r8 r2
jge m6_old_match
mov r5 r1
add r5 1
add r5 r8
load8 r6 $r5
mov r5 r4
add r5 r7
add r5 1
add r5 r8
load8 r9 $r5
cmp r6 r9
jne m6_next_old_language
add r8 1
jmp m6_old_letters
label m6_old_match
mov r12 r3
add r12 1
set r13 1
jmp m6_save
label m6_next_old_language
cmp r7 5
jne m6_next_old
set r7 14
jmp m6_old_language
label m6_next_old
add r3 1
jmp m6_old_concept
label m6_new_lexicon
load8 r10 7400000000000000004
load8 r5 7400000000000000005
mul r5 256
add r10 r5
cmp r10 512
jgt m6_invalid
set r3 0
label m6_new_word
cmp r3 r10
jge m6_unknown
set r4 7400000000000010000
mov r5 r3
mul r5 40
add r4 r5
mov r5 r4
add r5 3
load8 r6 $r5
cmp r6 r2
jne m6_next_word
set r8 0
label m6_new_letters
cmp r8 r2
jge m6_new_match
mov r5 r1
add r5 1
add r5 r8
load8 r6 $r5
mov r5 r4
add r5 4
add r5 r8
load8 r9 $r5
cmp r6 r9
jne m6_next_word
add r8 1
jmp m6_new_letters
label m6_new_match
load8 r12 $r4
add r4 1
load8 r13 $r4
jmp m6_save
label m6_next_word
add r3 1
jmp m6_new_word
label m6_unknown
set r12 0
set r13 0
label m6_save
set r5 7400000000000001600
mov r6 r0
mul r6 2
add r5 r6
store8 $r5 r12
add r5 1
store8 $r5 r13
add r0 1
jmp m6_token
label m6_done
jmp m7_entry
label m6_invalid
div r0 0
label m7_entry
# Read the old lexicon in place, then the append-only u16 extension. Unknown
# questions never allocate. For old IDs, aliases also normalize old K slots.
load8 r0 7800000000000000002
cmp r0 1
jne m7_done
load8 r0 7400000000000000040
cmp r0 0
jne m7_done
load8 r13 7400000000000000032
load8 r12 7800000000000000006
load8 r14 7800000000000000007
mul r14 256
add r12 r14
cmp r12 8192
jgt m7_invalid
set r0 0
label m7_token
cmp r0 r13
jge m7_done
set r7 7400000000000001600
mov r1 r0
mul r1 2
add r7 r1
load8 r10 $r7
add r7 1
load8 r11 $r7
cmp r10 0
jne m7_save
set r1 7400000000000000512
mov r2 r0
mul r2 34
add r1 r2
load8 r2 $r1
set r3 0
label m7_word
cmp r3 r12
jge m7_save
set r4 8600000000000400000
mov r5 r3
mul r5 40
add r4 r5
mov r7 r4
add r7 4
load8 r5 $r7
cmp r5 r2
jne m7_next_word
set r6 0
label m7_letters
cmp r6 r2
jge m7_found
mov r7 r1
add r7 1
add r7 r6
load8 r8 $r7
mov r7 r4
add r7 5
add r7 r6
load8 r9 $r7
cmp r8 r9
jne m7_next_word
add r6 1
jmp m7_letters
label m7_found
mov r15 r4
load8 r10 $r15
add r15 1
load8 r14 $r15
mul r14 256
add r10 r14
mov r7 r4
add r7 2
load8 r11 $r7
jmp m7_save
label m7_next_word
add r3 1
jmp m7_word
label m7_save
set r7 7800000000000001024
mov r1 r0
mul r1 4
add r7 r1
mov r15 r7
mov r14 r10
mod r14 256
store8 $r15 r14
add r15 1
mov r14 r10
div r14 256
store8 $r15 r14
add r7 2
store8 $r7 r11
cmp r10 255
jgt m7_next_token
set r7 7400000000000001600
mov r1 r0
mul r1 2
add r7 r1
store8 $r7 r10
add r7 1
store8 $r7 r11
label m7_next_token
add r0 1
jmp m7_token
label m7_done
jmp m8_entry
label m7_invalid
div r0 0
label m8_entry
# Supervised construction ID/intent plus semantic labels; no slot ordering is
# supplied. Infer masks from two differently labeled examples, retaining a
# literal possibility until varying examples distinguish it from a variable.
# +176 rewrite bank entry(1..64),+177 intent(1..12),+178 alias token+1,
# +180/182/184 S/P/O u16. This teaches syntax, never answers or facts.
load8 r0 8100000000000000016
load8 r1 7800000000000000176
cmp r0 r1
jne m8_invalid
load8 r0 8100000000000000002
cmp r0 1
jne m8_invalid
load8 r0 8100000000000000003
cmp r0 0
jne m8_invalid
load8 r0 8100000000000000019
cmp r0 1
jne m8_normal_input
load8 r0 8100000000000000020
cmp r0 0
je m8_empty_target
label m8_normal_input
load8 r0 7800000000000000002
cmp r0 1
jne m8_invalid
load8 r0 7400000000000000040
cmp r0 0
jne m8_invalid
load8 r13 7400000000000000032
cmp r13 1
jlt m8_invalid
load8 r0 7800000000000000176
cmp r0 1
jlt m8_invalid
cmp r0 64
jgt m8_invalid
load8 r1 8100000000000000004
cmp r0 r1
jle m8_count_ok
store8 8100000000000000004 r0
label m8_count_ok
sub r0 1
mul r0 96
set r12 8100000000000010000
load8 r1 8100000000000000019
cmp r1 0
je m8_bank_ready
set r12 8100000000000020000
label m8_bank_ready
add r12 r0
load8 r11 7800000000000000177
cmp r11 1
jlt m8_invalid
cmp r11 12
jgt m8_invalid
set r0 7
cmp r11 9
jne m8_not_context_property
set r0 2
label m8_not_context_property
cmp r11 10
jne m8_not_context_verify
set r0 6
label m8_not_context_verify
cmp r11 11
jne m8_not_context_subject
set r0 1
label m8_not_context_subject
cmp r11 12
jne m8_not_context_definition
set r0 0
label m8_not_context_definition
cmp r11 8
jne m8_generic_required
set r0 1
label m8_generic_required
cmp r11 1
jne m8_not_property
set r0 3
label m8_not_property
cmp r11 6
jne m8_not_alias
set r0 9
label m8_not_alias
cmp r11 5
jne m8_required_ready
load8 r1 7800000000000000180
load8 r14 7800000000000000181
mul r14 256
add r1 r14
load8 r2 7800000000000000182
load8 r14 7800000000000000183
mul r14 256
add r2 r14
add r1 r2
load8 r2 7800000000000000184
load8 r14 7800000000000000185
mul r14 256
add r2 r14
add r1 r2
cmp r1 0
jne m8_required_ready
set r0 0
label m8_required_ready
store8 7800000000000000186 r0
set r0 0
label m8_token
cmp r0 r13
jge m8_compare_header
set r7 7800000000000001024
mov r1 r0
mul r1 4
add r7 r1
mov r15 r7
load8 r8 $r15
add r15 1
load8 r14 $r15
mul r14 256
add r8 r14
add r7 2
load8 r9 $r7
load8 r1 7800000000000000178
mov r2 r0
add r2 1
cmp r1 r2
je m8_alias
cmp r8 0
je m8_invalid
set r10 16
load8 r1 7800000000000000180
load8 r14 7800000000000000181
mul r14 256
add r1 r14
cmp r1 0
je m8_predicate
cmp r8 r1
jne m8_predicate
add r10 1
label m8_predicate
load8 r1 7800000000000000182
load8 r14 7800000000000000183
mul r14 256
add r1 r14
cmp r1 0
je m8_object
cmp r8 r1
jne m8_object
add r10 2
label m8_object
load8 r1 7800000000000000184
load8 r14 7800000000000000185
mul r14 256
add r1 r14
cmp r1 0
je m8_descriptor
cmp r8 r1
jne m8_descriptor
add r10 4
jmp m8_descriptor
label m8_alias
set r10 8
label m8_descriptor
set r7 7800000000000002048
mov r1 r0
mul r1 4
add r7 r1
store8 $r7 r10
add r7 1
mov r15 r7
mov r14 r8
mod r14 256
store8 $r15 r14
add r15 1
mov r14 r8
div r14 256
store8 $r15 r14
add r7 2
store8 $r7 r9
add r0 1
jmp m8_token
label m8_compare_header
load8 r0 $r12
cmp r0 0
je m8_allocate
cmp r0 r13
jne m8_invalid
mov r7 r12
add r7 1
load8 r0 $r7
cmp r0 r11
jne m8_invalid
set r0 0
label m8_intersect_slot
cmp r0 r13
jge m8_second_witness
mov r7 r12
add r7 16
mov r1 r0
mul r1 4
add r7 r1
load8 r2 $r7
set r8 7800000000000002048
add r8 r1
load8 r3 $r8
mov r9 r7
add r9 1
mov r15 r9
load8 r4 $r15
add r15 1
load8 r14 $r15
mul r14 256
add r4 r14
mov r9 r8
add r9 1
mov r15 r9
load8 r5 $r15
add r15 1
load8 r14 $r15
mul r14 256
add r5 r14
set r6 1
set r10 0
label m8_bit
cmp r6 32
jge m8_mask_ready
mov r1 r2
div r1 r6
mod r1 2
cmp r1 0
je m8_next_bit
mov r1 r3
div r1 r6
mod r1 2
cmp r1 0
je m8_next_bit
cmp r6 16
jne m8_keep_bit
cmp r4 r5
jne m8_next_bit
mov r9 r7
add r9 3
load8 r1 $r9
mov r9 r8
add r9 3
load8 r11 $r9
cmp r1 r11
jne m8_next_bit
label m8_keep_bit
add r10 r6
label m8_next_bit
mul r6 2
jmp m8_bit
label m8_mask_ready
cmp r10 0
je m8_invalid
store8 $r7 r10
add r0 1
jmp m8_intersect_slot
label m8_allocate
store8 $r12 r13
mov r7 r12
add r7 1
store8 $r7 r11
add r7 2
store8 $r7 1
add r7 1
load8 r0 7800000000000000180
load8 r14 7800000000000000181
mul r14 256
add r0 r14
mov r15 r7
mov r14 r0
mod r14 256
store8 $r15 r14
add r15 1
mov r14 r0
div r14 256
store8 $r15 r14
add r7 2
load8 r0 7800000000000000182
load8 r14 7800000000000000183
mul r14 256
add r0 r14
mov r15 r7
mov r14 r0
mod r14 256
store8 $r15 r14
add r15 1
mov r14 r0
div r14 256
store8 $r15 r14
add r7 2
load8 r0 7800000000000000184
load8 r14 7800000000000000185
mul r14 256
add r0 r14
mov r15 r7
mov r14 r0
mod r14 256
store8 $r15 r14
add r15 1
mov r14 r0
div r14 256
store8 $r15 r14
mov r1 r13
mul r1 4
set r0 0
label m8_copy_slots
cmp r0 r1
jge m8_promote
set r7 7800000000000002048
add r7 r0
load8 r2 $r7
mov r7 r12
add r7 16
add r7 r0
store8 $r7 r2
add r0 1
jmp m8_copy_slots
label m8_second_witness
load8 r0 7800000000000000186
cmp r0 0
je m8_promote
set r1 0
set r3 1
label m8_distinct_role
cmp r1 3
jge m8_witness_ready
# A supervised predicate role may remain the same across examples. A single
# occurrence can still be distinguished from literal positions below.
cmp r1 1
jne m8_varied_role
# A predicate-only contextual frame must also vary its one explicit role.
cmp r0 2
jne m8_next_role
label m8_varied_role
mov r2 r0
div r2 r3
mod r2 2
cmp r2 0
je m8_next_role
set r7 7800000000000000180
mov r2 r1
mul r2 2
add r7 r2
mov r15 r7
load8 r4 $r15
add r15 1
load8 r14 $r15
mul r14 256
add r4 r14
mov r7 r12
add r7 4
add r7 r2
mov r15 r7
load8 r5 $r15
add r15 1
load8 r14 $r15
mul r14 256
add r5 r14
cmp r4 r5
je m8_promote
label m8_next_role
add r1 1
mul r3 2
jmp m8_distinct_role
label m8_witness_ready
mov r7 r12
add r7 3
store8 $r7 2
add r7 7
load8 r0 7800000000000000180
load8 r14 7800000000000000181
mul r14 256
add r0 r14
mov r15 r7
mov r14 r0
mod r14 256
store8 $r15 r14
add r15 1
mov r14 r0
div r14 256
store8 $r15 r14
add r7 2
load8 r0 7800000000000000182
load8 r14 7800000000000000183
mul r14 256
add r0 r14
mov r15 r7
mov r14 r0
mod r14 256
store8 $r15 r14
add r15 1
mov r14 r0
div r14 256
store8 $r15 r14
add r7 2
load8 r0 7800000000000000184
load8 r14 7800000000000000185
mul r14 256
add r0 r14
mov r15 r7
mov r14 r0
mod r14 256
store8 $r15 r14
add r15 1
mov r14 r0
div r14 256
store8 $r15 r14
label m8_promote
mov r7 r12
add r7 2
store8 $r7 0
load8 r0 7800000000000000186
cmp r0 0
je m8_check_slots
add r7 1
load8 r1 $r7
cmp r1 2
jne m8_done
label m8_check_slots
# Force a supervised variable when it has exactly one compatible position.
# Multiple occurrences (e.g. two copies of "is") remain ambiguous until
# varying examples distinguish the literal prefix from the predicate slot.
set r3 1
label m8_force_role
cmp r3 16
jge m8_forced_ready
load8 r4 7800000000000000186
div r4 r3
mod r4 2
cmp r4 0
je m8_force_next
set r0 0
set r4 0
set r6 0
label m8_force_scan
cmp r0 r13
jge m8_force_found
mov r7 r12
add r7 16
mov r1 r0
mul r1 4
add r7 r1
load8 r2 $r7
div r2 r3
mod r2 2
cmp r2 0
je m8_force_scan_next
add r4 1
mov r6 r7
label m8_force_scan_next
add r0 1
jmp m8_force_scan
label m8_force_found
cmp r4 1
jne m8_force_next
store8 $r6 r3
label m8_force_next
mul r3 2
jmp m8_force_role
label m8_forced_ready
set r0 0
set r8 0
label m8_unique
cmp r0 r13
jge m8_unique_done
mov r7 r12
add r7 16
mov r1 r0
mul r1 4
add r7 r1
load8 r2 $r7
cmp r2 16
je m8_next_slot
cmp r2 1
je m8_variable
cmp r2 2
je m8_variable
cmp r2 4
je m8_variable
cmp r2 8
jne m8_done
label m8_variable
mov r1 r8
div r1 r2
mod r1 2
cmp r1 0
jne m8_invalid
add r8 r2
label m8_next_slot
add r0 1
jmp m8_unique
label m8_unique_done
load8 r0 7800000000000000186
cmp r8 r0
jne m8_done
mov r7 r12
add r7 2
store8 $r7 1
label m8_done
jmp m9_entry
label m8_empty_target
load8 r0 7800000000000000180
load8 r1 7800000000000000181
add r0 r1
load8 r1 7800000000000000182
add r0 r1
load8 r1 7800000000000000183
add r0 r1
load8 r1 7800000000000000184
add r0 r1
load8 r1 7800000000000000185
add r0 r1
cmp r0 0
jne m8_invalid
load8 r0 7800000000000000176
cmp r0 1
jlt m8_invalid
cmp r0 64
jgt m8_invalid
sub r0 1
mul r0 96
set r7 8100000000000020000
add r7 r0
load8 r0 $r7
cmp r0 0
jne m8_invalid
add r7 1
store8 $r7 5
add r7 1
store8 $r7 1
add r7 1
store8 $r7 1
jmp m9_entry
label m8_invalid
div r0 0
label m9_entry
load8 r0 8100000000000000016
cmp r0 1
jlt m9_invalid
cmp r0 64
jgt m9_invalid
sub r0 1
mov r1 r0
mul r1 8
set r12 8100000000000030000
add r12 r1
load8 r1 $r12
cmp r1 0
je m9_new_meta
load8 r2 8100000000000000017
cmp r1 r2
jne m9_invalid
mov r7 r12
add r7 1
load8 r1 $r7
load8 r2 8100000000000000018
cmp r1 r2
jne m9_invalid
jmp m9_count
label m9_new_meta
load8 r1 8100000000000000017
cmp r1 1
jlt m9_invalid
cmp r1 4
jgt m9_invalid
store8 $r12 r1
mov r7 r12
add r7 1
load8 r1 8100000000000000018
cmp r1 2
jgt m9_invalid
store8 $r7 r1
mul r0 512
set r10 8100000000000040000
add r10 r0
set r0 0
label m9_canonical_raw
cmp r0 510
jge m9_count
set r7 7400000000000000512
add r7 r0
load8 r1 $r7
mov r7 r10
add r7 r0
store8 $r7 r1
add r0 1
jmp m9_canonical_raw
label m9_count
mov r7 r12
add r7 2
load8 r0 $r7
add r7 1
load8 r14 $r7
mul r14 256
add r0 r14
cmp r0 65535
jge m9_invalid
add r0 1
mov r1 r0
mod r1 256
sub r7 1
store8 $r7 r1
add r7 1
div r0 256
store8 $r7 r0
# Count the pair as one presentation, not two separate utterances.
set r7 8100000000000000008
set r0 1
set r1 0
label m9_total_count
cmp r1 4
jge m9_done
load8 r2 $r7
add r2 r0
mov r0 r2
div r0 256
mod r2 256
store8 $r7 r2
add r7 1
add r1 1
jmp m9_total_count
label m9_done
jmp m10_entry
label m9_invalid
div r0 0
label m10_entry
# E013: clear bounded actual intake and the visited-node queue, preserving the
# same E012 clean-state invariant. Token slots are cleared even after bad input.
load8 r2 7400000000000000017
load8 r3 7400000000000000050
set r0 0
label m10_visited
cmp r0 r3
jge m10_raw_start
set r7 7400000000000003000
add r7 r0
load8 r1 $r7
cmp r1 1
jlt m10_invalid
store8 $r7 0
set r7 7400000000000003400
add r7 r1
store8 $r7 0
set r7 7400000000000003800
add r7 r1
store8 $r7 0
set r7 7400000000000004200
add r7 r1
store8 $r7 0
add r0 1
jmp m10_visited
label m10_raw_start
set r0 0
label m10_raw
cmp r0 r2
jge m10_token_start
set r7 7400000000000000128
add r7 r0
store8 $r7 0
add r0 1
jmp m10_raw
label m10_token_start
set r0 0
label m10_tokens
set r7 7400000000000000512
add r7 r0
store8 $r7 0
add r0 1
cmp r0 510
jlt m10_tokens
set r0 0
label m10_resolved
set r7 7400000000000001600
add r7 r0
store8 $r7 0
add r0 1
cmp r0 30
jlt m10_resolved
set r0 16
label m10_control
set r7 7400000000000000000
add r7 r0
store8 $r7 0
add r0 1
cmp r0 64
jlt m10_control
jmp m11_entry
label m10_invalid
div r0 0
label m11_entry
load8 r0 7800000000000000002
cmp r0 0
je m11_done
cmp r0 1
jne m11_invalid
# A delegated query is only a context if the actual legacy search succeeded.
# Do not preserve the speculative slots of an unanswered question.
load8 r0 7800000000000000067
cmp r0 0
jne m11_context_ready
load8 r0 7800000000000000012
cmp r0 1
jne m11_context_ready
load8 r0 7400000000000000008
cmp r0 1
je m11_context_ready
cmp r0 2
je m11_context_ready
store8 7800000000000000012 0
label m11_context_ready
# Clear keyed visitation only for nodes actually queued, then their records.
load8 r10 7800000000000000120
set r0 0
label m11_queue
cmp r0 r10
jge m11_proof_start
set r7 7800000000008000000
mov r1 r0
mul r1 8
add r7 r1
mov r15 r7
load8 r2 $r15
add r15 1
load8 r14 $r15
mul r14 256
add r2 r14
set r8 7800000000008100000
add r8 r2
store8 $r8 0
set r1 0
label m11_queue_bytes
cmp r1 8
jge m11_next_node
mov r8 r7
add r8 r1
store8 $r8 0
add r1 1
jmp m11_queue_bytes
label m11_next_node
add r0 1
jmp m11_queue
label m11_proof_start
load8 r10 7800000000000000121
mul r10 4
set r0 0
label m11_proof
cmp r0 r10
jge m11_result_start
set r7 7800000000008200000
add r7 r0
store8 $r7 0
add r0 1
jmp m11_proof
label m11_result_start
load8 r10 7800000000000000082
mul r10 2
set r0 0
label m11_results
cmp r0 r10
jge m11_control_start
set r7 7800000000008300000
add r7 r0
store8 $r7 0
add r0 1
jmp m11_results
label m11_control_start
set r0 63
label m11_control
set r7 7800000000000000000
add r7 r0
store8 $r7 0
add r0 1
cmp r0 512
jlt m11_control
set r0 1024
label m11_tokens
set r7 7800000000000000000
add r7 r0
store8 $r7 0
add r0 1
cmp r0 1084
jlt m11_tokens
set r0 2048
label m11_descriptors
set r7 7800000000000000000
add r7 r0
store8 $r7 0
add r0 1
cmp r0 2108
jlt m11_descriptors
label m11_done
jmp m12_entry
label m11_invalid
div r0 0
label m12_entry
load8 r0 8100000000000000002
cmp r0 1
jne m12_done
set r0 16
label m12_control
set r7 8100000000000000000
add r7 r0
store8 $r7 0
add r0 1
cmp r0 128
jlt m12_control
set r0 512
label m12_target
set r7 8100000000000000000
add r7 r0
store8 $r7 0
add r0 1
cmp r0 768
jlt m12_target
set r0 1000
label m12_original
set r7 8100000000000000000
add r7 r0
store8 $r7 0
add r0 1
cmp r0 1602
jlt m12_original
set r0 2000
label m12_output
set r7 8100000000000000000
add r7 r0
store8 $r7 0
add r0 1
cmp r0 2600
jlt m12_output
label m12_done
jmp finish
label finish
halt
