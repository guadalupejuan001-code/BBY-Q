#!reverse-pc-machine-v1
# C06: politica secuencial aprendida y circuito de dos cubits Bell; no entrena.
load8 r0 8100000000000005000
cmp r0 83
jne invalid
load8 r0 8100000000000005004
cmp r0 1
jne invalid
load8 r9 8100000000000005005
load8 r10 8100000000000005006
cmp r9 1
jgt invalid
cmp r10 1
jgt invalid
# Seleccion etapa 0
mov r7 r9
mul r7 8
mov r8 r10
mul r8 2
add r7 r8
mul r7 2
add r7 8100000000000005100
load8 r11 $r7
add r7 1
load8 r12 $r7
mul r12 256
add r11 r12
add r7 1
load8 r12 $r7
add r7 1
load8 r15 $r7
mul r15 256
add r12 r15
set r13 0
cmp r12 r11
jle step0_chosen
set r13 1
label step0_chosen
mov r5 r10
add r5 r13
mod r5 2
# Seleccion etapa 1 dada la paridad alcanzada
mov r7 r9
mul r7 8
add r7 4
mov r8 r5
mul r8 2
add r7 r8
mul r7 2
add r7 8100000000000005100
load8 r11 $r7
add r7 1
load8 r12 $r7
mul r12 256
add r11 r12
add r7 1
load8 r12 $r7
add r7 1
load8 r15 $r7
mul r15 256
add r12 r15
set r14 0
cmp r12 r11
jle step1_chosen
set r14 1
label step1_chosen
mov r6 r5
add r6 r14
mod r6 2
set r7 0
cmp r6 r9
jne not_success
set r7 1
label not_success
print r13
print r5
print r14
print r6
print r7
# Acciones I/X sobre qubit 4 de par Bell 4,5.
cmp r10 1
jne initial_zero
x 5
label initial_zero
h 4
cx 4 5
cmp r13 1
jne after_step0
x 4
label after_step0
cmp r14 1
jne after_step1
x 4
label after_step1
expect Z:4 Z:5
expect X:4 X:5
probz 4
probz 5
# Deshacer ambas decisiones y Bell, sin medir ni contaminar el estado guardado.
cmp r14 1
jne undo_step1
x 4
label undo_step1
cmp r13 1
jne undo_step0
x 4
label undo_step0
cx 4 5
h 4
cmp r10 1
jne undo_initial
x 5
label undo_initial
probz 4
probz 5
halt
label invalid
div r0 0
