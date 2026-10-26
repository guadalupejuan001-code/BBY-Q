#!reverse-pc-machine-v1
# E010 XI: infer what an observed 'combine'/'remove' intervention DOES.
# Operator ID 1/2 is NOT hardcoded to + or -. Signed direction is learned.
# Lesson: +340=1 +341=operator +342=before +343=objects +344=after.
load8 r12 7200000000000000000
cmp r12 83
je schema_ok
div r12 0
label schema_ok
load8 r12 7200000000000000340
cmp r12 1
je action_observed
div r12 0
label action_observed
load8 r5 7200000000000000341
cmp r5 1
je op_valid
cmp r5 2
je op_valid
div r5 0
label op_valid
load8 r2 7200000000000000342
load8 r3 7200000000000000343
load8 r4 7200000000000000344
cmp r2 9
jle before_valid
div r2 0
label before_valid
cmp r3 1
jge amount_positive
div r3 0
label amount_positive
cmp r3 9
jle amount_valid
div r3 0
label amount_valid
cmp r4 9
jle after_valid
div r4 0
label after_valid
# All three quantities must first have been learned as sensory concepts.
set r0 0
label test_quantity_grounding
mov r8 r2
cmp r0 0
je selected_quantity
mov r8 r3
cmp r0 1
je selected_quantity
mov r8 r4
label selected_quantity
set r9 0
load8 r11 7200000000000000010
label lookup_count
cmp r9 r11
jge quantity_missing
set r10 7200000000000001000
mov r12 r9
mul r12 32
add r10 r12
load8 r12 $r10
cmp r12 4
jne next_count_slot
mov r12 r10
add r12 1
load8 r13 $r12
cmp r13 r8
jne next_count_slot
mov r12 r10
add r12 4
load8 r13 $r12
cmp r13 2
jge count_grounded
label next_count_slot
add r9 1
jmp lookup_count
label quantity_missing
div r9 0
label count_grounded
add r0 1
cmp r0 3
jlt test_quantity_grounding
# Only then compare the outcome with two candidate effects.
mov r8 r2
add r8 r3
cmp r8 r4
je positive_effect
mov r8 r2
sub r8 r3
cmp r8 r4
je negative_effect
div r8 0
label positive_effect
set r6 2
jmp consolidate_effect
label negative_effect
set r6 1
label consolidate_effect
set r10 7200000000000000330
mov r11 r5
sub r11 1
mul r11 2
add r10 r11
load8 r12 $r10
cmp r12 0
je first_operator_witness
cmp r12 r6
je repeated_operator_witness
div r12 0
label first_operator_witness
store8 $r10 r6
label repeated_operator_witness
add r10 1
load8 r12 $r10
cmp r12 200
jge erase_lesson
add r12 1
store8 $r10 r12
label erase_lesson
set r0 0
label remove_arithmetic_example
set r10 7200000000000000340
add r10 r0
store8 $r10 0
add r0 1
cmp r0 5
jlt remove_arithmetic_example
print r5
print r6
mem_stats
stats
