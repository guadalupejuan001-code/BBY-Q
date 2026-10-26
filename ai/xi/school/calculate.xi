#!reverse-pc-machine-v1
# E010 XI: apply a learned effect to NEW quantities, not a canned answer.
# Request +320=1 +321=before count +322=change +323=operator ID.
load8 r12 7200000000000000000
cmp r12 83
je school_valid
div r12 0
label school_valid
load8 r12 7200000000000000320
cmp r12 1
je operation_requested
div r12 0
label operation_requested
set r8 0
store8 7200000000000000201 r8
store8 7200000000000000200 r8
load8 r12 7200000000000000003
cmp r12 1
jge recognition_mastered
jmp unknown_result
label recognition_mastered
load8 r2 7200000000000000321
load8 r3 7200000000000000322
load8 r4 7200000000000000323
cmp r2 9
jgt unknown_result
cmp r3 9
jgt unknown_result
cmp r3 1
jlt unknown_result
cmp r4 1
je valid_operation
cmp r4 2
je valid_operation
jmp unknown_result
label valid_operation
set r6 7200000000000000330
mov r12 r4
sub r12 1
mul r12 2
add r6 r12
load8 r7 $r6
add r6 1
load8 r9 $r6
cmp r9 2
jlt unknown_result
cmp r7 1
je outcome_is_subtraction
cmp r7 2
je outcome_is_addition
jmp unknown_result
label outcome_is_subtraction
mov r5 r2
sub r5 r3
jmp count_bounds
label outcome_is_addition
mov r5 r2
add r5 r3
label count_bounds
cmp r5 0
jlt unknown_result
cmp r5 9
jgt unknown_result
# Verify the requested number and result were independently grounded.
load8 r15 7200000000000000010
set r0 0
label verify_three_counts
mov r8 r2
cmp r0 0
je count_ready
mov r8 r3
cmp r0 1
je count_ready
mov r8 r5
label count_ready
set r1 0
label find_grounded_quantity
cmp r1 r15
jge unknown_result
set r10 7200000000000001000
mov r11 r1
mul r11 32
add r10 r11
load8 r12 $r10
cmp r12 4
jne next_quantity
mov r11 r10
add r11 1
load8 r12 $r11
cmp r12 r8
jne next_quantity
mov r11 r10
add r11 4
load8 r12 $r11
cmp r12 2
jlt next_quantity
cmp r0 2
jne next_known_quantity
# The result is this learned numeral's bilingual lexical ID.
mov r14 r1
add r14 1
store8 7200000000000000200 r14
label next_known_quantity
add r0 1
cmp r0 3
jge arithmetic_supported
jmp verify_three_counts
label next_quantity
add r1 1
jmp find_grounded_quantity
label arithmetic_supported
store8 7200000000000000201 1
store8 7200000000000000203 4
jmp erase_math_input
label unknown_result
store8 7200000000000000200 0
store8 7200000000000000201 0
store8 7200000000000000203 4
label erase_math_input
set r0 0
label forget_operands
set r10 7200000000000000320
add r10 r0
store8 $r10 0
add r0 1
cmp r0 4
jlt forget_operands
load8 r14 7200000000000000201
print r14
load8 r14 7200000000000000200
print r14
mem_stats
