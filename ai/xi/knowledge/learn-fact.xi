#!reverse-pc-machine-v1
load8 r0 7400000000000000002
cmp r0 1
jne invalid
# event=2; subject/predicate/object +25/26/27; polarity +28; source +29.
# 1/2 assert positive/negative provenance; 3/4 retract corresponding support.
# Facts occupy sparse keyed Ether cells, not an external host database.
load8 r0 7400000000000000024
cmp r0 2
jne invalid
load8 r2 7400000000000000025
load8 r3 7400000000000000026
load8 r4 7400000000000000027
cmp r2 1
jlt invalid
cmp r3 1
jlt invalid
cmp r4 1
jlt invalid
set r7 7400000000000006000
add r7 r2
load8 r0 $r7
cmp r0 1
jlt invalid
cmp r0 2
jgt invalid
set r7 7400000000000006000
add r7 r3
load8 r0 $r7
cmp r0 2
jne invalid
set r7 7400000000000006000
add r7 r4
load8 r0 $r7
cmp r0 1
jlt invalid
cmp r0 2
jgt invalid
load8 r5 7400000000000000028
cmp r5 1
jlt invalid
cmp r5 4
jgt invalid
load8 r6 7400000000000000029
cmp r5 2
jgt provenance_ok
cmp r6 1
jlt invalid
label provenance_ok
mov r7 r2
mul r7 256
add r7 r3
mul r7 256
add r7 r4
mul r7 4
add r7 7400000000001000000

mov r11 r7
load8 r8 $r7
add r7 1
load8 r9 $r7
mov r12 r8
add r12 r9
cmp r5 1
je positive
cmp r5 2
je negative
cmp r5 3
je retract_positive
set r9 0
jmp publish
label retract_positive
set r8 0
jmp publish
label positive
cmp r8 0
jne publish
mov r8 r6
jmp publish
label negative
cmp r9 0
jne publish
mov r9 r6
label publish
load8 r13 7400000000000000006
load8 r0 7400000000000000007
mul r0 256
add r13 r0
mov r7 r11
add r7 2
load8 r14 $r7
cmp r14 1
je count_ready
cmp r14 0
jne invalid
mov r0 r8
add r0 r9
cmp r0 0
je count_ready
cmp r13 512
jge invalid
store8 $r7 1
set r7 7400000000000080000
mov r0 r13
mul r0 3
add r7 r0
store8 $r7 r2
add r7 1
store8 $r7 r3
add r7 1
store8 $r7 r4
add r13 1
label count_ready
store8 $r11 r8
add r11 1
store8 $r11 r9
mov r0 r13
mod r0 256
store8 7400000000000000006 r0
div r13 256
store8 7400000000000000007 r13
set r0 16
label clean
set r7 7400000000000000000
add r7 r0
store8 $r7 0
add r0 1
cmp r0 2048
jlt clean
halt
label invalid
div r0 0
