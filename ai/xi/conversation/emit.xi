#!reverse-pc-machine-v1
# Print selected memory bytes, including Spanish UTF-8 initial capitalization.
# No words, facts or response choice in the transport.
cmp r6 1
jlt invalid
cmp r6 255
jgt invalid
load8 r0 7700000000000000039
cmp r0 1
jne begin
set r14 32
print r14
label begin
set r3 0
label letter
cmp r3 r6
jge done
mov r4 r7
add r4 r3
load8 r14 $r4
cmp r14 95
jne case_check
set r14 32
label case_check
cmp r13 0
je print_byte
cmp r14 195
je print_byte
cmp r3 0
jne latin_initial
cmp r14 97
jlt case_done
cmp r14 122
jgt case_done
sub r14 32
jmp case_done
label latin_initial
cmp r3 1
jne case_done
load8 r0 $r7
cmp r0 195
jne case_done
cmp r14 160
jlt case_done
cmp r14 191
jgt case_done
cmp r14 183
je case_done
sub r14 32
label case_done
set r13 0
label print_byte
print r14
add r3 1
jmp letter
label done
store8 7700000000000000039 1
store8 7700000000000000038 0
halt
label invalid
div r0 0
