# BBY Q U03 C07 — trained XI epistemic head; no host-side training.
# Actions: 0=answer if corroborated, 1=request-evidence, 2=conflict.
# Teacher ONLY staged in c07_train; prediction reads 10 evidence features
# and learned native RVPC2 coefficients. No original C1/VQC bank touched.
# B = 8150000000013000000
# B+0 train_count, +8 teacher, +16 predicted, +24 mistakes
# B+64..+80 native float64 class scores
# B+256 feature[10], B+1024 weights[3,10]
label c07_predict
set r0 0
set r12 0
fset f20 -1000000
label c07_class
fset f21 0
set r1 0
label c07_dot
mov r2 r0
mul r2 10
add r2 r1
mul r2 8
add r2 8150000000013001024
fload f0 $r2
mov r3 r1
mul r3 8
add r3 8150000000013000256
fload f1 $r3
fmul f0 f1
fadd f21 f0
add r1 1
cmp r1 10
jlt c07_dot
mov r2 r0
mul r2 8
add r2 8150000000013000064
fstore $r2 f21
fcmp f21 f20
jle c07_next_class
fmov f20 f21
mov r12 r0
label c07_next_class
add r0 1
cmp r0 3
jlt c07_class
store64 8150000000013000016 r12
ret

label c07_train
load64 r11 8150000000013000008
cmp r11 0
jlt c07_invalid_label
cmp r11 3
jge c07_invalid_label
call c07_predict
load64 r0 8150000000013000000
add r0 1
store64 8150000000013000000 r0
cmp r12 r11
je c07_train_done
load64 r0 8150000000013000024
add r0 1
store64 8150000000013000024 r0
set r1 0
label c07_update
mov r2 r1
mul r2 8
add r2 8150000000013000256
fload f0 $r2
fmul f0 0.12
mov r3 r11
mul r3 10
add r3 r1
mul r3 8
add r3 8150000000013001024
fload f1 $r3
fadd f1 f0
fstore $r3 f1
mov r4 r12
mul r4 10
add r4 r1
mul r4 8
add r4 8150000000013001024
fload f2 $r4
fsub f2 f0
fstore $r4 f2
add r1 1
cmp r1 10
jlt c07_update
label c07_train_done
ret
label c07_invalid_label
store64 8150000000013000000 -1
ret
