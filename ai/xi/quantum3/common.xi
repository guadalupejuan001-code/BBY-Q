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

# Complete 1000-qubit forward pass, 250 entangled four-wire components.
# All 1000 observables contribute to the same score. No unused GHZ register.
label forward
set r10 -1
fset f31 0
set r0 8140000000000310000
store64 8140000000000000048 r0
fset f20 0
set r9 0
label forward_blocks
mov r1 r9
call block_forward
add r9 4
cmp r9 1000
jlt forward_blocks
fdiv f20 31.622776601683793
mov r0 r12
add r0 16
fload f0 $r0
fadd f20 f0
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

# r1 first feature, r10 shifted rotation index, f31 shift; preserves r9/r10.
# Output buffer is a byte address staged at control+48. f20 accumulates score.
label block_forward
mov r3 r1
add r3 4
mov r4 r15
add r4 r1
load64 r0 8140000000000000280
cmp r0 2
je classical_block
qprepare $r4 4
mov r2 r1
label encode_loop
mov r7 r2
mul r7 8
add r7 8140000000000300000
fload f0 $r7
mov r4 r15
add r4 r2
ry $r4 f0
add r2 1
cmp r2 r3
jlt encode_loop
mov r4 r15
add r4 r1
mov r5 r4
add r5 1
cx $r4 $r5
add r4 1
add r5 1
cx $r4 $r5
add r4 1
add r5 1
cx $r4 $r5
mov r2 r1
label variational_loop
mov r5 r2
mul r5 8
add r5 r13
fload f0 $r5
cmp r2 r10
jne no_shift
fadd f0 f31
label no_shift
mov r4 r15
add r4 r2
ry $r4 f0
add r2 1
cmp r2 r3
jlt variational_loop
mov r2 r1
label observe_loop
mov r4 r15
add r4 r2
fexpect f0 Z:$r4
load64 r0 8140000000000000280
cmp r0 1
jne keep_observation
fset f0 0
label keep_observation
call consume_observation
add r2 1
cmp r2 r3
jlt observe_loop
ret

# Matched classical baseline: independent cosine features, same parameter
# count, optimizer and samples; no simulated quantum operations in this path.
label classical_block
mov r2 r1
label classical_loop
mov r7 r2
mul r7 8
add r7 8140000000000300000
fload f0 $r7
mov r5 r2
mul r5 8
add r5 r13
fload f1 $r5
cmp r2 r10
jne classical_no_shift
fadd f1 f31
label classical_no_shift
fadd f0 f1
fcos f0 f0
call consume_observation
add r2 1
cmp r2 r3
jlt classical_loop
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
ret

# Exact local parameter-shift gradients, four coordinates per update.
# All 1000 rotations are visited cyclically over 250 supervised updates.
# The full forward observation still uses all 1000 wires on EVERY sample.
# Selected block start is r9; writes d(logit)/d(theta_i) to gradient buffer.
label selected_gradients
mov r10 r9
set r0 8140000000000320000
store64 8140000000000000048 r0
label gradient_coordinates
fset f20 0
fset f31 1.5707963267948966
mov r1 r9
call block_forward
fmov f23 f20
fset f20 0
fset f31 -1.5707963267948966
mov r1 r9
call block_forward
fsub f23 f20
fdiv f23 63.245553203367586
mov r0 r10
mul r0 8
add r0 8140000000000130000
fstore $r0 f23
add r10 1
mov r0 r9
add r0 4
cmp r10 r0
jlt gradient_coordinates
set r10 -1
fset f31 0
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
mov r0 r12
load64 r9 $r0
mod r9 250
mul r9 4
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
fmul f0 250
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
mov r0 r9
add r0 4
cmp r2 r0
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
