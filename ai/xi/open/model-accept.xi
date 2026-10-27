#!reverse-pc-machine-v1
load8 r0 7800000000000000250
add r0 1
store8 7800000000000000250 r0
load8 r0 7800000000000000249
cmp r0 0
je support
store8 7800000000000000253 1
label support
load8 r1 7800000000000000248
cmp r1 0
je done
load8 r0 7800000000000000251
add r0 1
store8 7800000000000000251 r0
load8 r2 7800000000000000252
set r3 0
mov r0 r1
mod r0 2
cmp r0 0
je second
mov r0 r2
mod r0 2
cmp r0 0
je second
add r3 1
label second
cmp r1 2
jlt ready
cmp r2 2
jlt ready
add r3 2
label ready
store8 7800000000000000252 r3
label done
halt
