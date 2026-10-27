#!reverse-pc-machine-v1
# +67 route: 0 original E016;1 intern statement;2 query;3 alias;4 retract;5 act.
load8 r0 7800000000000000063
cmp r0 0
je done
load8 r0 7800000000000000065
cmp r0 1
je ambiguous
load8 r0 7800000000000000064
cmp r0 5
je explain
store8 7800000000000000012 0
cmp r0 0
je done
# Resolve semantic labels from selected token positions, not host text parsing.
set r1 0
label role
cmp r1 3
jge dispatch
set r7 7800000000000000068
add r7 r1
load8 r2 $r7
set r3 0
cmp r2 0
je role_ready
sub r2 1
mul r2 4
set r7 7800000000000001024
add r7 r2
mov r15 r7
load8 r3 $r15
add r15 1
load8 r14 $r15
mul r14 256
add r3 r14
label role_ready
set r7 7800000000000000072
mov r2 r1
mul r2 2
add r7 r2
mov r15 r7
mov r14 r3
mod r14 256
store8 $r15 r14
add r15 1
mov r14 r3
div r14 256
store8 $r15 r14
add r1 1
jmp role
label dispatch
load8 r0 7800000000000000064
cmp r0 8
je definition
cmp r0 1
je property
cmp r0 2
je query
load8 r1 7400000000000000047
cmp r1 0
jne unsupported
cmp r0 3
je teach
cmp r0 4
je teach
cmp r0 6
je alias
cmp r0 7
je retract
jmp unsupported
label definition
load8 r0 7800000000000000032
load8 r14 7800000000000000033
mul r14 256
add r0 r14
mov r14 r0
mod r14 256
store8 7800000000000000074 r14
mov r14 r0
div r14 256
store8 7800000000000000075 r14
jmp property
label property
store8 7800000000000000090 1
jmp query_ready
label query
store8 7800000000000000090 2
label query_ready
store8 7800000000000000067 2
halt
label teach
# Conservative preflight prevents partially learned names at a full graph.
load8 r0 7800000000000000008
load8 r14 7800000000000000009
mul r14 256
add r0 r14
cmp r0 1024
jge limit
load8 r0 7800000000000000006
load8 r14 7800000000000000007
mul r14 256
add r0 r14
cmp r0 2045
jgt limit
load8 r0 7800000000000000004
load8 r14 7800000000000000005
mul r14 256
add r0 r14
cmp r0 65532
jgt limit
store8 7800000000000000067 1
halt
label alias
load8 r0 7800000000000000072
load8 r14 7800000000000000073
mul r14 256
add r0 r14
cmp r0 0
je unsupported
store8 7800000000000000067 3
halt
label retract
load8 r0 7800000000000000072
load8 r14 7800000000000000073
mul r14 256
add r0 r14
load8 r1 7800000000000000074
load8 r14 7800000000000000075
mul r14 256
add r1 r14
mul r0 r1
load8 r1 7800000000000000076
load8 r14 7800000000000000077
mul r14 256
add r1 r14
mul r0 r1
cmp r0 0
je unsupported
store8 7800000000000000067 4
halt
label explain
store8 7800000000000000085 1
load8 r0 7800000000000000068
cmp r0 0
jne explicit_explanation
load8 r0 7800000000000000012
cmp r0 1
jne clarify
load8 r0 7800000000000000013
store8 7800000000000000090 r0
load8 r0 7800000000000000014
load8 r14 7800000000000000015
mul r14 256
add r0 r14
mov r14 r0
mod r14 256
store8 7800000000000000072 r14
mov r14 r0
div r14 256
store8 7800000000000000073 r14
load8 r0 7800000000000000016
load8 r14 7800000000000000017
mul r14 256
add r0 r14
mov r14 r0
mod r14 256
store8 7800000000000000074 r14
mov r14 r0
div r14 256
store8 7800000000000000075 r14
load8 r0 7800000000000000018
load8 r14 7800000000000000019
mul r14 256
add r0 r14
mov r14 r0
mod r14 256
store8 7800000000000000076 r14
mov r14 r0
div r14 256
store8 7800000000000000077 r14
store8 7800000000000000067 2
halt
label explicit_explanation
store8 7800000000000000012 0
set r1 0
label explanation_role
cmp r1 3
jge explicit_ready
set r7 7800000000000000068
add r7 r1
load8 r2 $r7
sub r2 1
mul r2 4
set r7 7800000000000001024
add r7 r2
mov r15 r7
load8 r3 $r15
add r15 1
load8 r14 $r15
mul r14 256
add r3 r14
set r7 7800000000000000072
mov r2 r1
mul r2 2
add r7 r2
mov r15 r7
mov r14 r3
mod r14 256
store8 $r15 r14
add r15 1
mov r14 r3
div r14 256
store8 $r15 r14
add r1 1
jmp explanation_role
label explicit_ready
store8 7800000000000000090 2
store8 7800000000000000067 2
halt
label unsupported
store8 7800000000000000080 3
jmp act
label clarify
store8 7800000000000000080 8
jmp act
label ambiguous
store8 7800000000000000012 0
store8 7800000000000000080 10
jmp act
label limit
store8 7800000000000000080 9
label act
store8 7800000000000000067 5
label done
halt
