#!reverse-pc-machine-v1
# Idempotent append-only layout migration from E024. Copy live account/topic
# records and taught social fragments; never replace their original banks.
load8 r0 8600000000000000000
cmp r0 25
je done
cmp r0 0
jne invalid
load8 r0 8500000000000000002
cmp r0 1
jne invalid
store8 8600000000000000000 25
store8 8600000000000000001 1
set r0 0
label accounts
set r7 7500000000000001000
add r7 r0
load8 r1 $r7
set r7 8600000000000010000
add r7 r0
store8 $r7 r1
add r0 1
cmp r0 128
jlt accounts
set r0 0
label topics
set r7 8000000000000000128
add r7 r0
load8 r1 $r7
set r7 8600000000000030000
add r7 r0
store8 $r7 r1
add r0 1
cmp r0 128
jlt topics
load8 r2 8500000000000000003
mul r2 516
set r0 0
label fragments
cmp r0 r2
jge words_start
set r7 8500000000000010000
add r7 r0
load8 r1 $r7
set r7 8600000000000100000
add r7 r0
store8 $r7 r1
add r0 1
jmp fragments
label words_start
halt
label done
halt
label invalid
div r0 0
