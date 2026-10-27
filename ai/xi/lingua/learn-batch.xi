#!reverse-pc-machine-v1
# Supervised reinforcement of native-induced constructions. Full concept-token
# sequences plus S/P/O labels enter each row. No slot positions are supplied.
# L+16 mode 0 training / 1 held-out validation; +17 construction; +18..19
# count <=512. Rows at L+100000: S,P,O:u16 followed by length token IDs:u16.
# Every observed token is checked in XI against the inferred role/literal mask.
load8 r0 8000000000000000002
cmp r0 1
jne invalid
load8 r0 8000000000000000003
cmp r0 0
jne invalid
load8 r0 8000000000000000016
cmp r0 1
jgt invalid
load8 r0 8000000000000000017
cmp r0 1
jlt invalid
load8 r1 8000000000000000004
cmp r0 r1
jgt invalid
sub r0 1
mul r0 96
set r12 8000000000000010000
add r12 r0
load8 r11 $r12
cmp r11 1
jlt invalid
cmp r11 15
jgt invalid
mov r7 r12
add r7 2
load8 r0 $r7
cmp r0 1
jne invalid
load8 r10 8000000000000000018
load8 r14 8000000000000000019
mul r14 256
add r10 r14
cmp r10 1
jlt invalid
cmp r10 512
jgt invalid
set r13 8000000000000100000
set r9 0
label row
cmp r9 r10
jge finish
load8 r2 $r13
add r13 1
load8 r14 $r13
mul r14 256
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
set r0 0
label token
cmp r0 r11
jge next_row
load8 r5 $r13
add r13 1
load8 r14 $r13
mul r14 256
add r5 r14
add r13 1
set r7 16
mov r1 r0
mul r1 4
add r7 r1
add r7 r12
load8 r6 $r7
cmp r6 1
je subject
cmp r6 2
je predicate
cmp r6 4
je object
cmp r6 16
jne invalid
add r7 1
load8 r8 $r7
add r7 1
load8 r14 $r7
mul r14 256
add r8 r14
jmp compare
label subject
mov r8 r2
jmp entity
label object
mov r8 r4
label entity
cmp r8 0
je invalid
cmp r8 13
jlt compare
cmp r8 22
jle invalid
cmp r8 255
jgt extended_entity
set r7 7400000000000006000
add r7 r8
jmp entity_kind
label extended_entity
set r7 7800000000000020000
add r7 r8
label entity_kind
load8 r1 $r7
cmp r1 1
jne invalid
jmp compare
label predicate
mov r8 r3
cmp r8 22
jle invalid
cmp r8 255
jgt extended_predicate
set r7 7400000000000006000
add r7 r8
jmp predicate_kind
label extended_predicate
set r7 7800000000000020000
add r7 r8
label predicate_kind
load8 r1 $r7
cmp r1 2
jne invalid
label compare
cmp r5 r8
jne invalid
add r0 1
jmp token
label next_row
add r9 1
jmp row
label finish
# Per-construction and global counters increase only after the whole batch
# agrees. Runtime errors roll the input state back, including earlier rows.
mov r7 r12
add r7 80
load8 r0 8000000000000000016
mul r0 4
add r7 r0
set r6 8000000000000000008
add r6 r0
set r8 0
label counter
set r1 0
set r2 1
set r3 0
label read_count
mov r4 r7
add r4 r3
load8 r0 $r4
mul r0 r2
add r1 r0
mul r2 256
add r3 1
cmp r3 4
jlt read_count
add r1 r10
cmp r1 4294967295
jgt invalid
set r3 0
label write_count
mov r4 r7
add r4 r3
mov r0 r1
mod r0 256
store8 $r4 r0
div r1 256
add r3 1
cmp r3 4
jlt write_count
cmp r8 1
je cleanup
set r8 1
mov r7 r6
jmp counter
label cleanup
set r7 8000000000000100000
label clean_rows
cmp r7 r13
jge clean_header
store8 $r7 0
add r7 1
jmp clean_rows
label clean_header
set r0 16
label clean_control
set r7 8000000000000000000
add r7 r0
store8 $r7 0
add r0 1
cmp r0 64
jlt clean_control
halt
label invalid
div r0 0
