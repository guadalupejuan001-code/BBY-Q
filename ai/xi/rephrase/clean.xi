#!reverse-pc-machine-v1
load8 r0 8100000000000000002
cmp r0 1
jne done
set r0 16
label control
set r7 8100000000000000000
add r7 r0
store8 $r7 0
add r0 1
cmp r0 128
jlt control
set r0 512
label target
set r7 8100000000000000000
add r7 r0
store8 $r7 0
add r0 1
cmp r0 768
jlt target
set r0 1000
label original
set r7 8100000000000000000
add r7 r0
store8 $r7 0
add r0 1
cmp r0 1602
jlt original
set r0 2000
label output
set r7 8100000000000000000
add r7 r0
store8 $r7 0
add r0 1
cmp r0 2600
jlt output
label done
halt
