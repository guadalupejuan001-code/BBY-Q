#!reverse-pc-machine-v1
# Single evidence view over the immutable old graph and new taught assertions.
# Input +200/202/204 S/P/O u16; output +208=0/1/2/3, +209 provenance bitmask.
load8 r2 7800000000000000200
load8 r14 7800000000000000201
mul r14 256
add r2 r14
load8 r3 7800000000000000202
load8 r14 7800000000000000203
mul r14 256
add r3 r14
load8 r4 7800000000000000204
load8 r14 7800000000000000205
mul r14 256
add r4 r14
set r8 0
set r9 0
set r10 0
cmp r2 0
je finish
cmp r3 0
je finish
cmp r4 0
je finish
cmp r2 255
jgt extension
cmp r3 255
jgt extension
cmp r4 255
jgt extension
mov r7 r2
mul r7 256
add r7 r3
mul r7 256
add r7 r4
mul r7 4
add r7 7400000000001000000
load8 r8 $r7
add r7 1
load8 r9 $r7
mov r0 r8
add r0 r9
cmp r0 0
je extension
set r10 1
label extension
mov r7 r2
mul r7 65536
add r7 r3
mul r7 65536
add r7 r4
mul r7 4
add r7 7800000010000000000
load8 r0 $r7
add r8 r0
add r7 1
load8 r1 $r7
add r9 r1
add r0 r1
cmp r0 0
je finish
add r10 2
label finish
set r0 0
cmp r8 0
je negative
set r0 1
label negative
cmp r9 0
je done
add r0 2
label done
store8 7800000000000000208 r0
store8 7800000000000000209 r10
halt
