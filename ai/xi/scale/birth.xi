#!reverse-pc-machine-v1
# E020: bounded streaming numerical concept learner. Own M region only.
load8 r0 7900000000000000002
cmp r0 0
jne invalid
store8 7900000000000000000 77
store8 7900000000000000001 83
store8 7900000000000000002 1
set r0 0
label model
set r7 7900000000000000128
mov r1 r0
mul r1 64
add r7 r1
store8 $r7 255
add r0 1
cmp r0 8
jlt model
halt
label invalid
div r0 0
