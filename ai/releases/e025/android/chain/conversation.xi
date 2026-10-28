#!reverse-pc-machine-v1
load8 r0 8500000000000000002
cmp r0 1
jne social_skip
label m0_entry
# Social-only reader. Never used by the desktop command interpreter. Normalize
# case and punctuation into private tokens; preserve the original input bytes.
# S=8500000000000000000; +16 error, +17 count; +512 tokens, stride 34.
store8 8500000000000000016 0
store8 8500000000000000017 0
store8 8500000000000000018 0
load8 r9 7400000000000000017
cmp r9 1
jlt m0_bad
set r0 0
set r1 0
set r2 0
label m0_character
cmp r0 r9
jge m0_end
set r7 7400000000000000128
add r7 r0
load8 r3 $r7
cmp r3 32
je m0_separator
cmp r3 9
je m0_separator
cmp r3 33
je m0_separator
cmp r3 63
je m0_separator
cmp r3 44
je m0_separator
cmp r3 46
je m0_separator
cmp r3 194
je m0_opening_mark
cmp r3 195
je m0_latin
cmp r3 45
je m0_write
cmp r3 65
jlt m0_digit
cmp r3 90
jgt m0_lowercase
add r3 32
label m0_lowercase
cmp r3 97
jlt m0_bad
cmp r3 122
jgt m0_bad
jmp m0_write
label m0_digit
cmp r3 48
jlt m0_bad
cmp r3 57
jgt m0_bad
label m0_write
cmp r1 15
jge m0_bad
cmp r2 32
jge m0_bad
set r7 8500000000000000513
mov r8 r1
mul r8 34
add r7 r8
add r7 r2
store8 $r7 r3
add r2 1
jmp m0_next
label m0_opening_mark
cmp r2 0
jne m0_bad
add r0 1
cmp r0 r9
jge m0_bad
set r7 7400000000000000128
add r7 r0
load8 r3 $r7
cmp r3 161
je m0_next
cmp r3 191
jne m0_bad
jmp m0_next
label m0_latin
cmp r1 15
jge m0_bad
cmp r2 30
jgt m0_bad
set r7 8500000000000000513
mov r8 r1
mul r8 34
add r7 r8
add r7 r2
store8 $r7 195
add r2 1
add r0 1
cmp r0 r9
jge m0_bad
set r7 7400000000000000128
add r7 r0
load8 r3 $r7
cmp r3 128
jlt m0_bad
cmp r3 191
jgt m0_bad
cmp r3 159
jgt m0_write
cmp r3 151
je m0_bad
add r3 32
jmp m0_write
label m0_separator
cmp r2 0
je m0_next
set r7 8500000000000000512
mov r8 r1
mul r8 34
add r7 r8
store8 $r7 r2
add r1 1
set r2 0
label m0_next
add r0 1
jmp m0_character
label m0_end
cmp r2 0
je m0_count
set r7 8500000000000000512
mov r8 r1
mul r8 34
add r7 r8
store8 $r7 r2
add r1 1
label m0_count
cmp r1 0
je m0_bad
store8 8500000000000000017 r1
jmp m1_entry
label m0_bad
store8 8500000000000000016 1
jmp m1_entry
label m1_entry
# Cover the entire turn with learned fragments. Longest match, at most five
# distinct acts, one main question. No substring trigger and no tool output.
load8 r0 8500000000000000002
cmp r0 1
jne m1_done
load8 r0 8500000000000000016
cmp r0 0
jne m1_done
load8 r15 8500000000000000017
set r12 0
store8 8500000000000000064 0
store8 8500000000000000068 0
store8 8500000000000000065 0
store8 8500000000000000066 0
store8 8500000000000000067 0
label m1_segment
cmp r12 r15
jge m1_covered
set r0 0
set r10 0
set r11 0
label m1_record
load8 r1 8500000000000000003
cmp r0 r1
jge m1_choose
set r7 8600000000000100000
mov r1 r0
mul r1 516
add r7 r1
load8 r13 $r7
mov r1 r12
add r1 r13
cmp r1 r15
jgt m1_next_record
cmp r13 r10
jlt m1_next_record
set r1 0
label m1_word
cmp r1 r13
jge m1_candidate
set r8 8500000000000000512
mov r2 r12
add r2 r1
mul r2 34
add r8 r2
mov r9 r7
add r9 2
mov r2 r1
mul r2 34
add r9 r2
load8 r3 $r8
load8 r4 $r9
cmp r3 r4
jne m1_next_record
set r5 0
label m1_byte
cmp r5 r3
jge m1_word_done
add r8 1
add r9 1
load8 r4 $r8
load8 r6 $r9
cmp r4 r6
jne m1_next_record
add r5 1
jmp m1_byte
label m1_word_done
add r1 1
jmp m1_word
label m1_candidate
mov r10 r13
add r7 1
load8 r11 $r7
label m1_next_record
add r0 1
jmp m1_record
label m1_choose
cmp r10 0
je m1_done
load8 r0 8500000000000000065
cmp r0 8
jge m1_done
set r1 1
mov r2 r11
label m1_bit
sub r2 1
cmp r2 0
je m1_have_bit
mul r1 2
jmp m1_bit
label m1_have_bit
load8 r3 8500000000000000064
load8 r4 8500000000000000068
mul r4 256
add r3 r4
mov r4 r3
div r4 r1
mod r4 2
cmp r4 1
je m1_done
add r3 r1
mov r4 r3
mod r4 256
store8 8500000000000000064 r4
div r3 256
store8 8500000000000000068 r3
set r7 8500000000000000080
add r7 r0
store8 $r7 r11
add r0 1
store8 8500000000000000065 r0
cmp r11 2
je m1_advance
load8 r0 8500000000000000066
add r0 1
store8 8500000000000000066 r0
cmp r11 3
je m1_main
cmp r11 7
je m1_main
cmp r11 8
jne m1_advance
label m1_main
load8 r0 8500000000000000067
add r0 1
cmp r0 1
jgt m1_done
store8 8500000000000000067 r0
label m1_advance
add r12 r10
jmp m1_segment
label m1_covered
load8 r0 8500000000000000066
cmp r0 0
je m1_done
# Do not accept a greeting and a farewell as one social intention.
load8 r0 8500000000000000064
mov r1 r0
mod r1 2
cmp r1 0
je m1_accepted
div r0 16
mod r0 2
cmp r0 1
je m1_done
label m1_accepted
store8 8500000000000000018 1
label m1_done
jmp social_route
label social_route
load8 r0 8500000000000000018
cmp r0 1
jne social_fallback
label m2_entry
# Responses are taught bytes. Only render after full social coverage.
set r12 0
set r13 0
label m2_act
load8 r0 8500000000000000065
cmp r12 r0
jge m2_done
set r7 8500000000000000080
add r7 r12
load8 r0 $r7
cmp r0 2
je m2_next_act
# Avoid repeating the name in a greeting followed by identity.
cmp r0 1
jne m2_response
load8 r1 8500000000000000064
div r1 64
mod r1 2
cmp r1 1
jne m2_response
set r0 10
label m2_response
sub r0 1
mul r0 512
set r7 8500000000000100000
add r7 r0
load8 r0 7400000000000000003
sub r0 1
mul r0 256
add r7 r0
load8 r6 $r7
cmp r6 1
jlt m2_invalid
cmp r13 0
je m2_begin
set r14 32
print r14
label m2_begin
set r3 0
label m2_character
cmp r3 r6
jge m2_emitted
add r7 1
load8 r14 $r7
print r14
add r3 1
jmp m2_character
label m2_emitted
set r13 1
label m2_next_act
add r12 1
jmp m2_act
label m2_done
jmp m3_entry
label m2_invalid
div r0 0
label m3_entry
# Keep only the sealed teaching table. Queries leave no private scratch bytes.
set r0 16
label m3_controls
set r7 8500000000000000000
add r7 r0
store8 $r7 0
add r0 1
cmp r0 128
jlt m3_controls
set r0 512
label m3_tokens
set r7 8500000000000000000
add r7 r0
store8 $r7 0
add r0 1
cmp r0 1024
jlt m3_tokens
jmp m4_entry
label m4_entry
# E013: clear bounded actual intake and the visited-node queue, preserving the
# same E012 clean-state invariant. Token slots are cleared even after bad input.
load8 r2 7400000000000000017
load8 r3 7400000000000000050
set r0 0
label m4_visited
cmp r0 r3
jge m4_raw_start
set r7 7400000000000003000
add r7 r0
load8 r1 $r7
cmp r1 1
jlt m4_invalid
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
jmp m4_visited
label m4_raw_start
set r0 0
label m4_raw
cmp r0 r2
jge m4_token_start
set r7 7400000000000000128
add r7 r0
store8 $r7 0
add r0 1
jmp m4_raw
label m4_token_start
set r0 0
label m4_tokens
set r7 7400000000000000512
add r7 r0
store8 $r7 0
add r0 1
cmp r0 510
jlt m4_tokens
set r0 0
label m4_resolved
set r7 7400000000000001600
add r7 r0
store8 $r7 0
add r0 1
cmp r0 30
jlt m4_resolved
set r0 16
label m4_control
set r7 7400000000000000000
add r7 r0
store8 $r7 0
add r0 1
cmp r0 64
jlt m4_control
jmp finish
label m4_invalid
div r0 0
label social_fallback
label m5_entry
# Keep only the sealed teaching table. Queries leave no private scratch bytes.
set r0 16
label m5_controls
set r7 8500000000000000000
add r7 r0
store8 $r7 0
add r0 1
cmp r0 128
jlt m5_controls
set r0 512
label m5_tokens
set r7 8500000000000000000
add r7 r0
store8 $r7 0
add r0 1
cmp r0 1024
jlt m5_tokens
jmp social_skip
label social_skip
set r0 0
set r1 0
set r2 0
set r3 0
set r4 0
set r5 0
set r6 0
set r7 0
set r8 0
set r9 0
set r10 0
set r11 0
set r12 0
set r13 0
set r14 0
set r15 0
set r13 1
label m6_entry
# Source linker supplies the surface mode in r13 (1 conversation,2 compact).
load8 r0 7800000000000000002
cmp r0 0
je m6_done
cmp r0 1
jne m6_invalid
store8 7800000000000000063 r13
label m6_done
jmp m7_entry
label m6_invalid
div r0 0
label m7_entry
# Optional conversational surface; historical models keep their old protocol.
load8 r0 7700000000000000002
cmp r0 0
je m7_done
cmp r0 1
jne m7_invalid
store8 7700000000000000016 1
label m7_done
jmp m8_entry
label m7_invalid
div r0 0
label m8_entry
# Tokenize real text in XI. A trained E022 reader also allows a single Spanish
# opening question mark at a word boundary after a preamble ("oye, ¿qué...").
# Intake +16=1, +17=byte length, +128..382=raw bytes. Max 15 words of 32 bytes.
# Tokens +512, stride 34; parse error +40. No semantic answers in this stage.
load8 r0 7400000000000000002
cmp r0 1
jne m8_invalid
load8 r0 7400000000000000016
cmp r0 1
jne m8_invalid
load8 r9 7400000000000000017
cmp r9 0
je m8_bad_text
set r0 0
set r1 0
set r2 0
set r10 0
set r11 0
store8 7400000000000000040 0
store8 7400000000000000047 0
label m8_char_loop
cmp r0 r9
jge m8_end_text
set r7 7400000000000000128
add r7 r0
load8 r3 $r7
cmp r3 44
jne m8_ordinary_separator
load8 r7 8100000000000000003
cmp r7 1
je m8_separator
label m8_ordinary_separator
cmp r3 32
je m8_separator
cmp r3 9
je m8_separator
cmp r10 1
je m8_bad_text
cmp r3 46
je m8_period_mark
cmp r3 63
je m8_question_mark
cmp r3 194
je m8_inverted_question
cmp r3 195
je m8_latin_character
cmp r3 95
je m8_write_char
cmp r3 65
jlt m8_check_digit
cmp r3 90
jgt m8_check_alpha
add r3 32
label m8_check_alpha
cmp r3 97
jlt m8_bad_text
cmp r3 122
jgt m8_bad_text
jmp m8_write_char
label m8_check_digit
cmp r3 48
jlt m8_bad_text
cmp r3 57
jgt m8_bad_text
label m8_write_char
cmp r1 15
jge m8_bad_text
cmp r2 32
jge m8_bad_text
set r7 7400000000000000513
mov r8 r1
mul r8 34
add r7 r8
add r7 r2
store8 $r7 r3
add r2 1
jmp m8_next_char
label m8_inverted_question
cmp r11 0
jne m8_bad_text
cmp r1 0
je m8_opening_question
load8 r7 8100000000000000003
cmp r7 1
jne m8_bad_text
label m8_opening_question
cmp r2 0
jne m8_bad_text
add r0 1
cmp r0 r9
jge m8_bad_text
set r7 7400000000000000128
add r7 r0
load8 r3 $r7
cmp r3 191
jne m8_bad_text
set r11 1
store8 7400000000000000047 1
jmp m8_next_char
label m8_latin_character
# Canonical Latin-1 UTF-8: Spanish accents and enye, including uppercase.
cmp r1 15
jge m8_bad_text
cmp r2 30
jgt m8_bad_text
set r7 7400000000000000513
mov r8 r1
mul r8 34
add r7 r8
add r7 r2
store8 $r7 195
add r2 1
add r0 1
cmp r0 r9
jge m8_bad_text
set r7 7400000000000000128
add r7 r0
load8 r3 $r7
cmp r3 128
jlt m8_bad_text
cmp r3 191
jgt m8_bad_text
cmp r3 159
jgt m8_write_char
cmp r3 151
je m8_bad_text
add r3 32
jmp m8_write_char
label m8_period_mark
# A final statement period is enabled only by the conversational XI surface.
load8 r7 7700000000000000016
cmp r7 1
jne m8_bad_text
load8 r7 7700000000000000002
cmp r7 1
jne m8_bad_text
cmp r11 0
jne m8_bad_text
cmp r2 0
jne m8_mark_terminal
cmp r1 0
je m8_bad_text
jmp m8_mark_terminal
label m8_question_mark
store8 7400000000000000047 1
cmp r2 0
jne m8_mark_terminal
cmp r1 0
je m8_bad_text
label m8_mark_terminal
set r10 1
jmp m8_next_char
label m8_separator
cmp r2 0
je m8_next_char
set r7 7400000000000000512
mov r8 r1
mul r8 34
add r7 r8
store8 $r7 r2
add r1 1
set r2 0
label m8_next_char
add r0 1
jmp m8_char_loop
label m8_end_text
cmp r2 0
je m8_finish_tokens
set r7 7400000000000000512
mov r8 r1
mul r8 34
add r7 r8
store8 $r7 r2
add r1 1
label m8_finish_tokens
cmp r1 0
je m8_bad_text
store8 7400000000000000032 r1
jmp m9_entry
label m8_bad_text
store8 7400000000000000040 1
store8 7400000000000000032 0
jmp m9_entry
label m8_invalid
div r0 0
label m9_entry
# Resolve words to SHARED concept IDs. No subject matter or dictionary in code.
# 1..22 use original E010 words directly; only new aliases occupy E012 memory.
# Token +512+i*34; resolved +1600+i*2 = ID, kind (entity/predicate/question).
load8 r0 7400000000000000002
cmp r0 1
jne m9_invalid
load8 r0 7400000000000000016
cmp r0 1
jne m9_invalid
load8 r0 7400000000000000040
cmp r0 0
jne m9_done
load8 r15 7400000000000000032
cmp r15 15
jgt m9_invalid
set r0 0
label m9_token
cmp r0 r15
jge m9_done
set r1 7400000000000000512
mov r2 r0
mul r2 34
add r1 r2
load8 r2 $r1
set r3 0
label m9_old_concept
cmp r3 22
jge m9_new_lexicon
set r4 7200000000000001000
mov r5 r3
mul r5 32
add r4 r5
mov r5 r4
add r5 4
load8 r6 $r5
cmp r6 2
jlt m9_next_old
set r7 5
label m9_old_language
mov r5 r4
add r5 r7
load8 r6 $r5
cmp r6 r2
jne m9_next_old_language
set r8 0
label m9_old_letters
cmp r8 r2
jge m9_old_match
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
jne m9_next_old_language
add r8 1
jmp m9_old_letters
label m9_old_match
mov r12 r3
add r12 1
set r13 1
jmp m9_save
label m9_next_old_language
cmp r7 5
jne m9_next_old
set r7 14
jmp m9_old_language
label m9_next_old
add r3 1
jmp m9_old_concept
label m9_new_lexicon
load8 r10 7400000000000000004
load8 r5 7400000000000000005
mul r5 256
add r10 r5
cmp r10 512
jgt m9_invalid
set r3 0
label m9_new_word
cmp r3 r10
jge m9_unknown
set r4 7400000000000010000
mov r5 r3
mul r5 40
add r4 r5
mov r5 r4
add r5 3
load8 r6 $r5
cmp r6 r2
jne m9_next_word
set r8 0
label m9_new_letters
cmp r8 r2
jge m9_new_match
mov r5 r1
add r5 1
add r5 r8
load8 r6 $r5
mov r5 r4
add r5 4
add r5 r8
load8 r9 $r5
cmp r6 r9
jne m9_next_word
add r8 1
jmp m9_new_letters
label m9_new_match
load8 r12 $r4
add r4 1
load8 r13 $r4
jmp m9_save
label m9_next_word
add r3 1
jmp m9_new_word
label m9_unknown
set r12 0
set r13 0
label m9_save
set r5 7400000000000001600
mov r6 r0
mul r6 2
add r5 r6
store8 $r5 r12
add r5 1
store8 $r5 r13
add r0 1
jmp m9_token
label m9_done
jmp m10_entry
label m9_invalid
div r0 0
label m10_entry
# Read the old lexicon in place, then the append-only u16 extension. Unknown
# questions never allocate. For old IDs, aliases also normalize old K slots.
load8 r0 7800000000000000002
cmp r0 1
jne m10_done
load8 r0 7400000000000000040
cmp r0 0
jne m10_done
load8 r13 7400000000000000032
load8 r12 7800000000000000006
load8 r14 7800000000000000007
mul r14 256
add r12 r14
cmp r12 8192
jgt m10_invalid
set r0 0
label m10_token
cmp r0 r13
jge m10_done
set r7 7400000000000001600
mov r1 r0
mul r1 2
add r7 r1
load8 r10 $r7
add r7 1
load8 r11 $r7
cmp r10 0
jne m10_save
set r1 7400000000000000512
mov r2 r0
mul r2 34
add r1 r2
load8 r2 $r1
set r3 0
label m10_word
cmp r3 r12
jge m10_save
set r4 8600000000000400000
mov r5 r3
mul r5 40
add r4 r5
mov r7 r4
add r7 4
load8 r5 $r7
cmp r5 r2
jne m10_next_word
set r6 0
label m10_letters
cmp r6 r2
jge m10_found
mov r7 r1
add r7 1
add r7 r6
load8 r8 $r7
mov r7 r4
add r7 5
add r7 r6
load8 r9 $r7
cmp r8 r9
jne m10_next_word
add r6 1
jmp m10_letters
label m10_found
mov r15 r4
load8 r10 $r15
add r15 1
load8 r14 $r15
mul r14 256
add r10 r14
mov r7 r4
add r7 2
load8 r11 $r7
jmp m10_save
label m10_next_word
add r3 1
jmp m10_word
label m10_save
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
jgt m10_next_token
set r7 7400000000000001600
mov r1 r0
mul r1 2
add r7 r1
store8 $r7 r10
add r7 1
store8 $r7 r11
label m10_next_token
add r0 1
jmp m10_token
label m10_done
jmp m11_entry
label m10_invalid
div r0 0
label m11_entry
# Learned query-only rewrites. Exact literal/typed-variable patterns and their
# canonical sides live in the state. No spelling or response is encoded here.
load8 r0 8100000000000000003
cmp r0 1
jne m11_inactive
load8 r0 7400000000000000040
cmp r0 0
jne m11_inactive
load8 r12 7400000000000000032
cmp r12 1
jlt m11_inactive
# Any learned global veto leaves the original interpretation untouched.
set r0 0
label m11_veto_token
cmp r0 r12
jge m11_snapshot_start
set r7 7800000000000001024
mov r1 r0
mul r1 4
add r7 r1
load8 r8 $r7
add r7 1
load8 r14 $r7
mul r14 256
add r8 r14
set r1 0
label m11_veto_cue
load8 r2 8000000000000000005
cmp r1 r2
jge m11_next_veto_token
set r7 8000000000000001000
mov r2 r1
mul r2 40
add r7 r2
load8 r2 $r7
cmp r2 2
jne m11_next_veto_cue
add r7 2
load8 r2 $r7
add r7 1
load8 r14 $r7
mul r14 256
add r2 r14
cmp r2 r8
je m11_inactive
label m11_next_veto_cue
add r1 1
jmp m11_veto_cue
label m11_next_veto_token
add r0 1
jmp m11_veto_token
label m11_snapshot_start
store8 8100000000000001600 r12
set r0 0
label m11_snapshot_raw
set r7 7400000000000000512
add r7 r0
load8 r1 $r7
set r7 8100000000000001000
add r7 r0
store8 $r7 r1
add r0 1
cmp r0 510
jlt m11_snapshot_raw
set r0 0
label m11_snapshot_legacy
set r7 7400000000000001600
add r7 r0
load8 r1 $r7
set r7 8100000000000001510
add r7 r0
store8 $r7 r1
add r0 1
cmp r0 30
jlt m11_snapshot_legacy
set r0 0
label m11_snapshot_open
set r7 7800000000000001024
add r7 r0
load8 r1 $r7
set r7 8100000000000001540
add r7 r0
store8 $r7 r1
add r0 1
cmp r0 60
jlt m11_snapshot_open
# A literal learned question cue licenses suffixes even before a whole-rule
# reorder. This reuses the parent's exact spelling table, not a word constant.
set r0 0
label m11_question_token
cmp r0 r12
jge m11_choose
set r8 7400000000000000512
mov r1 r0
mul r1 34
add r8 r1
load8 r10 $r8
set r1 0
label m11_question_cue
load8 r2 8000000000000000005
cmp r1 r2
jge m11_next_question_token
set r7 8000000000000001000
mov r2 r1
mul r2 40
add r7 r2
load8 r2 $r7
cmp r2 1
jne m11_next_question_cue
add r7 1
load8 r2 $r7
cmp r2 r10
jne m11_next_question_cue
add r7 3
set r2 0
label m11_question_letters
cmp r2 r10
jge m11_question_found
mov r3 r7
add r3 r2
load8 r3 $r3
mov r4 r8
add r4 1
add r4 r2
load8 r4 $r4
cmp r3 r4
jne m11_next_question_cue
add r2 1
jmp m11_question_letters
label m11_question_found
store8 8100000000000000027 2
jmp m11_choose
label m11_next_question_cue
add r1 1
jmp m11_question_cue
label m11_next_question_token
add r0 1
jmp m11_question_token
label m11_choose
load8 r12 7400000000000000032
store8 8100000000000000080 0
store8 8100000000000000096 0
store8 8100000000000000104 0
store8 8100000000000000105 0
set r0 0
label m11_rule
load8 r1 8100000000000000004
cmp r0 r1
jge m11_chosen
set r7 8100000000000030000
mov r1 r0
mul r1 8
add r7 r1
load8 r10 $r7
add r7 1
load8 r11 $r7
cmp r10 4
je m11_whole_scope
cmp r10 1
je m11_prefix_scope
load8 r1 8100000000000000027
cmp r1 0
je m11_next_rule
cmp r11 0
je m11_prepare_rule
cmp r1 r11
jne m11_next_rule
jmp m11_prepare_rule
label m11_whole_scope
load8 r1 8100000000000000029
cmp r1 1
je m11_next_rule
jmp m11_prepare_rule
label m11_prefix_scope
load8 r1 8100000000000000028
cmp r1 1
je m11_next_rule
label m11_prepare_rule
set r9 8100000000000010000
mov r1 r0
mul r1 96
add r9 r1
load8 r8 $r9
cmp r8 r12
jgt m11_next_rule
cmp r10 4
jne m11_length_ready
cmp r8 r12
jne m11_next_rule
label m11_length_ready
set r1 0
cmp r10 2
jne m11_position
mov r1 r12
sub r1 r8
label m11_position
store8 8100000000000000090 0
store8 8100000000000000091 0
store8 8100000000000000092 0
set r2 0
set r6 0
label m11_slot
cmp r2 r8
jge m11_matched
mov r7 r9
add r7 16
mov r3 r2
mul r3 4
add r7 r3
load8 r3 $r7
add r7 1
load8 r4 $r7
add r7 1
load8 r14 $r7
mul r14 256
add r4 r14
add r7 1
load8 r5 $r7
mov r7 r1
add r7 r2
mul r7 4
add r7 7800000000000001024
load8 r14 $r7
add r7 1
load8 r15 $r7
mul r15 256
add r14 r15
add r7 1
load8 r15 $r7
cmp r3 16
jne m11_variable
cmp r14 r4
jne m11_next_position
cmp r15 r5
jne m11_next_position
add r6 1
jmp m11_next_slot
label m11_variable
cmp r3 2
je m11_predicate
cmp r3 1
je m11_subject
cmp r3 4
jne m11_fail
set r7 8100000000000000092
jmp m11_entity
label m11_subject
set r7 8100000000000000090
label m11_entity
cmp r14 0
je m11_bind
cmp r15 1
jne m11_next_position
cmp r14 13
jlt m11_bind
cmp r14 22
jle m11_next_position
jmp m11_bind
label m11_predicate
set r7 8100000000000000091
cmp r14 0
je m11_bind
cmp r15 2
jne m11_next_position
label m11_bind
mov r3 r1
add r3 r2
add r3 1
store8 $r7 r3
label m11_next_slot
add r2 1
jmp m11_slot
label m11_matched
# Shared lexical aliases already have the same semantic IDs. Do not keep
# replacing an inner alias with itself; prefix identities may activate scope.
cmp r10 1
je m11_semantic_progress
cmp r10 4
je m11_semantic_progress
set r5 8100000000000020000
mov r4 r0
mul r4 96
add r5 r4
load8 r4 $r5
cmp r4 r8
jne m11_semantic_progress
mul r4 4
mov r7 r9
add r7 16
add r5 16
set r2 0
label m11_identical_span
cmp r2 r4
jge m11_next_rule
mov r14 r7
add r14 r2
load8 r14 $r14
mov r15 r5
add r15 r2
load8 r15 $r15
cmp r14 r15
jne m11_semantic_progress
add r2 1
jmp m11_identical_span
label m11_semantic_progress
# Whole patterns precede prefix heads; then longer literal spans win.
mov r3 r8
set r4 256
cmp r10 4
jne m11_not_whole_score
set r4 768
mov r3 r6
label m11_not_whole_score
cmp r10 1
jne m11_score_ready
set r4 512
label m11_score_ready
add r3 r4
load8 r4 8100000000000000104
load8 r14 8100000000000000105
mul r14 256
add r4 r14
cmp r3 r4
jlt m11_next_position
jgt m11_remember
# Disjoint functional spans compose left to right. Overlapping equally
# specific candidates must agree; otherwise preserve the original request.
load8 r4 8100000000000000081
cmp r1 r4
je m11_same_span
jlt m11_earlier_span
load8 r5 8100000000000000082
add r4 r5
cmp r1 r4
jlt m11_conflict
jmp m11_next_position
label m11_earlier_span
mov r5 r1
add r5 r8
cmp r5 r4
jgt m11_conflict
jmp m11_remember
label m11_same_span
# Ties must bind the same roles and produce the same semantic token sequence.
set r2 0
label m11_compare_bindings
set r7 8100000000000000090
add r7 r2
load8 r4 $r7
add r7 3
load8 r5 $r7
cmp r4 r5
jne m11_conflict
add r2 1
cmp r2 3
jlt m11_compare_bindings
load8 r4 8100000000000000080
sub r4 1
mul r4 96
set r7 8100000000000020000
add r7 r4
set r5 8100000000000020000
mov r4 r0
mul r4 96
add r5 r4
load8 r4 $r7
load8 r14 $r5
cmp r4 r14
jne m11_conflict
mul r4 4
add r7 16
add r5 16
set r2 0
label m11_compare_output
cmp r2 r4
jge m11_next_position
mov r14 r7
add r14 r2
load8 r14 $r14
mov r15 r5
add r15 r2
load8 r15 $r15
cmp r14 r15
jne m11_conflict
add r2 1
jmp m11_compare_output
label m11_conflict
store8 8100000000000000096 1
jmp m11_next_position
label m11_remember
store8 8100000000000000096 0
mov r4 r3
mod r4 256
store8 8100000000000000104 r4
div r3 256
store8 8100000000000000105 r3
mov r4 r0
add r4 1
store8 8100000000000000080 r4
store8 8100000000000000081 r1
store8 8100000000000000082 r8
store8 8100000000000000085 r10
store8 8100000000000000086 r11
set r2 0
label m11_remember_bindings
set r7 8100000000000000090
add r7 r2
load8 r4 $r7
add r7 3
store8 $r7 r4
add r2 1
cmp r2 3
jlt m11_remember_bindings
label m11_next_position
cmp r10 3
jne m11_next_rule
add r1 1
mov r2 r1
add r2 r8
cmp r2 r12
jle m11_position
label m11_next_rule
add r0 1
jmp m11_rule
label m11_chosen
load8 r0 8100000000000000080
cmp r0 0
je m11_done
load8 r0 8100000000000000096
cmp r0 1
je m11_fail
load8 r0 8100000000000000030
cmp r0 8
jge m11_fail
add r0 1
store8 8100000000000000030 r0
store8 8100000000000000024 1
# apply.xi is linked next, and returns to choose after committing one rewrite.
jmp rephrase_apply_check
label m11_fail
store8 8100000000000000026 1
label m11_done
# No winner: skip apply, while leaving the snapshot for accept/cleanup.
store8 8100000000000000080 0
jmp rephrase_apply_check

label m11_inactive
jmp rephrase_apply_check
label rephrase_apply_check
load8 r0 8100000000000000003
cmp r0 1
jne rephrase_match
load8 r0 8100000000000000080
cmp r0 0
je rephrase_match
label m12_entry
# Rebuild token vectors in a disjoint buffer, using source-bound words for
# variable RHS slots and learned canonical spellings for literal RHS slots.
load8 r0 8100000000000000080
cmp r0 0
je m12_done
sub r0 1
set r12 8100000000000020000
mov r1 r0
mul r1 96
add r12 r1
load8 r11 $r12
set r13 8100000000000040000
mul r0 512
add r13 r0
load8 r10 7400000000000000032
load8 r9 8100000000000000081
load8 r8 8100000000000000082
mov r0 r10
sub r0 r8
add r0 r11
cmp r0 1
jlt m12_fail
cmp r0 15
jgt m12_fail
store8 8100000000000000084 r0
set r0 0
label m12_output_token
load8 r1 8100000000000000084
cmp r0 r1
jge m12_commit
cmp r0 r9
jlt m12_original_before
mov r1 r9
add r1 r11
cmp r0 r1
jge m12_original_after
mov r1 r0
sub r1 r9
mov r7 r12
add r7 16
mov r2 r1
mul r2 4
add r7 r2
load8 r2 $r7
cmp r2 16
je m12_canonical
cmp r2 1
je m12_source_subject
cmp r2 2
je m12_source_predicate
cmp r2 4
jne m12_fail
load8 r1 8100000000000000095
jmp m12_bound_source
label m12_source_subject
load8 r1 8100000000000000093
jmp m12_bound_source
label m12_source_predicate
load8 r1 8100000000000000094
label m12_bound_source
cmp r1 0
je m12_fail
sub r1 1
jmp m12_original
label m12_original_before
mov r1 r0
jmp m12_original
label m12_original_after
mov r1 r0
sub r1 r11
add r1 r8
label m12_original
set r5 7400000000000000512
mov r2 r1
mul r2 34
add r5 r2
set r6 7800000000000001024
mul r1 4
add r6 r1
jmp m12_copy_token
label m12_canonical
mov r5 r13
mov r2 r1
mul r2 34
add r5 r2
mov r6 r7
# r7 points at the learned RHS mask; following bytes contain CID and kind.
add r6 1
label m12_copy_token
set r2 0
label m12_copy_raw
mov r7 r5
add r7 r2
load8 r3 $r7
set r7 8100000000000002000
mov r4 r0
mul r4 34
add r7 r4
add r7 r2
store8 $r7 r3
add r2 1
cmp r2 34
jlt m12_copy_raw
# Canonical descriptors and live resolutions use the same CID:u16,kind byte.
load8 r3 $r6
add r6 1
load8 r14 $r6
add r6 1
load8 r4 $r6
set r7 8100000000000002540
mov r1 r0
mul r1 4
add r7 r1
store8 $r7 r3
add r7 1
store8 $r7 r14
add r7 1
store8 $r7 r4
set r7 8100000000000002510
mov r1 r0
mul r1 2
add r7 r1
cmp r14 0
je m12_narrow
store8 $r7 0
add r7 1
store8 $r7 0
jmp m12_next_output
label m12_narrow
store8 $r7 r3
add r7 1
store8 $r7 r4
label m12_next_output
add r0 1
jmp m12_output_token
label m12_commit
load8 r0 8100000000000000084
store8 7400000000000000032 r0
set r1 0
label m12_commit_raw
set r7 8100000000000002000
add r7 r1
load8 r2 $r7
set r7 7400000000000000512
add r7 r1
store8 $r7 r2
# Clear after copying so shorter subsequent outputs cannot inherit a token.
set r7 8100000000000002000
add r7 r1
store8 $r7 0
add r1 1
cmp r1 510
jlt m12_commit_raw
set r1 0
label m12_commit_legacy
set r7 8100000000000002510
add r7 r1
load8 r2 $r7
set r7 7400000000000001600
add r7 r1
store8 $r7 r2
set r7 8100000000000002510
add r7 r1
store8 $r7 0
add r1 1
cmp r1 30
jlt m12_commit_legacy
set r1 0
label m12_commit_open
set r7 8100000000000002540
add r7 r1
load8 r2 $r7
set r7 7800000000000001024
add r7 r1
store8 $r7 r2
set r7 8100000000000002540
add r7 r1
store8 $r7 0
add r1 1
cmp r1 60
jlt m12_commit_open
load8 r0 8100000000000000085
cmp r0 4
jne m12_prefix
store8 8100000000000000029 1
store8 8100000000000000028 1
jmp m12_set_scope
label m12_prefix
cmp r0 1
jne m12_done
store8 8100000000000000028 1
label m12_set_scope
load8 r0 8100000000000000086
store8 8100000000000000027 r0
label m12_done
jmp rephrase_loop
label m12_fail
store8 8100000000000000026 1
store8 8100000000000000080 0
jmp rephrase_loop
label rephrase_loop
load8 r0 8100000000000000026
cmp r0 1
je rephrase_match
jmp m11_choose
label rephrase_match
label m13_entry
# Compare every enabled learned construction. More literal constraints beat
# a generic frame; equally specific competing semantic assignments abstain.
# Unknown variables are interpreted only after an explicit intent is
# recognized; matching itself never allocates a concept or teaches an answer.
load8 r0 7800000000000000063
cmp r0 0
je m13_done
load8 r0 7400000000000000040
cmp r0 0
jne m13_done
load8 r13 7400000000000000032
load8 r0 7800000000000000010
store8 7800000000000000187 r0
store8 7800000000000000188 0
set r0 0
label m13_pattern
load8 r1 7800000000000000187
cmp r0 r1
jge m13_bank_complete
set r1 7800000000000010000
load8 r2 7800000000000000190
cmp r2 0
je m13_record_bank_ready
set r1 8000000000000010000
label m13_record_bank_ready
mov r2 r0
mul r2 96
add r1 r2
load8 r2 $r1
cmp r2 r13
jne m13_next_pattern
mov r7 r1
add r7 2
load8 r2 $r7
cmp r2 1
jne m13_next_pattern
mov r7 r1
add r7 1
load8 r8 $r7
set r9 0
set r10 0
set r11 0
set r12 0
store8 7800000000000000189 0
set r2 0
label m13_token
cmp r2 r13
jge m13_matched
mov r3 r1
add r3 16
mov r4 r2
mul r4 4
add r3 r4
load8 r4 $r3
set r5 7800000000000001024
mov r6 r2
mul r6 4
add r5 r6
mov r15 r5
load8 r6 $r15
add r15 1
load8 r14 $r15
mul r14 256
add r6 r14
add r5 2
load8 r7 $r5
cmp r4 16
je m13_literal
cmp r4 8
je m13_alias
# An unresolved decimal is a quantity, not an unknown entity or predicate.
# Leave it to the original arithmetic/story interpreters instead of allowing
# the generic S/P/O and P/S/O constructions to compete over three unknowns.
cmp r6 0
jne m13_typed_variable
set r3 7400000000000000512
mov r14 r2
mul r14 34
add r3 r14
load8 r5 $r3
set r14 0
label m13_decimal_character
cmp r14 r5
jge m13_next_pattern
mov r15 r3
add r15 1
add r15 r14
load8 r15 $r15
cmp r15 48
jlt m13_typed_variable
cmp r15 57
jgt m13_typed_variable
add r14 1
jmp m13_decimal_character
label m13_typed_variable
cmp r4 2
je m13_predicate
cmp r6 0
je m13_entity_ready
cmp r7 1
je m13_entity_kind
cmp r8 6
jne m13_next_pattern
cmp r7 3
jgt m13_next_pattern
label m13_entity_kind
cmp r6 13
jlt m13_entity_ready
cmp r6 22
jle m13_next_pattern
label m13_entity_ready
cmp r4 1
je m13_subject
cmp r4 4
jne m13_invalid
mov r11 r2
add r11 1
jmp m13_next_token
label m13_subject
mov r9 r2
add r9 1
jmp m13_next_token
label m13_predicate
cmp r6 0
je m13_predicate_ready
cmp r7 2
jne m13_next_pattern
label m13_predicate_ready
mov r10 r2
add r10 1
jmp m13_next_token
label m13_alias
mov r12 r2
add r12 1
jmp m13_next_token
label m13_literal
add r3 1
mov r15 r3
load8 r5 $r15
add r15 1
load8 r14 $r15
mul r14 256
add r5 r14
cmp r5 r6
jne m13_next_pattern
add r3 2
load8 r5 $r3
cmp r5 r7
jne m13_next_pattern
load8 r5 7800000000000000189
add r5 1
store8 7800000000000000189 r5
label m13_next_token
add r2 1
jmp m13_token
label m13_matched
load8 r3 7800000000000000189
load8 r4 7800000000000000188
cmp r3 r4
jgt m13_first
jlt m13_next_pattern
load8 r3 7800000000000000064
cmp r3 0
je m13_first
cmp r3 r8
jne m13_ambiguous
load8 r3 7800000000000000068
cmp r3 r9
jne m13_ambiguous
load8 r3 7800000000000000069
cmp r3 r10
jne m13_ambiguous
load8 r3 7800000000000000070
cmp r3 r11
jne m13_ambiguous
load8 r3 7800000000000000071
cmp r3 r12
jne m13_ambiguous
mov r3 r1
add r3 76
load8 r3 $r3
load8 r4 7800000000000000079
cmp r3 r4
jne m13_ambiguous
jmp m13_next_pattern
label m13_first
mov r3 r1
add r3 76
load8 r3 $r3
store8 7800000000000000079 r3
load8 r3 7800000000000000189
store8 7800000000000000188 r3
store8 7800000000000000065 0
store8 7800000000000000064 r8
store8 7800000000000000068 r9
store8 7800000000000000069 r10
store8 7800000000000000070 r11
store8 7800000000000000071 r12
jmp m13_next_pattern
label m13_ambiguous
store8 7800000000000000065 1
label m13_next_pattern
add r0 1
jmp m13_pattern
label m13_bank_complete
load8 r2 7800000000000000190
cmp r2 1
je m13_done
load8 r2 8000000000000000003
cmp r2 1
jne m13_done
store8 7800000000000000190 1
load8 r2 8000000000000000004
store8 7800000000000000187 r2
set r0 0
jmp m13_pattern
label m13_done
jmp m14_entry
label m13_invalid
div r0 0
label m14_entry
# Designed compositional generalization, enabled only by the trained model.
# An exact learned construction always wins. A learned literal question cue
# can license an unfamiliar preamble, followed by a completely known clause
# with exactly one entity and one predicate. Its complete tail must agree with
# the tail of an enabled learned property construction. No discarded function
# words or unknown content in that clause,
# no multiple roles, no negation/teaching/retraction/alias veto concepts.
# This parser can only ask; it has no fact/word mutation route.
load8 r0 8000000000000000003
cmp r0 1
jne m14_done
load8 r0 7800000000000000064
cmp r0 0
jne m14_done
load8 r0 7400000000000000040
cmp r0 0
jne m14_done
load8 r12 7400000000000000032
load8 r11 8000000000000000005
cmp r11 16
jgt m14_done
set r0 0
label m14_token
cmp r0 r12
jge m14_cue_ready
set r8 7400000000000000512
mov r1 r0
mul r1 34
add r8 r1
load8 r10 $r8
set r7 7800000000000001024
mov r1 r0
mul r1 4
add r7 r1
load8 r9 $r7
add r7 1
load8 r14 $r7
mul r14 256
add r9 r14
set r1 0
label m14_cue
cmp r1 r11
jge m14_next_token
set r7 8000000000000001000
mov r2 r1
mul r2 40
add r7 r2
load8 r2 $r7
cmp r2 1
je m14_spelling
cmp r2 3
je m14_next_cue
add r7 2
load8 r2 $r7
add r7 1
load8 r14 $r7
mul r14 256
add r2 r14
cmp r2 r9
je m14_done
jmp m14_next_cue
label m14_spelling
add r7 1
load8 r2 $r7
cmp r2 r10
jne m14_next_cue
add r7 3
set r2 0
label m14_letters
cmp r2 r10
jge m14_found_cue
mov r3 r7
add r3 r2
load8 r3 $r3
mov r4 r8
add r4 1
add r4 r2
load8 r4 $r4
cmp r3 r4
jne m14_next_cue
add r2 1
jmp m14_letters
label m14_found_cue
load8 r2 8000000000000000026
cmp r2 0
jne m14_done
mov r2 r0
add r2 1
store8 8000000000000000026 r2
label m14_next_cue
add r1 1
jmp m14_cue
label m14_next_token
add r0 1
jmp m14_token
label m14_cue_ready
load8 r10 8000000000000000026
cmp r10 0
je m14_done
# A conditional veto immediately before the question cue marks a different
# question (e.g. purpose/why). Earlier occurrences in a preamble are harmless.
mov r0 r10
sub r0 2
cmp r0 0
jlt m14_no_previous
mul r0 4
set r7 7800000000000001024
add r7 r0
load8 r8 $r7
add r7 1
load8 r14 $r7
mul r14 256
add r8 r14
set r1 0
label m14_preceding_veto
cmp r1 r11
jge m14_no_previous
set r7 8000000000000001000
mov r0 r1
mul r0 40
add r7 r0
load8 r0 $r7
cmp r0 3
jne m14_next_preceding
add r7 2
load8 r0 $r7
add r7 1
load8 r14 $r7
mul r14 256
add r0 r14
cmp r0 r8
je m14_done
label m14_next_preceding
add r1 1
jmp m14_preceding_veto
label m14_no_previous
set r0 0
label m14_role
cmp r0 r12
jge m14_roles_ready
set r7 7800000000000001024
mov r1 r0
mul r1 4
add r7 r1
load8 r8 $r7
add r7 1
load8 r14 $r7
mul r14 256
add r8 r14
add r7 1
load8 r9 $r7
mov r1 r0
add r1 1
cmp r1 r10
je m14_next_role
jlt m14_preamble
cmp r8 0
je m14_done
cmp r9 3
je m14_next_role
cmp r9 1
je m14_subject
cmp r9 2
jne m14_done
load8 r2 7800000000000000069
cmp r2 0
jne m14_done
store8 7800000000000000069 r1
jmp m14_next_role
label m14_subject
cmp r8 13
jlt m14_valid_subject
cmp r8 22
jle m14_done
label m14_valid_subject
load8 r2 7800000000000000068
cmp r2 0
jne m14_done
store8 7800000000000000068 r1
jmp m14_next_role
label m14_preamble
# Recognized content before the question cue would leave its scope unclear.
cmp r9 2
je m14_done
cmp r9 1
jne m14_next_role
# Numeric question numbering is allowed only before the cue, never as S.
cmp r8 13
jlt m14_done
cmp r8 22
jgt m14_done
label m14_next_role
add r0 1
jmp m14_role
label m14_roles_ready
load8 r0 7800000000000000068
cmp r0 0
je m14_done
load8 r0 7800000000000000069
cmp r0 0
je m14_done
# Count every token after the learned question cue. Match an equally long
# suffix of a taught property frame, including each literal and S/P position.
# This reuses learned syntax instead of treating all function words as filler.
mov r5 r12
sub r5 r10
add r5 1
set r0 0
set r1 0
label m14_tail_pattern
load8 r7 7800000000000000010
cmp r1 0
je m14_tail_count_ready
load8 r7 8000000000000000004
label m14_tail_count_ready
cmp r0 r7
jge m14_tail_bank_complete
set r2 7800000000000010000
cmp r1 0
je m14_tail_bank_ready
set r2 8000000000000010000
label m14_tail_bank_ready
mov r7 r0
mul r7 96
add r2 r7
mov r7 r2
add r7 1
load8 r8 $r7
cmp r8 1
jne m14_next_tail_pattern
add r7 1
load8 r8 $r7
cmp r8 1
jne m14_next_tail_pattern
load8 r3 $r2
mov r4 r3
sub r4 r5
cmp r4 0
jlt m14_next_tail_pattern
set r6 0
label m14_tail_token
cmp r6 r5
jge m14_tail_matched
mov r9 r10
sub r9 1
add r9 r6
mov r13 r4
add r13 r6
mul r13 4
add r13 r2
add r13 16
load8 r8 $r13
cmp r8 16
je m14_tail_literal
cmp r8 1
je m14_tail_subject
cmp r8 2
jne m14_next_tail_pattern
load8 r8 7800000000000000069
jmp m14_tail_role
label m14_tail_subject
load8 r8 7800000000000000068
label m14_tail_role
mov r7 r9
add r7 1
cmp r7 r8
jne m14_next_tail_pattern
jmp m14_next_tail_token
label m14_tail_literal
set r7 7800000000000001024
mul r9 4
add r7 r9
add r13 1
load8 r8 $r13
load8 r14 $r7
cmp r8 r14
jne m14_next_tail_pattern
add r13 1
add r7 1
load8 r8 $r13
load8 r14 $r7
cmp r8 r14
jne m14_next_tail_pattern
add r13 1
add r7 1
load8 r8 $r13
load8 r14 $r7
cmp r8 r14
jne m14_next_tail_pattern
label m14_next_tail_token
add r6 1
jmp m14_tail_token
label m14_next_tail_pattern
add r0 1
jmp m14_tail_pattern
label m14_tail_bank_complete
cmp r1 1
je m14_done
set r1 1
set r0 0
jmp m14_tail_pattern
label m14_tail_matched
store8 7800000000000000064 1
label m14_done
jmp m15_entry
label m15_entry
# A rewrite is accepted only for a unique read-only query interpretation.
# Otherwise restore every original token vector, reset the matcher and retry
# the original route. No transformed input can teach, retract, alias or act.
load8 r0 8100000000000000003
cmp r0 1
jne m15_done
load8 r0 8100000000000000026
cmp r0 1
je m15_restore
load8 r0 8100000000000000024
cmp r0 1
jne m15_done
load8 r0 7800000000000000065
cmp r0 0
jne m15_restore
load8 r0 7800000000000000064
cmp r0 1
je m15_done
cmp r0 2
je m15_done
cmp r0 5
je m15_done
cmp r0 8
je m15_done
cmp r0 9
jlt m15_restore
cmp r0 12
jle m15_done
label m15_restore
load8 r0 8100000000000001600
store8 7400000000000000032 r0
set r0 0
label m15_raw
set r7 8100000000000001000
add r7 r0
load8 r1 $r7
set r7 7400000000000000512
add r7 r0
store8 $r7 r1
add r0 1
cmp r0 510
jlt m15_raw
set r0 0
label m15_legacy
set r7 8100000000000001510
add r7 r0
load8 r1 $r7
set r7 7400000000000001600
add r7 r0
store8 $r7 r1
add r0 1
cmp r0 30
jlt m15_legacy
set r0 0
label m15_open
set r7 8100000000000001540
add r7 r0
load8 r1 $r7
set r7 7800000000000001024
add r7 r0
store8 $r7 r1
add r0 1
cmp r0 60
jlt m15_open
set r0 64
label m15_selection
set r7 7800000000000000000
add r7 r0
store8 $r7 0
add r0 1
cmp r0 80
jlt m15_selection
set r0 187
label m15_matching
set r7 7800000000000000000
add r7 r0
store8 $r7 0
add r0 1
cmp r0 191
jlt m15_matching
store8 8100000000000000024 0
store8 8100000000000000026 0
store8 8100000000000000025 1
label m15_done
jmp rephrase_accepted
label rephrase_accepted
load8 r0 8100000000000000025
cmp r0 1
jne rephrase_prepared
store8 8100000000000000025 0
jmp rephrase_match
label rephrase_prepared
label m16_entry
# +67 route: 0 original E016;1 intern statement;2 query;3 alias;4 retract;5 act.
load8 r0 7800000000000000063
cmp r0 0
je m16_done
load8 r0 7800000000000000065
cmp r0 1
je m16_ambiguous
load8 r0 7800000000000000064
cmp r0 5
je m16_explain
cmp r0 9
jge m16_contextual_roles
store8 7800000000000000012 0
cmp r0 0
je m16_done
label m16_contextual_roles
# Resolve semantic labels from selected token positions, not host text parsing.
set r1 0
label m16_role
cmp r1 3
jge m16_dispatch
set r7 7800000000000000068
add r7 r1
load8 r2 $r7
set r3 0
cmp r2 0
je m16_role_ready
sub r2 1
mul r2 4
set r7 7800000000000001024
add r7 r2
mov r15 r7
load8 r3 $r15
add r15 1
load8 r14 $r15
mul r14 256
add r3 r14
label m16_role_ready
set r7 7800000000000000072
mov r2 r1
mul r2 2
add r7 r2
mov r15 r7
mov r14 r3
mod r14 256
store8 $r15 r14
add r15 1
mov r14 r3
div r14 256
store8 $r15 r14
add r1 1
jmp m16_role
label m16_dispatch
load8 r0 7800000000000000064
cmp r0 13
je m16_social
cmp r0 14
je m16_resume_named
cmp r0 15
je m16_resume_previous
load8 r0 7800000000000000064
cmp r0 9
jge m16_contextual
cmp r0 8
je m16_definition
cmp r0 1
je m16_property
cmp r0 2
je m16_query
load8 r1 7400000000000000047
cmp r1 0
jne m16_unsupported
cmp r0 3
je m16_teach
cmp r0 4
je m16_teach
cmp r0 6
je m16_alias
cmp r0 7
je m16_retract
jmp m16_unsupported
label m16_social
store8 7800000000000000080 13
store8 7800000000000000067 5
jmp open_dispatch
label m16_resume_named
store8 8000000000000000025 1
jmp m16_resume_ready
label m16_resume_previous
store8 8000000000000000025 2
label m16_resume_ready
store8 7800000000000000067 6
jmp open_dispatch
label m16_definition
load8 r0 7800000000000000032
load8 r14 7800000000000000033
mul r14 256
add r0 r14
mov r14 r0
mod r14 256
store8 7800000000000000074 r14
mov r14 r0
div r14 256
store8 7800000000000000075 r14
jmp m16_property
label m16_property
store8 7800000000000000090 1
jmp m16_query_ready
label m16_query
store8 7800000000000000090 2
label m16_query_ready
store8 7800000000000000067 2
jmp open_dispatch
label m16_contextual
# Only a supported preceding factual query supplies this unique referent.
# 9: same S/new P, 10: same S/new P/O, 11: new S/same P,
# 12: definition of same S. No contextual construction can teach a fact.
cmp r0 11
jne m16_factual_context
load8 r1 7700000000000000010
cmp r1 1
jne m16_factual_context
# The preexisting account domain owns "and Luis/pears" in an account topic.
store8 7800000000000000012 0
jmp open_dispatch
label m16_factual_context
load8 r1 7800000000000000012
cmp r1 1
je m16_context_resolved
# Legacy factual answers also have a unique supported S/P descriptor.
load8 r1 7700000000000000010
cmp r1 2
jne m16_context_missing
load8 r1 7700000000000000007
cmp r1 1
jne m16_context_missing
load8 r1 7700000000000000008
store8 7800000000000000014 r1
store8 7800000000000000015 0
load8 r1 7700000000000000009
store8 7800000000000000016 r1
store8 7800000000000000017 0
label m16_context_resolved
store8 7800000000000000012 0
cmp r0 11
je m16_context_subject
load8 r1 7800000000000000014
store8 7800000000000000072 r1
load8 r1 7800000000000000015
store8 7800000000000000073 r1
cmp r0 12
je m16_definition
cmp r0 9
je m16_property
cmp r0 10
je m16_query
jmp m16_unsupported
label m16_context_subject
load8 r1 7800000000000000016
store8 7800000000000000074 r1
load8 r1 7800000000000000017
store8 7800000000000000075 r1
jmp m16_property
label m16_context_missing
store8 7800000000000000080 12
jmp m16_act
label m16_teach
# Conservative preflight prevents partially learned names at a full graph.
load8 r0 7800000000000000008
load8 r14 7800000000000000009
mul r14 256
add r0 r14
cmp r0 4096
jge m16_limit
load8 r0 7800000000000000006
load8 r14 7800000000000000007
mul r14 256
add r0 r14
cmp r0 2045
jgt m16_limit
load8 r0 7800000000000000004
load8 r14 7800000000000000005
mul r14 256
add r0 r14
cmp r0 65532
jgt m16_limit
store8 7800000000000000067 1
jmp open_dispatch
label m16_alias
load8 r0 7800000000000000072
load8 r14 7800000000000000073
mul r14 256
add r0 r14
cmp r0 0
je m16_unsupported
store8 7800000000000000067 3
jmp open_dispatch
label m16_retract
load8 r0 7800000000000000072
load8 r14 7800000000000000073
mul r14 256
add r0 r14
load8 r1 7800000000000000074
load8 r14 7800000000000000075
mul r14 256
add r1 r14
mul r0 r1
load8 r1 7800000000000000076
load8 r14 7800000000000000077
mul r14 256
add r1 r14
mul r0 r1
cmp r0 0
je m16_unsupported
store8 7800000000000000067 4
jmp open_dispatch
label m16_explain
store8 7800000000000000085 1
load8 r0 7800000000000000068
cmp r0 0
jne m16_explicit_explanation
load8 r0 7800000000000000012
cmp r0 1
jne m16_clarify
load8 r0 7800000000000000013
store8 7800000000000000090 r0
load8 r0 7800000000000000014
load8 r14 7800000000000000015
mul r14 256
add r0 r14
mov r14 r0
mod r14 256
store8 7800000000000000072 r14
mov r14 r0
div r14 256
store8 7800000000000000073 r14
load8 r0 7800000000000000016
load8 r14 7800000000000000017
mul r14 256
add r0 r14
mov r14 r0
mod r14 256
store8 7800000000000000074 r14
mov r14 r0
div r14 256
store8 7800000000000000075 r14
load8 r0 7800000000000000018
load8 r14 7800000000000000019
mul r14 256
add r0 r14
mov r14 r0
mod r14 256
store8 7800000000000000076 r14
mov r14 r0
div r14 256
store8 7800000000000000077 r14
store8 7800000000000000067 2
jmp open_dispatch
label m16_explicit_explanation
store8 7800000000000000012 0
set r1 0
label m16_explanation_role
cmp r1 3
jge m16_explicit_ready
set r7 7800000000000000068
add r7 r1
load8 r2 $r7
sub r2 1
mul r2 4
set r7 7800000000000001024
add r7 r2
mov r15 r7
load8 r3 $r15
add r15 1
load8 r14 $r15
mul r14 256
add r3 r14
set r7 7800000000000000072
mov r2 r1
mul r2 2
add r7 r2
mov r15 r7
mov r14 r3
mod r14 256
store8 $r15 r14
add r15 1
mov r14 r3
div r14 256
store8 $r15 r14
add r1 1
jmp m16_explanation_role
label m16_explicit_ready
store8 7800000000000000090 2
store8 7800000000000000067 2
jmp open_dispatch
label m16_unsupported
store8 7800000000000000080 3
jmp m16_act
label m16_clarify
store8 7800000000000000080 8
jmp m16_act
label m16_ambiguous
store8 7800000000000000012 0
store8 7800000000000000080 10
jmp m16_act
label m16_limit
store8 7800000000000000080 9
label m16_act
store8 7800000000000000067 5
label m16_done
jmp open_dispatch
label open_dispatch
load8 r0 7800000000000000067
cmp r0 1
je open_teach_check
cmp r0 2
je open_query
cmp r0 3
je open_alias
cmp r0 4
je open_mutate
cmp r0 6
je lingua_resume
cmp r0 5
je open_reply
label open_fallback
label m17_entry
# Designed conversational grammar over supervised functional concepts.
# Normalize only resolved semantic slots. E014 still owns all account changes.
load8 r0 7700000000000000016
cmp r0 1
jne m17_done
load8 r0 7400000000000000040
cmp r0 0
jne m17_unsupported
load8 r15 7400000000000000032
# Pronouns name the last explicit count referent, never a guessed new entity.
set r0 0
set r10 0
set r12 0
label m17_pronoun_scan
cmp r0 r15
jge m17_pronouns_ready
set r7 7400000000000001600
mov r1 r0
mul r1 2
add r7 r1
load8 r2 $r7
load8 r3 7700000000000000519
cmp r2 r3
je m17_feminine
load8 r3 7700000000000000520
cmp r2 r3
je m17_masculine
set r7 7700000000000010000
mul r2 4
add r7 r2
load8 r3 $r7
cmp r3 1
jne m17_scan_next
add r12 1
jmp m17_scan_next
label m17_feminine
set r11 2
jmp m17_pronoun
label m17_masculine
set r11 1
label m17_pronoun
cmp r10 0
jne m17_clarify
mov r10 r0
add r10 1
label m17_scan_next
add r0 1
jmp m17_pronoun_scan
label m17_pronouns_ready
cmp r10 0
je m17_intents
cmp r12 0
jne m17_clarify
load8 r0 7700000000000000010
cmp r0 1
jne m17_clarify
load8 r0 7700000000000000004
cmp r0 1
jne m17_clarify
load8 r2 7700000000000000005
set r7 7700000000000010001
mov r0 r2
mul r0 4
add r7 r0
load8 r0 $r7
cmp r0 r11
jne m17_clarify
sub r10 1
mul r10 2
set r7 7400000000000001600
add r7 r10
store8 $r7 r2
add r7 1
store8 $r7 1
label m17_intents
load8 r8 7400000000000001600
load8 r9 7400000000000001602
load8 r10 7400000000000001604
load8 r11 7400000000000001606
load8 r12 7400000000000001608
load8 r0 7700000000000000537
cmp r8 r0
jne m17_usual_intents
cmp r15 2
jne m17_usual_intents
load8 r0 7700000000000000538
cmp r9 r0
je m17_status
label m17_usual_intents
load8 r0 7700000000000000513
cmp r8 r0
je m17_greeting
load8 r0 7700000000000000515
cmp r8 r0
je m17_who
load8 r0 7700000000000000530
cmp r8 r0
je m17_what
load8 r0 7700000000000000523
cmp r8 r0
je m17_tell
load8 r0 7700000000000000531
cmp r8 r0
je m17_followup
load8 r0 7700000000000000535
cmp r8 r0
je m17_count_short
load8 r0 7700000000000000532
cmp r8 r0
je m17_english_count_short
jmp m17_action_short
label m17_greeting
cmp r15 1
je m17_greet
cmp r15 2
jne m17_done
load8 r0 7700000000000000526
cmp r9 r0
jne m17_done
label m17_greet
store8 7700000000000000017 1
jmp conversation_intake
label m17_who
load8 r0 7700000000000000528
cmp r9 r0
jne m17_done
cmp r15 2
je m17_identity
cmp r15 3
jne m17_done
load8 r0 7700000000000000516
cmp r10 r0
jne m17_done
jmp m17_identity
label m17_what
cmp r15 2
jne m17_what_name
load8 r0 7700000000000000521
cmp r9 r0
je m17_identity
jmp m17_done
label m17_what_name
cmp r15 4
jne m17_done
load8 r0 7700000000000000522
cmp r9 r0
jne m17_check_name
load8 r0 7700000000000000516
cmp r10 r0
jne m17_done
load8 r0 7700000000000000521
cmp r11 r0
je m17_identity
jmp m17_done
label m17_check_name
load8 r0 7700000000000000528
cmp r9 r0
jne m17_factual_article
load8 r0 7700000000000000517
cmp r10 r0
jne m17_factual_article
load8 r0 7700000000000000518
cmp r11 r0
je m17_identity
label m17_factual_article
load8 r0 7400000000000001603
cmp r0 2
jne m17_done
cmp r10 14
je m17_article_ok
load8 r0 7700000000000000514
cmp r10 r0
je m17_article_ok
load8 r0 7700000000000000536
cmp r10 r0
jne m17_done
label m17_article_ok
load8 r0 7400000000000001607
cmp r0 1
jne m17_unsupported
mov r8 r11
jmp m17_fact_query
label m17_tell
cmp r15 3
je m17_tell_three
cmp r15 4
je m17_tell_four
cmp r15 5
jne m17_done
load8 r0 7700000000000000525
cmp r9 r0
jne m17_done
load8 r0 7700000000000000524
cmp r10 r0
jne m17_done
mov r10 r11
mov r11 r12
jmp m17_tell_article
label m17_tell_four
load8 r0 7700000000000000525
cmp r9 r0
jne m17_spanish_tell
load8 r0 7700000000000000524
cmp r10 r0
jne m17_done
mov r8 r11
jmp m17_tell_subject
label m17_spanish_tell
load8 r0 7700000000000000524
cmp r9 r0
jne m17_done
label m17_tell_article
cmp r10 14
je m17_tell_article_ready
load8 r0 7700000000000000514
cmp r10 r0
je m17_tell_article_ready
load8 r0 7700000000000000536
cmp r10 r0
jne m17_done
label m17_tell_article_ready
mov r8 r11
jmp m17_tell_subject
label m17_tell_three
load8 r0 7700000000000000524
cmp r9 r0
jne m17_done
mov r8 r10
label m17_tell_subject
load8 r9 7700000000000000528
jmp m17_fact_query
label m17_followup
cmp r15 2
je m17_followup_two
cmp r15 3
jne m17_done
cmp r9 14
je m17_followup_article
load8 r0 7700000000000000514
cmp r9 r0
je m17_followup_article
load8 r0 7700000000000000536
cmp r9 r0
jne m17_done
label m17_followup_article
mov r8 r10
jmp m17_followup_entity
label m17_followup_two
mov r8 r9
label m17_followup_entity
cmp r8 0
je m17_unsupported
cmp r8 13
jlt m17_followup_topic
cmp r8 22
jle m17_clarify
label m17_followup_topic
load8 r0 7700000000000000010
cmp r0 1
je m17_followup_count
cmp r0 2
jne m17_clarify
load8 r0 7700000000000000007
cmp r0 1
jne m17_clarify
load8 r9 7700000000000000009
jmp m17_fact_query
label m17_followup_count
set r7 7700000000000010000
mov r0 r8
mul r0 4
add r7 r0
load8 r0 $r7
cmp r0 1
je m17_followup_actor
cmp r0 2
jne m17_clarify
mov r10 r8
load8 r8 7700000000000000005
jmp m17_count_query
label m17_followup_actor
load8 r10 7700000000000000006
jmp m17_count_query
label m17_count_short
load8 r0 7700000000000000529
cmp r9 r0
jne m17_done
cmp r15 2
je m17_implicit_count
cmp r15 3
jne m17_done
load8 r0 7400000000000001605
cmp r0 1
jne m17_unsupported
mov r8 r10
jmp m17_explicit_count
label m17_english_count_short
cmp r15 3
jne m17_english_count_five
load8 r0 7700000000000000528
cmp r9 r0
jne m17_done
load8 r0 7700000000000000516
cmp r10 r0
je m17_status
jmp m17_done
label m17_english_count_five
cmp r15 5
jne m17_done
load8 r0 7700000000000000533
cmp r9 r0
jne m17_done
load8 r0 7700000000000000534
cmp r10 r0
jne m17_done
load8 r0 7700000000000000529
cmp r12 r0
jne m17_done
load8 r0 7400000000000001607
cmp r0 1
jne m17_unsupported
mov r8 r11
jmp m17_explicit_count
label m17_implicit_count
load8 r8 7700000000000000005
label m17_explicit_count
load8 r0 7700000000000000010
cmp r0 1
jne m17_clarify
load8 r0 7700000000000000004
cmp r0 1
jne m17_clarify
load8 r10 7700000000000000006
jmp m17_count_query
label m17_action_short
cmp r15 4
je m17_actor_more
cmp r15 3
jne m17_verb_first
load8 r0 7400000000000001601
cmp r0 1
jne m17_verb_first
# Explicit actor with omitted object: A V NUMBER.
load8 r0 7400000000000001603
cmp r0 2
jne m17_done
cmp r10 0
je m17_actor_number
cmp r10 13
jlt m17_done
cmp r10 22
jgt m17_done
label m17_actor_number
set r12 0
jmp m17_actor_effect
label m17_actor_more
load8 r0 7400000000000001601
cmp r0 1
jne m17_done
load8 r0 7700000000000000527
cmp r11 r0
jne m17_done
load8 r0 7400000000000001603
cmp r0 2
jne m17_done
set r12 1
label m17_actor_effect
set r7 7500000000000010002
mov r0 r9
mul r0 24
add r7 r0
load8 r0 $r7
cmp r0 1
jlt m17_done
cmp r0 3
jgt m17_done
cmp r12 1
jne m17_actor_context
cmp r0 1
je m17_unsupported
label m17_actor_context
load8 r0 7700000000000000010
cmp r0 1
jne m17_clarify
load8 r0 7700000000000000004
cmp r0 1
jne m17_clarify
load8 r0 7700000000000000006
store8 7400000000000001606 r0
store8 7400000000000001607 1
store8 7400000000000000032 4
jmp conversation_intake
label m17_verb_first
cmp r15 2
jlt m17_done
cmp r15 3
jgt m17_done
load8 r0 7400000000000001601
cmp r0 2
jne m17_done
set r7 7500000000000010002
mov r0 r8
mul r0 24
add r7 r0
load8 r0 $r7
cmp r0 1
jlt m17_done
cmp r0 3
jgt m17_done
cmp r15 3
jne m17_verb_question
load8 r1 7700000000000000527
cmp r10 r1
jne m17_verb_question
cmp r0 1
je m17_unsupported
label m17_verb_question
load8 r0 7400000000000000047
cmp r0 0
jne m17_unsupported
load8 r0 7700000000000000010
cmp r0 1
jne m17_clarify
load8 r0 7700000000000000004
cmp r0 1
jne m17_clarify
mov r11 r8
load8 r8 7700000000000000005
cmp r15 2
je m17_action_implicit_item
load8 r0 7700000000000000527
cmp r10 r0
je m17_action_implicit_item
load8 r0 7400000000000001605
cmp r0 1
jne m17_unsupported
jmp m17_action_item
label m17_action_implicit_item
load8 r10 7700000000000000006
label m17_action_item
# Copy only the numeric token to its canonical E014 position. XI resolves it.
set r0 0
label m17_number_copy
set r7 7400000000000000546
add r7 r0
load8 r1 $r7
set r7 7400000000000000580
add r7 r0
store8 $r7 r1
add r0 1
cmp r0 34
jlt m17_number_copy
load8 r0 7400000000000001603
store8 7400000000000001605 r0
store8 7400000000000001604 r9
store8 7400000000000001600 r8
store8 7400000000000001601 1
store8 7400000000000001602 r11
store8 7400000000000001603 2
store8 7400000000000001606 r10
store8 7400000000000001607 1
store8 7400000000000000032 4
jmp conversation_intake
label m17_count_query
cmp r8 0
je m17_clarify
cmp r10 0
je m17_clarify
load8 r0 7700000000000000535
store8 7400000000000001600 r0
store8 7400000000000001601 3
store8 7400000000000001602 r10
store8 7400000000000001603 1
load8 r0 7700000000000000529
store8 7400000000000001604 r0
store8 7400000000000001605 2
store8 7400000000000001606 r8
store8 7400000000000001607 1
store8 7400000000000000032 4
jmp conversation_intake
label m17_fact_query
cmp r8 0
je m17_unsupported
cmp r8 13
jlt m17_fact_entity
cmp r8 22
jle m17_unsupported
label m17_fact_entity
cmp r8 12
jle m17_fact_ready
set r7 7400000000000006000
add r7 r8
load8 r0 $r7
cmp r0 1
jne m17_unsupported
label m17_fact_ready
load8 r0 7700000000000000530
store8 7400000000000001600 r0
store8 7400000000000001601 3
store8 7400000000000001602 r9
store8 7400000000000001603 2
store8 7400000000000001604 r8
store8 7400000000000001605 1
store8 7400000000000000032 3
jmp conversation_intake
label m17_identity
store8 7700000000000000017 2
jmp conversation_intake
label m17_status
store8 7700000000000000017 8
jmp conversation_intake
label m17_unsupported
store8 7700000000000000017 3
jmp conversation_intake
label m17_clarify
store8 7700000000000000017 4
label m17_done
jmp conversation_intake
label conversation_intake
load8 r0 7700000000000000017
cmp r0 0
jne conversation_shortcut
label m18_entry
# Read learned structural records only; no Spanish/English spelling in code.
# Match all enabled patterns. Conflicting semantic roles cause abstention.
# On one semantic interpretation, normalize RESOLVED slots to E014's query.
# Raw input and numeric expressions are never rewritten.
load8 r0 7600000000000000002
cmp r0 0
je m18_done
cmp r0 1
jne m18_invalid
load8 r0 7400000000000000040
cmp r0 0
jne m18_done
load8 r15 7400000000000000032
cmp r15 4
jlt m18_done
load8 r13 7600000000000000003
cmp r13 16
jgt m18_invalid
set r0 0
label m18_pattern
cmp r0 r13
jge m18_matched
set r1 7600000000000001000
mov r2 r0
mul r2 64
add r1 r2
load8 r2 $r1
cmp r2 r15
jne m18_next_pattern
mov r7 r1
add r7 1
load8 r2 $r7
cmp r2 1
jne m18_next_pattern
set r2 0
set r9 0
set r10 0
set r11 0
label m18_token
cmp r2 r15
jge m18_full_match
mov r3 r1
add r3 8
mov r4 r2
mul r4 3
add r3 r4
load8 r4 $r3
set r5 7400000000000001600
mov r6 r2
mul r6 2
add r5 r6
load8 r6 $r5
add r5 1
load8 r7 $r5
cmp r6 0
je m18_next_pattern
cmp r4 0
je m18_literal
cmp r4 3
je m18_verb
cmp r4 2
jgt m18_invalid
cmp r7 1
jne m18_next_pattern
cmp r6 13
jlt m18_entity
cmp r6 22
jle m18_next_pattern
label m18_entity
cmp r4 1
jne m18_item
mov r9 r6
jmp m18_next_token
label m18_item
mov r10 r6
jmp m18_next_token
label m18_verb
cmp r7 2
jne m18_next_pattern
set r5 7500000000000010002
mov r8 r6
mul r8 24
add r5 r8
load8 r8 $r5
cmp r8 1
jne m18_next_pattern
mov r11 r6
jmp m18_next_token
label m18_literal
add r3 1
load8 r8 $r3
cmp r8 r6
jne m18_next_pattern
add r3 1
load8 r8 $r3
cmp r8 r7
jne m18_next_pattern
label m18_next_token
add r2 1
jmp m18_token
label m18_full_match
cmp r9 0
je m18_invalid
cmp r10 0
je m18_invalid
cmp r11 0
je m18_invalid
load8 r4 7600000000000000008
cmp r4 0
je m18_first_match
load8 r4 7600000000000000009
cmp r4 r9
jne m18_ambiguous
load8 r4 7600000000000000010
cmp r4 r10
jne m18_ambiguous
load8 r4 7600000000000000011
cmp r4 r11
jne m18_ambiguous
jmp m18_next_pattern
label m18_first_match
store8 7600000000000000008 1
store8 7600000000000000009 r9
store8 7600000000000000010 r10
store8 7600000000000000011 r11
jmp m18_next_pattern
label m18_ambiguous
store8 7600000000000000008 2
label m18_next_pattern
add r0 1
jmp m18_pattern
label m18_matched
load8 r0 7600000000000000008
cmp r0 0
je m18_clean
cmp r0 1
jne m18_conflict
load8 r0 7500000000000000004
cmp r0 0
je m18_invalid
store8 7400000000000001600 r0
store8 7400000000000001601 3
load8 r0 7600000000000000010
store8 7400000000000001602 r0
store8 7400000000000001603 1
load8 r0 7600000000000000011
store8 7400000000000001604 r0
store8 7400000000000001605 2
load8 r0 7600000000000000009
store8 7400000000000001606 r0
store8 7400000000000001607 1
store8 7400000000000000032 4
jmp m18_clean
label m18_conflict
store8 7400000000000000040 1
label m18_clean
store8 7600000000000000008 0
store8 7600000000000000009 0
store8 7600000000000000010 0
store8 7600000000000000011 0
label m18_done
jmp m19_entry
label m18_invalid
div r0 0
label m19_entry
# Microgrammar uses learned roles, not literal Spanish/English question words:
# SUBJECT PREDICATE OBJECT? or QUESTION PREDICATE SUBJECT?
store8 7400000000000000008 0
store8 7400000000000000009 0
store8 7400000000000000010 0
store8 7400000000000000011 0
store8 7400000000000000012 0
store8 7400000000000000013 0
store8 7400000000000000014 0
store8 7400000000000000015 0
set r0 0
label m19_clear_answers
set r7 7400000000000002100
add r7 r0
store8 $r7 0
add r0 1
cmp r0 8
jlt m19_clear_answers
set r0 0
label m19_clear_proof
set r7 7400000000000002200
add r7 r0
store8 $r7 0
add r0 1
cmp r0 32
jlt m19_clear_proof
load8 r0 7400000000000000040
cmp r0 0
jne m19_grammar_error
load8 r0 7400000000000000032
cmp r0 3
jne m19_grammar_error
load8 r0 7400000000000001603
cmp r0 2
jne m19_grammar_error
load8 r3 7400000000000001602
store8 7400000000000000011 r3
load8 r0 7400000000000001601
cmp r0 3
je m19_object_question
store8 7400000000000000013 1
load8 r2 7400000000000001600
load8 r4 7400000000000001604
store8 7400000000000000010 r2
store8 7400000000000000012 r4
cmp r2 0
je m19_unknown
cmp r4 0
je m19_unknown
load8 r0 7400000000000001605
cmp r0 3
je m19_grammar_error
jmp dispatch
label m19_object_question
store8 7400000000000000013 2
load8 r2 7400000000000001604
store8 7400000000000000010 r2
cmp r2 0
je m19_unknown
load8 r0 7400000000000001605
cmp r0 3
je m19_grammar_error
jmp dispatch
label m19_unknown
store8 7400000000000000009 1
jmp dispatch
label m19_grammar_error
store8 7400000000000000009 2
jmp dispatch
label dispatch
label m20_entry
# Optional E014 route. Historical checkpoints incur a schema check only.
load8 r0 7500000000000000002
cmp r0 1
jne m20_done
load8 r0 7400000000000000040
cmp r0 0
jne m20_done
load8 r0 7400000000000000032
cmp r0 1
jlt m20_done
load8 r1 7400000000000001600
load8 r2 7500000000000000004
cmp r2 0
je m20_check_verb
cmp r1 r2
je m20_story
label m20_check_verb
load8 r0 7400000000000000032
# Three-token factual/legacy/arithmetic routes retain their existing priority.
cmp r0 4
jlt m20_done
load8 r1 7400000000000001602
cmp r1 0
je m20_check_actor
set r7 7500000000000010001
mul r1 24
add r7 r1
load8 r0 $r7
cmp r0 0
jne m20_story
label m20_check_actor
load8 r0 7400000000000001601
cmp r0 1
jne m20_done
load8 r0 7400000000000001600
cmp r0 13
jlt m20_story
cmp r0 22
jle m20_done
label m20_story
store8 7500000000000000016 1
label m20_done
jmp choose_story
label choose_story
load8 r0 7500000000000000016
cmp r0 1
je story
label m21_entry
# Read-only recognition of complete questions in the existing E009 vocabulary.
# Missing new words must not make previous learned relations inaccessible.
store8 7400000000000000046 0
load8 r0 7400000000000000040
cmp r0 0
jne m21_done
load8 r0 7400000000000000032
cmp r0 3
jne m21_done
load8 r0 7100000000000000002
cmp r0 1
jne m21_done
load8 r15 7100000000000000016
set r0 0
label m21_token
set r1 7400000000000000512
mov r2 r0
mul r2 34
add r1 r2
load8 r2 $r1
cmp r2 8
jgt m21_done
set r3 0
label m21_lexeme
cmp r3 r15
jge m21_done
set r4 7100000000000001000
mov r5 r3
mul r5 16
add r4 r5
load8 r5 $r4
cmp r5 r2
jne m21_next_lexeme
set r6 0
label m21_letter
cmp r6 r2
jge m21_found
mov r7 r1
add r7 1
add r7 r6
load8 r8 $r7
mov r7 r4
add r7 2
add r7 r6
load8 r9 $r7
cmp r8 r9
jne m21_next_lexeme
add r6 1
jmp m21_letter
label m21_found
add r0 1
cmp r0 3
jlt m21_token
store8 7400000000000000046 1
jmp choose_route
label m21_next_lexeme
add r3 1
jmp m21_lexeme
label m21_done
jmp choose_route
label choose_route
load8 r0 7400000000000000013
cmp r0 0
je check_legacy
load8 r0 7400000000000000009
cmp r0 0
je knowledge
label check_legacy
load8 r0 7400000000000000046
cmp r0 1
je legacy
load8 r0 7400000000000000013
cmp r0 0
jne knowledge
load8 r0 7400000000000000040
cmp r0 0
jne knowledge
label m22_entry
# Route canonical bytes to the EXISTING E011 arithmetic learner, not a host
# classifier. No knowledge content or replacement arithmetic model here.
store8 7300000000000000016 1
load8 r0 7400000000000000003
store8 7300000000000000003 r0
load8 r15 7400000000000000032
set r0 0
set r1 0
label m22_token
cmp r0 r15
jge m22_complete
# Conversational aliases of a grounded numeral reuse its original E010 name.
load8 r4 7700000000000000016
cmp r4 1
jne m22_raw_token
set r7 7400000000000001600
mov r2 r0
mul r2 2
add r7 r2
load8 r4 $r7
cmp r4 13
jlt m22_raw_token
cmp r4 22
jgt m22_raw_token
sub r4 1
mul r4 32
set r7 7200000000000001005
add r7 r4
jmp m22_token_ready
label m22_raw_token
set r7 7400000000000000512
mov r2 r0
mul r2 34
add r7 r2
label m22_token_ready
load8 r3 $r7
set r2 0
label m22_character
cmp r2 r3
jge m22_separator
mov r8 r7
add r8 1
add r8 r2
load8 r9 $r8
set r8 7300000000000000128
add r8 r1
store8 $r8 r9
add r1 1
add r2 1
jmp m22_character
label m22_separator
add r0 1
cmp r0 r15
jge m22_complete
set r8 7300000000000000128
add r8 r1
store8 $r8 32
add r1 1
jmp m22_token
label m22_complete
store8 7300000000000000017 r1
jmp m23_entry
label m23_entry
# Tokenize real text in XI. ASCII case folding, whitespace and final '?' only.
# Intake +16=1, +17=byte length, +128..382=raw bytes. Max 15 words of 16 bytes.
# Tokens +512, stride 18; parse error +40. No semantic answers in this stage.
load8 r0 7300000000000000002
cmp r0 1
jne m23_invalid
load8 r0 7300000000000000016
cmp r0 1
jne m23_invalid
load8 r9 7300000000000000017
cmp r9 0
je m23_bad_text
set r0 0
set r1 0
set r2 0
set r10 0
store8 7300000000000000040 0
label m23_char_loop
cmp r0 r9
jge m23_end_text
set r7 7300000000000000128
add r7 r0
load8 r3 $r7
cmp r3 32
je m23_separator
cmp r3 9
je m23_separator
cmp r10 1
je m23_bad_text
cmp r3 63
je m23_question_mark
cmp r3 195
je m23_conversational_accent
cmp r3 65
jlt m23_check_digit
cmp r3 90
jgt m23_check_alpha
add r3 32
label m23_check_alpha
cmp r3 97
jlt m23_bad_text
cmp r3 122
jgt m23_bad_text
jmp m23_write_char
label m23_check_digit
cmp r3 48
jlt m23_bad_text
cmp r3 57
jgt m23_bad_text
label m23_write_char
cmp r1 15
jge m23_bad_text
cmp r2 16
jge m23_bad_text
set r7 7300000000000000513
mov r8 r1
mul r8 18
add r7 r8
add r7 r2
store8 $r7 r3
add r2 1
jmp m23_next_char
label m23_conversational_accent
# Accent folding is optional on the conversational surface. Old E011 models
# retain their ASCII protocol. Operator meanings still come from learned D.
load8 r7 7700000000000000016
cmp r7 1
jne m23_bad_text
add r0 1
cmp r0 r9
jge m23_bad_text
set r7 7300000000000000128
add r7 r0
load8 r3 $r7
cmp r3 129
je m23_accent_a
cmp r3 137
je m23_accent_e
cmp r3 141
je m23_accent_i
cmp r3 147
je m23_accent_o
cmp r3 154
je m23_accent_u
cmp r3 161
je m23_accent_a
cmp r3 169
je m23_accent_e
cmp r3 173
je m23_accent_i
cmp r3 179
je m23_accent_o
cmp r3 186
je m23_accent_u
jmp m23_bad_text
label m23_accent_a
set r3 97
jmp m23_write_char
label m23_accent_e
set r3 101
jmp m23_write_char
label m23_accent_i
set r3 105
jmp m23_write_char
label m23_accent_o
set r3 111
jmp m23_write_char
label m23_accent_u
set r3 117
jmp m23_write_char
label m23_question_mark
cmp r2 0
jne m23_mark_terminal
cmp r1 0
je m23_bad_text
label m23_mark_terminal
set r10 1
jmp m23_next_char
label m23_separator
cmp r2 0
je m23_next_char
set r7 7300000000000000512
mov r8 r1
mul r8 18
add r7 r8
store8 $r7 r2
add r1 1
set r2 0
label m23_next_char
add r0 1
jmp m23_char_loop
label m23_end_text
cmp r2 0
je m23_finish_tokens
set r7 7300000000000000512
mov r8 r1
mul r8 18
add r7 r8
store8 $r7 r2
add r1 1
label m23_finish_tokens
cmp r1 0
je m23_bad_text
store8 7300000000000000032 r1
jmp m24_entry
label m23_bad_text
store8 7300000000000000040 1
store8 7300000000000000032 0
jmp m24_entry
label m23_invalid
div r0 0
label m24_entry
# Resolve every word through E010's existing bilingual numerals and E011's
# learned operator lexicon. Decimal notation is a designed base-10 grammar,
# anchored to the ten learned digit concepts; it is not a learned number name.
# Resolution +800+i*4: kind 1=number 2=operator 0=unknown; low/high value.
load8 r0 7300000000000000002
cmp r0 1
jne m24_invalid
load8 r0 7300000000000000016
cmp r0 1
jne m24_invalid
load8 r0 7300000000000000040
cmp r0 0
jne m24_done
load8 r15 7300000000000000032
cmp r15 15
jgt m24_invalid
set r0 0
label m24_each_token
cmp r0 r15
jge m24_done
set r1 7300000000000000512
mov r2 r0
mul r2 18
add r1 r2
load8 r2 $r1
set r3 0
set r4 0
# First try a decimal string, requiring a learned grounding for every digit.
label m24_decimal_chars
cmp r3 r2
jge m24_decimal_complete
mov r5 r1
add r5 1
add r5 r3
load8 r6 $r5
cmp r6 48
jlt m24_lexical_number
cmp r6 57
jgt m24_lexical_number
sub r6 48
load8 r7 7200000000000000010
set r8 0
label m24_ground_digit
cmp r8 r7
jge m24_unresolved
set r9 7200000000000001000
mov r10 r8
mul r10 32
add r9 r10
load8 r10 $r9
cmp r10 4
jne m24_next_digit_concept
add r9 1
load8 r10 $r9
cmp r10 r6
jne m24_next_digit_concept
add r9 3
load8 r10 $r9
cmp r10 2
jlt m24_next_digit_concept
mul r4 10
add r4 r6
cmp r4 65535
jgt m24_unresolved
add r3 1
jmp m24_decimal_chars
label m24_next_digit_concept
add r8 1
jmp m24_ground_digit
label m24_decimal_complete
set r12 1
jmp m24_save_resolution
label m24_lexical_number
load8 r7 7200000000000000010
set r8 0
set r11 0
label m24_each_numeral
cmp r8 r7
jge m24_learned_operator
set r9 7200000000000001000
mov r10 r8
mul r10 32
add r9 r10
load8 r10 $r9
cmp r10 4
jne m24_next_numeral
mov r10 r9
add r10 4
load8 r10 $r10
cmp r10 2
jlt m24_next_numeral
set r13 5
label m24_each_language
mov r10 r9
add r10 r13
load8 r10 $r10
cmp r10 r2
jne m24_next_language
set r3 0
label m24_lexical_chars
cmp r3 r2
jge m24_numeral_match
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
jne m24_next_language
add r3 1
jmp m24_lexical_chars
label m24_numeral_match
mov r5 r9
add r5 1
load8 r6 $r5
cmp r11 0
je m24_first_numeral_match
cmp r4 r6
jne m24_unresolved
jmp m24_next_language
label m24_first_numeral_match
set r11 1
mov r4 r6
label m24_next_language
cmp r13 5
jne m24_next_numeral
set r13 14
jmp m24_each_language
label m24_next_numeral
add r8 1
jmp m24_each_numeral
label m24_learned_operator
cmp r11 1
je m24_resolved_number
load8 r7 7300000000000000004
cmp r7 32
jgt m24_invalid
set r8 0
label m24_each_operator
cmp r8 r7
jge m24_unresolved
set r9 7300000000000001000
mov r10 r8
mul r10 32
add r9 r10
load8 r10 $r9
cmp r10 r2
jne m24_next_operator
mov r5 r9
add r5 18
load8 r10 $r5
cmp r10 2
jlt m24_next_operator
set r3 0
label m24_operator_chars
cmp r3 r2
jge m24_operator_match
mov r5 r1
add r5 1
add r5 r3
load8 r6 $r5
mov r5 r9
add r5 1
add r5 r3
load8 r10 $r5
cmp r6 r10
jne m24_next_operator
add r3 1
jmp m24_operator_chars
label m24_operator_match
add r9 17
load8 r4 $r9
set r12 2
jmp m24_save_resolution
label m24_next_operator
add r8 1
jmp m24_each_operator
label m24_resolved_number
set r12 1
jmp m24_save_resolution
label m24_unresolved
# Optional E020 spellings refer to sealed, independently validated concepts.
# No mapping from a Spanish/English spelling to an arithmetic family here.
load8 r7 7900000000000000003
cmp r7 1
jne m24_no_scale_word
load8 r7 7900000000000000004
cmp r7 128
jgt m24_invalid
set r8 0
label m24_scale_operator
cmp r8 r7
jge m24_no_scale_word
set r9 7900000000000001000
mov r10 r8
mul r10 32
add r9 r10
load8 r10 $r9
cmp r10 r2
jne m24_next_scale_operator
set r3 0
label m24_scale_chars
cmp r3 r2
jge m24_scale_match
mov r5 r1
add r5 1
add r5 r3
load8 r6 $r5
mov r5 r9
add r5 1
add r5 r3
load8 r10 $r5
cmp r6 r10
jne m24_next_scale_operator
add r3 1
jmp m24_scale_chars
label m24_scale_match
add r9 17
load8 r4 $r9
cmp r4 1
jlt m24_invalid
cmp r4 8
jgt m24_invalid
sub r4 1
mul r4 64
set r9 7900000000000000130
add r9 r4
load8 r4 $r9
cmp r4 1
jlt m24_invalid
cmp r4 8
jgt m24_invalid
set r12 2
jmp m24_save_resolution
label m24_next_scale_operator
add r8 1
jmp m24_scale_operator
label m24_no_scale_word
set r12 0
set r4 0
label m24_save_resolution
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
jmp m24_each_token
label m24_done
jmp m25_entry
label m24_invalid
div r0 0
label m25_entry
# Evaluate new compositions using ONLY grounded quantities and learned effects.
# Grammar: NUMBER (OP NUMBER)*; OP NUMBER... may continue the last valid turn.
# Designed left-to-right grammar, 0..65535 at EVERY step, max seven effects.
load8 r0 7300000000000000002
cmp r0 1
jne m25_invalid
load8 r0 7300000000000000016
cmp r0 1
jne m25_invalid
load8 r0 7300000000000000024
cmp r0 0
jne m25_invalid
set r14 0
set r13 0
set r11 0
load8 r0 7300000000000000040
cmp r0 0
jne m25_syntax_error
load8 r15 7300000000000000032
cmp r15 1
jlt m25_syntax_error
load8 r0 7300000000000000800
cmp r0 1
je m25_explicit_start
cmp r0 2
jne m25_unknown_word
load8 r0 7300000000000000005
cmp r0 1
jne m25_missing_context
load8 r2 7300000000000000006
load8 r3 7300000000000000007
mul r3 256
add r2 r3
set r1 0
jmp m25_apply_pairs
label m25_explicit_start
load8 r2 7300000000000000801
load8 r3 7300000000000000802
mul r3 256
add r2 r3
set r1 1
label m25_apply_pairs
cmp r1 r15
jge m25_supported
mov r0 r1
add r0 1
cmp r0 r15
jge m25_syntax_error
set r7 7300000000000000800
mov r8 r1
mul r8 4
add r7 r8
load8 r0 $r7
cmp r0 2
jne m25_unknown_word
add r7 1
load8 r4 $r7
add r7 3
load8 r0 $r7
cmp r0 1
jne m25_unknown_word
add r7 1
load8 r3 $r7
add r7 1
load8 r0 $r7
mul r0 256
add r3 r0
# Until a precedence grammar is implemented, do not silently evaluate a
# lower-priority sum/difference before a following product/division/remainder.
cmp r4 3
jlt m25_precedence_ready
cmp r4 5
jgt m25_precedence_ready
cmp r11 1
je m25_syntax_error
label m25_precedence_ready
cmp r4 1
je m25_subtract
cmp r4 2
je m25_add
cmp r4 3
je m25_multiply
cmp r4 4
je m25_exact_divide
cmp r4 5
je m25_remainder
cmp r4 6
je m25_minimum
cmp r4 7
je m25_maximum
cmp r4 8
jne m25_unknown_word
sub r2 r3
cmp r2 0
jge m25_check_bounds
mul r2 -1
jmp m25_check_bounds
label m25_add
set r11 1
add r2 r3
jmp m25_check_bounds
label m25_subtract
set r11 1
sub r2 r3
jmp m25_check_bounds
label m25_multiply
mul r2 r3
jmp m25_check_bounds
label m25_exact_divide
cmp r3 0
je m25_range_error
mov r0 r2
mod r0 r3
cmp r0 0
jne m25_range_error
div r2 r3
jmp m25_check_bounds
label m25_remainder
cmp r3 0
je m25_range_error
mod r2 r3
jmp m25_check_bounds
label m25_minimum
cmp r2 r3
jle m25_check_bounds
mov r2 r3
jmp m25_check_bounds
label m25_maximum
cmp r2 r3
jge m25_check_bounds
mov r2 r3
label m25_check_bounds
cmp r2 0
jlt m25_range_error
cmp r2 65535
jgt m25_range_error
add r13 1
add r1 2
jmp m25_apply_pairs
label m25_supported
store8 7300000000000000005 1
store8 7300000000000000008 1
store8 7300000000000000009 0
store8 7300000000000000012 r13
mov r3 r2
mod r3 256
store8 7300000000000000006 r3
store8 7300000000000000010 r3
div r2 256
store8 7300000000000000007 r2
store8 7300000000000000011 r2
jmp m25_clean
label m25_unknown_word
set r14 1
jmp m25_abstain
label m25_syntax_error
set r14 2
jmp m25_abstain
label m25_missing_context
set r14 3
jmp m25_abstain
label m25_range_error
set r14 4
label m25_abstain
# Failed turns invalidate context: never silently reuse a stale answer.
store8 7300000000000000005 0
store8 7300000000000000006 0
store8 7300000000000000007 0
store8 7300000000000000008 0
store8 7300000000000000009 r14
store8 7300000000000000010 0
store8 7300000000000000011 0
store8 7300000000000000012 0
label m25_clean
set r0 16
label m25_clear_query
set r7 7300000000000000000
add r7 r0
store8 $r7 0
add r0 1
cmp r0 864
jlt m25_clear_query
load8 r10 7300000000000000008
print r10
load8 r11 7300000000000000009
print r11
jmp arithmetic_reply
label m25_invalid
div r0 0
label arithmetic_reply
load8 r0 7700000000000000016
cmp r0 1
je conversation_arithmetic
label m26_entry
# Read-only response: learned ES/EN number names, otherwise composed digits.
load8 r0 7300000000000000002
cmp r0 1
jne m26_invalid
load8 r0 7300000000000000008
cmp r0 1
je m26_supported
set r14 63
print r14
jmp cleanup
label m26_supported
load8 r2 7300000000000000010
load8 r0 7300000000000000011
mul r0 256
add r2 r0
load8 r15 7300000000000000003
cmp r15 1
je m26_language_ready
cmp r15 2
jne m26_invalid
label m26_language_ready
load8 r7 7200000000000000010
set r0 0
label m26_find_learned_name
cmp r0 r7
jge m26_decimal_output
set r8 7200000000000001000
mov r9 r0
mul r9 32
add r8 r9
load8 r9 $r8
cmp r9 4
jne m26_next_numeral
mov r9 r8
add r9 1
load8 r9 $r9
cmp r9 r2
jne m26_next_numeral
mov r9 r8
add r9 4
load8 r9 $r9
cmp r9 2
jlt m26_next_numeral
set r5 5
cmp r15 1
je m26_select_label
set r5 14
label m26_select_label
add r8 r5
load8 r6 $r8
cmp r6 1
jlt m26_invalid
cmp r6 8
jgt m26_invalid
set r1 0
label m26_emit_label
cmp r1 r6
jge m26_done
mov r9 r8
add r9 1
add r9 r1
load8 r14 $r9
print r14
add r1 1
jmp m26_emit_label
label m26_next_numeral
add r0 1
jmp m26_find_learned_name
label m26_decimal_output
set r3 10000
set r4 0
label m26_decimal_digit
mov r14 r2
div r14 r3
mod r2 r3
cmp r14 0
jne m26_nonzero_digit
cmp r4 1
je m26_print_digit
cmp r3 1
je m26_print_digit
jmp m26_next_place
label m26_nonzero_digit
set r4 1
label m26_print_digit
add r14 48
print r14
label m26_next_place
div r3 10
cmp r3 0
jgt m26_decimal_digit
label m26_done
jmp cleanup
label m26_invalid
div r0 0
label conversation_arithmetic
store8 7700000000000000025 3
label m27_entry
# 7700000000000000025 is set by native source linkage: 0 act,1 story,2 fact,3 arithmetic.
# Successful semantic results update small persistent discourse descriptors.
store8 7700000000000000032 0
store8 7700000000000000033 0
store8 7700000000000000034 0
store8 7700000000000000039 0
store8 7700000000000000038 1
load8 r0 7700000000000000017
cmp r0 0
jne m27_act
load8 r0 7700000000000000025
cmp r0 1
je m27_story
cmp r0 2
je m27_factual
cmp r0 3
jne m27_invalid
load8 r0 7300000000000000008
cmp r0 1
jne m27_unknown
store8 7700000000000000010 0
store8 7700000000000000018 3
store8 7700000000000000019 5
jmp conversation_render
label m27_story
load8 r0 7500000000000000008
cmp r0 1
jne m27_unknown
store8 7700000000000000004 1
load8 r0 7500000000000000010
store8 7700000000000000005 r0
load8 r0 7500000000000000011
store8 7700000000000000006 r0
store8 7700000000000000010 1
# A grammatical count sentence requires a learned order and noun inflection.
load8 r1 7400000000000000003
set r7 7700000000000001001
sub r1 1
mul r1 32
add r7 r1
load8 r0 $r7
cmp r0 2
jne m27_count_fallback
load8 r0 7500000000000000011
mul r0 224
set r7 7700000000000100000
add r7 r0
load8 r1 7400000000000000003
sub r1 1
mul r1 112
add r7 r1
load8 r0 7500000000000000012
load8 r1 7500000000000000013
cmp r1 0
jne m27_plural
cmp r0 1
jne m27_plural
load8 r0 $r7
cmp r0 0
je m27_count_fallback
add r7 34
load8 r0 $r7
cmp r0 0
je m27_count_fallback
jmp m27_count_ready
label m27_plural
add r7 101
load8 r0 $r7
cmp r0 3
jne m27_count_fallback
sub r7 33
load8 r0 $r7
cmp r0 0
je m27_count_fallback
label m27_count_ready
store8 7700000000000000018 2
jmp conversation_render
label m27_count_fallback
store8 7700000000000000018 3
store8 7700000000000000019 6
jmp conversation_render
label m27_factual
load8 r0 7400000000000000008
cmp r0 1
je m27_fact_ready
cmp r0 2
jne m27_unknown
label m27_fact_ready
store8 7700000000000000007 1
load8 r0 7400000000000000010
store8 7700000000000000008 r0
load8 r0 7400000000000000011
store8 7700000000000000009 r0
store8 7700000000000000010 2
store8 7700000000000000018 4
jmp conversation_render
label m27_unknown
set r0 3
label m27_act
store8 7700000000000000018 1
store8 7700000000000000019 r0
cmp r0 3
jlt m27_done
cmp r0 8
je m27_done
store8 7700000000000000010 0
label m27_done
jmp conversation_render
label m27_invalid
div r0 0
label legacy
label m28_entry
# Adapt canonical tokens to the original E009 ask/speak without duplicating
# its lexicon or facts. Back up only transient query descriptors/counters.
set r0 0
label m28_backup
set r7 7100000000000000140
add r7 r0
load8 r8 $r7
set r7 7400000000000004600
add r7 r0
store8 $r7 r8
add r0 1
cmp r0 57
jlt m28_backup
set r0 0
label m28_token
set r7 7400000000000000512
mov r1 r0
mul r1 34
add r7 r1
load8 r2 $r7
set r8 7100000000000000140
mov r1 r0
mul r1 10
add r8 r1
store8 $r8 r2
set r1 0
label m28_letter
cmp r1 r2
jge m28_next
mov r9 r7
add r9 1
add r9 r1
load8 r10 $r9
mov r9 r8
add r9 1
add r9 r1
store8 $r9 r10
add r1 1
jmp m28_letter
label m28_next
add r0 1
cmp r0 3
jlt m28_token
store8 7100000000000000175 3
jmp m29_entry
label m29_entry
# E009 semantic question in XI. Three grounded ASCII words in the intake.
# Answer statuses: 0=unknown, 1=supported, 2=counterevidence.
# For supported inference return an evidence witness (intermediate concept).
load8 r14 7100000000000000002
cmp r14 1
je m29_schema_ok
div r14 0
label m29_schema_ok
load8 r14 7100000000000000175
cmp r14 3
je m29_question_ready
div r14 0
label m29_question_ready
set r15 0
label m29_resolve_next_query_word
set r7 7100000000000000140
mov r8 r15
mul r8 10
add r7 r8
load8 r2 $r7
cmp r2 1
jlt m29_unknown_word
cmp r2 8
jgt m29_unknown_word
load8 r5 7100000000000000016
set r0 0
label m29_scan_word_memory
cmp r0 r5
jge m29_unknown_word
set r4 7100000000000001000
mov r8 r0
mul r8 16
add r4 r8
load8 r9 $r4
cmp r9 r2
jne m29_next_word
set r1 0
label m29_compare_letters
cmp r1 r2
jge m29_lexeme_resolved
mov r8 r7
add r8 r1
add r8 1
load8 r9 $r8
mov r10 r4
add r10 r1
add r10 2
load8 r11 $r10
cmp r9 r11
jne m29_next_word
add r1 1
jmp m29_compare_letters
label m29_lexeme_resolved
mov r8 r4
add r8 1
load8 r3 $r8
set r8 7100000000000000180
add r8 r15
store8 $r8 r3
add r15 1
cmp r15 3
jlt m29_resolve_next_query_word
jmp m29_all_words_found
label m29_next_word
add r0 1
jmp m29_scan_word_memory
label m29_unknown_word
set r2 0
set r3 0
set r4 0
set r6 0
set r10 0
set r11 0
jmp m29_commit_result
label m29_all_words_found
load8 r2 7100000000000000180
load8 r3 7100000000000000181
load8 r4 7100000000000000182
set r10 0
set r11 0
set r6 0
load8 r5 7100000000000000018
set r0 0
label m29_direct_fact_lookup
cmp r0 r5
jge m29_try_composition
set r7 7100000000000003000
mov r8 r0
mul r8 8
add r7 r8
load8 r9 $r7
cmp r9 r2
jne m29_next_direct
add r7 1
load8 r9 $r7
cmp r9 r3
jne m29_next_direct
add r7 1
load8 r9 $r7
cmp r9 r4
jne m29_next_direct
# An explicitly observed negative fact beats a hypothetical composition.
add r7 1
load8 r12 $r7
add r7 1
load8 r13 $r7
cmp r13 2
jlt m29_positive_evidence
cmp r13 r12
jlt m29_positive_evidence
set r10 2
set r11 1
jmp m29_commit_result
label m29_positive_evidence
cmp r12 2
jlt m29_commit_result
cmp r12 r13
jle m29_commit_result
set r10 1
set r11 1
jmp m29_commit_result
label m29_next_direct
add r0 1
jmp m29_direct_fact_lookup
label m29_try_composition
set r7 7100000000000002000
add r7 r3
load8 r9 $r7
cmp r9 1
jne m29_commit_result
# Transitive two-hop proof: (S,R,W) and (W,R,O), with grounded edges.
set r0 0
label m29_first_proven_edge
cmp r0 r5
jge m29_commit_result
set r7 7100000000000003000
mov r8 r0
mul r8 8
add r7 r8
load8 r9 $r7
cmp r9 r2
jne m29_next_first_edge
add r7 1
load8 r9 $r7
cmp r9 r3
jne m29_next_first_edge
add r7 1
load8 r6 $r7
add r7 1
load8 r12 $r7
cmp r12 2
jlt m29_next_first_edge
add r7 1
load8 r13 $r7
cmp r12 r13
jle m29_next_first_edge
set r1 0
label m29_second_proven_edge
cmp r1 r5
jge m29_next_first_edge
set r7 7100000000000003000
mov r8 r1
mul r8 8
add r7 r8
load8 r9 $r7
cmp r9 r6
jne m29_next_second_edge
add r7 1
load8 r9 $r7
cmp r9 r3
jne m29_next_second_edge
add r7 1
load8 r9 $r7
cmp r9 r4
jne m29_next_second_edge
add r7 1
load8 r12 $r7
cmp r12 2
jlt m29_next_second_edge
add r7 1
load8 r13 $r7
cmp r12 r13
jle m29_next_second_edge
set r10 1
set r11 2
jmp m29_commit_result
label m29_next_second_edge
add r1 1
jmp m29_second_proven_edge
label m29_next_first_edge
add r0 1
jmp m29_first_proven_edge
label m29_commit_result
# The utterance is assembled LATER from these concept IDs, not a reply table.
store8 7100000000000000190 r10
store8 7100000000000000191 r2
store8 7100000000000000192 r3
store8 7100000000000000193 r4
store8 7100000000000000194 r6
store8 7100000000000000195 r11
set r0 0
label m29_erase_query_intake
set r7 7100000000000000140
add r7 r0
store8 $r7 0
add r0 1
cmp r0 29
jlt m29_erase_query_intake
store8 7100000000000000170 0
store8 7100000000000000175 0
set r0 0
label m29_erase_resolution_scratch
set r7 7100000000000000180
add r7 r0
store8 $r7 0
add r0 1
cmp r0 3
jlt m29_erase_resolution_scratch
load8 r12 7100000000000000196
cmp r12 250
jge m29_count_queries_done
add r12 1
store8 7100000000000000196 r12
label m29_count_queries_done
print r10
print r11
print r6
mem_stats
stats
label m30_entry
# E009 first compositional utterances in original XI. ASCII byte stream.
# Decoding these bytes to characters is display I/O, never another language AI.
# S, P, O and (optional) witness ALL come from learned lexical concept IDs.
load8 r12 7100000000000000002
cmp r12 1
je m30_native_language_ready
div r12 0
label m30_native_language_ready
load8 r10 7100000000000000190
cmp r10 0
jne m30_known_response
set r9 63
print r9
jmp m31_entry
label m30_known_response
cmp r10 2
jne m30_affirmative_response
# Prefix denied triple with a syntactic negation, not a learned fact.
set r9 110
print r9
set r9 111
print r9
set r9 58
print r9
set r9 32
print r9
label m30_affirmative_response
set r15 0
label m30_next_utterance_word
cmp r15 3
jne m30_normal_word
# Explanation is selected only if the proof has an actual intermediary.
set r9 32
print r9
set r9 40
print r9
set r9 118
print r9
set r9 105
print r9
set r9 97
print r9
set r9 32
print r9
set r7 7100000000000000194
jmp m30_resolve_word_id
label m30_normal_word
set r7 7100000000000000191
add r7 r15
label m30_resolve_word_id
load8 r8 $r7
cmp r8 1
jge m30_known_concept
set r9 63
print r9
jmp m31_entry
label m30_known_concept
load8 r5 7100000000000000016
set r0 0
label m30_find_spelling
cmp r0 r5
jge m30_missing_spelling
set r4 7100000000000001000
mov r6 r0
mul r6 16
add r4 r6
mov r7 r4
add r7 1
load8 r6 $r7
cmp r6 r8
je m30_spelling_found
add r0 1
jmp m30_find_spelling
label m30_missing_spelling
set r9 63
print r9
jmp m31_entry
label m30_spelling_found
load8 r6 $r4
set r1 0
label m30_emit_ascii
cmp r1 r6
jge m30_word_complete
mov r7 r4
add r7 r1
add r7 2
load8 r9 $r7
print r9
add r1 1
jmp m30_emit_ascii
label m30_word_complete
add r15 1
cmp r15 3
jlt m30_more_words
cmp r15 4
je m30_witness_done
load8 r12 7100000000000000195
cmp r12 2
je m30_next_utterance_word
jmp m30_finish_utterance
label m30_more_words
set r9 32
print r9
jmp m30_next_utterance_word
label m30_witness_done
set r9 41
print r9
label m30_finish_utterance
set r9 46
print r9
jmp m31_entry
label m31_entry
# Complete this read-only facade: old working descriptors and query count are
# restored after the original speaker emits its answer. No old learned byte
# changes, and no second model/authority is published.
load8 r8 7100000000000000190
store8 7400000000000000008 r8
# Mode 3 explicitly identifies an original E009 utterance, whose concept IDs
# belong to its existing namespace; never mislabel them as new E012 concepts.
store8 7400000000000000013 3
store8 7400000000000000009 0
store8 7400000000000000010 0
store8 7400000000000000011 0
store8 7400000000000000012 0
store8 7400000000000000014 1
store8 7400000000000000015 0
cmp r8 0
jne m31_begin_restore
store8 7400000000000000009 3
store8 7400000000000000014 0
label m31_begin_restore
set r0 0
label m31_restore
set r7 7400000000000004600
add r7 r0
load8 r8 $r7
store8 $r7 0
set r7 7100000000000000140
add r7 r0
store8 $r7 r8
add r0 1
cmp r0 57
jlt m31_restore
jmp cleanup
label story
label m32_entry
# Stage a whole turn. No episode fact is published before all clauses pass.
# E011's prior arithmetic context is backed up and restored after the answer.
set r0 8
label m32_result
set r7 7500000000000000000
add r7 r0
store8 $r7 0
add r0 1
cmp r0 16
jlt m32_result
store8 7500000000000000008 1
store8 7400000000000000013 4
set r0 0
label m32_backup_arithmetic
set r7 7300000000000000000
add r7 r0
load8 r1 $r7
set r7 7500000000000002200
add r7 r0
store8 $r7 r1
add r0 1
cmp r0 16
jlt m32_backup_arithmetic
set r0 0
label m32_stage_ledger
set r7 8600000000000010000
add r7 r0
load8 r1 $r7
set r7 8600000000000020000
add r7 r0
store8 $r7 r1
add r0 1
cmp r0 512
jlt m32_stage_ledger
load8 r0 7500000000000000006
cmp r0 64
jgt m32_invalid
store8 7500000000000000032 r0
jmp story_parse
label m32_invalid
div r0 0
label story_parse
label m33_entry
# Designed microgrammar over shared learned IDs, never literal word spellings.
# A V NUMBER ITEM (LINK [A] V NUMBER ITEM)*, <=15 tokens.
# QUESTION ITEM ASSIGN_VERB A asks about an existing pair.
# +33 cursor,+34 previous actor,+35 ledger slot,+36 effect,+37 quantity token,
# +38 next cursor,+39 actor,+40 item,+17 pending arithmetic flag.
store8 7500000000000000017 0
load8 r0 7500000000000000008
cmp r0 1
jne m33_done
load8 r0 7500000000000000033
load8 r15 7400000000000000032
cmp r0 r15
jge m33_done
cmp r0 0
jne m33_require_link
load8 r1 7400000000000001600
load8 r2 7500000000000000004
cmp r2 0
je m33_explicit
cmp r1 r2
je m33_question
jmp m33_explicit
label m33_require_link
set r7 7400000000000001600
mov r1 r0
mul r1 2
add r7 r1
load8 r1 $r7
load8 r2 7500000000000000005
cmp r2 0
je m33_syntax
cmp r1 r2
jne m33_syntax
add r0 1
cmp r0 r15
jge m33_syntax
set r7 7400000000000001601
mov r1 r0
mul r1 2
add r7 r1
load8 r1 $r7
cmp r1 2
jne m33_explicit
load8 r2 7500000000000000034
cmp r2 0
je m33_syntax
mov r1 r0
add r0 3
jmp m33_clause_slots
label m33_explicit
load8 r1 7400000000000000047
cmp r1 0
jne m33_syntax
set r7 7400000000000001600
mov r1 r0
mul r1 2
add r7 r1
load8 r2 $r7
add r7 1
load8 r3 $r7
cmp r3 1
jne m33_unknown
cmp r2 13
jlt m33_actor_ok
cmp r2 22
jle m33_syntax
label m33_actor_ok
mov r1 r0
add r1 1
add r0 4
label m33_clause_slots
cmp r0 r15
jgt m33_syntax
store8 7500000000000000038 r0
store8 7500000000000000039 r2
set r7 7400000000000001600
mov r3 r1
mul r3 2
add r7 r3
load8 r3 $r7
add r7 1
load8 r4 $r7
cmp r4 2
jne m33_unknown
set r7 7500000000000010002
mul r3 24
add r7 r3
load8 r3 $r7
cmp r3 1
jlt m33_unknown
cmp r3 3
jgt m33_invalid
store8 7500000000000000036 r3
add r1 1
store8 7500000000000000037 r1
add r1 1
set r7 7400000000000001600
mul r1 2
add r7 r1
load8 r4 $r7
add r7 1
load8 r5 $r7
cmp r5 1
jne m33_unknown
cmp r4 13
jlt m33_item_ok
cmp r4 22
jle m33_syntax
label m33_item_ok
store8 7500000000000000040 r4
store8 7500000000000000015 2
jmp m33_lookup
label m33_question
cmp r15 4
jne m33_syntax
load8 r2 7400000000000001606
load8 r3 7400000000000001607
cmp r3 1
jne m33_unknown
cmp r2 13
jlt m33_question_actor_ok
cmp r2 22
jle m33_syntax
label m33_question_actor_ok
load8 r4 7400000000000001602
load8 r3 7400000000000001603
cmp r3 1
jne m33_unknown
cmp r4 13
jlt m33_question_item_ok
cmp r4 22
jle m33_syntax
label m33_question_item_ok
load8 r3 7400000000000001604
load8 r5 7400000000000001605
cmp r5 2
jne m33_unknown
set r7 7500000000000010002
mul r3 24
add r7 r3
load8 r3 $r7
cmp r3 1
jne m33_syntax
store8 7500000000000000039 r2
store8 7500000000000000040 r4
store8 7500000000000000015 1
store8 7500000000000000033 r15
label m33_lookup
load8 r5 7500000000000000032
set r0 0
label m33_pair
cmp r0 r5
jge m33_missing
set r7 8600000000000020000
mov r1 r0
mul r1 8
add r7 r1
load8 r1 $r7
cmp r1 r2
jne m33_next_pair
add r7 1
load8 r1 $r7
cmp r1 r4
je m33_found
label m33_next_pair
add r0 1
jmp m33_pair
label m33_missing
load8 r1 7500000000000000015
cmp r1 1
je m33_no_memory
load8 r1 7500000000000000036
cmp r1 1
jne m33_no_memory
cmp r0 64
jge m33_capacity
label m33_found
store8 7500000000000000035 r0
load8 r1 7500000000000000015
cmp r1 1
jne m33_ready
set r7 8600000000000020002
mul r0 8
add r7 r0
load8 r0 $r7
store8 7500000000000000012 r0
add r7 1
load8 r0 $r7
store8 7500000000000000013 r0
store8 7500000000000000010 r2
store8 7500000000000000011 r4
jmp story_parsed
label m33_ready
store8 7500000000000000017 1
jmp story_parsed
label m33_unknown
set r0 1
jmp m33_failure
label m33_syntax
set r0 2
jmp m33_failure
label m33_no_memory
set r0 3
jmp m33_failure
label m33_capacity
set r0 5
label m33_failure
store8 7500000000000000008 0
store8 7500000000000000009 r0
store8 7500000000000000017 0
label m33_done
jmp story_parsed
label m33_invalid
div r0 0
label story_parsed
load8 r0 7500000000000000017
cmp r0 1
jne story_finish
label m34_entry
# Reuse E011's number resolver. A shared E010 number alias is canonicalized
# to its original taught Spanish name, then resolved by the original code.
# Other text (including decimals) is copied unchanged, never host-parsed.
store8 7300000000000000016 1
store8 7300000000000000024 0
store8 7300000000000000032 1
store8 7300000000000000040 0
load8 r0 7500000000000000037
set r7 7400000000000001600
mov r1 r0
mul r1 2
add r7 r1
load8 r2 $r7
cmp r2 1
jlt m34_raw
cmp r2 22
jgt m34_raw
sub r2 1
mul r2 32
set r7 7200000000000001000
add r7 r2
load8 r1 $r7
cmp r1 4
jne m34_raw
add r7 4
load8 r1 $r7
cmp r1 2
jlt m34_raw
add r7 1
jmp m34_copy_start
label m34_raw
set r7 7400000000000000512
mul r0 34
add r7 r0
label m34_copy_start
load8 r2 $r7
cmp r2 1
jlt m34_invalid
cmp r2 17
jgt m34_too_long
store8 7300000000000000512 r2
set r0 0
label m34_copy
cmp r0 r2
jge m34_done
mov r8 r7
add r8 1
add r8 r0
load8 r1 $r8
set r8 7300000000000000513
add r8 r0
store8 $r8 r1
add r0 1
jmp m34_copy
label m34_too_long
store8 7300000000000000040 1
label m34_done
jmp m35_entry
label m34_invalid
div r0 0
label m35_entry
# Resolve every word through E010's existing bilingual numerals and E011's
# learned operator lexicon. Decimal notation is a designed base-10 grammar,
# anchored to the ten learned digit concepts; it is not a learned number name.
# Resolution +800+i*4: kind 1=number 2=operator 0=unknown; low/high value.
load8 r0 7300000000000000002
cmp r0 1
jne m35_invalid
load8 r0 7300000000000000016
cmp r0 1
jne m35_invalid
load8 r0 7300000000000000040
cmp r0 0
jne m35_done
load8 r15 7300000000000000032
cmp r15 15
jgt m35_invalid
set r0 0
label m35_each_token
cmp r0 r15
jge m35_done
set r1 7300000000000000512
mov r2 r0
mul r2 18
add r1 r2
load8 r2 $r1
set r3 0
set r4 0
# First try a decimal string, requiring a learned grounding for every digit.
label m35_decimal_chars
cmp r3 r2
jge m35_decimal_complete
mov r5 r1
add r5 1
add r5 r3
load8 r6 $r5
cmp r6 48
jlt m35_lexical_number
cmp r6 57
jgt m35_lexical_number
sub r6 48
load8 r7 7200000000000000010
set r8 0
label m35_ground_digit
cmp r8 r7
jge m35_unresolved
set r9 7200000000000001000
mov r10 r8
mul r10 32
add r9 r10
load8 r10 $r9
cmp r10 4
jne m35_next_digit_concept
add r9 1
load8 r10 $r9
cmp r10 r6
jne m35_next_digit_concept
add r9 3
load8 r10 $r9
cmp r10 2
jlt m35_next_digit_concept
mul r4 10
add r4 r6
cmp r4 65535
jgt m35_unresolved
add r3 1
jmp m35_decimal_chars
label m35_next_digit_concept
add r8 1
jmp m35_ground_digit
label m35_decimal_complete
set r12 1
jmp m35_save_resolution
label m35_lexical_number
load8 r7 7200000000000000010
set r8 0
set r11 0
label m35_each_numeral
cmp r8 r7
jge m35_learned_operator
set r9 7200000000000001000
mov r10 r8
mul r10 32
add r9 r10
load8 r10 $r9
cmp r10 4
jne m35_next_numeral
mov r10 r9
add r10 4
load8 r10 $r10
cmp r10 2
jlt m35_next_numeral
set r13 5
label m35_each_language
mov r10 r9
add r10 r13
load8 r10 $r10
cmp r10 r2
jne m35_next_language
set r3 0
label m35_lexical_chars
cmp r3 r2
jge m35_numeral_match
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
jne m35_next_language
add r3 1
jmp m35_lexical_chars
label m35_numeral_match
mov r5 r9
add r5 1
load8 r6 $r5
cmp r11 0
je m35_first_numeral_match
cmp r4 r6
jne m35_unresolved
jmp m35_next_language
label m35_first_numeral_match
set r11 1
mov r4 r6
label m35_next_language
cmp r13 5
jne m35_next_numeral
set r13 14
jmp m35_each_language
label m35_next_numeral
add r8 1
jmp m35_each_numeral
label m35_learned_operator
cmp r11 1
je m35_resolved_number
load8 r7 7300000000000000004
cmp r7 32
jgt m35_invalid
set r8 0
label m35_each_operator
cmp r8 r7
jge m35_unresolved
set r9 7300000000000001000
mov r10 r8
mul r10 32
add r9 r10
load8 r10 $r9
cmp r10 r2
jne m35_next_operator
mov r5 r9
add r5 18
load8 r10 $r5
cmp r10 2
jlt m35_next_operator
set r3 0
label m35_operator_chars
cmp r3 r2
jge m35_operator_match
mov r5 r1
add r5 1
add r5 r3
load8 r6 $r5
mov r5 r9
add r5 1
add r5 r3
load8 r10 $r5
cmp r6 r10
jne m35_next_operator
add r3 1
jmp m35_operator_chars
label m35_operator_match
add r9 17
load8 r4 $r9
set r12 2
jmp m35_save_resolution
label m35_next_operator
add r8 1
jmp m35_each_operator
label m35_resolved_number
set r12 1
jmp m35_save_resolution
label m35_unresolved
# Optional E020 spellings refer to sealed, independently validated concepts.
# No mapping from a Spanish/English spelling to an arithmetic family here.
load8 r7 7900000000000000003
cmp r7 1
jne m35_no_scale_word
load8 r7 7900000000000000004
cmp r7 128
jgt m35_invalid
set r8 0
label m35_scale_operator
cmp r8 r7
jge m35_no_scale_word
set r9 7900000000000001000
mov r10 r8
mul r10 32
add r9 r10
load8 r10 $r9
cmp r10 r2
jne m35_next_scale_operator
set r3 0
label m35_scale_chars
cmp r3 r2
jge m35_scale_match
mov r5 r1
add r5 1
add r5 r3
load8 r6 $r5
mov r5 r9
add r5 1
add r5 r3
load8 r10 $r5
cmp r6 r10
jne m35_next_scale_operator
add r3 1
jmp m35_scale_chars
label m35_scale_match
add r9 17
load8 r4 $r9
cmp r4 1
jlt m35_invalid
cmp r4 8
jgt m35_invalid
sub r4 1
mul r4 64
set r9 7900000000000000130
add r9 r4
load8 r4 $r9
cmp r4 1
jlt m35_invalid
cmp r4 8
jgt m35_invalid
set r12 2
jmp m35_save_resolution
label m35_next_scale_operator
add r8 1
jmp m35_scale_operator
label m35_no_scale_word
set r12 0
set r4 0
label m35_save_resolution
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
jmp m35_each_token
label m35_done
jmp m36_entry
label m35_invalid
div r0 0
label m36_entry
# Reuse E011's exact arithmetic interpreter, using explicit resolved operands.
# No story arithmetic result is computed by this adapter.
load8 r0 7300000000000000800
cmp r0 1
jne m36_unknown
load8 r0 7300000000000000040
cmp r0 0
jne m36_unknown
load8 r2 7300000000000000801
load8 r3 7300000000000000802
load8 r4 7500000000000000036
cmp r4 1
je m36_ready
store8 7300000000000000808 1
store8 7300000000000000809 r2
store8 7300000000000000810 r3
store8 7300000000000000804 2
cmp r4 2
je m36_addition
store8 7300000000000000805 1
jmp m36_previous
label m36_addition
store8 7300000000000000805 2
label m36_previous
load8 r0 7500000000000000035
set r7 8600000000000020002
mul r0 8
add r7 r0
load8 r2 $r7
add r7 1
load8 r3 $r7
store8 7300000000000000800 1
store8 7300000000000000801 r2
store8 7300000000000000802 r3
store8 7300000000000000032 3
label m36_ready
jmp story_number_ready
label m36_unknown
store8 7500000000000000008 0
store8 7500000000000000009 1
store8 7500000000000000017 0
jmp story_number_ready
label story_number_ready
load8 r0 7500000000000000017
cmp r0 1
jne story_finish
label m37_entry
# Evaluate new compositions using ONLY grounded quantities and learned effects.
# Grammar: NUMBER (OP NUMBER)*; OP NUMBER... may continue the last valid turn.
# Designed left-to-right grammar, 0..65535 at EVERY step, max seven effects.
load8 r0 7300000000000000002
cmp r0 1
jne m37_invalid
load8 r0 7300000000000000016
cmp r0 1
jne m37_invalid
load8 r0 7300000000000000024
cmp r0 0
jne m37_invalid
set r14 0
set r13 0
set r11 0
load8 r0 7300000000000000040
cmp r0 0
jne m37_syntax_error
load8 r15 7300000000000000032
cmp r15 1
jlt m37_syntax_error
load8 r0 7300000000000000800
cmp r0 1
je m37_explicit_start
cmp r0 2
jne m37_unknown_word
load8 r0 7300000000000000005
cmp r0 1
jne m37_missing_context
load8 r2 7300000000000000006
load8 r3 7300000000000000007
mul r3 256
add r2 r3
set r1 0
jmp m37_apply_pairs
label m37_explicit_start
load8 r2 7300000000000000801
load8 r3 7300000000000000802
mul r3 256
add r2 r3
set r1 1
label m37_apply_pairs
cmp r1 r15
jge m37_supported
mov r0 r1
add r0 1
cmp r0 r15
jge m37_syntax_error
set r7 7300000000000000800
mov r8 r1
mul r8 4
add r7 r8
load8 r0 $r7
cmp r0 2
jne m37_unknown_word
add r7 1
load8 r4 $r7
add r7 3
load8 r0 $r7
cmp r0 1
jne m37_unknown_word
add r7 1
load8 r3 $r7
add r7 1
load8 r0 $r7
mul r0 256
add r3 r0
# Until a precedence grammar is implemented, do not silently evaluate a
# lower-priority sum/difference before a following product/division/remainder.
cmp r4 3
jlt m37_precedence_ready
cmp r4 5
jgt m37_precedence_ready
cmp r11 1
je m37_syntax_error
label m37_precedence_ready
cmp r4 1
je m37_subtract
cmp r4 2
je m37_add
cmp r4 3
je m37_multiply
cmp r4 4
je m37_exact_divide
cmp r4 5
je m37_remainder
cmp r4 6
je m37_minimum
cmp r4 7
je m37_maximum
cmp r4 8
jne m37_unknown_word
sub r2 r3
cmp r2 0
jge m37_check_bounds
mul r2 -1
jmp m37_check_bounds
label m37_add
set r11 1
add r2 r3
jmp m37_check_bounds
label m37_subtract
set r11 1
sub r2 r3
jmp m37_check_bounds
label m37_multiply
mul r2 r3
jmp m37_check_bounds
label m37_exact_divide
cmp r3 0
je m37_range_error
mov r0 r2
mod r0 r3
cmp r0 0
jne m37_range_error
div r2 r3
jmp m37_check_bounds
label m37_remainder
cmp r3 0
je m37_range_error
mod r2 r3
jmp m37_check_bounds
label m37_minimum
cmp r2 r3
jle m37_check_bounds
mov r2 r3
jmp m37_check_bounds
label m37_maximum
cmp r2 r3
jge m37_check_bounds
mov r2 r3
label m37_check_bounds
cmp r2 0
jlt m37_range_error
cmp r2 65535
jgt m37_range_error
add r13 1
add r1 2
jmp m37_apply_pairs
label m37_supported
store8 7300000000000000005 1
store8 7300000000000000008 1
store8 7300000000000000009 0
store8 7300000000000000012 r13
mov r3 r2
mod r3 256
store8 7300000000000000006 r3
store8 7300000000000000010 r3
div r2 256
store8 7300000000000000007 r2
store8 7300000000000000011 r2
jmp m37_clean
label m37_unknown_word
set r14 1
jmp m37_abstain
label m37_syntax_error
set r14 2
jmp m37_abstain
label m37_missing_context
set r14 3
jmp m37_abstain
label m37_range_error
set r14 4
label m37_abstain
# Failed turns invalidate context: never silently reuse a stale answer.
store8 7300000000000000005 0
store8 7300000000000000006 0
store8 7300000000000000007 0
store8 7300000000000000008 0
store8 7300000000000000009 r14
store8 7300000000000000010 0
store8 7300000000000000011 0
store8 7300000000000000012 0
label m37_clean
set r0 16
label m37_clear_query
set r7 7300000000000000000
add r7 r0
store8 $r7 0
add r0 1
cmp r0 864
jlt m37_clear_query
load8 r10 7300000000000000008
print r10
load8 r11 7300000000000000009
print r11
jmp m38_entry
label m37_invalid
div r0 0
label m38_entry
# Only a supported E011 result can enter this turn's private episode ledger.
load8 r0 7300000000000000008
cmp r0 1
jne m38_range_error
load8 r0 7500000000000000035
set r7 8600000000000020000
mov r1 r0
mul r1 8
add r7 r1
load8 r2 7500000000000000039
load8 r3 7500000000000000040
load8 r4 7300000000000000010
load8 r5 7300000000000000011
store8 $r7 r2
add r7 1
store8 $r7 r3
add r7 1
store8 $r7 r4
add r7 1
store8 $r7 r5
load8 r1 7500000000000000032
cmp r0 r1
jne m38_count_ready
add r1 1
store8 7500000000000000032 r1
label m38_count_ready
store8 7500000000000000010 r2
store8 7500000000000000011 r3
store8 7500000000000000012 r4
store8 7500000000000000013 r5
load8 r0 7500000000000000014
add r0 1
store8 7500000000000000014 r0
load8 r0 7500000000000000038
store8 7500000000000000033 r0
store8 7500000000000000034 r2
jmp story_parse
label m38_range_error
store8 7500000000000000008 0
store8 7500000000000000009 4
store8 7500000000000000017 0
jmp story_parse
label story_finish
label m39_entry
# Publish all episode changes together, or none. Use E011's original speaker.
load8 r0 7500000000000000008
store8 7400000000000000008 r0
load8 r1 7500000000000000009
store8 7400000000000000009 r1
cmp r0 1
jne m39_failure_result
load8 r0 7500000000000000014
cmp r0 0
je m39_response
set r0 0
label m39_commit
set r7 8600000000000020000
add r7 r0
load8 r1 $r7
set r7 8600000000000010000
add r7 r0
store8 $r7 r1
add r0 1
cmp r0 512
jlt m39_commit
load8 r0 7500000000000000032
store8 7500000000000000006 r0
jmp m39_response
label m39_failure_result
set r0 10
label m39_clear_result
set r7 7500000000000000000
add r7 r0
store8 $r7 0
add r0 1
cmp r0 16
jlt m39_clear_result
label m39_response
load8 r0 7400000000000000003
store8 7300000000000000003 r0
load8 r0 7500000000000000008
store8 7300000000000000008 r0
load8 r0 7500000000000000012
store8 7300000000000000010 r0
load8 r0 7500000000000000013
store8 7300000000000000011 r0
jmp story_reply
label story_reply
load8 r0 7700000000000000016
cmp r0 1
je conversation_story
label m40_entry
# Read-only response: learned ES/EN number names, otherwise composed digits.
load8 r0 7300000000000000002
cmp r0 1
jne m40_invalid
load8 r0 7300000000000000008
cmp r0 1
je m40_supported
set r14 63
print r14
jmp story_clean
label m40_supported
load8 r2 7300000000000000010
load8 r0 7300000000000000011
mul r0 256
add r2 r0
load8 r15 7300000000000000003
cmp r15 1
je m40_language_ready
cmp r15 2
jne m40_invalid
label m40_language_ready
load8 r7 7200000000000000010
set r0 0
label m40_find_learned_name
cmp r0 r7
jge m40_decimal_output
set r8 7200000000000001000
mov r9 r0
mul r9 32
add r8 r9
load8 r9 $r8
cmp r9 4
jne m40_next_numeral
mov r9 r8
add r9 1
load8 r9 $r9
cmp r9 r2
jne m40_next_numeral
mov r9 r8
add r9 4
load8 r9 $r9
cmp r9 2
jlt m40_next_numeral
set r5 5
cmp r15 1
je m40_select_label
set r5 14
label m40_select_label
add r8 r5
load8 r6 $r8
cmp r6 1
jlt m40_invalid
cmp r6 8
jgt m40_invalid
set r1 0
label m40_emit_label
cmp r1 r6
jge m40_done
mov r9 r8
add r9 1
add r9 r1
load8 r14 $r9
print r14
add r1 1
jmp m40_emit_label
label m40_next_numeral
add r0 1
jmp m40_find_learned_name
label m40_decimal_output
set r3 10000
set r4 0
label m40_decimal_digit
mov r14 r2
div r14 r3
mod r2 r3
cmp r14 0
jne m40_nonzero_digit
cmp r4 1
je m40_print_digit
cmp r3 1
je m40_print_digit
jmp m40_next_place
label m40_nonzero_digit
set r4 1
label m40_print_digit
add r14 48
print r14
label m40_next_place
div r3 10
cmp r3 0
jgt m40_decimal_digit
label m40_done
jmp story_clean
label m40_invalid
div r0 0
label story_clean
label m41_entry
# Restore the pre-turn E011 arithmetic context, including after any abstention.
set r0 0
label m41_restore_arithmetic
set r7 7500000000000002200
add r7 r0
load8 r1 $r7
store8 $r7 0
set r7 7300000000000000000
add r7 r0
store8 $r7 r1
add r0 1
cmp r0 16
jlt m41_restore_arithmetic
set r0 16
label m41_arithmetic_scratch
set r7 7300000000000000000
add r7 r0
store8 $r7 0
add r0 1
cmp r0 64
jlt m41_arithmetic_scratch
set r0 512
label m41_arithmetic_token
set r7 7300000000000000000
add r7 r0
store8 $r7 0
add r0 1
cmp r0 530
jlt m41_arithmetic_token
set r0 800
label m41_arithmetic_resolved
set r7 7300000000000000000
add r7 r0
store8 $r7 0
add r0 1
cmp r0 812
jlt m41_arithmetic_resolved
set r0 16
label m41_control
set r7 7500000000000000000
add r7 r0
store8 $r7 0
add r0 1
cmp r0 64
jlt m41_control
set r0 0
label m41_staging
set r7 8600000000000020000
add r7 r0
store8 $r7 0
add r0 1
cmp r0 512
jlt m41_staging
jmp cleanup
label conversation_story
store8 7700000000000000025 1
label m42_entry
# 7700000000000000025 is set by native source linkage: 0 act,1 story,2 fact,3 arithmetic.
# Successful semantic results update small persistent discourse descriptors.
store8 7700000000000000032 0
store8 7700000000000000033 0
store8 7700000000000000034 0
store8 7700000000000000039 0
store8 7700000000000000038 1
load8 r0 7700000000000000017
cmp r0 0
jne m42_act
load8 r0 7700000000000000025
cmp r0 1
je m42_story
cmp r0 2
je m42_factual
cmp r0 3
jne m42_invalid
load8 r0 7300000000000000008
cmp r0 1
jne m42_unknown
store8 7700000000000000010 0
store8 7700000000000000018 3
store8 7700000000000000019 5
jmp conversation_render
label m42_story
load8 r0 7500000000000000008
cmp r0 1
jne m42_unknown
store8 7700000000000000004 1
load8 r0 7500000000000000010
store8 7700000000000000005 r0
load8 r0 7500000000000000011
store8 7700000000000000006 r0
store8 7700000000000000010 1
# A grammatical count sentence requires a learned order and noun inflection.
load8 r1 7400000000000000003
set r7 7700000000000001001
sub r1 1
mul r1 32
add r7 r1
load8 r0 $r7
cmp r0 2
jne m42_count_fallback
load8 r0 7500000000000000011
mul r0 224
set r7 7700000000000100000
add r7 r0
load8 r1 7400000000000000003
sub r1 1
mul r1 112
add r7 r1
load8 r0 7500000000000000012
load8 r1 7500000000000000013
cmp r1 0
jne m42_plural
cmp r0 1
jne m42_plural
load8 r0 $r7
cmp r0 0
je m42_count_fallback
add r7 34
load8 r0 $r7
cmp r0 0
je m42_count_fallback
jmp m42_count_ready
label m42_plural
add r7 101
load8 r0 $r7
cmp r0 3
jne m42_count_fallback
sub r7 33
load8 r0 $r7
cmp r0 0
je m42_count_fallback
label m42_count_ready
store8 7700000000000000018 2
jmp conversation_render
label m42_count_fallback
store8 7700000000000000018 3
store8 7700000000000000019 6
jmp conversation_render
label m42_factual
load8 r0 7400000000000000008
cmp r0 1
je m42_fact_ready
cmp r0 2
jne m42_unknown
label m42_fact_ready
store8 7700000000000000007 1
load8 r0 7400000000000000010
store8 7700000000000000008 r0
load8 r0 7400000000000000011
store8 7700000000000000009 r0
store8 7700000000000000010 2
store8 7700000000000000018 4
jmp conversation_render
label m42_unknown
set r0 3
label m42_act
store8 7700000000000000018 1
store8 7700000000000000019 r0
cmp r0 3
jlt m42_done
cmp r0 8
je m42_done
store8 7700000000000000010 0
label m42_done
jmp conversation_render
label m42_invalid
div r0 0
label knowledge
label m43_entry
# Recheck current facts at inference time. Stale/contradicted witnesses cannot
# preserve a rule. At least TWO different positive closures and zero negatives.
load8 r5 7400000000000000011
set r11 7400000000000050000
mov r0 r5
mul r0 40
add r11 r0
load8 r15 $r11
cmp r15 8
jgt m43_invalid
set r0 0
set r6 0
set r12 0
label m43_witness
cmp r0 r15
jge m43_finish
mov r7 r11
add r7 1
mov r1 r0
mul r1 3
add r7 r1
load8 r2 $r7
add r7 1
load8 r3 $r7
add r7 1
load8 r4 $r7
mov r7 r2
mul r7 256
add r7 r5
mul r7 256
add r7 r3
mul r7 4
add r7 7400000000001000000
load8 r8 $r7
add r7 1
load8 r9 $r7
set r10 0
cmp r8 0
je m43_ab_no_positive
set r10 1
label m43_ab_no_positive
cmp r9 0
je m43_ab_done
add r10 2
label m43_ab_done

cmp r10 1
jne m43_next
mov r7 r3
mul r7 256
add r7 r5
mul r7 256
add r7 r4
mul r7 4
add r7 7400000000001000000
load8 r8 $r7
add r7 1
load8 r9 $r7
set r10 0
cmp r8 0
je m43_bc_no_positive
set r10 1
label m43_bc_no_positive
cmp r9 0
je m43_bc_done
add r10 2
label m43_bc_done

cmp r10 1
jne m43_next
mov r7 r2
mul r7 256
add r7 r5
mul r7 256
add r7 r4
mul r7 4
add r7 7400000000001000000
load8 r8 $r7
add r7 1
load8 r9 $r7
set r10 0
cmp r8 0
je m43_ac_no_positive
set r10 1
label m43_ac_no_positive
cmp r9 0
je m43_ac_done
add r10 2
label m43_ac_done

cmp r10 1
je m43_positive
cmp r10 0
je m43_next
# Negative or conflicted closure blocks this empirical generalization.
set r12 1
jmp m43_next
label m43_positive
add r6 1
label m43_next
add r0 1
jmp m43_witness
label m43_finish
store8 7400000000000000041 0
cmp r12 0
jne m43_done
cmp r6 2
jlt m43_done
store8 7400000000000000041 1
label m43_done
jmp m44_entry
label m43_invalid
div r0 0
label m44_entry
# Open-world reasoning: missing data is UNKNOWN, not false.
# Negative and conflicted direct evidence block hypothetical composition.
load8 r0 7400000000000000009
cmp r0 0
jne m44_done
load8 r2 7400000000000000010
load8 r3 7400000000000000011
load8 r4 7400000000000000012
load8 r0 7400000000000000013
cmp r0 2
je m44_objects
mov r7 r2
mul r7 256
add r7 r3
mul r7 256
add r7 r4
mul r7 4
add r7 7400000000001000000
load8 r8 $r7
add r7 1
load8 r9 $r7
set r10 0
cmp r8 0
je m44_direct_no_positive
set r10 1
label m44_direct_no_positive
cmp r9 0
je m44_direct_done
add r10 2
label m44_direct_done

cmp r10 1
je m44_direct_yes
cmp r10 2
je m44_direct_no
cmp r10 3
je m44_conflict
load8 r0 7400000000000000041
cmp r0 1
jne m44_no_proof
# Sparse keyed edges; bounded native BFS supports multi-hop paths and cycles.
set r7 7400000000000003400
add r7 r2
store8 $r7 1
store8 7400000000000003000 r2
store8 7400000000000000050 1
set r0 0
set r1 1
label m44_breadth_first
cmp r0 r1
jge m44_no_proof
cmp r0 64
jge m44_budget
set r7 7400000000000003000
add r7 r0
load8 r5 $r7
set r6 1
label m44_candidate
cmp r6 255
jgt m44_next_node
mov r7 r5
mul r7 256
add r7 r3
mul r7 256
add r7 r6
mul r7 4
add r7 7400000000001000000
load8 r8 $r7
add r7 1
load8 r9 $r7
set r10 0
cmp r8 0
je m44_edge_no_positive
set r10 1
label m44_edge_no_positive
cmp r9 0
je m44_edge_done
add r10 2
label m44_edge_done

cmp r10 1
jne m44_next_candidate
set r7 7400000000000003400
add r7 r6
load8 r8 $r7
cmp r8 0
jne m44_next_candidate
set r7 7400000000000004200
add r7 r5
load8 r8 $r7
add r8 1
cmp r8 31
jgt m44_next_candidate
cmp r1 255
jge m44_budget
set r7 7400000000000003400
add r7 r6
store8 $r7 1
set r7 7400000000000003800
add r7 r6
store8 $r7 r5
set r7 7400000000000004200
add r7 r6
store8 $r7 r8
set r7 7400000000000003000
add r7 r1
store8 $r7 r6
add r1 1
store8 7400000000000000050 r1
cmp r6 r4
je m44_path_found
label m44_next_candidate
add r6 1
jmp m44_candidate
label m44_next_node
add r0 1
jmp m44_breadth_first
label m44_path_found
store8 7400000000000000015 r8
mov r5 r4
set r0 0
label m44_reconstruct
cmp r0 32
jge m44_budget
set r7 7400000000000002200
add r7 r0
store8 $r7 r5
cmp r5 r2
je m44_direct_yes
set r7 7400000000000003800
add r7 r5
load8 r5 $r7
cmp r5 0
je m44_budget
add r0 1
jmp m44_reconstruct
label m44_direct_yes
store8 7400000000000000008 1
store8 7400000000000000014 1
store8 7400000000000002100 r4
load8 r0 7400000000000000015
cmp r0 0
jne m44_done
store8 7400000000000000015 1
jmp knowledge_reply
label m44_direct_no
store8 7400000000000000008 2
store8 7400000000000000014 1
store8 7400000000000002100 r4
store8 7400000000000000015 1
jmp knowledge_reply
label m44_conflict
store8 7400000000000000008 0
store8 7400000000000000009 4
jmp knowledge_reply
label m44_objects
# What-questions list directly taught objects, not every abstract ancestor.
set r4 1
set r0 0
label m44_object_candidate
cmp r4 255
jgt m44_object_done
mov r7 r2
mul r7 256
add r7 r3
mul r7 256
add r7 r4
mul r7 4
add r7 7400000000001000000
load8 r8 $r7
add r7 1
load8 r9 $r7
set r10 0
cmp r8 0
je m44_obj_no_positive
set r10 1
label m44_obj_no_positive
cmp r9 0
je m44_obj_done
add r10 2
label m44_obj_done

cmp r10 1
jne m44_next_object
cmp r0 8
jge m44_truncated
set r7 7400000000000002100
add r7 r0
store8 $r7 r4
add r0 1
jmp m44_next_object
label m44_truncated
store8 7400000000000000042 1
label m44_next_object
add r4 1
jmp m44_object_candidate
label m44_object_done
cmp r0 0
je m44_no_proof
store8 7400000000000000008 1
store8 7400000000000000014 r0
jmp knowledge_reply
label m44_no_proof
store8 7400000000000000009 3
jmp knowledge_reply
label m44_budget
store8 7400000000000000008 0
store8 7400000000000000009 5
jmp knowledge_reply
label m44_done
jmp knowledge_reply
label knowledge_reply
load8 r0 7700000000000000016
cmp r0 1
je conversation_fact
label m45_entry
# All content words come from the learned bilingual lexicon. No ready answers.
# Render factual triples and, for inference, the actual parent chain from BFS.
load8 r0 7400000000000000008
cmp r0 0
jne m45_supported
set r14 63
print r14
jmp cleanup
label m45_supported
cmp r0 2
jne m45_begin_response
set r14 110
print r14
set r14 111
print r14
set r14 58
print r14
set r14 32
print r14
label m45_begin_response
set r0 0
set r1 0
set r12 0
label m45_choose_word
cmp r12 1
je m45_proof_word
cmp r1 0
je m45_subject_word
cmp r1 1
je m45_predicate_word
set r7 7400000000000002100
add r7 r0
load8 r2 $r7
jmp m45_emit_word
label m45_subject_word
load8 r2 7400000000000000010
jmp m45_emit_word
label m45_predicate_word
load8 r2 7400000000000000011
jmp m45_emit_word
label m45_proof_word
set r7 7400000000000002200
add r7 r1
load8 r2 $r7
label m45_emit_word
load8 r15 7400000000000000003
cmp r2 22
jgt m45_new_name
set r7 7200000000000001000
mov r3 r2
sub r3 1
mul r3 32
add r7 r3
set r3 5
cmp r15 1
je m45_old_name
set r3 14
label m45_old_name
add r7 r3
load8 r6 $r7
add r7 1
jmp m45_letters_start
label m45_new_name
load8 r10 7400000000000000004
load8 r3 7400000000000000005
mul r3 256
add r10 r3
set r3 0
label m45_lexeme
cmp r3 r10
jge m45_invalid
set r7 7400000000000010000
mov r4 r3
mul r4 40
add r7 r4
load8 r4 $r7
cmp r4 r2
jne m45_next_lexeme
mov r4 r7
add r4 2
load8 r5 $r4
cmp r5 r15
jne m45_next_lexeme
add r7 3
load8 r6 $r7
add r7 1
jmp m45_letters_start
label m45_next_lexeme
add r3 1
jmp m45_lexeme
label m45_letters_start
cmp r6 1
jlt m45_invalid
cmp r6 32
jgt m45_invalid
set r3 0
label m45_letter
cmp r3 r6
jge m45_word_done
mov r4 r7
add r4 r3
load8 r14 $r4
print r14
add r3 1
jmp m45_letter
label m45_word_done
cmp r12 1
je m45_after_proof_word
add r1 1
cmp r1 3
jge m45_triple_done
set r14 32
print r14
jmp m45_choose_word
label m45_triple_done
add r0 1
load8 r4 7400000000000000014
cmp r0 r4
jge m45_response_done
set r14 59
print r14
set r14 32
print r14
set r1 0
jmp m45_choose_word
label m45_response_done
set r14 46
print r14
load8 r1 7400000000000000015
cmp r1 2
jlt m45_done
set r14 32
print r14
set r14 91
print r14
set r12 1
jmp m45_choose_word
label m45_after_proof_word
cmp r1 0
je m45_proof_done
set r14 32
print r14
set r14 45
print r14
set r14 62
print r14
set r14 32
print r14
sub r1 1
jmp m45_choose_word
label m45_proof_done
set r14 93
print r14
label m45_done
jmp cleanup
label m45_invalid
div r0 0
label conversation_fact
store8 7700000000000000025 2
label m46_entry
# 7700000000000000025 is set by native source linkage: 0 act,1 story,2 fact,3 arithmetic.
# Successful semantic results update small persistent discourse descriptors.
store8 7700000000000000032 0
store8 7700000000000000033 0
store8 7700000000000000034 0
store8 7700000000000000039 0
store8 7700000000000000038 1
load8 r0 7700000000000000017
cmp r0 0
jne m46_act
load8 r0 7700000000000000025
cmp r0 1
je m46_story
cmp r0 2
je m46_factual
cmp r0 3
jne m46_invalid
load8 r0 7300000000000000008
cmp r0 1
jne m46_unknown
store8 7700000000000000010 0
store8 7700000000000000018 3
store8 7700000000000000019 5
jmp conversation_render
label m46_story
load8 r0 7500000000000000008
cmp r0 1
jne m46_unknown
store8 7700000000000000004 1
load8 r0 7500000000000000010
store8 7700000000000000005 r0
load8 r0 7500000000000000011
store8 7700000000000000006 r0
store8 7700000000000000010 1
# A grammatical count sentence requires a learned order and noun inflection.
load8 r1 7400000000000000003
set r7 7700000000000001001
sub r1 1
mul r1 32
add r7 r1
load8 r0 $r7
cmp r0 2
jne m46_count_fallback
load8 r0 7500000000000000011
mul r0 224
set r7 7700000000000100000
add r7 r0
load8 r1 7400000000000000003
sub r1 1
mul r1 112
add r7 r1
load8 r0 7500000000000000012
load8 r1 7500000000000000013
cmp r1 0
jne m46_plural
cmp r0 1
jne m46_plural
load8 r0 $r7
cmp r0 0
je m46_count_fallback
add r7 34
load8 r0 $r7
cmp r0 0
je m46_count_fallback
jmp m46_count_ready
label m46_plural
add r7 101
load8 r0 $r7
cmp r0 3
jne m46_count_fallback
sub r7 33
load8 r0 $r7
cmp r0 0
je m46_count_fallback
label m46_count_ready
store8 7700000000000000018 2
jmp conversation_render
label m46_count_fallback
store8 7700000000000000018 3
store8 7700000000000000019 6
jmp conversation_render
label m46_factual
load8 r0 7400000000000000008
cmp r0 1
je m46_fact_ready
cmp r0 2
jne m46_unknown
label m46_fact_ready
store8 7700000000000000007 1
load8 r0 7400000000000000010
store8 7700000000000000008 r0
load8 r0 7400000000000000011
store8 7700000000000000009 r0
store8 7700000000000000010 2
store8 7700000000000000018 4
jmp conversation_render
label m46_unknown
set r0 3
label m46_act
store8 7700000000000000018 1
store8 7700000000000000019 r0
cmp r0 3
jlt m46_done
cmp r0 8
je m46_done
store8 7700000000000000010 0
label m46_done
jmp conversation_render
label m46_invalid
div r0 0
label conversation_shortcut
store8 7700000000000000025 0
label m47_entry
# 7700000000000000025 is set by native source linkage: 0 act,1 story,2 fact,3 arithmetic.
# Successful semantic results update small persistent discourse descriptors.
store8 7700000000000000032 0
store8 7700000000000000033 0
store8 7700000000000000034 0
store8 7700000000000000039 0
store8 7700000000000000038 1
load8 r0 7700000000000000017
cmp r0 0
jne m47_act
load8 r0 7700000000000000025
cmp r0 1
je m47_story
cmp r0 2
je m47_factual
cmp r0 3
jne m47_invalid
load8 r0 7300000000000000008
cmp r0 1
jne m47_unknown
store8 7700000000000000010 0
store8 7700000000000000018 3
store8 7700000000000000019 5
jmp conversation_render
label m47_story
load8 r0 7500000000000000008
cmp r0 1
jne m47_unknown
store8 7700000000000000004 1
load8 r0 7500000000000000010
store8 7700000000000000005 r0
load8 r0 7500000000000000011
store8 7700000000000000006 r0
store8 7700000000000000010 1
# A grammatical count sentence requires a learned order and noun inflection.
load8 r1 7400000000000000003
set r7 7700000000000001001
sub r1 1
mul r1 32
add r7 r1
load8 r0 $r7
cmp r0 2
jne m47_count_fallback
load8 r0 7500000000000000011
mul r0 224
set r7 7700000000000100000
add r7 r0
load8 r1 7400000000000000003
sub r1 1
mul r1 112
add r7 r1
load8 r0 7500000000000000012
load8 r1 7500000000000000013
cmp r1 0
jne m47_plural
cmp r0 1
jne m47_plural
load8 r0 $r7
cmp r0 0
je m47_count_fallback
add r7 34
load8 r0 $r7
cmp r0 0
je m47_count_fallback
jmp m47_count_ready
label m47_plural
add r7 101
load8 r0 $r7
cmp r0 3
jne m47_count_fallback
sub r7 33
load8 r0 $r7
cmp r0 0
je m47_count_fallback
label m47_count_ready
store8 7700000000000000018 2
jmp conversation_render
label m47_count_fallback
store8 7700000000000000018 3
store8 7700000000000000019 6
jmp conversation_render
label m47_factual
load8 r0 7400000000000000008
cmp r0 1
je m47_fact_ready
cmp r0 2
jne m47_unknown
label m47_fact_ready
store8 7700000000000000007 1
load8 r0 7400000000000000010
store8 7700000000000000008 r0
load8 r0 7400000000000000011
store8 7700000000000000009 r0
store8 7700000000000000010 2
store8 7700000000000000018 4
jmp conversation_render
label m47_unknown
set r0 3
label m47_act
store8 7700000000000000018 1
store8 7700000000000000019 r0
cmp r0 3
jlt m47_done
cmp r0 8
je m47_done
store8 7700000000000000010 0
label m47_done
jmp conversation_render
label m47_invalid
div r0 0
label conversation_render
load8 r0 7700000000000000018
cmp r0 2
je conversation_count
cmp r0 3
je conversation_number
cmp r0 4
je conversation_fact_start
label m48_entry
# Select a teacher-supplied dialogue act; renderer gets only bytes in RVPC2.
load8 r0 7700000000000000019
cmp r0 1
jlt m48_invalid
cmp r0 8
jgt m48_invalid
load8 r1 7400000000000000003
set r7 7700000000000002000
sub r0 1
mul r0 512
add r7 r0
sub r1 1
mul r1 256
add r7 r1
load8 r6 $r7
cmp r6 1
jlt m48_invalid
add r7 1
set r13 0
jmp m49_entry
label m48_invalid
div r0 0
label m49_entry
# Print selected memory bytes, including Spanish UTF-8 initial capitalization.
# No words, facts or response choice in the transport.
cmp r6 1
jlt m49_invalid
cmp r6 255
jgt m49_invalid
load8 r0 7700000000000000039
cmp r0 1
jne m49_begin
set r14 32
print r14
label m49_begin
set r3 0
label m49_letter
cmp r3 r6
jge m49_done
mov r4 r7
add r4 r3
load8 r14 $r4
cmp r14 95
jne m49_case_check
set r14 32
label m49_case_check
cmp r13 0
je m49_print_byte
cmp r14 195
je m49_print_byte
cmp r3 0
jne m49_latin_initial
cmp r14 97
jlt m49_case_done
cmp r14 122
jgt m49_case_done
sub r14 32
jmp m49_case_done
label m49_latin_initial
cmp r3 1
jne m49_case_done
load8 r0 $r7
cmp r0 195
jne m49_case_done
cmp r14 160
jlt m49_case_done
cmp r14 191
jgt m49_case_done
cmp r14 183
je m49_case_done
sub r14 32
label m49_case_done
set r13 0
label m49_print_byte
print r14
add r3 1
jmp m49_letter
label m49_done
store8 7700000000000000039 1
store8 7700000000000000038 0
jmp conversation_done
label m49_invalid
div r0 0
label conversation_count
label m50_entry
# Follow the learned ordering of actor/assignment verb/quantity/item.
# +35 action: 1 shared name,2 direct bytes,3 decimal via E011,4 done.
load8 r0 7700000000000000032
cmp r0 4
jge m50_done
load8 r1 7400000000000000003
set r7 7700000000000001008
sub r1 1
mul r1 32
add r7 r1
add r7 r0
load8 r2 $r7
add r0 1
store8 7700000000000000032 r0
store8 7700000000000000038 0
cmp r0 1
jne m50_role
store8 7700000000000000038 1
label m50_role
cmp r2 1
je m50_actor
cmp r2 2
je m50_verb
cmp r2 3
je m50_quantity
cmp r2 4
jne m50_invalid
load8 r0 7500000000000000011
set r7 7700000000000100000
mul r0 224
add r7 r0
load8 r1 7400000000000000003
sub r1 1
mul r1 112
add r7 r1
load8 r0 7500000000000000012
load8 r1 7500000000000000013
cmp r1 0
jne m50_plural
cmp r0 1
jne m50_plural
add r7 34
jmp m50_direct
label m50_plural
add r7 68
jmp m50_direct
label m50_actor
load8 r0 7500000000000000010
jmp m50_name
label m50_verb
load8 r0 7700000000000000529
jmp m50_name
label m50_quantity
load8 r0 7500000000000000012
load8 r1 7500000000000000013
cmp r1 0
jne m50_decimal
cmp r0 1
je m50_one
cmp r0 9
jgt m50_decimal
add r0 13
jmp m50_name
label m50_one
load8 r0 7500000000000000011
set r7 7700000000000100000
mul r0 224
add r7 r0
load8 r1 7400000000000000003
sub r1 1
mul r1 112
add r7 r1
label m50_direct
load8 r6 $r7
add r7 1
load8 r13 7700000000000000038
store8 7700000000000000035 2
jmp conversation_count_dispatch
label m50_name
store8 7700000000000000040 r0
store8 7700000000000000035 1
jmp conversation_count_dispatch
label m50_decimal
load8 r0 7700000000000000039
cmp r0 0
je m50_decimal_ready
set r14 32
print r14
label m50_decimal_ready
store8 7700000000000000039 1
store8 7700000000000000035 3
jmp conversation_count_dispatch
label m50_done
set r14 46
print r14
store8 7700000000000000035 4
jmp conversation_count_dispatch
label m50_invalid
div r0 0
label conversation_count_dispatch
load8 r0 7700000000000000035
cmp r0 1
je conversation_count_name
cmp r0 2
je conversation_count_direct
cmp r0 3
je conversation_count_decimal
jmp conversation_done
label conversation_count_name
label m51_entry
# Resolve 7700000000000000040 to an existing shared bilingual name. r7=bytes,r6=len,r13=case.
load8 r2 7700000000000000040
cmp r2 0
je m51_invalid
load8 r13 7700000000000000038
set r7 7700000000000010000
mov r0 r2
mul r0 4
add r7 r0
load8 r0 $r7
cmp r0 1
jne m51_language
set r13 1
label m51_language
load8 r15 7400000000000000003
cmp r2 22
jgt m51_new_name
set r7 7200000000000001000
mov r3 r2
sub r3 1
mul r3 32
add r7 r3
set r3 5
cmp r15 1
je m51_old_name
set r3 14
label m51_old_name
add r7 r3
load8 r6 $r7
add r7 1
jmp conversation_count_direct
label m51_new_name
load8 r10 7400000000000000004
load8 r3 7400000000000000005
mul r3 256
add r10 r3
set r3 0
label m51_lexeme
cmp r3 r10
jge m51_invalid
set r7 7400000000000010000
mov r4 r3
mul r4 40
add r7 r4
load8 r4 $r7
cmp r4 r2
jne m51_next_lexeme
mov r4 r7
add r4 2
load8 r5 $r4
cmp r5 r15
jne m51_next_lexeme
add r7 3
load8 r6 $r7
add r7 1
jmp conversation_count_direct
label m51_next_lexeme
add r3 1
jmp m51_lexeme
label m51_invalid
div r0 0
label conversation_count_direct
label m52_entry
# Print selected memory bytes, including Spanish UTF-8 initial capitalization.
# No words, facts or response choice in the transport.
cmp r6 1
jlt m52_invalid
cmp r6 255
jgt m52_invalid
load8 r0 7700000000000000039
cmp r0 1
jne m52_begin
set r14 32
print r14
label m52_begin
set r3 0
label m52_letter
cmp r3 r6
jge m52_done
mov r4 r7
add r4 r3
load8 r14 $r4
cmp r14 95
jne m52_case_check
set r14 32
label m52_case_check
cmp r13 0
je m52_print_byte
cmp r14 195
je m52_print_byte
cmp r3 0
jne m52_latin_initial
cmp r14 97
jlt m52_case_done
cmp r14 122
jgt m52_case_done
sub r14 32
jmp m52_case_done
label m52_latin_initial
cmp r3 1
jne m52_case_done
load8 r0 $r7
cmp r0 195
jne m52_case_done
cmp r14 160
jlt m52_case_done
cmp r14 191
jgt m52_case_done
cmp r14 183
je m52_case_done
sub r14 32
label m52_case_done
set r13 0
label m52_print_byte
print r14
add r3 1
jmp m52_letter
label m52_done
store8 7700000000000000039 1
store8 7700000000000000038 0
jmp conversation_count
label m52_invalid
div r0 0
label conversation_count_decimal
label m53_entry
# Read-only response: learned ES/EN number names, otherwise composed digits.
load8 r0 7300000000000000002
cmp r0 1
jne m53_invalid
load8 r0 7300000000000000008
cmp r0 1
je m53_supported
set r14 63
print r14
jmp conversation_count
label m53_supported
load8 r2 7300000000000000010
load8 r0 7300000000000000011
mul r0 256
add r2 r0
load8 r15 7300000000000000003
cmp r15 1
je m53_language_ready
cmp r15 2
jne m53_invalid
label m53_language_ready
load8 r7 7200000000000000010
set r0 0
label m53_find_learned_name
cmp r0 r7
jge m53_decimal_output
set r8 7200000000000001000
mov r9 r0
mul r9 32
add r8 r9
load8 r9 $r8
cmp r9 4
jne m53_next_numeral
mov r9 r8
add r9 1
load8 r9 $r9
cmp r9 r2
jne m53_next_numeral
mov r9 r8
add r9 4
load8 r9 $r9
cmp r9 2
jlt m53_next_numeral
set r5 5
cmp r15 1
je m53_select_label
set r5 14
label m53_select_label
add r8 r5
load8 r6 $r8
cmp r6 1
jlt m53_invalid
cmp r6 8
jgt m53_invalid
set r1 0
label m53_emit_label
cmp r1 r6
jge m53_done
mov r9 r8
add r9 1
add r9 r1
load8 r14 $r9
print r14
add r1 1
jmp m53_emit_label
label m53_next_numeral
add r0 1
jmp m53_find_learned_name
label m53_decimal_output
set r3 10000
set r4 0
label m53_decimal_digit
mov r14 r2
div r14 r3
mod r2 r3
cmp r14 0
jne m53_nonzero_digit
cmp r4 1
je m53_print_digit
cmp r3 1
je m53_print_digit
jmp m53_next_place
label m53_nonzero_digit
set r4 1
label m53_print_digit
add r14 48
print r14
label m53_next_place
div r3 10
cmp r3 0
jgt m53_decimal_digit
label m53_done
jmp conversation_count
label m53_invalid
div r0 0
label conversation_number
label m54_entry
# Select a teacher-supplied dialogue act; renderer gets only bytes in RVPC2.
load8 r0 7700000000000000019
cmp r0 1
jlt m54_invalid
cmp r0 8
jgt m54_invalid
load8 r1 7400000000000000003
set r7 7700000000000002000
sub r0 1
mul r0 512
add r7 r0
sub r1 1
mul r1 256
add r7 r1
load8 r6 $r7
cmp r6 1
jlt m54_invalid
add r7 1
set r13 0
jmp m55_entry
label m54_invalid
div r0 0
label m55_entry
# Print selected memory bytes, including Spanish UTF-8 initial capitalization.
# No words, facts or response choice in the transport.
cmp r6 1
jlt m55_invalid
cmp r6 255
jgt m55_invalid
load8 r0 7700000000000000039
cmp r0 1
jne m55_begin
set r14 32
print r14
label m55_begin
set r3 0
label m55_letter
cmp r3 r6
jge m55_done
mov r4 r7
add r4 r3
load8 r14 $r4
cmp r14 95
jne m55_case_check
set r14 32
label m55_case_check
cmp r13 0
je m55_print_byte
cmp r14 195
je m55_print_byte
cmp r3 0
jne m55_latin_initial
cmp r14 97
jlt m55_case_done
cmp r14 122
jgt m55_case_done
sub r14 32
jmp m55_case_done
label m55_latin_initial
cmp r3 1
jne m55_case_done
load8 r0 $r7
cmp r0 195
jne m55_case_done
cmp r14 160
jlt m55_case_done
cmp r14 191
jgt m55_case_done
cmp r14 183
je m55_case_done
sub r14 32
label m55_case_done
set r13 0
label m55_print_byte
print r14
add r3 1
jmp m55_letter
label m55_done
store8 7700000000000000039 1
store8 7700000000000000038 0
jmp conversation_number_space
label m55_invalid
div r0 0
label conversation_number_space
set r14 32
print r14
label m56_entry
# Read-only response: learned ES/EN number names, otherwise composed digits.
load8 r0 7300000000000000002
cmp r0 1
jne m56_invalid
load8 r0 7300000000000000008
cmp r0 1
je m56_supported
set r14 63
print r14
jmp conversation_number_done
label m56_supported
load8 r2 7300000000000000010
load8 r0 7300000000000000011
mul r0 256
add r2 r0
load8 r15 7300000000000000003
cmp r15 1
je m56_language_ready
cmp r15 2
jne m56_invalid
label m56_language_ready
load8 r7 7200000000000000010
set r0 0
label m56_find_learned_name
cmp r0 r7
jge m56_decimal_output
set r8 7200000000000001000
mov r9 r0
mul r9 32
add r8 r9
load8 r9 $r8
cmp r9 4
jne m56_next_numeral
mov r9 r8
add r9 1
load8 r9 $r9
cmp r9 r2
jne m56_next_numeral
mov r9 r8
add r9 4
load8 r9 $r9
cmp r9 2
jlt m56_next_numeral
set r5 5
cmp r15 1
je m56_select_label
set r5 14
label m56_select_label
add r8 r5
load8 r6 $r8
cmp r6 1
jlt m56_invalid
cmp r6 8
jgt m56_invalid
set r1 0
label m56_emit_label
cmp r1 r6
jge m56_done
mov r9 r8
add r9 1
add r9 r1
load8 r14 $r9
print r14
add r1 1
jmp m56_emit_label
label m56_next_numeral
add r0 1
jmp m56_find_learned_name
label m56_decimal_output
set r3 10000
set r4 0
label m56_decimal_digit
mov r14 r2
div r14 r3
mod r2 r3
cmp r14 0
jne m56_nonzero_digit
cmp r4 1
je m56_print_digit
cmp r3 1
je m56_print_digit
jmp m56_next_place
label m56_nonzero_digit
set r4 1
label m56_print_digit
add r14 48
print r14
label m56_next_place
div r3 10
cmp r3 0
jgt m56_decimal_digit
label m56_done
jmp conversation_number_done
label m56_invalid
div r0 0
label conversation_number_done
set r14 46
print r14
jmp conversation_done
label conversation_fact_start
load8 r0 7400000000000000008
cmp r0 2
jne conversation_fact_next
store8 7700000000000000019 7
label m57_entry
# Select a teacher-supplied dialogue act; renderer gets only bytes in RVPC2.
load8 r0 7700000000000000019
cmp r0 1
jlt m57_invalid
cmp r0 8
jgt m57_invalid
load8 r1 7400000000000000003
set r7 7700000000000002000
sub r0 1
mul r0 512
add r7 r0
sub r1 1
mul r1 256
add r7 r1
load8 r6 $r7
cmp r6 1
jlt m57_invalid
add r7 1
set r13 0
jmp m58_entry
label m57_invalid
div r0 0
label m58_entry
# Print selected memory bytes, including Spanish UTF-8 initial capitalization.
# No words, facts or response choice in the transport.
cmp r6 1
jlt m58_invalid
cmp r6 255
jgt m58_invalid
load8 r0 7700000000000000039
cmp r0 1
jne m58_begin
set r14 32
print r14
label m58_begin
set r3 0
label m58_letter
cmp r3 r6
jge m58_done
mov r4 r7
add r4 r3
load8 r14 $r4
cmp r14 95
jne m58_case_check
set r14 32
label m58_case_check
cmp r13 0
je m58_print_byte
cmp r14 195
je m58_print_byte
cmp r3 0
jne m58_latin_initial
cmp r14 97
jlt m58_case_done
cmp r14 122
jgt m58_case_done
sub r14 32
jmp m58_case_done
label m58_latin_initial
cmp r3 1
jne m58_case_done
load8 r0 $r7
cmp r0 195
jne m58_case_done
cmp r14 160
jlt m58_case_done
cmp r14 191
jgt m58_case_done
cmp r14 183
je m58_case_done
sub r14 32
label m58_case_done
set r13 0
label m58_print_byte
print r14
add r3 1
jmp m58_letter
label m58_done
store8 7700000000000000039 1
store8 7700000000000000038 0
jmp conversation_fact_prefix_done
label m58_invalid
div r0 0
label conversation_fact_prefix_done
set r14 32
print r14
store8 7700000000000000039 0
store8 7700000000000000038 0
label conversation_fact_next
label m59_entry
# Compose factual clauses from actual semantic results and taught articles.
# Retain the exact inference path; do not replace evidence with fluent prose.
# 7700000000000000032 answer index or proof cursor,+33 stage,+34 proof flag,+35 dispatch.
load8 r0 7700000000000000034
cmp r0 1
je m59_proof
load8 r0 7700000000000000033
cmp r0 0
je m59_subject_article
cmp r0 1
je m59_subject
cmp r0 2
je m59_predicate
cmp r0 3
je m59_object_article
cmp r0 4
je m59_object
jmp m59_triple_done
label m59_subject_article
store8 7700000000000000033 1
load8 r0 7400000000000000011
load8 r1 7700000000000000528
cmp r0 r1
jne m59_subject
load8 r2 7400000000000000010
jmp m59_article
label m59_subject
store8 7700000000000000033 2
load8 r2 7400000000000000010
jmp m59_name
label m59_predicate
store8 7700000000000000033 3
load8 r2 7400000000000000011
jmp m59_name
label m59_object_article
store8 7700000000000000033 4
load8 r0 7400000000000000011
load8 r1 7700000000000000528
cmp r0 r1
jne m59_object
load8 r0 7700000000000000032
set r7 7400000000000002100
add r7 r0
load8 r2 $r7
jmp m59_article
label m59_object
store8 7700000000000000033 5
load8 r0 7700000000000000032
set r7 7400000000000002100
add r7 r0
load8 r2 $r7
jmp m59_name
label m59_article
set r7 7700000000000100102
mov r0 r2
mul r0 224
add r7 r0
load8 r0 7400000000000000003
sub r0 1
mul r0 112
add r7 r0
load8 r6 $r7
cmp r6 0
je m59_no_article
add r7 1
load8 r13 7700000000000000038
store8 7700000000000000035 2
jmp conversation_fact_dispatch
label m59_no_article
load8 r0 7700000000000000033
cmp r0 1
je m59_subject
jmp m59_object
label m59_name
store8 7700000000000000040 r2
store8 7700000000000000035 1
jmp conversation_fact_dispatch
label m59_triple_done
load8 r0 7700000000000000032
add r0 1
load8 r1 7400000000000000014
cmp r0 r1
jge m59_response_done
store8 7700000000000000032 r0
store8 7700000000000000033 0
load8 r2 7800000000000000003
cmp r2 1
jne m59_full_clause
store8 7700000000000000033 3
store8 7700000000000000038 0
sub r1 1
cmp r0 r1
je m59_conjunction
store8 7700000000000000039 0
set r14 44
print r14
set r14 32
print r14
jmp m59_object_article
label m59_conjunction
# Select the independently taught E018 conjunction, keeping every result.
set r7 7800000000000507168
load8 r0 7400000000000000003
sub r0 1
mul r0 256
add r7 r0
load8 r6 $r7
add r7 1
set r13 0
store8 7700000000000000035 2
jmp conversation_fact_dispatch
label m59_full_clause
set r14 59
print r14
set r14 32
print r14
store8 7700000000000000039 0
store8 7700000000000000038 0
jmp m59_subject_article
label m59_response_done
set r14 46
print r14
# Only a checkpoint with the explicit E018 preference hides routine proofs.
load8 r0 7800000000000000003
cmp r0 1
jne m59_show_proof
load8 r0 7800000000000000085
cmp r0 1
jne m59_done
label m59_show_proof
load8 r0 7400000000000000015
cmp r0 2
jlt m59_done
store8 7700000000000000032 r0
store8 7700000000000000033 0
store8 7700000000000000034 1
store8 7700000000000000038 0
store8 7700000000000000039 0
set r14 32
print r14
set r14 91
print r14
label m59_proof
load8 r0 7700000000000000033
cmp r0 0
je m59_proof_name
load8 r0 7700000000000000032
cmp r0 0
je m59_proof_done
sub r0 1
store8 7700000000000000032 r0
store8 7700000000000000039 0
set r14 32
print r14
set r14 45
print r14
set r14 62
print r14
set r14 32
print r14
label m59_proof_name
load8 r0 7700000000000000032
set r7 7400000000000002200
add r7 r0
load8 r2 $r7
store8 7700000000000000033 1
jmp m59_name
label m59_proof_done
set r14 93
print r14
label m59_done
store8 7700000000000000035 4
jmp conversation_fact_dispatch
label conversation_fact_dispatch
load8 r0 7700000000000000035
cmp r0 1
je conversation_fact_name
cmp r0 2
je conversation_fact_direct
jmp conversation_done
label conversation_fact_name
label m60_entry
# Resolve 7700000000000000040 to an existing shared bilingual name. r7=bytes,r6=len,r13=case.
load8 r2 7700000000000000040
cmp r2 0
je m60_invalid
load8 r13 7700000000000000038
set r7 7700000000000010000
mov r0 r2
mul r0 4
add r7 r0
load8 r0 $r7
cmp r0 1
jne m60_language
set r13 1
label m60_language
load8 r15 7400000000000000003
cmp r2 22
jgt m60_new_name
set r7 7200000000000001000
mov r3 r2
sub r3 1
mul r3 32
add r7 r3
set r3 5
cmp r15 1
je m60_old_name
set r3 14
label m60_old_name
add r7 r3
load8 r6 $r7
add r7 1
jmp conversation_fact_direct
label m60_new_name
load8 r10 7400000000000000004
load8 r3 7400000000000000005
mul r3 256
add r10 r3
set r3 0
label m60_lexeme
cmp r3 r10
jge m60_invalid
set r7 7400000000000010000
mov r4 r3
mul r4 40
add r7 r4
load8 r4 $r7
cmp r4 r2
jne m60_next_lexeme
mov r4 r7
add r4 2
load8 r5 $r4
cmp r5 r15
jne m60_next_lexeme
add r7 3
load8 r6 $r7
add r7 1
jmp conversation_fact_direct
label m60_next_lexeme
add r3 1
jmp m60_lexeme
label m60_invalid
div r0 0
label conversation_fact_direct
label m61_entry
# Print selected memory bytes, including Spanish UTF-8 initial capitalization.
# No words, facts or response choice in the transport.
cmp r6 1
jlt m61_invalid
cmp r6 255
jgt m61_invalid
load8 r0 7700000000000000039
cmp r0 1
jne m61_begin
set r14 32
print r14
label m61_begin
set r3 0
label m61_letter
cmp r3 r6
jge m61_done
mov r4 r7
add r4 r3
load8 r14 $r4
cmp r14 95
jne m61_case_check
set r14 32
label m61_case_check
cmp r13 0
je m61_print_byte
cmp r14 195
je m61_print_byte
cmp r3 0
jne m61_latin_initial
cmp r14 97
jlt m61_case_done
cmp r14 122
jgt m61_case_done
sub r14 32
jmp m61_case_done
label m61_latin_initial
cmp r3 1
jne m61_case_done
load8 r0 $r7
cmp r0 195
jne m61_case_done
cmp r14 160
jlt m61_case_done
cmp r14 191
jgt m61_case_done
cmp r14 183
je m61_case_done
sub r14 32
label m61_case_done
set r13 0
label m61_print_byte
print r14
add r3 1
jmp m61_letter
label m61_done
store8 7700000000000000039 1
store8 7700000000000000038 0
jmp conversation_fact_next
label m61_invalid
div r0 0
label conversation_done
load8 r0 7700000000000000025
cmp r0 1
je story_clean
jmp cleanup
label open_teach_check
label m62_entry
# A spelling cannot acquire entity and predicate types in the same statement.
# Reject the ambiguity before any vocabulary or graph cell is changed.
load8 r0 7800000000000000069
sub r0 1
set r8 7400000000000000512
mul r0 34
add r8 r0
load8 r9 $r8
set r10 0
label m62_entity
cmp r10 2
jge m62_ready
set r7 7800000000000000068
mov r0 r10
mul r0 2
add r7 r0
load8 r0 $r7
sub r0 1
mul r0 34
set r7 7400000000000000512
add r7 r0
load8 r0 $r7
cmp r0 r9
jne m62_next
set r0 0
label m62_letters
cmp r0 r9
jge m62_ambiguous
mov r1 r8
add r1 1
add r1 r0
load8 r2 $r1
mov r1 r7
add r1 1
add r1 r0
load8 r3 $r1
cmp r2 r3
jne m62_next
add r0 1
jmp m62_letters
label m62_next
add r10 1
jmp m62_entity
label m62_ambiguous
store8 7800000000000000080 10
store8 7800000000000000087 0
jmp open_teach_checked
label m62_ready
store8 7800000000000000087 1
jmp open_teach_checked
label open_teach_checked
load8 r0 7800000000000000087
cmp r0 0
je open_reply
label open_intern
label m63_entry
# Intern only the variables of an already recognized explicit teaching act.
load8 r0 7800000000000000088
cmp r0 3
jge m63_done
set r7 7800000000000000068
add r7 r0
load8 r1 $r7
sub r1 1
store8 7800000000000000164 r1
set r1 0
mov r14 r1
mod r14 256
store8 7800000000000000160 r14
mov r14 r1
div r14 256
store8 7800000000000000161 r14
set r1 1
cmp r0 1
jne m63_kind_ready
set r1 2
label m63_kind_ready
store8 7800000000000000162 r1
load8 r1 7400000000000000003
store8 7800000000000000163 r1
store8 7800000000000000087 1
jmp open_intern_ready
label m63_done
store8 7800000000000000087 0
jmp open_intern_ready
label open_intern_ready
load8 r0 7800000000000000087
cmp r0 0
je open_mutate
label m64_entry
# Explicit teacher only: 7800000000000000160 requested u16 ID (0 allocate),+162 kind,
# +163 language,+164 raw token index. Return +166 u16 ID. All failures throw
# so the original native transaction rolls back vocabulary and facts together.
load8 r0 7800000000000000002
cmp r0 1
jne m64_invalid
load8 r0 7400000000000000040
cmp r0 0
jne m64_invalid
load8 r0 7800000000000000164
load8 r1 7400000000000000032
cmp r0 r1
jge m64_invalid
load8 r11 7800000000000000162
cmp r11 1
jlt m64_invalid
cmp r11 3
jgt m64_invalid
load8 r12 7800000000000000163
cmp r12 1
jlt m64_invalid
cmp r12 2
jgt m64_invalid
set r8 7400000000000000512
mov r1 r0
mul r1 34
add r8 r1
load8 r9 $r8
cmp r9 1
jlt m64_invalid
cmp r9 32
jgt m64_invalid
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
je m64_unknown
cmp r3 r11
jne m64_invalid
cmp r10 0
je m64_reuse
cmp r10 r2
jne m64_invalid
label m64_reuse
mov r14 r2
mod r14 256
store8 7800000000000000166 r14
mov r14 r2
div r14 256
store8 7800000000000000167 r14
jmp m65_entry
label m64_unknown
load8 r6 7800000000000000006
load8 r14 7800000000000000007
mul r14 256
add r6 r14
cmp r6 8192
jge m64_invalid
cmp r10 0
jne m64_requested
load8 r10 7800000000000000004
load8 r14 7800000000000000005
mul r14 256
add r10 r14
cmp r10 65535
jge m64_invalid
mov r0 r10
add r0 1
mov r14 r0
mod r14 256
store8 7800000000000000004 r14
mov r14 r0
div r14 256
store8 7800000000000000005 r14
jmp m64_new_kind
label m64_requested
cmp r10 255
jgt m64_extended_kind
cmp r10 22
jle m64_old_entity
set r7 7400000000000006000
add r7 r10
load8 r0 $r7
cmp r0 r11
jne m64_invalid
jmp m64_new_entry
label m64_old_entity
cmp r11 1
jne m64_invalid
jmp m64_new_entry
label m64_extended_kind
set r7 7800000000000020000
add r7 r10
load8 r0 $r7
cmp r0 0
je m64_update_next
cmp r0 r11
jne m64_invalid
jmp m64_new_entry
label m64_update_next
load8 r0 7800000000000000004
load8 r14 7800000000000000005
mul r14 256
add r0 r14
cmp r10 r0
jlt m64_new_kind
cmp r10 65535
jge m64_invalid
mov r0 r10
add r0 1
mov r14 r0
mod r14 256
store8 7800000000000000004 r14
mov r14 r0
div r14 256
store8 7800000000000000005 r14
label m64_new_kind
set r7 7800000000000020000
add r7 r10
store8 $r7 r11
label m64_new_entry
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
label m64_copy
cmp r0 r9
jge m64_publish
mov r1 r8
add r1 1
add r1 r0
load8 r2 $r1
mov r1 r7
add r1 r0
store8 $r1 r2
add r0 1
jmp m64_copy
label m64_publish
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
jmp m65_entry
label m64_invalid
div r0 0
label m65_entry
load8 r0 7800000000000000088
mul r0 2
set r7 7800000000000000072
add r7 r0
load8 r1 7800000000000000166
load8 r14 7800000000000000167
mul r14 256
add r1 r14
mov r15 r7
mov r14 r1
mod r14 256
store8 $r15 r14
add r15 1
mov r14 r1
div r14 256
store8 $r15 r14
load8 r0 7800000000000000088
add r0 1
store8 7800000000000000088 r0
jmp m66_entry
label m66_entry
# Read the old lexicon in place, then the append-only u16 extension. Unknown
# questions never allocate. For old IDs, aliases also normalize old K slots.
load8 r0 7800000000000000002
cmp r0 1
jne m66_done
load8 r0 7400000000000000040
cmp r0 0
jne m66_done
load8 r13 7400000000000000032
load8 r12 7800000000000000006
load8 r14 7800000000000000007
mul r14 256
add r12 r14
cmp r12 8192
jgt m66_invalid
set r0 0
label m66_token
cmp r0 r13
jge m66_done
set r7 7400000000000001600
mov r1 r0
mul r1 2
add r7 r1
load8 r10 $r7
add r7 1
load8 r11 $r7
cmp r10 0
jne m66_save
set r1 7400000000000000512
mov r2 r0
mul r2 34
add r1 r2
load8 r2 $r1
set r3 0
label m66_word
cmp r3 r12
jge m66_save
set r4 8600000000000400000
mov r5 r3
mul r5 40
add r4 r5
mov r7 r4
add r7 4
load8 r5 $r7
cmp r5 r2
jne m66_next_word
set r6 0
label m66_letters
cmp r6 r2
jge m66_found
mov r7 r1
add r7 1
add r7 r6
load8 r8 $r7
mov r7 r4
add r7 5
add r7 r6
load8 r9 $r7
cmp r8 r9
jne m66_next_word
add r6 1
jmp m66_letters
label m66_found
mov r15 r4
load8 r10 $r15
add r15 1
load8 r14 $r15
mul r14 256
add r10 r14
mov r7 r4
add r7 2
load8 r11 $r7
jmp m66_save
label m66_next_word
add r3 1
jmp m66_word
label m66_save
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
jgt m66_next_token
set r7 7400000000000001600
mov r1 r0
mul r1 2
add r7 r1
store8 $r7 r10
add r7 1
store8 $r7 r11
label m66_next_token
add r0 1
jmp m66_token
label m66_done
jmp open_intern
label m66_invalid
div r0 0
label open_mutate
label m67_entry
# S/P/O at +72/74/76; intent +64=3 positive,4 negative,7 retract dialogue layer.
# This never overwrites any original K byte. Exact repeats do not grow indexes.
load8 r2 7800000000000000072
load8 r14 7800000000000000073
mul r14 256
add r2 r14
load8 r3 7800000000000000074
load8 r14 7800000000000000075
mul r14 256
add r3 r14
load8 r4 7800000000000000076
load8 r14 7800000000000000077
mul r14 256
add r4 r14
load8 r5 7800000000000000064
cmp r2 0
je m67_invalid
cmp r3 0
je m67_invalid
cmp r4 0
je m67_invalid
mov r7 r2
mul r7 65536
add r7 r3
mul r7 65536
add r7 r4
mul r7 4
add r7 7800000010000000000
cmp r5 7
je m67_retract
# Avoid recording a second positive/negative copy of an identical old fact.
cmp r2 255
jgt m67_publish
cmp r3 255
jgt m67_publish
cmp r4 255
jgt m67_publish
mov r0 r2
mul r0 256
add r0 r3
mul r0 256
add r0 r4
mul r0 4
add r0 7400000000001000000
cmp r5 3
je m67_old_support
add r0 1
label m67_old_support
load8 r0 $r0
cmp r0 0
jne m67_learned
label m67_publish
mov r6 r7
add r6 2
load8 r0 $r6
cmp r0 1
je m67_support
load8 r11 7800000000000000008
load8 r14 7800000000000000009
mul r14 256
add r11 r14
cmp r11 4096
jge m67_invalid
store8 $r6 1
set r0 7800000000000200000
mov r1 r11
mul r1 6
add r0 r1
mov r15 r0
mov r14 r2
mod r14 256
store8 $r15 r14
add r15 1
mov r14 r2
div r14 256
store8 $r15 r14
add r0 2
mov r15 r0
mov r14 r3
mod r14 256
store8 $r15 r14
add r15 1
mov r14 r3
div r14 256
store8 $r15 r14
add r0 2
mov r15 r0
mov r14 r4
mod r14 256
store8 $r15 r14
add r15 1
mov r14 r4
div r14 256
store8 $r15 r14
add r11 1
mov r14 r11
mod r14 256
store8 7800000000000000008 r14
mov r14 r11
div r14 256
store8 7800000000000000009 r14
label m67_support
cmp r5 3
je m67_positive
add r7 1
label m67_positive
store8 $r7 1
label m67_learned
cmp r2 255
jgt m67_learned_ready
store8 7800000000000000040 1
label m67_learned_ready
store8 7800000000000000080 5
jmp open_reply
label m67_retract
store8 $r7 0
add r7 1
store8 $r7 0
store8 7800000000000000080 7
jmp open_reply
label m67_invalid
div r0 0
label open_alias
label m68_entry
load8 r0 7800000000000000072
load8 r14 7800000000000000073
mul r14 256
add r0 r14
mov r14 r0
mod r14 256
store8 7800000000000000160 r14
mov r14 r0
div r14 256
store8 7800000000000000161 r14
load8 r1 7800000000000000071
sub r1 1
mul r1 4
set r7 7800000000000001024
add r7 r1
mov r15 r7
load8 r1 $r15
add r15 1
load8 r14 $r15
mul r14 256
add r1 r14
cmp r1 0
je m68_capacity
cmp r1 r0
jne m68_collision
jmp m68_kind_dispatch
label m68_capacity
load8 r1 7800000000000000006
load8 r14 7800000000000000007
mul r14 256
add r1 r14
cmp r1 8192
jge m68_limit
label m68_kind_dispatch
cmp r0 22
jle m68_old_kind
cmp r0 255
jle m68_legacy_kind
set r7 7800000000000020000
add r7 r0
load8 r1 $r7
jmp m68_kind
label m68_legacy_kind
set r7 7400000000000006000
add r7 r0
load8 r1 $r7
jmp m68_kind
label m68_old_kind
set r1 1
label m68_kind
store8 7800000000000000162 r1
load8 r0 7400000000000000003
store8 7800000000000000163 r0
load8 r0 7800000000000000071
sub r0 1
store8 7800000000000000164 r0
store8 7800000000000000087 1
jmp open_alias_ready
label m68_collision
store8 7800000000000000080 11
store8 7800000000000000087 0
jmp open_alias_ready
label m68_limit
store8 7800000000000000080 9
store8 7800000000000000087 0
jmp open_alias_ready
label open_alias_ready
load8 r0 7800000000000000087
cmp r0 0
je open_reply
label m69_entry
# Explicit teacher only: 7800000000000000160 requested u16 ID (0 allocate),+162 kind,
# +163 language,+164 raw token index. Return +166 u16 ID. All failures throw
# so the original native transaction rolls back vocabulary and facts together.
load8 r0 7800000000000000002
cmp r0 1
jne m69_invalid
load8 r0 7400000000000000040
cmp r0 0
jne m69_invalid
load8 r0 7800000000000000164
load8 r1 7400000000000000032
cmp r0 r1
jge m69_invalid
load8 r11 7800000000000000162
cmp r11 1
jlt m69_invalid
cmp r11 3
jgt m69_invalid
load8 r12 7800000000000000163
cmp r12 1
jlt m69_invalid
cmp r12 2
jgt m69_invalid
set r8 7400000000000000512
mov r1 r0
mul r1 34
add r8 r1
load8 r9 $r8
cmp r9 1
jlt m69_invalid
cmp r9 32
jgt m69_invalid
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
je m69_unknown
cmp r3 r11
jne m69_invalid
cmp r10 0
je m69_reuse
cmp r10 r2
jne m69_invalid
label m69_reuse
mov r14 r2
mod r14 256
store8 7800000000000000166 r14
mov r14 r2
div r14 256
store8 7800000000000000167 r14
jmp open_alias_done
label m69_unknown
load8 r6 7800000000000000006
load8 r14 7800000000000000007
mul r14 256
add r6 r14
cmp r6 8192
jge m69_invalid
cmp r10 0
jne m69_requested
load8 r10 7800000000000000004
load8 r14 7800000000000000005
mul r14 256
add r10 r14
cmp r10 65535
jge m69_invalid
mov r0 r10
add r0 1
mov r14 r0
mod r14 256
store8 7800000000000000004 r14
mov r14 r0
div r14 256
store8 7800000000000000005 r14
jmp m69_new_kind
label m69_requested
cmp r10 255
jgt m69_extended_kind
cmp r10 22
jle m69_old_entity
set r7 7400000000000006000
add r7 r10
load8 r0 $r7
cmp r0 r11
jne m69_invalid
jmp m69_new_entry
label m69_old_entity
cmp r11 1
jne m69_invalid
jmp m69_new_entry
label m69_extended_kind
set r7 7800000000000020000
add r7 r10
load8 r0 $r7
cmp r0 0
je m69_update_next
cmp r0 r11
jne m69_invalid
jmp m69_new_entry
label m69_update_next
load8 r0 7800000000000000004
load8 r14 7800000000000000005
mul r14 256
add r0 r14
cmp r10 r0
jlt m69_new_kind
cmp r10 65535
jge m69_invalid
mov r0 r10
add r0 1
mov r14 r0
mod r14 256
store8 7800000000000000004 r14
mov r14 r0
div r14 256
store8 7800000000000000005 r14
label m69_new_kind
set r7 7800000000000020000
add r7 r10
store8 $r7 r11
label m69_new_entry
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
label m69_copy
cmp r0 r9
jge m69_publish
mov r1 r8
add r1 1
add r1 r0
load8 r2 $r1
mov r1 r7
add r1 r0
store8 $r1 r2
add r0 1
jmp m69_copy
label m69_publish
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
jmp open_alias_done
label m69_invalid
div r0 0
label open_alias_done
store8 7800000000000000080 6
jmp open_reply
label lingua_resume
label m70_entry
# Designed topic-memory operation; syntax invoking it is learned. Never return
# an old answer: restore roles and route through current evidence and conflicts.
load8 r0 8000000000000000003
cmp r0 1
jne m70_missing
load8 r0 8000000000000000025
cmp r0 2
je m70_previous
load8 r8 7800000000000000072
load8 r14 7800000000000000073
mul r14 256
add r8 r14
cmp r8 0
je m70_missing
set r10 0
label m70_find
cmp r10 64
jge m70_missing
set r7 8600000000000030000
mov r0 r10
mul r0 16
add r7 r0
load8 r0 $r7
cmp r0 1
jne m70_missing
add r7 2
load8 r0 $r7
add r7 1
load8 r14 $r7
mul r14 256
add r0 r14
cmp r0 r8
je m70_found
add r10 1
jmp m70_find
label m70_previous
set r10 1
label m70_found
set r7 8600000000000030000
mul r10 16
add r7 r10
load8 r0 $r7
cmp r0 1
jne m70_missing
add r7 1
load8 r0 $r7
store8 7800000000000000090 r0
add r7 1
set r1 0
label m70_copy_role
mov r2 r7
add r2 r1
load8 r0 $r2
set r2 7800000000000000072
add r2 r1
store8 $r2 r0
add r1 1
cmp r1 6
jlt m70_copy_role
store8 7800000000000000012 0
store8 7800000000000000067 2
jmp lingua_resumed
label m70_missing
store8 7800000000000000012 0
store8 7800000000000000080 12
store8 7800000000000000067 5
jmp lingua_resumed
label lingua_resumed
load8 r0 7800000000000000067
cmp r0 2
je open_query
jmp open_reply
label open_query
label m71_entry
# Fast compatible delegation is sound while all extra assertions have NEW
# subjects and all newly calibrated rules have NEW predicates. Any explicit
# assertion on an old subject permanently disables this optimization.
load8 r0 7800000000000000085
cmp r0 1
je m71_native
load8 r0 7800000000000000040
cmp r0 0
jne m71_native
load8 r2 7800000000000000072
load8 r14 7800000000000000073
mul r14 256
add r2 r14
load8 r3 7800000000000000074
load8 r14 7800000000000000075
mul r14 256
add r3 r14
load8 r4 7800000000000000076
load8 r14 7800000000000000077
mul r14 256
add r4 r14
cmp r2 255
jgt m71_native
cmp r3 255
jgt m71_native
cmp r4 255
jgt m71_native
# Normalize semantic slots only, retaining raw words for the E009 fallback.
load8 r0 7800000000000000090
cmp r0 1
jne m71_legacy_verify
store8 7400000000000001600 250
store8 7400000000000001601 3
store8 7400000000000001602 r3
store8 7400000000000001603 2
store8 7400000000000001604 r2
store8 7400000000000001605 1
jmp m71_delegate
label m71_legacy_verify
store8 7400000000000001600 r2
store8 7400000000000001601 1
store8 7400000000000001602 r3
store8 7400000000000001603 2
store8 7400000000000001604 r4
store8 7400000000000001605 1
label m71_delegate
store8 7400000000000000032 3
store8 7800000000000000067 0
cmp r2 0
je m71_done
cmp r3 0
je m71_done
store8 7800000000000000012 1
load8 r0 7800000000000000090
store8 7800000000000000013 r0
mov r14 r2
mod r14 256
store8 7800000000000000014 r14
mov r14 r2
div r14 256
store8 7800000000000000015 r14
mov r14 r3
mod r14 256
store8 7800000000000000016 r14
mov r14 r3
div r14 256
store8 7800000000000000017 r14
mov r14 r4
mod r14 256
store8 7800000000000000018 r14
mov r14 r4
div r14 256
store8 7800000000000000019 r14
jmp open_query_ready
label m71_native
load8 r2 7800000000000000072
load8 r14 7800000000000000073
mul r14 256
add r2 r14
load8 r3 7800000000000000074
load8 r14 7800000000000000075
mul r14 256
add r3 r14
cmp r2 0
je m71_unknown
cmp r3 0
je m71_unknown
load8 r0 7800000000000000090
cmp r0 1
je m71_property
load8 r4 7800000000000000076
load8 r14 7800000000000000077
mul r14 256
add r4 r14
cmp r4 0
je m71_unknown
mov r14 r2
mod r14 256
store8 7800000000000000200 r14
mov r14 r2
div r14 256
store8 7800000000000000201 r14
mov r14 r3
mod r14 256
store8 7800000000000000202 r14
mov r14 r3
div r14 256
store8 7800000000000000203 r14
mov r14 r4
mod r14 256
store8 7800000000000000204 r14
mov r14 r4
div r14 256
store8 7800000000000000205 r14
store8 7800000000000000087 2
jmp open_query_ready
label m71_property
store8 7800000000000000087 1
jmp open_query_ready
label m71_unknown
load8 r0 7800000000000000082
cmp r0 0
je m71_no_result
store8 7800000000000000080 1
store8 7800000000000000087 0
jmp open_query_ready
label m71_no_result
store8 7800000000000000080 3
store8 7800000000000000087 0
label m71_done
jmp open_query_ready
label open_query_ready
load8 r0 7800000000000000067
cmp r0 0
je open_fallback
load8 r0 7800000000000000087
cmp r0 0
je open_reply
cmp r0 1
je open_property
label m72_entry
# Single evidence view over the immutable old graph and new taught assertions.
# Input +200/202/204 S/P/O u16; output +208=0/1/2/3, +209 provenance bitmask.
load8 r2 7800000000000000200
load8 r14 7800000000000000201
mul r14 256
add r2 r14
load8 r3 7800000000000000202
load8 r14 7800000000000000203
mul r14 256
add r3 r14
load8 r4 7800000000000000204
load8 r14 7800000000000000205
mul r14 256
add r4 r14
set r8 0
set r9 0
set r10 0
cmp r2 0
je m72_finish
cmp r3 0
je m72_finish
cmp r4 0
je m72_finish
cmp r2 255
jgt m72_extension
cmp r3 255
jgt m72_extension
cmp r4 255
jgt m72_extension
mov r7 r2
mul r7 256
add r7 r3
mul r7 256
add r7 r4
mul r7 4
add r7 7400000000001000000
load8 r8 $r7
add r7 1
load8 r9 $r7
mov r0 r8
add r0 r9
cmp r0 0
je m72_extension
set r10 1
label m72_extension
mov r7 r2
mul r7 65536
add r7 r3
mul r7 65536
add r7 r4
mul r7 4
add r7 7800000010000000000
load8 r0 $r7
add r8 r0
add r7 1
load8 r1 $r7
add r9 r1
add r0 r1
cmp r0 0
je m72_finish
add r10 2
label m72_finish
set r0 0
cmp r8 0
je m72_negative
set r0 1
label m72_negative
cmp r9 0
je m72_done
add r0 2
label m72_done
store8 7800000000000000208 r0
store8 7800000000000000209 r10
jmp m73_entry
label m73_entry
# +87=1 supported/blocked direct answer;0 means rule search is needed.
load8 r0 7800000000000000208
cmp r0 0
je m73_need_rule
store8 7800000000000000087 1
cmp r0 3
je m73_conflict
store8 7800000000000000080 r0
load8 r0 7800000000000000209
cmp r0 2
jlt m73_answer
store8 7800000000000000089 1
label m73_answer
load8 r0 7800000000000000076
load8 r14 7800000000000000077
mul r14 256
add r0 r14
mov r14 r0
mod r14 256
store8 7800000000008300000 r14
mov r14 r0
div r14 256
store8 7800000000008300001 r14
store8 7800000000000000082 1
jmp open_direct_ready
label m73_conflict
store8 7800000000000000080 4
jmp open_direct_ready
label m73_need_rule
store8 7800000000000000087 0
jmp open_direct_ready
label open_direct_ready
load8 r0 7800000000000000087
cmp r0 1
je open_reply
label m74_entry
load8 r0 7800000000000000074
load8 r14 7800000000000000075
mul r14 256
add r0 r14
cmp r0 255
jgt m74_extended
store8 7400000000000000011 r0
store8 7800000000000000087 1
jmp open_rule_ready
label m74_extended
store8 7800000000000000087 0
jmp open_rule_ready
label open_rule_ready
load8 r0 7800000000000000087
cmp r0 0
je open_model_start
label m75_entry
# Recheck current facts at inference time. Stale/contradicted witnesses cannot
# preserve a rule. At least TWO different positive closures and zero negatives.
load8 r5 7400000000000000011
set r11 7400000000000050000
mov r0 r5
mul r0 40
add r11 r0
load8 r15 $r11
cmp r15 8
jgt m75_invalid
set r0 0
set r6 0
set r12 0
label m75_witness
cmp r0 r15
jge m75_finish
mov r7 r11
add r7 1
mov r1 r0
mul r1 3
add r7 r1
load8 r2 $r7
add r7 1
load8 r3 $r7
add r7 1
load8 r4 $r7
mov r7 r2
mul r7 256
add r7 r5
mul r7 256
add r7 r3
mul r7 4
add r7 7400000000001000000
load8 r8 $r7
add r7 1
load8 r9 $r7
set r10 0
cmp r8 0
je m75_ab_no_positive
set r10 1
label m75_ab_no_positive
cmp r9 0
je m75_ab_done
add r10 2
label m75_ab_done

cmp r10 1
jne m75_next
mov r7 r3
mul r7 256
add r7 r5
mul r7 256
add r7 r4
mul r7 4
add r7 7400000000001000000
load8 r8 $r7
add r7 1
load8 r9 $r7
set r10 0
cmp r8 0
je m75_bc_no_positive
set r10 1
label m75_bc_no_positive
cmp r9 0
je m75_bc_done
add r10 2
label m75_bc_done

cmp r10 1
jne m75_next
mov r7 r2
mul r7 256
add r7 r5
mul r7 256
add r7 r4
mul r7 4
add r7 7400000000001000000
load8 r8 $r7
add r7 1
load8 r9 $r7
set r10 0
cmp r8 0
je m75_ac_no_positive
set r10 1
label m75_ac_no_positive
cmp r9 0
je m75_ac_done
add r10 2
label m75_ac_done

cmp r10 1
je m75_positive
cmp r10 0
je m75_next
# Negative or conflicted closure blocks this empirical generalization.
set r12 1
jmp m75_next
label m75_positive
add r6 1
label m75_next
add r0 1
jmp m75_witness
label m75_finish
store8 7400000000000000041 0
cmp r12 0
jne m75_done
cmp r6 2
jlt m75_done
store8 7400000000000000041 1
label m75_done
jmp open_model_start
label m75_invalid
div r0 0
label open_model_start
label m76_entry
load8 r0 7800000000000000087
cmp r0 1
jne m76_extension
load8 r0 7400000000000000041
cmp r0 1
jne m76_extension
store8 7800000000000000091 1
store8 7800000000000000255 0
jmp open_model_route
label m76_extension
store8 7800000000000000250 0
store8 7800000000000000251 0
store8 7800000000000000252 3
load8 r0 7800000000000000074
load8 r14 7800000000000000075
mul r14 256
add r0 r14
set r7 7800000000002000000
mul r0 64
add r7 r0
load8 r0 $r7
cmp r0 6
jgt m76_invalid
store8 7800000000000000254 r0
store8 7800000000000000255 1
jmp open_model_route
label m76_invalid
div r0 0
label open_model_route
load8 r0 7800000000000000255
cmp r0 0
je open_bfs_start
label open_model_next
label m77_entry
load8 r0 7800000000000000250
load8 r1 7800000000000000254
cmp r0 r1
jge m77_finish
load8 r1 7800000000000000074
load8 r14 7800000000000000075
mul r14 256
add r1 r14
set r7 7800000000002000004
mul r1 64
add r7 r1
mul r0 6
add r7 r0
mov r15 r7
load8 r2 $r15
add r15 1
load8 r14 $r15
mul r14 256
add r2 r14
add r7 2
mov r15 r7
load8 r3 $r15
add r15 1
load8 r14 $r15
mul r14 256
add r3 r14
add r7 2
mov r15 r7
load8 r4 $r15
add r15 1
load8 r14 $r15
mul r14 256
add r4 r14
mov r14 r2
mod r14 256
store8 7800000000000000240 r14
mov r14 r2
div r14 256
store8 7800000000000000241 r14
mov r14 r3
mod r14 256
store8 7800000000000000242 r14
mov r14 r3
div r14 256
store8 7800000000000000243 r14
mov r14 r4
mod r14 256
store8 7800000000000000244 r14
mov r14 r4
div r14 256
store8 7800000000000000245 r14
store8 7800000000000000246 0
store8 7800000000000000248 0
store8 7800000000000000249 0
store8 7800000000000000255 1
jmp open_model_next_ready
label m77_finish
store8 7800000000000000255 0
load8 r0 7800000000000000251
cmp r0 2
jlt m77_done
load8 r0 7800000000000000253
cmp r0 0
jne m77_done
load8 r0 7800000000000000252
cmp r0 1
je m77_transitive
cmp r0 2
jne m77_done
store8 7800000000000000091 2
jmp open_model_next_ready
label m77_transitive
store8 7800000000000000091 1
label m77_done
jmp open_model_next_ready
label open_model_next_ready
load8 r0 7800000000000000255
cmp r0 0
je open_bfs_start
label open_witness
label m78_entry
# Four real evidence reads: closure S-P-O, A-P-O, S-P-A, S-IS-A.
load8 r0 7800000000000000246
cmp r0 4
jge m78_done
load8 r2 7800000000000000240
load8 r14 7800000000000000241
mul r14 256
add r2 r14
load8 r3 7800000000000000074
load8 r14 7800000000000000075
mul r14 256
add r3 r14
load8 r4 7800000000000000244
load8 r14 7800000000000000245
mul r14 256
add r4 r14
cmp r0 1
jne m78_not_middle
load8 r2 7800000000000000242
load8 r14 7800000000000000243
mul r14 256
add r2 r14
label m78_not_middle
cmp r0 2
jlt m78_arguments
load8 r4 7800000000000000242
load8 r14 7800000000000000243
mul r14 256
add r4 r14
cmp r0 3
jne m78_arguments
load8 r3 7800000000000000032
load8 r14 7800000000000000033
mul r14 256
add r3 r14
label m78_arguments
mov r14 r2
mod r14 256
store8 7800000000000000200 r14
mov r14 r2
div r14 256
store8 7800000000000000201 r14
mov r14 r3
mod r14 256
store8 7800000000000000202 r14
mov r14 r3
div r14 256
store8 7800000000000000203 r14
mov r14 r4
mod r14 256
store8 7800000000000000204 r14
mov r14 r4
div r14 256
store8 7800000000000000205 r14
store8 7800000000000000247 1
jmp open_witness_ready
label m78_done
store8 7800000000000000247 0
jmp open_witness_ready
label open_witness_ready
load8 r0 7800000000000000247
cmp r0 0
je open_model_accept
label m79_entry
# Single evidence view over the immutable old graph and new taught assertions.
# Input +200/202/204 S/P/O u16; output +208=0/1/2/3, +209 provenance bitmask.
load8 r2 7800000000000000200
load8 r14 7800000000000000201
mul r14 256
add r2 r14
load8 r3 7800000000000000202
load8 r14 7800000000000000203
mul r14 256
add r3 r14
load8 r4 7800000000000000204
load8 r14 7800000000000000205
mul r14 256
add r4 r14
set r8 0
set r9 0
set r10 0
cmp r2 0
je m79_finish
cmp r3 0
je m79_finish
cmp r4 0
je m79_finish
cmp r2 255
jgt m79_extension
cmp r3 255
jgt m79_extension
cmp r4 255
jgt m79_extension
mov r7 r2
mul r7 256
add r7 r3
mul r7 256
add r7 r4
mul r7 4
add r7 7400000000001000000
load8 r8 $r7
add r7 1
load8 r9 $r7
mov r0 r8
add r0 r9
cmp r0 0
je m79_extension
set r10 1
label m79_extension
mov r7 r2
mul r7 65536
add r7 r3
mul r7 65536
add r7 r4
mul r7 4
add r7 7800000010000000000
load8 r0 $r7
add r8 r0
add r7 1
load8 r1 $r7
add r9 r1
add r0 r1
cmp r0 0
je m79_finish
add r10 2
label m79_finish
set r0 0
cmp r8 0
je m79_negative
set r0 1
label m79_negative
cmp r9 0
je m79_done
add r0 2
label m79_done
store8 7800000000000000208 r0
store8 7800000000000000209 r10
jmp m80_entry
label m80_entry
load8 r0 7800000000000000246
load8 r1 7800000000000000208
cmp r0 0
jne m80_premise
cmp r1 1
je m80_next
cmp r1 0
je m80_failed
store8 7800000000000000249 1
jmp m80_failed
label m80_premise
cmp r0 1
jne m80_family
cmp r1 1
jne m80_failed
jmp m80_next
label m80_family
cmp r1 1
jne m80_next
load8 r2 7800000000000000248
cmp r0 2
jne m80_inheritance
add r2 1
jmp m80_mask
label m80_inheritance
add r2 2
label m80_mask
store8 7800000000000000248 r2
label m80_next
add r0 1
store8 7800000000000000246 r0
jmp open_witness
label m80_failed
store8 7800000000000000248 0
store8 7800000000000000246 4
jmp open_witness
label open_model_accept
label m81_entry
load8 r0 7800000000000000250
add r0 1
store8 7800000000000000250 r0
load8 r0 7800000000000000249
cmp r0 0
je m81_support
store8 7800000000000000253 1
label m81_support
load8 r1 7800000000000000248
cmp r1 0
je m81_done
load8 r0 7800000000000000251
add r0 1
store8 7800000000000000251 r0
load8 r2 7800000000000000252
set r3 0
mov r0 r1
mod r0 2
cmp r0 0
je m81_second
mov r0 r2
mod r0 2
cmp r0 0
je m81_second
add r3 1
label m81_second
cmp r1 2
jlt m81_ready
cmp r2 2
jlt m81_ready
add r3 2
label m81_ready
store8 7800000000000000252 r3
label m81_done
jmp open_model_next
label open_bfs_start
label m82_entry
load8 r0 7800000000000000091
cmp r0 0
je m82_unknown
load8 r2 7800000000000000072
load8 r14 7800000000000000073
mul r14 256
add r2 r14
mov r14 r2
mod r14 256
store8 7800000000008000000 r14
mov r14 r2
div r14 256
store8 7800000000008000001 r14
store8 7800000000008000002 255
set r7 7800000000008100000
add r7 r2
store8 $r7 1
store8 7800000000000000120 1
store8 7800000000000000122 0
store8 7800000000000000087 1
jmp open_bfs_ready
label m82_unknown
load8 r0 7800000000000000082
cmp r0 0
je m82_no_result
store8 7800000000000000080 1
store8 7800000000000000087 0
jmp open_bfs_ready
label m82_no_result
store8 7800000000000000080 3
store8 7800000000000000087 0
jmp open_bfs_ready
label open_bfs_ready
load8 r0 7800000000000000087
cmp r0 0
je open_reply
label open_bfs_node
label m83_entry
load8 r0 7800000000000000122
load8 r1 7800000000000000120
cmp r0 r1
jge m83_exhausted
set r7 7800000000008000000
mul r0 8
add r7 r0
mov r15 r7
load8 r2 $r15
add r15 1
load8 r14 $r15
mul r14 256
add r2 r14
add r7 3
load8 r3 $r7
mov r14 r2
mod r14 256
store8 7800000000000000094 r14
mov r14 r2
div r14 256
store8 7800000000000000095 r14
store8 7800000000000000123 r3
set r0 0
mov r14 r0
mod r14 256
store8 7800000000000000092 r14
mov r14 r0
div r14 256
store8 7800000000000000093 r14
store8 7800000000000000233 0
load8 r0 7800000000000000091
load8 r0 7800000000000000090
cmp r0 1
je m83_listing
mov r14 r2
mod r14 256
store8 7800000000000000200 r14
mov r14 r2
div r14 256
store8 7800000000000000201 r14
load8 r0 7800000000000000074
load8 r14 7800000000000000075
mul r14 256
add r0 r14
mov r14 r0
mod r14 256
store8 7800000000000000202 r14
mov r14 r0
div r14 256
store8 7800000000000000203 r14
load8 r0 7800000000000000076
load8 r14 7800000000000000077
mul r14 256
add r0 r14
mov r14 r0
mod r14 256
store8 7800000000000000204 r14
mov r14 r0
div r14 256
store8 7800000000000000205 r14
store8 7800000000000000232 1
jmp open_bfs_node_ready
label m83_listing
store8 7800000000000000232 0
jmp open_bfs_node_ready
label m83_exhausted
store8 7800000000000000080 3
load8 r0 7800000000000000082
cmp r0 0
je m83_budget_check
store8 7800000000000000080 1
label m83_budget_check
load8 r0 7800000000000000125
cmp r0 0
je m83_finish
store8 7800000000000000080 9
label m83_finish
store8 7800000000000000233 1
jmp open_bfs_node_ready
label open_bfs_node_ready
load8 r0 7800000000000000233
cmp r0 1
je open_bfs_complete
load8 r0 7800000000000000232
cmp r0 0
je open_bfs_scan
label m84_entry
# Single evidence view over the immutable old graph and new taught assertions.
# Input +200/202/204 S/P/O u16; output +208=0/1/2/3, +209 provenance bitmask.
load8 r2 7800000000000000200
load8 r14 7800000000000000201
mul r14 256
add r2 r14
load8 r3 7800000000000000202
load8 r14 7800000000000000203
mul r14 256
add r3 r14
load8 r4 7800000000000000204
load8 r14 7800000000000000205
mul r14 256
add r4 r14
set r8 0
set r9 0
set r10 0
cmp r2 0
je m84_finish
cmp r3 0
je m84_finish
cmp r4 0
je m84_finish
cmp r2 255
jgt m84_extension
cmp r3 255
jgt m84_extension
cmp r4 255
jgt m84_extension
mov r7 r2
mul r7 256
add r7 r3
mul r7 256
add r7 r4
mul r7 4
add r7 7400000000001000000
load8 r8 $r7
add r7 1
load8 r9 $r7
mov r0 r8
add r0 r9
cmp r0 0
je m84_extension
set r10 1
label m84_extension
mov r7 r2
mul r7 65536
add r7 r3
mul r7 65536
add r7 r4
mul r7 4
add r7 7800000010000000000
load8 r0 $r7
add r8 r0
add r7 1
load8 r1 $r7
add r9 r1
add r0 r1
cmp r0 0
je m84_finish
add r10 2
label m84_finish
set r0 0
cmp r8 0
je m84_negative
set r0 1
label m84_negative
cmp r9 0
je m84_done
add r0 2
label m84_done
store8 7800000000000000208 r0
store8 7800000000000000209 r10
jmp m85_entry
label m85_entry
# An explicit negative at an ancestor is an exception barrier. Contradictory
# ancestor evidence blocks a confident inherited answer.
store8 7800000000000000234 0
load8 r0 7800000000000000208
cmp r0 0
je m85_done
cmp r0 1
je m85_found
cmp r0 3
je m85_conflict
store8 7800000000000000234 2
jmp open_bfs_check
label m85_found
load8 r0 7800000000000000123
cmp r0 31
jge m85_depth_limit
store8 7800000000000000234 1
store8 7800000000000000235 1
load8 r0 7800000000000000122
store8 7800000000000000124 r0
load8 r0 7800000000000000209
cmp r0 2
jlt m85_done
store8 7800000000000000089 1
jmp open_bfs_check
label m85_conflict
store8 7800000000000000080 4
store8 7800000000000000234 3
jmp open_bfs_check
label m85_depth_limit
store8 7800000000000000080 9
store8 7800000000000000234 3
label m85_done
jmp open_bfs_check
label open_bfs_check
load8 r0 7800000000000000234
cmp r0 4
je open_property_path
cmp r0 1
je open_proof
cmp r0 2
je open_bfs_advance
cmp r0 3
je open_reply
label open_bfs_scan
label m86_entry
# Enumerate sparse registered edges, never all 65536 possible entity IDs.
# Return +224/226/228 S/P/O; +231 ready. Cursor +92 advances before return.
load8 r0 7800000000000000092
load8 r14 7800000000000000093
mul r14 256
add r0 r14
load8 r1 7400000000000000006
load8 r14 7400000000000000007
mul r14 256
add r1 r14
cmp r0 r1
jlt m86_legacy
sub r0 r1
load8 r1 7800000000000000008
load8 r14 7800000000000000009
mul r14 256
add r1 r14
cmp r0 r1
jge m86_done
set r7 7800000000000200000
mul r0 6
add r7 r0
mov r15 r7
load8 r2 $r15
add r15 1
load8 r14 $r15
mul r14 256
add r2 r14
add r7 2
mov r15 r7
load8 r3 $r15
add r15 1
load8 r14 $r15
mul r14 256
add r3 r14
add r7 2
mov r15 r7
load8 r4 $r15
add r15 1
load8 r14 $r15
mul r14 256
add r4 r14
jmp m86_ready
label m86_legacy
set r7 7400000000000080000
mul r0 3
add r7 r0
load8 r2 $r7
add r7 1
load8 r3 $r7
add r7 1
load8 r4 $r7
label m86_ready
mov r14 r2
mod r14 256
store8 7800000000000000224 r14
mov r14 r2
div r14 256
store8 7800000000000000225 r14
mov r14 r3
mod r14 256
store8 7800000000000000226 r14
mov r14 r3
div r14 256
store8 7800000000000000227 r14
mov r14 r4
mod r14 256
store8 7800000000000000228 r14
mov r14 r4
div r14 256
store8 7800000000000000229 r14
load8 r0 7800000000000000092
load8 r14 7800000000000000093
mul r14 256
add r0 r14
add r0 1
mov r14 r0
mod r14 256
store8 7800000000000000092 r14
mov r14 r0
div r14 256
store8 7800000000000000093 r14
store8 7800000000000000231 1
jmp open_bfs_candidate
label m86_done
store8 7800000000000000231 0
jmp open_bfs_candidate
label open_bfs_candidate
load8 r0 7800000000000000231
cmp r0 0
je open_bfs_advance
label m87_entry
store8 7800000000000000087 0
load8 r2 7800000000000000224
load8 r14 7800000000000000225
mul r14 256
add r2 r14
load8 r0 7800000000000000094
load8 r14 7800000000000000095
mul r14 256
add r0 r14
cmp r2 r0
jne m87_done
load8 r3 7800000000000000226
load8 r14 7800000000000000227
mul r14 256
add r3 r14
load8 r0 7800000000000000090
cmp r0 1
jne m87_traversal
load8 r0 7800000000000000074
load8 r14 7800000000000000075
mul r14 256
add r0 r14
cmp r3 r0
je m87_listing_edge
label m87_traversal
load8 r0 7800000000000000091
cmp r0 2
je m87_inherited
load8 r0 7800000000000000074
load8 r14 7800000000000000075
mul r14 256
add r0 r14
jmp m87_predicate
label m87_inherited
load8 r0 7800000000000000032
load8 r14 7800000000000000033
mul r14 256
add r0 r14
label m87_predicate
cmp r3 r0
jne m87_done
load8 r4 7800000000000000228
load8 r14 7800000000000000229
mul r14 256
add r4 r14
mov r14 r2
mod r14 256
store8 7800000000000000200 r14
mov r14 r2
div r14 256
store8 7800000000000000201 r14
mov r14 r3
mod r14 256
store8 7800000000000000202 r14
mov r14 r3
div r14 256
store8 7800000000000000203 r14
mov r14 r4
mod r14 256
store8 7800000000000000204 r14
mov r14 r4
div r14 256
store8 7800000000000000205 r14
store8 7800000000000000087 1
jmp open_bfs_selected
label m87_listing_edge
load8 r0 7800000000000000091
cmp r0 2
jne m87_traversal
load8 r4 7800000000000000228
load8 r14 7800000000000000229
mul r14 256
add r4 r14
mov r14 r2
mod r14 256
store8 7800000000000000200 r14
mov r14 r2
div r14 256
store8 7800000000000000201 r14
mov r14 r3
mod r14 256
store8 7800000000000000202 r14
mov r14 r3
div r14 256
store8 7800000000000000203 r14
mov r14 r4
mod r14 256
store8 7800000000000000204 r14
mov r14 r4
div r14 256
store8 7800000000000000205 r14
mov r14 r4
mod r14 256
store8 7800000000000000096 r14
mov r14 r4
div r14 256
store8 7800000000000000097 r14
load8 r0 7800000000000000122
store8 7800000000000000127 r0
store8 7800000000000000135 2
store8 7800000000000000087 2
label m87_done
jmp open_bfs_selected
label open_bfs_selected
load8 r0 7800000000000000087
cmp r0 0
je open_bfs_scan
label m88_entry
# Single evidence view over the immutable old graph and new taught assertions.
# Input +200/202/204 S/P/O u16; output +208=0/1/2/3, +209 provenance bitmask.
load8 r2 7800000000000000200
load8 r14 7800000000000000201
mul r14 256
add r2 r14
load8 r3 7800000000000000202
load8 r14 7800000000000000203
mul r14 256
add r3 r14
load8 r4 7800000000000000204
load8 r14 7800000000000000205
mul r14 256
add r4 r14
set r8 0
set r9 0
set r10 0
cmp r2 0
je m88_finish
cmp r3 0
je m88_finish
cmp r4 0
je m88_finish
cmp r2 255
jgt m88_extension
cmp r3 255
jgt m88_extension
cmp r4 255
jgt m88_extension
mov r7 r2
mul r7 256
add r7 r3
mul r7 256
add r7 r4
mul r7 4
add r7 7400000000001000000
load8 r8 $r7
add r7 1
load8 r9 $r7
mov r0 r8
add r0 r9
cmp r0 0
je m88_extension
set r10 1
label m88_extension
mov r7 r2
mul r7 65536
add r7 r3
mul r7 65536
add r7 r4
mul r7 4
add r7 7800000010000000000
load8 r0 $r7
add r8 r0
add r7 1
load8 r1 $r7
add r9 r1
add r0 r1
cmp r0 0
je m88_finish
add r10 2
label m88_finish
set r0 0
cmp r8 0
je m88_negative
set r0 1
label m88_negative
cmp r9 0
je m88_done
add r0 2
label m88_done
store8 7800000000000000208 r0
store8 7800000000000000209 r10
jmp open_bfs_edge_ready
label open_bfs_edge_ready
load8 r0 7800000000000000087
cmp r0 2
jne open_bfs_traverse
load8 r0 7800000000000000208
cmp r0 1
je open_property_path
cmp r0 3
jne open_bfs_scan
store8 7800000000000000080 4
jmp open_reply
label open_bfs_traverse
label m89_entry
store8 7800000000000000234 0
load8 r0 7800000000000000208
cmp r0 1
jne m89_done
load8 r2 7800000000000000228
load8 r14 7800000000000000229
mul r14 256
add r2 r14
set r7 7800000000008100000
add r7 r2
load8 r0 $r7
cmp r0 0
jne m89_done
load8 r3 7800000000000000123
cmp r3 31
jge m89_depth_limit
load8 r4 7800000000000000120
cmp r4 64
jge m89_limit
mov r0 r4
add r0 1
store8 $r7 r0
store8 7800000000000000120 r0
set r7 7800000000008000000
mov r0 r4
mul r0 8
add r7 r0
mov r15 r7
mov r14 r2
mod r14 256
store8 $r15 r14
add r15 1
mov r14 r2
div r14 256
store8 $r15 r14
add r7 2
load8 r0 7800000000000000122
store8 $r7 r0
add r7 1
add r3 1
store8 $r7 r3
add r7 1
load8 r0 7800000000000000226
load8 r14 7800000000000000227
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
load8 r0 7800000000000000209
store8 $r7 r0
load8 r0 7800000000000000091
cmp r0 1
jne m89_done
load8 r0 7800000000000000090
cmp r0 1
jne m89_verify_goal
mov r14 r2
mod r14 256
store8 7800000000000000096 r14
mov r14 r2
div r14 256
store8 7800000000000000097 r14
load8 r0 7800000000000000122
store8 7800000000000000127 r0
store8 7800000000000000135 1
store8 7800000000000000234 4
jmp open_bfs_check
label m89_verify_goal
load8 r0 7800000000000000076
load8 r14 7800000000000000077
mul r14 256
add r0 r14
cmp r2 r0
jne m89_done
store8 7800000000000000124 r4
store8 7800000000000000235 0
store8 7800000000000000234 1
jmp open_bfs_check
label m89_depth_limit
store8 7800000000000000125 1
jmp open_bfs_check
label m89_limit
store8 7800000000000000080 9
store8 7800000000000000234 3
label m89_done
jmp open_bfs_check
label open_property_path
label m90_entry
# Validate every subgoal on the actual path before inheriting a wh-answer.
load8 r0 7800000000000000127
set r7 7800000000008000000
mul r0 8
add r7 r0
mov r15 r7
load8 r2 $r15
add r15 1
load8 r14 $r15
mul r14 256
add r2 r14
load8 r3 7800000000000000074
load8 r14 7800000000000000075
mul r14 256
add r3 r14
load8 r4 7800000000000000096
load8 r14 7800000000000000097
mul r14 256
add r4 r14
mov r14 r2
mod r14 256
store8 7800000000000000200 r14
mov r14 r2
div r14 256
store8 7800000000000000201 r14
mov r14 r3
mod r14 256
store8 7800000000000000202 r14
mov r14 r3
div r14 256
store8 7800000000000000203 r14
mov r14 r4
mod r14 256
store8 7800000000000000204 r14
mov r14 r4
div r14 256
store8 7800000000000000205 r14
jmp m91_entry
label m91_entry
# Single evidence view over the immutable old graph and new taught assertions.
# Input +200/202/204 S/P/O u16; output +208=0/1/2/3, +209 provenance bitmask.
load8 r2 7800000000000000200
load8 r14 7800000000000000201
mul r14 256
add r2 r14
load8 r3 7800000000000000202
load8 r14 7800000000000000203
mul r14 256
add r3 r14
load8 r4 7800000000000000204
load8 r14 7800000000000000205
mul r14 256
add r4 r14
set r8 0
set r9 0
set r10 0
cmp r2 0
je m91_finish
cmp r3 0
je m91_finish
cmp r4 0
je m91_finish
cmp r2 255
jgt m91_extension
cmp r3 255
jgt m91_extension
cmp r4 255
jgt m91_extension
mov r7 r2
mul r7 256
add r7 r3
mul r7 256
add r7 r4
mul r7 4
add r7 7400000000001000000
load8 r8 $r7
add r7 1
load8 r9 $r7
mov r0 r8
add r0 r9
cmp r0 0
je m91_extension
set r10 1
label m91_extension
mov r7 r2
mul r7 65536
add r7 r3
mul r7 65536
add r7 r4
mul r7 4
add r7 7800000010000000000
load8 r0 $r7
add r8 r0
add r7 1
load8 r1 $r7
add r9 r1
add r0 r1
cmp r0 0
je m91_finish
add r10 2
label m91_finish
set r0 0
cmp r8 0
je m91_negative
set r0 1
label m91_negative
cmp r9 0
je m91_done
add r0 2
label m91_done
store8 7800000000000000208 r0
store8 7800000000000000209 r10
jmp m92_entry
label m92_entry
# +137: 0 continue path,1 accept,2 explicit exception,3 conflict.
load8 r0 7800000000000000208
cmp r0 2
je m92_negative
cmp r0 3
je m92_conflict
load8 r0 7800000000000000127
set r7 7800000000008000002
mul r0 8
add r7 r0
load8 r0 $r7
cmp r0 255
je m92_accept
store8 7800000000000000127 r0
store8 7800000000000000137 0
jmp open_property_path_ready
label m92_accept
store8 7800000000000000137 1
jmp open_property_path_ready
label m92_negative
store8 7800000000000000137 2
jmp open_property_path_ready
label m92_conflict
store8 7800000000000000080 4
store8 7800000000000000137 3
jmp open_property_path_ready
label open_property_path_ready
load8 r0 7800000000000000137
cmp r0 0
je open_property_path
cmp r0 2
je open_bfs_scan
cmp r0 3
je open_reply
label m93_entry
# Append a validated inferred answer; preserve one proof reference only when
# there is exactly one answer. Multiple answers never receive a misleading
# single path presented as if it explained every clause.
load8 r2 7800000000000000096
load8 r14 7800000000000000097
mul r14 256
add r2 r14
load8 r3 7800000000000000082
set r0 0
label m93_duplicate
cmp r0 r3
jge m93_append
set r7 7800000000008300000
mov r1 r0
mul r1 2
add r7 r1
mov r15 r7
load8 r1 $r15
add r15 1
load8 r14 $r15
mul r14 256
add r1 r14
cmp r1 r2
je m93_done
add r0 1
jmp m93_duplicate
label m93_append
cmp r3 8
jge m93_limit
set r7 7800000000008300000
mov r1 r3
mul r1 2
add r7 r1
mov r15 r7
mov r14 r2
mod r14 256
store8 $r15 r14
add r15 1
mov r14 r2
div r14 256
store8 $r15 r14
add r3 1
store8 7800000000000000082 r3
store8 7800000000000000080 1
cmp r3 1
jne m93_done
store8 7800000000000000136 1
mov r14 r2
mod r14 256
store8 7800000000000000132 r14
mov r14 r2
div r14 256
store8 7800000000000000133 r14
load8 r0 7800000000000000135
cmp r0 1
je m93_transitive
load8 r0 7800000000000000122
store8 7800000000000000130 r0
store8 7800000000000000131 1
jmp open_property_derived_ready
label m93_transitive
# bfs-accept placed the new node at queue_count-1.
load8 r0 7800000000000000120
sub r0 1
store8 7800000000000000130 r0
store8 7800000000000000131 0
jmp open_property_derived_ready
label m93_limit
store8 7800000000000000080 9
label m93_done
jmp open_property_derived_ready
label open_property_derived_ready
load8 r0 7800000000000000080
cmp r0 9
je open_reply
jmp open_bfs_scan
label open_bfs_advance
load8 r0 7800000000000000122
add r0 1
store8 7800000000000000122 r0
jmp open_bfs_node
label open_bfs_complete
load8 r0 7800000000000000090
cmp r0 1
jne open_reply
load8 r0 7800000000000000082
cmp r0 1
jne open_reply
load8 r0 7800000000000000136
cmp r0 1
jne open_reply
load8 r0 7800000000000000130
store8 7800000000000000124 r0
load8 r0 7800000000000000131
store8 7800000000000000235 r0
label open_proof
label m94_entry
# Reconstruct actual edge labels. Reverse proof records contain node u16 and
# the predicate of its incoming edge. No invented free-form explanation.
load8 r0 7800000000000000235
cmp r0 1
jne m94_walk
load8 r2 7800000000000000076
load8 r14 7800000000000000077
mul r14 256
add r2 r14
load8 r0 7800000000000000090
cmp r0 1
jne m94_proof_target_ready
load8 r2 7800000000000000132
load8 r14 7800000000000000133
mul r14 256
add r2 r14
label m94_proof_target_ready
mov r14 r2
mod r14 256
store8 7800000000008200000 r14
mov r14 r2
div r14 256
store8 7800000000008200001 r14
load8 r2 7800000000000000074
load8 r14 7800000000000000075
mul r14 256
add r2 r14
mov r14 r2
mod r14 256
store8 7800000000008200002 r14
mov r14 r2
div r14 256
store8 7800000000008200003 r14
store8 7800000000000000121 1
label m94_walk
load8 r0 7800000000000000124
set r7 7800000000008000000
mul r0 8
add r7 r0
mov r15 r7
load8 r2 $r15
add r15 1
load8 r14 $r15
mul r14 256
add r2 r14
add r7 2
load8 r3 $r7
add r7 2
mov r15 r7
load8 r4 $r15
add r15 1
load8 r14 $r15
mul r14 256
add r4 r14
add r7 2
load8 r5 $r7
cmp r5 2
jlt m94_source_ready
store8 7800000000000000089 1
label m94_source_ready
load8 r6 7800000000000000121
cmp r6 32
jge m94_limit
set r7 7800000000008200000
mov r0 r6
mul r0 4
add r7 r0
mov r15 r7
mov r14 r2
mod r14 256
store8 $r15 r14
add r15 1
mov r14 r2
div r14 256
store8 $r15 r14
add r7 2
mov r15 r7
mov r14 r4
mod r14 256
store8 $r15 r14
add r15 1
mov r14 r4
div r14 256
store8 $r15 r14
add r6 1
store8 7800000000000000121 r6
cmp r3 255
je m94_found
store8 7800000000000000124 r3
jmp m94_walk
label m94_found
store8 7800000000000000080 1
load8 r0 7800000000000000076
load8 r14 7800000000000000077
mul r14 256
add r0 r14
load8 r1 7800000000000000090
cmp r1 1
jne m94_found_target_ready
load8 r0 7800000000000000132
load8 r14 7800000000000000133
mul r14 256
add r0 r14
label m94_found_target_ready
mov r14 r0
mod r14 256
store8 7800000000008300000 r14
mov r14 r0
div r14 256
store8 7800000000008300001 r14
store8 7800000000000000082 1
jmp open_reply
label m94_limit
store8 7800000000000000080 9
jmp open_reply
label open_property
label m95_entry
# Enumerate sparse registered edges, never all 65536 possible entity IDs.
# Return +224/226/228 S/P/O; +231 ready. Cursor +92 advances before return.
load8 r0 7800000000000000092
load8 r14 7800000000000000093
mul r14 256
add r0 r14
load8 r1 7400000000000000006
load8 r14 7400000000000000007
mul r14 256
add r1 r14
cmp r0 r1
jlt m95_legacy
sub r0 r1
load8 r1 7800000000000000008
load8 r14 7800000000000000009
mul r14 256
add r1 r14
cmp r0 r1
jge m95_done
set r7 7800000000000200000
mul r0 6
add r7 r0
mov r15 r7
load8 r2 $r15
add r15 1
load8 r14 $r15
mul r14 256
add r2 r14
add r7 2
mov r15 r7
load8 r3 $r15
add r15 1
load8 r14 $r15
mul r14 256
add r3 r14
add r7 2
mov r15 r7
load8 r4 $r15
add r15 1
load8 r14 $r15
mul r14 256
add r4 r14
jmp m95_ready
label m95_legacy
set r7 7400000000000080000
mul r0 3
add r7 r0
load8 r2 $r7
add r7 1
load8 r3 $r7
add r7 1
load8 r4 $r7
label m95_ready
mov r14 r2
mod r14 256
store8 7800000000000000224 r14
mov r14 r2
div r14 256
store8 7800000000000000225 r14
mov r14 r3
mod r14 256
store8 7800000000000000226 r14
mov r14 r3
div r14 256
store8 7800000000000000227 r14
mov r14 r4
mod r14 256
store8 7800000000000000228 r14
mov r14 r4
div r14 256
store8 7800000000000000229 r14
load8 r0 7800000000000000092
load8 r14 7800000000000000093
mul r14 256
add r0 r14
add r0 1
mov r14 r0
mod r14 256
store8 7800000000000000092 r14
mov r14 r0
div r14 256
store8 7800000000000000093 r14
store8 7800000000000000231 1
jmp open_property_candidate
label m95_done
store8 7800000000000000231 0
jmp open_property_candidate
label open_property_candidate
load8 r0 7800000000000000231
cmp r0 0
je open_property_reasoning
label m96_entry
store8 7800000000000000087 0
load8 r0 7800000000000000231
cmp r0 1
jne m96_done
load8 r2 7800000000000000224
load8 r14 7800000000000000225
mul r14 256
add r2 r14
load8 r3 7800000000000000226
load8 r14 7800000000000000227
mul r14 256
add r3 r14
load8 r4 7800000000000000228
load8 r14 7800000000000000229
mul r14 256
add r4 r14
load8 r0 7800000000000000072
load8 r14 7800000000000000073
mul r14 256
add r0 r14
cmp r2 r0
jne m96_done
load8 r0 7800000000000000074
load8 r14 7800000000000000075
mul r14 256
add r0 r14
cmp r3 r0
jne m96_done
mov r14 r2
mod r14 256
store8 7800000000000000200 r14
mov r14 r2
div r14 256
store8 7800000000000000201 r14
mov r14 r3
mod r14 256
store8 7800000000000000202 r14
mov r14 r3
div r14 256
store8 7800000000000000203 r14
mov r14 r4
mod r14 256
store8 7800000000000000204 r14
mov r14 r4
div r14 256
store8 7800000000000000205 r14
mov r14 r4
mod r14 256
store8 7800000000000000096 r14
mov r14 r4
div r14 256
store8 7800000000000000097 r14
store8 7800000000000000087 1
label m96_done
jmp open_property_selected
label open_property_selected
load8 r0 7800000000000000087
cmp r0 0
je open_property
label m97_entry
# Single evidence view over the immutable old graph and new taught assertions.
# Input +200/202/204 S/P/O u16; output +208=0/1/2/3, +209 provenance bitmask.
load8 r2 7800000000000000200
load8 r14 7800000000000000201
mul r14 256
add r2 r14
load8 r3 7800000000000000202
load8 r14 7800000000000000203
mul r14 256
add r3 r14
load8 r4 7800000000000000204
load8 r14 7800000000000000205
mul r14 256
add r4 r14
set r8 0
set r9 0
set r10 0
cmp r2 0
je m97_finish
cmp r3 0
je m97_finish
cmp r4 0
je m97_finish
cmp r2 255
jgt m97_extension
cmp r3 255
jgt m97_extension
cmp r4 255
jgt m97_extension
mov r7 r2
mul r7 256
add r7 r3
mul r7 256
add r7 r4
mul r7 4
add r7 7400000000001000000
load8 r8 $r7
add r7 1
load8 r9 $r7
mov r0 r8
add r0 r9
cmp r0 0
je m97_extension
set r10 1
label m97_extension
mov r7 r2
mul r7 65536
add r7 r3
mul r7 65536
add r7 r4
mul r7 4
add r7 7800000010000000000
load8 r0 $r7
add r8 r0
add r7 1
load8 r1 $r7
add r9 r1
add r0 r1
cmp r0 0
je m97_finish
add r10 2
label m97_finish
set r0 0
cmp r8 0
je m97_negative
set r0 1
label m97_negative
cmp r9 0
je m97_done
add r0 2
label m97_done
store8 7800000000000000208 r0
store8 7800000000000000209 r10
jmp m98_entry
label m98_entry
load8 r0 7800000000000000208
cmp r0 3
je m98_conflict
cmp r0 1
jne m98_done
load8 r0 7800000000000000209
cmp r0 2
jlt m98_result
store8 7800000000000000089 1
label m98_result
load8 r2 7800000000000000096
load8 r14 7800000000000000097
mul r14 256
add r2 r14
load8 r3 7800000000000000082
set r0 0
label m98_duplicate
cmp r0 r3
jge m98_append
set r7 7800000000008300000
mov r1 r0
mul r1 2
add r7 r1
mov r15 r7
load8 r1 $r15
add r15 1
load8 r14 $r15
mul r14 256
add r1 r14
cmp r1 r2
je m98_done
add r0 1
jmp m98_duplicate
label m98_append
cmp r3 8
jge m98_limit
set r7 7800000000008300000
mov r1 r3
mul r1 2
add r7 r1
mov r15 r7
mov r14 r2
mod r14 256
store8 $r15 r14
add r15 1
mov r14 r2
div r14 256
store8 $r15 r14
add r3 1
store8 7800000000000000082 r3
store8 7800000000000000080 1
jmp open_property_accepted
label m98_conflict
store8 7800000000000000080 4
jmp open_property_accepted
label m98_limit
store8 7800000000000000080 9
label m98_done
jmp open_property_accepted
label open_property_accepted
load8 r0 7800000000000000080
cmp r0 4
je open_reply
cmp r0 9
je open_reply
jmp open_property
label open_property_reasoning
label m99_entry
load8 r0 7800000000000000074
load8 r14 7800000000000000075
mul r14 256
add r0 r14
cmp r0 255
jgt m99_extended
store8 7400000000000000011 r0
store8 7800000000000000087 1
jmp open_rule_ready
label m99_extended
store8 7800000000000000087 0
jmp open_rule_ready
label open_reply
label m100_entry
store8 7700000000000000010 0
store8 7700000000000000039 0
store8 7700000000000000038 0
load8 r0 7800000000000000080
cmp r0 0
jne m100_status
set r0 3
store8 7800000000000000080 3
label m100_status
cmp r0 13
je m100_social_act
cmp r0 2
jle m100_supported
store8 7800000000000000012 0
load8 r1 7800000000000000063
cmp r1 2
jne m100_act
cmp r0 5
jlt m100_compact_unknown
cmp r0 7
jgt m100_compact_unknown
label m100_act
cmp r0 5
je m100_learn
cmp r0 6
je m100_alias
cmp r0 7
je m100_forget
cmp r0 3
je m100_unknown
cmp r0 4
je m100_conflict
cmp r0 8
je m100_clarify
cmp r0 10
je m100_ambiguous_act
cmp r0 11
je m100_collision_act
cmp r0 12
je m100_context_act
set r0 7
jmp m100_act_ready
label m100_learn
set r0 1
jmp m100_act_ready
label m100_alias
set r0 2
jmp m100_act_ready
label m100_forget
set r0 3
jmp m100_act_ready
label m100_unknown
set r0 4
jmp m100_act_ready
label m100_conflict
set r0 5
jmp m100_act_ready
label m100_clarify
set r0 6
jmp m100_act_ready
label m100_ambiguous_act
set r0 11
jmp m100_act_ready
label m100_collision_act
set r0 12
jmp m100_act_ready
label m100_context_act
set r0 16
jmp m100_act_ready
label m100_social_act
load8 r0 7800000000000000079
cmp r0 17
jlt m100_invalid
cmp r0 24
jgt m100_invalid
label m100_act_ready
store8 7800000000000000304 r0
store8 7800000000000000302 2
jmp open_reply_route
label m100_compact_unknown
set r14 63
print r14
store8 7800000000000000302 0
jmp open_reply_route
label m100_supported
store8 7800000000000000012 1
load8 r0 7800000000000000090
store8 7800000000000000013 r0
load8 r0 7800000000000000072
load8 r14 7800000000000000073
mul r14 256
add r0 r14
mov r14 r0
mod r14 256
store8 7800000000000000014 r14
mov r14 r0
div r14 256
store8 7800000000000000015 r14
load8 r0 7800000000000000074
load8 r14 7800000000000000075
mul r14 256
add r0 r14
mov r14 r0
mod r14 256
store8 7800000000000000016 r14
mov r14 r0
div r14 256
store8 7800000000000000017 r14
load8 r0 7800000000000000076
load8 r14 7800000000000000077
mul r14 256
add r0 r14
mov r14 r0
mod r14 256
store8 7800000000000000018 r14
mov r14 r0
div r14 256
store8 7800000000000000019 r14
load8 r0 7800000000000000080
cmp r0 2
jne m100_output_mode
load8 r0 7400000000000000003
cmp r0 2
jne m100_output_mode
load8 r0 7800000000000000074
load8 r14 7800000000000000075
mul r14 256
add r0 r14
load8 r1 7800000000000000032
load8 r14 7800000000000000033
mul r14 256
add r1 r14
cmp r0 r1
je m100_output_mode
set r7 7800000000009000000
mul r0 34
add r7 r0
load8 r0 $r7
cmp r0 0
je m100_quoted_negative
store8 7800000000000000139 1
jmp m100_output_mode
label m100_quoted_negative
store8 7800000000000000138 2
label m100_output_mode
load8 r0 7800000000000000063
cmp r0 2
je m100_compact
set r0 8
load8 r1 7800000000000000085
cmp r1 0
je m100_prefix
set r0 9
label m100_prefix
store8 7800000000000000304 r0
store8 7800000000000000302 3
jmp open_reply_route
label m100_compact
store8 7800000000000000302 1
jmp open_reply_route
label m100_invalid
div r0 0
label open_reply_route
load8 r0 7800000000000000302
cmp r0 0
je cleanup
cmp r0 1
je open_body
load8 r0 7800000000000000304
label m101_entry
# Teacher-supplied surface fragments at +500000. r0 is act number 1..15.
cmp r0 1
jlt m101_invalid
cmp r0 24
jgt m101_invalid
sub r0 1
mul r0 512
set r7 7800000000000500000
add r7 r0
load8 r0 7400000000000000003
sub r0 1
mul r0 256
add r7 r0
load8 r6 $r7
cmp r6 1
jlt m101_invalid
add r7 1
set r13 0
jmp m102_entry
label m101_invalid
div r0 0
label m102_entry
# Print selected memory bytes, including Spanish UTF-8 initial capitalization.
# No words, facts or response choice in the transport.
cmp r6 1
jlt m102_invalid
cmp r6 255
jgt m102_invalid
load8 r0 7700000000000000039
cmp r0 1
jne m102_begin
set r14 32
print r14
label m102_begin
set r3 0
label m102_letter
cmp r3 r6
jge m102_done
mov r4 r7
add r4 r3
load8 r14 $r4
cmp r14 95
jne m102_case_check
set r14 32
label m102_case_check
cmp r13 0
je m102_print_byte
cmp r14 195
je m102_print_byte
cmp r3 0
jne m102_latin_initial
cmp r14 97
jlt m102_case_done
cmp r14 122
jgt m102_case_done
sub r14 32
jmp m102_case_done
label m102_latin_initial
cmp r3 1
jne m102_case_done
load8 r0 $r7
cmp r0 195
jne m102_case_done
cmp r14 160
jlt m102_case_done
cmp r14 191
jgt m102_case_done
cmp r14 183
je m102_case_done
sub r14 32
label m102_case_done
set r13 0
label m102_print_byte
print r14
add r3 1
jmp m102_letter
label m102_done
store8 7700000000000000039 1
store8 7700000000000000038 0
jmp open_prefix_done
label m102_invalid
div r0 0
label open_prefix_done
load8 r0 7800000000000000080
cmp r0 2
jgt cleanup
load8 r0 7800000000000000138
cmp r0 2
jne open_prefix_body
set r0 14
label m103_entry
# Teacher-supplied surface fragments at +500000. r0 is act number 1..15.
cmp r0 1
jlt m103_invalid
cmp r0 24
jgt m103_invalid
sub r0 1
mul r0 512
set r7 7800000000000500000
add r7 r0
load8 r0 7400000000000000003
sub r0 1
mul r0 256
add r7 r0
load8 r6 $r7
cmp r6 1
jlt m103_invalid
add r7 1
set r13 0
jmp m104_entry
label m103_invalid
div r0 0
label m104_entry
# Print selected memory bytes, including Spanish UTF-8 initial capitalization.
# No words, facts or response choice in the transport.
cmp r6 1
jlt m104_invalid
cmp r6 255
jgt m104_invalid
load8 r0 7700000000000000039
cmp r0 1
jne m104_begin
set r14 32
print r14
label m104_begin
set r3 0
label m104_letter
cmp r3 r6
jge m104_done
mov r4 r7
add r4 r3
load8 r14 $r4
cmp r14 95
jne m104_case_check
set r14 32
label m104_case_check
cmp r13 0
je m104_print_byte
cmp r14 195
je m104_print_byte
cmp r3 0
jne m104_latin_initial
cmp r14 97
jlt m104_case_done
cmp r14 122
jgt m104_case_done
sub r14 32
jmp m104_case_done
label m104_latin_initial
cmp r3 1
jne m104_case_done
load8 r0 $r7
cmp r0 195
jne m104_case_done
cmp r14 160
jlt m104_case_done
cmp r14 191
jgt m104_case_done
cmp r14 183
je m104_case_done
sub r14 32
label m104_case_done
set r13 0
label m104_print_byte
print r14
add r3 1
jmp m104_letter
label m104_done
store8 7700000000000000039 1
store8 7700000000000000038 0
jmp open_prefix_body
label m104_invalid
div r0 0
label open_prefix_body
store8 7700000000000000038 1
label open_body
label m105_entry
# Construct clauses and labeled proof paths from actual semantic results.
# +300 stage,+301 answer index,+302 dispatch (1 name,2 bytes,3 act,0 done).
load8 r0 7800000000000000309
cmp r0 1
je m105_proof
load8 r0 7800000000000000300
cmp r0 0
je m105_subject_article
cmp r0 1
je m105_subject
cmp r0 2
je m105_spanish_negative
cmp r0 3
je m105_predicate
cmp r0 4
je m105_english_negative
cmp r0 5
je m105_object_article
cmp r0 6
je m105_object
jmp m105_triple_done
label m105_subject_article
store8 7800000000000000300 1
load8 r2 7800000000000000072
load8 r14 7800000000000000073
mul r14 256
add r2 r14
jmp m105_article
label m105_subject
store8 7800000000000000300 2
load8 r2 7800000000000000072
load8 r14 7800000000000000073
mul r14 256
add r2 r14
jmp m105_name
label m105_spanish_negative
store8 7800000000000000300 3
load8 r0 7800000000000000138
cmp r0 2
je m105_predicate
load8 r0 7800000000000000080
cmp r0 2
jne m105_predicate
load8 r0 7400000000000000003
cmp r0 1
je m105_negative_word
load8 r0 7800000000000000139
cmp r0 1
jne m105_predicate
store8 7800000000000000304 13
store8 7800000000000000302 3
jmp open_body_dispatch
jmp m105_predicate
label m105_predicate
store8 7800000000000000300 4
load8 r2 7800000000000000074
load8 r14 7800000000000000075
mul r14 256
add r2 r14
load8 r0 7800000000000000139
cmp r0 1
jne m105_name
set r7 7800000000009000000
mov r0 r2
mul r0 34
add r7 r0
load8 r6 $r7
add r7 1
load8 r13 7700000000000000038
store8 7800000000000000302 2
jmp open_body_dispatch
jmp m105_name
label m105_english_negative
store8 7800000000000000300 5
load8 r0 7800000000000000080
cmp r0 2
jne m105_object_article
load8 r0 7400000000000000003
cmp r0 2
jne m105_object_article
load8 r0 7800000000000000074
load8 r14 7800000000000000075
mul r14 256
add r0 r14
load8 r1 7800000000000000032
load8 r14 7800000000000000033
mul r14 256
add r1 r14
cmp r0 r1
je m105_negative_word
jmp m105_object_article
label m105_negative_word
store8 7800000000000000304 10
store8 7800000000000000302 3
jmp open_body_dispatch
label m105_object_article
store8 7800000000000000300 6
load8 r0 7800000000000000301
set r7 7800000000008300000
mul r0 2
add r7 r0
mov r15 r7
load8 r2 $r15
add r15 1
load8 r14 $r15
mul r14 256
add r2 r14
jmp m105_article
label m105_object
store8 7800000000000000300 7
load8 r0 7800000000000000301
set r7 7800000000008300000
mul r0 2
add r7 r0
mov r15 r7
load8 r2 $r15
add r15 1
load8 r14 $r15
mul r14 256
add r2 r14
jmp m105_name
label m105_article
load8 r0 7800000000000000063
cmp r0 1
jne m105_no_article
load8 r0 7800000000000000074
load8 r14 7800000000000000075
mul r14 256
add r0 r14
load8 r1 7800000000000000032
load8 r14 7800000000000000033
mul r14 256
add r1 r14
cmp r0 r1
jne m105_no_article
cmp r2 255
jgt m105_no_article
set r7 7700000000000100102
mov r0 r2
mul r0 224
add r7 r0
load8 r0 7400000000000000003
sub r0 1
mul r0 112
add r7 r0
load8 r6 $r7
cmp r6 0
je m105_no_article
add r7 1
load8 r13 7700000000000000038
store8 7800000000000000302 2
jmp open_body_dispatch
label m105_no_article
load8 r0 7800000000000000300
cmp r0 1
je m105_subject
jmp m105_object
label m105_name
mov r14 r2
mod r14 256
store8 7800000000000000306 r14
mov r14 r2
div r14 256
store8 7800000000000000307 r14
store8 7800000000000000302 1
jmp open_body_dispatch
label m105_triple_done
load8 r0 7800000000000000301
add r0 1
load8 r1 7800000000000000082
cmp r0 r1
jge m105_response_done
store8 7800000000000000301 r0
store8 7800000000000000300 0
store8 7700000000000000038 0
load8 r2 7800000000000000003
cmp r2 1
jne m105_full_clause
load8 r2 7800000000000000063
cmp r2 1
jne m105_full_clause
# Same subject and predicate: enumerate all objects without repeating them.
store8 7800000000000000300 5
sub r1 1
cmp r0 r1
je m105_conjunction
store8 7700000000000000039 0
set r14 44
print r14
set r14 32
print r14
jmp m105_object_article
label m105_conjunction
store8 7800000000000000304 15
store8 7800000000000000302 3
jmp open_body_dispatch
label m105_full_clause
store8 7700000000000000039 0
set r14 59
print r14
set r14 32
print r14
jmp m105_subject_article
label m105_response_done
set r14 46
print r14
# E018 explicitly configured brevity affects presentation, not search.
# Historical checkpoints (preference 0) and the compact API keep their proofs.
load8 r0 7800000000000000003
cmp r0 1
jne m105_show_proof
load8 r0 7800000000000000063
cmp r0 1
jne m105_show_proof
load8 r0 7800000000000000085
cmp r0 1
jne m105_done
label m105_show_proof
load8 r0 7800000000000000121
cmp r0 2
jlt m105_done
sub r0 1
store8 7800000000000000311 r0
store8 7800000000000000309 1
store8 7700000000000000038 0
store8 7700000000000000039 0
set r14 32
print r14
set r14 91
print r14
label m105_proof
load8 r0 7800000000000000310
cmp r0 0
je m105_proof_node
cmp r0 2
je m105_after_predicate
load8 r0 7800000000000000311
cmp r0 0
je m105_proof_done
sub r0 1
store8 7800000000000000311 r0
set r7 7800000000008200002
mul r0 4
add r7 r0
mov r15 r7
load8 r2 $r15
add r15 1
load8 r14 $r15
mul r14 256
add r2 r14
store8 7800000000000000310 2
store8 7700000000000000039 0
set r14 32
print r14
set r14 45
print r14
print r14
jmp m105_name
label m105_after_predicate
store8 7700000000000000039 0
set r14 45
print r14
print r14
set r14 62
print r14
set r14 32
print r14
label m105_proof_node
load8 r0 7800000000000000311
set r7 7800000000008200000
mul r0 4
add r7 r0
mov r15 r7
load8 r2 $r15
add r15 1
load8 r14 $r15
mul r14 256
add r2 r14
store8 7800000000000000310 1
jmp m105_name
label m105_proof_done
set r14 93
print r14
label m105_done
store8 7800000000000000302 0
jmp open_body_dispatch
label open_body_dispatch
load8 r0 7800000000000000302
cmp r0 0
je cleanup
cmp r0 1
je open_body_name
cmp r0 2
je open_body_emit
load8 r0 7800000000000000304
label m106_entry
# Teacher-supplied surface fragments at +500000. r0 is act number 1..15.
cmp r0 1
jlt m106_invalid
cmp r0 24
jgt m106_invalid
sub r0 1
mul r0 512
set r7 7800000000000500000
add r7 r0
load8 r0 7400000000000000003
sub r0 1
mul r0 256
add r7 r0
load8 r6 $r7
cmp r6 1
jlt m106_invalid
add r7 1
set r13 0
jmp open_body_emit
label m106_invalid
div r0 0
label open_body_name
label m107_entry
# +306=u16 concept. +302=1 means use original C name resolver;2=direct bytes.
load8 r2 7800000000000000306
load8 r14 7800000000000000307
mul r14 256
add r2 r14
cmp r2 0
je m107_invalid
cmp r2 255
jgt m107_extended
store8 7700000000000000040 r2
store8 7800000000000000302 1
jmp open_name_route
label m107_extended
load8 r10 7800000000000000006
load8 r14 7800000000000000007
mul r14 256
add r10 r14
load8 r11 7400000000000000003
set r0 0
set r12 0
label m107_lexeme
cmp r0 r10
jge m107_fallback
set r7 8600000000000400000
mov r1 r0
mul r1 40
add r7 r1
mov r15 r7
load8 r1 $r15
add r15 1
load8 r14 $r15
mul r14 256
add r1 r14
cmp r1 r2
jne m107_next
cmp r12 0
jne m107_language
mov r12 r7
label m107_language
mov r8 r7
add r8 3
load8 r1 $r8
cmp r1 r11
je m107_selected
label m107_next
add r0 1
jmp m107_lexeme
label m107_fallback
cmp r12 0
je m107_invalid
mov r7 r12
label m107_selected
add r7 4
load8 r6 $r7
add r7 1
load8 r13 7700000000000000038
store8 7800000000000000302 2
jmp open_name_route
label m107_invalid
div r0 0
label open_name_route
load8 r0 7800000000000000302
cmp r0 2
je open_body_emit
label m108_entry
# Resolve 7700000000000000040 to an existing shared bilingual name. r7=bytes,r6=len,r13=case.
load8 r2 7700000000000000040
cmp r2 0
je m108_invalid
load8 r13 7700000000000000038
set r7 7700000000000010000
mov r0 r2
mul r0 4
add r7 r0
load8 r0 $r7
cmp r0 1
jne m108_language
set r13 1
label m108_language
load8 r15 7400000000000000003
cmp r2 22
jgt m108_new_name
set r7 7200000000000001000
mov r3 r2
sub r3 1
mul r3 32
add r7 r3
set r3 5
cmp r15 1
je m108_old_name
set r3 14
label m108_old_name
add r7 r3
load8 r6 $r7
add r7 1
jmp open_body_emit
label m108_new_name
load8 r10 7400000000000000004
load8 r3 7400000000000000005
mul r3 256
add r10 r3
set r3 0
label m108_lexeme
cmp r3 r10
jge m108_invalid
set r7 7400000000000010000
mov r4 r3
mul r4 40
add r7 r4
load8 r4 $r7
cmp r4 r2
jne m108_next_lexeme
mov r4 r7
add r4 2
load8 r5 $r4
cmp r5 r15
jne m108_next_lexeme
add r7 3
load8 r6 $r7
add r7 1
jmp open_body_emit
label m108_next_lexeme
add r3 1
jmp m108_lexeme
label m108_invalid
div r0 0
label open_body_emit
label m109_entry
# Print selected memory bytes, including Spanish UTF-8 initial capitalization.
# No words, facts or response choice in the transport.
cmp r6 1
jlt m109_invalid
cmp r6 255
jgt m109_invalid
load8 r0 7700000000000000039
cmp r0 1
jne m109_begin
set r14 32
print r14
label m109_begin
set r3 0
label m109_letter
cmp r3 r6
jge m109_done
mov r4 r7
add r4 r3
load8 r14 $r4
cmp r14 95
jne m109_case_check
set r14 32
label m109_case_check
cmp r13 0
je m109_print_byte
cmp r14 195
je m109_print_byte
cmp r3 0
jne m109_latin_initial
cmp r14 97
jlt m109_case_done
cmp r14 122
jgt m109_case_done
sub r14 32
jmp m109_case_done
label m109_latin_initial
cmp r3 1
jne m109_case_done
load8 r0 $r7
cmp r0 195
jne m109_case_done
cmp r14 160
jlt m109_case_done
cmp r14 191
jgt m109_case_done
cmp r14 183
je m109_case_done
sub r14 32
label m109_case_done
set r13 0
label m109_print_byte
print r14
add r3 1
jmp m109_letter
label m109_done
store8 7700000000000000039 1
store8 7700000000000000038 0
jmp open_body
label m109_invalid
div r0 0
label cleanup
label m110_entry
# E013: clear bounded actual intake and the visited-node queue, preserving the
# same E012 clean-state invariant. Token slots are cleared even after bad input.
load8 r2 7400000000000000017
load8 r3 7400000000000000050
set r0 0
label m110_visited
cmp r0 r3
jge m110_raw_start
set r7 7400000000000003000
add r7 r0
load8 r1 $r7
cmp r1 1
jlt m110_invalid
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
jmp m110_visited
label m110_raw_start
set r0 0
label m110_raw
cmp r0 r2
jge m110_token_start
set r7 7400000000000000128
add r7 r0
store8 $r7 0
add r0 1
jmp m110_raw
label m110_token_start
set r0 0
label m110_tokens
set r7 7400000000000000512
add r7 r0
store8 $r7 0
add r0 1
cmp r0 510
jlt m110_tokens
set r0 0
label m110_resolved
set r7 7400000000000001600
add r7 r0
store8 $r7 0
add r0 1
cmp r0 30
jlt m110_resolved
set r0 16
label m110_control
set r7 7400000000000000000
add r7 r0
store8 $r7 0
add r0 1
cmp r0 64
jlt m110_control
jmp m111_entry
label m110_invalid
div r0 0
label m111_entry
load8 r0 7700000000000000002
cmp r0 0
je m111_done
cmp r0 1
jne m111_invalid
set r0 16
label m111_scratch
set r7 7700000000000000000
add r7 r0
store8 $r7 0
add r0 1
cmp r0 256
jlt m111_scratch
label m111_done
jmp open_final_cleanup
label m111_invalid
div r0 0
label open_final_cleanup
load8 r0 7800000000000000002
cmp r0 1
jne finish
label m112_entry
load8 r0 7700000000000000002
cmp r0 0
je m112_done
cmp r0 1
jne m112_invalid
set r0 16
label m112_scratch
set r7 7700000000000000000
add r7 r0
store8 $r7 0
add r0 1
cmp r0 256
jlt m112_scratch
label m112_done
jmp m113_entry
label m112_invalid
div r0 0
label m113_entry
load8 r0 7800000000000000002
cmp r0 0
je m113_done
cmp r0 1
jne m113_invalid
# A delegated query is only a context if the actual legacy search succeeded.
# Do not preserve the speculative slots of an unanswered question.
load8 r0 7800000000000000067
cmp r0 0
jne m113_context_ready
load8 r0 7800000000000000012
cmp r0 1
jne m113_context_ready
load8 r0 7400000000000000008
cmp r0 1
je m113_context_ready
cmp r0 2
je m113_context_ready
store8 7800000000000000012 0
label m113_context_ready
# Clear keyed visitation only for nodes actually queued, then their records.
load8 r10 7800000000000000120
set r0 0
label m113_queue
cmp r0 r10
jge m113_proof_start
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
label m113_queue_bytes
cmp r1 8
jge m113_next_node
mov r8 r7
add r8 r1
store8 $r8 0
add r1 1
jmp m113_queue_bytes
label m113_next_node
add r0 1
jmp m113_queue
label m113_proof_start
load8 r10 7800000000000000121
mul r10 4
set r0 0
label m113_proof
cmp r0 r10
jge m113_result_start
set r7 7800000000008200000
add r7 r0
store8 $r7 0
add r0 1
jmp m113_proof
label m113_result_start
load8 r10 7800000000000000082
mul r10 2
set r0 0
label m113_results
cmp r0 r10
jge m113_control_start
set r7 7800000000008300000
add r7 r0
store8 $r7 0
add r0 1
jmp m113_results
label m113_control_start
set r0 63
label m113_control
set r7 7800000000000000000
add r7 r0
store8 $r7 0
add r0 1
cmp r0 512
jlt m113_control
set r0 1024
label m113_tokens
set r7 7800000000000000000
add r7 r0
store8 $r7 0
add r0 1
cmp r0 1084
jlt m113_tokens
set r0 2048
label m113_descriptors
set r7 7800000000000000000
add r7 r0
store8 $r7 0
add r0 1
cmp r0 2108
jlt m113_descriptors
label m113_done
jmp m114_entry
label m113_invalid
div r0 0
label m114_entry
# Eight most recent supported factual topics. These are references, not cached
# answers: resuming always performs a fresh evidence search in the same state.
load8 r0 8000000000000000003
cmp r0 1
jne m114_done
load8 r0 7800000000000000012
cmp r0 1
jne m114_clean
load8 r8 7800000000000000014
load8 r14 7800000000000000015
mul r14 256
add r8 r14
set r10 0
label m114_find
cmp r10 64
jge m114_evict
set r7 8600000000000030000
mov r0 r10
mul r0 16
add r7 r0
load8 r0 $r7
cmp r0 1
jne m114_shift_start
add r7 2
load8 r0 $r7
add r7 1
load8 r14 $r7
mul r14 256
add r0 r14
cmp r0 r8
je m114_shift_start
add r10 1
jmp m114_find
label m114_evict
set r10 63
label m114_shift_start
cmp r10 0
je m114_insert
set r0 0
label m114_shift_byte
set r7 8600000000000030000
mov r1 r10
sub r1 1
mul r1 16
add r7 r1
add r7 r0
load8 r2 $r7
add r7 16
store8 $r7 r2
add r0 1
cmp r0 16
jlt m114_shift_byte
sub r10 1
jmp m114_shift_start
label m114_insert
set r0 0
label m114_insert_byte
set r7 7800000000000000012
add r7 r0
load8 r2 $r7
set r7 8600000000000030000
add r7 r0
store8 $r7 r2
add r0 1
cmp r0 8
jlt m114_insert_byte
label m114_clean
set r0 16
label m114_clean_byte
set r7 8000000000000000000
add r7 r0
store8 $r7 0
add r0 1
cmp r0 64
jlt m114_clean_byte
label m114_done
jmp m115_entry
label m115_entry
load8 r0 8100000000000000002
cmp r0 1
jne m115_done
set r0 16
label m115_control
set r7 8100000000000000000
add r7 r0
store8 $r7 0
add r0 1
cmp r0 128
jlt m115_control
set r0 512
label m115_target
set r7 8100000000000000000
add r7 r0
store8 $r7 0
add r0 1
cmp r0 768
jlt m115_target
set r0 1000
label m115_original
set r7 8100000000000000000
add r7 r0
store8 $r7 0
add r0 1
cmp r0 1602
jlt m115_original
set r0 2000
label m115_output
set r7 8100000000000000000
add r7 r0
store8 $r7 0
add r0 1
cmp r0 2600
jlt m115_output
label m115_done
jmp finish
label finish
halt
