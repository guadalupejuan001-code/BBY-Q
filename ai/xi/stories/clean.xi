#!reverse-pc-machine-v1
# Restore the pre-turn E011 arithmetic context, including after any abstention.
set r0 0
label restore_arithmetic
set r7 7500000000000002200
add r7 r0
load8 r1 $r7
store8 $r7 0
set r7 7300000000000000000
add r7 r0
store8 $r7 r1
add r0 1
cmp r0 16
jlt restore_arithmetic
set r0 16
label arithmetic_scratch
set r7 7300000000000000000
add r7 r0
store8 $r7 0
add r0 1
cmp r0 64
jlt arithmetic_scratch
set r0 512
label arithmetic_token
set r7 7300000000000000000
add r7 r0
store8 $r7 0
add r0 1
cmp r0 530
jlt arithmetic_token
set r0 800
label arithmetic_resolved
set r7 7300000000000000000
add r7 r0
store8 $r7 0
add r0 1
cmp r0 812
jlt arithmetic_resolved
set r0 16
label control
set r7 7500000000000000000
add r7 r0
store8 $r7 0
add r0 1
cmp r0 64
jlt control
set r0 0
label staging
set r7 7500000000000002000
add r7 r0
store8 $r7 0
add r0 1
cmp r0 128
jlt staging
halt
