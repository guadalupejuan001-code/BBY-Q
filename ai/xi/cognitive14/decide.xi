#!reverse-pc-machine-v1
# Conservative shadow selection: 70% purity, support >=3, abstain on guarded/mixed.
load8 r0 8270000000000000000
cmp r0 14
jne c14_invalid
load8 r1 8270000000000000001
cmp r1 143
jgt c14_invalid
set r2 0
set r3 0
set r4 -1
set r5 0
set r6 0
label c14_choice
mov r7 r1
mul r7 4
add r7 r2
mul r7 2
add r7 8270000000000000100
load8 r8 $r7
add r7 1
load8 r9 $r7
mul r9 256
add r8 r9
add r5 r8
cmp r8 r4
jle c14_keep
mov r4 r8
mov r3 r2
label c14_keep
add r2 1
cmp r2 4
jlt c14_choice
cmp r5 3
jlt c14_abstain
mov r10 r4
mul r10 100
mov r11 r5
mul r11 70
cmp r10 r11
jlt c14_abstain
mov r10 r1
div r10 2
mod r10 8
cmp r10 4
je c14_abstain
cmp r10 7
je c14_abstain
set r6 1
jmp c14_result
label c14_abstain
set r6 0
set r3 0
label c14_result
set r11 0
cmp r5 0
je c14_print
mov r11 r4
mul r11 100
div r11 r5
label c14_print
print r1
print r3
print r4
print r5
print r6
print r11
halt
label c14_invalid
div r0 0
