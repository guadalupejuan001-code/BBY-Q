#!reverse-pc-machine-v1
# S/P/O at +72/74/76; intent +64=3 positive,4 negative,7 retract dialogue layer.
# This never overwrites any original K byte. Exact repeats do not grow indexes.
load8 r2 7800000000000000072
load8 r14 7800000000000000073
mul r14 256
add r2 r14
load8 r3 7800000000000000074
load8 r14 7800000000000000075
mul r14 256
add r3 r14
load8 r4 7800000000000000076
load8 r14 7800000000000000077
mul r14 256
add r4 r14
load8 r5 7800000000000000064
cmp r2 0
je invalid
cmp r3 0
je invalid
cmp r4 0
je invalid
mov r7 r2
mul r7 65536
add r7 r3
mul r7 65536
add r7 r4
mul r7 4
add r7 7800000010000000000
cmp r5 7
je retract
# Avoid recording a second positive/negative copy of an identical old fact.
cmp r2 255
jgt publish
cmp r3 255
jgt publish
cmp r4 255
jgt publish
mov r0 r2
mul r0 256
add r0 r3
mul r0 256
add r0 r4
mul r0 4
add r0 7400000000001000000
cmp r5 3
je old_support
add r0 1
label old_support
load8 r0 $r0
cmp r0 0
jne learned
label publish
mov r6 r7
add r6 2
load8 r0 $r6
cmp r0 1
je support
load8 r11 7800000000000000008
load8 r14 7800000000000000009
mul r14 256
add r11 r14
cmp r11 1024
jge invalid
store8 $r6 1
set r0 7800000000000200000
mov r1 r11
mul r1 6
add r0 r1
mov r15 r0
mov r14 r2
mod r14 256
store8 $r15 r14
add r15 1
mov r14 r2
div r14 256
store8 $r15 r14
add r0 2
mov r15 r0
mov r14 r3
mod r14 256
store8 $r15 r14
add r15 1
mov r14 r3
div r14 256
store8 $r15 r14
add r0 2
mov r15 r0
mov r14 r4
mod r14 256
store8 $r15 r14
add r15 1
mov r14 r4
div r14 256
store8 $r15 r14
add r11 1
mov r14 r11
mod r14 256
store8 7800000000000000008 r14
mov r14 r11
div r14 256
store8 7800000000000000009 r14
label support
cmp r5 3
je positive
add r7 1
label positive
store8 $r7 1
label learned
cmp r2 255
jgt learned_ready
store8 7800000000000000040 1
label learned_ready
store8 7800000000000000080 5
halt
label retract
store8 $r7 0
add r7 1
store8 $r7 0
store8 7800000000000000080 7
halt
label invalid
div r0 0
