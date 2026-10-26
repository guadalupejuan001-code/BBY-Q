#!reverse-pc-machine-v1
# BBY Q / XI: read-only, disjoint blind evaluation (240 odd-x points).
# Model reads stored weights; it MUST NOT learn from the holdout feedback.
# Also report a constant-one frozen baseline and an XOR negative control.
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
load8 r5 7000000000000000064
sub r5 128
load8 r6 7000000000000000065
sub r6 128
load8 r7 7000000000000000066
sub r7 128
load8 r8 7000000000000000067
sub r8 128
set r0 0
set r1 907601
set r12 0
set r13 0
set r15 0
label holdout_loop
# Unlike training's even x, all x values here are odd.
mul r1 48271
mod r1 2147483647
mov r2 r1
mod r2 50
mul r2 2
sub r2 49
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
# Agent predicts solely from four weights in Ether logical memory.
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
# Oracle for linear task is confined to the evaluation, with NO store8.
mov r9 r2
mul r9 3
mov r14 r3
mul r14 2
sub r9 r14
mov r14 r4
mul r14 25
add r9 r14
set r11 0
cmp r9 0
jlt linear_label_ready
set r11 1
label linear_label_ready
cmp r10 r11
jne not_correct_linear
add r13 1
label not_correct_linear
cmp r11 1
jne frozen_incorrect
add r15 1
label frozen_incorrect
# Nonlinearly mismatched sign parity. Track but do not update.
set r11 0
cmp r2 0
jge xor_x_done
set r11 1
label xor_x_done
cmp r3 0
jge xor_label_done
cmp r11 1
je xor_flip_off
set r11 1
jmp xor_label_done
label xor_flip_off
set r11 0
label xor_label_done
cmp r10 r11
jne not_correct_negative
add r12 1
label not_correct_negative
add r0 1
cmp r0 240
jlt holdout_loop
# Fail atomically if there is no generalization above simple controls.
cmp r13 r15
jgt better_than_frozen
div r0 0
label better_than_frozen
cmp r13 190
jge sufficiently_accurate
div r0 0
label sufficiently_accurate
# For the different XOR task, reject implausibly strong generalization claims.
cmp r12 60
jge negative_lower_ok
div r0 0
label negative_lower_ok
cmp r12 180
jle negative_upper_ok
div r0 0
label negative_upper_ok
# Output: correct (learned), correct (frozen), correct (negative), total.
print r13
print r15
print r12
print r0
mem_stats
stats
