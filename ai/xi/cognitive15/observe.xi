#!reverse-pc-machine-v1
# C15 XI policy. R+1 context, +4 C14 route, +5 C14 admission, +6 semantic.
# Q only proposes a replacement after >=3 verified outcomes and Q>=7000.
# C14 guarded/mixed classes never permit replacement. No memory mutation.
load8 r0 8280000000000000000
cmp r0 15
jne c15_bad
load8 r1 8280000000000000001
cmp r1 143
jgt c15_bad
load8 r2 8280000000000000004
cmp r2 3
jgt c15_bad
load8 r3 8280000000000000005
cmp r3 1
jgt c15_bad
load8 r4 8280000000000000006
cmp r4 7
jgt c15_bad
load8 r15 8280000000000000008
load8 r0 8280000000000000009
mul r0 256
add r15 r0
set r13 0
set r14 0
set r9 0
set r10 0
set r11 0
cmp r4 4
je c15_guard
cmp r4 7
je c15_guard
cmp r3 0
je c15_guard
set r13 1
set r14 1
mov r10 r2
set r0 0
set r12 -1
label c15_scan
mov r7 r1
mul r7 4
add r7 r0
mul r7 2
add r7 8280000000000001000
load8 r5 $r7
add r7 1
load8 r6 $r7
mul r6 256
add r5 r6
mov r7 r1
mul r7 4
add r7 r0
mul r7 2
add r7 8280000000000002400
load8 r8 $r7
add r7 1
load8 r6 $r7
mul r6 256
add r8 r6
cmp r8 3
jlt c15_next
cmp r5 r12
jle c15_next
mov r12 r5
mov r10 r0
mov r11 r8
label c15_next
add r0 1
cmp r0 4
jlt c15_scan
cmp r12 7000
jlt c15_prior
mov r9 r12
set r13 2
jmp c15_result
label c15_prior
mov r10 r2
set r9 0
set r11 0
jmp c15_result
label c15_guard
set r10 0
set r11 0
set r9 0
set r13 0
set r14 0
label c15_result
print r1
print r10
print r14
print r13
print r9
print r11
print r15
halt
label c15_bad
div r0 0
