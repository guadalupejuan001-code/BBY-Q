#!reverse-pc-machine-v1
# Explicit new fictional episode. Close any native session before structured
# teaching/control programs. Learned words, effects and prior regions survive.
load8 r0 7500000000000000002
cmp r0 1
jne invalid
load8 r0 7500000000000000016
cmp r0 0
jne invalid
store8 7500000000000000006 0
set r0 8
label output
set r7 7500000000000000000
add r7 r0
store8 $r7 0
add r0 1
cmp r0 16
jlt output
set r0 0
label ledger
set r7 7500000000000001000
add r7 r0
store8 $r7 0
add r0 1
cmp r0 128
jlt ledger
halt
label invalid
div r0 0
