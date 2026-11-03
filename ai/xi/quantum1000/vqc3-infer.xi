#!reverse-pc-machine-v1
store64 8140000000000000000 0
call select_agent
call forward
femit probability f21
set r0 0
fcmp f21 0.5
jlt classification_ready
set r0 1
label classification_ready
itof f0 r0
femit prediction f0
halt
