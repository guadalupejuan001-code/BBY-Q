# Native XI subroutines. r12=metadata, r13=theta, r14=weights,
# r15=quantum start. No target/reward or optimizer is implemented by the host.
label select_agent
load64 r0 8140000000000000000
set r12 8140000000000004000
set r13 8140000000000100000
set r14 8140000000000110000
set r15 5000
cmp r0 0
je selected
set r12 8140000000000005000
set r13 8140000000000200000
set r14 8140000000000210000
set r15 7000
label selected
ret

# LCG, reproducible uniform [0,1); algorithm is part of the XI test environment.
# Clobbers only r0 and f30. All products fit signed int64.
label random_uniform
load64 r0 8140000000000000256
mul r0 1103515245
add r0 12345
mod r0 2147483648
store64 8140000000000000256 r0
itof f30 r0
fdiv f30 2147483648
ret

# One 1000-wire MPS register. Every neighbour pair is connected, including
# former four-wire boundaries. All theta coordinates are trained per update.
# d<Z_q>/d(theta_q)=-<X_q> because RY(theta_q) is the final gate on q.
# This exact commutator identity avoids 2000 full-circuit shifted evaluations;
# the quantum X and Z expectations are both evaluated on the connected state.
label forward
fset f20 0
set r0 8140000000000310000
store64 8140000000000000048 r0
load64 r0 8140000000000000280
cmp r0 2
je classical_forward
qmps $r15 1000
set r2 0
label encode_loop
mov r7 r2
mul r7 8
add r7 8140000000000300000
fload f0 $r7
mov r4 r15
add r4 r2
ry $r4 f0
add r2 1
cmp r2 1000
jlt encode_loop
set r2 0
label chain_entanglers
mov r4 r15
add r4 r2
mov r5 r4
add r5 1
cx $r4 $r5
add r2 1
cmp r2 999
jlt chain_entanglers
set r2 0
label variational_loop
mov r5 r2
mul r5 8
add r5 r13
fload f0 $r5
mov r4 r15
add r4 r2
ry $r4 f0
add r2 1
cmp r2 1000
jlt variational_loop
set r2 0
label observe_loop
mov r4 r15
add r4 r2
fexpect f0 Z:$r4
fexpect f3 X:$r4
load64 r0 8140000000000000280
cmp r0 1
jne keep_observation
fset f0 0
fset f3 0
label keep_observation
call consume_observation
fmul f3 f1
fmul f3 -1
fdiv f3 31.622776601683793
mov r0 r2
mul r0 8
add r0 8140000000000130000
fstore $r0 f3
add r2 1
cmp r2 1000
jlt observe_loop
jmp finish_score

# Matched independent classical cosine baseline, with all 1000 parameters.
label classical_forward
set r2 0
label classical_loop
mov r0 r2
mul r0 8
add r0 8140000000000300000
fload f0 $r0
mov r0 r2
mul r0 8
add r0 r13
fload f1 $r0
fadd f0 f1
fsin f3 f0
fcos f0 f0
call consume_observation
fmul f3 f1
fmul f3 -1
fdiv f3 31.622776601683793
mov r0 r2
mul r0 8
add r0 8140000000000130000
fstore $r0 f3
add r2 1
cmp r2 1000
jlt classical_loop

label finish_score
fdiv f20 31.622776601683793
mov r0 r12
add r0 16
fload f0 $r0
fadd f20 f0
# Derivative of the explicit logit clamp. In the saturated region both
# readout and angle learning signals are zero, rather than straight-through.
fset f18 1
fcmp f20 25
jge saturated_score
fcmp f20 -25
jgt score_derivative_ready
label saturated_score
fset f18 0
set r2 0
label zero_saturated_gradients
mov r0 r2
mul r0 8
add r0 8140000000000130000
fstore $r0 0
add r2 1
cmp r2 1000
jlt zero_saturated_gradients
label score_derivative_ready
fstore 8140000000000000152 f18
fmax f20 -25
fmin f20 25
fmov f21 f20
fmul f21 -1
fexp f21 f21
fadd f21 1
fset f0 1
fdiv f0 f21
fmov f21 f0
fstore 8140000000000000120 f21
fstore 8140000000000000112 f20
ret

label consume_observation
load64 r8 8140000000000000048
mov r0 r2
mul r0 8
add r8 r0
fstore $r8 f0
mov r6 r14
add r6 r0
fload f1 $r6
fmul f1 f0
fadd f20 f1
# Return the unmultiplied readout weight for the exact angle derivative.
fload f1 $r6
ret

label selected_gradients
# forward already computed all 1000 exact derivatives on the full state.
ret

# One native supervised SGD update. y is staged at control+128.
# Theta gradients are applied before changing the linear readout weights.
label supervised_update
call select_agent
clock f28
call forward
fload f0 8140000000000000128
fmov f22 f21
fsub f22 f0
fmov f24 f22
fmul f24 f22
fstore 8140000000000000136 f24
fmov f25 f21
flog f25 f25
fmul f25 f0
fmul f25 -1
fset f26 1
fsub f26 f21
flog f26 f26
fset f1 1
fsub f1 f0
fmul f26 f1
fsub f25 f26
fload f0 8140000000000000152
fmul f22 f0
mov r0 r12
load64 r9 $r0
set r9 0
clock f27
call selected_gradients
mov r2 r9
label apply_theta
mov r0 r2
mul r0 8
add r0 8140000000000130000
fload f0 $r0
fmul f0 f22
mov r0 r12
add r0 32
fload f1 $r0
fmul f0 f1
mov r0 r2
mul r0 8
add r0 r13
fload f1 $r0
fsub f1 f0
fmax f1 -6.283185307179586
fmin f1 6.283185307179586
fstore $r0 f1
call record_rotation_update
add r2 1
cmp r2 1000
jlt apply_theta
set r2 0
label apply_readout
mov r0 r2
mul r0 8
add r0 8140000000000310000
fload f0 $r0
fmul f0 f22
fdiv f0 31.622776601683793
mov r0 r12
add r0 24
fload f1 $r0
fmul f0 f1
mov r0 r2
mul r0 8
add r0 r14
fload f1 $r0
fsub f1 f0
fstore $r0 f1
add r2 1
cmp r2 1000
jlt apply_readout
mov r0 r12
add r0 24
fload f0 $r0
fmul f0 f22
mov r0 r12
add r0 16
fload f1 $r0
fsub f1 f0
fstore $r0 f1
load64 r0 $r12
add r0 1
store64 $r12 r0
clock f29
fmov f26 f29
fsub f26 f27
fsub f29 f28
femit update_ms f26
femit episode_ms f29
femit probability f21
femit brier f24
femit cross_entropy f25
ret

# f0 is the actual update magnitude. Counts ONLY a nonzero rotation update.
label record_rotation_update
fmov f2 f0
fmul f2 f2
fcmp f2 0.000000000000000000000001
jle record_done
mov r0 r2
mul r0 8
add r0 r13
add r0 20000
load64 r11 $r0
add r11 1
store64 $r0 r11
label record_done
ret
