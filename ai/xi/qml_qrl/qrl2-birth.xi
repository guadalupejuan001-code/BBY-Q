#!reverse-pc-machine-v1
# C06: MDP finito 2 pasos, contexto=objetivo+paso+paridad; 16 valores Q u16 Ether.
load8 r0 8100000000000000000
cmp r0 81
jne invalid
load8 r0 8100000000000005000
cmp r0 0
jne invalid
store8 8100000000000005000 83
store8 8100000000000005001 0
store8 8100000000000005002 40
store8 8100000000000005003 9
store8 8100000000000005004 0
store8 8100000000000005005 1
store8 8100000000000005006 0
set r1 0
label clear_table
mov r2 r1
mul r2 2
add r2 8100000000000005100
store8 $r2 0
add r2 1
store8 $r2 0
add r1 1
cmp r1 16
jlt clear_table
set r0 83
print r0
halt
label invalid
div r0 0
