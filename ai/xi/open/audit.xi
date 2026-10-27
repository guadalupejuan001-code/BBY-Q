#!reverse-pc-machine-v1
# Read-only structural audit. The external examiner independently checks old
# learned bytes, uniqueness, exact evidence and all query answers.
load8 r0 7800000000000000000
cmp r0 79
jne invalid
load8 r0 7800000000000000001
cmp r0 80
jne invalid
load8 r0 7800000000000000002
cmp r0 1
jne invalid
load8 r0 7800000000000000003
cmp r0 1
jgt invalid
cmp r0 0
je style_ready
load8 r0 7800000000000507168
cmp r0 0
je invalid
load8 r0 7800000000000507424
cmp r0 0
je invalid
label style_ready
load8 r13 7800000000000000004
load8 r14 7800000000000000005
mul r14 256
add r13 r14
cmp r13 256
jlt invalid
load8 r12 7800000000000000006
load8 r14 7800000000000000007
mul r14 256
add r12 r14
cmp r12 2048
jgt invalid
load8 r11 7800000000000000008
load8 r14 7800000000000000009
mul r14 256
add r11 r14
cmp r11 1024
jgt invalid
load8 r0 7800000000000000040
cmp r0 1
jgt invalid
set r0 0
label lexeme
cmp r0 r12
jge facts
set r7 7800000000000100000
mov r1 r0
mul r1 40
add r7 r1
mov r15 r7
load8 r2 $r15
add r15 1
load8 r14 $r15
mul r14 256
add r2 r14
cmp r2 1
jlt invalid
add r7 2
load8 r3 $r7
cmp r3 1
jlt invalid
cmp r3 3
jgt invalid
add r7 1
load8 r4 $r7
cmp r4 1
jlt invalid
cmp r4 2
jgt invalid
add r7 1
load8 r4 $r7
cmp r4 1
jlt invalid
cmp r4 32
jgt invalid
cmp r2 255
jle old_kind
cmp r2 r13
jge invalid
set r7 7800000000000020000
add r7 r2
load8 r4 $r7
jmp kind
label old_kind
cmp r2 22
jle old_entity
set r7 7400000000000006000
add r7 r2
load8 r4 $r7
jmp kind
label old_entity
set r4 1
label kind
cmp r4 r3
jne invalid
add r0 1
jmp lexeme
label facts
set r0 0
label fact
cmp r0 r11
jge models
set r7 7800000000000200000
mov r1 r0
mul r1 6
add r7 r1
mov r15 r7
load8 r2 $r15
add r15 1
load8 r14 $r15
mul r14 256
add r2 r14
add r7 2
mov r15 r7
load8 r3 $r15
add r15 1
load8 r14 $r15
mul r14 256
add r3 r14
add r7 2
mov r15 r7
load8 r4 $r15
add r15 1
load8 r14 $r15
mul r14 256
add r4 r14
cmp r2 0
je invalid
cmp r3 0
je invalid
cmp r4 0
je invalid
mov r7 r2
mul r7 65536
add r7 r3
mul r7 65536
add r7 r4
mul r7 4
add r7 7800000010000000000
load8 r5 $r7
cmp r5 1
jgt invalid
add r7 1
load8 r6 $r7
cmp r6 1
jgt invalid
add r7 1
load8 r7 $r7
cmp r7 1
jne invalid
cmp r2 255
jgt next_fact
add r5 r6
cmp r5 0
je next_fact
load8 r5 7800000000000000040
cmp r5 1
jne invalid
label next_fact
add r0 1
jmp fact
label models
set r0 256
label model
cmp r0 r13
jge patterns
set r7 7800000000002000000
mov r1 r0
mul r1 64
add r7 r1
load8 r1 $r7
cmp r1 6
jgt invalid
add r7 1
load8 r1 $r7
cmp r1 3
jgt invalid
add r0 1
jmp model
label patterns
load8 r10 7800000000000000010
cmp r10 64
jgt invalid
set r0 0
label pattern
cmp r0 r10
jge scratch_start
set r7 7800000000000010000
mov r1 r0
mul r1 96
add r7 r1
load8 r9 $r7
cmp r9 1
jlt invalid
cmp r9 15
jgt invalid
add r7 1
load8 r1 $r7
cmp r1 1
jlt invalid
cmp r1 8
jgt invalid
add r7 1
load8 r8 $r7
cmp r8 1
jgt invalid
add r7 1
load8 r1 $r7
cmp r1 1
jlt invalid
cmp r1 2
jgt invalid
add r7 13
set r1 0
label slot
cmp r1 r9
jge next_pattern
mov r2 r7
mov r3 r1
mul r3 4
add r2 r3
load8 r3 $r2
cmp r3 1
jlt invalid
cmp r8 0
je candidate_mask
cmp r3 1
je next_slot
cmp r3 2
je next_slot
cmp r3 4
je next_slot
cmp r3 8
je next_slot
cmp r3 16
jne invalid
jmp next_slot
label candidate_mask
cmp r3 31
jgt invalid
label next_slot
add r1 1
jmp slot
label next_pattern
add r0 1
jmp pattern
label scratch_start
set r0 63
label scratch
set r7 7800000000000000000
add r7 r0
load8 r1 $r7
cmp r1 0
jne invalid
add r0 1
cmp r0 512
jlt scratch
set r0 1024
label tokens
set r7 7800000000000000000
add r7 r0
load8 r1 $r7
cmp r1 0
jne invalid
add r0 1
cmp r0 1084
jlt tokens
set r0 2048
label descriptors
set r7 7800000000000000000
add r7 r0
load8 r1 $r7
cmp r1 0
jne invalid
add r0 1
cmp r0 2108
jlt descriptors
set r0 0
label visited
cmp r0 r13
jge queue_start
set r7 7800000000008100000
add r7 r0
load8 r1 $r7
cmp r1 0
jne invalid
add r0 1
jmp visited
label queue_start
set r0 0
label queue
cmp r0 512
jge proof_start
set r7 7800000000008000000
add r7 r0
load8 r1 $r7
cmp r1 0
jne invalid
add r0 1
jmp queue
label proof_start
set r0 0
label proof
cmp r0 128
jge result_start
set r7 7800000000008200000
add r7 r0
load8 r1 $r7
cmp r1 0
jne invalid
add r0 1
jmp proof
label result_start
set r0 0
label result
cmp r0 16
jge done
set r7 7800000000008300000
add r7 r0
load8 r1 $r7
cmp r1 0
jne invalid
add r0 1
jmp result
label done
mem_stats
stats
halt
label invalid
div r0 0
