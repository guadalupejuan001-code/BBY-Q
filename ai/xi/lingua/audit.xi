#!reverse-pc-machine-v1
# Read-only state and accounting audit, including ephemeral topic descriptors.
load8 r0 8000000000000000000
cmp r0 76
jne invalid
load8 r0 8000000000000000001
cmp r0 71
jne invalid
load8 r0 8000000000000000002
cmp r0 1
jne invalid
load8 r0 8000000000000000003
cmp r0 1
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
set r5 0
set r6 0
label pattern
cmp r9 r10
jge totals
set r12 8000000000000010000
mov r0 r9
mul r0 96
add r12 r0
load8 r11 $r12
cmp r11 1
jlt invalid
cmp r11 15
jgt invalid
mov r7 r12
add r7 1
load8 r0 $r7
cmp r0 1
jlt invalid
cmp r0 15
jgt invalid
add r7 1
load8 r0 $r7
cmp r0 1
jne invalid
set r0 0
label slots
cmp r0 r11
jge counts
mov r7 r12
add r7 16
mov r1 r0
mul r1 4
add r7 r1
load8 r1 $r7
cmp r1 1
je next_slot
cmp r1 2
je next_slot
cmp r1 4
je next_slot
cmp r1 16
jne invalid
label next_slot
add r0 1
jmp slots
label counts
mov r7 r12
add r7 80
set r8 0
label count
set r0 0
set r1 1
set r2 0
label count_byte
mov r3 r7
add r3 r2
load8 r4 $r3
mul r4 r1
add r0 r4
mul r1 256
add r2 1
cmp r2 4
jlt count_byte
cmp r0 0
je invalid
cmp r8 1
je validation
add r5 r0
add r7 4
set r8 1
jmp count
label validation
add r6 r0
add r9 1
jmp pattern
label totals
set r7 8000000000000000008
set r8 0
label total
set r0 0
set r1 1
set r2 0
label total_byte
mov r3 r7
add r3 r2
load8 r4 $r3
mul r4 r1
add r0 r4
mul r1 256
add r2 1
cmp r2 4
jlt total_byte
cmp r8 1
je validation_total
cmp r0 r5
jne invalid
add r7 4
set r8 1
jmp total
label validation_total
cmp r0 r6
jne invalid
set r0 16
label control
set r7 8000000000000000000
add r7 r0
load8 r1 $r7
cmp r1 0
jne invalid
add r0 1
cmp r0 64
jlt control
set r0 0
label topic
cmp r0 8
jge scratch_start
set r7 8000000000000000128
mov r1 r0
mul r1 16
add r7 r1
load8 r1 $r7
cmp r1 1
jgt invalid
cmp r1 0
je next_topic
add r7 1
load8 r1 $r7
cmp r1 1
jlt invalid
cmp r1 2
jgt invalid
label next_topic
add r0 1
jmp topic
label scratch_start
set r0 0
label scratch
set r7 8000000000000100000
add r7 r0
load8 r1 $r7
cmp r1 0
jne invalid
add r0 1
cmp r0 18432
jlt scratch
mem_stats
stats
halt
label invalid
div r0 0
