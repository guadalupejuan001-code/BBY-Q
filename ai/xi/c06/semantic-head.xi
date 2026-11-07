# U03 C06 supervised 3-way semantic head, native XI ONLY.
# Input features supplied via C05 span transport, not labels at prediction.
# Targets are staged ONLY into c06_train from training examples.
# Base +0 count, +8 teacher, +16 last_prediction, +24 mistakes.
# Feature values at +256, weights at +1024, per class 8 coordinates.
# No C1 original parameter address, external labels, or frozen model bytes.
label c06_predict
set r0 0
set r12 0
fset f20 -1000000
label c06_class
fset f21 0
set r1 0
label c06_dot
mov r2 r0
mul r2 8
add r2 r1
mul r2 8
add r2 8150000000012001024
fload f0 $r2
mov r3 r1
mul r3 8
add r3 8150000000012000256
fload f1 $r3
fmul f0 f1
fadd f21 f0
add r1 1
cmp r1 8
jlt c06_dot
fcmp f21 f20
jle c06_next_class
fmov f20 f21
mov r12 r0
label c06_next_class
add r0 1
cmp r0 3
jlt c06_class
store64 8150000000012000016 r12
ret

label c06_train
load64 r11 8150000000012000008
cmp r11 0
jlt c06_bad_label
cmp r11 3
jge c06_bad_label
call c06_predict
load64 r0 8150000000012000000
add r0 1
store64 8150000000012000000 r0
cmp r12 r11
je c06_train_done
load64 r0 8150000000012000024
add r0 1
store64 8150000000012000024 r0
set r1 0
label c06_update
mov r2 r1
mul r2 8
add r2 8150000000012000256
fload f0 $r2
fmul f0 0.15
mov r3 r11
mul r3 8
add r3 r1
mul r3 8
add r3 8150000000012001024
fload f1 $r3
fadd f1 f0
fstore $r3 f1
mov r4 r12
mul r4 8
add r4 r1
mul r4 8
add r4 8150000000012001024
fload f2 $r4
fsub f2 f0
fstore $r4 f2
add r1 1
cmp r1 8
jlt c06_update
label c06_train_done
ret
label c06_bad_label
store64 8150000000012000000 -1
ret
