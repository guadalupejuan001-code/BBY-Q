#!reverse-pc-machine-v1
# Supervised semantic labels for shared question/connective concept IDs.
# 7500000000000000016=2, +17=role (1 question / 2 conjunction), +18=shared concept.
load8 r0 7500000000000000002
cmp r0 1
jne invalid
load8 r0 7500000000000000016
cmp r0 2
jne invalid
load8 r2 7500000000000000017
cmp r2 1
jlt invalid
cmp r2 2
jgt invalid
load8 r3 7500000000000000018
cmp r3 0
je invalid
set r7 7400000000000006000
add r7 r3
load8 r0 $r7
cmp r0 3
jne invalid
set r7 7500000000000000003
add r7 r2
load8 r0 $r7
cmp r0 0
je check_other
cmp r0 r3
jne invalid
label check_other
set r8 7500000000000000006
sub r8 r2
load8 r0 $r8
cmp r0 r3
je invalid
store8 $r7 r3
set r0 16
label clean
set r7 7500000000000000000
add r7 r0
store8 $r7 0
add r0 1
cmp r0 64
jlt clean
halt
label invalid
div r0 0
