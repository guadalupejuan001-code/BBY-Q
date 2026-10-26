#!reverse-pc-machine-v1
# Read-only recognition of complete questions in the existing E009 vocabulary.
# Missing new words must not make previous learned relations inaccessible.
store8 7400000000000000046 0
load8 r0 7400000000000000040
cmp r0 0
jne done
load8 r0 7400000000000000032
cmp r0 3
jne done
load8 r0 7100000000000000002
cmp r0 1
jne done
load8 r15 7100000000000000016
set r0 0
label token
set r1 7400000000000000512
mov r2 r0
mul r2 34
add r1 r2
load8 r2 $r1
cmp r2 8
jgt done
set r3 0
label lexeme
cmp r3 r15
jge done
set r4 7100000000000001000
mov r5 r3
mul r5 16
add r4 r5
load8 r5 $r4
cmp r5 r2
jne next_lexeme
set r6 0
label letter
cmp r6 r2
jge found
mov r7 r1
add r7 1
add r7 r6
load8 r8 $r7
mov r7 r4
add r7 2
add r7 r6
load8 r9 $r7
cmp r8 r9
jne next_lexeme
add r6 1
jmp letter
label found
add r0 1
cmp r0 3
jlt token
store8 7400000000000000046 1
halt
label next_lexeme
add r3 1
jmp lexeme
label done
halt
