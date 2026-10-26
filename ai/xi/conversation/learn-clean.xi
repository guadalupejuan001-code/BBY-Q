#!reverse-pc-machine-v1
set r0 16
label conversation
set r7 7700000000000000000
add r7 r0
store8 $r7 0
add r0 1
cmp r0 256
jlt conversation
set r0 16
label intake
set r7 7400000000000000000
add r7 r0
store8 $r7 0
add r0 1
cmp r0 2048
jlt intake
halt
