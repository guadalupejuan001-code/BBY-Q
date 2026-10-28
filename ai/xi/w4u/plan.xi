#!reverse-pc-machine-v1
# Planner's state and goal, in the owner's shared Ether/RVPC2.
# M=8300000000000000000. No language/model logic lives in the host.
set r0 16
label reset
set r7 8300000000000000000
add r7 r0
store8 $r7 0
add r0 1
cmp r0 64
jlt reset
set r0 128
label reset_steps
set r7 8300000000000000000
add r7 r0
store8 $r7 0
add r0 1
cmp r0 132
jlt reset_steps
load8 r0 8200000000000000067
cmp r0 1
jne done
load8 r0 8300000000000000000
cmp r0 77
jne invalid
load8 r0 8300000000000000001
cmp r0 1
jne invalid
load8 r0 8200000000000000064
load8 r1 8200000000000000065
store8 8300000000000000017 r0
store8 8300000000000000018 r1
store8 8300000000000000016 1
store8 8300000000000000032 1
label done
halt
label invalid
store8 8200000000000000064 0
store8 8200000000000000065 0
store8 8200000000000000067 6
store8 8300000000000000016 4
halt
