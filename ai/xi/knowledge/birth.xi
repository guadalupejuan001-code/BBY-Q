#!reverse-pc-machine-v1
# E012 extends the SAME authentic E011 RVPC2; all earlier knowledge is reused.
load8 r0 7300000000000000002
cmp r0 1
jne invalid
load8 r0 7400000000000000000
cmp r0 0
jne invalid
store8 7400000000000000000 75
store8 7400000000000000001 78
store8 7400000000000000002 1
load8 r0 7300000000000000003
store8 7400000000000000003 r0
# Shared concept IDs 1..22 are the existing E010 prototypes, not copies.
set r0 1
label ground_existing
set r7 7400000000000006000
add r7 r0
store8 $r7 1
add r0 1
cmp r0 22
jle ground_existing
halt
label invalid
div r0 0
