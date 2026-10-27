#!reverse-pc-machine-v1
# Compare every enabled learned construction. More literal constraints beat
# a generic frame; equally specific competing semantic assignments abstain.
# Unknown variables are interpreted only after an explicit intent is
# recognized; matching itself never allocates a concept or teaches an answer.
load8 r0 7800000000000000063
cmp r0 0
je done
load8 r0 7400000000000000040
cmp r0 0
jne done
load8 r13 7400000000000000032
load8 r0 7800000000000000010
store8 7800000000000000187 r0
store8 7800000000000000188 0
set r0 0
label pattern
load8 r1 7800000000000000187
cmp r0 r1
jge done
set r1 7800000000000010000
mov r2 r0
mul r2 96
add r1 r2
load8 r2 $r1
cmp r2 r13
jne next_pattern
mov r7 r1
add r7 2
load8 r2 $r7
cmp r2 1
jne next_pattern
mov r7 r1
add r7 1
load8 r8 $r7
set r9 0
set r10 0
set r11 0
set r12 0
store8 7800000000000000189 0
set r2 0
label token
cmp r2 r13
jge matched
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
je literal
cmp r4 8
je alias
# An unresolved decimal is a quantity, not an unknown entity or predicate.
# Leave it to the original arithmetic/story interpreters instead of allowing
# the generic S/P/O and P/S/O constructions to compete over three unknowns.
cmp r6 0
jne typed_variable
set r3 7400000000000000512
mov r14 r2
mul r14 34
add r3 r14
load8 r5 $r3
set r14 0
label decimal_character
cmp r14 r5
jge next_pattern
mov r15 r3
add r15 1
add r15 r14
load8 r15 $r15
cmp r15 48
jlt typed_variable
cmp r15 57
jgt typed_variable
add r14 1
jmp decimal_character
label typed_variable
cmp r4 2
je predicate
cmp r6 0
je entity_ready
cmp r7 1
je entity_kind
cmp r8 6
jne next_pattern
cmp r7 3
jgt next_pattern
label entity_kind
cmp r6 13
jlt entity_ready
cmp r6 22
jle next_pattern
label entity_ready
cmp r4 1
je subject
cmp r4 4
jne invalid
mov r11 r2
add r11 1
jmp next_token
label subject
mov r9 r2
add r9 1
jmp next_token
label predicate
cmp r6 0
je predicate_ready
cmp r7 2
jne next_pattern
label predicate_ready
mov r10 r2
add r10 1
jmp next_token
label alias
mov r12 r2
add r12 1
jmp next_token
label literal
add r3 1
mov r15 r3
load8 r5 $r15
add r15 1
load8 r14 $r15
mul r14 256
add r5 r14
cmp r5 r6
jne next_pattern
add r3 2
load8 r5 $r3
cmp r5 r7
jne next_pattern
load8 r5 7800000000000000189
add r5 1
store8 7800000000000000189 r5
label next_token
add r2 1
jmp token
label matched
load8 r3 7800000000000000189
load8 r4 7800000000000000188
cmp r3 r4
jgt first
jlt next_pattern
load8 r3 7800000000000000064
cmp r3 0
je first
cmp r3 r8
jne ambiguous
load8 r3 7800000000000000068
cmp r3 r9
jne ambiguous
load8 r3 7800000000000000069
cmp r3 r10
jne ambiguous
load8 r3 7800000000000000070
cmp r3 r11
jne ambiguous
load8 r3 7800000000000000071
cmp r3 r12
jne ambiguous
jmp next_pattern
label first
load8 r3 7800000000000000189
store8 7800000000000000188 r3
store8 7800000000000000065 0
store8 7800000000000000064 r8
store8 7800000000000000068 r9
store8 7800000000000000069 r10
store8 7800000000000000070 r11
store8 7800000000000000071 r12
jmp next_pattern
label ambiguous
store8 7800000000000000065 1
label next_pattern
add r0 1
jmp pattern
label done
halt
label invalid
div r0 0
