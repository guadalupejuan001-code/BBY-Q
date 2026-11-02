#!reverse-pc-machine-v1
# Controlled negative case only: corruption on a disposable RVPC2 copy.
load8 r0 8100000000000006000
cmp r0 113
jne invalid
store8 8100000000000006000 255
halt
label invalid
div r0 0
