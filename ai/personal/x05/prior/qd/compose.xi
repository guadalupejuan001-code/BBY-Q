#!reverse-pc-machine-v1
# ReverseCoding XI source emitter: opcode and digits are selected and printed by XI.
# Input at N: magic81, contract2, opcode1..5, A0..99, B0..99.
# Byte stream represents an executable four-statement XI program.
load8 r0 8430000000000000000
cmp r0 81
jne invalid
load8 r0 8430000000000000001
cmp r0 2
jne invalid
load8 r6 8430000000000000002
cmp r6 1
jlt invalid
cmp r6 5
jgt invalid
load8 r4 8430000000000000003
cmp r4 99
jgt invalid
load8 r5 8430000000000000004
cmp r5 99
jgt invalid
cmp r6 4
je divisor_test
cmp r6 5
jne initial
label divisor_test
cmp r5 0
je invalid
label initial
set r0 35
print r0
set r0 33
print r0
set r0 114
print r0
set r0 101
print r0
set r0 118
print r0
set r0 101
print r0
set r0 114
print r0
set r0 115
print r0
set r0 101
print r0
set r0 45
print r0
set r0 112
print r0
set r0 99
print r0
set r0 45
print r0
set r0 109
print r0
set r0 97
print r0
set r0 99
print r0
set r0 104
print r0
set r0 105
print r0
set r0 110
print r0
set r0 101
print r0
set r0 45
print r0
set r0 118
print r0
set r0 49
print r0
set r0 10
print r0
set r0 115
print r0
set r0 101
print r0
set r0 116
print r0
set r0 32
print r0
set r0 114
print r0
set r0 48
print r0
set r0 32
print r0
mov r0 r4
div r0 10
cmp r0 0
je first_digit
add r0 48
print r0
label first_digit
mov r0 r4
mod r0 10
add r0 48
print r0
set r0 10
print r0
cmp r6 1
je operation_add
cmp r6 2
je operation_sub
cmp r6 3
je operation_mul
cmp r6 4
je operation_div
cmp r6 5
je operation_mod
jmp invalid
label operation_add
set r0 97
print r0
set r0 100
print r0
set r0 100
print r0
jmp operation_end
label operation_sub
set r0 115
print r0
set r0 117
print r0
set r0 98
print r0
jmp operation_end
label operation_mul
set r0 109
print r0
set r0 117
print r0
set r0 108
print r0
jmp operation_end
label operation_div
set r0 100
print r0
set r0 105
print r0
set r0 118
print r0
jmp operation_end
label operation_mod
set r0 109
print r0
set r0 111
print r0
set r0 100
print r0
jmp operation_end
label operation_end
set r0 32
print r0
set r0 114
print r0
set r0 48
print r0
set r0 32
print r0
mov r0 r5
div r0 10
cmp r0 0
je second_digit
add r0 48
print r0
label second_digit
mov r0 r5
mod r0 10
add r0 48
print r0
set r0 10
print r0
set r0 112
print r0
set r0 114
print r0
set r0 105
print r0
set r0 110
print r0
set r0 116
print r0
set r0 32
print r0
set r0 114
print r0
set r0 48
print r0
set r0 10
print r0
set r0 104
print r0
set r0 97
print r0
set r0 108
print r0
set r0 116
print r0
set r0 10
print r0
halt
label invalid
div r0 0
halt
