#!reverse-pc-machine-v1
# E006 independent validation-world producer in the owner's XI language.
# Odd magnitudes (1,3,...49) are disjoint from training's even magnitudes.
# The learner is a different program and never computes these labels.
load8 r5 7000000000000000002
cmp r5 6
je version_ok
div r5 0
label version_ok
load8 r5 7000000000000000031
cmp r5 0
je candidate_unpublished
div r5 0
label candidate_unpublished
load8 r5 7000000000000000040
cmp r5 0
je train_feed_consumed
div r5 0
label train_feed_consumed
load8 r5 7000000000000000041
cmp r5 0
je clean_validation
div r5 0
label clean_validation
load8 r7 7000000000000000016
load8 r8 7000000000000000020
set r1 907601
mov r5 r8
mul r5 7919
add r1 r5
mov r5 r7
mul r5 101
add r1 r5
set r9 123457
mov r5 r8
mul r5 2729
add r9 r5
mov r5 r7
mul r5 997
add r9 r5
set r0 0
label generate_unseen
mul r1 48271
mod r1 2147483647
mov r2 r1
mod r2 25
mul r2 2
add r2 1
mul r1 48271
mod r1 2147483647
mov r5 r1
mod r5 2
cmp r5 0
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
mov r5 r1
mod r5 2
cmp r5 0
jne p_positive
mul r3 -1
label p_positive
# World xnor: consequence determined independently of the learner.
set r4 0
cmp r2 0
jge x_done
set r4 1
label x_done
cmp r3 0
jge p_done
cmp r4 1
je flip_zero
set r4 1
jmp p_done
label flip_zero
set r4 0
label p_done
cmp r4 0
je invert_zero
set r4 0
jmp final_label
label invert_zero
set r4 1
label final_label
mul r1 48271
mod r1 2147483647
add r2 100
add r3 100
set r6 7000000000000010000
add r6 r0
store8 $r6 r2
set r6 7000000000000011000
add r6 r0
store8 $r6 r3
set r6 7000000000000012000
add r6 r0
store8 $r6 r4
add r0 1
cmp r0 240
jlt generate_unseen
add r7 1
store8 7000000000000000041 r7
store8 7000000000000000042 1
print r0
print r7
mem_stats
