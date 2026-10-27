#!reverse-pc-machine-v1
load8 r0 8100000000000000016
cmp r0 1
jlt invalid
cmp r0 64
jgt invalid
sub r0 1
mov r1 r0
mul r1 8
set r12 8100000000000030000
add r12 r1
load8 r1 $r12
cmp r1 0
je new_meta
load8 r2 8100000000000000017
cmp r1 r2
jne invalid
mov r7 r12
add r7 1
load8 r1 $r7
load8 r2 8100000000000000018
cmp r1 r2
jne invalid
jmp count
label new_meta
load8 r1 8100000000000000017
cmp r1 1
jlt invalid
cmp r1 4
jgt invalid
store8 $r12 r1
mov r7 r12
add r7 1
load8 r1 8100000000000000018
cmp r1 2
jgt invalid
store8 $r7 r1
mul r0 512
set r10 8100000000000040000
add r10 r0
set r0 0
label canonical_raw
cmp r0 510
jge count
set r7 7400000000000000512
add r7 r0
load8 r1 $r7
mov r7 r10
add r7 r0
store8 $r7 r1
add r0 1
jmp canonical_raw
label count
mov r7 r12
add r7 2
load8 r0 $r7
add r7 1
load8 r14 $r7
mul r14 256
add r0 r14
cmp r0 65535
jge invalid
add r0 1
mov r1 r0
mod r1 256
sub r7 1
store8 $r7 r1
add r7 1
div r0 256
store8 $r7 r0
# Count the pair as one presentation, not two separate utterances.
set r7 8100000000000000008
set r0 1
set r1 0
label total_count
cmp r1 4
jge done
load8 r2 $r7
add r2 r0
mov r0 r2
div r0 256
mod r2 256
store8 $r7 r2
add r7 1
add r1 1
jmp total_count
label done
halt
label invalid
div r0 0
