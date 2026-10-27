#!reverse-pc-machine-v1
load8 r0 7800000000000000246
load8 r1 7800000000000000208
cmp r0 0
jne premise
cmp r1 1
je next
cmp r1 0
je failed
store8 7800000000000000249 1
jmp failed
label premise
cmp r0 1
jne family
cmp r1 1
jne failed
jmp next
label family
cmp r1 1
jne next
load8 r2 7800000000000000248
cmp r0 2
jne inheritance
add r2 1
jmp mask
label inheritance
add r2 2
label mask
store8 7800000000000000248 r2
label next
add r0 1
store8 7800000000000000246 r0
halt
label failed
store8 7800000000000000248 0
store8 7800000000000000246 4
halt
