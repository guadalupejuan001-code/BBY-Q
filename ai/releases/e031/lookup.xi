label lex_lookup
load8 r3 8700000000000000008
load8 r4 8700000000000000009
mul r4 256
add r3 r4
load8 r4 8700000000000000010
mul r4 65536
add r3 r4
cmp r0 r3
jne lex_missing
load8 r9 8700000000000000001
load8 r10 8700000000000000016
load8 r3 8700000000000000017
mul r3 256
add r10 r3
load8 r3 8700000000000000018
mul r3 65536
add r10 r3
set r0 0
label lex_record
cmp r0 r10
jge lex_missing
set r7 8700000000000001024
add r7 r0
load8 r11 $r7
add r7 1
load8 r3 $r7
mul r3 256
add r11 r3
add r7 1
load8 r12 $r7
add r7 1
load8 r3 $r7
mul r3 256
add r12 r3
add r7 1
load8 r3 $r7
mul r3 65536
add r12 r3
add r7 1
load8 r3 $r7
mul r3 16777216
add r12 r3
add r0 6
cmp r11 r9
jne lex_record_next
set r1 0
label lex_compare
cmp r1 r9
jge lex_emit_start
set r7 8700000000000001024
add r7 r0
add r7 r1
load8 r3 $r7
set r7 8700000000000000128
add r7 r1
load8 r4 $r7
cmp r3 r4
jne lex_record_next
add r1 1
jmp lex_compare
label lex_emit_start
add r0 r11
set r1 0
label lex_emit
cmp r1 r12
jge lex_finish
set r7 8700000000000001024
add r7 r0
add r7 r1
load8 r14 $r7
print r14
add r1 1
jmp lex_emit
label lex_record_next
add r0 r11
add r0 r12
jmp lex_record
label lex_missing
set r14 78
print r14
set r14 111
print r14
set r14 32
print r14
set r14 99
print r14
set r14 111
print r14
set r14 110
print r14
set r14 115
print r14
set r14 116
print r14
set r14 97
print r14
set r14 32
print r14
set r14 101
print r14
set r14 110
print r14
set r14 32
print r14
set r14 101
print r14
set r14 115
print r14
set r14 116
print r14
set r14 101
print r14
set r14 32
print r14
set r14 100
print r14
set r14 105
print r14
set r14 99
print r14
set r14 99
print r14
set r14 105
print r14
set r14 111
print r14
set r14 110
print r14
set r14 97
print r14
set r14 114
print r14
set r14 105
print r14
set r14 111
print r14
set r14 46
print r14
label lex_finish
set r0 0
label lex_clean
set r7 7400000000000000128
add r7 r0
store8 $r7 0
set r7 8700000000000000128
add r7 r0
store8 $r7 0
add r0 1
cmp r0 255
jlt lex_clean
store8 7400000000000000017 0
store8 7400000000000000016 0
store8 8700000000000000001 0
store8 8700000000000000002 0
halt
