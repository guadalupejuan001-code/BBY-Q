#!reverse-pc-machine-v1
# Designed topic-memory operation; syntax invoking it is learned. Never return
# an old answer: restore roles and route through current evidence and conflicts.
load8 r0 8000000000000000003
cmp r0 1
jne missing
load8 r0 8000000000000000025
cmp r0 2
je previous
load8 r8 7800000000000000072
load8 r14 7800000000000000073
mul r14 256
add r8 r14
cmp r8 0
je missing
set r10 0
label find
cmp r10 8
jge missing
set r7 8000000000000000128
mov r0 r10
mul r0 16
add r7 r0
load8 r0 $r7
cmp r0 1
jne missing
add r7 2
load8 r0 $r7
add r7 1
load8 r14 $r7
mul r14 256
add r0 r14
cmp r0 r8
je found
add r10 1
jmp find
label previous
set r10 1
label found
set r7 8000000000000000128
mul r10 16
add r7 r10
load8 r0 $r7
cmp r0 1
jne missing
add r7 1
load8 r0 $r7
store8 7800000000000000090 r0
add r7 1
set r1 0
label copy_role
mov r2 r7
add r2 r1
load8 r0 $r2
set r2 7800000000000000072
add r2 r1
store8 $r2 r0
add r1 1
cmp r1 6
jlt copy_role
store8 7800000000000000012 0
store8 7800000000000000067 2
halt
label missing
store8 7800000000000000012 0
store8 7800000000000000080 12
store8 7800000000000000067 5
halt
