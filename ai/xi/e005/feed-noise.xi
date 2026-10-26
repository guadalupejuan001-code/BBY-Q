#!reverse-pc-machine-v1
# E005 independent DATA PRODUCER in XI. Agent learner is a different program.
# Magnitudes: even, nonzero, ±2..±50. Evaluation uses disjoint odd magnitudes.
# Source only writes observations and delayed consequence to logical Ether.
load8 r0 7000000000000000002
cmp r0 5
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
# Separate Park-Miller generator for feedback; NEVER reuse observation RNG parity.
set r9 790123
mov r5 r7
mul r5 3467
add r9 r5
mov r5 r8
mul r5 6011
add r9 r5
set r0 0
set r10 0
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
# Independent feedback stream; use a high-order threshold, NOT mod 2.
# Keep input PRNG schedule equal to feed-xor.xi, discarding its extra draw.
mul r1 48271
mod r1 2147483647
mul r9 16807
mod r9 2147483647
mov r4 r9
div r4 1073741824
# Diagnostic: observed agreement of noise with XOR on this training batch.
set r11 0
cmp r2 0
jge xor_diag_x
set r11 1
label xor_diag_x
cmp r3 0
jge xor_diag_p
cmp r11 1
je xor_diag_flip
set r11 1
jmp xor_diag_p
label xor_diag_flip
set r11 0
label xor_diag_p
cmp r11 r4
jne xor_diag_end
add r10 1
label xor_diag_end
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
print r10
mem_stats
