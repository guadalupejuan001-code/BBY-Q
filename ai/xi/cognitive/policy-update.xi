#!reverse-pc-machine-v1
# Explicit outcome annotation: Q += trunc((reward-Q)/2). No implicit feedback.
load8 r0 8250000000000000000
cmp r0 67
jne invalid
load8 r1 8250000000000000001
cmp r1 17
jgt invalid
load8 r2 8250000000000000002
cmp r2 3
jgt invalid
load8 r3 8250000000000000003
load8 r4 8250000000000000004
mul r4 256
add r3 r4
cmp r3 10000
jgt invalid
mov r7 r1
mul r7 4
add r7 r2
mul r7 2
add r7 8250000000000000100
load8 r8 $r7
add r7 1
load8 r9 $r7
mul r9 256
add r8 r9
mov r10 r3
sub r10 r8
div r10 2
add r8 r10
mov r11 r8
mod r11 256
sub r7 1
store8 $r7 r11
add r7 1
mov r11 r8
div r11 256
store8 $r7 r11
load8 r12 8250000000000000005
load8 r13 8250000000000000006
mul r13 256
add r12 r13
cmp r12 65535
jge invalid
add r12 1
mov r11 r12
mod r11 256
store8 8250000000000000005 r11
mov r11 r12
div r11 256
store8 8250000000000000006 r11
print r1
print r2
print r8
print r12
halt
label invalid
div r0 0
