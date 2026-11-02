#!reverse-pc-machine-v1
# Agent-native XI feedback: VQC supervised label; QRL environment reward.
# Both are based on the ACTUAL 1000-qubit quantum probz output staged by host.
# One-hot training only, full 1000-feature inference supports sparse combinations.
load8 r0 8120000000000000000
cmp r0 166
jne invalid
load8 r1 8120000000000000001
cmp r1 1
jgt invalid
load8 r2 8120000000000000002
cmp r2 1
jne invalid
load8 r3 8120000000000000020
load8 r4 8120000000000000021
mul r4 256
add r3 r4
cmp r3 999
jgt invalid
load8 r5 8120000000000000003
cmp r5 1
jgt invalid
load8 r6 8120000000000000004
cmp r6 1
jgt invalid
load8 r7 8120000000000000005
cmp r7 100
jgt invalid
cmp r1 0
je vqc
cmp r7 0
je qrl_update
cmp r7 100
jne invalid
jmp qrl_no_update
label vqc
cmp r5 r6
je qrl_no_update
jmp qrl_update
label qrl_update
mov r8 r3
cmp r1 0
jne qrl_vector
add r8 8120000000000001500
jmp model_ready
label qrl_vector
add r8 8120000000000002600
label model_ready
load8 r9 $r8
cmp r9 1
jgt invalid
set r10 1
sub r10 r9
store8 $r8 r10
jmp visit
label qrl_no_update
mov r8 r3
cmp r1 0
jne qrl_vector_read
add r8 8120000000000001500
jmp model_ready_read
label qrl_vector_read
add r8 8120000000000002600
label model_ready_read
load8 r10 $r8
cmp r10 1
jgt invalid
label visit
mov r8 r3
cmp r1 0
jne qrl_visit
add r8 8120000000000003700
jmp visit_ready
label qrl_visit
add r8 8120000000000004800
label visit_ready
load8 r11 $r8
cmp r11 255
jge invalid
add r11 1
store8 $r8 r11
cmp r1 0
jne update_rl
load8 r12 8120000000000000006
load8 r13 8120000000000000007
jmp update_ready
label update_rl
load8 r12 8120000000000000008
load8 r13 8120000000000000009
label update_ready
mul r13 256
add r12 r13
cmp r12 65535
jge invalid
add r12 1
mov r15 r12
mod r15 256
mov r0 r12
div r0 256
cmp r1 0
jne store_rl
store8 8120000000000000006 r15
store8 8120000000000000007 r0
jmp done
label store_rl
store8 8120000000000000008 r15
store8 8120000000000000009 r0
label done
print r1
print r3
print r10
print r11
print r12
print r6
print r7
halt
label invalid
div r0 0
