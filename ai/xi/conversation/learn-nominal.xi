#!reverse-pc-machine-v1
# From labeled quantity phrases, learn singular, plural and one-word agreement.
# 7700000000000000016=3,+17=noun,+18=1 singular/2 plural/3 indefinite article.
# Existing shared concept IDs must resolve; all text remains in XI.
load8 r0 7700000000000000002
cmp r0 1
jne invalid
load8 r0 7700000000000000016
cmp r0 3
jne invalid
load8 r0 7400000000000000040
cmp r0 0
jne invalid
load8 r0 7400000000000000032
cmp r0 2
jne invalid
load8 r9 7700000000000000017
load8 r10 7700000000000000018
load8 r0 7400000000000001602
cmp r0 r9
jne invalid
load8 r0 7400000000000001603
cmp r0 1
jne invalid
load8 r11 7400000000000000003
cmp r11 1
jlt invalid
cmp r11 2
jgt invalid
set r12 7700000000000100000
mov r0 r9
mul r0 224
add r12 r0
mov r0 r11
sub r0 1
mul r0 112
add r12 r0
load8 r0 7400000000000001600
cmp r10 1
je singular
cmp r10 2
je plural
cmp r10 3
jne invalid
cmp r0 0
je invalid
load8 r0 7400000000000000512
cmp r0 8
jgt invalid
set r13 34
jmp noun
label singular
cmp r0 14
jne invalid
set r13 34
jmp noun
label plural
cmp r0 15
je plural_two
cmp r0 16
jne invalid
set r14 2
jmp plural_ready
label plural_two
set r14 1
label plural_ready
store8 7700000000000000022 r14
set r13 68
label noun
set r8 7400000000000000546
mov r7 r12
add r7 r13
set r15 0
jmp segment
label prefix
cmp r10 2
je plural_mask
set r8 7400000000000000512
mov r7 r12
cmp r10 1
je prefix_ready
add r7 102
label prefix_ready
set r15 1
label segment
load8 r6 $r8
cmp r6 1
jlt invalid
cmp r6 32
jgt invalid
load8 r1 $r7
cmp r1 0
je write_segment
cmp r1 r6
jne invalid
set r0 0
label compare
cmp r0 r6
jge segment_done
mov r1 r7
add r1 1
add r1 r0
load8 r2 $r1
mov r1 r8
add r1 1
add r1 r0
load8 r3 $r1
cmp r2 r3
jne invalid
add r0 1
jmp compare
label write_segment
store8 $r7 r6
set r0 0
label copy
cmp r0 r6
jge segment_done
mov r1 r8
add r1 1
add r1 r0
load8 r2 $r1
mov r1 r7
add r1 1
add r1 r0
store8 $r1 r2
add r0 1
jmp copy
label segment_done
cmp r15 0
je prefix
jmp done
label plural_mask
mov r7 r12
add r7 101
load8 r1 $r7
load8 r2 7700000000000000022
mov r0 r1
div r0 r2
mod r0 2
cmp r0 0
jne done
add r1 r2
store8 $r7 r1
label done
halt
label invalid
div r0 0
