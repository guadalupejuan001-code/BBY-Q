#!reverse-pc-machine-v1
# E017 shares the original RVPC2. No imported or copied knowledge authority.
load8 r0 7800000000000000002
cmp r0 0
jne invalid
load8 r0 7700000000000000002
cmp r0 1
jne invalid
store8 7800000000000000000 79
store8 7800000000000000001 80
store8 7800000000000000002 1
set r0 256
mov r14 r0
mod r14 256
store8 7800000000000000004 r14
mov r14 r0
div r14 256
store8 7800000000000000005 r14
set r0 23
mov r14 r0
mod r14 256
store8 7800000000000000032 r14
mov r14 r0
div r14 256
store8 7800000000000000033 r14
halt
label invalid
div r0 0
