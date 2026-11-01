#!reverse-pc-machine-v1
# Cambia exclusivamente el objetivo QRL a |0>.
load8 r0 8100000000000002000
cmp r0 82
jne invalid
store8 8100000000000002003 0
halt
label invalid
div r0 0
