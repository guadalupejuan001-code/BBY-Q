#!reverse-pc-machine-v1
# Promote only an unambiguous concept with varied evidence and a separate
# successful validation campaign. No primitive identity comes from the host.
load8 r0 7900000000000000002
cmp r0 1
jne invalid
load8 r0 7900000000000000003
cmp r0 0
jne invalid
set r0 0
label model
set r7 7900000000000000128
mov r1 r0
mul r1 64
add r7 r1
load8 r2 $r7
mov r8 r7
add r8 1
load8 r3 $r8
cmp r2 r3
jne invalid
cmp r2 0
je invalid
add r8 2
load8 r3 $r8
cmp r3 1
jne invalid
add r8 2
load8 r3 $r8
add r8 1
load8 r4 $r8
add r3 r4
add r8 1
load8 r4 $r8
add r3 r4
cmp r3 0
je invalid
mov r8 r7
add r8 17
load8 r3 $r8
add r8 1
load8 r4 $r8
add r3 r4
add r8 1
load8 r4 $r8
add r3 r4
cmp r3 0
je invalid
set r3 1
set r4 1
label decode
cmp r3 r2
je decoded
mul r3 2
add r4 1
cmp r4 8
jle decode
jmp invalid
label decoded
add r7 2
store8 $r7 r4
add r0 1
cmp r0 8
jlt model
store8 7900000000000000003 1
halt
label invalid
div r0 0
