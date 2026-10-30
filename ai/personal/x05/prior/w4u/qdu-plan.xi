#!reverse-pc-machine-v1
# w4U extension for ONE bounded QdU code task; no new coordinator or model.
# Runs on a disposable COPY of the BBY Q/w4U RVPC2, using w4U M slots +768..785.
load8 r0 8300000000000000000
cmp r0 77
jne rejected
load8 r0 8300000000000000001
cmp r0 1
jne rejected
load8 r0 8460000000000000006
cmp r0 1
jne rejected
load8 r0 8460000000000000064
cmp r0 1
jne rejected
load8 r0 8460000000000000065
cmp r0 1
jne rejected
load8 r0 8300000000000000768
cmp r0 0
jne rejected
set r8 0
set r9 0
label nonce_loop
cmp r8 4
jge nonce_ok
set r7 8460000000000000060
add r7 r8
load8 r6 $r7
add r9 r6
add r8 1
jmp nonce_loop
label nonce_ok
cmp r9 0
je rejected
set r8 0
label copy_nonce
cmp r8 4
jge copy_digest
set r7 8460000000000000060
add r7 r8
load8 r6 $r7
set r7 8300000000000000769
add r7 r8
store8 $r7 r6
add r8 1
jmp copy_nonce
label copy_digest
set r8 0
label digest_loop
cmp r8 4
jge approved
set r7 8460000000000000070
add r7 r8
load8 r6 $r7
set r7 8300000000000000780
add r7 r8
store8 $r7 r6
add r8 1
jmp digest_loop
label approved
store8 8300000000000000768 1
store8 8300000000000000773 0
store8 8300000000000000774 11
store8 8300000000000000775 12
set r0 0
jmp emit
label rejected
set r0 1
label emit
print r0
halt
