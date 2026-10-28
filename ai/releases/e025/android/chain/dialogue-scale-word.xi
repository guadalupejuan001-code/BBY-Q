#!reverse-pc-machine-v1
label s0_entry
# Tokenize real text in XI. ASCII case folding, whitespace and final '?' only.
# Intake +16=1, +17=byte length, +128..382=raw bytes. Max 15 words of 16 bytes.
# Tokens +512, stride 18; parse error +40. No semantic answers in this stage.
load8 r0 7300000000000000002
cmp r0 1
jne s0_invalid
load8 r0 7300000000000000016
cmp r0 1
jne s0_invalid
load8 r9 7300000000000000017
cmp r9 0
je s0_bad_text
set r0 0
set r1 0
set r2 0
set r10 0
store8 7300000000000000040 0
label s0_char_loop
cmp r0 r9
jge s0_end_text
set r7 7300000000000000128
add r7 r0
load8 r3 $r7
cmp r3 32
je s0_separator
cmp r3 9
je s0_separator
cmp r10 1
je s0_bad_text
cmp r3 63
je s0_question_mark
cmp r3 195
je s0_conversational_accent
cmp r3 65
jlt s0_check_digit
cmp r3 90
jgt s0_check_alpha
add r3 32
label s0_check_alpha
cmp r3 97
jlt s0_bad_text
cmp r3 122
jgt s0_bad_text
jmp s0_write_char
label s0_check_digit
cmp r3 48
jlt s0_bad_text
cmp r3 57
jgt s0_bad_text
label s0_write_char
cmp r1 15
jge s0_bad_text
cmp r2 16
jge s0_bad_text
set r7 7300000000000000513
mov r8 r1
mul r8 18
add r7 r8
add r7 r2
store8 $r7 r3
add r2 1
jmp s0_next_char
label s0_conversational_accent
# Accent folding is optional on the conversational surface. Old E011 models
# retain their ASCII protocol. Operator meanings still come from learned D.
load8 r7 7700000000000000016
cmp r7 1
jne s0_bad_text
add r0 1
cmp r0 r9
jge s0_bad_text
set r7 7300000000000000128
add r7 r0
load8 r3 $r7
cmp r3 129
je s0_accent_a
cmp r3 137
je s0_accent_e
cmp r3 141
je s0_accent_i
cmp r3 147
je s0_accent_o
cmp r3 154
je s0_accent_u
cmp r3 161
je s0_accent_a
cmp r3 169
je s0_accent_e
cmp r3 173
je s0_accent_i
cmp r3 179
je s0_accent_o
cmp r3 186
je s0_accent_u
jmp s0_bad_text
label s0_accent_a
set r3 97
jmp s0_write_char
label s0_accent_e
set r3 101
jmp s0_write_char
label s0_accent_i
set r3 105
jmp s0_write_char
label s0_accent_o
set r3 111
jmp s0_write_char
label s0_accent_u
set r3 117
jmp s0_write_char
label s0_question_mark
cmp r2 0
jne s0_mark_terminal
cmp r1 0
je s0_bad_text
label s0_mark_terminal
set r10 1
jmp s0_next_char
label s0_separator
cmp r2 0
je s0_next_char
set r7 7300000000000000512
mov r8 r1
mul r8 18
add r7 r8
store8 $r7 r2
add r1 1
set r2 0
label s0_next_char
add r0 1
jmp s0_char_loop
label s0_end_text
cmp r2 0
je s0_finish_tokens
set r7 7300000000000000512
mov r8 r1
mul r8 18
add r7 r8
store8 $r7 r2
add r1 1
label s0_finish_tokens
cmp r1 0
je s0_bad_text
store8 7300000000000000032 r1
jmp s1_entry
label s0_bad_text
store8 7300000000000000040 1
store8 7300000000000000032 0
jmp s1_entry
label s0_invalid
div r0 0
label s1_entry
# Resolve every word through E010's existing bilingual numerals and E011's
# learned operator lexicon. Decimal notation is a designed base-10 grammar,
# anchored to the ten learned digit concepts; it is not a learned number name.
# Resolution +800+i*4: kind 1=number 2=operator 0=unknown; low/high value.
load8 r0 7300000000000000002
cmp r0 1
jne s1_invalid
load8 r0 7300000000000000016
cmp r0 1
jne s1_invalid
load8 r0 7300000000000000040
cmp r0 0
jne s1_done
load8 r15 7300000000000000032
cmp r15 15
jgt s1_invalid
set r0 0
label s1_each_token
cmp r0 r15
jge s1_done
set r1 7300000000000000512
mov r2 r0
mul r2 18
add r1 r2
load8 r2 $r1
set r3 0
set r4 0
# First try a decimal string, requiring a learned grounding for every digit.
label s1_decimal_chars
cmp r3 r2
jge s1_decimal_complete
mov r5 r1
add r5 1
add r5 r3
load8 r6 $r5
cmp r6 48
jlt s1_lexical_number
cmp r6 57
jgt s1_lexical_number
sub r6 48
load8 r7 7200000000000000010
set r8 0
label s1_ground_digit
cmp r8 r7
jge s1_unresolved
set r9 7200000000000001000
mov r10 r8
mul r10 32
add r9 r10
load8 r10 $r9
cmp r10 4
jne s1_next_digit_concept
add r9 1
load8 r10 $r9
cmp r10 r6
jne s1_next_digit_concept
add r9 3
load8 r10 $r9
cmp r10 2
jlt s1_next_digit_concept
mul r4 10
add r4 r6
cmp r4 65535
jgt s1_unresolved
add r3 1
jmp s1_decimal_chars
label s1_next_digit_concept
add r8 1
jmp s1_ground_digit
label s1_decimal_complete
set r12 1
jmp s1_save_resolution
label s1_lexical_number
load8 r7 7200000000000000010
set r8 0
set r11 0
label s1_each_numeral
cmp r8 r7
jge s1_learned_operator
set r9 7200000000000001000
mov r10 r8
mul r10 32
add r9 r10
load8 r10 $r9
cmp r10 4
jne s1_next_numeral
mov r10 r9
add r10 4
load8 r10 $r10
cmp r10 2
jlt s1_next_numeral
set r13 5
label s1_each_language
mov r10 r9
add r10 r13
load8 r10 $r10
cmp r10 r2
jne s1_next_language
set r3 0
label s1_lexical_chars
cmp r3 r2
jge s1_numeral_match
mov r5 r1
add r5 1
add r5 r3
load8 r6 $r5
mov r5 r9
add r5 r13
add r5 1
add r5 r3
load8 r10 $r5
cmp r6 r10
jne s1_next_language
add r3 1
jmp s1_lexical_chars
label s1_numeral_match
mov r5 r9
add r5 1
load8 r6 $r5
cmp r11 0
je s1_first_numeral_match
cmp r4 r6
jne s1_unresolved
jmp s1_next_language
label s1_first_numeral_match
set r11 1
mov r4 r6
label s1_next_language
cmp r13 5
jne s1_next_numeral
set r13 14
jmp s1_each_language
label s1_next_numeral
add r8 1
jmp s1_each_numeral
label s1_learned_operator
cmp r11 1
je s1_resolved_number
load8 r7 7300000000000000004
cmp r7 32
jgt s1_invalid
set r8 0
label s1_each_operator
cmp r8 r7
jge s1_unresolved
set r9 7300000000000001000
mov r10 r8
mul r10 32
add r9 r10
load8 r10 $r9
cmp r10 r2
jne s1_next_operator
mov r5 r9
add r5 18
load8 r10 $r5
cmp r10 2
jlt s1_next_operator
set r3 0
label s1_operator_chars
cmp r3 r2
jge s1_operator_match
mov r5 r1
add r5 1
add r5 r3
load8 r6 $r5
mov r5 r9
add r5 1
add r5 r3
load8 r10 $r5
cmp r6 r10
jne s1_next_operator
add r3 1
jmp s1_operator_chars
label s1_operator_match
add r9 17
load8 r4 $r9
set r12 2
jmp s1_save_resolution
label s1_next_operator
add r8 1
jmp s1_each_operator
label s1_resolved_number
set r12 1
jmp s1_save_resolution
label s1_unresolved
# Optional E020 spellings refer to sealed, independently validated concepts.
# No mapping from a Spanish/English spelling to an arithmetic family here.
load8 r7 7900000000000000003
cmp r7 1
jne s1_no_scale_word
load8 r7 7900000000000000004
cmp r7 128
jgt s1_invalid
set r8 0
label s1_scale_operator
cmp r8 r7
jge s1_no_scale_word
set r9 7900000000000001000
mov r10 r8
mul r10 32
add r9 r10
load8 r10 $r9
cmp r10 r2
jne s1_next_scale_operator
set r3 0
label s1_scale_chars
cmp r3 r2
jge s1_scale_match
mov r5 r1
add r5 1
add r5 r3
load8 r6 $r5
mov r5 r9
add r5 1
add r5 r3
load8 r10 $r5
cmp r6 r10
jne s1_next_scale_operator
add r3 1
jmp s1_scale_chars
label s1_scale_match
add r9 17
load8 r4 $r9
cmp r4 1
jlt s1_invalid
cmp r4 8
jgt s1_invalid
sub r4 1
mul r4 64
set r9 7900000000000000130
add r9 r4
load8 r4 $r9
cmp r4 1
jlt s1_invalid
cmp r4 8
jgt s1_invalid
set r12 2
jmp s1_save_resolution
label s1_next_scale_operator
add r8 1
jmp s1_scale_operator
label s1_no_scale_word
set r12 0
set r4 0
label s1_save_resolution
set r5 7300000000000000800
mov r6 r0
mul r6 4
add r5 r6
store8 $r5 r12
add r5 1
mov r6 r4
mod r6 256
store8 $r5 r6
add r5 1
div r4 256
store8 $r5 r4
add r0 1
jmp s1_each_token
label s1_done
jmp s2_entry
label s1_invalid
div r0 0
label s2_entry
# Bind the middle spelling of NUMBER WORD NUMBER to an opaque concept ID.
# M+24 concept (1..8),+25 language (1..2). Never assign a primitive here.
load8 r0 7900000000000000002
cmp r0 1
jne s2_invalid
load8 r0 7300000000000000040
cmp r0 0
jne s2_invalid
load8 r0 7300000000000000032
cmp r0 3
jne s2_invalid
load8 r0 7300000000000000800
cmp r0 1
jne s2_invalid
load8 r0 7300000000000000808
cmp r0 1
jne s2_invalid
load8 r0 7300000000000000804
cmp r0 0
jne s2_invalid
load8 r10 7900000000000000024
cmp r10 1
jlt s2_invalid
cmp r10 8
jgt s2_invalid
load8 r11 7900000000000000025
cmp r11 1
jlt s2_invalid
cmp r11 2
jgt s2_invalid
load8 r2 7300000000000000530
cmp r2 1
jlt s2_invalid
cmp r2 16
jgt s2_invalid
set r0 0
label s2_validate
cmp r0 r2
jge s2_lookup
set r7 7300000000000000531
add r7 r0
load8 r3 $r7
cmp r3 97
jlt s2_invalid
cmp r3 122
jgt s2_invalid
add r0 1
jmp s2_validate
label s2_lookup
load8 r12 7900000000000000004
set r0 0
label s2_word
cmp r0 r12
jge s2_allocate
set r7 7900000000000001000
mov r3 r0
mul r3 32
add r7 r3
load8 r3 $r7
cmp r3 r2
jne s2_next_word
set r1 0
label s2_compare
cmp r1 r2
jge s2_duplicate
set r8 7300000000000000531
add r8 r1
load8 r3 $r8
mov r8 r7
add r8 1
add r8 r1
load8 r4 $r8
cmp r3 r4
jne s2_next_word
add r1 1
jmp s2_compare
label s2_duplicate
mov r8 r7
add r8 17
load8 r3 $r8
cmp r3 r10
jne s2_invalid
add r8 1
load8 r3 $r8
cmp r3 r11
jne s2_invalid
jmp s2_clean
label s2_next_word
add r0 1
jmp s2_word
label s2_allocate
cmp r12 128
jge s2_invalid
set r7 7900000000000001000
mov r3 r12
mul r3 32
add r7 r3
store8 $r7 r2
set r0 0
label s2_copy
cmp r0 r2
jge s2_copied
set r8 7300000000000000531
add r8 r0
load8 r3 $r8
mov r8 r7
add r8 1
add r8 r0
store8 $r8 r3
add r0 1
jmp s2_copy
label s2_copied
add r7 17
store8 $r7 r10
add r7 1
store8 $r7 r11
add r12 1
store8 7900000000000000004 r12
label s2_clean
store8 7900000000000000024 0
store8 7900000000000000025 0
set r0 16
label s2_clear_intake
set r7 7300000000000000000
add r7 r0
store8 $r7 0
add r0 1
cmp r0 864
jlt s2_clear_intake
halt
label s2_invalid
div r0 0
