#!reverse-pc-machine-v1
# Acknowledgement is an observation, not proof on its own. Verify observable
# postconditions; run/arrange/current-window use the host's typed outcome.
store8 8200000000000000064 0
store8 8200000000000000065 0
load8 r0 8300000000000000016
cmp r0 2
jne fail
load8 r0 8300000000000000080
cmp r0 1
jne fail
load8 r0 8200000000000000016
cmp r0 1
jne fail
load8 r12 8300000000000000019
load8 r13 8300000000000000020
cmp r12 1
jlt fail
cmp r12 2
jgt fail
cmp r13 r12
jge fail
mov r7 r13
mul r7 2
add r7 8300000000000000128
load8 r0 $r7
add r7 1
load8 r1 $r7
cmp r0 1
jlt fail
cmp r0 10
jgt fail
cmp r0 7
je passed
cmp r0 8
je desktop
cmp r0 9
je space
cmp r0 10
je passed
cmp r1 15
je passed
cmp r1 1
jlt fail
cmp r1 31
jgt fail
set r7 8200000000000000032
add r7 r1
load8 r2 $r7
cmp r0 6
je closed
cmp r2 1
jlt fail
cmp r0 1
je passed
cmp r0 2
je focused
cmp r0 3
je minimized
set r7 8300000000000000672
add r7 r1
load8 r2 $r7
cmp r0 4
je maximized
cmp r0 5
jne fail
cmp r2 0
jne fail
jmp passed
label closed
cmp r2 0
jne fail
jmp passed
label focused
load8 r2 8200000000000000017
cmp r2 r1
jne fail
jmp passed
label minimized
set r7 8300000000000000640
add r7 r1
load8 r2 $r7
cmp r2 1
jlt fail
jmp passed
label maximized
cmp r2 1
jlt fail
jmp passed
label desktop
load8 r2 8300000000000000711
load8 r3 8200000000000000018
cmp r2 r3
jne fail
jmp passed
label space
load8 r2 8300000000000000710
sub r1 13
cmp r2 r1
jne fail
label passed
add r13 1
store8 8300000000000000020 r13
cmp r13 r12
jge complete
store8 8300000000000000016 1
halt
label complete
store8 8300000000000000016 3
store8 8200000000000000067 2
halt
label fail
store8 8300000000000000034 2
store8 8300000000000000016 4
store8 8200000000000000067 3
halt
