# One-step policy feedback for the action actually taken in the shared task.
# Environment supplies verified reward in E+304. It never selects the action.
label entity_qrl_feedback
# Do not punish the actor for an incorrect upstream premise.
load64 r0 8184000000000000056
load64 r1 8184000000000000264
cmp r0 r1
jne entity_qrl_feedback_done
load64 r0 8184000000000000064
load64 r1 8184000000000000272
cmp r0 r1
jne entity_qrl_feedback_done
store64 8140000000000000000 1
call select_agent
call qrl_observe
call forward
load64 r0 8184000000000000080
cmp r0 0
jlt entity_qrl_feedback_done
cmp r0 1
jgt entity_qrl_feedback_done
itof f22 r0
fsub f22 f21
fload f23 8184000000000000304
fmul f23 2
fsub f23 1
fmul f22 f23
fstore 8184000000000000320 f22
load64 r9 8140000000000005000
mod r9 250
mul r9 4
call selected_gradients
fload f22 8184000000000000320
set r2 0
label entity_qrl_readout
mov r0 r2
mul r0 8
add r0 8140000000000310000
fload f0 $r0
fmul f0 f22
fdiv f0 31.622776601683793
fmul f0 0.015
mov r0 r2
mul r0 8
add r0 8140000000000210000
fload f1 $r0
fadd f1 f0
fmax f1 -4
fmin f1 4
fstore $r0 f1
add r2 1
cmp r2 1000
jlt entity_qrl_readout
mov r2 r9
label entity_qrl_angles
mov r0 r2
mul r0 8
add r0 8140000000000130000
fload f0 $r0
fmul f0 f22
fmul f0 0.00001
mov r0 r2
mul r0 8
add r0 8140000000000200000
fload f1 $r0
fadd f1 f0
fstore $r0 f1
call record_rotation_update
add r2 1
mov r0 r9
add r0 4
cmp r2 r0
jlt entity_qrl_angles
fload f0 8140000000000005016
fmov f1 f22
fmul f1 0.015
fadd f0 f1
fstore 8140000000000005016 f0
load64 r0 8140000000000005000
add r0 1
store64 8140000000000005000 r0
label entity_qrl_feedback_done
ret
