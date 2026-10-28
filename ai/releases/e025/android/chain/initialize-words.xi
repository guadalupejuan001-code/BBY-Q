#!reverse-pc-machine-v1
label words_start
load8 r2 7800000000000000006
load8 r3 7800000000000000007
mul r3 256
add r2 r3
mul r2 40
set r0 0
label words
cmp r0 r2
jge done
set r7 7800000000000100000
add r7 r0
load8 r1 $r7
set r7 8600000000000400000
add r7 r0
store8 $r7 r1
add r0 1
jmp words
label done
halt
label invalid
div r0 0
