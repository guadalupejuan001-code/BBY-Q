#!reverse-pc-machine-v1
# Read-only response: learned ES/EN number names, otherwise composed digits.
load8 r0 7300000000000000002
cmp r0 1
jne invalid
load8 r0 7300000000000000008
cmp r0 1
je supported
set r14 63
print r14
halt
label supported
load8 r2 7300000000000000010
load8 r0 7300000000000000011
mul r0 256
add r2 r0
load8 r15 7300000000000000003
cmp r15 1
je language_ready
cmp r15 2
jne invalid
label language_ready
load8 r7 7200000000000000010
set r0 0
label find_learned_name
cmp r0 r7
jge decimal_output
set r8 7200000000000001000
mov r9 r0
mul r9 32
add r8 r9
load8 r9 $r8
cmp r9 4
jne next_numeral
mov r9 r8
add r9 1
load8 r9 $r9
cmp r9 r2
jne next_numeral
mov r9 r8
add r9 4
load8 r9 $r9
cmp r9 2
jlt next_numeral
set r5 5
cmp r15 1
je select_label
set r5 14
label select_label
add r8 r5
load8 r6 $r8
cmp r6 1
jlt invalid
cmp r6 8
jgt invalid
set r1 0
label emit_label
cmp r1 r6
jge done
mov r9 r8
add r9 1
add r9 r1
load8 r14 $r9
print r14
add r1 1
jmp emit_label
label next_numeral
add r0 1
jmp find_learned_name
label decimal_output
set r3 10000
set r4 0
label decimal_digit
mov r14 r2
div r14 r3
mod r2 r3
cmp r14 0
jne nonzero_digit
cmp r4 1
je print_digit
cmp r3 1
je print_digit
jmp next_place
label nonzero_digit
set r4 1
label print_digit
add r14 48
print r14
label next_place
div r3 10
cmp r3 0
jgt decimal_digit
label done
halt
label invalid
div r0 0
