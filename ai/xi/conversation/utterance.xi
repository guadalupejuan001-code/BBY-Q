#!reverse-pc-machine-v1
# Select a teacher-supplied dialogue act; renderer gets only bytes in RVPC2.
load8 r0 7700000000000000019
cmp r0 1
jlt invalid
cmp r0 8
jgt invalid
load8 r1 7400000000000000003
set r7 7700000000000002000
sub r0 1
mul r0 512
add r7 r0
sub r1 1
mul r1 256
add r7 r1
load8 r6 $r7
cmp r6 1
jlt invalid
add r7 1
set r13 0
halt
label invalid
div r0 0
