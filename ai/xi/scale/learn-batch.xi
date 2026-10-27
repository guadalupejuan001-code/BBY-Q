#!reverse-pc-machine-v1
# M+16: 0 training,1 independent validation; +17 opaque concept (1..8),
# +18..19 row count (1..1024). Rows at M+10000: X:u32,Y:u16,result:i32.
# The teacher supplies consequences. All candidate selection is native XI.
# Candidate primitives are designed; their assignment to concepts is learned.
load8 r0 7900000000000000002
cmp r0 1
jne invalid
load8 r0 7900000000000000003
cmp r0 0
jne invalid
load8 r0 7900000000000000016
cmp r0 1
jgt invalid
load8 r0 7900000000000000017
cmp r0 1
jlt invalid
cmp r0 8
jgt invalid
sub r0 1
mul r0 64
set r12 7900000000000000128
add r12 r0
load8 r9 $r12
mov r7 r12
add r7 1
load8 r10 $r7
add r7 2
load8 r11 $r7
load8 r0 7900000000000000016
cmp r0 0
je mode_ready
cmp r10 0
je invalid
label mode_ready
load8 r1 7900000000000000018
load8 r14 7900000000000000019
mul r14 256
add r1 r14
cmp r1 1
jlt invalid
cmp r1 1024
jgt invalid
set r0 0
set r13 7900000000000010000
label row
cmp r0 r1
jge finish
load8 r2 $r13
add r13 1
load8 r14 $r13
mul r14 256
add r2 r14
add r13 1
load8 r14 $r13
mul r14 65536
add r2 r14
add r13 1
load8 r14 $r13
mul r14 16777216
add r2 r14
add r13 1
load8 r3 $r13
add r13 1
load8 r14 $r13
mul r14 256
add r3 r14
add r13 1
load8 r4 $r13
add r13 1
load8 r14 $r13
mul r14 256
add r4 r14
add r13 1
load8 r14 $r13
mul r14 65536
add r4 r14
add r13 1
load8 r14 $r13
mul r14 16777216
add r4 r14
add r13 1
cmp r4 2147483647
jle signed_result
sub r4 4294967296
label signed_result
cmp r11 1
je witnessed
mov r7 r12
add r7 14
load8 r14 $r7
cmp r14 0
je first_witness
mov r7 r12
add r7 8
load8 r14 $r7
add r7 1
load8 r15 $r7
mul r15 256
add r14 r15
add r7 1
load8 r15 $r7
mul r15 65536
add r14 r15
add r7 1
load8 r15 $r7
mul r15 16777216
add r14 r15
cmp r14 r2
jne distinct
add r7 1
load8 r14 $r7
add r7 1
load8 r15 $r7
mul r15 256
add r14 r15
cmp r14 r3
je witnessed
label distinct
set r11 1
jmp witnessed
label first_witness
store8 $r7 1
mov r7 r12
add r7 8
mov r14 r2
set r15 0
label copy_x
mov r5 r14
mod r5 256
store8 $r7 r5
div r14 256
add r7 1
add r15 1
cmp r15 4
jlt copy_x
mov r14 r3
mod r14 256
store8 $r7 r14
add r7 1
mov r14 r3
div r14 256
store8 $r7 r14
label witnessed
cmp r10 0
je ambiguous_candidates
mov r6 r10
jmp calculate
label ambiguous_candidates
set r6 1
set r8 0
label candidate
cmp r6 256
jge candidates_ready
mov r14 r9
div r14 r6
mod r14 2
cmp r14 0
je next_candidate
label calculate
mov r5 r2
cmp r6 1
je subtract
cmp r6 2
je add
cmp r6 4
je multiply
cmp r6 8
je exact_divide
cmp r6 16
je remainder
cmp r6 32
je minimum
cmp r6 64
je maximum
cmp r6 128
jne invalid
sub r5 r3
cmp r5 0
jge consequence
mul r5 -1
jmp consequence
label subtract
sub r5 r3
jmp consequence
label add
add r5 r3
jmp consequence
label multiply
mul r5 r3
jmp consequence
label exact_divide
cmp r3 0
je undefined
mov r14 r2
mod r14 r3
cmp r14 0
jne undefined
div r5 r3
jmp consequence
label remainder
cmp r3 0
je undefined
mod r5 r3
jmp consequence
label minimum
cmp r2 r3
jle consequence
mov r5 r3
jmp consequence
label maximum
cmp r2 r3
jge consequence
mov r5 r3
jmp consequence
label undefined
set r5 -4294967296
label consequence
cmp r10 0
jne unique_consequence
cmp r5 r4
jne next_candidate
add r8 r6
label next_candidate
mul r6 2
jmp candidate
label candidates_ready
cmp r8 0
je invalid
mov r9 r8
set r6 1
label find_unique
cmp r6 r9
je set_unique
mul r6 2
cmp r6 256
jlt find_unique
jmp next_row
label set_unique
mov r10 r6
jmp next_row
label unique_consequence
cmp r5 r4
jne invalid
label next_row
add r0 1
jmp row
label finish
mov r7 r12
load8 r0 7900000000000000016
cmp r0 1
je validation_count
store8 $r7 r9
add r7 1
store8 $r7 r10
add r7 2
store8 $r7 r11
add r7 1
jmp increment_count
label validation_count
add r7 16
label increment_count
load8 r2 $r7
mov r8 r7
add r8 1
load8 r14 $r8
mul r14 256
add r2 r14
add r8 1
load8 r14 $r8
mul r14 65536
add r2 r14
add r8 1
load8 r14 $r8
mul r14 16777216
add r2 r14
add r2 r1
cmp r2 4294967295
jgt invalid
set r0 0
label write_count
mov r14 r2
mod r14 256
store8 $r7 r14
div r2 256
add r7 1
add r0 1
cmp r0 4
jlt write_count
# Independently increment the global durable training/validation count.
set r7 7900000000000000008
load8 r0 7900000000000000016
cmp r0 0
je global_count
add r7 4
label global_count
load8 r2 $r7
mov r8 r7
add r8 1
load8 r14 $r8
mul r14 256
add r2 r14
add r8 1
load8 r14 $r8
mul r14 65536
add r2 r14
add r8 1
load8 r14 $r8
mul r14 16777216
add r2 r14
add r2 r1
cmp r2 4294967295
jgt invalid
set r0 0
label write_global
mov r14 r2
mod r14 256
store8 $r7 r14
div r2 256
add r7 1
add r0 1
cmp r0 4
jlt write_global
set r0 0
mul r1 10
label erase_rows
cmp r0 r1
jge erase_header
set r7 7900000000000010000
add r7 r0
store8 $r7 0
add r0 1
jmp erase_rows
label erase_header
set r0 16
label header
set r7 7900000000000000000
add r7 r0
store8 $r7 0
add r0 1
cmp r0 32
jlt header
halt
label invalid
div r0 0
