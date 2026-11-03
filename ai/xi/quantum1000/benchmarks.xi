# Benchmark environment, separate from agent logic. Synthetic structured
# tasks; labels are exposed only through the supervised training interface.
# Task at control+272: 0 linear, 1 XOR signs, 2 radial, 3 dense signal.
# Noise at control+296; new RNG seed is supplied per example by the test.
label vqc_sample
set r11 0
label sample_latents
call random_uniform
fmul f30 2
fsub f30 1
mov r0 r11
mul r0 8
add r0 8140000000000000600
fstore $r0 f30
add r11 1
cmp r11 4
jlt sample_latents
fload f24 8140000000000000600
fload f25 8140000000000000608
load64 r0 8140000000000000272
cmp r0 1
je label_xor
cmp r0 2
je label_radial
fmul f25 0.5
fadd f24 f25
jmp label_threshold
label label_xor
fmul f24 f25
fmul f24 -1
jmp label_threshold
label label_radial
fmul f24 f24
fmul f25 f25
fadd f24 f25
fsub f24 0.6
label label_threshold
fset f26 0
fcmp f24 0
jlt label_stored
fset f26 1
label label_stored
fstore 8140000000000000128 f26
fset f24 0
set r2 0
label sample_features
load64 r0 8140000000000000272
cmp r0 3
je independent_feature
mov r0 r2
mod r0 4
mul r0 8
add r0 8140000000000000600
fload f0 $r0
jmp feature_ready
label independent_feature
call random_uniform
fmov f0 f30
fmul f0 2
fsub f0 1
fmov f1 f0
mov r0 r2
mod r0 7
cmp r0 3
jlt dense_sign
fmul f1 -1
label dense_sign
fadd f24 f1
label feature_ready
fmul f0 1.1
fadd f0 1.2
call random_uniform
fsub f30 0.5
fload f1 8140000000000000296
fmul f30 f1
fadd f0 f30
mov r0 r2
mul r0 8
add r0 8140000000000300000
fstore $r0 f0
add r2 1
cmp r2 1000
jlt sample_features
load64 r0 8140000000000000272
cmp r0 3
jne sample_done
fset f26 0
fcmp f24 0
jlt dense_label
fset f26 1
label dense_label
fstore 8140000000000000128 f26
label sample_done
ret
