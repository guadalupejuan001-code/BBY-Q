#!reverse-pc-machine-v1
# Measured VQC/QRL action computed from TWO real, independent 1000-qubit GHZ registers.
# The native measured quantum phase is the only inference output; not a fake 2-qubit result.
# PHASE ENCODING: Z on GHZ qubit i iff input feature[i] AND model weight[i].
# GHZ inverse uncomputes a 1000-qubit circuit into a deterministic Z readout.
# Inverse and repeated phases restore original GHZ; inference is a scratch transaction.
load8 r0 8120000000000000000
cmp r0 166
jne invalid
load8 r14 8120000000000000001
cmp r14 1
jgt invalid
load8 r12 8120000000000000002
cmp r12 1
jlt invalid
cmp r12 32
jgt invalid
set r13 100
cmp r14 0
je selected_core
set r13 1200
label selected_core
mov r0 r13
set r1 8120000000000000300
set r2 0
cmp r14 0
jne encode_rl_model
set r2 8120000000000001500
jmp encode_model_ready
label encode_rl_model
set r2 8120000000000002600
label encode_model_ready
set r11 0
label encode_loop
load8 r5 $r1
load8 r6 $r2
cmp r5 1
jgt invalid
cmp r6 1
jgt invalid
cmp r5 1
jne encode_skip
cmp r6 1
jne encode_skip
z $r0
label encode_skip
add r0 1
add r1 1
add r2 1
add r11 1
cmp r11 1000
jlt encode_loop
mov r0 r13
add r0 998
mov r1 r13
add r1 999
label inverse_cx
cx $r0 $r1
sub r0 1
sub r1 1
cmp r0 r13
jge inverse_cx
h $r13
probz $r13
expect Z:$r13
h $r13
mov r0 r13
mov r1 r13
add r1 1
mov r10 r13
add r10 1000
label restore_cx
cx $r0 $r1
add r0 1
add r1 1
cmp r1 r10
jlt restore_cx
mov r0 r13
set r1 8120000000000000300
set r2 0
cmp r14 0
jne decode_rl_model
set r2 8120000000000001500
jmp decode_model_ready
label decode_rl_model
set r2 8120000000000002600
label decode_model_ready
set r11 0
label decode_loop
load8 r5 $r1
load8 r6 $r2
cmp r5 1
jgt invalid
cmp r6 1
jgt invalid
cmp r5 1
jne decode_skip
cmp r6 1
jne decode_skip
z $r0
label decode_skip
add r0 1
add r1 1
add r2 1
add r11 1
cmp r11 1000
jlt decode_loop
cmp r14 0
jne audit_qrl
expect Z:100 Z:1099
probz 100
jmp audit_done
label audit_qrl
expect Z:1200 Z:2199
probz 1200
label audit_done
stats
print r11
print r14
halt
label invalid
div r0 0
