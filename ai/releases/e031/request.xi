#!reverse-pc-machine-v1
load8 r9 7400000000000000017
cmp r9 6
jlt lex_delegate
load8 r3 7400000000000000128
cmp r3 64
jne lex_delegate
load8 r3 7400000000000000129
cmp r3 108
jne lex_delegate
load8 r3 7400000000000000130
cmp r3 101
jne lex_delegate
load8 r3 7400000000000000131
cmp r3 120
jne lex_delegate
load8 r3 7400000000000000132
cmp r3 32
jne lex_delegate
sub r9 5
store8 8700000000000000001 r9
load8 r8 7400000000000000003
store8 8700000000000000002 r8
set r0 0
set r1 0
label lex_hash_loop
cmp r0 r9
jge lex_hash_done
set r7 7400000000000000133
add r7 r0
load8 r3 $r7
cmp r3 65
jlt lex_hash_folded
cmp r3 90
jgt lex_hash_folded
add r3 32
label lex_hash_folded
set r7 8700000000000000128
add r7 r0
store8 $r7 r3
mul r1 131
add r1 r3
mod r1 65536
add r0 1
jmp lex_hash_loop
label lex_hash_done
sub r8 1
mul r8 65536
add r1 r8
mov r0 r1
print r0
halt
label lex_delegate
div r0 0
