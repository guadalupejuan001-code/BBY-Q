#!reverse-pc-machine-v1
# Promotion requires unique native-induced roles and held-out sequences.
load8 r0 8000000000000000002
cmp r0 1
jne invalid
load8 r0 8000000000000000003
cmp r0 0
jne invalid
load8 r0 8000000000000000005
cmp r0 10
jne invalid
set r9 0
label cue_record
cmp r9 10
jge cues_ready
set r7 8000000000000001000
mov r0 r9
mul r0 40
add r7 r0
load8 r0 $r7
cmp r0 1
jlt invalid
cmp r0 3
jgt invalid
add r7 1
load8 r0 $r7
cmp r0 1
jlt invalid
cmp r0 32
jgt invalid
add r7 1
load8 r0 $r7
add r7 1
load8 r14 $r7
mul r14 256
add r0 r14
cmp r0 22
jle invalid
cmp r0 255
jgt extended_cue_kind
set r7 7400000000000006000
add r7 r0
jmp cue_kind
label extended_cue_kind
set r7 7800000000000020000
add r7 r0
label cue_kind
load8 r0 $r7
cmp r0 3
jne invalid
add r9 1
jmp cue_record
label cues_ready
load8 r10 8000000000000000004
cmp r10 128
jne invalid
set r9 0
label pattern
cmp r9 r10
jge publish
set r12 8000000000000010000
mov r0 r9
mul r0 96
add r12 r0
mov r7 r12
add r7 2
load8 r0 $r7
cmp r0 1
jne invalid
load8 r11 $r12
set r0 0
set r8 0
label role
cmp r0 r11
jge minima
mov r7 r12
add r7 16
mov r1 r0
mul r1 4
add r7 r1
load8 r1 $r7
cmp r1 16
je next_role
cmp r1 1
je add_role
cmp r1 2
je add_role
cmp r1 4
jne invalid
label add_role
mov r2 r8
div r2 r1
mod r2 2
cmp r2 0
jne invalid
add r8 r1
label next_role
add r0 1
jmp role
label minima
set r5 1
set r6 1
cmp r8 0
je get_training
mov r7 r12
add r7 3
load8 r0 $r7
cmp r0 2
jne invalid
set r5 64
set r6 16
cmp r8 1
je get_training
set r5 4
set r6 2
cmp r8 2
je get_training
set r5 128
set r6 64
cmp r8 7
jne get_training
set r5 1024
label get_training
mov r7 r12
add r7 80
set r8 0
label count
set r0 0
set r1 1
set r2 0
label read_count
mov r3 r7
add r3 r2
load8 r4 $r3
mul r4 r1
add r0 r4
mul r1 256
add r2 1
cmp r2 4
jlt read_count
cmp r8 1
je validate_count
cmp r0 r5
jlt invalid
set r8 1
add r7 4
jmp count
label validate_count
cmp r0 r6
jlt invalid
mov r7 r12
add r7 1
load8 r0 $r7
cmp r0 13
jne next_pattern
add r7 75
load8 r0 $r7
cmp r0 17
jlt invalid
cmp r0 24
jgt invalid
sub r0 1
mul r0 512
set r7 7800000000000500000
add r7 r0
load8 r0 $r7
cmp r0 0
je invalid
add r7 256
load8 r0 $r7
cmp r0 0
je invalid
label next_pattern
add r9 1
jmp pattern
label publish
store8 8000000000000000003 1
halt
label invalid
div r0 0
