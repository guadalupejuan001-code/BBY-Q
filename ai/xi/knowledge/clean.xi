#!reverse-pc-machine-v1
# E013: clear bounded actual intake and the visited-node queue, preserving the
# same E012 clean-state invariant. Token slots are cleared even after bad input.
load8 r2 7400000000000000017
load8 r3 7400000000000000050
set r0 0
label visited
cmp r0 r3
jge raw_start
set r7 7400000000000003000
add r7 r0
load8 r1 $r7
cmp r1 1
jlt invalid
store8 $r7 0
set r7 7400000000000003400
add r7 r1
store8 $r7 0
set r7 7400000000000003800
add r7 r1
store8 $r7 0
set r7 7400000000000004200
add r7 r1
store8 $r7 0
add r0 1
jmp visited
label raw_start
set r0 0
label raw
cmp r0 r2
jge token_start
set r7 7400000000000000128
add r7 r0
store8 $r7 0
add r0 1
jmp raw
label token_start
set r0 0
label tokens
set r7 7400000000000000512
add r7 r0
store8 $r7 0
add r0 1
cmp r0 510
jlt tokens
set r0 0
label resolved
set r7 7400000000000001600
add r7 r0
store8 $r7 0
add r0 1
cmp r0 30
jlt resolved
set r0 16
label control
set r7 7400000000000000000
add r7 r0
store8 $r7 0
add r0 1
cmp r0 64
jlt control
halt
label invalid
div r0 0
