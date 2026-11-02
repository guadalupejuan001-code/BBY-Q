#!reverse-pc-machine-v1
# QRL-1000 environmental reward, computed by XI on the actually measured action.
# NOT a label passed into the QRL weight-update rule: only reward is passed.
load8 r0 8120000000000000000
cmp r0 166
jne invalid
load8 r1 8120000000000000001
cmp r1 1
jne invalid
load8 r2 8120000000000000003
cmp r2 1
jgt invalid
load8 r3 8120000000000000004
cmp r3 1
jgt invalid
set r4 0
cmp r2 r3
jne miss
set r4 100
label miss
store8 8120000000000000005 r4
print r4
print r3
halt
label invalid
div r0 0
