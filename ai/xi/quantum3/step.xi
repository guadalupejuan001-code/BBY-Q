# Environment terminal check and the unchanged learned QRL3 policy.
# A completed goal emits no action and does not evaluate a circuit.
label qrl_step
load64 r0 8140000000000000344
load64 r1 8140000000000000352
cmp r0 r1
je qrl_step_complete
store64 8140000000000000000 1
call select_agent
call qrl_observe
call forward
load64 r0 8140000000000000320
cmp r0 2
je qrl_step_greedy
call random_uniform
fcmp f30 f21
jlt qrl_step_right
set r0 0
jmp qrl_step_action
label qrl_step_greedy
fcmp f21 0.5
jge qrl_step_right
set r0 0
jmp qrl_step_action
label qrl_step_right
set r0 1
label qrl_step_action
itof f0 r0
femit action f0
femit probability_right f21
fset f0 0
femit terminal f0
ret
label qrl_step_complete
fset f0 1
femit terminal f0
ret
