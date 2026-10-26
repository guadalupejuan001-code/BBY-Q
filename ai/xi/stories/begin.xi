#!reverse-pc-machine-v1
# Stage a whole turn. No episode fact is published before all clauses pass.
# E011's prior arithmetic context is backed up and restored after the answer.
set r0 8
label result
set r7 7500000000000000000
add r7 r0
store8 $r7 0
add r0 1
cmp r0 16
jlt result
store8 7500000000000000008 1
store8 7400000000000000013 4
set r0 0
label backup_arithmetic
set r7 7300000000000000000
add r7 r0
load8 r1 $r7
set r7 7500000000000002200
add r7 r0
store8 $r7 r1
add r0 1
cmp r0 16
jlt backup_arithmetic
set r0 0
label stage_ledger
set r7 7500000000000001000
add r7 r0
load8 r1 $r7
set r7 7500000000000002000
add r7 r0
store8 $r7 r1
add r0 1
cmp r0 128
jlt stage_ledger
load8 r0 7500000000000000006
cmp r0 16
jgt invalid
store8 7500000000000000032 r0
halt
label invalid
div r0 0
