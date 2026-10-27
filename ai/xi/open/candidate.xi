#!reverse-pc-machine-v1
# Enumerate sparse registered edges, never all 65536 possible entity IDs.
# Return +224/226/228 S/P/O; +231 ready. Cursor +92 advances before return.
load8 r0 7800000000000000092
load8 r14 7800000000000000093
mul r14 256
add r0 r14
load8 r1 7400000000000000006
load8 r14 7400000000000000007
mul r14 256
add r1 r14
cmp r0 r1
jlt legacy
sub r0 r1
load8 r1 7800000000000000008
load8 r14 7800000000000000009
mul r14 256
add r1 r14
cmp r0 r1
jge done
set r7 7800000000000200000
mul r0 6
add r7 r0
mov r15 r7
load8 r2 $r15
add r15 1
load8 r14 $r15
mul r14 256
add r2 r14
add r7 2
mov r15 r7
load8 r3 $r15
add r15 1
load8 r14 $r15
mul r14 256
add r3 r14
add r7 2
mov r15 r7
load8 r4 $r15
add r15 1
load8 r14 $r15
mul r14 256
add r4 r14
jmp ready
label legacy
set r7 7400000000000080000
mul r0 3
add r7 r0
load8 r2 $r7
add r7 1
load8 r3 $r7
add r7 1
load8 r4 $r7
label ready
mov r14 r2
mod r14 256
store8 7800000000000000224 r14
mov r14 r2
div r14 256
store8 7800000000000000225 r14
mov r14 r3
mod r14 256
store8 7800000000000000226 r14
mov r14 r3
div r14 256
store8 7800000000000000227 r14
mov r14 r4
mod r14 256
store8 7800000000000000228 r14
mov r14 r4
div r14 256
store8 7800000000000000229 r14
load8 r0 7800000000000000092
load8 r14 7800000000000000093
mul r14 256
add r0 r14
add r0 1
mov r14 r0
mod r14 256
store8 7800000000000000092 r14
mov r14 r0
div r14 256
store8 7800000000000000093 r14
store8 7800000000000000231 1
halt
label done
store8 7800000000000000231 0
halt
