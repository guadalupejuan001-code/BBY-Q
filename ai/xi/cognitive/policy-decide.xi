#!reverse-pc-machine-v1
# Deterministic greedy shadow decision; reads Ether, never modifies weights.
load8 r0 8250000000000000000
cmp r0 67
jne invalid
load8 r1 8250000000000000001
cmp r1 17
jgt invalid
set r3 0
set r4 0
set r5 -1
label search
mov r7 r1
mul r7 4
add r7 r3
mul r7 2
add r7 8250000000000000100
load8 r8 $r7
add r7 1
load8 r9 $r7
mul r9 256
add r8 r9
cmp r8 r5
jle keep
mov r4 r3
mov r5 r8
label keep
add r3 1
cmp r3 4
jlt search
load8 r10 8250000000000000005
load8 r11 8250000000000000006
mul r11 256
add r10 r11
print r1
print r4
print r5
print r10
halt
label invalid
div r0 0
