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
# From labeled quantity phrases, learn singular, plural and one-word agreement.
# 7700000000000000016=3,+17=noun,+18=1 singular/2 plural/3 indefinite article.
# Existing shared concept IDs must resolve; all text remains in XI.
load8 r0 7700000000000000002
cmp r0 1
jne m2_invalid
load8 r0 7700000000000000016
cmp r0 3
jne m2_invalid
load8 r0 7400000000000000040
cmp r0 0
jne m2_invalid
load8 r0 7400000000000000032
cmp r0 2
jne m2_invalid
load8 r9 7700000000000000017
load8 r10 7700000000000000018
load8 r0 7400000000000001602
cmp r0 r9
jne m2_invalid
load8 r0 7400000000000001603
cmp r0 1
jne m2_invalid
load8 r11 7400000000000000003
cmp r11 1
jlt m2_invalid
cmp r11 2
jgt m2_invalid
set r12 7700000000000100000
mov r0 r9
mul r0 224
add r12 r0
mov r0 r11
sub r0 1
mul r0 112
add r12 r0
load8 r0 7400000000000001600
cmp r10 1
je m2_singular
cmp r10 2
je m2_plural
cmp r10 3
jne m2_invalid
cmp r0 0
je m2_invalid
load8 r0 7400000000000000512
cmp r0 8
jgt m2_invalid
set r13 34
jmp m2_noun
label m2_singular
cmp r0 14
jne m2_invalid
set r13 34
jmp m2_noun
label m2_plural
cmp r0 15
je m2_plural_two
cmp r0 16
jne m2_invalid
set r14 2
jmp m2_plural_ready
label m2_plural_two
set r14 1
label m2_plural_ready
store8 7700000000000000022 r14
set r13 68
label m2_noun
set r8 7400000000000000546
mov r7 r12
add r7 r13
set r15 0
jmp m2_segment
label m2_prefix
cmp r10 2
je m2_plural_mask
set r8 7400000000000000512
mov r7 r12
cmp r10 1
je m2_prefix_ready
add r7 102
label m2_prefix_ready
set r15 1
label m2_segment
load8 r6 $r8
cmp r6 1
jlt m2_invalid
cmp r6 32
jgt m2_invalid
load8 r1 $r7
cmp r1 0
je m2_write_segment
cmp r1 r6
jne m2_invalid
set r0 0
label m2_compare
cmp r0 r6
jge m2_segment_done
mov r1 r7
add r1 1
add r1 r0
load8 r2 $r1
mov r1 r8
add r1 1
add r1 r0
load8 r3 $r1
cmp r2 r3
jne m2_invalid
add r0 1
jmp m2_compare
label m2_write_segment
store8 $r7 r6
set r0 0
label m2_copy
cmp r0 r6
jge m2_segment_done
mov r1 r8
add r1 1
add r1 r0
load8 r2 $r1
mov r1 r7
add r1 1
add r1 r0
store8 $r1 r2
add r0 1
jmp m2_copy
label m2_segment_done
cmp r15 0
je m2_prefix
jmp m2_done
label m2_plural_mask
mov r7 r12
add r7 101
load8 r1 $r7
load8 r2 7700000000000000022
mov r0 r1
div r0 r2
mod r0 2
cmp r0 0
jne m2_done
add r1 r2
store8 $r7 r1
label m2_done
jmp m3_entry
label m2_invalid
div r0 0
label m3_entry
set r0 16
label m3_conversation
set r7 7700000000000000000
add r7 r0
store8 $r7 0
add r0 1
cmp r0 256
jlt m3_conversation
set r0 16
label m3_intake
set r7 7400000000000000000
add r7 r0
store8 $r7 0
add r0 1
cmp r0 2048
jlt m3_intake
jmp finish
label finish
halt
