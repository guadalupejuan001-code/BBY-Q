#!reverse-pc-machine-v1
# Induce response word order from raw examples and labeled semantic referents.
# 7700000000000000016=2,+17=actor,+18=item,+19=verb,+20=number concept. 4 variable slots.
load8 r0 7700000000000000002
cmp r0 1
jne invalid
load8 r0 7700000000000000016
cmp r0 2
jne invalid
load8 r0 7400000000000000040
cmp r0 0
jne invalid
load8 r0 7400000000000000032
cmp r0 4
jne invalid
load8 r9 7700000000000000017
load8 r10 7700000000000000018
load8 r11 7700000000000000019
load8 r12 7700000000000000020
cmp r9 r10
je invalid
cmp r12 13
jlt invalid
cmp r12 22
jgt invalid
set r0 0
set r13 0
label token
cmp r0 4
jge order
set r7 7400000000000001600
mov r1 r0
mul r1 2
add r7 r1
load8 r2 $r7
add r7 1
load8 r3 $r7
cmp r2 r9
je actor
cmp r2 r10
je item
cmp r2 r11
je verb
cmp r2 r12
je number
jmp invalid
label actor
set r4 1
set r5 1
cmp r3 1
jne invalid
jmp save
label verb
set r4 2
set r5 2
cmp r3 2
jne invalid
set r7 7500000000000010002
mov r1 r2
mul r1 24
add r7 r1
load8 r1 $r7
cmp r1 1
jne invalid
jmp save
label number
set r4 3
set r5 4
cmp r3 1
jne invalid
jmp save
label item
set r4 4
set r5 8
cmp r3 1
jne invalid
label save
mov r1 r13
div r1 r5
mod r1 2
cmp r1 0
jne invalid
add r13 r5
set r7 7700000000000000128
add r7 r0
store8 $r7 r4
add r0 1
jmp token
label order
cmp r13 15
jne invalid
load8 r1 7400000000000000003
cmp r1 1
jlt invalid
cmp r1 2
jgt invalid
set r7 7700000000000001000
sub r1 1
mul r1 32
add r7 r1
load8 r0 $r7
cmp r0 0
je first
cmp r0 4
jne invalid
set r0 0
label same_order
cmp r0 4
jge witness
mov r8 r7
add r8 8
add r8 r0
load8 r1 $r8
set r8 7700000000000000128
add r8 r0
load8 r2 $r8
cmp r1 r2
jne invalid
add r0 1
jmp same_order
label witness
mov r8 r7
add r8 1
load8 r0 $r8
cmp r0 2
je done
add r8 1
load8 r0 $r8
cmp r0 r9
je done
add r8 1
load8 r0 $r8
cmp r0 r10
je done
add r8 1
load8 r0 $r8
cmp r0 r12
je done
mov r8 r7
add r8 5
store8 $r8 r9
add r8 1
store8 $r8 r10
add r8 1
store8 $r8 r12
add r7 1
store8 $r7 2
jmp done
label first
store8 $r7 4
mov r8 r7
add r8 1
store8 $r8 1
add r8 1
store8 $r8 r9
add r8 1
store8 $r8 r10
add r8 1
store8 $r8 r12
set r0 0
label copy
cmp r0 4
jge done
set r8 7700000000000000128
add r8 r0
load8 r1 $r8
mov r8 r7
add r8 8
add r8 r0
store8 $r8 r1
add r0 1
jmp copy
label done
halt
label invalid
div r0 0
