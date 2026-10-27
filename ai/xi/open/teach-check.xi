#!reverse-pc-machine-v1
# A spelling cannot acquire entity and predicate types in the same statement.
# Reject the ambiguity before any vocabulary or graph cell is changed.
load8 r0 7800000000000000069
sub r0 1
set r8 7400000000000000512
mul r0 34
add r8 r0
load8 r9 $r8
set r10 0
label entity
cmp r10 2
jge ready
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
jne next
set r0 0
label letters
cmp r0 r9
jge ambiguous
mov r1 r8
add r1 1
add r1 r0
load8 r2 $r1
mov r1 r7
add r1 1
add r1 r0
load8 r3 $r1
cmp r2 r3
jne next
add r0 1
jmp letters
label next
add r10 1
jmp entity
label ambiguous
store8 7800000000000000080 10
store8 7800000000000000087 0
halt
label ready
store8 7800000000000000087 1
halt
