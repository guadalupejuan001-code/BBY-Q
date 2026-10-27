#!reverse-pc-machine-v1
# +306=u16 concept. +302=1 means use original C name resolver;2=direct bytes.
load8 r2 7800000000000000306
load8 r14 7800000000000000307
mul r14 256
add r2 r14
cmp r2 0
je invalid
cmp r2 255
jgt extended
store8 7700000000000000040 r2
store8 7800000000000000302 1
halt
label extended
load8 r10 7800000000000000006
load8 r14 7800000000000000007
mul r14 256
add r10 r14
load8 r11 7400000000000000003
set r0 0
set r12 0
label lexeme
cmp r0 r10
jge fallback
set r7 7800000000000100000
mov r1 r0
mul r1 40
add r7 r1
mov r15 r7
load8 r1 $r15
add r15 1
load8 r14 $r15
mul r14 256
add r1 r14
cmp r1 r2
jne next
cmp r12 0
jne language
mov r12 r7
label language
mov r8 r7
add r8 3
load8 r1 $r8
cmp r1 r11
je selected
label next
add r0 1
jmp lexeme
label fallback
cmp r12 0
je invalid
mov r7 r12
label selected
add r7 4
load8 r6 $r7
add r7 1
load8 r13 7700000000000000038
store8 7800000000000000302 2
halt
label invalid
div r0 0
