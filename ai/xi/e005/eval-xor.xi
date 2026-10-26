#!reverse-pc-machine-v1
# E005 READ-ONLY independent holdout. Odd magnitudes never occur in training.
# Labels are generated AFTER prediction. This program contains NO store8.
load8 r12 7000000000000000002
cmp r12 5
je schema_ok
div r12 0
label schema_ok
load8 r5 7000000000000000064
sub r5 128
load8 r6 7000000000000000065
sub r6 128
load8 r7 7000000000000000066
sub r7 128
load8 r12 7000000000000000020
mul r12 7919
set r1 907601
add r1 r12
set r0 0
set r11 0
set r15 0
label next_sample
mul r1 48271
mod r1 2147483647
mov r2 r1
mod r2 25
mul r2 2
add r2 1
mul r1 48271
mod r1 2147483647
mov r12 r1
mod r12 2
cmp r12 0
jne x_positive
mul r2 -1
label x_positive
mul r1 48271
mod r1 2147483647
mov r3 r1
mod r3 25
mul r3 2
add r3 1
mul r1 48271
mod r1 2147483647
mov r12 r1
mod r12 2
cmp r12 0
jne p_positive
mul r3 -1
label p_positive
# The very same prediction formula as learn.xi (without labels or updates).
set r4 1
cmp r2 0
jlt x_desc_done
add r4 2
label x_desc_done
cmp r3 0
jlt p_desc_done
add r4 1
label p_desc_done
mov r8 r5
mov r12 r6
mul r12 r2
add r8 r12
mov r12 r7
mul r12 r3
add r8 r12
set r13 0
label score_slots
set r12 7000000000000000200
add r12 r13
load8 r14 $r12
cmp r14 r4
jne slot_not_matched
set r12 7000000000000000220
add r12 r13
load8 r14 $r12
sub r14 128
add r8 r14
label slot_not_matched
add r13 1
cmp r13 4
jlt score_slots
set r9 0
cmp r8 0
jlt prediction_ready
set r9 1
label prediction_ready
# Independent XOR consequence, observed only after prediction.
set r10 0
cmp r2 0
jge oracle_x_done
set r10 1
label oracle_x_done
cmp r3 0
jge oracle_p_done
cmp r10 1
je oracle_p_toggle_zero
set r10 1
jmp oracle_p_done
label oracle_p_toggle_zero
set r10 0
label oracle_p_done
mul r1 48271
mod r1 2147483647
cmp r9 r10
jne wrong_prediction
add r11 1
label wrong_prediction
# Frozen always-one classifier measures task balance on IDENTICAL observations.
cmp r10 1
jne baseline_zero
add r15 1
label baseline_zero
add r0 1
cmp r0 240
jlt next_sample
load8 r14 7000000000000000030
# Exact integer counts, not a preformatted or fabricated percentage.
print r11
print r15
print r0
print r14
mem_stats
stats
