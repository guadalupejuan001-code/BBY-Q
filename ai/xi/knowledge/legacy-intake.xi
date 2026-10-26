#!reverse-pc-machine-v1
# Adapt canonical tokens to the original E009 ask/speak without duplicating
# its lexicon or facts. Back up only transient query descriptors/counters.
set r0 0
label backup
set r7 7100000000000000140
add r7 r0
load8 r8 $r7
set r7 7400000000000004600
add r7 r0
store8 $r7 r8
add r0 1
cmp r0 57
jlt backup
set r0 0
label token
set r7 7400000000000000512
mov r1 r0
mul r1 34
add r7 r1
load8 r2 $r7
set r8 7100000000000000140
mov r1 r0
mul r1 10
add r8 r1
store8 $r8 r2
set r1 0
label letter
cmp r1 r2
jge next
mov r9 r7
add r9 1
add r9 r1
load8 r10 $r9
mov r9 r8
add r9 1
add r9 r1
store8 $r9 r10
add r1 1
jmp letter
label next
add r0 1
cmp r0 3
jlt token
store8 7100000000000000175 3
halt
