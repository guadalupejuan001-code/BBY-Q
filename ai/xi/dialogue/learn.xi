#!reverse-pc-machine-v1
# Learn an operator spelling from 'quantity WORD quantity' plus its observed
# consequence. No Spanish/English word or spelling-to-operation table here.
# Select among effects already learned in E010. Two witnesses are required.
load8 r0 7300000000000000002
cmp r0 1
jne invalid
load8 r0 7300000000000000024
cmp r0 1
jne invalid
load8 r0 7300000000000000040
cmp r0 0
jne invalid
load8 r0 7300000000000000032
cmp r0 3
jne invalid
load8 r0 7300000000000000800
cmp r0 1
jne invalid
load8 r0 7300000000000000808
cmp r0 1
jne invalid
# A teacher cannot repurpose a grounded numeral as an operator.
load8 r0 7300000000000000804
cmp r0 1
je invalid
load8 r2 7300000000000000801
load8 r0 7300000000000000802
mul r0 256
add r2 r0
load8 r3 7300000000000000809
load8 r0 7300000000000000810
mul r0 256
add r3 r0
cmp r3 0
je invalid
load8 r4 7300000000000000025
load8 r0 7300000000000000026
mul r0 256
add r4 r0
set r0 0
set r6 0
label test_inherited_effects
set r7 7200000000000000330
mov r8 r0
mul r8 2
add r7 r8
load8 r8 $r7
add r7 1
load8 r9 $r7
cmp r9 2
jlt next_effect
mov r10 r2
cmp r8 1
je try_subtract
cmp r8 2
jne invalid
add r10 r3
jmp compare_consequence
label try_subtract
sub r10 r3
label compare_consequence
cmp r10 r4
jne next_effect
cmp r6 0
je first_effect
cmp r6 r8
jne invalid
label first_effect
mov r6 r8
label next_effect
add r0 1
cmp r0 2
jlt test_inherited_effects
cmp r6 0
je invalid
load8 r2 7300000000000000530
cmp r2 1
jlt invalid
cmp r2 16
jgt invalid
# Only alphabetic operator names; no number/digit collision.
set r0 0
label validate_word
cmp r0 r2
jge lookup_spelling
set r7 7300000000000000531
add r7 r0
load8 r8 $r7
cmp r8 97
jlt invalid
cmp r8 122
jgt invalid
add r0 1
jmp validate_word
label lookup_spelling
load8 r3 7300000000000000004
set r0 0
label existing_word
cmp r0 r3
jge new_word
set r7 7300000000000001000
mov r8 r0
mul r8 32
add r7 r8
load8 r8 $r7
cmp r8 r2
jne next_word
set r1 0
label compare_word
cmp r1 r2
jge same_word
set r8 7300000000000000531
add r8 r1
load8 r9 $r8
mov r8 r7
add r8 1
add r8 r1
load8 r10 $r8
cmp r9 r10
jne next_word
add r1 1
jmp compare_word
label same_word
mov r8 r7
add r8 17
load8 r9 $r8
cmp r9 r6
jne invalid
jmp reinforce
label next_word
add r0 1
jmp existing_word
label new_word
cmp r3 32
jge invalid
set r7 7300000000000001000
mov r8 r3
mul r8 32
add r7 r8
store8 $r7 r2
set r1 0
label copy_word
cmp r1 r2
jge word_copied
set r8 7300000000000000531
add r8 r1
load8 r9 $r8
mov r8 r7
add r8 1
add r8 r1
store8 $r8 r9
add r1 1
jmp copy_word
label word_copied
mov r8 r7
add r8 17
store8 $r8 r6
add r3 1
store8 7300000000000000004 r3
label reinforce
mov r8 r7
add r8 18
load8 r9 $r8
cmp r9 2
jge clean
cmp r9 0
je first_witness
set r0 0
label compare_first_witness
cmp r0 4
jge clean
set r10 7300000000000000801
cmp r0 2
jlt first_operand
add r10 6
label first_operand
add r10 r0
load8 r11 $r10
mov r12 r7
add r12 19
add r12 r0
load8 r13 $r12
cmp r11 r13
jne second_distinct_witness
add r0 1
jmp compare_first_witness
label second_distinct_witness
store8 $r8 2
jmp clean
label first_witness
store8 $r8 1
set r0 0
label save_first_witness
cmp r0 4
jge clean
set r10 7300000000000000801
cmp r0 2
jlt copy_first_operand
add r10 6
label copy_first_operand
add r10 r0
load8 r11 $r10
mov r12 r7
add r12 19
add r12 r0
store8 $r12 r11
add r0 1
jmp save_first_witness
label clean
set r0 16
label clear_teaching_intake
set r7 7300000000000000000
add r7 r0
store8 $r7 0
add r0 1
cmp r0 864
jlt clear_teaching_intake
print r6
print r3
halt
label invalid
div r0 0
