#!reverse-pc-machine-v1
# E005 independent DATA PRODUCER in XI. Agent learner is a different program.
# Magnitudes: even, nonzero, ±2..±50. Evaluation uses disjoint odd magnitudes.
# Source only writes observations and delayed consequence to logical Ether.
load8 r0 7000000000000000002
cmp r0 6
je schema_ok
div r0 0
label schema_ok
load8 r7 7000000000000000016
load8 r8 7000000000000000020
set r1 37
mov r5 r7
mul r5 1009
add r1 r5
mov r5 r8
mul r5 7919
add r1 r5
set r0 0
label next_observation
mul r1 48271
mod r1 2147483647
mov r2 r1
mod r2 25
add r2 1
mul r2 2
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
add r3 1
mul r3 2
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
# Three bounded arrays exist in the SAME RVPC2, not an external dataset.
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
cmp r0 200
jlt next_observation
# Prevent learning from stale examples after resuming a generation.
add r7 1
store8 7000000000000000040 r7
print r0
print r7
mem_stats
