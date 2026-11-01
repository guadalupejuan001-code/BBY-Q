#!reverse-pc-machine-v1
# C05: entrelazamiento real Bell H/CX, paridad ZZ, coherencia XX, deshacer todo.
load8 r0 8100000000000000000
cmp r0 81
jne invalid
load8 r0 8100000000000004000
cmp r0 87
jne invalid
load8 r0 8100000000000004003
cmp r0 1
jne invalid
load8 r8 8100000000000004002
cmp r8 7
jgt invalid
load8 r9 8100000000000004700
load8 r10 8100000000000004701
cmp r9 1
jgt invalid
cmp r10 1
jgt invalid
mov r14 r8
mul r14 2
add r14 8100000000000000100
load8 r7 $r14
add r14 1
load8 r11 $r14
mul r11 256
add r7 r11
sub r7 10000
mov r11 r9
add r11 r10
mod r11 2
mov r15 r11
mul r15 2
set r13 1
sub r13 r15
mul r13 r7
set r12 10000
sub r12 r13
div r12 2
set r13 0
cmp r12 5000
jlt predicted
set r13 1
label predicted
print r8
print r12
print r13
print r11
cmp r9 1
jne skip_x0
x 2
label skip_x0
cmp r10 1
jne skip_x1
x 3
label skip_x1
h 2
cx 2 3
h 2
set r15 0
label forward_t
cmp r15 r8
jge forward_done
t 2
add r15 1
jmp forward_t
label forward_done
h 2
expect Z:2 Z:3
expect X:2 X:3
probz 2
probz 3
h 2
set r15 0
label backward_t
cmp r15 r8
jge reverse_done
tdg 2
add r15 1
jmp backward_t
label reverse_done
h 2
cx 2 3
h 2
cmp r10 1
jne reset_x1
x 3
label reset_x1
cmp r9 1
jne reset_x0
x 2
label reset_x0
probz 2
probz 3
halt
label invalid
div r0 0
