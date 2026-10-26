#!reverse-pc-machine-v1
# Structured fictional roles: person(1), count object(2), nominal category(3).
# Person gender labels only resolve explicit latest-referent pronouns.
load8 r0 7700000000000000002
cmp r0 1
jne invalid
load8 r0 7700000000000000016
cmp r0 4
jne invalid
load8 r1 7700000000000000017
cmp r1 0
je invalid
cmp r1 13
jlt old_entity
cmp r1 22
jle invalid
label old_entity
cmp r1 12
jle role
set r7 7400000000000006000
add r7 r1
load8 r0 $r7
cmp r0 1
jne invalid
label role
load8 r2 7700000000000000018
cmp r2 1
jlt invalid
cmp r2 3
jgt invalid
load8 r3 7700000000000000019
cmp r2 1
je person
cmp r3 0
jne invalid
jmp address
label person
cmp r3 1
jlt invalid
cmp r3 2
jgt invalid
label address
set r7 7700000000000010000
mul r1 4
add r7 r1
load8 r0 $r7
cmp r0 0
je write
cmp r0 r2
jne invalid
mov r8 r7
add r8 1
load8 r0 $r8
cmp r0 r3
jne invalid
label write
store8 $r7 r2
add r7 1
store8 $r7 r3
halt
label invalid
div r0 0
