#!reverse-pc-machine-v1
# Supervised English negative/base form of a shared predicate. No stemming or
# invented inflection. Unknown predicates can use a quoted negative clause.
load8 r2 7800000000000000312
load8 r14 7800000000000000313
mul r14 256
add r2 r14
load8 r0 7400000000000000040
cmp r0 0
jne invalid
load8 r0 7400000000000000032
cmp r0 1
jne invalid
load8 r0 7800000000000001024
load8 r14 7800000000000001025
mul r14 256
add r0 r14
cmp r0 r2
jne invalid
load8 r0 7800000000000001026
cmp r0 2
jne invalid
load8 r6 7400000000000000512
cmp r6 1
jlt invalid
cmp r6 32
jgt invalid
set r7 7800000000009000000
mul r2 34
add r7 r2
load8 r0 $r7
cmp r0 0
je write
cmp r0 r6
jne invalid
set r0 0
label compare
cmp r0 r6
jge done
mov r8 r7
add r8 1
add r8 r0
load8 r1 $r8
set r8 7400000000000000513
add r8 r0
load8 r2 $r8
cmp r1 r2
jne invalid
add r0 1
jmp compare
label write
store8 $r7 r6
set r0 0
label copy
cmp r0 r6
jge done
set r8 7400000000000000513
add r8 r0
load8 r1 $r8
mov r8 r7
add r8 1
add r8 r0
store8 $r8 r1
add r0 1
jmp copy
label done
halt
label invalid
div r0 0
