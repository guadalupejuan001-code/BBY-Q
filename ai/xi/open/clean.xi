#!reverse-pc-machine-v1
load8 r0 7800000000000000002
cmp r0 0
je done
cmp r0 1
jne invalid
# Clear keyed visitation only for nodes actually queued, then their records.
load8 r10 7800000000000000120
set r0 0
label queue
cmp r0 r10
jge proof_start
set r7 7800000000008000000
mov r1 r0
mul r1 8
add r7 r1
mov r15 r7
load8 r2 $r15
add r15 1
load8 r14 $r15
mul r14 256
add r2 r14
set r8 7800000000008100000
add r8 r2
store8 $r8 0
set r1 0
label queue_bytes
cmp r1 8
jge next_node
mov r8 r7
add r8 r1
store8 $r8 0
add r1 1
jmp queue_bytes
label next_node
add r0 1
jmp queue
label proof_start
load8 r10 7800000000000000121
mul r10 4
set r0 0
label proof
cmp r0 r10
jge result_start
set r7 7800000000008200000
add r7 r0
store8 $r7 0
add r0 1
jmp proof
label result_start
load8 r10 7800000000000000082
mul r10 2
set r0 0
label results
cmp r0 r10
jge control_start
set r7 7800000000008300000
add r7 r0
store8 $r7 0
add r0 1
jmp results
label control_start
set r0 63
label control
set r7 7800000000000000000
add r7 r0
store8 $r7 0
add r0 1
cmp r0 512
jlt control
set r0 1024
label tokens
set r7 7800000000000000000
add r7 r0
store8 $r7 0
add r0 1
cmp r0 1084
jlt tokens
set r0 2048
label descriptors
set r7 7800000000000000000
add r7 r0
store8 $r7 0
add r0 1
cmp r0 2108
jlt descriptors
label done
halt
label invalid
div r0 0
