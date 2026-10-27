#!reverse-pc-machine-v1
load8 r0 8100000000000000003
cmp r0 0
jne invalid
store8 8100000000000000003 1
halt
label invalid
div r0 0
