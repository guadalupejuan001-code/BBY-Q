#!reverse-pc-machine-v1
# Explorer: propose the direct route, or acquire a missing window first.
# The bounded search has two routes, at most two actions; it is not a model.
load8 r0 8300000000000000016
cmp r0 1
jne done
load8 r0 8300000000000000017
load8 r1 8300000000000000018
store8 8300000000000000033 1
store8 8300000000000000128 r0
store8 8300000000000000129 r1
store8 8300000000000000019 1
cmp r1 16
jlt choose
set r7 8300000000000000512
add r7 r1
load8 r2 $r7
cmp r2 0
je missing
cmp r0 10
jne choose
cmp r2 2
jne reject
label choose
cmp r1 15
je done
cmp r0 2
je prerequisite
cmp r0 4
je prerequisite
cmp r0 5
je prerequisite
cmp r0 10
jne done
label prerequisite
set r7 8200000000000000032
add r7 r1
load8 r2 $r7
cmp r2 0
jne done
store8 8300000000000000019 2
store8 8300000000000000128 1
store8 8300000000000000130 r0
store8 8300000000000000131 r1
jmp done
label missing
set r0 5
jmp fail
label reject
set r0 6
label fail
store8 8300000000000000033 2
store8 8300000000000000016 4
store8 8200000000000000064 0
store8 8200000000000000065 0
store8 8200000000000000067 r0
label done
halt
