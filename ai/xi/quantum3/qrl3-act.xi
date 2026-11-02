#!reverse-pc-machine-v1
store64 8140000000000000000 1
call select_agent
call forward
load64 r0 8140000000000000320
cmp r0 2
je act_greedy
call random_uniform
fcmp f30 f21
jlt act_right
set r0 0
jmp act_ready
label act_greedy
fcmp f21 0.5
jge act_right
set r0 0
jmp act_ready
label act_right
set r0 1
label act_ready
itof f0 r0
femit action f0
femit probability_right f21
halt
