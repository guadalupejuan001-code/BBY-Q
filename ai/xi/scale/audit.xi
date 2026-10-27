#!reverse-pc-machine-v1
# Read-only E020 integrity, counter sums and complete transient erasure.
load8 r0 7900000000000000000
cmp r0 77
jne invalid
load8 r0 7900000000000000001
cmp r0 83
jne invalid
load8 r0 7900000000000000002
cmp r0 1
jne invalid
load8 r15 7900000000000000003
cmp r15 1
jgt invalid
set r0 0
set r12 0
set r13 0
label model
set r7 7900000000000000128
mov r1 r0
mul r1 64
add r7 r1
load8 r2 $r7
cmp r2 0
je invalid
mov r8 r7
add r8 1
load8 r3 $r8
cmp r3 0
je not_unique
cmp r2 r3
jne invalid
label not_unique
add r8 1
load8 r4 $r8
cmp r15 0
je unsealed
cmp r4 1
jlt invalid
cmp r4 8
jgt invalid
set r5 1
set r6 1
label code_bit
cmp r6 r4
jge code_ready
mul r5 2
add r6 1
jmp code_bit
label code_ready
cmp r5 r2
jne invalid
jmp validity_ready
label unsealed
cmp r4 0
jne invalid
label validity_ready
add r8 1
load8 r4 $r8
cmp r4 1
jgt invalid
cmp r15 0
je count
cmp r4 1
jne invalid
label count
add r8 1
set r4 0
set r5 1
set r6 0
label sum_train
load8 r9 $r8
mul r9 r5
add r4 r9
add r8 1
mul r5 256
add r6 1
cmp r6 4
jlt sum_train
add r12 r4
add r8 8
set r4 0
set r5 1
set r6 0
label sum_validation
load8 r9 $r8
mul r9 r5
add r4 r9
add r8 1
mul r5 256
add r6 1
cmp r6 4
jlt sum_validation
add r13 r4
add r0 1
cmp r0 8
jlt model
set r7 7900000000000000008
set r0 0
label global
set r4 0
set r5 1
set r6 0
label sum_global
load8 r9 $r7
mul r9 r5
add r4 r9
add r7 1
mul r5 256
add r6 1
cmp r6 4
jlt sum_global
cmp r0 1
je check_validation
cmp r4 r12
jne invalid
add r0 1
jmp global
label check_validation
cmp r4 r13
jne invalid
load8 r12 7900000000000000004
cmp r12 32
jgt invalid
set r0 0
label word
cmp r0 r12
jge transient
set r7 7900000000000001000
mov r1 r0
mul r1 32
add r7 r1
load8 r1 $r7
cmp r1 1
jlt invalid
cmp r1 16
jgt invalid
add r7 17
load8 r1 $r7
cmp r1 1
jlt invalid
cmp r1 8
jgt invalid
add r7 1
load8 r1 $r7
cmp r1 1
jlt invalid
cmp r1 2
jgt invalid
add r0 1
jmp word
label transient
set r0 16
label header
set r7 7900000000000000000
add r7 r0
load8 r1 $r7
cmp r1 0
jne invalid
add r0 1
cmp r0 32
jlt header
set r0 10000
label rows
set r7 7900000000000000000
add r7 r0
load8 r1 $r7
cmp r1 0
jne invalid
add r0 1
cmp r0 20240
jlt rows
mem_stats
stats
halt
label invalid
div r0 0
