# E02: shared task workspace. Learning and semantic checks execute in XI.
# E=8184000000000000000. Teacher fields (+264/+272) are only read by feedback.
label entity_infer
store64 8184000000000000056 0
store64 8184000000000000064 0
store64 8184000000000000088 0
store64 8184000000000000080 -1
store64 8184000000000000072 -1
load64 r0 8184000000000000008
cmp r0 1
jne entity_infer_done
load64 r0 8184000000000000016
cmp r0 1
jne entity_infer_done
load64 r0 8184000000000000024
cmp r0 0
jlt entity_infer_done
cmp r0 6
jgt entity_infer_done
fload f0 8184000000000000040
set r0 0
fcmp f0 0.5
jlt entity_rule_ready
set r0 1
label entity_rule_ready
store64 8184000000000000064 r0
fload f0 8184000000000000048
set r1 0
fcmp f0 0.5
jlt entity_class_ready
set r1 1
label entity_class_ready
store64 8184000000000000056 r1
add r1 r0
mod r1 2
mul r1 6
store64 8184000000000000072 r1
store64 8184000000000000088 1
label entity_infer_done
ret

label entity_features
fstore 8184000000000002000 1
fload f0 8184000000000000048
fsub f0 0.5
fmul f0 f0
fsqrt f0 f0
fmul f0 2
fstore 8184000000000002008 f0
fload f0 8184000000000000040
fsub f0 0.5
fmul f0 f0
fsqrt f0 f0
fmul f0 2
fstore 8184000000000002016 f0
fload f0 8184000000000000160
fsub f0 0.5
fmul f0 f0
fsqrt f0 f0
fmul f0 2
fstore 8184000000000002024 f0
load64 r0 8184000000000000088
itof f0 r0
fstore 8184000000000002032 f0
fset f20 0
set r2 0
label entity_predict_loop
mov r0 r2
mul r0 8
add r0 8184000000000001000
fload f0 $r0
add r0 1000
fload f1 $r0
fmul f0 f1
fadd f20 f0
add r2 1
cmp r2 5
jlt entity_predict_loop
fmax f20 -15
fmin f20 15
fmul f20 -1
fexp f20 f20
fadd f20 1
fset f21 1
fdiv f21 f20
fstore 8184000000000000112 f21
ret

# Explicit verified feedback only, never predictions recycled as labels.
label entity_learn
call entity_features
fload f22 8184000000000000096
fsub f22 f21
fmul f22 0.04
set r2 0
label entity_learn_loop
mov r0 r2
mul r0 8
add r0 8184000000000002000
fload f0 $r0
fmul f0 f22
sub r0 1000
fload f1 $r0
fadd f1 f0
fstore $r0 f1
add r2 1
cmp r2 5
jlt entity_learn_loop
load64 r0 8184000000000000128
add r0 1
store64 8184000000000000128 r0
ret

label entity_decide
call entity_features
load64 r0 8184000000000000176
cmp r0 1
jne entity_decide_done
fload f0 8184000000000000112
fcmp f0 0.55
jge entity_decide_done
store64 8184000000000000080 -1
label entity_decide_done
ret

# Curriculum environment and independent result verifier, not the QRL actor.
label entity_score
load64 r0 8184000000000000264
load64 r1 8184000000000000272
add r0 r1
mod r0 2
mul r0 6
store64 8184000000000000280 r0
load64 r1 8184000000000000024
set r2 2
cmp r1 r0
je entity_gold_ready
set r2 0
cmp r1 r0
jgt entity_gold_ready
set r2 1
label entity_gold_ready
store64 8184000000000000288 r2
load64 r0 8184000000000000008
load64 r1 8184000000000000016
mul r0 r1
cmp r0 1
je entity_score_present
set r2 -1
store64 8184000000000000288 r2
label entity_score_present
load64 r0 8184000000000000080
set r1 0
cmp r0 r2
jne entity_score_wrong
set r1 1
label entity_score_wrong
itof f0 r1
fstore 8184000000000000304 f0
load64 r0 8184000000000000144
itof f1 r0
fmul f0 f1
fstore 8184000000000000096 f0
femit joint_success f0
femit plan_success f1
ret

# Shared state -> 64 semantic bits, before the same exact 100-qubit encoder.
# Remaining bits contain the output prefix and token-position byte codec.
label entity_voice_bits
set r2 0
label entity_voice_clear
mov r0 r2
add r0 8160000000000001000
store8 $r0 0
add r2 1
cmp r2 64
jlt entity_voice_clear
load64 r0 8184000000000000080
add r0 1
add r0 8160000000000001000
store8 $r0 1
ret

# The learned voice must describe the actual selected action exactly.
# Vocabulary extension is append-only: mover=75, izquierda=76, derecha=77,
# objetivo=78, alcanzado=79; existing indices remain unchanged.
label entity_voice_check
store64 8184000000000000144 0
load64 r0 8184000000000000080
cmp r0 -1
je entity_voice_refusal
cmp r0 2
je entity_voice_terminal
load64 r1 8184000000000000592
cmp r1 5
jne entity_voice_check_done
load8 r1 8184000000000000600
cmp r1 75
jne entity_voice_check_done
load8 r1 8184000000000000601
cmp r1 4
jne entity_voice_check_done
load8 r1 8184000000000000602
cmp r1 43
jne entity_voice_check_done
add r0 76
load8 r1 8184000000000000603
cmp r1 r0
jne entity_voice_check_done
load8 r1 8184000000000000604
cmp r1 3
jne entity_voice_check_done
jmp entity_voice_correct
label entity_voice_terminal
load64 r1 8184000000000000592
cmp r1 3
jne entity_voice_check_done
load8 r1 8184000000000000600
cmp r1 78
jne entity_voice_check_done
load8 r1 8184000000000000601
cmp r1 79
jne entity_voice_check_done
load8 r1 8184000000000000602
cmp r1 3
jne entity_voice_check_done
jmp entity_voice_correct
label entity_voice_refusal
load64 r1 8184000000000000592
cmp r1 4
jne entity_voice_check_done
load8 r1 8184000000000000600
cmp r1 52
jne entity_voice_check_done
load8 r1 8184000000000000601
cmp r1 50
jne entity_voice_check_done
load8 r1 8184000000000000602
cmp r1 40
jne entity_voice_check_done
load8 r1 8184000000000000603
cmp r1 3
jne entity_voice_check_done
label entity_voice_correct
store64 8184000000000000144 1
label entity_voice_check_done
ret
