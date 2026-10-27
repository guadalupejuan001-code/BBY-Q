#!reverse-pc-machine-v1
# Rebuild token vectors in a disjoint buffer, using source-bound words for
# variable RHS slots and learned canonical spellings for literal RHS slots.
load8 r0 8100000000000000080
cmp r0 0
je done
sub r0 1
set r12 8100000000000020000
mov r1 r0
mul r1 96
add r12 r1
load8 r11 $r12
set r13 8100000000000040000
mul r0 512
add r13 r0
load8 r10 7400000000000000032
load8 r9 8100000000000000081
load8 r8 8100000000000000082
mov r0 r10
sub r0 r8
add r0 r11
cmp r0 1
jlt fail
cmp r0 15
jgt fail
store8 8100000000000000084 r0
set r0 0
label output_token
load8 r1 8100000000000000084
cmp r0 r1
jge commit
cmp r0 r9
jlt original_before
mov r1 r9
add r1 r11
cmp r0 r1
jge original_after
mov r1 r0
sub r1 r9
mov r7 r12
add r7 16
mov r2 r1
mul r2 4
add r7 r2
load8 r2 $r7
cmp r2 16
je canonical
cmp r2 1
je source_subject
cmp r2 2
je source_predicate
cmp r2 4
jne fail
load8 r1 8100000000000000095
jmp bound_source
label source_subject
load8 r1 8100000000000000093
jmp bound_source
label source_predicate
load8 r1 8100000000000000094
label bound_source
cmp r1 0
je fail
sub r1 1
jmp original
label original_before
mov r1 r0
jmp original
label original_after
mov r1 r0
sub r1 r11
add r1 r8
label original
set r5 7400000000000000512
mov r2 r1
mul r2 34
add r5 r2
set r6 7800000000000001024
mul r1 4
add r6 r1
jmp copy_token
label canonical
mov r5 r13
mov r2 r1
mul r2 34
add r5 r2
mov r6 r7
# r7 points at the learned RHS mask; following bytes contain CID and kind.
add r6 1
label copy_token
set r2 0
label copy_raw
mov r7 r5
add r7 r2
load8 r3 $r7
set r7 8100000000000002000
mov r4 r0
mul r4 34
add r7 r4
add r7 r2
store8 $r7 r3
add r2 1
cmp r2 34
jlt copy_raw
# Canonical descriptors and live resolutions use the same CID:u16,kind byte.
load8 r3 $r6
add r6 1
load8 r14 $r6
add r6 1
load8 r4 $r6
set r7 8100000000000002540
mov r1 r0
mul r1 4
add r7 r1
store8 $r7 r3
add r7 1
store8 $r7 r14
add r7 1
store8 $r7 r4
set r7 8100000000000002510
mov r1 r0
mul r1 2
add r7 r1
cmp r14 0
je narrow
store8 $r7 0
add r7 1
store8 $r7 0
jmp next_output
label narrow
store8 $r7 r3
add r7 1
store8 $r7 r4
label next_output
add r0 1
jmp output_token
label commit
load8 r0 8100000000000000084
store8 7400000000000000032 r0
set r1 0
label commit_raw
set r7 8100000000000002000
add r7 r1
load8 r2 $r7
set r7 7400000000000000512
add r7 r1
store8 $r7 r2
# Clear after copying so shorter subsequent outputs cannot inherit a token.
set r7 8100000000000002000
add r7 r1
store8 $r7 0
add r1 1
cmp r1 510
jlt commit_raw
set r1 0
label commit_legacy
set r7 8100000000000002510
add r7 r1
load8 r2 $r7
set r7 7400000000000001600
add r7 r1
store8 $r7 r2
set r7 8100000000000002510
add r7 r1
store8 $r7 0
add r1 1
cmp r1 30
jlt commit_legacy
set r1 0
label commit_open
set r7 8100000000000002540
add r7 r1
load8 r2 $r7
set r7 7800000000000001024
add r7 r1
store8 $r7 r2
set r7 8100000000000002540
add r7 r1
store8 $r7 0
add r1 1
cmp r1 60
jlt commit_open
load8 r0 8100000000000000085
cmp r0 4
jne prefix
store8 8100000000000000029 1
store8 8100000000000000028 1
jmp set_scope
label prefix
cmp r0 1
jne done
store8 8100000000000000028 1
label set_scope
load8 r0 8100000000000000086
store8 8100000000000000027 r0
label done
halt
label fail
store8 8100000000000000026 1
store8 8100000000000000080 0
halt
