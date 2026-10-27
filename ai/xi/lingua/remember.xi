#!reverse-pc-machine-v1
# Eight most recent supported factual topics. These are references, not cached
# answers: resuming always performs a fresh evidence search in the same state.
load8 r0 8000000000000000003
cmp r0 1
jne done
load8 r0 7800000000000000012
cmp r0 1
jne clean
load8 r8 7800000000000000014
load8 r14 7800000000000000015
mul r14 256
add r8 r14
set r10 0
label find
cmp r10 8
jge evict
set r7 8000000000000000128
mov r0 r10
mul r0 16
add r7 r0
load8 r0 $r7
cmp r0 1
jne shift_start
add r7 2
load8 r0 $r7
add r7 1
load8 r14 $r7
mul r14 256
add r0 r14
cmp r0 r8
je shift_start
add r10 1
jmp find
label evict
set r10 7
label shift_start
cmp r10 0
je insert
set r0 0
label shift_byte
set r7 8000000000000000128
mov r1 r10
sub r1 1
mul r1 16
add r7 r1
add r7 r0
load8 r2 $r7
add r7 16
store8 $r7 r2
add r0 1
cmp r0 16
jlt shift_byte
sub r10 1
jmp shift_start
label insert
set r0 0
label insert_byte
set r7 7800000000000000012
add r7 r0
load8 r2 $r7
set r7 8000000000000000128
add r7 r0
store8 $r7 r2
add r0 1
cmp r0 8
jlt insert_byte
label clean
set r0 16
label clean_byte
set r7 8000000000000000000
add r7 r0
store8 $r7 0
add r0 1
cmp r0 64
jlt clean_byte
label done
halt
