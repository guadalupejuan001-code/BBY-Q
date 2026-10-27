#!reverse-pc-machine-v1
# Intern only the variables of an already recognized explicit teaching act.
load8 r0 7800000000000000088
cmp r0 3
jge done
set r7 7800000000000000068
add r7 r0
load8 r1 $r7
sub r1 1
store8 7800000000000000164 r1
set r1 0
mov r14 r1
mod r14 256
store8 7800000000000000160 r14
mov r14 r1
div r14 256
store8 7800000000000000161 r14
set r1 1
cmp r0 1
jne kind_ready
set r1 2
label kind_ready
store8 7800000000000000162 r1
load8 r1 7400000000000000003
store8 7800000000000000163 r1
store8 7800000000000000087 1
halt
label done
store8 7800000000000000087 0
halt
