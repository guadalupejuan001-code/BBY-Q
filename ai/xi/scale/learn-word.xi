#!reverse-pc-machine-v1
# Bind the middle spelling of NUMBER WORD NUMBER to an opaque concept ID.
# M+24 concept (1..8),+25 language (1..2). Never assign a primitive here.
load8 r0 7900000000000000002
cmp r0 1
jne invalid
load8 r0 7300000000000000040
cmp r0 0
jne invalid
load8 r0 7300000000000000032
cmp r0 3
jne invalid
load8 r0 7300000000000000800
cmp r0 1
jne invalid
load8 r0 7300000000000000808
cmp r0 1
jne invalid
load8 r0 7300000000000000804
cmp r0 0
jne invalid
load8 r10 7900000000000000024
cmp r10 1
jlt invalid
cmp r10 8
jgt invalid
load8 r11 7900000000000000025
cmp r11 1
jlt invalid
cmp r11 2
jgt invalid
load8 r2 7300000000000000530
cmp r2 1
jlt invalid
cmp r2 16
jgt invalid
set r0 0
label validate
cmp r0 r2
jge lookup
set r7 7300000000000000531
add r7 r0
load8 r3 $r7
cmp r3 97
jlt invalid
cmp r3 122
jgt invalid
add r0 1
jmp validate
label lookup
load8 r12 7900000000000000004
set r0 0
label word
cmp r0 r12
jge allocate
set r7 7900000000000001000
mov r3 r0
mul r3 32
add r7 r3
load8 r3 $r7
cmp r3 r2
jne next_word
set r1 0
label compare
cmp r1 r2
jge duplicate
set r8 7300000000000000531
add r8 r1
load8 r3 $r8
mov r8 r7
add r8 1
add r8 r1
load8 r4 $r8
cmp r3 r4
jne next_word
add r1 1
jmp compare
label duplicate
mov r8 r7
add r8 17
load8 r3 $r8
cmp r3 r10
jne invalid
add r8 1
load8 r3 $r8
cmp r3 r11
jne invalid
jmp clean
label next_word
add r0 1
jmp word
label allocate
cmp r12 32
jge invalid
set r7 7900000000000001000
mov r3 r12
mul r3 32
add r7 r3
store8 $r7 r2
set r0 0
label copy
cmp r0 r2
jge copied
set r8 7300000000000000531
add r8 r0
load8 r3 $r8
mov r8 r7
add r8 1
add r8 r0
store8 $r8 r3
add r0 1
jmp copy
label copied
add r7 17
store8 $r7 r10
add r7 1
store8 $r7 r11
add r12 1
store8 7900000000000000004 r12
label clean
store8 7900000000000000024 0
store8 7900000000000000025 0
set r0 16
label clear_intake
set r7 7300000000000000000
add r7 r0
store8 $r7 0
add r0 1
cmp r0 864
jlt clear_intake
halt
label invalid
div r0 0
