#!reverse-pc-machine-v1
# Functional concepts are supervised, not hardcoded word spellings.
# 7700000000000000016=5,+17=function index(1..26),+18=shared concept.
load8 r0 7700000000000000002
cmp r0 1
jne invalid
load8 r0 7700000000000000016
cmp r0 5
jne invalid
load8 r1 7700000000000000017
cmp r1 1
jlt invalid
cmp r1 26
jgt invalid
load8 r2 7700000000000000018
cmp r2 1
jlt invalid
set r7 7400000000000006000
add r7 r2
load8 r0 $r7
cmp r0 0
je invalid
set r7 7700000000000000512
add r7 r1
load8 r0 $r7
cmp r0 0
je write
cmp r0 r2
jne invalid
label write
store8 $r7 r2
halt
label invalid
div r0 0
