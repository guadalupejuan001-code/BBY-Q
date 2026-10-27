#!reverse-pc-machine-v1
load8 r0 8100000000000000002
cmp r0 1
jne invalid
load8 r0 8100000000000000003
cmp r0 0
jne invalid
store8 8100000000000000019 1
set r0 0
label clear_raw
set r7 7400000000000000128
add r7 r0
store8 $r7 0
add r0 1
cmp r0 255
jlt clear_raw
set r0 0
label copy_target
load8 r1 8100000000000000020
cmp r0 r1
jge clear_tokens
set r7 8100000000000000512
add r7 r0
load8 r2 $r7
set r7 7400000000000000128
add r7 r0
store8 $r7 r2
add r0 1
jmp copy_target
label clear_tokens
set r0 0
label token_byte
set r7 7400000000000000512
add r7 r0
store8 $r7 0
add r0 1
cmp r0 510
jlt token_byte
set r0 0
label resolved_byte
set r7 7400000000000001600
add r7 r0
store8 $r7 0
add r0 1
cmp r0 30
jlt resolved_byte
set r0 0
label open_byte
set r7 7800000000000001024
add r7 r0
store8 $r7 0
set r7 7800000000000002048
add r7 r0
store8 $r7 0
add r0 1
cmp r0 60
jlt open_byte
store8 7400000000000000016 1
load8 r0 8100000000000000020
store8 7400000000000000017 r0
store8 7400000000000000032 0
store8 7400000000000000040 0
store8 7400000000000000047 0
halt
label invalid
div r0 0
