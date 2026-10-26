#!reverse-pc-machine-v1
# Read-only integrity check of grammar schema, distinct witnesses and slots.
load8 r0 7600000000000000000
cmp r0 71
jne invalid
load8 r0 7600000000000000001
cmp r0 82
jne invalid
load8 r0 7600000000000000002
cmp r0 1
jne invalid
load8 r15 7600000000000000003
cmp r15 16
jgt invalid
set r0 4
label scratch
set r7 7600000000000000000
add r7 r0
load8 r1 $r7
cmp r1 0
jne invalid
add r0 1
cmp r0 192
jlt scratch
set r0 0
label record
cmp r0 r15
jge done
set r1 7600000000000001000
mov r2 r0
mul r2 64
add r1 r2
load8 r12 $r1
cmp r12 4
jlt invalid
cmp r12 15
jgt invalid
mov r7 r1
add r7 1
load8 r13 $r7
cmp r13 1
jgt invalid
add r7 1
load8 r9 $r7
add r7 1
load8 r10 $r7
cmp r9 0
je invalid
cmp r10 0
je invalid
cmp r9 r10
je invalid
cmp r13 0
je slots
mov r7 r1
add r7 5
load8 r2 $r7
cmp r2 0
je invalid
cmp r2 r9
je invalid
add r7 1
load8 r3 $r7
cmp r3 0
je invalid
cmp r3 r10
je invalid
cmp r2 r3
je invalid
label slots
set r2 0
set r9 0
set r10 0
set r11 0
label slot
cmp r2 r12
jge roles
mov r7 r1
add r7 8
mov r3 r2
mul r3 3
add r7 r3
load8 r3 $r7
cmp r3 0
je literal
cmp r3 3
jgt invalid
cmp r3 1
jne not_actor
add r9 1
jmp variable
label not_actor
cmp r3 2
jne not_item
add r10 1
jmp variable
label not_item
add r11 1
label variable
add r7 1
load8 r4 $r7
cmp r4 0
jne invalid
add r7 1
load8 r4 $r7
cmp r4 0
jne invalid
jmp next_slot
label literal
add r7 1
load8 r4 $r7
cmp r4 0
je invalid
set r8 7400000000000006000
add r8 r4
load8 r4 $r8
cmp r4 3
jne invalid
add r7 1
load8 r4 $r7
cmp r4 3
jne invalid
label next_slot
add r2 1
jmp slot
label roles
cmp r9 1
jne invalid
cmp r10 1
jne invalid
cmp r11 1
jne invalid
add r0 1
jmp record
label done
mem_stats
stats
halt
label invalid
div r0 0
