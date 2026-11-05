# QMemory: 250 independent four-qubit memories, three shared trainable angles.
# Local real excitation exchange; fixed Z readout. No MPS or trainable readout.
label qm_random
load64 r0 8170000000000000200
mul r0 1103515245
add r0 12345
mod r0 2147483648
store64 8170000000000000200 r0
set r1 0
cmp r0 1073741824
jlt qm_random_return
set r1 1
label qm_random_return
ret

label qm_data
set r15 0
label qm_data_case
call qm_random
mov r0 r15
add r0 8170000000000010000
store8 $r0 r1
mov r6 r1
call qm_random
mov r0 r15
add r0 8170000000000011000
store8 $r0 r1
mov r7 r1
call qm_random
mov r0 r15
add r0 8170000000000012000
store8 $r0 r1
cmp r7 0
je qm_keep_target
mov r6 r1
label qm_keep_target
mov r0 r15
add r0 8170000000000050000
store8 $r0 r6
set r12 0
label qm_data_noise
call qm_random
mov r0 r12
mul r0 250
add r0 r15
add r0 8170000000000020000
store8 $r0 r1
add r12 1
cmp r12 24
jlt qm_data_noise
add r15 1
load64 r0 8170000000000000008
cmp r15 r0
jlt qm_data_case
ret

# r14 memory site, r7 auxiliary site, f5 angle. Only f6 is clobbered.
label qm_exchange
cx $r14 $r7
ry $r14 f5
cx $r7 $r14
fmov f6 f5
fmul f6 -1
ry $r14 f6
cx $r7 $r14
cx $r14 $r7
ret

# Consecutive inputs evolve the SAME state; initialization occurs once per sequence.
label qm_quantum
set r15 0
label qm_quantum_case
mov r14 r15
mul r14 4
add r14 20000
qprepare $r14 4
mov r0 r15
add r0 8170000000000010000
load8 r1 $r0
cmp r1 0
je qm_teacher_encoded
mov r7 r14
add r7 1
x $r7
label qm_teacher_encoded
mov r0 r15
add r0 8170000000000012000
load8 r1 $r0
cmp r1 0
je qm_correction_encoded
mov r7 r14
add r7 2
x $r7
label qm_correction_encoded
mov r7 r14
add r7 1
fload f5 8170000000000000064
call qm_exchange
set r12 0
load64 r13 8170000000000000208
cmp r13 0
je qm_correct
label qm_noise_before
call qm_quantum_noise
add r12 1
cmp r12 r13
jlt qm_noise_before
label qm_correct
mov r0 r15
add r0 8170000000000011000
load8 r1 $r0
cmp r1 0
je qm_corrected
mov r7 r14
add r7 2
fload f5 8170000000000000072
call qm_exchange
label qm_corrected
load64 r13 8170000000000000208
mul r13 2
cmp r12 r13
jge qm_query
label qm_noise_after
call qm_quantum_noise
add r12 1
cmp r12 r13
jlt qm_noise_after
label qm_query
load64 r0 8170000000000000048
cmp r0 1
jne qm_read
qprepare $r14 4
label qm_read
fexpect f0 Z:$r14
fset f10 1
fsub f10 f0
fdiv f10 2
mov r0 r15
mul r0 8
add r0 8170000000000051000
fstore $r0 f10
add r15 1
load64 r0 8170000000000000008
cmp r15 r0
jlt qm_quantum_case
ret

label qm_quantum_noise
mov r0 r12
mul r0 250
add r0 r15
add r0 8170000000000020000
load8 r1 $r0
mov r7 r14
add r7 3
cmp r1 0
je qm_noise_encoded
x $r7
label qm_noise_encoded
fload f5 8170000000000000080
call qm_exchange
ret

# Matched classical recurrent control: two scalar states, same three gate parameters.
# It receives all input operations; its output is fixed as h, with no readout learner.
label qm_classical
fload f12 8170000000000000096
call qm_gate
fmov f12 f0
fload f13 8170000000000000104
fmov f12 f12
fmov f5 f13
fmul f5 2
fcos f5 f5
fset f13 1
fsub f13 f5
fdiv f13 2
fload f14 8170000000000000112
fmov f5 f14
fmul f5 2
fcos f5 f5
fset f14 1
fsub f14 f5
fdiv f14 2
set r15 0
label qm_classic_case
mov r0 r15
add r0 8170000000000010000
load8 r1 $r0
itof f10 r1
fmul f10 f12
fset f11 0
set r12 0
load64 r13 8170000000000000208
cmp r13 0
je qm_classic_correct
label qm_classic_before
call qm_classic_noise
add r12 1
cmp r12 r13
jlt qm_classic_before
label qm_classic_correct
mov r0 r15
add r0 8170000000000011000
load8 r1 $r0
cmp r1 0
je qm_classic_corrected
mov r0 r15
add r0 8170000000000012000
load8 r1 $r0
itof f0 r1
fsub f0 f10
fmul f0 f13
fadd f10 f0
label qm_classic_corrected
load64 r13 8170000000000000208
mul r13 2
cmp r12 r13
jge qm_classic_query
label qm_classic_after
call qm_classic_noise
add r12 1
cmp r12 r13
jlt qm_classic_after
label qm_classic_query
load64 r0 8170000000000000048
cmp r0 1
jne qm_classic_read
fset f10 0
label qm_classic_read
mov r0 r15
mul r0 8
add r0 8170000000000051000
fstore $r0 f10
add r15 1
load64 r0 8170000000000000008
cmp r15 r0
jlt qm_classic_case
ret

label qm_gate
fmov f5 f12
fmul f5 2
fcos f5 f5
fset f0 1
fsub f0 f5
fdiv f0 2
ret

label qm_classic_noise
mov r0 r12
mul r0 250
add r0 r15
add r0 8170000000000020000
load8 r1 $r0
cmp r1 0
je qm_classic_noise_ready
fset f0 1
fsub f0 f11
fmov f11 f0
label qm_classic_noise_ready
fmov f0 f11
fsub f0 f10
fmul f0 f14
fadd f10 f0
ret

label qm_forward
load64 r0 8170000000000000016
cmp r0 0
jne qm_forward_classic
call qm_quantum
ret
label qm_forward_classic
call qm_classical
ret

# Only the scorer reads targets. Forward passes never read this address range.
label qm_score
set r15 0
set r6 0
set r7 0
set r8 0
fset f24 0
label qm_score_case
mov r0 r15
mul r0 8
add r0 8170000000000051000
fload f10 $r0
mov r0 r15
add r0 8170000000000050000
load8 r1 $r0
itof f0 r1
fsub f0 f10
fmul f0 f0
fadd f24 f0
set r2 0
fcmp f10 0.5
jlt qm_predicted
set r2 1
label qm_predicted
cmp r1 r2
jne qm_score_next
add r6 1
label qm_score_next
mov r0 r15
add r0 8170000000000011000
load8 r1 $r0
cmp r1 0
je qm_score_advance
add r7 1
mov r0 r15
add r0 8170000000000050000
load8 r1 $r0
cmp r1 r2
jne qm_score_advance
add r8 1
label qm_score_advance
add r15 1
load64 r0 8170000000000000008
cmp r15 r0
jlt qm_score_case
fmov f25 f24
itof f0 r0
fdiv f25 f0
ret

# Central finite differences: a shared angle can occur many times per sequence.
# A single-gate parameter-shift rule would be invalid here.
label qm_train
load64 r0 8170000000000000016
set r9 8170000000000000064
cmp r0 0
je qm_train_selected
set r9 8170000000000000096
label qm_train_selected
set r10 0
label qm_gradient
mov r0 r10
mul r0 8
add r0 r9
fload f20 $r0
fstore 8170000000000000160 f20
fload f21 8170000000000000136
fadd f20 f21
fstore $r0 f20
call qm_forward
call qm_score
fstore 8170000000000000184 f25
fload f20 8170000000000000160
fload f21 8170000000000000136
fsub f20 f21
mov r0 r10
mul r0 8
add r0 r9
fstore $r0 f20
call qm_forward
call qm_score
fload f20 8170000000000000184
fsub f20 f25
fload f21 8170000000000000136
fmul f21 2
fdiv f20 f21
mov r0 r10
mul r0 8
add r0 8170000000000000256
fstore $r0 f20
fload f20 8170000000000000160
mov r0 r10
mul r0 8
add r0 r9
fstore $r0 f20
add r10 1
cmp r10 3
jlt qm_gradient
set r10 0
label qm_apply
mov r0 r10
mul r0 8
add r0 8170000000000000256
fload f0 $r0
fload f1 8170000000000000128
fmul f0 f1
# Reused noise gates need an exposure-normalized update, in both controls.
cmp r10 2
jne qm_unscaled
load64 r1 8170000000000000208
mul r1 2
add r1 1
itof f1 r1
fdiv f0 f1
label qm_unscaled
mov r0 r10
mul r0 8
add r0 r9
fload f1 $r0
fsub f1 f0
fmax f1 -1.5707963267948966
fmin f1 1.5707963267948966
fstore $r0 f1
add r10 1
cmp r10 3
jlt qm_apply
load64 r0 8170000000000000016
mul r0 8
add r0 8170000000000000024
load64 r1 $r0
add r1 1
store64 $r0 r1
call qm_forward
call qm_score
ret
