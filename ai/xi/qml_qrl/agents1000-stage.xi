#!reverse-pc-machine-v1
# 1..32 feature positions, each 0..999, are staged into 1000-dimensional XI input.
# Host only transports index bytes; XI clears/validates the feature vector.
load8 r0 8120000000000000000
cmp r0 166
jne invalid
load8 r1 8120000000000000001
cmp r1 1
jgt invalid
load8 r2 8120000000000000002
cmp r2 1
jlt invalid
cmp r2 32
jgt invalid
set r3 0
label clear_input
mov r4 r3
add r4 8120000000000000300
store8 $r4 0
add r3 1
cmp r3 1000
jlt clear_input
set r3 0
label stage_input
mov r4 r3
mul r4 2
add r4 8120000000000000020
load8 r5 $r4
add r4 1
load8 r6 $r4
mul r6 256
add r5 r6
cmp r5 999
jgt invalid
mov r7 r5
add r7 8120000000000000300
store8 $r7 1
add r3 1
cmp r3 r2
jlt stage_input
print r2
halt
label invalid
div r0 0
