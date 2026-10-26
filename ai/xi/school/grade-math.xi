#!reverse-pc-machine-v1
# Blind scoring of mathematically computed result. Expected count comes
# AFTER calculate.xi and is never visible to the operator learner.
load8 r14 7200000000000000000
cmp r14 83
je schema_ok
div r14 0
label schema_ok
load8 r14 7200000000000000350
cmp r14 1
je feedback_ready
div r14 0
label feedback_ready
load8 r7 7200000000000000351
cmp r7 9
jle graded_count_valid
cmp r7 255
je graded_count_valid
div r7 0
label graded_count_valid
load8 r8 7200000000000000072
cmp r8 240
jlt test_budget_ok
div r8 0
label test_budget_ok
add r8 1
store8 7200000000000000072 r8
set r10 0
load8 r9 7200000000000000201
cmp r7 255
je expect_abstention
cmp r9 1
jne failed_test
load8 r11 7200000000000000200
cmp r11 1
jlt failed_test
sub r11 1
mul r11 32
set r12 7200000000000001000
add r12 r11
load8 r13 $r12
cmp r13 4
jne failed_test
add r12 1
load8 r13 $r12
cmp r13 r7
jne failed_test
set r10 1
jmp after_math_grade
label expect_abstention
cmp r9 0
jne failed_test
set r10 1
jmp after_math_grade
label failed_test
label after_math_grade
cmp r10 1
jne math_incorrect
load8 r8 7200000000000000073
add r8 1
store8 7200000000000000073 r8
label math_incorrect
store8 7200000000000000350 0
store8 7200000000000000351 0
print r10
load8 r14 7200000000000000072
print r14
load8 r14 7200000000000000073
print r14
mem_stats
