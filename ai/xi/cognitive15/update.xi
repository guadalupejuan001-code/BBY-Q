#!reverse-pc-machine-v1
# Terminal one-step TD(0): Q <- Q + trunc((100*reward-Q)/2), XI only.
# Reward belongs ONLY to route actually executed in a preserved X10 receipt.
# Input byte offsets R+1=context, +2=executed action, +3=reward 0..100.
load8 r0 8280000000000000000
cmp r0 15
jne c15_bad
load8 r1 8280000000000000001
cmp r1 143
jgt c15_bad
load8 r2 8280000000000000002
cmp r2 3
jgt c15_bad
load8 r3 8280000000000000003
cmp r3 100
jgt c15_bad
load8 r10 8280000000000000008
load8 r11 8280000000000000009
mul r11 256
add r10 r11
cmp r10 65535
jge c15_bad
mov r4 r1
mul r4 4
add r4 r2
mul r4 2
add r4 8280000000000001000
load8 r5 $r4
mov r6 r4
add r6 1
load8 r7 $r6
mul r7 256
add r5 r7
mov r8 r4
sub r8 8280000000000001000
add r8 8280000000000002400
load8 r9 $r8
mov r11 r8
add r11 1
load8 r12 $r11
mul r12 256
add r9 r12
cmp r9 65535
jge c15_bad
mul r3 100
sub r3 r5
div r3 2
add r5 r3
cmp r5 0
jlt c15_bad
cmp r5 10000
jgt c15_bad
add r9 1
add r10 1
mov r13 r5
mod r13 256
store8 $r4 r13
mov r13 r5
div r13 256
store8 $r6 r13
mov r13 r9
mod r13 256
store8 $r8 r13
mov r13 r9
div r13 256
store8 $r11 r13
mov r13 r10
mod r13 256
store8 8280000000000000008 r13
mov r13 r10
div r13 256
store8 8280000000000000009 r13
store8 8280000000000000001 0
store8 8280000000000000002 0
store8 8280000000000000003 0
print r1
print r2
print r5
print r9
print r10
halt
label c15_bad
div r0 0
