#!reverse-pc-machine-v1
# Append a validated inferred answer; preserve one proof reference only when
# there is exactly one answer. Multiple answers never receive a misleading
# single path presented as if it explained every clause.
load8 r2 7800000000000000096
load8 r14 7800000000000000097
mul r14 256
add r2 r14
load8 r3 7800000000000000082
set r0 0
label duplicate
cmp r0 r3
jge append
set r7 7800000000008300000
mov r1 r0
mul r1 2
add r7 r1
mov r15 r7
load8 r1 $r15
add r15 1
load8 r14 $r15
mul r14 256
add r1 r14
cmp r1 r2
je done
add r0 1
jmp duplicate
label append
cmp r3 8
jge limit
set r7 7800000000008300000
mov r1 r3
mul r1 2
add r7 r1
mov r15 r7
mov r14 r2
mod r14 256
store8 $r15 r14
add r15 1
mov r14 r2
div r14 256
store8 $r15 r14
add r3 1
store8 7800000000000000082 r3
store8 7800000000000000080 1
cmp r3 1
jne done
store8 7800000000000000136 1
mov r14 r2
mod r14 256
store8 7800000000000000132 r14
mov r14 r2
div r14 256
store8 7800000000000000133 r14
load8 r0 7800000000000000135
cmp r0 1
je transitive
load8 r0 7800000000000000122
store8 7800000000000000130 r0
store8 7800000000000000131 1
halt
label transitive
# bfs-accept placed the new node at queue_count-1.
load8 r0 7800000000000000120
sub r0 1
store8 7800000000000000130 r0
store8 7800000000000000131 0
halt
label limit
store8 7800000000000000080 9
label done
halt
