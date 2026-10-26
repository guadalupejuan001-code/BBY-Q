#!reverse-pc-machine-v1
# Resolve 7700000000000000040 to an existing shared bilingual name. r7=bytes,r6=len,r13=case.
load8 r2 7700000000000000040
cmp r2 0
je invalid
load8 r13 7700000000000000038
set r7 7700000000000010000
mov r0 r2
mul r0 4
add r7 r0
load8 r0 $r7
cmp r0 1
jne language
set r13 1
label language
load8 r15 7400000000000000003
cmp r2 22
jgt new_name
set r7 7200000000000001000
mov r3 r2
sub r3 1
mul r3 32
add r7 r3
set r3 5
cmp r15 1
je old_name
set r3 14
label old_name
add r7 r3
load8 r6 $r7
add r7 1
halt
label new_name
load8 r10 7400000000000000004
load8 r3 7400000000000000005
mul r3 256
add r10 r3
set r3 0
label lexeme
cmp r3 r10
jge invalid
set r7 7400000000000010000
mov r4 r3
mul r4 40
add r7 r4
load8 r4 $r7
cmp r4 r2
jne next_lexeme
mov r4 r7
add r4 2
load8 r5 $r4
cmp r5 r15
jne next_lexeme
add r7 3
load8 r6 $r7
add r7 1
halt
label next_lexeme
add r3 1
jmp lexeme
label invalid
div r0 0
