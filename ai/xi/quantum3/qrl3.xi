# QRL3: stochastic Bernoulli policy over measured 1000-wire expectations.
# Native episodic REINFORCE, full delayed return, EMA baseline, gamma=1.
# No action is computed from a programmed goal-direction rule.
label qrl_episode
clock f28
fstore 8140000000000000496 f28
fstore 8140000000000000504 0
store64 8140000000000000000 1
call select_agent
call random_uniform
set r0 0
fcmp f30 0.5
jlt goal_first
set r0 6
label goal_first
load64 r1 8140000000000000328
cmp r1 0
je goal_ready
cmp r0 0
jne goal_five
set r0 1
jmp goal_ready
label goal_five
set r0 5
label goal_ready
store64 8140000000000000352 r0
store64 8140000000000000344 3
load64 r0 8140000000000000336
cmp r0 0
je start_ready
call random_uniform
fmul f30 4
ftoi r0 f30
mul r0 2
store64 8140000000000000344 r0
label start_ready
store64 8140000000000000360 0
store64 8140000000000000368 0
fstore 8140000000000000400 0
set r2 0
label clear_eligibility
mov r0 r2
mul r0 8
add r0 8140000000000230000
fstore $r0 0
add r0 10000
fstore $r0 0
add r2 1
cmp r2 1000
jlt clear_eligibility
label qrl_decision
call qrl_observe
load64 r0 8140000000000000320
cmp r0 3
jne circuit_policy
fset f21 0.5
jmp choose_action
label circuit_policy
call forward
label choose_action
load64 r0 8140000000000000320
cmp r0 2
je greedy_action
call random_uniform
fcmp f30 f21
jlt action_right
set r1 0
jmp action_chosen
label greedy_action
fcmp f21 0.5
jge action_right
set r1 0
jmp action_chosen
label action_right
set r1 1
label action_chosen
store64 8140000000000000376 r1
load64 r0 8140000000000000320
cmp r0 0
jne perform_transition
clock f27
itof f22 r1
fsub f22 f21
fstore 8140000000000000448 f22
fload f0 8140000000000000400
fadd f0 f22
fstore 8140000000000000400 f0
# The stochastic-gradient block cycles with actual training decisions.
mov r0 r12
add r0 8
load64 r9 $r0
mod r9 250
mul r9 4
call selected_gradients
mov r2 r9
label theta_eligibility
mov r0 r2
mul r0 8
add r0 8140000000000130000
fload f0 $r0
fmul f0 f22
mov r0 r2
mul r0 8
add r0 8140000000000240000
fload f1 $r0
fadd f1 f0
fstore $r0 f1
add r2 1
mov r0 r9
add r0 4
cmp r2 r0
jlt theta_eligibility
set r2 0
label readout_eligibility
mov r0 r2
mul r0 8
add r0 8140000000000310000
fload f0 $r0
fmul f0 f22
fdiv f0 31.622776601683793
mov r0 r2
mul r0 8
add r0 8140000000000230000
fload f1 $r0
fadd f1 f0
fstore $r0 f1
add r2 1
cmp r2 1000
jlt readout_eligibility
mov r0 r12
add r0 8
load64 r1 $r0
add r1 1
store64 $r0 r1
clock f29
fsub f29 f27
fload f0 8140000000000000504
fadd f0 f29
fstore 8140000000000000504 f0
label perform_transition
load64 r1 8140000000000000376
call random_uniform
fload f0 8140000000000000304
fcmp f30 f0
jge no_slip
set r0 1
sub r0 r1
mov r1 r0
label no_slip
load64 r2 8140000000000000344
mul r1 2
sub r1 1
add r2 r1
cmp r2 0
jge lower_bound
set r2 0
label lower_bound
cmp r2 6
jle upper_bound
set r2 6
label upper_bound
store64 8140000000000000344 r2
load64 r0 8140000000000000360
add r0 1
store64 8140000000000000360 r0
load64 r1 8140000000000000352
cmp r2 r1
je qrl_success
load64 r1 8140000000000000312
cmp r0 r1
jlt qrl_decision
jmp qrl_terminal
label qrl_success
store64 8140000000000000368 1
label qrl_terminal
load64 r0 8140000000000000368
itof f24 r0
load64 r0 8140000000000000360
itof f0 r0
fmul f0 0.02
fsub f24 f0
fstore 8140000000000000384 f24
load64 r0 8140000000000000320
cmp r0 0
jne qrl_report
clock f27
mov r0 r12
add r0 40
fload f0 $r0
fmov f22 f24
fsub f22 f0
fmul f0 0.9
fmov f1 f24
fmul f1 0.1
fadd f0 f1
fstore $r0 f0
set r2 0
label reinforce_parameters
# Gradient ascent using the actual return and recorded measured-policy scores.
mov r0 r2
mul r0 8
add r0 8140000000000230000
fload f0 $r0
fmul f0 f22
mov r0 r12
add r0 24
fload f1 $r0
fmul f0 f1
mov r0 r2
mul r0 8
add r0 r14
fload f1 $r0
fadd f1 f0
fmax f1 -4
fmin f1 4
fstore $r0 f1
mov r0 r2
mul r0 8
add r0 8140000000000240000
fload f0 $r0
fmul f0 f22
mov r0 r12
add r0 32
fload f1 $r0
fmul f0 f1
fmul f0 250
mov r0 r2
mul r0 8
add r0 r13
fload f1 $r0
fadd f1 f0
fmax f1 -6.283185307179586
fmin f1 6.283185307179586
fstore $r0 f1
call record_rotation_update
add r2 1
cmp r2 1000
jlt reinforce_parameters
fload f0 8140000000000000400
fmul f0 f22
mov r0 r12
add r0 24
fload f1 $r0
fmul f0 f1
mov r0 r12
add r0 16
fload f1 $r0
fadd f1 f0
fmax f1 -5
fmin f1 5
fstore $r0 f1
load64 r0 $r12
add r0 1
store64 $r12 r0
clock f29
fsub f29 f27
fload f0 8140000000000000504
fadd f0 f29
fstore 8140000000000000504 f0
label qrl_report
clock f29
fload f28 8140000000000000496
fsub f29 f28
femit episode_ms f29
fload f0 8140000000000000504
femit update_ms f0
fload f24 8140000000000000384
femit reward f24
load64 r0 8140000000000000368
itof f0 r0
femit success f0
load64 r0 8140000000000000360
itof f0 r0
femit decisions f0
ret

# Observable state -> 1000 feature angles. Four latent channels (relative
# displacement, position, goal, elapsed fraction) with per-wire calibration.
# Redundancy is disclosed; 1000 effective wires do not mean 1000 independent
# input bits or a proven 2^1000 learning capacity.
label qrl_observe
load64 r0 8140000000000000352
load64 r1 8140000000000000344
sub r0 r1
itof f24 r0
fdiv f24 6
itof f25 r1
fdiv f25 3
fsub f25 1
load64 r0 8140000000000000352
itof f26 r0
fdiv f26 3
fsub f26 1
load64 r0 8140000000000000360
itof f27 r0
load64 r0 8140000000000000312
itof f0 r0
fdiv f27 f0
set r2 0
label qrl_features
mov r0 r2
mod r0 4
fmov f0 f24
cmp r0 0
je qrl_feature_value
fmov f0 f25
cmp r0 1
je qrl_feature_value
fmov f0 f26
cmp r0 2
je qrl_feature_value
fmov f0 f27
label qrl_feature_value
fmul f0 1.1
fadd f0 1.2
mov r0 r2
mod r0 11
itof f1 r0
fmul f1 0.01
fsub f1 0.05
fadd f0 f1
mov r0 r2
mul r0 8
add r0 8140000000000300000
fstore $r0 f0
add r2 1
cmp r2 1000
jlt qrl_features
ret
