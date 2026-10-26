#!reverse-pc-machine-v1
# Evaluate new compositions using ONLY grounded quantities and learned effects.
# Grammar: NUMBER (OP NUMBER)*; OP NUMBER... may continue the last valid turn.
# Designed left-to-right grammar, 0..65535 at EVERY step, max seven effects.
load8 r0 7300000000000000002
cmp r0 1
jne invalid
load8 r0 7300000000000000016
cmp r0 1
jne invalid
load8 r0 7300000000000000024
cmp r0 0
jne invalid
set r14 0
set r13 0
load8 r0 7300000000000000040
cmp r0 0
jne syntax_error
load8 r15 7300000000000000032
cmp r15 1
jlt syntax_error
load8 r0 7300000000000000800
cmp r0 1
je explicit_start
cmp r0 2
jne unknown_word
load8 r0 7300000000000000005
cmp r0 1
jne missing_context
load8 r2 7300000000000000006
load8 r3 7300000000000000007
mul r3 256
add r2 r3
set r1 0
jmp apply_pairs
label explicit_start
load8 r2 7300000000000000801
load8 r3 7300000000000000802
mul r3 256
add r2 r3
set r1 1
label apply_pairs
cmp r1 r15
jge supported
mov r0 r1
add r0 1
cmp r0 r15
jge syntax_error
set r7 7300000000000000800
mov r8 r1
mul r8 4
add r7 r8
load8 r0 $r7
cmp r0 2
jne unknown_word
add r7 1
load8 r4 $r7
add r7 3
load8 r0 $r7
cmp r0 1
jne unknown_word
add r7 1
load8 r3 $r7
add r7 1
load8 r0 $r7
mul r0 256
add r3 r0
cmp r4 1
je subtract
cmp r4 2
jne unknown_word
add r2 r3
jmp check_bounds
label subtract
sub r2 r3
label check_bounds
cmp r2 0
jlt range_error
cmp r2 65535
jgt range_error
add r13 1
add r1 2
jmp apply_pairs
label supported
store8 7300000000000000005 1
store8 7300000000000000008 1
store8 7300000000000000009 0
store8 7300000000000000012 r13
mov r3 r2
mod r3 256
store8 7300000000000000006 r3
store8 7300000000000000010 r3
div r2 256
store8 7300000000000000007 r2
store8 7300000000000000011 r2
jmp clean
label unknown_word
set r14 1
jmp abstain
label syntax_error
set r14 2
jmp abstain
label missing_context
set r14 3
jmp abstain
label range_error
set r14 4
label abstain
# Failed turns invalidate context: never silently reuse a stale answer.
store8 7300000000000000005 0
store8 7300000000000000006 0
store8 7300000000000000007 0
store8 7300000000000000008 0
store8 7300000000000000009 r14
store8 7300000000000000010 0
store8 7300000000000000011 0
store8 7300000000000000012 0
label clean
set r0 16
label clear_query
set r7 7300000000000000000
add r7 r0
store8 $r7 0
add r0 1
cmp r0 864
jlt clear_query
load8 r10 7300000000000000008
print r10
load8 r11 7300000000000000009
print r11
halt
label invalid
div r0 0
