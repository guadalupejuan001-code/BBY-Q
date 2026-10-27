#!reverse-pc-machine-v1
store8 7700000000000000010 0
store8 7700000000000000039 0
store8 7700000000000000038 0
load8 r0 7800000000000000080
cmp r0 0
jne status
set r0 3
store8 7800000000000000080 3
label status
cmp r0 2
jle supported
store8 7800000000000000012 0
load8 r1 7800000000000000063
cmp r1 2
jne act
cmp r0 5
jlt compact_unknown
cmp r0 7
jgt compact_unknown
label act
cmp r0 5
je learn
cmp r0 6
je alias
cmp r0 7
je forget
cmp r0 3
je unknown
cmp r0 4
je conflict
cmp r0 8
je clarify
cmp r0 10
je ambiguous_act
cmp r0 11
je collision_act
set r0 7
jmp act_ready
label learn
set r0 1
jmp act_ready
label alias
set r0 2
jmp act_ready
label forget
set r0 3
jmp act_ready
label unknown
set r0 4
jmp act_ready
label conflict
set r0 5
jmp act_ready
label clarify
set r0 6
jmp act_ready
label ambiguous_act
set r0 11
jmp act_ready
label collision_act
set r0 12
label act_ready
store8 7800000000000000304 r0
store8 7800000000000000302 2
halt
label compact_unknown
set r14 63
print r14
store8 7800000000000000302 0
halt
label supported
store8 7800000000000000012 1
load8 r0 7800000000000000090
store8 7800000000000000013 r0
load8 r0 7800000000000000072
load8 r14 7800000000000000073
mul r14 256
add r0 r14
mov r14 r0
mod r14 256
store8 7800000000000000014 r14
mov r14 r0
div r14 256
store8 7800000000000000015 r14
load8 r0 7800000000000000074
load8 r14 7800000000000000075
mul r14 256
add r0 r14
mov r14 r0
mod r14 256
store8 7800000000000000016 r14
mov r14 r0
div r14 256
store8 7800000000000000017 r14
load8 r0 7800000000000000076
load8 r14 7800000000000000077
mul r14 256
add r0 r14
mov r14 r0
mod r14 256
store8 7800000000000000018 r14
mov r14 r0
div r14 256
store8 7800000000000000019 r14
load8 r0 7800000000000000080
cmp r0 2
jne output_mode
load8 r0 7400000000000000003
cmp r0 2
jne output_mode
load8 r0 7800000000000000074
load8 r14 7800000000000000075
mul r14 256
add r0 r14
load8 r1 7800000000000000032
load8 r14 7800000000000000033
mul r14 256
add r1 r14
cmp r0 r1
je output_mode
set r7 7800000000009000000
mul r0 34
add r7 r0
load8 r0 $r7
cmp r0 0
je quoted_negative
store8 7800000000000000139 1
jmp output_mode
label quoted_negative
store8 7800000000000000138 2
label output_mode
load8 r0 7800000000000000063
cmp r0 2
je compact
set r0 8
load8 r1 7800000000000000085
cmp r1 0
je prefix
set r0 9
label prefix
store8 7800000000000000304 r0
store8 7800000000000000302 3
halt
label compact
store8 7800000000000000302 1
halt
