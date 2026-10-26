#!reverse-pc-machine-v1
# E011 extends the authentic E010 authority. No reset of previous learning.
load8 r0 7200000000000000002
cmp r0 1
jne invalid
load8 r0 7200000000000000003
cmp r0 2
jne invalid
load8 r0 7300000000000000000
cmp r0 0
jne invalid
store8 7300000000000000000 68
store8 7300000000000000001 76
store8 7300000000000000002 1
load8 r0 7200000000000000004
store8 7300000000000000003 r0
halt
label invalid
div r0 0
