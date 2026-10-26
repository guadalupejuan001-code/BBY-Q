#!reverse-pc-machine-v1
# Native structural audit; the external examiner separately checks complete
# provenance cells, old memories and the original core for exact retention.
load8 r0 7400000000000000000
cmp r0 75
jne invalid
load8 r0 7400000000000000001
cmp r0 78
jne invalid
load8 r0 7400000000000000002
cmp r0 1
jne invalid
load8 r0 7400000000000000003
cmp r0 1
je language_valid
cmp r0 2
jne invalid
label language_valid
load8 r15 7400000000000000004
load8 r0 7400000000000000005
mul r0 256
add r15 r0
cmp r15 512
jgt invalid
set r0 0
label lexeme
cmp r0 r15
jge fact_start
set r7 7400000000000010000
mov r1 r0
mul r1 40
add r7 r1
load8 r2 $r7
cmp r2 0
je invalid
add r7 1
load8 r3 $r7
set r8 7400000000000006000
add r8 r2
load8 r4 $r8
cmp r3 r4
jne invalid
add r7 1
load8 r3 $r7
cmp r3 1
je lex_language
cmp r3 2
jne invalid
label lex_language
add r7 1
load8 r3 $r7
cmp r3 1
jlt invalid
cmp r3 32
jgt invalid
add r0 1
jmp lexeme
label fact_start
load8 r15 7400000000000000006
load8 r0 7400000000000000007
mul r0 256
add r15 r0
cmp r15 512
jgt invalid
set r0 0
label indexed_fact
cmp r0 r15
jge scratch_start
set r7 7400000000000080000
mov r1 r0
mul r1 3
add r7 r1
load8 r2 $r7
add r7 1
load8 r3 $r7
add r7 1
load8 r4 $r7
cmp r2 0
je invalid
cmp r3 0
je invalid
cmp r4 0
je invalid
set r7 7400000000000006000
add r7 r3
load8 r8 $r7
cmp r8 2
jne invalid
mov r7 r2
mul r7 256
add r7 r3
mul r7 256
add r7 r4
mul r7 4
add r7 7400000000001000000

add r7 2
load8 r8 $r7
cmp r8 1
jne invalid
add r0 1
jmp indexed_fact
label scratch_start
set r0 16
label scratch
set r7 7400000000000000000
add r7 r0
load8 r8 $r7
cmp r8 0
jne invalid
add r0 1
cmp r0 2048
jlt scratch
set r0 3000
label work
set r7 7400000000000000000
add r7 r0
load8 r8 $r7
cmp r8 0
jne invalid
add r0 1
cmp r0 4500
jlt work
load8 r0 7400000000000000014
cmp r0 8
jgt invalid
load8 r0 7400000000000000015
cmp r0 31
jgt invalid
mem_stats
stats
halt
label invalid
div r0 0
