#!reverse-pc-machine-v1
load8 r0 7700000000000000002
cmp r0 0
je done
cmp r0 1
jne invalid
set r0 16
label scratch
set r7 7700000000000000000
add r7 r0
store8 $r7 0
add r0 1
cmp r0 256
jlt scratch
label done
halt
label invalid
div r0 0
