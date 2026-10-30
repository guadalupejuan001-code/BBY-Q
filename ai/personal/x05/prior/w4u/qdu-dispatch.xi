#!reverse-pc-machine-v1
# w4U XI: consume one-use authorization for an unchanged typed program request.
load8 r0 8300000000000000768
cmp r0 1
jne denied
load8 r0 8300000000000000773
cmp r0 0
jne denied
load8 r0 8300000000000000774
cmp r0 11
jne denied
load8 r0 8300000000000000775
cmp r0 12
jne denied
load8 r0 8460000000000000006
cmp r0 1
jne denied
load8 r0 8460000000000000064
cmp r0 1
jne denied
set r8 0
label check
cmp r8 4
jge grant
set r7 8460000000000000060
add r7 r8
load8 r6 $r7
set r7 8300000000000000769
add r7 r8
load8 r5 $r7
cmp r6 r5
jne denied
set r7 8460000000000000070
add r7 r8
load8 r6 $r7
set r7 8300000000000000780
add r7 r8
load8 r5 $r7
cmp r6 r5
jne denied
add r8 1
jmp check
label grant
store8 8300000000000000768 2
store8 8300000000000000773 1
set r0 0
jmp emit
label denied
set r0 1
label emit
print r0
halt
