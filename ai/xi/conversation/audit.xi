#!reverse-pc-machine-v1
# Read-only structural checks. Examiners independently compare every learned
# byte and the unchanged parent authority; this is not a semantic oracle.
load8 r0 7700000000000000000
cmp r0 67
jne invalid
load8 r0 7700000000000000001
cmp r0 86
jne invalid
load8 r0 7700000000000000002
cmp r0 1
jne invalid
set r0 16
label scratch
set r7 7700000000000000000
add r7 r0
load8 r1 $r7
cmp r1 0
jne invalid
add r0 1
cmp r0 256
jlt scratch
set r0 1
label functions
set r7 7700000000000000512
add r7 r0
load8 r1 $r7
cmp r1 0
je invalid
set r7 7400000000000006000
add r7 r1
load8 r1 $r7
cmp r1 0
je invalid
add r0 1
cmp r0 26
jle functions
set r0 0
label order
set r7 7700000000000001000
mov r1 r0
mul r1 32
add r7 r1
load8 r1 $r7
cmp r1 4
jne invalid
add r7 1
load8 r1 $r7
cmp r1 2
jne invalid
add r7 1
load8 r2 $r7
add r7 1
load8 r3 $r7
add r7 1
load8 r4 $r7
add r7 1
load8 r5 $r7
cmp r2 r5
je invalid
add r7 1
load8 r5 $r7
cmp r3 r5
je invalid
add r7 1
load8 r5 $r7
cmp r4 r5
je invalid
add r7 1
set r1 0
set r8 0
label slots
cmp r1 4
jge order_done
mov r9 r7
add r9 r1
load8 r2 $r9
cmp r2 1
jlt invalid
cmp r2 4
jgt invalid
set r3 1
label power
cmp r2 1
jle bit_ready
mul r3 2
sub r2 1
jmp power
label bit_ready
mov r2 r8
div r2 r3
mod r2 2
cmp r2 0
jne invalid
add r8 r3
add r1 1
jmp slots
label order_done
cmp r8 15
jne invalid
add r0 1
cmp r0 2
jlt order
set r0 0
label utterances
set r7 7700000000000002000
mov r1 r0
mul r1 256
add r7 r1
load8 r1 $r7
cmp r1 1
jlt invalid
add r0 1
cmp r0 16
jlt utterances
set r0 0
label roles
set r7 7700000000000010000
mov r1 r0
mul r1 4
add r7 r1
load8 r2 $r7
cmp r2 3
jgt invalid
add r7 1
load8 r3 $r7
cmp r2 1
je person
cmp r3 0
jne invalid
jmp next_role
label person
cmp r3 1
jlt invalid
cmp r3 2
jgt invalid
label next_role
add r0 1
cmp r0 256
jlt roles
load8 r0 7700000000000000010
cmp r0 2
jgt invalid
mem_stats
stats
halt
label invalid
div r0 0
