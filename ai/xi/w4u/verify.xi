#!reverse-pc-machine-v1
# Verifier independently validates the complete proposal, its relation to the
# user's goal, the current step and fresh desktop evidence before dispatch.
load8 r0 8300000000000000016
cmp r0 1
jne done
store8 8200000000000000064 0
store8 8200000000000000065 0
load8 r0 8200000000000000016
cmp r0 1
jne disconnected
load8 r10 8300000000000000017
load8 r11 8300000000000000018
load8 r12 8300000000000000019
load8 r13 8300000000000000020
cmp r12 1
jlt reject
cmp r12 2
jgt reject
cmp r13 r12
jge reject
load8 r0 8300000000000000129
cmp r0 r11
jne reject
load8 r0 8300000000000000128
cmp r12 1
jne two
cmp r0 r10
jne reject
jmp step
label two
cmp r0 1
jne reject
load8 r0 8300000000000000130
cmp r0 r10
jne reject
load8 r0 8300000000000000131
cmp r0 r11
jne reject
cmp r10 2
je step
cmp r10 4
je step
cmp r10 5
je step
cmp r10 10
jne reject
label step
mov r7 r13
mul r7 2
add r7 8300000000000000128
load8 r0 $r7
add r7 1
load8 r1 $r7
cmp r0 1
jlt reject
cmp r0 10
jgt reject
cmp r0 7
jlt window
cmp r0 8
jle global
cmp r0 9
je space
# Running a program requires a catalog capability AND its unique open window.
cmp r1 16
jlt reject
cmp r1 31
jgt reject
set r7 8300000000000000512
add r7 r1
load8 r2 $r7
cmp r2 2
jne reject
jmp unique
label window
cmp r1 1
jlt reject
cmp r1 10
jle capability_ok
cmp r1 15
je current
cmp r1 16
jlt reject
cmp r1 31
jgt reject
set r7 8300000000000000512
add r7 r1
load8 r2 $r7
cmp r2 1
jlt missing
cmp r2 2
jgt reject
label capability_ok
cmp r0 1
jne unique
set r7 8200000000000000032
add r7 r1
load8 r2 $r7
cmp r2 0
jne accept
load8 r2 8200000000000000018
cmp r2 12
jge reject
jmp accept
label unique
set r7 8200000000000000032
add r7 r1
load8 r2 $r7
cmp r2 0
je missing
cmp r2 1
jne reject
jmp accept
label current
cmp r0 1
je reject
load8 r2 8200000000000000017
cmp r2 0
je missing
jmp accept
label global
cmp r1 0
jne reject
jmp accept
label space
cmp r1 13
je accept
cmp r1 14
jne reject
label accept
store8 8200000000000000064 r0
store8 8200000000000000065 r1
store8 8200000000000000067 1
store8 8300000000000000016 2
store8 8300000000000000034 1
halt
label disconnected
set r0 4
jmp fail
label missing
set r0 5
jmp fail
label reject
set r0 6
label fail
store8 8300000000000000034 2
store8 8300000000000000016 4
store8 8200000000000000067 r0
label done
halt
