#!reverse-pc-machine-v1
# Reconstruct actual edge labels. Reverse proof records contain node u16 and
# the predicate of its incoming edge. No invented free-form explanation.
load8 r0 7800000000000000235
cmp r0 1
jne walk
load8 r2 7800000000000000076
load8 r14 7800000000000000077
mul r14 256
add r2 r14
load8 r0 7800000000000000090
cmp r0 1
jne proof_target_ready
load8 r2 7800000000000000132
load8 r14 7800000000000000133
mul r14 256
add r2 r14
label proof_target_ready
mov r14 r2
mod r14 256
store8 7800000000008200000 r14
mov r14 r2
div r14 256
store8 7800000000008200001 r14
load8 r2 7800000000000000074
load8 r14 7800000000000000075
mul r14 256
add r2 r14
mov r14 r2
mod r14 256
store8 7800000000008200002 r14
mov r14 r2
div r14 256
store8 7800000000008200003 r14
store8 7800000000000000121 1
label walk
load8 r0 7800000000000000124
set r7 7800000000008000000
mul r0 8
add r7 r0
mov r15 r7
load8 r2 $r15
add r15 1
load8 r14 $r15
mul r14 256
add r2 r14
add r7 2
load8 r3 $r7
add r7 2
mov r15 r7
load8 r4 $r15
add r15 1
load8 r14 $r15
mul r14 256
add r4 r14
add r7 2
load8 r5 $r7
cmp r5 2
jlt source_ready
store8 7800000000000000089 1
label source_ready
load8 r6 7800000000000000121
cmp r6 32
jge limit
set r7 7800000000008200000
mov r0 r6
mul r0 4
add r7 r0
mov r15 r7
mov r14 r2
mod r14 256
store8 $r15 r14
add r15 1
mov r14 r2
div r14 256
store8 $r15 r14
add r7 2
mov r15 r7
mov r14 r4
mod r14 256
store8 $r15 r14
add r15 1
mov r14 r4
div r14 256
store8 $r15 r14
add r6 1
store8 7800000000000000121 r6
cmp r3 255
je found
store8 7800000000000000124 r3
jmp walk
label found
store8 7800000000000000080 1
load8 r0 7800000000000000076
load8 r14 7800000000000000077
mul r14 256
add r0 r14
load8 r1 7800000000000000090
cmp r1 1
jne found_target_ready
load8 r0 7800000000000000132
load8 r14 7800000000000000133
mul r14 256
add r0 r14
label found_target_ready
mov r14 r0
mod r14 256
store8 7800000000008300000 r14
mov r14 r0
div r14 256
store8 7800000000008300001 r14
store8 7800000000000000082 1
halt
label limit
store8 7800000000000000080 9
halt
