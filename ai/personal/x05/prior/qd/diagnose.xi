#!reverse-pc-machine-v1
# Qd/Cody cycle 02. Single-fault symbolic diagnostic in XI/Ether.
# Run ONLY on an initialized disposable RVPC2. Typed inputs D=8420...:
# +0 magic 81, +1 contract 1, +2 expected skill (1 add,2 sub,3 mul,4 mod),
# +3 observed op (1..5 incl div), +4 arithmetic destination register,
# +5 initial set destination, +6 print count (0..1),
# +7 print register or 255 when absent, +8 set-before-operation (0/1),
# +9 RHS token (1 a, 2 b, 3 literal zero).
# Outputs: status (0 clean, 1 one repair, 2 multiple faults, 3 bad input),
# patch kind (1 op, 2 dest, 3 print register, 4 insert print,
# 5 swap set/op, 6 set register, 7 RHS), patch argument.
# No persistent writes, no training examples, no external model.
load8 r0 8420000000000000000
cmp r0 81
jne invalid
load8 r0 8420000000000000001
cmp r0 1
jne invalid
load8 r1 8420000000000000002
cmp r1 1
jlt invalid
cmp r1 4
jgt invalid
load8 r2 8420000000000000003
cmp r2 1
jlt invalid
cmp r2 5
jgt invalid
load8 r3 8420000000000000004
cmp r3 3
jgt invalid
load8 r4 8420000000000000005
cmp r4 3
jgt invalid
load8 r5 8420000000000000006
cmp r5 1
jgt invalid
load8 r6 8420000000000000007
cmp r5 0
je print_register_valid
cmp r6 3
jgt invalid
label print_register_valid
load8 r7 8420000000000000008
cmp r7 1
jgt invalid
load8 r8 8420000000000000009
cmp r8 1
jlt invalid
cmp r8 3
jgt invalid
set r9 0
set r10 0
set r11 0
cmp r1 r2
je operation_ok
add r9 1
set r10 1
mov r11 r1
label operation_ok
cmp r3 0
je arithmetic_destination_ok
add r9 1
set r10 2
set r11 0
label arithmetic_destination_ok
cmp r4 0
je initial_destination_ok
add r9 1
set r10 6
set r11 0
label initial_destination_ok
cmp r5 0
jne output_present
add r9 1
set r10 4
set r11 0
jmp output_ok
label output_present
cmp r6 0
je output_ok
add r9 1
set r10 3
set r11 0
label output_ok
cmp r7 1
je order_ok
add r9 1
set r10 5
set r11 0
label order_ok
cmp r8 2
je operand_ok
add r9 1
set r10 7
set r11 0
label operand_ok
set r0 0
cmp r9 0
je emit
cmp r9 1
je repairable
set r0 2
set r10 0
set r11 0
jmp emit
label repairable
set r0 1
label emit
print r0
mov r0 r10
print r0
mov r0 r11
print r0
halt
label invalid
set r0 3
set r10 0
set r11 0
jmp emit
