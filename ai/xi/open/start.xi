#!reverse-pc-machine-v1
# Source linker supplies the surface mode in r13 (1 conversation,2 compact).
load8 r0 7800000000000000002
cmp r0 0
je done
cmp r0 1
jne invalid
store8 7800000000000000063 r13
label done
halt
label invalid
div r0 0
