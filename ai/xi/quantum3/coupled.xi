# VQC3 -> QRL3 representation experiment. Both registers are evaluated at
# every policy decision. Frozen and alternating joint training are distinct.
label coupled_forward
# Keep the state-only feature vector for the later auxiliary task.
set r2 0
label preserve_raw_features
mov r0 r2
mul r0 8
add r0 8140000000000300000
fload f0 $r0
add r0 50000
fstore $r0 f0
add r2 1
cmp r2 1000
jlt preserve_raw_features
store64 8140000000000000000 0
call select_agent
call forward
# Measured VQC observables become QRL input angles, without a predicted action
# or environment target being supplied to the policy.
set r2 0
label representation_angles
mov r0 r2
mul r0 8
add r0 8140000000000310000
fload f0 $r0
fset f1 1
fsub f1 f0
fmul f1 1.5707963267948966
sub r0 10000
fstore $r0 f1
add r2 1
cmp r2 1000
jlt representation_angles
store64 8140000000000000000 1
call select_agent
call forward
ret

# Alternating joint training, not an end-to-end gradient through both agents:
# after the RL return is observed, VQC predicts the episode's actual success
# from its last observed state. This signal is experience-derived, never a
# programmed correct action. Frozen mode performs no VQC parameter update.
label coupled_aux_update
load64 r0 8140000000000000544
cmp r0 2
jne auxiliary_done
clock f0
fstore 8140000000000000560 f0
set r2 0
label restore_raw_features
mov r0 r2
mul r0 8
add r0 8140000000000350000
fload f0 $r0
sub r0 50000
fstore $r0 f0
add r2 1
cmp r2 1000
jlt restore_raw_features
load64 r0 8140000000000000368
itof f0 r0
fstore 8140000000000000128 f0
store64 8140000000000000000 0
call supervised_update
clock f0
fload f1 8140000000000000560
fsub f0 f1
fload f1 8140000000000000504
fadd f0 f1
fstore 8140000000000000504 f0
store64 8140000000000000000 1
call select_agent
label auxiliary_done
ret
