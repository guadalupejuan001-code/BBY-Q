#!reverse-pc-machine-v1
load8 r0 8100000000000000003
cmp r0 1
jne invalid
mem_stats
stats
halt
label invalid
div r0 0
