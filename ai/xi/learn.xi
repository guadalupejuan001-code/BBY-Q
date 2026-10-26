#!reverse-pc-machine-v1
# BBY Q / XI: online, error-driven, persistent learning.
# One execution = 400 novel synthetic experiences.
# All relation weights live in the single Inverse Ether Memory RVPC2.
# r0 example; r1 RNG; r2 signal; r3 pressure; r4 action;
# r5 bias; r6 signal weight; r7 pressure weight; r8 action weight;
# r9 score; r10 prediction; r11 observed consequence; r12 world score;
# r13 correct-before-feedback; r14 scratch; r15 persistent epoch.
load8 r14 7000000000000000000
cmp r14 66
je check_b
div r14 0
label check_b
load8 r14 7000000000000000001
cmp r14 81
je check_v
div r14 0
label check_v
load8 r14 7000000000000000002
cmp r14 4
je schema_ok
div r14 0
label schema_ok
load8 r15 7000000000000000016
cmp r15 250
jlt epoch_ok
div r15 0
label epoch_ok
# Each pass has a new deterministic stream derived only from epoch.
set r1 43
mov r14 r15
mul r14 101
add r1 r14
load8 r5 7000000000000000064
sub r5 128
load8 r6 7000000000000000065
sub r6 128
load8 r7 7000000000000000066
sub r7 128
load8 r8 7000000000000000067
sub r8 128
set r0 0
set r13 0
label training_loop
# Even-valued x reserves odd-valued x for an independent blind holdout.
mul r1 48271
mod r1 2147483647
mov r2 r1
mod r2 51
mul r2 2
sub r2 50
mul r1 48271
mod r1 2147483647
mov r3 r1
mod r3 101
sub r3 50
mul r1 48271
mod r1 2147483647
mov r4 r1
mod r4 2
mul r4 2
sub r4 1
# Predict BEFORE obtaining the world's label. Four interpretable relations.
mov r9 r5
mov r14 r2
div r14 10
mul r14 r6
add r9 r14
mov r14 r3
div r14 10
mul r14 r7
add r9 r14
mov r14 r4
mul r14 r8
add r9 r14
set r10 0
cmp r9 0
jlt predicted
set r10 1
label predicted
# Only the environment knows this fixed secret linear consequence rule.
# The learner below receives r11 AFTER predicting, never its coefficients.
mov r12 r2
mul r12 3
mov r14 r3
mul r14 2
sub r12 r14
mov r14 r4
mul r14 25
add r12 r14
set r11 0
cmp r12 0
jlt feedback_ready
set r11 1
label feedback_ready
cmp r10 r11
jne prediction_error
add r13 1
jmp end_sample
label prediction_error
# Signed mistake-driven update, implemented entirely with XI instructions.
set r14 -1
cmp r11 1
jne direction_ready
set r14 1
label direction_ready
add r5 r14
mov r9 r2
div r9 10
mul r9 r14
add r6 r9
mov r9 r3
div r9 10
mul r9 r14
add r7 r9
mov r9 r4
mul r9 2
mul r9 r14
add r8 r9
# A finite signed memory budget: weights always fit one byte after bias.
cmp r5 120
jle bias_upper_ok
set r5 120
label bias_upper_ok
cmp r5 -120
jge bias_lower_ok
set r5 -120
label bias_lower_ok
cmp r6 120
jle signal_upper_ok
set r6 120
label signal_upper_ok
cmp r6 -120
jge signal_lower_ok
set r6 -120
label signal_lower_ok
cmp r7 120
jle pressure_upper_ok
set r7 120
label pressure_upper_ok
cmp r7 -120
jge pressure_lower_ok
set r7 -120
label pressure_lower_ok
cmp r8 120
jle action_upper_ok
set r8 120
label action_upper_ok
cmp r8 -120
jge action_lower_ok
set r8 -120
label action_lower_ok
label end_sample
add r0 1
cmp r0 400
jlt training_loop
# One atomic program: weights and epoch publish together only on success.
mov r14 r5
add r14 128
store8 7000000000000000064 r14
mov r14 r6
add r14 128
store8 7000000000000000065 r14
mov r14 r7
add r14 128
store8 7000000000000000066 r14
mov r14 r8
add r14 128
store8 7000000000000000067 r14
add r15 1
store8 7000000000000000016 r15
# Output: examples, correct online, new epoch, learned relations.
print r0
print r13
print r15
print r5
print r6
print r7
print r8
mem_stats
stats
