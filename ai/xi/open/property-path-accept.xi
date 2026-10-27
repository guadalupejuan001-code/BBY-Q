#!reverse-pc-machine-v1
# +137: 0 continue path,1 accept,2 explicit exception,3 conflict.
load8 r0 7800000000000000208
cmp r0 2
je negative
cmp r0 3
je conflict
load8 r0 7800000000000000127
set r7 7800000000008000002
mul r0 8
add r7 r0
load8 r0 $r7
cmp r0 255
je accept
store8 7800000000000000127 r0
store8 7800000000000000137 0
halt
label accept
store8 7800000000000000137 1
halt
label negative
store8 7800000000000000137 2
halt
label conflict
store8 7800000000000000080 4
store8 7800000000000000137 3
halt
