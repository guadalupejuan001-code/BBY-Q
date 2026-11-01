#!reverse-pc-machine-v1
# C14 separate supervised count model: 144 contexts * 4 routes, 16-bit counters, XI only.
load8 r0 8270000000000000000
cmp r0 0
jne c14_invalid
store8 8270000000000000000 14
store8 8270000000000000004 0
store8 8270000000000000005 0
store8 8270000000000000006 0
store8 8270000000000000007 0
set r1 0
label c14_clear
mov r2 r1
mul r2 1
add r2 8270000000000000100
store8 $r2 0
add r1 1
cmp r1 1152
jlt c14_clear
set r0 14
print r0
halt
label c14_invalid
div r0 0
