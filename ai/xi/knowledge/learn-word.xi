#!reverse-pc-machine-v1
# Symbolic lexical teaching: event +24=1, ID +25, role +26, language +27.
# The teacher supplies a referent, not a sensor; no claim of real perception.
load8 r0 7400000000000000024
cmp r0 1
jne invalid
load8 r0 7400000000000000040
cmp r0 0
jne invalid
load8 r0 7400000000000000032
cmp r0 1
jne invalid
load8 r2 7400000000000000025
cmp r2 1
jlt invalid
load8 r3 7400000000000000026
cmp r3 1
jlt invalid
cmp r3 3
jgt invalid
load8 r4 7400000000000000027
cmp r4 1
je language_ok
cmp r4 2
jne invalid
label language_ok
load8 r0 7400000000000001600
cmp r0 0
je check_role
cmp r0 r2
jne invalid
label check_role
set r7 7400000000000006000
add r7 r2
load8 r8 $r7
cmp r8 0
je new_concept
cmp r8 r3
jne invalid
jmp concept_ok
label new_concept
store8 $r7 r3
label concept_ok
load8 r5 7400000000000000004
load8 r0 7400000000000000005
mul r0 256
add r5 r0
set r0 0
label same_language_entry
cmp r0 r5
jge allocate
set r7 7400000000000010000
mov r8 r0
mul r8 40
add r7 r8
load8 r8 $r7
cmp r8 r2
jne next_entry
add r7 2
load8 r8 $r7
cmp r8 r4
jne next_entry
add r7 1
load8 r8 $r7
load8 r9 7400000000000000512
cmp r8 r9
jne next_entry
set r1 0
label compare_entry
cmp r1 r9
jge clean
set r10 7400000000000000513
add r10 r1
load8 r11 $r10
mov r10 r7
add r10 1
add r10 r1
load8 r12 $r10
cmp r11 r12
jne next_entry
add r1 1
jmp compare_entry
label next_entry
add r0 1
jmp same_language_entry
label allocate
cmp r5 512
jge invalid
set r7 7400000000000010000
mov r0 r5
mul r0 40
add r7 r0
store8 $r7 r2
add r7 1
store8 $r7 r3
add r7 1
store8 $r7 r4
add r7 1
load8 r6 7400000000000000512
store8 $r7 r6
add r7 1
set r0 0
label copy_letters
cmp r0 r6
jge committed
set r8 7400000000000000513
add r8 r0
load8 r9 $r8
mov r8 r7
add r8 r0
store8 $r8 r9
add r0 1
jmp copy_letters
label committed
add r5 1
mov r0 r5
mod r0 256
store8 7400000000000000004 r0
div r5 256
store8 7400000000000000005 r5
label clean
set r0 16
label clear_intake
set r7 7400000000000000000
add r7 r0
store8 $r7 0
add r0 1
cmp r0 2048
jlt clear_intake
halt
label invalid
div r0 0
