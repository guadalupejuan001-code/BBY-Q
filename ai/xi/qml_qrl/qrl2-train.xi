#!reverse-pc-machine-v1
# C06: TD tabular por barridos de transiciones. Recompensa final; gamma=0.9.
# Cada Q(t,objetivo,paridad,accion) actualiza a mitad de su objetivo de Bellman.
# En XI: accion 0=I, 1=X; paridad siguiente = paridad XOR accion.
load8 r0 8100000000000005000
cmp r0 83
jne invalid
load8 r0 8100000000000005001
cmp r0 255
jge invalid
load8 r0 8100000000000005002
cmp r0 40
jne invalid
load8 r0 8100000000000005003
cmp r0 9
jne invalid
set r13 0
label pass
set r0 0
label target
set r1 1
label stage
set r2 0
label state
set r3 0
label action
mov r5 r2
add r5 r3
mod r5 2
set r6 100
mov r7 r3
mul r7 40
sub r6 r7
cmp r1 1
jne bootstrap
cmp r5 r0
jne target_ready
add r6 10000
jmp target_ready
label bootstrap
mov r7 r0
mul r7 8
add r7 4
mov r8 r5
mul r8 2
add r7 r8
mul r7 2
add r7 8100000000000005100
load8 r9 $r7
add r7 1
load8 r10 $r7
mul r10 256
add r9 r10
add r7 1
load8 r10 $r7
add r7 1
load8 r11 $r7
mul r11 256
add r10 r11
cmp r10 r9
jle best_ready
mov r9 r10
label best_ready
mul r9 9
div r9 10
add r6 r9
label target_ready
mov r7 r0
mul r7 8
mov r8 r1
mul r8 4
add r7 r8
mov r8 r2
mul r8 2
add r7 r8
add r7 r3
mul r7 2
add r7 8100000000000005100
load8 r9 $r7
add r7 1
load8 r10 $r7
mul r10 256
add r9 r10
mov r12 r6
sub r12 r9
div r12 2
add r9 r12
mov r12 r9
mod r12 256
sub r7 1
store8 $r7 r12
add r7 1
mov r12 r9
div r12 256
store8 $r7 r12
add r3 1
cmp r3 2
jlt action
add r2 1
cmp r2 2
jlt state
sub r1 1
cmp r1 0
jge stage
add r0 1
cmp r0 2
jlt target
add r13 1
cmp r13 16
jlt pass
load8 r0 8100000000000005001
add r0 1
store8 8100000000000005001 r0
store8 8100000000000005004 1
print r0
halt
label invalid
div r0 0
