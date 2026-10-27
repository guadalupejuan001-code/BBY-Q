#!reverse-pc-machine-v1
# Supervised question spellings, global and preceding-cue veto concepts for the compositional clause
# parser. Only this teacher route writes the table; an ordinary query cannot.
load8 r0 8000000000000000002
cmp r0 1
jne invalid
load8 r0 8000000000000000003
cmp r0 0
jne invalid
load8 r0 7400000000000000040
cmp r0 0
jne invalid
load8 r0 7400000000000000032
cmp r0 1
jne invalid
load8 r11 8000000000000000048
cmp r11 1
jlt invalid
cmp r11 3
jgt invalid
load8 r9 7400000000000000512
load8 r8 7800000000000001024
load8 r14 7800000000000001025
mul r14 256
add r8 r14
cmp r8 0
je invalid
load8 r0 7800000000000001026
cmp r0 3
jne invalid
load8 r10 8000000000000000005
cmp r10 16
jge invalid
set r7 8000000000000001000
mov r0 r10
mul r0 40
add r7 r0
store8 $r7 r11
add r7 1
store8 $r7 r9
add r7 1
mov r0 r8
mod r0 256
store8 $r7 r0
add r7 1
div r8 256
store8 $r7 r8
add r7 1
set r0 0
label copy
cmp r0 r9
jge publish
set r1 7400000000000000513
add r1 r0
load8 r2 $r1
mov r1 r7
add r1 r0
store8 $r1 r2
add r0 1
jmp copy
label publish
add r10 1
store8 8000000000000000005 r10
store8 8000000000000000048 0
halt
label invalid
div r0 0
