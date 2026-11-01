#!reverse-pc-machine-v1
# C12 isolated contextual Q learner, 9 P01 intents x 2 context flags x 4 actions.
# Actions: 0 legacy X10, 1 P05 memory, 2 P03 reason, 3 P04 compose.
load8 r0 8250000000000000000
cmp r0 0
jne invalid
store8 8250000000000000000 67
store8 8250000000000000005 0
store8 8250000000000000006 0
set r1 0
label clear_q
mov r2 r1
mul r2 2
add r2 8250000000000000100
store8 $r2 0
add r2 1
store8 $r2 0
add r1 1
cmp r1 72
jlt clear_q
set r0 67
print r0
halt
label invalid
div r0 0
