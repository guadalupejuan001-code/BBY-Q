#!reverse-pc-machine-v1
# C03 Aprendizaje por refuerzo: contextual bandit (gamma=0), recompensa exacta Q10000.
# Acciones: k puertas T dentro de H*T^k*H (Rx(k*pi/4) hasta fase global).
# Cada llamada hace 4 pasadas exploratorias, Q := Q+(R-Q)/2; 2 objetivos.
# Se usa simulacion matematica tabulada dentro de XI, no medidas cuanticas como feedback.
load8 r0 8100000000000000000
cmp r0 81
jne invalid
load8 r0 8100000000000002000
cmp r0 82
jne invalid
load8 r13 8100000000000002001
cmp r13 255
jge invalid
load8 r6 8100000000000002002
cmp r6 255
jgt invalid
set r15 0
label epoch
set r0 0
label context
set r1 0
label action
mov r2 r1
mul r2 2
add r2 8100000000000000100
load8 r3 $r2
add r2 1
load8 r4 $r2
mul r4 256
add r3 r4
sub r3 10000
set r4 10000
cmp r0 0
je target_zero
sub r4 r3
jmp fidelity_ready
label target_zero
add r4 r3
label fidelity_ready
div r4 2
add r4 2000
mov r5 r1
mul r5 r6
sub r4 r5
# direccion q-table: base+16*contexto+2*k
mov r7 r0
mul r7 16
mov r8 r1
mul r8 2
add r7 r8
add r7 8100000000000002100
load8 r9 $r7
add r7 1
load8 r10 $r7
mul r10 256
add r9 r10
mov r11 r4
sub r11 r9
div r11 2
add r9 r11
mov r12 r9
mod r12 256
sub r7 1
store8 $r7 r12
add r7 1
mov r12 r9
div r12 256
store8 $r7 r12
add r1 1
cmp r1 8
jlt action
add r0 1
cmp r0 2
jlt context
add r15 1
cmp r15 4
jlt epoch
# Explotacion de Q para cada contexto; desempate a k mas bajo.
set r0 0
label select_context
set r1 0
set r3 -1
set r4 0
label select_action
mov r7 r0
mul r7 16
mov r8 r1
mul r8 2
add r7 r8
add r7 8100000000000002100
load8 r9 $r7
add r7 1
load8 r10 $r7
mul r10 256
add r9 r10
cmp r9 r3
jle keep_best
mov r3 r9
mov r4 r1
label keep_best
add r1 1
cmp r1 8
jlt select_action
cmp r0 0
jne save_best_one
store8 8100000000000002005 r4
jmp best_saved
label save_best_one
store8 8100000000000002006 r4
label best_saved
add r0 1
cmp r0 2
jlt select_context
load8 r13 8100000000000002001
add r13 1
store8 8100000000000002001 r13
store8 8100000000000002004 1
load8 r14 8100000000000002005
load8 r15 8100000000000002006
print r14
print r15
print r13
halt
label invalid
div r0 0
