#!reverse-pc-machine-v1
# Teacher-supplied surface fragments at +500000. r0 is act number 1..15.
cmp r0 1
jlt invalid
cmp r0 16
jgt invalid
sub r0 1
mul r0 512
set r7 7800000000000500000
add r7 r0
load8 r0 7400000000000000003
sub r0 1
mul r0 256
add r7 r0
load8 r6 $r7
cmp r6 1
jlt invalid
add r7 1
set r13 0
halt
label invalid
div r0 0
