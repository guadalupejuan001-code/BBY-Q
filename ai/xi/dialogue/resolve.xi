#!reverse-pc-machine-v1
# Resolve every word through E010's existing bilingual numerals and E011's
# learned operator lexicon. Decimal notation is a designed base-10 grammar,
# anchored to the ten learned digit concepts; it is not a learned number name.
# Resolution +800+i*4: kind 1=number 2=operator 0=unknown; low/high value.
load8 r0 7300000000000000002
cmp r0 1
jne invalid
load8 r0 7300000000000000016
cmp r0 1
jne invalid
load8 r0 7300000000000000040
cmp r0 0
jne done
load8 r15 7300000000000000032
cmp r15 15
jgt invalid
set r0 0
label each_token
cmp r0 r15
jge done
set r1 7300000000000000512
mov r2 r0
mul r2 18
add r1 r2
load8 r2 $r1
set r3 0
set r4 0
# First try a decimal string, requiring a learned grounding for every digit.
label decimal_chars
cmp r3 r2
jge decimal_complete
mov r5 r1
add r5 1
add r5 r3
load8 r6 $r5
cmp r6 48
jlt lexical_number
cmp r6 57
jgt lexical_number
sub r6 48
load8 r7 7200000000000000010
set r8 0
label ground_digit
cmp r8 r7
jge unresolved
set r9 7200000000000001000
mov r10 r8
mul r10 32
add r9 r10
load8 r10 $r9
cmp r10 4
jne next_digit_concept
add r9 1
load8 r10 $r9
cmp r10 r6
jne next_digit_concept
add r9 3
load8 r10 $r9
cmp r10 2
jlt next_digit_concept
mul r4 10
add r4 r6
cmp r4 65535
jgt unresolved
add r3 1
jmp decimal_chars
label next_digit_concept
add r8 1
jmp ground_digit
label decimal_complete
set r12 1
jmp save_resolution
label lexical_number
load8 r7 7200000000000000010
set r8 0
set r11 0
label each_numeral
cmp r8 r7
jge learned_operator
set r9 7200000000000001000
mov r10 r8
mul r10 32
add r9 r10
load8 r10 $r9
cmp r10 4
jne next_numeral
mov r10 r9
add r10 4
load8 r10 $r10
cmp r10 2
jlt next_numeral
set r13 5
label each_language
mov r10 r9
add r10 r13
load8 r10 $r10
cmp r10 r2
jne next_language
set r3 0
label lexical_chars
cmp r3 r2
jge numeral_match
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
jne next_language
add r3 1
jmp lexical_chars
label numeral_match
mov r5 r9
add r5 1
load8 r6 $r5
cmp r11 0
je first_numeral_match
cmp r4 r6
jne unresolved
jmp next_language
label first_numeral_match
set r11 1
mov r4 r6
label next_language
cmp r13 5
jne next_numeral
set r13 14
jmp each_language
label next_numeral
add r8 1
jmp each_numeral
label learned_operator
cmp r11 1
je resolved_number
load8 r7 7300000000000000004
cmp r7 32
jgt invalid
set r8 0
label each_operator
cmp r8 r7
jge unresolved
set r9 7300000000000001000
mov r10 r8
mul r10 32
add r9 r10
load8 r10 $r9
cmp r10 r2
jne next_operator
mov r5 r9
add r5 18
load8 r10 $r5
cmp r10 2
jlt next_operator
set r3 0
label operator_chars
cmp r3 r2
jge operator_match
mov r5 r1
add r5 1
add r5 r3
load8 r6 $r5
mov r5 r9
add r5 1
add r5 r3
load8 r10 $r5
cmp r6 r10
jne next_operator
add r3 1
jmp operator_chars
label operator_match
add r9 17
load8 r4 $r9
set r12 2
jmp save_resolution
label next_operator
add r8 1
jmp each_operator
label resolved_number
set r12 1
jmp save_resolution
label unresolved
# Optional E020 spellings refer to sealed, independently validated concepts.
# No mapping from a Spanish/English spelling to an arithmetic family here.
load8 r7 7900000000000000003
cmp r7 1
jne no_scale_word
load8 r7 7900000000000000004
cmp r7 32
jgt invalid
set r8 0
label scale_operator
cmp r8 r7
jge no_scale_word
set r9 7900000000000001000
mov r10 r8
mul r10 32
add r9 r10
load8 r10 $r9
cmp r10 r2
jne next_scale_operator
set r3 0
label scale_chars
cmp r3 r2
jge scale_match
mov r5 r1
add r5 1
add r5 r3
load8 r6 $r5
mov r5 r9
add r5 1
add r5 r3
load8 r10 $r5
cmp r6 r10
jne next_scale_operator
add r3 1
jmp scale_chars
label scale_match
add r9 17
load8 r4 $r9
cmp r4 1
jlt invalid
cmp r4 8
jgt invalid
sub r4 1
mul r4 64
set r9 7900000000000000130
add r9 r4
load8 r4 $r9
cmp r4 1
jlt invalid
cmp r4 8
jgt invalid
set r12 2
jmp save_resolution
label next_scale_operator
add r8 1
jmp scale_operator
label no_scale_word
set r12 0
set r4 0
label save_resolution
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
jmp each_token
label done
halt
label invalid
div r0 0
