#!reverse-pc-machine-v1
# Teacher supplies semantic referents, never a syntax template or answer.
# Input: resolved text in K; 7600000000000000016=1,+17=actor,+18=item,+19=assignment verb.
# Infer each slot as actor/item/verb or a learned literal marker. Two examples
# with BOTH different actors and items are required before use. 16 patterns.
# Record: length, enabled, first A/I/V, second A/I/V, 15 triples (role,ID,kind).
load8 r0 7600000000000000002
cmp r0 1
jne invalid
load8 r0 7600000000000000016
cmp r0 1
jne invalid
load8 r0 7400000000000000040
cmp r0 0
jne invalid
load8 r15 7400000000000000032
cmp r15 4
jlt invalid
cmp r15 15
jgt invalid
load8 r9 7600000000000000017
load8 r10 7600000000000000018
load8 r11 7600000000000000019
cmp r9 0
je invalid
cmp r10 0
je invalid
cmp r9 r10
je invalid
cmp r9 r11
je invalid
cmp r10 r11
je invalid
set r7 7500000000000010002
mov r0 r11
mul r0 24
add r7 r0
load8 r0 $r7
cmp r0 1
jne invalid
set r0 0
label token
cmp r0 r15
jge roles_ready
set r7 7400000000000001600
mov r1 r0
mul r1 2
add r7 r1
load8 r2 $r7
add r7 1
load8 r3 $r7
cmp r2 0
je invalid
cmp r2 r9
je actor
cmp r2 r10
je item
cmp r2 r11
je verb
cmp r3 3
jne invalid
set r4 0
jmp descriptor
label actor
set r4 1
jmp entity
label item
set r4 2
label entity
cmp r3 1
jne invalid
cmp r2 13
jlt role_count
cmp r2 22
jle invalid
jmp role_count
label verb
set r4 3
cmp r3 2
jne invalid
label role_count
set r7 7600000000000000019
add r7 r4
load8 r5 $r7
add r5 1
cmp r5 1
jne invalid
store8 $r7 r5
set r2 0
set r3 0
label descriptor
set r7 7600000000000000128
mov r1 r0
mul r1 3
add r7 r1
store8 $r7 r4
add r7 1
store8 $r7 r2
add r7 1
store8 $r7 r3
add r0 1
jmp token
label roles_ready
load8 r0 7600000000000000020
cmp r0 1
jne invalid
load8 r0 7600000000000000021
cmp r0 1
jne invalid
load8 r0 7600000000000000022
cmp r0 1
jne invalid
load8 r13 7600000000000000003
cmp r13 16
jgt invalid
mov r14 r15
mul r14 3
set r0 0
label pattern
cmp r0 r13
jge allocate
set r1 7600000000000001000
mov r2 r0
mul r2 64
add r1 r2
load8 r2 $r1
cmp r2 r15
jne next_pattern
set r2 0
label same_descriptor
cmp r2 r14
jge witness
mov r7 r1
add r7 8
add r7 r2
load8 r3 $r7
set r7 7600000000000000128
add r7 r2
load8 r4 $r7
cmp r3 r4
jne next_pattern
add r2 1
jmp same_descriptor
label next_pattern
add r0 1
jmp pattern
label allocate
cmp r13 16
jge invalid
set r1 7600000000000001000
mov r2 r13
mul r2 64
add r1 r2
store8 $r1 r15
mov r7 r1
add r7 2
store8 $r7 r9
add r7 1
store8 $r7 r10
add r7 1
store8 $r7 r11
set r2 0
label copy_descriptor
cmp r2 r14
jge allocated
set r7 7600000000000000128
add r7 r2
load8 r3 $r7
mov r7 r1
add r7 8
add r7 r2
store8 $r7 r3
add r2 1
jmp copy_descriptor
label allocated
add r13 1
store8 7600000000000000003 r13
jmp clean
label witness
mov r7 r1
add r7 1
load8 r2 $r7
cmp r2 1
je clean
add r7 1
load8 r2 $r7
cmp r2 r9
je clean
add r7 1
load8 r2 $r7
cmp r2 r10
je clean
mov r7 r1
add r7 5
store8 $r7 r9
add r7 1
store8 $r7 r10
add r7 1
store8 $r7 r11
mov r7 r1
add r7 1
store8 $r7 1
label clean
set r0 16
label grammar_clean
set r7 7600000000000000000
add r7 r0
store8 $r7 0
add r0 1
cmp r0 192
jlt grammar_clean
set r0 16
label intake_clean
set r7 7400000000000000000
add r7 r0
store8 $r7 0
add r0 1
cmp r0 2048
jlt intake_clean
halt
label invalid
div r0 0
