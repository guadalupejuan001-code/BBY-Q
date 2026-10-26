#!reverse-pc-machine-v1
# Learn from observed before/amount/after, not a verb spelling/effect table.
# Candidate family is engineered: assignment, addition, subtraction.
# 7500000000000000016=1, +17=predicate ID, +18..23=three little-endian uint16 values.
# Keyed slots +10000+ID*24: mask,count,ready,first triple,second triple.
load8 r0 7500000000000000002
cmp r0 1
jne invalid
load8 r0 7500000000000000016
cmp r0 1
jne invalid
load8 r5 7500000000000000017
cmp r5 0
je invalid
set r7 7400000000000006000
add r7 r5
load8 r0 $r7
cmp r0 2
jne invalid
load8 r2 7500000000000000018
load8 r0 7500000000000000019
mul r0 256
add r2 r0
load8 r3 7500000000000000020
load8 r0 7500000000000000021
mul r0 256
add r3 r0
load8 r4 7500000000000000022
load8 r0 7500000000000000023
mul r0 256
add r4 r0
set r7 7500000000000010000
mul r5 24
add r7 r5
load8 r8 $r7
cmp r8 0
jne existing_mask
set r8 7
label existing_mask
set r12 0
set r6 1
label candidate
mov r9 r8
div r9 r6
mod r9 2
cmp r9 0
je next_candidate
mov r10 r3
cmp r6 1
je compare
mov r10 r2
cmp r6 4
je subtract
add r10 r3
jmp compare
label subtract
sub r10 r3
label compare
cmp r10 0
jlt next_candidate
cmp r10 65535
jgt next_candidate
cmp r10 r4
jne next_candidate
add r12 r6
label next_candidate
mul r6 2
cmp r6 4
jle candidate
cmp r12 0
je invalid
store8 $r7 r12
mov r8 r7
add r8 1
load8 r9 $r8
cmp r9 2
jge promote
cmp r9 0
je first
set r0 0
label compare_pair
cmp r0 4
jge promote
set r10 7500000000000000018
add r10 r0
load8 r11 $r10
mov r10 r7
add r10 3
add r10 r0
load8 r13 $r10
cmp r11 r13
jne second
add r0 1
jmp compare_pair
label first
set r9 1
set r13 3
jmp save_witness
label second
set r9 2
set r13 9
label save_witness
store8 $r8 r9
set r0 0
label copy
cmp r0 6
jge promote
set r10 7500000000000000018
add r10 r0
load8 r11 $r10
mov r10 r7
add r10 r13
add r10 r0
store8 $r10 r11
add r0 1
jmp copy
label promote
set r10 0
cmp r9 2
jlt save_ready
cmp r12 1
je assign
cmp r12 2
je add
cmp r12 4
jne save_ready
set r10 3
jmp save_ready
label assign
set r10 1
jmp save_ready
label add
set r10 2
label save_ready
mov r8 r7
add r8 2
store8 $r8 r10
set r0 16
label clean
set r7 7500000000000000000
add r7 r0
store8 $r7 0
add r0 1
cmp r0 64
jlt clean
halt
label invalid
div r0 0
