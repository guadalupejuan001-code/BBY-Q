#!reverse-pc-machine-v1
# Extend the existing E012 authority. Never clear/retrain an earlier region.
load8 r0 7500000000000000000
cmp r0 0
jne invalid
load8 r0 7500000000000000002
cmp r0 0
jne invalid
load8 r0 7400000000000000002
cmp r0 1
jne invalid
load8 r0 7300000000000000002
cmp r0 1
jne invalid
store8 7500000000000000000 83
store8 7500000000000000001 84
store8 7500000000000000002 1
halt
label invalid
div r0 0
