#!reverse-pc-machine-v1
# Read-only E011 invariants. All earlier regions are independently compared
# bytewise by the examiner, not merely checked for presence.
load8 r0 7300000000000000000
cmp r0 68
jne invalid
load8 r0 7300000000000000001
cmp r0 76
jne invalid
load8 r0 7300000000000000002
cmp r0 1
jne invalid
load8 r0 7300000000000000003
cmp r0 1
je valid_language
cmp r0 2
jne invalid
label valid_language
load8 r15 7300000000000000004
cmp r15 32
jgt invalid
set r0 0
label each_operator
cmp r0 r15
jge check_intake
set r7 7300000000000001000
mov r8 r0
mul r8 32
add r7 r8
load8 r2 $r7
cmp r2 1
jlt invalid
cmp r2 16
jgt invalid
mov r8 r7
add r8 17
load8 r9 $r8
cmp r9 1
je effect_valid
cmp r9 2
jne invalid
label effect_valid
add r8 1
load8 r9 $r8
cmp r9 1
jlt invalid
cmp r9 2
jgt invalid
set r1 0
label check_spelling
cmp r1 r2
jge next_operator
mov r8 r7
add r8 1
add r8 r1
load8 r9 $r8
cmp r9 97
jlt invalid
cmp r9 122
jgt invalid
add r1 1
jmp check_spelling
label next_operator
add r0 1
jmp each_operator
label check_intake
set r0 16
label intake_byte
set r7 7300000000000000000
add r7 r0
load8 r8 $r7
cmp r8 0
jne invalid
add r0 1
cmp r0 864
jlt intake_byte
print r15
mem_stats
stats
halt
label invalid
div r0 0
