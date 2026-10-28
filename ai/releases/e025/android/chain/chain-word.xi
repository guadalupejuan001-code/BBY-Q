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
# Functional-word extension with a runtime allocated identity. Replaying the
# curriculum against a live user's vocabulary must never reuse factory IDs.
load8 r0 7800000000000001024
load8 r1 7800000000000001025
add r0 r1
cmp r0 0
jne m3_done
load8 r0 7800000000000000004
store8 7800000000000000160 r0
load8 r0 7800000000000000005
store8 7800000000000000161 r0
store8 7800000000000000162 3
load8 r0 7400000000000000003
store8 7800000000000000163 r0
store8 7800000000000000164 0
store8 8600000000000000032 1
jmp chain_word_ready
label m3_done
store8 8600000000000000032 0
jmp chain_word_ready
label chain_word_ready
load8 r0 8600000000000000032
cmp r0 1
jne chain_word_clean
label m4_entry
# Explicit teacher only: 7800000000000000160 requested u16 ID (0 allocate),+162 kind,
# +163 language,+164 raw token index. Return +166 u16 ID. All failures throw
# so the original native transaction rolls back vocabulary and facts together.
load8 r0 7800000000000000002
cmp r0 1
jne m4_invalid
load8 r0 7400000000000000040
cmp r0 0
jne m4_invalid
load8 r0 7800000000000000164
load8 r1 7400000000000000032
cmp r0 r1
jge m4_invalid
load8 r11 7800000000000000162
cmp r11 1
jlt m4_invalid
cmp r11 3
jgt m4_invalid
load8 r12 7800000000000000163
cmp r12 1
jlt m4_invalid
cmp r12 2
jgt m4_invalid
set r8 7400000000000000512
mov r1 r0
mul r1 34
add r8 r1
load8 r9 $r8
cmp r9 1
jlt m4_invalid
cmp r9 32
jgt m4_invalid
set r7 7800000000000001024
mul r0 4
add r7 r0
mov r15 r7
load8 r2 $r15
add r15 1
load8 r14 $r15
mul r14 256
add r2 r14
add r7 2
load8 r3 $r7
load8 r10 7800000000000000160
load8 r14 7800000000000000161
mul r14 256
add r10 r14
cmp r2 0
je m4_unknown
cmp r3 r11
jne m4_invalid
cmp r10 0
je m4_reuse
cmp r10 r2
jne m4_invalid
label m4_reuse
mov r14 r2
mod r14 256
store8 7800000000000000166 r14
mov r14 r2
div r14 256
store8 7800000000000000167 r14
jmp chain_word_clean
label m4_unknown
load8 r6 7800000000000000006
load8 r14 7800000000000000007
mul r14 256
add r6 r14
cmp r6 8192
jge m4_invalid
cmp r10 0
jne m4_requested
load8 r10 7800000000000000004
load8 r14 7800000000000000005
mul r14 256
add r10 r14
cmp r10 65535
jge m4_invalid
mov r0 r10
add r0 1
mov r14 r0
mod r14 256
store8 7800000000000000004 r14
mov r14 r0
div r14 256
store8 7800000000000000005 r14
jmp m4_new_kind
label m4_requested
cmp r10 255
jgt m4_extended_kind
cmp r10 22
jle m4_old_entity
set r7 7400000000000006000
add r7 r10
load8 r0 $r7
cmp r0 r11
jne m4_invalid
jmp m4_new_entry
label m4_old_entity
cmp r11 1
jne m4_invalid
jmp m4_new_entry
label m4_extended_kind
set r7 7800000000000020000
add r7 r10
load8 r0 $r7
cmp r0 0
je m4_update_next
cmp r0 r11
jne m4_invalid
jmp m4_new_entry
label m4_update_next
load8 r0 7800000000000000004
load8 r14 7800000000000000005
mul r14 256
add r0 r14
cmp r10 r0
jlt m4_new_kind
cmp r10 65535
jge m4_invalid
mov r0 r10
add r0 1
mov r14 r0
mod r14 256
store8 7800000000000000004 r14
mov r14 r0
div r14 256
store8 7800000000000000005 r14
label m4_new_kind
set r7 7800000000000020000
add r7 r10
store8 $r7 r11
label m4_new_entry
set r7 8600000000000400000
mov r0 r6
mul r0 40
add r7 r0
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
add r7 1
store8 $r7 r12
add r7 1
store8 $r7 r9
add r7 1
set r0 0
label m4_copy
cmp r0 r9
jge m4_publish
mov r1 r8
add r1 1
add r1 r0
load8 r2 $r1
mov r1 r7
add r1 r0
store8 $r1 r2
add r0 1
jmp m4_copy
label m4_publish
add r6 1
mov r14 r6
mod r14 256
store8 7800000000000000006 r14
mov r14 r6
div r14 256
store8 7800000000000000007 r14
mov r14 r10
mod r14 256
store8 7800000000000000166 r14
mov r14 r10
div r14 256
store8 7800000000000000167 r14
jmp chain_word_clean
label m4_invalid
div r0 0
label chain_word_clean
store8 8600000000000000032 0
label m5_entry
# E013: clear bounded actual intake and the visited-node queue, preserving the
# same E012 clean-state invariant. Token slots are cleared even after bad input.
load8 r2 7400000000000000017
load8 r3 7400000000000000050
set r0 0
label m5_visited
cmp r0 r3
jge m5_raw_start
set r7 7400000000000003000
add r7 r0
load8 r1 $r7
cmp r1 1
jlt m5_invalid
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
jmp m5_visited
label m5_raw_start
set r0 0
label m5_raw
cmp r0 r2
jge m5_token_start
set r7 7400000000000000128
add r7 r0
store8 $r7 0
add r0 1
jmp m5_raw
label m5_token_start
set r0 0
label m5_tokens
set r7 7400000000000000512
add r7 r0
store8 $r7 0
add r0 1
cmp r0 510
jlt m5_tokens
set r0 0
label m5_resolved
set r7 7400000000000001600
add r7 r0
store8 $r7 0
add r0 1
cmp r0 30
jlt m5_resolved
set r0 16
label m5_control
set r7 7400000000000000000
add r7 r0
store8 $r7 0
add r0 1
cmp r0 64
jlt m5_control
jmp m6_entry
label m5_invalid
div r0 0
label m6_entry
load8 r0 7800000000000000002
cmp r0 0
je m6_done
cmp r0 1
jne m6_invalid
# A delegated query is only a context if the actual legacy search succeeded.
# Do not preserve the speculative slots of an unanswered question.
load8 r0 7800000000000000067
cmp r0 0
jne m6_context_ready
load8 r0 7800000000000000012
cmp r0 1
jne m6_context_ready
load8 r0 7400000000000000008
cmp r0 1
je m6_context_ready
cmp r0 2
je m6_context_ready
store8 7800000000000000012 0
label m6_context_ready
# Clear keyed visitation only for nodes actually queued, then their records.
load8 r10 7800000000000000120
set r0 0
label m6_queue
cmp r0 r10
jge m6_proof_start
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
label m6_queue_bytes
cmp r1 8
jge m6_next_node
mov r8 r7
add r8 r1
store8 $r8 0
add r1 1
jmp m6_queue_bytes
label m6_next_node
add r0 1
jmp m6_queue
label m6_proof_start
load8 r10 7800000000000000121
mul r10 4
set r0 0
label m6_proof
cmp r0 r10
jge m6_result_start
set r7 7800000000008200000
add r7 r0
store8 $r7 0
add r0 1
jmp m6_proof
label m6_result_start
load8 r10 7800000000000000082
mul r10 2
set r0 0
label m6_results
cmp r0 r10
jge m6_control_start
set r7 7800000000008300000
add r7 r0
store8 $r7 0
add r0 1
jmp m6_results
label m6_control_start
set r0 63
label m6_control
set r7 7800000000000000000
add r7 r0
store8 $r7 0
add r0 1
cmp r0 512
jlt m6_control
set r0 1024
label m6_tokens
set r7 7800000000000000000
add r7 r0
store8 $r7 0
add r0 1
cmp r0 1084
jlt m6_tokens
set r0 2048
label m6_descriptors
set r7 7800000000000000000
add r7 r0
store8 $r7 0
add r0 1
cmp r0 2108
jlt m6_descriptors
label m6_done
jmp finish
label m6_invalid
div r0 0
label finish
halt
