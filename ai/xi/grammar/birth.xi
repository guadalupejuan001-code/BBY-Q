#!reverse-pc-machine-v1
# Add a bounded grammar learner to the existing authority, preserving all E014.
load8 r0 7600000000000000000
cmp r0 0
jne invalid
load8 r0 7600000000000000002
cmp r0 0
jne invalid
load8 r0 7500000000000000002
cmp r0 1
jne invalid
store8 7600000000000000000 71
store8 7600000000000000001 82
store8 7600000000000000002 1
halt
label invalid
div r0 0
