#!reverse-pc-machine-v1
# E010 blind evaluation: expected slot is supplied ONLY AFTER recognize.xi.
# Its input cannot be read by the classifier. Score the user's own XI state.
load8 r12 7200000000000000000
cmp r12 83
je schema_ok
div r12 0
label schema_ok
load8 r12 7200000000000000300
cmp r12 1
je grade_ready
div r12 0
label grade_ready
load8 r6 7200000000000000203
cmp r6 1
jge domain_lower
div r6 0
label domain_lower
cmp r6 4
jle domain_upper
div r6 0
label domain_upper
load8 r7 7200000000000000301
cmp r7 0
je unknown_expected
load8 r8 7200000000000000010
cmp r7 r8
jle valid_expected_slot
div r7 0
label valid_expected_slot
set r9 7200000000000001000
mov r10 r7
sub r10 1
mul r10 32
add r9 r10
load8 r11 $r9
cmp r11 r6
je same_category
div r11 0
label same_category
label unknown_expected
mov r8 r6
sub r8 1
set r9 7200000000000000040
add r9 r8
load8 r10 $r9
cmp r10 240
jlt tests_bounded
div r10 0
label tests_bounded
add r10 1
store8 $r9 r10
set r11 0
load8 r12 7200000000000000200
cmp r12 r7
jne classification_wrong
set r11 1
set r9 7200000000000000050
add r9 r8
load8 r10 $r9
add r10 1
store8 $r9 r10
label classification_wrong
store8 7200000000000000210 r11
store8 7200000000000000300 0
store8 7200000000000000301 0
print r11
print r6
mem_stats
