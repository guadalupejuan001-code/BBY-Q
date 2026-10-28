#!reverse-pc-machine-v1
# Tokenize real text in XI. A trained E022 reader also allows a single Spanish
# opening question mark at a word boundary after a preamble ("oye, ¿qué...").
# Intake +16=1, +17=byte length, +128..382=raw bytes. Max 15 words of 32 bytes.
# Tokens +512, stride 34; parse error +40. No semantic answers in this stage.
load8 r0 7400000000000000002
cmp r0 1
jne invalid
load8 r0 7400000000000000016
cmp r0 1
jne invalid
load8 r9 7400000000000000017
cmp r9 0
je bad_text
set r0 0
set r1 0
set r2 0
set r10 0
set r11 0
store8 7400000000000000040 0
store8 7400000000000000047 0
label char_loop
cmp r0 r9
jge end_text
set r7 7400000000000000128
add r7 r0
load8 r3 $r7
cmp r3 44
jne ordinary_separator
load8 r7 8100000000000000003
cmp r7 1
je separator
label ordinary_separator
cmp r3 32
je separator
cmp r3 9
je separator
cmp r10 1
je bad_text
cmp r3 46
je period_mark
cmp r3 63
je question_mark
cmp r3 194
je inverted_question
cmp r3 195
je latin_character
cmp r3 95
je write_char
cmp r3 65
jlt check_digit
cmp r3 90
jgt check_alpha
add r3 32
label check_alpha
cmp r3 97
jlt bad_text
cmp r3 122
jgt bad_text
jmp write_char
label check_digit
cmp r3 48
jlt bad_text
cmp r3 57
jgt bad_text
label write_char
cmp r1 15
jge bad_text
cmp r2 32
jge bad_text
set r7 7400000000000000513
mov r8 r1
mul r8 34
add r7 r8
add r7 r2
store8 $r7 r3
add r2 1
jmp next_char
label inverted_question
cmp r11 0
jne bad_text
cmp r1 0
je opening_question
load8 r7 8100000000000000003
cmp r7 1
jne bad_text
label opening_question
cmp r2 0
jne bad_text
add r0 1
cmp r0 r9
jge bad_text
set r7 7400000000000000128
add r7 r0
load8 r3 $r7
cmp r3 191
jne bad_text
set r11 1
store8 7400000000000000047 1
jmp next_char
label latin_character
# Canonical Latin-1 UTF-8: Spanish accents and enye, including uppercase.
cmp r1 15
jge bad_text
cmp r2 30
jgt bad_text
set r7 7400000000000000513
mov r8 r1
mul r8 34
add r7 r8
add r7 r2
store8 $r7 195
add r2 1
add r0 1
cmp r0 r9
jge bad_text
set r7 7400000000000000128
add r7 r0
load8 r3 $r7
cmp r3 128
jlt bad_text
cmp r3 191
jgt bad_text
cmp r3 159
jgt write_char
cmp r3 151
je bad_text
add r3 32
jmp write_char
label period_mark
# A final statement period is enabled only by the conversational XI surface.
load8 r7 7700000000000000016
cmp r7 1
jne bad_text
load8 r7 7700000000000000002
cmp r7 1
jne bad_text
cmp r11 0
jne bad_text
cmp r2 0
jne mark_terminal
cmp r1 0
je bad_text
jmp mark_terminal
label question_mark
store8 7400000000000000047 1
cmp r2 0
jne mark_terminal
cmp r1 0
je bad_text
label mark_terminal
set r10 1
jmp next_char
label separator
cmp r2 0
je next_char
set r7 7400000000000000512
mov r8 r1
mul r8 34
add r7 r8
store8 $r7 r2
add r1 1
set r2 0
label next_char
add r0 1
jmp char_loop
label end_text
cmp r2 0
je finish_tokens
set r7 7400000000000000512
mov r8 r1
mul r8 34
add r7 r8
store8 $r7 r2
add r1 1
label finish_tokens
cmp r1 0
je bad_text
store8 7400000000000000032 r1
halt
label bad_text
store8 7400000000000000040 1
store8 7400000000000000032 0
halt
label invalid
div r0 0
