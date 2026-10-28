#!reverse-pc-machine-v1
label m0_entry
# Publish only complete bilingual response coverage and at least one fragment.
load8 r0 8500000000000000000
cmp r0 85
jne m0_invalid
load8 r0 8500000000000000003
cmp r0 1
jlt m0_invalid
set r0 0
label m0_reply
cmp r0 20
jge m0_publish
cmp r0 2
je m0_next
cmp r0 3
je m0_next
set r7 8500000000000100000
mov r1 r0
mul r1 256
add r7 r1
load8 r1 $r7
cmp r1 1
jlt m0_invalid
label m0_next
add r0 1
jmp m0_reply
label m0_publish
store8 8500000000000000002 1
jmp m1_entry
label m0_invalid
div r0 0
label m1_entry
# Keep only the sealed teaching table. Queries leave no private scratch bytes.
set r0 16
label m1_controls
set r7 8500000000000000000
add r7 r0
store8 $r7 0
add r0 1
cmp r0 128
jlt m1_controls
set r0 512
label m1_tokens
set r7 8500000000000000000
add r7 r0
store8 $r7 0
add r0 1
cmp r0 1024
jlt m1_tokens
jmp m2_entry
label m2_entry
# E013: clear bounded actual intake and the visited-node queue, preserving the
# same E012 clean-state invariant. Token slots are cleared even after bad input.
load8 r2 7400000000000000017
load8 r3 7400000000000000050
set r0 0
label m2_visited
cmp r0 r3
jge m2_raw_start
set r7 7400000000000003000
add r7 r0
load8 r1 $r7
cmp r1 1
jlt m2_invalid
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
jmp m2_visited
label m2_raw_start
set r0 0
label m2_raw
cmp r0 r2
jge m2_token_start
set r7 7400000000000000128
add r7 r0
store8 $r7 0
add r0 1
jmp m2_raw
label m2_token_start
set r0 0
label m2_tokens
set r7 7400000000000000512
add r7 r0
store8 $r7 0
add r0 1
cmp r0 510
jlt m2_tokens
set r0 0
label m2_resolved
set r7 7400000000000001600
add r7 r0
store8 $r7 0
add r0 1
cmp r0 30
jlt m2_resolved
set r0 16
label m2_control
set r7 7400000000000000000
add r7 r0
store8 $r7 0
add r0 1
cmp r0 64
jlt m2_control
jmp finish
label m2_invalid
div r0 0
label finish
halt
