#!reverse-pc-machine-v1
# Scientific ablation only, run on a disposable 1000+1000 qubit candidate.
# Flipping phase on remote last qubit MUST flip the measured root action.
load8 r0 8120000000000000000
cmp r0 166
jne invalid
load8 r1 8120000000000000001
cmp r1 1
jgt invalid
set r13 100
cmp r1 0
je start
set r13 1200
label start
mov r0 r13
add r0 999
z $r0
sub r0 1
mov r1 r13
add r1 999
label invert
cx $r0 $r1
sub r0 1
sub r1 1
cmp r0 r13
jge invert
h $r13
probz $r13
expect Z:$r13
halt
label invalid
div r0 0
