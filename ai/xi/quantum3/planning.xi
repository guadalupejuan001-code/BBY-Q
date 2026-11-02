# Explicit model-based planning experiment: two candidate actions, two
# stochastic policy rollouts per candidate, horizon three. The transition and
# terminal reward rules are known, not learned. The QRL circuit guides every
# rollout continuation; there is no programmed goal-to-action lookup.
label plan_action
load64 r0 8140000000000000344
store64 8140000000000000600 r0
load64 r0 8140000000000000360
store64 8140000000000000608 r0
load64 r0 8140000000000000256
store64 8140000000000000616 r0
fstore 8140000000000000688 f21
store64 8140000000000000624 0
label plan_candidate
store64 8140000000000000632 0
fstore 8140000000000000696 0
label plan_rollout
load64 r0 8140000000000000600
store64 8140000000000000344 r0
load64 r0 8140000000000000608
store64 8140000000000000360 r0
store64 8140000000000000640 0
fstore 8140000000000000648 0
load64 r0 8140000000000000624
store64 8140000000000000680 r0
label plan_simulated_transition
load64 r1 8140000000000000680
call random_uniform
fload f0 8140000000000000304
fcmp f30 f0
jge planned_no_slip
set r0 1
sub r0 r1
mov r1 r0
label planned_no_slip
load64 r2 8140000000000000344
mul r1 2
sub r1 1
add r2 r1
cmp r2 0
jge planned_lower
set r2 0
label planned_lower
cmp r2 6
jle planned_upper
set r2 6
label planned_upper
store64 8140000000000000344 r2
load64 r0 8140000000000000360
add r0 1
store64 8140000000000000360 r0
fload f0 8140000000000000648
fsub f0 0.02
fstore 8140000000000000648 f0
load64 r0 8140000000000000352
cmp r2 r0
jne rollout_not_success
fadd f0 1
fstore 8140000000000000648 f0
jmp rollout_finished
label rollout_not_success
load64 r0 8140000000000000640
add r0 1
store64 8140000000000000640 r0
cmp r0 3
jge rollout_finished
load64 r0 8140000000000000360
load64 r1 8140000000000000312
cmp r0 r1
jge rollout_finished
call qrl_observe
call forward
call random_uniform
set r0 0
fcmp f30 f21
jge planned_policy_action
set r0 1
label planned_policy_action
store64 8140000000000000680 r0
jmp plan_simulated_transition
label rollout_finished
fload f0 8140000000000000648
fload f1 8140000000000000696
fadd f1 f0
fstore 8140000000000000696 f1
load64 r0 8140000000000000632
add r0 1
store64 8140000000000000632 r0
cmp r0 2
jlt plan_rollout
load64 r0 8140000000000000624
cmp r0 1
je candidate_one_finished
fstore 8140000000000000656 f1
store64 8140000000000000624 1
jmp plan_candidate
label candidate_one_finished
fstore 8140000000000000664 f1
load64 r0 8140000000000000600
store64 8140000000000000344 r0
load64 r0 8140000000000000608
store64 8140000000000000360 r0
load64 r0 8140000000000000616
store64 8140000000000000256 r0
fload f0 8140000000000000656
fload f1 8140000000000000664
fcmp f0 f1
jgt plan_zero
jlt plan_one
# Equal rollouts fall back to the original measured policy, not a goal rule.
call random_uniform
fload f0 8140000000000000688
fcmp f30 f0
jlt plan_one
label plan_zero
set r1 0
ret
label plan_one
set r1 1
ret
