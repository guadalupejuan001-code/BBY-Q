#!reverse-pc-machine-v1
# E006 sealed model inference: relation scores contribute ONLY after jury.
# Four sign-pair probes in canonical order: --, -+, +-, ++.
load8 r12 7000000000000000002
cmp r12 6
je schema_ok
div r12 0
label schema_ok
load8 r5 7000000000000000064
sub r5 128
load8 r6 7000000000000000065
sub r6 128
load8 r7 7000000000000000066
sub r7 128
load8 r9 7000000000000000031
set r0 1
label next_sign_pair
set r2 -1
cmp r0 3
jlt x_done
set r2 1
label x_done
set r3 -1
mov r11 r0
mod r11 2
cmp r11 1
je p_done
set r3 1
label p_done
mov r4 r0
mov r8 r5
mov r11 r6
mul r11 r2
add r8 r11
mov r11 r7
mul r11 r3
add r8 r11
cmp r9 1
jne no_promotion
set r12 0
label inspect_live_relations
set r13 7000000000000000200
add r13 r12
load8 r14 $r13
cmp r14 r4
jne no_relation
set r13 7000000000000000220
add r13 r12
load8 r14 $r13
sub r14 128
add r8 r14
label no_relation
add r12 1
cmp r12 4
jlt inspect_live_relations
label no_promotion
set r10 0
cmp r8 0
jlt predicted
set r10 1
label predicted
print r10
add r0 1
cmp r0 5
jlt next_sign_pair
mem_stats
