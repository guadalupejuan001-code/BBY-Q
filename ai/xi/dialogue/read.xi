#!reverse-pc-machine-v1
# Tokenize real text in XI. ASCII case folding, whitespace and final '?' only.
# Intake +16=1, +17=byte length, +128..382=raw bytes. Max 15 words of 16 bytes.
# Tokens +512, stride 18; parse error +40. No semantic answers in this stage.
load8 r0 7300000000000000002
cmp r0 1
jne invalid
load8 r0 7300000000000000016
cmp r0 1
jne invalid
load8 r9 7300000000000000017
cmp r9 0
je bad_text
set r0 0
set r1 0
set r2 0
set r10 0
store8 7300000000000000040 0
label char_loop
cmp r0 r9
jge end_text
set r7 7300000000000000128
add r7 r0
load8 r3 $r7
cmp r3 32
je separator
cmp r3 9
je separator
cmp r10 1
je bad_text
cmp r3 63
je question_mark
cmp r3 195
je conversational_accent
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
cmp r2 16
jge bad_text
set r7 7300000000000000513
mov r8 r1
mul r8 18
add r7 r8
add r7 r2
store8 $r7 r3
add r2 1
jmp next_char
label conversational_accent
# Accent folding is optional on the conversational surface. Old E011 models
# retain their ASCII protocol. Operator meanings still come from learned D.
load8 r7 7700000000000000016
cmp r7 1
jne bad_text
add r0 1
cmp r0 r9
jge bad_text
set r7 7300000000000000128
add r7 r0
load8 r3 $r7
cmp r3 129
je accent_a
cmp r3 137
je accent_e
cmp r3 141
je accent_i
cmp r3 147
je accent_o
cmp r3 154
je accent_u
cmp r3 161
je accent_a
cmp r3 169
je accent_e
cmp r3 173
je accent_i
cmp r3 179
je accent_o
cmp r3 186
je accent_u
jmp bad_text
label accent_a
set r3 97
jmp write_char
label accent_e
set r3 101
jmp write_char
label accent_i
set r3 105
jmp write_char
label accent_o
set r3 111
jmp write_char
label accent_u
set r3 117
jmp write_char
label question_mark
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
set r7 7300000000000000512
mov r8 r1
mul r8 18
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
set r7 7300000000000000512
mov r8 r1
mul r8 18
add r7 r8
store8 $r7 r2
add r1 1
label finish_tokens
cmp r1 0
je bad_text
store8 7300000000000000032 r1
halt
label bad_text
store8 7300000000000000040 1
store8 7300000000000000032 0
halt
label invalid
div r0 0
