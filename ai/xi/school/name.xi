#!reverse-pc-machine-v1
# E010 XI bilingual naming: output bytes are taken ONLY from taught labels.
# 1=Spanish, 2=English; no words or translations in this executable.
load8 r12 7200000000000000000
cmp r12 83
je identity_ok
div r12 0
label identity_ok
load8 r12 7200000000000000201
cmp r12 1
je identified
set r14 63
print r14
halt
label identified
load8 r8 7200000000000000200
cmp r8 1
jge valid_index_low
div r8 0
label valid_index_low
load8 r9 7200000000000000010
cmp r8 r9
jle valid_index_high
div r8 0
label valid_index_high
sub r8 1
set r7 7200000000000001000
mul r8 32
add r7 r8
load8 r9 7200000000000000004
cmp r9 1
je spanish_output
cmp r9 2
je english_output
div r9 0
label spanish_output
mov r6 r7
add r6 5
load8 r5 $r6
set r4 6
jmp emit_lexeme
label english_output
mov r6 r7
add r6 14
load8 r5 $r6
set r4 15
label emit_lexeme
cmp r5 1
jge word_length_valid_low
div r5 0
label word_length_valid_low
cmp r5 8
jle word_length_valid_high
div r5 0
label word_length_valid_high
set r0 0
label emit_native_letters
cmp r0 r5
jge done
mov r6 r7
add r6 r4
add r6 r0
load8 r14 $r6
print r14
add r0 1
jmp emit_native_letters
label done
halt
