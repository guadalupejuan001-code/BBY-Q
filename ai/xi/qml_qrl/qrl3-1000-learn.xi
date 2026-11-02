#!reverse-pc-machine-v1
# QRL3 learns by changing Pauli X gates on its own 1000-qubit
# GHZ circuit, not by changing an unrelated memory-only lookup.
# Shared discrete parameter controls 9 physical readout qubits per group.
# Reward-only binary contextual bandit; observed action must match circuit.
load8 r0 8350000000000000000
cmp r0 114
jne invalid
load8 r1 8350000000000000001
cmp r1 110
jgt invalid
load8 r2 8350000000000000002
cmp r2 1
jgt invalid
load8 r5 8350000000000000005
cmp r5 241
jne invalid
load8 r3 8350000000000000003
cmp r3 1
jgt invalid
load8 r4 8350000000000000004
cmp r4 100
je valid_reward
cmp r4 0
jne invalid
label valid_reward

load8 r7 8350000000000000030
load8 r8 8350000000000000031
mul r8 256
add r7 r8
cmp r7 65535
jge invalid
mov r9 r1
add r9 8350000000000000256
load8 r10 $r9
cmp r10 1
jgt invalid
cmp r3 r10
jne invalid
mov r11 r10
cmp r4 100
je unchanged
set r11 1
sub r11 r10
jmp should_flip

label should_flip
mov r12 r1
mul r12 9
add r12 3001
set r13 0
label flip_nine
x $r12
add r12 1
add r13 1
cmp r13 9
jlt flip_nine
store8 $r9 r11
jmp done_gate
label unchanged
set r13 0
label done_gate
add r7 1
mov r14 r7
mod r14 256
store8 8350000000000000030 r14
mov r14 r7
div r14 256
store8 8350000000000000031 r14
store8 8350000000000000005 0
store8 8350000000000000001 0
store8 8350000000000000002 0
store8 8350000000000000003 0
store8 8350000000000000004 0
print r1
print r10
print r11
print r13
print r7
halt
label invalid
div r0 0
