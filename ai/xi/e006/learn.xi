#!reverse-pc-machine-v1
# BBY Q E005: genuine XI-only ONLINE learner, no built-in XOR oracle.
# Infers only from buffered observations and *subsequently* visible outcomes.
# Relations (pairwise sign conjunctions) are generated ON ERRORS, not at birth.
# Persistent authority: one REVERSE-PC Inverse Ether Memory RVPC2.
# r0 example, r2/r3 observed signs, r4 pair descriptor, r5..r7 linear weights
# r8 score, r9 prediction, r10 consequence, r11 online-correct,
# r12 direction/scratch, r13 slot, r14 memory address/weight, r15 generation.
load8 r12 7000000000000000000
cmp r12 66
je check_identity
div r12 0
label check_identity
load8 r12 7000000000000000002
cmp r12 6
je check_version
div r12 0
label check_version
# A promoted model is immutable. Future adaptations use a new shadow bank.
load8 r12 7000000000000000031
cmp r12 0
je mutable_shadow
div r12 0
label mutable_shadow
load8 r15 7000000000000000016
cmp r15 250
jlt epoch_bounded
div r15 0
label epoch_bounded
load8 r12 7000000000000000040
mov r14 r15
add r14 1
cmp r12 r14
je current_feed
div r12 0
label current_feed
load8 r5 7000000000000000064
sub r5 128
load8 r6 7000000000000000065
sub r6 128
load8 r7 7000000000000000066
sub r7 128
set r0 0
set r11 0
label next_sample
# Obtain the observation. Do not read outcome until AFTER prediction.
set r12 7000000000000010000
add r12 r0
load8 r2 $r12
sub r2 100
cmp r2 0
jlt x_is_negative
set r2 1
jmp x_observed
label x_is_negative
set r2 -1
label x_observed
set r12 7000000000000011000
add r12 r0
load8 r3 $r12
sub r3 100
cmp r3 0
jlt p_is_negative
set r3 1
jmp p_observed
label p_is_negative
set r3 -1
label p_observed
# Synthesize candidate descriptor from observed primitive polarities:
# 1=(x-,p-), 2=(x-,p+), 3=(x+,p-), 4=(x+,p+).
set r4 1
cmp r2 0
jlt x_descriptor_done
add r4 2
label x_descriptor_done
cmp r3 0
jlt p_descriptor_done
add r4 1
label p_descriptor_done
# Base predictor: ordinary linear signed perceptron.
mov r8 r5
mov r12 r6
mul r12 r2
add r8 r12
mov r12 r7
mul r12 r3
add r8 r12
# Visit only relations that really exist in Ether, never a fixed target XOR.
set r13 0
label relation_score
set r12 7000000000000000200
add r12 r13
load8 r14 $r12
cmp r14 r4
jne no_relation_match
set r12 7000000000000000220
add r12 r13
load8 r14 $r12
sub r14 128
add r8 r14
label no_relation_match
add r13 1
cmp r13 4
jlt relation_score
set r9 0
cmp r8 0
jlt prediction_ready
set r9 1
label prediction_ready
# Prediction is fixed before consequence is read.
set r12 7000000000000012000
add r12 r0
load8 r10 $r12
cmp r10 0
je valid_label
cmp r10 1
je valid_label
div r10 0
label valid_label
cmp r9 r10
jne error_observed
add r11 1
jmp sample_finished
label error_observed
# Correct basic relations on every mistake; cap signed byte weights.
set r12 -1
cmp r10 1
jne direction_ready
set r12 1
label direction_ready
add r5 r12
mov r14 r12
mul r14 r2
add r6 r14
mov r14 r12
mul r14 r3
add r7 r14
cmp r5 24
jle clamp_bias_low
set r5 24
label clamp_bias_low
cmp r5 -24
jge clamp_signal_high
set r5 -24
label clamp_signal_high
cmp r6 24
jle clamp_signal_low
set r6 24
label clamp_signal_low
cmp r6 -24
jge clamp_pressure_high
set r6 -24
label clamp_pressure_high
cmp r7 24
jle clamp_pressure_low
set r7 24
label clamp_pressure_low
cmp r7 -24
jge growth_mode
set r7 -24
label growth_mode
load8 r13 7000000000000000003
cmp r13 1
jne sample_finished
# If a previously composed relation matches, reinforce it with feedback.
set r13 0
label scan_compositions
set r14 7000000000000000200
add r14 r13
load8 r8 $r14
cmp r8 r4
je adjust_composition
add r13 1
cmp r13 4
jlt scan_compositions
# Persistent evidence for an UNCREATED relation; do not allocate on first error.
mov r13 r4
sub r13 1
set r14 7000000000000000120
add r14 r13
load8 r8 $r14
cmp r8 2
jge mint_composition
add r8 1
store8 $r14 r8
jmp sample_finished
label mint_composition
# Grow a new descriptor into the first empty logical slot.
set r13 0
label find_empty_slot
set r14 7000000000000000200
add r14 r13
load8 r8 $r14
cmp r8 0
je empty_slot_found
add r13 1
cmp r13 4
jlt find_empty_slot
div r13 0
label empty_slot_found
store8 $r14 r4
set r14 7000000000000000220
add r14 r13
mov r8 r12
mul r8 8
add r8 128
store8 $r14 r8
load8 r8 7000000000000000030
add r8 1
store8 7000000000000000030 r8
jmp sample_finished
label adjust_composition
set r14 7000000000000000220
add r14 r13
load8 r8 $r14
sub r8 128
mov r13 r12
mul r13 8
add r8 r13
cmp r8 112
jle relation_lower_bound
set r8 112
label relation_lower_bound
cmp r8 -112
jge relation_encoded
set r8 -112
label relation_encoded
add r8 128
store8 $r14 r8
label sample_finished
add r0 1
cmp r0 200
jlt next_sample
# One atomic machine program publishes the 3 base weights and generation.
mov r12 r5
add r12 128
store8 7000000000000000064 r12
mov r12 r6
add r12 128
store8 7000000000000000065 r12
mov r12 r7
add r12 128
store8 7000000000000000066 r12
add r15 1
store8 7000000000000000016 r15
# Keep knowledge; erase raw observations AND known consequences within this
# SAME atomic XI transaction. Nothing external stores a second copy.
# Removing overrides restores the global Ether background-zero rule.
set r0 0
label erase_consumed_batch
set r12 7000000000000010000
add r12 r0
store8 $r12 0
set r12 7000000000000011000
add r12 r0
store8 $r12 0
set r12 7000000000000012000
add r12 r0
store8 $r12 0
add r0 1
cmp r0 200
jlt erase_consumed_batch
# Clear feed generation marker, forbidding duplicate training.
store8 7000000000000000040 0
load8 r12 7000000000000000030
# 200 outcomes, online successes, generation, physically created relations
print r0
print r11
print r15
print r12
print r5
print r6
print r7
mem_stats
stats
