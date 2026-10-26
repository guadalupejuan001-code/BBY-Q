#!reverse-pc-machine-v1
# BBY Q E009.1: a text line is tokenized INSIDE original XI.
# Accepted microgrammar: "sujeto predicado objeto?" (3 ASCII words).
# No Bash splitting, English parser, external LLM, or ungrounded vocabulary.
load8 r11 7100000000000000002
cmp r11 1
je language_ready
div r11 0
label language_ready
load8 r11 7100000000000000175
cmp r11 4
je raw_line_pending
div r11 0
label raw_line_pending
load8 r9 7100000000000000400
cmp r9 5
jge line_min
div r9 0
label line_min
cmp r9 32
jle line_max
div r9 0
label line_max
# A source frame must be empty. A failed parse must not publish a new RVPC2.
set r0 0
label assert_frame_empty
set r7 7100000000000000140
add r7 r0
load8 r11 $r7
cmp r11 0
je empty_frame_byte
div r11 0
label empty_frame_byte
add r0 1
cmp r0 29
jlt assert_frame_empty
set r0 0
set r1 0
set r2 0
label consume_text
cmp r0 r9
jge finish_last_word
set r7 7100000000000000401
add r7 r0
load8 r3 $r7
cmp r3 32
je word_separator
cmp r3 63
je terminal_question
# Only lowercase ASCII is accepted by this first explicit language grammar.
cmp r3 97
jge alpha_low
div r3 0
label alpha_low
cmp r3 122
jle alpha_high
div r3 0
label alpha_high
cmp r2 8
jlt letter_fits
div r2 0
label letter_fits
set r7 7100000000000000141
mov r8 r1
mul r8 10
add r7 r8
add r7 r2
store8 $r7 r3
add r2 1
add r0 1
jmp consume_text
label word_separator
# Reject doubled spaces, leading/trailing spaces and four-word sentences.
cmp r2 1
jge word_not_empty
div r2 0
label word_not_empty
cmp r1 2
jlt remaining_word_slot
div r1 0
label remaining_word_slot
set r7 7100000000000000140
mov r8 r1
mul r8 10
add r7 r8
store8 $r7 r2
add r1 1
set r2 0
add r0 1
cmp r0 r9
jlt consume_text
div r0 0
label terminal_question
# Question mark is allowed ONLY once, as the very last byte.
mov r11 r0
add r11 1
cmp r11 r9
je question_is_terminal
div r11 0
label question_is_terminal
jmp finish_last_word
label finish_last_word
cmp r1 2
je three_tokens_complete
div r1 0
label three_tokens_complete
cmp r2 1
jge last_token_nonempty
div r2 0
label last_token_nonempty
set r7 7100000000000000160
store8 $r7 r2
# Erase the raw text; durable lexical forms and semantic graph are untouched.
set r0 0
label erase_source_text
set r7 7100000000000000401
add r7 r0
store8 $r7 0
add r0 1
cmp r0 32
jlt erase_source_text
store8 7100000000000000400 0
store8 7100000000000000175 3
set r9 3
print r9
mem_stats
stats
