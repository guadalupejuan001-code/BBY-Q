label c26_finish
load8 r0 8800000000000000000
cmp r0 1
jne c26_clear
store8 8800000000000000000 2
load8 r6 8800000000000000002
set r0 0
label c26_second_copy
cmp r0 r6
jge c26_second_ready
set r7 8800000000000000128
add r7 r0
load8 r3 $r7
set r7 7400000000000000128
add r7 r0
store8 $r7 r3
add r0 1
jmp c26_second_copy
label c26_second_ready
store8 7400000000000000017 r6
store8 7400000000000000016 1
set r14 32
print r14
jmp c26_base_entry
label c26_clear
set r0 0
label c26_clear_byte
set r7 8800000000000000000
add r7 r0
store8 $r7 0
add r0 1
cmp r0 512
jlt c26_clear_byte
halt
