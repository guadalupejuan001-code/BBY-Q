#!reverse-pc-machine-v1
# C14 native XI semantic cue parser consumes only P01-native-normalized bytes.
# Input: P01 normalization N and intent P. Input memory reference: F+17 (0 or 1).
# Classes: 0 generic,1 memory,2 formal reasoning,3 composition,4 mixed,5 execution,6 explanation,7 guarded.
# Output F+16 semantic class; F+18 0..143 training context; prints intent,cue,context.
store8 8270000000000000016 0
store8 8270000000000000020 0
store8 8270000000000000021 0
store8 8270000000000000022 0
store8 8270000000000000023 0
load8 r9 9190000000000000136
cmp r9 0
jle c14_bad
cmp r9 190
jgt c14_bad
load8 r14 8270000000000000017
cmp r14 1
jgt c14_bad
cmp r9 6
jlt c14_next_0
set r0 0
label c14_match_0_seek
mov r8 r9
sub r8 6
cmp r0 r8
jgt c14_next_0
mov r7 r0
add r7 9190000000000001024
load8 r2 $r7
cmp r2 32
jne c14_match_0_advance
mov r7 r0
add r7 9190000000000001025
load8 r2 $r7
cmp r2 100
jne c14_match_0_advance
mov r7 r0
add r7 9190000000000001026
load8 r2 $r7
cmp r2 105
jne c14_match_0_advance
mov r7 r0
add r7 9190000000000001027
load8 r2 $r7
cmp r2 106
jne c14_match_0_advance
mov r7 r0
add r7 9190000000000001028
load8 r2 $r7
cmp r2 101
jne c14_match_0_advance
mov r7 r0
add r7 9190000000000001029
load8 r2 $r7
cmp r2 32
jne c14_match_0_advance
store8 8270000000000000020 1
jmp c14_next_0
label c14_match_0_advance
add r0 1
jmp c14_match_0_seek
label c14_next_0
cmp r9 9
jlt c14_next_1
set r0 0
label c14_match_1_seek
mov r8 r9
sub r8 9
cmp r0 r8
jgt c14_next_1
mov r7 r0
add r7 9190000000000001024
load8 r2 $r7
cmp r2 32
jne c14_match_1_advance
mov r7 r0
add r7 9190000000000001025
load8 r2 $r7
cmp r2 100
jne c14_match_1_advance
mov r7 r0
add r7 9190000000000001026
load8 r2 $r7
cmp r2 105
jne c14_match_1_advance
mov r7 r0
add r7 9190000000000001027
load8 r2 $r7
cmp r2 106
jne c14_match_1_advance
mov r7 r0
add r7 9190000000000001028
load8 r2 $r7
cmp r2 105
jne c14_match_1_advance
mov r7 r0
add r7 9190000000000001029
load8 r2 $r7
cmp r2 109
jne c14_match_1_advance
mov r7 r0
add r7 9190000000000001030
load8 r2 $r7
cmp r2 111
jne c14_match_1_advance
mov r7 r0
add r7 9190000000000001031
load8 r2 $r7
cmp r2 115
jne c14_match_1_advance
mov r7 r0
add r7 9190000000000001032
load8 r2 $r7
cmp r2 32
jne c14_match_1_advance
store8 8270000000000000020 1
jmp c14_next_1
label c14_match_1_advance
add r0 1
jmp c14_match_1_seek
label c14_next_1
cmp r9 10
jlt c14_next_2
set r0 0
label c14_match_2_seek
mov r8 r9
sub r8 10
cmp r0 r8
jgt c14_next_2
mov r7 r0
add r7 9190000000000001024
load8 r2 $r7
cmp r2 32
jne c14_match_2_advance
mov r7 r0
add r7 9190000000000001025
load8 r2 $r7
cmp r2 104
jne c14_match_2_advance
mov r7 r0
add r7 9190000000000001026
load8 r2 $r7
cmp r2 97
jne c14_match_2_advance
mov r7 r0
add r7 9190000000000001027
load8 r2 $r7
cmp r2 98
jne c14_match_2_advance
mov r7 r0
add r7 9190000000000001028
load8 r2 $r7
cmp r2 108
jne c14_match_2_advance
mov r7 r0
add r7 9190000000000001029
load8 r2 $r7
cmp r2 97
jne c14_match_2_advance
mov r7 r0
add r7 9190000000000001030
load8 r2 $r7
cmp r2 109
jne c14_match_2_advance
mov r7 r0
add r7 9190000000000001031
load8 r2 $r7
cmp r2 111
jne c14_match_2_advance
mov r7 r0
add r7 9190000000000001032
load8 r2 $r7
cmp r2 115
jne c14_match_2_advance
mov r7 r0
add r7 9190000000000001033
load8 r2 $r7
cmp r2 32
jne c14_match_2_advance
store8 8270000000000000020 1
jmp c14_next_2
label c14_match_2_advance
add r0 1
jmp c14_match_2_seek
label c14_next_2
cmp r9 14
jlt c14_next_3
set r0 0
label c14_match_3_seek
mov r8 r9
sub r8 14
cmp r0 r8
jgt c14_next_3
mov r7 r0
add r7 9190000000000001024
load8 r2 $r7
cmp r2 32
jne c14_match_3_advance
mov r7 r0
add r7 9190000000000001025
load8 r2 $r7
cmp r2 99
jne c14_match_3_advance
mov r7 r0
add r7 9190000000000001026
load8 r2 $r7
cmp r2 111
jne c14_match_3_advance
mov r7 r0
add r7 9190000000000001027
load8 r2 $r7
cmp r2 110
jne c14_match_3_advance
mov r7 r0
add r7 9190000000000001028
load8 r2 $r7
cmp r2 118
jne c14_match_3_advance
mov r7 r0
add r7 9190000000000001029
load8 r2 $r7
cmp r2 101
jne c14_match_3_advance
mov r7 r0
add r7 9190000000000001030
load8 r2 $r7
cmp r2 114
jne c14_match_3_advance
mov r7 r0
add r7 9190000000000001031
load8 r2 $r7
cmp r2 115
jne c14_match_3_advance
mov r7 r0
add r7 9190000000000001032
load8 r2 $r7
cmp r2 97
jne c14_match_3_advance
mov r7 r0
add r7 9190000000000001033
load8 r2 $r7
cmp r2 99
jne c14_match_3_advance
mov r7 r0
add r7 9190000000000001034
load8 r2 $r7
cmp r2 105
jne c14_match_3_advance
mov r7 r0
add r7 9190000000000001035
load8 r2 $r7
cmp r2 111
jne c14_match_3_advance
mov r7 r0
add r7 9190000000000001036
load8 r2 $r7
cmp r2 110
jne c14_match_3_advance
mov r7 r0
add r7 9190000000000001037
load8 r2 $r7
cmp r2 32
jne c14_match_3_advance
store8 8270000000000000020 1
jmp c14_next_3
label c14_match_3_advance
add r0 1
jmp c14_match_3_seek
label c14_next_3
cmp r9 11
jlt c14_next_4
set r0 0
label c14_match_4_seek
mov r8 r9
sub r8 11
cmp r0 r8
jgt c14_next_4
mov r7 r0
add r7 9190000000000001024
load8 r2 $r7
cmp r2 32
jne c14_match_4_advance
mov r7 r0
add r7 9190000000000001025
load8 r2 $r7
cmp r2 104
jne c14_match_4_advance
mov r7 r0
add r7 9190000000000001026
load8 r2 $r7
cmp r2 105
jne c14_match_4_advance
mov r7 r0
add r7 9190000000000001027
load8 r2 $r7
cmp r2 115
jne c14_match_4_advance
mov r7 r0
add r7 9190000000000001028
load8 r2 $r7
cmp r2 116
jne c14_match_4_advance
mov r7 r0
add r7 9190000000000001029
load8 r2 $r7
cmp r2 111
jne c14_match_4_advance
mov r7 r0
add r7 9190000000000001030
load8 r2 $r7
cmp r2 114
jne c14_match_4_advance
mov r7 r0
add r7 9190000000000001031
load8 r2 $r7
cmp r2 105
jne c14_match_4_advance
mov r7 r0
add r7 9190000000000001032
load8 r2 $r7
cmp r2 97
jne c14_match_4_advance
mov r7 r0
add r7 9190000000000001033
load8 r2 $r7
cmp r2 108
jne c14_match_4_advance
mov r7 r0
add r7 9190000000000001034
load8 r2 $r7
cmp r2 32
jne c14_match_4_advance
store8 8270000000000000020 1
jmp c14_next_4
label c14_match_4_advance
add r0 1
jmp c14_match_4_seek
label c14_next_4
cmp r9 9
jlt c14_next_5
set r0 0
label c14_match_5_seek
mov r8 r9
sub r8 9
cmp r0 r8
jgt c14_next_5
mov r7 r0
add r7 9190000000000001024
load8 r2 $r7
cmp r2 32
jne c14_match_5_advance
mov r7 r0
add r7 9190000000000001025
load8 r2 $r7
cmp r2 109
jne c14_match_5_advance
mov r7 r0
add r7 9190000000000001026
load8 r2 $r7
cmp r2 101
jne c14_match_5_advance
mov r7 r0
add r7 9190000000000001027
load8 r2 $r7
cmp r2 109
jne c14_match_5_advance
mov r7 r0
add r7 9190000000000001028
load8 r2 $r7
cmp r2 111
jne c14_match_5_advance
mov r7 r0
add r7 9190000000000001029
load8 r2 $r7
cmp r2 114
jne c14_match_5_advance
mov r7 r0
add r7 9190000000000001030
load8 r2 $r7
cmp r2 105
jne c14_match_5_advance
mov r7 r0
add r7 9190000000000001031
load8 r2 $r7
cmp r2 97
jne c14_match_5_advance
mov r7 r0
add r7 9190000000000001032
load8 r2 $r7
cmp r2 32
jne c14_match_5_advance
store8 8270000000000000020 1
jmp c14_next_5
label c14_match_5_advance
add r0 1
jmp c14_match_5_seek
label c14_next_5
cmp r9 10
jlt c14_next_6
set r0 0
label c14_match_6_seek
mov r8 r9
sub r8 10
cmp r0 r8
jgt c14_next_6
mov r7 r0
add r7 9190000000000001024
load8 r2 $r7
cmp r2 32
jne c14_match_6_advance
mov r7 r0
add r7 9190000000000001025
load8 r2 $r7
cmp r2 114
jne c14_match_6_advance
mov r7 r0
add r7 9190000000000001026
load8 r2 $r7
cmp r2 101
jne c14_match_6_advance
mov r7 r0
add r7 9190000000000001027
load8 r2 $r7
cmp r2 99
jne c14_match_6_advance
mov r7 r0
add r7 9190000000000001028
load8 r2 $r7
cmp r2 117
jne c14_match_6_advance
mov r7 r0
add r7 9190000000000001029
load8 r2 $r7
cmp r2 101
jne c14_match_6_advance
mov r7 r0
add r7 9190000000000001030
load8 r2 $r7
cmp r2 114
jne c14_match_6_advance
mov r7 r0
add r7 9190000000000001031
load8 r2 $r7
cmp r2 100
jne c14_match_6_advance
mov r7 r0
add r7 9190000000000001032
load8 r2 $r7
cmp r2 97
jne c14_match_6_advance
mov r7 r0
add r7 9190000000000001033
load8 r2 $r7
cmp r2 32
jne c14_match_6_advance
store8 8270000000000000020 1
jmp c14_next_6
label c14_match_6_advance
add r0 1
jmp c14_match_6_seek
label c14_next_6
cmp r9 12
jlt c14_next_7
set r0 0
label c14_match_7_seek
mov r8 r9
sub r8 12
cmp r0 r8
jgt c14_next_7
mov r7 r0
add r7 9190000000000001024
load8 r2 $r7
cmp r2 32
jne c14_match_7_advance
mov r7 r0
add r7 9190000000000001025
load8 r2 $r7
cmp r2 114
jne c14_match_7_advance
mov r7 r0
add r7 9190000000000001026
load8 r2 $r7
cmp r2 101
jne c14_match_7_advance
mov r7 r0
add r7 9190000000000001027
load8 r2 $r7
cmp r2 99
jne c14_match_7_advance
mov r7 r0
add r7 9190000000000001028
load8 r2 $r7
cmp r2 117
jne c14_match_7_advance
mov r7 r0
add r7 9190000000000001029
load8 r2 $r7
cmp r2 101
jne c14_match_7_advance
mov r7 r0
add r7 9190000000000001030
load8 r2 $r7
cmp r2 114
jne c14_match_7_advance
mov r7 r0
add r7 9190000000000001031
load8 r2 $r7
cmp r2 100
jne c14_match_7_advance
mov r7 r0
add r7 9190000000000001032
load8 r2 $r7
cmp r2 97
jne c14_match_7_advance
mov r7 r0
add r7 9190000000000001033
load8 r2 $r7
cmp r2 109
jne c14_match_7_advance
mov r7 r0
add r7 9190000000000001034
load8 r2 $r7
cmp r2 101
jne c14_match_7_advance
mov r7 r0
add r7 9190000000000001035
load8 r2 $r7
cmp r2 32
jne c14_match_7_advance
store8 8270000000000000020 1
jmp c14_next_7
label c14_match_7_advance
add r0 1
jmp c14_match_7_seek
label c14_next_7
cmp r9 10
jlt c14_next_8
set r0 0
label c14_match_8_seek
mov r8 r9
sub r8 10
cmp r0 r8
jgt c14_next_8
mov r7 r0
add r7 9190000000000001024
load8 r2 $r7
cmp r2 32
jne c14_match_8_advance
mov r7 r0
add r7 9190000000000001025
load8 r2 $r7
cmp r2 114
jne c14_match_8_advance
mov r7 r0
add r7 9190000000000001026
load8 r2 $r7
cmp r2 101
jne c14_match_8_advance
mov r7 r0
add r7 9190000000000001027
load8 r2 $r7
cmp r2 99
jne c14_match_8_advance
mov r7 r0
add r7 9190000000000001028
load8 r2 $r7
cmp r2 111
jne c14_match_8_advance
mov r7 r0
add r7 9190000000000001029
load8 r2 $r7
cmp r2 114
jne c14_match_8_advance
mov r7 r0
add r7 9190000000000001030
load8 r2 $r7
cmp r2 100
jne c14_match_8_advance
mov r7 r0
add r7 9190000000000001031
load8 r2 $r7
cmp r2 97
jne c14_match_8_advance
mov r7 r0
add r7 9190000000000001032
load8 r2 $r7
cmp r2 114
jne c14_match_8_advance
mov r7 r0
add r7 9190000000000001033
load8 r2 $r7
cmp r2 32
jne c14_match_8_advance
store8 8270000000000000020 1
jmp c14_next_8
label c14_match_8_advance
add r0 1
jmp c14_match_8_seek
label c14_next_8
cmp r9 10
jlt c14_next_9
set r0 0
label c14_match_9_seek
mov r8 r9
sub r8 10
cmp r0 r8
jgt c14_next_9
mov r7 r0
add r7 9190000000000001024
load8 r2 $r7
cmp r2 32
jne c14_match_9_advance
mov r7 r0
add r7 9190000000000001025
load8 r2 $r7
cmp r2 109
jne c14_match_9_advance
mov r7 r0
add r7 9190000000000001026
load8 r2 $r7
cmp r2 101
jne c14_match_9_advance
mov r7 r0
add r7 9190000000000001027
load8 r2 $r7
cmp r2 110
jne c14_match_9_advance
mov r7 r0
add r7 9190000000000001028
load8 r2 $r7
cmp r2 99
jne c14_match_9_advance
mov r7 r0
add r7 9190000000000001029
load8 r2 $r7
cmp r2 105
jne c14_match_9_advance
mov r7 r0
add r7 9190000000000001030
load8 r2 $r7
cmp r2 111
jne c14_match_9_advance
mov r7 r0
add r7 9190000000000001031
load8 r2 $r7
cmp r2 110
jne c14_match_9_advance
mov r7 r0
add r7 9190000000000001032
load8 r2 $r7
cmp r2 101
jne c14_match_9_advance
mov r7 r0
add r7 9190000000000001033
load8 r2 $r7
cmp r2 32
jne c14_match_9_advance
store8 8270000000000000020 1
jmp c14_next_9
label c14_match_9_advance
add r0 1
jmp c14_match_9_seek
label c14_next_9
cmp r9 10
jlt c14_next_10
set r0 0
label c14_match_10_seek
mov r8 r9
sub r8 10
cmp r0 r8
jgt c14_next_10
mov r7 r0
add r7 9190000000000001024
load8 r2 $r7
cmp r2 32
jne c14_match_10_advance
mov r7 r0
add r7 9190000000000001025
load8 r2 $r7
cmp r2 114
jne c14_match_10_advance
mov r7 r0
add r7 9190000000000001026
load8 r2 $r7
cmp r2 101
jne c14_match_10_advance
mov r7 r0
add r7 9190000000000001027
load8 r2 $r7
cmp r2 115
jne c14_match_10_advance
mov r7 r0
add r7 9190000000000001028
load8 r2 $r7
cmp r2 112
jne c14_match_10_advance
mov r7 r0
add r7 9190000000000001029
load8 r2 $r7
cmp r2 111
jne c14_match_10_advance
mov r7 r0
add r7 9190000000000001030
load8 r2 $r7
cmp r2 110
jne c14_match_10_advance
mov r7 r0
add r7 9190000000000001031
load8 r2 $r7
cmp r2 100
jne c14_match_10_advance
mov r7 r0
add r7 9190000000000001032
load8 r2 $r7
cmp r2 105
jne c14_match_10_advance
mov r7 r0
add r7 9190000000000001033
load8 r2 $r7
cmp r2 32
jne c14_match_10_advance
store8 8270000000000000020 1
jmp c14_next_10
label c14_match_10_advance
add r0 1
jmp c14_match_10_seek
label c14_next_10
cmp r9 12
jlt c14_next_11
set r0 0
label c14_match_11_seek
mov r8 r9
sub r8 12
cmp r0 r8
jgt c14_next_11
mov r7 r0
add r7 9190000000000001024
load8 r2 $r7
cmp r2 32
jne c14_match_11_advance
mov r7 r0
add r7 9190000000000001025
load8 r2 $r7
cmp r2 99
jne c14_match_11_advance
mov r7 r0
add r7 9190000000000001026
load8 r2 $r7
cmp r2 111
jne c14_match_11_advance
mov r7 r0
add r7 9190000000000001027
load8 r2 $r7
cmp r2 109
jne c14_match_11_advance
mov r7 r0
add r7 9190000000000001028
load8 r2 $r7
cmp r2 101
jne c14_match_11_advance
mov r7 r0
add r7 9190000000000001029
load8 r2 $r7
cmp r2 110
jne c14_match_11_advance
mov r7 r0
add r7 9190000000000001030
load8 r2 $r7
cmp r2 116
jne c14_match_11_advance
mov r7 r0
add r7 9190000000000001031
load8 r2 $r7
cmp r2 97
jne c14_match_11_advance
mov r7 r0
add r7 9190000000000001032
load8 r2 $r7
cmp r2 115
jne c14_match_11_advance
mov r7 r0
add r7 9190000000000001033
load8 r2 $r7
cmp r2 116
jne c14_match_11_advance
mov r7 r0
add r7 9190000000000001034
load8 r2 $r7
cmp r2 101
jne c14_match_11_advance
mov r7 r0
add r7 9190000000000001035
load8 r2 $r7
cmp r2 32
jne c14_match_11_advance
store8 8270000000000000020 1
jmp c14_next_11
label c14_match_11_advance
add r0 1
jmp c14_match_11_seek
label c14_next_11
cmp r9 10
jlt c14_next_12
set r0 0
label c14_match_12_seek
mov r8 r9
sub r8 10
cmp r0 r8
jgt c14_next_12
mov r7 r0
add r7 9190000000000001024
load8 r2 $r7
cmp r2 32
jne c14_match_12_advance
mov r7 r0
add r7 9190000000000001025
load8 r2 $r7
cmp r2 99
jne c14_match_12_advance
mov r7 r0
add r7 9190000000000001026
load8 r2 $r7
cmp r2 111
jne c14_match_12_advance
mov r7 r0
add r7 9190000000000001027
load8 r2 $r7
cmp r2 110
jne c14_match_12_advance
mov r7 r0
add r7 9190000000000001028
load8 r2 $r7
cmp r2 116
jne c14_match_12_advance
mov r7 r0
add r7 9190000000000001029
load8 r2 $r7
cmp r2 97
jne c14_match_12_advance
mov r7 r0
add r7 9190000000000001030
load8 r2 $r7
cmp r2 115
jne c14_match_12_advance
mov r7 r0
add r7 9190000000000001031
load8 r2 $r7
cmp r2 116
jne c14_match_12_advance
mov r7 r0
add r7 9190000000000001032
load8 r2 $r7
cmp r2 101
jne c14_match_12_advance
mov r7 r0
add r7 9190000000000001033
load8 r2 $r7
cmp r2 32
jne c14_match_12_advance
store8 8270000000000000020 1
jmp c14_next_12
label c14_match_12_advance
add r0 1
jmp c14_match_12_seek
label c14_next_12
cmp r9 10
jlt c14_next_13
set r0 0
label c14_match_13_seek
mov r8 r9
sub r8 10
cmp r0 r8
jgt c14_next_13
mov r7 r0
add r7 9190000000000001024
load8 r2 $r7
cmp r2 32
jne c14_match_13_advance
mov r7 r0
add r7 9190000000000001025
load8 r2 $r7
cmp r2 114
jne c14_match_13_advance
mov r7 r0
add r7 9190000000000001026
load8 r2 $r7
cmp r2 101
jne c14_match_13_advance
mov r7 r0
add r7 9190000000000001027
load8 r2 $r7
cmp r2 99
jne c14_match_13_advance
mov r7 r0
add r7 9190000000000001028
load8 r2 $r7
cmp r2 117
jne c14_match_13_advance
mov r7 r0
add r7 9190000000000001029
load8 r2 $r7
cmp r2 112
jne c14_match_13_advance
mov r7 r0
add r7 9190000000000001030
load8 r2 $r7
cmp r2 101
jne c14_match_13_advance
mov r7 r0
add r7 9190000000000001031
load8 r2 $r7
cmp r2 114
jne c14_match_13_advance
mov r7 r0
add r7 9190000000000001032
load8 r2 $r7
cmp r2 97
jne c14_match_13_advance
mov r7 r0
add r7 9190000000000001033
load8 r2 $r7
cmp r2 32
jne c14_match_13_advance
store8 8270000000000000020 1
jmp c14_next_13
label c14_match_13_advance
add r0 1
jmp c14_match_13_seek
label c14_next_13
cmp r9 8
jlt c14_next_14
set r0 0
label c14_match_14_seek
mov r8 r9
sub r8 8
cmp r0 r8
jgt c14_next_14
mov r7 r0
add r7 9190000000000001024
load8 r2 $r7
cmp r2 32
jne c14_match_14_advance
mov r7 r0
add r7 9190000000000001025
load8 r2 $r7
cmp r2 100
jne c14_match_14_advance
mov r7 r0
add r7 9190000000000001026
load8 r2 $r7
cmp r2 101
jne c14_match_14_advance
mov r7 r0
add r7 9190000000000001027
load8 r2 $r7
cmp r2 100
jne c14_match_14_advance
mov r7 r0
add r7 9190000000000001028
load8 r2 $r7
cmp r2 117
jne c14_match_14_advance
mov r7 r0
add r7 9190000000000001029
load8 r2 $r7
cmp r2 99
jne c14_match_14_advance
mov r7 r0
add r7 9190000000000001030
load8 r2 $r7
cmp r2 101
jne c14_match_14_advance
mov r7 r0
add r7 9190000000000001031
load8 r2 $r7
cmp r2 32
jne c14_match_14_advance
store8 8270000000000000021 1
jmp c14_next_14
label c14_match_14_advance
add r0 1
jmp c14_match_14_seek
label c14_next_14
cmp r9 11
jlt c14_next_15
set r0 0
label c14_match_15_seek
mov r8 r9
sub r8 11
cmp r0 r8
jgt c14_next_15
mov r7 r0
add r7 9190000000000001024
load8 r2 $r7
cmp r2 32
jne c14_match_15_advance
mov r7 r0
add r7 9190000000000001025
load8 r2 $r7
cmp r2 100
jne c14_match_15_advance
mov r7 r0
add r7 9190000000000001026
load8 r2 $r7
cmp r2 101
jne c14_match_15_advance
mov r7 r0
add r7 9190000000000001027
load8 r2 $r7
cmp r2 100
jne c14_match_15_advance
mov r7 r0
add r7 9190000000000001028
load8 r2 $r7
cmp r2 117
jne c14_match_15_advance
mov r7 r0
add r7 9190000000000001029
load8 r2 $r7
cmp r2 99
jne c14_match_15_advance
mov r7 r0
add r7 9190000000000001030
load8 r2 $r7
cmp r2 99
jne c14_match_15_advance
mov r7 r0
add r7 9190000000000001031
load8 r2 $r7
cmp r2 105
jne c14_match_15_advance
mov r7 r0
add r7 9190000000000001032
load8 r2 $r7
cmp r2 111
jne c14_match_15_advance
mov r7 r0
add r7 9190000000000001033
load8 r2 $r7
cmp r2 110
jne c14_match_15_advance
mov r7 r0
add r7 9190000000000001034
load8 r2 $r7
cmp r2 32
jne c14_match_15_advance
store8 8270000000000000021 1
jmp c14_next_15
label c14_match_15_advance
add r0 1
jmp c14_match_15_seek
label c14_next_15
cmp r9 10
jlt c14_next_16
set r0 0
label c14_match_16_seek
mov r8 r9
sub r8 10
cmp r0 r8
jgt c14_next_16
mov r7 r0
add r7 9190000000000001024
load8 r2 $r7
cmp r2 32
jne c14_match_16_advance
mov r7 r0
add r7 9190000000000001025
load8 r2 $r7
cmp r2 112
jne c14_match_16_advance
mov r7 r0
add r7 9190000000000001026
load8 r2 $r7
cmp r2 114
jne c14_match_16_advance
mov r7 r0
add r7 9190000000000001027
load8 r2 $r7
cmp r2 101
jne c14_match_16_advance
mov r7 r0
add r7 9190000000000001028
load8 r2 $r7
cmp r2 109
jne c14_match_16_advance
mov r7 r0
add r7 9190000000000001029
load8 r2 $r7
cmp r2 105
jne c14_match_16_advance
mov r7 r0
add r7 9190000000000001030
load8 r2 $r7
cmp r2 115
jne c14_match_16_advance
mov r7 r0
add r7 9190000000000001031
load8 r2 $r7
cmp r2 97
jne c14_match_16_advance
mov r7 r0
add r7 9190000000000001032
load8 r2 $r7
cmp r2 115
jne c14_match_16_advance
mov r7 r0
add r7 9190000000000001033
load8 r2 $r7
cmp r2 32
jne c14_match_16_advance
store8 8270000000000000021 1
jmp c14_next_16
label c14_match_16_advance
add r0 1
jmp c14_match_16_seek
label c14_next_16
cmp r9 8
jlt c14_next_17
set r0 0
label c14_match_17_seek
mov r8 r9
sub r8 8
cmp r0 r8
jgt c14_next_17
mov r7 r0
add r7 9190000000000001024
load8 r2 $r7
cmp r2 32
jne c14_match_17_advance
mov r7 r0
add r7 9190000000000001025
load8 r2 $r7
cmp r2 114
jne c14_match_17_advance
mov r7 r0
add r7 9190000000000001026
load8 r2 $r7
cmp r2 97
jne c14_match_17_advance
mov r7 r0
add r7 9190000000000001027
load8 r2 $r7
cmp r2 122
jne c14_match_17_advance
mov r7 r0
add r7 9190000000000001028
load8 r2 $r7
cmp r2 111
jne c14_match_17_advance
mov r7 r0
add r7 9190000000000001029
load8 r2 $r7
cmp r2 110
jne c14_match_17_advance
mov r7 r0
add r7 9190000000000001030
load8 r2 $r7
cmp r2 97
jne c14_match_17_advance
mov r7 r0
add r7 9190000000000001031
load8 r2 $r7
cmp r2 32
jne c14_match_17_advance
store8 8270000000000000021 1
jmp c14_next_17
label c14_match_17_advance
add r0 1
jmp c14_match_17_seek
label c14_next_17
cmp r9 14
jlt c14_next_18
set r0 0
label c14_match_18_seek
mov r8 r9
sub r8 14
cmp r0 r8
jgt c14_next_18
mov r7 r0
add r7 9190000000000001024
load8 r2 $r7
cmp r2 32
jne c14_match_18_advance
mov r7 r0
add r7 9190000000000001025
load8 r2 $r7
cmp r2 114
jne c14_match_18_advance
mov r7 r0
add r7 9190000000000001026
load8 r2 $r7
cmp r2 97
jne c14_match_18_advance
mov r7 r0
add r7 9190000000000001027
load8 r2 $r7
cmp r2 122
jne c14_match_18_advance
mov r7 r0
add r7 9190000000000001028
load8 r2 $r7
cmp r2 111
jne c14_match_18_advance
mov r7 r0
add r7 9190000000000001029
load8 r2 $r7
cmp r2 110
jne c14_match_18_advance
mov r7 r0
add r7 9190000000000001030
load8 r2 $r7
cmp r2 97
jne c14_match_18_advance
mov r7 r0
add r7 9190000000000001031
load8 r2 $r7
cmp r2 109
jne c14_match_18_advance
mov r7 r0
add r7 9190000000000001032
load8 r2 $r7
cmp r2 105
jne c14_match_18_advance
mov r7 r0
add r7 9190000000000001033
load8 r2 $r7
cmp r2 101
jne c14_match_18_advance
mov r7 r0
add r7 9190000000000001034
load8 r2 $r7
cmp r2 110
jne c14_match_18_advance
mov r7 r0
add r7 9190000000000001035
load8 r2 $r7
cmp r2 116
jne c14_match_18_advance
mov r7 r0
add r7 9190000000000001036
load8 r2 $r7
cmp r2 111
jne c14_match_18_advance
mov r7 r0
add r7 9190000000000001037
load8 r2 $r7
cmp r2 32
jne c14_match_18_advance
store8 8270000000000000021 1
jmp c14_next_18
label c14_match_18_advance
add r0 1
jmp c14_match_18_seek
label c14_next_18
cmp r9 8
jlt c14_next_19
set r0 0
label c14_match_19_seek
mov r8 r9
sub r8 8
cmp r0 r8
jgt c14_next_19
mov r7 r0
add r7 9190000000000001024
load8 r2 $r7
cmp r2 32
jne c14_match_19_advance
mov r7 r0
add r7 9190000000000001025
load8 r2 $r7
cmp r2 108
jne c14_match_19_advance
mov r7 r0
add r7 9190000000000001026
load8 r2 $r7
cmp r2 111
jne c14_match_19_advance
mov r7 r0
add r7 9190000000000001027
load8 r2 $r7
cmp r2 103
jne c14_match_19_advance
mov r7 r0
add r7 9190000000000001028
load8 r2 $r7
cmp r2 105
jne c14_match_19_advance
mov r7 r0
add r7 9190000000000001029
load8 r2 $r7
cmp r2 99
jne c14_match_19_advance
mov r7 r0
add r7 9190000000000001030
load8 r2 $r7
cmp r2 97
jne c14_match_19_advance
mov r7 r0
add r7 9190000000000001031
load8 r2 $r7
cmp r2 32
jne c14_match_19_advance
store8 8270000000000000021 1
jmp c14_next_19
label c14_match_19_advance
add r0 1
jmp c14_match_19_seek
label c14_next_19
cmp r9 11
jlt c14_next_20
set r0 0
label c14_match_20_seek
mov r8 r9
sub r8 11
cmp r0 r8
jgt c14_next_20
mov r7 r0
add r7 9190000000000001024
load8 r2 $r7
cmp r2 32
jne c14_match_20_advance
mov r7 r0
add r7 9190000000000001025
load8 r2 $r7
cmp r2 115
jne c14_match_20_advance
mov r7 r0
add r7 9190000000000001026
load8 r2 $r7
cmp r2 105
jne c14_match_20_advance
mov r7 r0
add r7 9190000000000001027
load8 r2 $r7
cmp r2 108
jne c14_match_20_advance
mov r7 r0
add r7 9190000000000001028
load8 r2 $r7
cmp r2 111
jne c14_match_20_advance
mov r7 r0
add r7 9190000000000001029
load8 r2 $r7
cmp r2 103
jne c14_match_20_advance
mov r7 r0
add r7 9190000000000001030
load8 r2 $r7
cmp r2 105
jne c14_match_20_advance
mov r7 r0
add r7 9190000000000001031
load8 r2 $r7
cmp r2 115
jne c14_match_20_advance
mov r7 r0
add r7 9190000000000001032
load8 r2 $r7
cmp r2 109
jne c14_match_20_advance
mov r7 r0
add r7 9190000000000001033
load8 r2 $r7
cmp r2 111
jne c14_match_20_advance
mov r7 r0
add r7 9190000000000001034
load8 r2 $r7
cmp r2 32
jne c14_match_20_advance
store8 8270000000000000021 1
jmp c14_next_20
label c14_match_20_advance
add r0 1
jmp c14_match_20_seek
label c14_next_20
cmp r9 12
jlt c14_next_21
set r0 0
label c14_match_21_seek
mov r8 r9
sub r8 12
cmp r0 r8
jgt c14_next_21
mov r7 r0
add r7 9190000000000001024
load8 r2 $r7
cmp r2 32
jne c14_match_21_advance
mov r7 r0
add r7 9190000000000001025
load8 r2 $r7
cmp r2 99
jne c14_match_21_advance
mov r7 r0
add r7 9190000000000001026
load8 r2 $r7
cmp r2 111
jne c14_match_21_advance
mov r7 r0
add r7 9190000000000001027
load8 r2 $r7
cmp r2 110
jne c14_match_21_advance
mov r7 r0
add r7 9190000000000001028
load8 r2 $r7
cmp r2 99
jne c14_match_21_advance
mov r7 r0
add r7 9190000000000001029
load8 r2 $r7
cmp r2 108
jne c14_match_21_advance
mov r7 r0
add r7 9190000000000001030
load8 r2 $r7
cmp r2 117
jne c14_match_21_advance
mov r7 r0
add r7 9190000000000001031
load8 r2 $r7
cmp r2 115
jne c14_match_21_advance
mov r7 r0
add r7 9190000000000001032
load8 r2 $r7
cmp r2 105
jne c14_match_21_advance
mov r7 r0
add r7 9190000000000001033
load8 r2 $r7
cmp r2 111
jne c14_match_21_advance
mov r7 r0
add r7 9190000000000001034
load8 r2 $r7
cmp r2 110
jne c14_match_21_advance
mov r7 r0
add r7 9190000000000001035
load8 r2 $r7
cmp r2 32
jne c14_match_21_advance
store8 8270000000000000021 1
jmp c14_next_21
label c14_match_21_advance
add r0 1
jmp c14_match_21_seek
label c14_next_21
cmp r9 11
jlt c14_next_22
set r0 0
label c14_match_22_seek
mov r8 r9
sub r8 11
cmp r0 r8
jgt c14_next_22
mov r7 r0
add r7 9190000000000001024
load8 r2 $r7
cmp r2 32
jne c14_match_22_advance
mov r7 r0
add r7 9190000000000001025
load8 r2 $r7
cmp r2 100
jne c14_match_22_advance
mov r7 r0
add r7 9190000000000001026
load8 r2 $r7
cmp r2 101
jne c14_match_22_advance
mov r7 r0
add r7 9190000000000001027
load8 r2 $r7
cmp r2 109
jne c14_match_22_advance
mov r7 r0
add r7 9190000000000001028
load8 r2 $r7
cmp r2 117
jne c14_match_22_advance
mov r7 r0
add r7 9190000000000001029
load8 r2 $r7
cmp r2 101
jne c14_match_22_advance
mov r7 r0
add r7 9190000000000001030
load8 r2 $r7
cmp r2 115
jne c14_match_22_advance
mov r7 r0
add r7 9190000000000001031
load8 r2 $r7
cmp r2 116
jne c14_match_22_advance
mov r7 r0
add r7 9190000000000001032
load8 r2 $r7
cmp r2 114
jne c14_match_22_advance
mov r7 r0
add r7 9190000000000001033
load8 r2 $r7
cmp r2 97
jne c14_match_22_advance
mov r7 r0
add r7 9190000000000001034
load8 r2 $r7
cmp r2 32
jne c14_match_22_advance
store8 8270000000000000021 1
jmp c14_next_22
label c14_match_22_advance
add r0 1
jmp c14_match_22_seek
label c14_next_22
cmp r9 9
jlt c14_next_23
set r0 0
label c14_match_23_seek
mov r8 r9
sub r8 9
cmp r0 r8
jgt c14_next_23
mov r7 r0
add r7 9190000000000001024
load8 r2 $r7
cmp r2 32
jne c14_match_23_advance
mov r7 r0
add r7 9190000000000001025
load8 r2 $r7
cmp r2 105
jne c14_match_23_advance
mov r7 r0
add r7 9190000000000001026
load8 r2 $r7
cmp r2 109
jne c14_match_23_advance
mov r7 r0
add r7 9190000000000001027
load8 r2 $r7
cmp r2 112
jne c14_match_23_advance
mov r7 r0
add r7 9190000000000001028
load8 r2 $r7
cmp r2 108
jne c14_match_23_advance
mov r7 r0
add r7 9190000000000001029
load8 r2 $r7
cmp r2 105
jne c14_match_23_advance
mov r7 r0
add r7 9190000000000001030
load8 r2 $r7
cmp r2 99
jne c14_match_23_advance
mov r7 r0
add r7 9190000000000001031
load8 r2 $r7
cmp r2 97
jne c14_match_23_advance
mov r7 r0
add r7 9190000000000001032
load8 r2 $r7
cmp r2 32
jne c14_match_23_advance
store8 8270000000000000021 1
jmp c14_next_23
label c14_match_23_advance
add r0 1
jmp c14_match_23_seek
label c14_next_23
cmp r9 12
jlt c14_next_24
set r0 0
label c14_match_24_seek
mov r8 r9
sub r8 12
cmp r0 r8
jgt c14_next_24
mov r7 r0
add r7 9190000000000001024
load8 r2 $r7
cmp r2 32
jne c14_match_24_advance
mov r7 r0
add r7 9190000000000001025
load8 r2 $r7
cmp r2 105
jne c14_match_24_advance
mov r7 r0
add r7 9190000000000001026
load8 r2 $r7
cmp r2 110
jne c14_match_24_advance
mov r7 r0
add r7 9190000000000001027
load8 r2 $r7
cmp r2 102
jne c14_match_24_advance
mov r7 r0
add r7 9190000000000001028
load8 r2 $r7
cmp r2 101
jne c14_match_24_advance
mov r7 r0
add r7 9190000000000001029
load8 r2 $r7
cmp r2 114
jne c14_match_24_advance
mov r7 r0
add r7 9190000000000001030
load8 r2 $r7
cmp r2 101
jne c14_match_24_advance
mov r7 r0
add r7 9190000000000001031
load8 r2 $r7
cmp r2 110
jne c14_match_24_advance
mov r7 r0
add r7 9190000000000001032
load8 r2 $r7
cmp r2 99
jne c14_match_24_advance
mov r7 r0
add r7 9190000000000001033
load8 r2 $r7
cmp r2 105
jne c14_match_24_advance
mov r7 r0
add r7 9190000000000001034
load8 r2 $r7
cmp r2 97
jne c14_match_24_advance
mov r7 r0
add r7 9190000000000001035
load8 r2 $r7
cmp r2 32
jne c14_match_24_advance
store8 8270000000000000021 1
jmp c14_next_24
label c14_match_24_advance
add r0 1
jmp c14_match_24_seek
label c14_next_24
cmp r9 9
jlt c14_next_25
set r0 0
label c14_match_25_seek
mov r8 r9
sub r8 9
cmp r0 r8
jgt c14_next_25
mov r7 r0
add r7 9190000000000001024
load8 r2 $r7
cmp r2 32
jne c14_match_25_advance
mov r7 r0
add r7 9190000000000001025
load8 r2 $r7
cmp r2 105
jne c14_match_25_advance
mov r7 r0
add r7 9190000000000001026
load8 r2 $r7
cmp r2 110
jne c14_match_25_advance
mov r7 r0
add r7 9190000000000001027
load8 r2 $r7
cmp r2 102
jne c14_match_25_advance
mov r7 r0
add r7 9190000000000001028
load8 r2 $r7
cmp r2 101
jne c14_match_25_advance
mov r7 r0
add r7 9190000000000001029
load8 r2 $r7
cmp r2 114
jne c14_match_25_advance
mov r7 r0
add r7 9190000000000001030
load8 r2 $r7
cmp r2 105
jne c14_match_25_advance
mov r7 r0
add r7 9190000000000001031
load8 r2 $r7
cmp r2 114
jne c14_match_25_advance
mov r7 r0
add r7 9190000000000001032
load8 r2 $r7
cmp r2 32
jne c14_match_25_advance
store8 8270000000000000021 1
jmp c14_next_25
label c14_match_25_advance
add r0 1
jmp c14_match_25_seek
label c14_next_25
cmp r9 11
jlt c14_next_26
set r0 0
label c14_match_26_seek
mov r8 r9
sub r8 11
cmp r0 r8
jgt c14_next_26
mov r7 r0
add r7 9190000000000001024
load8 r2 $r7
cmp r2 32
jne c14_match_26_advance
mov r7 r0
add r7 9190000000000001025
load8 r2 $r7
cmp r2 106
jne c14_match_26_advance
mov r7 r0
add r7 9190000000000001026
load8 r2 $r7
cmp r2 117
jne c14_match_26_advance
mov r7 r0
add r7 9190000000000001027
load8 r2 $r7
cmp r2 115
jne c14_match_26_advance
mov r7 r0
add r7 9190000000000001028
load8 r2 $r7
cmp r2 116
jne c14_match_26_advance
mov r7 r0
add r7 9190000000000001029
load8 r2 $r7
cmp r2 105
jne c14_match_26_advance
mov r7 r0
add r7 9190000000000001030
load8 r2 $r7
cmp r2 102
jne c14_match_26_advance
mov r7 r0
add r7 9190000000000001031
load8 r2 $r7
cmp r2 105
jne c14_match_26_advance
mov r7 r0
add r7 9190000000000001032
load8 r2 $r7
cmp r2 99
jne c14_match_26_advance
mov r7 r0
add r7 9190000000000001033
load8 r2 $r7
cmp r2 97
jne c14_match_26_advance
mov r7 r0
add r7 9190000000000001034
load8 r2 $r7
cmp r2 32
jne c14_match_26_advance
store8 8270000000000000021 1
jmp c14_next_26
label c14_match_26_advance
add r0 1
jmp c14_match_26_seek
label c14_next_26
cmp r9 11
jlt c14_next_27
set r0 0
label c14_match_27_seek
mov r8 r9
sub r8 11
cmp r0 r8
jgt c14_next_27
mov r7 r0
add r7 9190000000000001024
load8 r2 $r7
cmp r2 32
jne c14_match_27_advance
mov r7 r0
add r7 9190000000000001025
load8 r2 $r7
cmp r2 97
jne c14_match_27_advance
mov r7 r0
add r7 9190000000000001026
load8 r2 $r7
cmp r2 114
jne c14_match_27_advance
mov r7 r0
add r7 9190000000000001027
load8 r2 $r7
cmp r2 103
jne c14_match_27_advance
mov r7 r0
add r7 9190000000000001028
load8 r2 $r7
cmp r2 117
jne c14_match_27_advance
mov r7 r0
add r7 9190000000000001029
load8 r2 $r7
cmp r2 109
jne c14_match_27_advance
mov r7 r0
add r7 9190000000000001030
load8 r2 $r7
cmp r2 101
jne c14_match_27_advance
mov r7 r0
add r7 9190000000000001031
load8 r2 $r7
cmp r2 110
jne c14_match_27_advance
mov r7 r0
add r7 9190000000000001032
load8 r2 $r7
cmp r2 116
jne c14_match_27_advance
mov r7 r0
add r7 9190000000000001033
load8 r2 $r7
cmp r2 111
jne c14_match_27_advance
mov r7 r0
add r7 9190000000000001034
load8 r2 $r7
cmp r2 32
jne c14_match_27_advance
store8 8270000000000000021 1
jmp c14_next_27
label c14_match_27_advance
add r0 1
jmp c14_match_27_seek
label c14_next_27
cmp r9 15
jlt c14_next_28
set r0 0
label c14_match_28_seek
mov r8 r9
sub r8 15
cmp r0 r8
jgt c14_next_28
mov r7 r0
add r7 9190000000000001024
load8 r2 $r7
cmp r2 32
jne c14_match_28_advance
mov r7 r0
add r7 9190000000000001025
load8 r2 $r7
cmp r2 99
jne c14_match_28_advance
mov r7 r0
add r7 9190000000000001026
load8 r2 $r7
cmp r2 111
jne c14_match_28_advance
mov r7 r0
add r7 9190000000000001027
load8 r2 $r7
cmp r2 110
jne c14_match_28_advance
mov r7 r0
add r7 9190000000000001028
load8 r2 $r7
cmp r2 116
jne c14_match_28_advance
mov r7 r0
add r7 9190000000000001029
load8 r2 $r7
cmp r2 114
jne c14_match_28_advance
mov r7 r0
add r7 9190000000000001030
load8 r2 $r7
cmp r2 97
jne c14_match_28_advance
mov r7 r0
add r7 9190000000000001031
load8 r2 $r7
cmp r2 100
jne c14_match_28_advance
mov r7 r0
add r7 9190000000000001032
load8 r2 $r7
cmp r2 105
jne c14_match_28_advance
mov r7 r0
add r7 9190000000000001033
load8 r2 $r7
cmp r2 99
jne c14_match_28_advance
mov r7 r0
add r7 9190000000000001034
load8 r2 $r7
cmp r2 99
jne c14_match_28_advance
mov r7 r0
add r7 9190000000000001035
load8 r2 $r7
cmp r2 105
jne c14_match_28_advance
mov r7 r0
add r7 9190000000000001036
load8 r2 $r7
cmp r2 111
jne c14_match_28_advance
mov r7 r0
add r7 9190000000000001037
load8 r2 $r7
cmp r2 110
jne c14_match_28_advance
mov r7 r0
add r7 9190000000000001038
load8 r2 $r7
cmp r2 32
jne c14_match_28_advance
store8 8270000000000000021 1
jmp c14_next_28
label c14_match_28_advance
add r0 1
jmp c14_match_28_seek
label c14_next_28
cmp r9 8
jlt c14_next_29
set r0 0
label c14_match_29_seek
mov r8 r9
sub r8 8
cmp r0 r8
jgt c14_next_29
mov r7 r0
add r7 9190000000000001024
load8 r2 $r7
cmp r2 32
jne c14_match_29_advance
mov r7 r0
add r7 9190000000000001025
load8 r2 $r7
cmp r2 99
jne c14_match_29_advance
mov r7 r0
add r7 9190000000000001026
load8 r2 $r7
cmp r2 117
jne c14_match_29_advance
mov r7 r0
add r7 9190000000000001027
load8 r2 $r7
cmp r2 101
jne c14_match_29_advance
mov r7 r0
add r7 9190000000000001028
load8 r2 $r7
cmp r2 110
jne c14_match_29_advance
mov r7 r0
add r7 9190000000000001029
load8 r2 $r7
cmp r2 116
jne c14_match_29_advance
mov r7 r0
add r7 9190000000000001030
load8 r2 $r7
cmp r2 111
jne c14_match_29_advance
mov r7 r0
add r7 9190000000000001031
load8 r2 $r7
cmp r2 32
jne c14_match_29_advance
store8 8270000000000000022 1
jmp c14_next_29
label c14_match_29_advance
add r0 1
jmp c14_match_29_seek
label c14_next_29
cmp r9 10
jlt c14_next_30
set r0 0
label c14_match_30_seek
mov r8 r9
sub r8 10
cmp r0 r8
jgt c14_next_30
mov r7 r0
add r7 9190000000000001024
load8 r2 $r7
cmp r2 32
jne c14_match_30_advance
mov r7 r0
add r7 9190000000000001025
load8 r2 $r7
cmp r2 104
jne c14_match_30_advance
mov r7 r0
add r7 9190000000000001026
load8 r2 $r7
cmp r2 105
jne c14_match_30_advance
mov r7 r0
add r7 9190000000000001027
load8 r2 $r7
cmp r2 115
jne c14_match_30_advance
mov r7 r0
add r7 9190000000000001028
load8 r2 $r7
cmp r2 116
jne c14_match_30_advance
mov r7 r0
add r7 9190000000000001029
load8 r2 $r7
cmp r2 111
jne c14_match_30_advance
mov r7 r0
add r7 9190000000000001030
load8 r2 $r7
cmp r2 114
jne c14_match_30_advance
mov r7 r0
add r7 9190000000000001031
load8 r2 $r7
cmp r2 105
jne c14_match_30_advance
mov r7 r0
add r7 9190000000000001032
load8 r2 $r7
cmp r2 97
jne c14_match_30_advance
mov r7 r0
add r7 9190000000000001033
load8 r2 $r7
cmp r2 32
jne c14_match_30_advance
store8 8270000000000000022 1
jmp c14_next_30
label c14_match_30_advance
add r0 1
jmp c14_match_30_seek
label c14_next_30
cmp r9 7
jlt c14_next_31
set r0 0
label c14_match_31_seek
mov r8 r9
sub r8 7
cmp r0 r8
jgt c14_next_31
mov r7 r0
add r7 9190000000000001024
load8 r2 $r7
cmp r2 32
jne c14_match_31_advance
mov r7 r0
add r7 9190000000000001025
load8 r2 $r7
cmp r2 112
jne c14_match_31_advance
mov r7 r0
add r7 9190000000000001026
load8 r2 $r7
cmp r2 111
jne c14_match_31_advance
mov r7 r0
add r7 9190000000000001027
load8 r2 $r7
cmp r2 101
jne c14_match_31_advance
mov r7 r0
add r7 9190000000000001028
load8 r2 $r7
cmp r2 109
jne c14_match_31_advance
mov r7 r0
add r7 9190000000000001029
load8 r2 $r7
cmp r2 97
jne c14_match_31_advance
mov r7 r0
add r7 9190000000000001030
load8 r2 $r7
cmp r2 32
jne c14_match_31_advance
store8 8270000000000000022 1
jmp c14_next_31
label c14_match_31_advance
add r0 1
jmp c14_match_31_seek
label c14_next_31
cmp r9 8
jlt c14_next_32
set r0 0
label c14_match_32_seek
mov r8 r9
sub r8 8
cmp r0 r8
jgt c14_next_32
mov r7 r0
add r7 9190000000000001024
load8 r2 $r7
cmp r2 32
jne c14_match_32_advance
mov r7 r0
add r7 9190000000000001025
load8 r2 $r7
cmp r2 118
jne c14_match_32_advance
mov r7 r0
add r7 9190000000000001026
load8 r2 $r7
cmp r2 101
jne c14_match_32_advance
mov r7 r0
add r7 9190000000000001027
load8 r2 $r7
cmp r2 114
jne c14_match_32_advance
mov r7 r0
add r7 9190000000000001028
load8 r2 $r7
cmp r2 115
jne c14_match_32_advance
mov r7 r0
add r7 9190000000000001029
load8 r2 $r7
cmp r2 111
jne c14_match_32_advance
mov r7 r0
add r7 9190000000000001030
load8 r2 $r7
cmp r2 115
jne c14_match_32_advance
mov r7 r0
add r7 9190000000000001031
load8 r2 $r7
cmp r2 32
jne c14_match_32_advance
store8 8270000000000000022 1
jmp c14_next_32
label c14_match_32_advance
add r0 1
jmp c14_match_32_seek
label c14_next_32
cmp r9 8
jlt c14_next_33
set r0 0
label c14_match_33_seek
mov r8 r9
sub r8 8
cmp r0 r8
jgt c14_next_33
mov r7 r0
add r7 9190000000000001024
load8 r2 $r7
cmp r2 32
jne c14_match_33_advance
mov r7 r0
add r7 9190000000000001025
load8 r2 $r7
cmp r2 114
jne c14_match_33_advance
mov r7 r0
add r7 9190000000000001026
load8 r2 $r7
cmp r2 101
jne c14_match_33_advance
mov r7 r0
add r7 9190000000000001027
load8 r2 $r7
cmp r2 108
jne c14_match_33_advance
mov r7 r0
add r7 9190000000000001028
load8 r2 $r7
cmp r2 97
jne c14_match_33_advance
mov r7 r0
add r7 9190000000000001029
load8 r2 $r7
cmp r2 116
jne c14_match_33_advance
mov r7 r0
add r7 9190000000000001030
load8 r2 $r7
cmp r2 111
jne c14_match_33_advance
mov r7 r0
add r7 9190000000000001031
load8 r2 $r7
cmp r2 32
jne c14_match_33_advance
store8 8270000000000000022 1
jmp c14_next_33
label c14_match_33_advance
add r0 1
jmp c14_match_33_seek
label c14_next_33
cmp r9 11
jlt c14_next_34
set r0 0
label c14_match_34_seek
mov r8 r9
sub r8 11
cmp r0 r8
jgt c14_next_34
mov r7 r0
add r7 9190000000000001024
load8 r2 $r7
cmp r2 32
jne c14_match_34_advance
mov r7 r0
add r7 9190000000000001025
load8 r2 $r7
cmp r2 110
jne c14_match_34_advance
mov r7 r0
add r7 9190000000000001026
load8 r2 $r7
cmp r2 97
jne c14_match_34_advance
mov r7 r0
add r7 9190000000000001027
load8 r2 $r7
cmp r2 114
jne c14_match_34_advance
mov r7 r0
add r7 9190000000000001028
load8 r2 $r7
cmp r2 114
jne c14_match_34_advance
mov r7 r0
add r7 9190000000000001029
load8 r2 $r7
cmp r2 97
jne c14_match_34_advance
mov r7 r0
add r7 9190000000000001030
load8 r2 $r7
cmp r2 99
jne c14_match_34_advance
mov r7 r0
add r7 9190000000000001031
load8 r2 $r7
cmp r2 105
jne c14_match_34_advance
mov r7 r0
add r7 9190000000000001032
load8 r2 $r7
cmp r2 111
jne c14_match_34_advance
mov r7 r0
add r7 9190000000000001033
load8 r2 $r7
cmp r2 110
jne c14_match_34_advance
mov r7 r0
add r7 9190000000000001034
load8 r2 $r7
cmp r2 32
jne c14_match_34_advance
store8 8270000000000000022 1
jmp c14_next_34
label c14_match_34_advance
add r0 1
jmp c14_match_34_seek
label c14_next_34
cmp r9 9
jlt c14_next_35
set r0 0
label c14_match_35_seek
mov r8 r9
sub r8 9
cmp r0 r8
jgt c14_next_35
mov r7 r0
add r7 9190000000000001024
load8 r2 $r7
cmp r2 32
jne c14_match_35_advance
mov r7 r0
add r7 9190000000000001025
load8 r2 $r7
cmp r2 105
jne c14_match_35_advance
mov r7 r0
add r7 9190000000000001026
load8 r2 $r7
cmp r2 110
jne c14_match_35_advance
mov r7 r0
add r7 9190000000000001027
load8 r2 $r7
cmp r2 118
jne c14_match_35_advance
mov r7 r0
add r7 9190000000000001028
load8 r2 $r7
cmp r2 101
jne c14_match_35_advance
mov r7 r0
add r7 9190000000000001029
load8 r2 $r7
cmp r2 110
jne c14_match_35_advance
mov r7 r0
add r7 9190000000000001030
load8 r2 $r7
cmp r2 116
jne c14_match_35_advance
mov r7 r0
add r7 9190000000000001031
load8 r2 $r7
cmp r2 97
jne c14_match_35_advance
mov r7 r0
add r7 9190000000000001032
load8 r2 $r7
cmp r2 32
jne c14_match_35_advance
store8 8270000000000000022 1
jmp c14_next_35
label c14_match_35_advance
add r0 1
jmp c14_match_35_seek
label c14_next_35
cmp r9 9
jlt c14_next_36
set r0 0
label c14_match_36_seek
mov r8 r9
sub r8 9
cmp r0 r8
jgt c14_next_36
mov r7 r0
add r7 9190000000000001024
load8 r2 $r7
cmp r2 32
jne c14_match_36_advance
mov r7 r0
add r7 9190000000000001025
load8 r2 $r7
cmp r2 101
jne c14_match_36_advance
mov r7 r0
add r7 9190000000000001026
load8 r2 $r7
cmp r2 115
jne c14_match_36_advance
mov r7 r0
add r7 9190000000000001027
load8 r2 $r7
cmp r2 99
jne c14_match_36_advance
mov r7 r0
add r7 9190000000000001028
load8 r2 $r7
cmp r2 114
jne c14_match_36_advance
mov r7 r0
add r7 9190000000000001029
load8 r2 $r7
cmp r2 105
jne c14_match_36_advance
mov r7 r0
add r7 9190000000000001030
load8 r2 $r7
cmp r2 98
jne c14_match_36_advance
mov r7 r0
add r7 9190000000000001031
load8 r2 $r7
cmp r2 101
jne c14_match_36_advance
mov r7 r0
add r7 9190000000000001032
load8 r2 $r7
cmp r2 32
jne c14_match_36_advance
store8 8270000000000000022 1
jmp c14_next_36
label c14_match_36_advance
add r0 1
jmp c14_match_36_seek
label c14_next_36
cmp r9 9
jlt c14_next_37
set r0 0
label c14_match_37_seek
mov r8 r9
sub r8 9
cmp r0 r8
jgt c14_next_37
mov r7 r0
add r7 9190000000000001024
load8 r2 $r7
cmp r2 32
jne c14_match_37_advance
mov r7 r0
add r7 9190000000000001025
load8 r2 $r7
cmp r2 114
jne c14_match_37_advance
mov r7 r0
add r7 9190000000000001026
load8 r2 $r7
cmp r2 101
jne c14_match_37_advance
mov r7 r0
add r7 9190000000000001027
load8 r2 $r7
cmp r2 100
jne c14_match_37_advance
mov r7 r0
add r7 9190000000000001028
load8 r2 $r7
cmp r2 97
jne c14_match_37_advance
mov r7 r0
add r7 9190000000000001029
load8 r2 $r7
cmp r2 99
jne c14_match_37_advance
mov r7 r0
add r7 9190000000000001030
load8 r2 $r7
cmp r2 116
jne c14_match_37_advance
mov r7 r0
add r7 9190000000000001031
load8 r2 $r7
cmp r2 97
jne c14_match_37_advance
mov r7 r0
add r7 9190000000000001032
load8 r2 $r7
cmp r2 32
jne c14_match_37_advance
store8 8270000000000000022 1
jmp c14_next_37
label c14_match_37_advance
add r0 1
jmp c14_match_37_seek
label c14_next_37
cmp r9 9
jlt c14_next_38
set r0 0
label c14_match_38_seek
mov r8 r9
sub r8 9
cmp r0 r8
jgt c14_next_38
mov r7 r0
add r7 9190000000000001024
load8 r2 $r7
cmp r2 32
jne c14_match_38_advance
mov r7 r0
add r7 9190000000000001025
load8 r2 $r7
cmp r2 99
jne c14_match_38_advance
mov r7 r0
add r7 9190000000000001026
load8 r2 $r7
cmp r2 111
jne c14_match_38_advance
mov r7 r0
add r7 9190000000000001027
load8 r2 $r7
cmp r2 109
jne c14_match_38_advance
mov r7 r0
add r7 9190000000000001028
load8 r2 $r7
cmp r2 112
jne c14_match_38_advance
mov r7 r0
add r7 9190000000000001029
load8 r2 $r7
cmp r2 111
jne c14_match_38_advance
mov r7 r0
add r7 9190000000000001030
load8 r2 $r7
cmp r2 110
jne c14_match_38_advance
mov r7 r0
add r7 9190000000000001031
load8 r2 $r7
cmp r2 101
jne c14_match_38_advance
mov r7 r0
add r7 9190000000000001032
load8 r2 $r7
cmp r2 32
jne c14_match_38_advance
store8 8270000000000000022 1
jmp c14_next_38
label c14_match_38_advance
add r0 1
jmp c14_match_38_seek
label c14_next_38
cmp r9 8
jlt c14_next_39
set r0 0
label c14_match_39_seek
mov r8 r9
sub r8 8
cmp r0 r8
jgt c14_next_39
mov r7 r0
add r7 9190000000000001024
load8 r2 $r7
cmp r2 32
jne c14_match_39_advance
mov r7 r0
add r7 9190000000000001025
load8 r2 $r7
cmp r2 99
jne c14_match_39_advance
mov r7 r0
add r7 9190000000000001026
load8 r2 $r7
cmp r2 111
jne c14_match_39_advance
mov r7 r0
add r7 9190000000000001027
load8 r2 $r7
cmp r2 109
jne c14_match_39_advance
mov r7 r0
add r7 9190000000000001028
load8 r2 $r7
cmp r2 112
jne c14_match_39_advance
mov r7 r0
add r7 9190000000000001029
load8 r2 $r7
cmp r2 111
jne c14_match_39_advance
mov r7 r0
add r7 9190000000000001030
load8 r2 $r7
cmp r2 110
jne c14_match_39_advance
mov r7 r0
add r7 9190000000000001031
load8 r2 $r7
cmp r2 32
jne c14_match_39_advance
store8 8270000000000000022 1
jmp c14_next_39
label c14_match_39_advance
add r0 1
jmp c14_match_39_seek
label c14_next_39
cmp r9 6
jlt c14_next_40
set r0 0
label c14_match_40_seek
mov r8 r9
sub r8 6
cmp r0 r8
jgt c14_next_40
mov r7 r0
add r7 9190000000000001024
load8 r2 $r7
cmp r2 32
jne c14_match_40_advance
mov r7 r0
add r7 9190000000000001025
load8 r2 $r7
cmp r2 99
jne c14_match_40_advance
mov r7 r0
add r7 9190000000000001026
load8 r2 $r7
cmp r2 114
jne c14_match_40_advance
mov r7 r0
add r7 9190000000000001027
load8 r2 $r7
cmp r2 101
jne c14_match_40_advance
mov r7 r0
add r7 9190000000000001028
load8 r2 $r7
cmp r2 97
jne c14_match_40_advance
mov r7 r0
add r7 9190000000000001029
load8 r2 $r7
cmp r2 32
jne c14_match_40_advance
store8 8270000000000000022 1
jmp c14_next_40
label c14_match_40_advance
add r0 1
jmp c14_match_40_seek
label c14_next_40
cmp r9 8
jlt c14_next_41
set r0 0
label c14_match_41_seek
mov r8 r9
sub r8 8
cmp r0 r8
jgt c14_next_41
mov r7 r0
add r7 9190000000000001024
load8 r2 $r7
cmp r2 32
jne c14_match_41_advance
mov r7 r0
add r7 9190000000000001025
load8 r2 $r7
cmp r2 102
jne c14_match_41_advance
mov r7 r0
add r7 9190000000000001026
load8 r2 $r7
cmp r2 97
jne c14_match_41_advance
mov r7 r0
add r7 9190000000000001027
load8 r2 $r7
cmp r2 98
jne c14_match_41_advance
mov r7 r0
add r7 9190000000000001028
load8 r2 $r7
cmp r2 117
jne c14_match_41_advance
mov r7 r0
add r7 9190000000000001029
load8 r2 $r7
cmp r2 108
jne c14_match_41_advance
mov r7 r0
add r7 9190000000000001030
load8 r2 $r7
cmp r2 97
jne c14_match_41_advance
mov r7 r0
add r7 9190000000000001031
load8 r2 $r7
cmp r2 32
jne c14_match_41_advance
store8 8270000000000000022 1
jmp c14_next_41
label c14_match_41_advance
add r0 1
jmp c14_match_41_seek
label c14_next_41
cmp r9 9
jlt c14_next_42
set r0 0
label c14_match_42_seek
mov r8 r9
sub r8 9
cmp r0 r8
jgt c14_next_42
mov r7 r0
add r7 9190000000000001024
load8 r2 $r7
cmp r2 32
jne c14_match_42_advance
mov r7 r0
add r7 9190000000000001025
load8 r2 $r7
cmp r2 102
jne c14_match_42_advance
mov r7 r0
add r7 9190000000000001026
load8 r2 $r7
cmp r2 105
jne c14_match_42_advance
mov r7 r0
add r7 9190000000000001027
load8 r2 $r7
cmp r2 99
jne c14_match_42_advance
mov r7 r0
add r7 9190000000000001028
load8 r2 $r7
cmp r2 99
jne c14_match_42_advance
mov r7 r0
add r7 9190000000000001029
load8 r2 $r7
cmp r2 105
jne c14_match_42_advance
mov r7 r0
add r7 9190000000000001030
load8 r2 $r7
cmp r2 111
jne c14_match_42_advance
mov r7 r0
add r7 9190000000000001031
load8 r2 $r7
cmp r2 110
jne c14_match_42_advance
mov r7 r0
add r7 9190000000000001032
load8 r2 $r7
cmp r2 32
jne c14_match_42_advance
store8 8270000000000000022 1
jmp c14_next_42
label c14_match_42_advance
add r0 1
jmp c14_match_42_seek
label c14_next_42
cmp r9 9
jlt c14_next_43
set r0 0
label c14_match_43_seek
mov r8 r9
sub r8 9
cmp r0 r8
jgt c14_next_43
mov r7 r0
add r7 9190000000000001024
load8 r2 $r7
cmp r2 32
jne c14_match_43_advance
mov r7 r0
add r7 9190000000000001025
load8 r2 $r7
cmp r2 105
jne c14_match_43_advance
mov r7 r0
add r7 9190000000000001026
load8 r2 $r7
cmp r2 109
jne c14_match_43_advance
mov r7 r0
add r7 9190000000000001027
load8 r2 $r7
cmp r2 97
jne c14_match_43_advance
mov r7 r0
add r7 9190000000000001028
load8 r2 $r7
cmp r2 103
jne c14_match_43_advance
mov r7 r0
add r7 9190000000000001029
load8 r2 $r7
cmp r2 105
jne c14_match_43_advance
mov r7 r0
add r7 9190000000000001030
load8 r2 $r7
cmp r2 110
jne c14_match_43_advance
mov r7 r0
add r7 9190000000000001031
load8 r2 $r7
cmp r2 97
jne c14_match_43_advance
mov r7 r0
add r7 9190000000000001032
load8 r2 $r7
cmp r2 32
jne c14_match_43_advance
store8 8270000000000000022 1
jmp c14_next_43
label c14_match_43_advance
add r0 1
jmp c14_match_43_seek
label c14_next_43
cmp r9 9
jlt c14_next_44
set r0 0
label c14_match_44_seek
mov r8 r9
sub r8 9
cmp r0 r8
jgt c14_next_44
mov r7 r0
add r7 9190000000000001024
load8 r2 $r7
cmp r2 32
jne c14_match_44_advance
mov r7 r0
add r7 9190000000000001025
load8 r2 $r7
cmp r2 101
jne c14_match_44_advance
mov r7 r0
add r7 9190000000000001026
load8 r2 $r7
cmp r2 106
jne c14_match_44_advance
mov r7 r0
add r7 9190000000000001027
load8 r2 $r7
cmp r2 101
jne c14_match_44_advance
mov r7 r0
add r7 9190000000000001028
load8 r2 $r7
cmp r2 99
jne c14_match_44_advance
mov r7 r0
add r7 9190000000000001029
load8 r2 $r7
cmp r2 117
jne c14_match_44_advance
mov r7 r0
add r7 9190000000000001030
load8 r2 $r7
cmp r2 116
jne c14_match_44_advance
mov r7 r0
add r7 9190000000000001031
load8 r2 $r7
cmp r2 97
jne c14_match_44_advance
mov r7 r0
add r7 9190000000000001032
load8 r2 $r7
cmp r2 32
jne c14_match_44_advance
store8 8270000000000000023 1
jmp c14_next_44
label c14_match_44_advance
add r0 1
jmp c14_match_44_seek
label c14_next_44
cmp r9 10
jlt c14_next_45
set r0 0
label c14_match_45_seek
mov r8 r9
sub r8 10
cmp r0 r8
jgt c14_next_45
mov r7 r0
add r7 9190000000000001024
load8 r2 $r7
cmp r2 32
jne c14_match_45_advance
mov r7 r0
add r7 9190000000000001025
load8 r2 $r7
cmp r2 112
jne c14_match_45_advance
mov r7 r0
add r7 9190000000000001026
load8 r2 $r7
cmp r2 114
jne c14_match_45_advance
mov r7 r0
add r7 9190000000000001027
load8 r2 $r7
cmp r2 111
jne c14_match_45_advance
mov r7 r0
add r7 9190000000000001028
load8 r2 $r7
cmp r2 103
jne c14_match_45_advance
mov r7 r0
add r7 9190000000000001029
load8 r2 $r7
cmp r2 114
jne c14_match_45_advance
mov r7 r0
add r7 9190000000000001030
load8 r2 $r7
cmp r2 97
jne c14_match_45_advance
mov r7 r0
add r7 9190000000000001031
load8 r2 $r7
cmp r2 109
jne c14_match_45_advance
mov r7 r0
add r7 9190000000000001032
load8 r2 $r7
cmp r2 97
jne c14_match_45_advance
mov r7 r0
add r7 9190000000000001033
load8 r2 $r7
cmp r2 32
jne c14_match_45_advance
store8 8270000000000000023 1
jmp c14_next_45
label c14_match_45_advance
add r0 1
jmp c14_match_45_seek
label c14_next_45
cmp r9 8
jlt c14_next_46
set r0 0
label c14_match_46_seek
mov r8 r9
sub r8 8
cmp r0 r8
jgt c14_next_46
mov r7 r0
add r7 9190000000000001024
load8 r2 $r7
cmp r2 32
jne c14_match_46_advance
mov r7 r0
add r7 9190000000000001025
load8 r2 $r7
cmp r2 99
jne c14_match_46_advance
mov r7 r0
add r7 9190000000000001026
load8 r2 $r7
cmp r2 111
jne c14_match_46_advance
mov r7 r0
add r7 9190000000000001027
load8 r2 $r7
cmp r2 100
jne c14_match_46_advance
mov r7 r0
add r7 9190000000000001028
load8 r2 $r7
cmp r2 105
jne c14_match_46_advance
mov r7 r0
add r7 9190000000000001029
load8 r2 $r7
cmp r2 103
jne c14_match_46_advance
mov r7 r0
add r7 9190000000000001030
load8 r2 $r7
cmp r2 111
jne c14_match_46_advance
mov r7 r0
add r7 9190000000000001031
load8 r2 $r7
cmp r2 32
jne c14_match_46_advance
store8 8270000000000000023 1
jmp c14_next_46
label c14_match_46_advance
add r0 1
jmp c14_match_46_seek
label c14_next_46
cmp r9 9
jlt c14_next_47
set r0 0
label c14_match_47_seek
mov r8 r9
sub r8 9
cmp r0 r8
jgt c14_next_47
mov r7 r0
add r7 9190000000000001024
load8 r2 $r7
cmp r2 32
jne c14_match_47_advance
mov r7 r0
add r7 9190000000000001025
load8 r2 $r7
cmp r2 105
jne c14_match_47_advance
mov r7 r0
add r7 9190000000000001026
load8 r2 $r7
cmp r2 110
jne c14_match_47_advance
mov r7 r0
add r7 9190000000000001027
load8 r2 $r7
cmp r2 115
jne c14_match_47_advance
mov r7 r0
add r7 9190000000000001028
load8 r2 $r7
cmp r2 116
jne c14_match_47_advance
mov r7 r0
add r7 9190000000000001029
load8 r2 $r7
cmp r2 97
jne c14_match_47_advance
mov r7 r0
add r7 9190000000000001030
load8 r2 $r7
cmp r2 108
jne c14_match_47_advance
mov r7 r0
add r7 9190000000000001031
load8 r2 $r7
cmp r2 97
jne c14_match_47_advance
mov r7 r0
add r7 9190000000000001032
load8 r2 $r7
cmp r2 32
jne c14_match_47_advance
store8 8270000000000000023 1
jmp c14_next_47
label c14_match_47_advance
add r0 1
jmp c14_match_47_seek
label c14_next_47
cmp r9 6
jlt c14_next_48
set r0 0
label c14_match_48_seek
mov r8 r9
sub r8 6
cmp r0 r8
jgt c14_next_48
mov r7 r0
add r7 9190000000000001024
load8 r2 $r7
cmp r2 32
jne c14_match_48_advance
mov r7 r0
add r7 9190000000000001025
load8 r2 $r7
cmp r2 97
jne c14_match_48_advance
mov r7 r0
add r7 9190000000000001026
load8 r2 $r7
cmp r2 98
jne c14_match_48_advance
mov r7 r0
add r7 9190000000000001027
load8 r2 $r7
cmp r2 114
jne c14_match_48_advance
mov r7 r0
add r7 9190000000000001028
load8 r2 $r7
cmp r2 101
jne c14_match_48_advance
mov r7 r0
add r7 9190000000000001029
load8 r2 $r7
cmp r2 32
jne c14_match_48_advance
store8 8270000000000000023 1
jmp c14_next_48
label c14_match_48_advance
add r0 1
jmp c14_match_48_seek
label c14_next_48
cmp r9 9
jlt c14_next_49
set r0 0
label c14_match_49_seek
mov r8 r9
sub r8 9
cmp r0 r8
jgt c14_next_49
mov r7 r0
add r7 9190000000000001024
load8 r2 $r7
cmp r2 32
jne c14_match_49_advance
mov r7 r0
add r7 9190000000000001025
load8 r2 $r7
cmp r2 99
jne c14_match_49_advance
mov r7 r0
add r7 9190000000000001026
load8 r2 $r7
cmp r2 111
jne c14_match_49_advance
mov r7 r0
add r7 9190000000000001027
load8 r2 $r7
cmp r2 109
jne c14_match_49_advance
mov r7 r0
add r7 9190000000000001028
load8 r2 $r7
cmp r2 97
jne c14_match_49_advance
mov r7 r0
add r7 9190000000000001029
load8 r2 $r7
cmp r2 110
jne c14_match_49_advance
mov r7 r0
add r7 9190000000000001030
load8 r2 $r7
cmp r2 100
jne c14_match_49_advance
mov r7 r0
add r7 9190000000000001031
load8 r2 $r7
cmp r2 111
jne c14_match_49_advance
mov r7 r0
add r7 9190000000000001032
load8 r2 $r7
cmp r2 32
jne c14_match_49_advance
store8 8270000000000000023 1
jmp c14_next_49
label c14_match_49_advance
add r0 1
jmp c14_match_49_seek
label c14_next_49
cmp r9 12
jlt c14_next_50
set r0 0
label c14_match_50_seek
mov r8 r9
sub r8 12
cmp r0 r8
jgt c14_next_50
mov r7 r0
add r7 9190000000000001024
load8 r2 $r7
cmp r2 32
jne c14_match_50_advance
mov r7 r0
add r7 9190000000000001025
load8 r2 $r7
cmp r2 97
jne c14_match_50_advance
mov r7 r0
add r7 9190000000000001026
load8 r2 $r7
cmp r2 112
jne c14_match_50_advance
mov r7 r0
add r7 9190000000000001027
load8 r2 $r7
cmp r2 108
jne c14_match_50_advance
mov r7 r0
add r7 9190000000000001028
load8 r2 $r7
cmp r2 105
jne c14_match_50_advance
mov r7 r0
add r7 9190000000000001029
load8 r2 $r7
cmp r2 99
jne c14_match_50_advance
mov r7 r0
add r7 9190000000000001030
load8 r2 $r7
cmp r2 97
jne c14_match_50_advance
mov r7 r0
add r7 9190000000000001031
load8 r2 $r7
cmp r2 99
jne c14_match_50_advance
mov r7 r0
add r7 9190000000000001032
load8 r2 $r7
cmp r2 105
jne c14_match_50_advance
mov r7 r0
add r7 9190000000000001033
load8 r2 $r7
cmp r2 111
jne c14_match_50_advance
mov r7 r0
add r7 9190000000000001034
load8 r2 $r7
cmp r2 110
jne c14_match_50_advance
mov r7 r0
add r7 9190000000000001035
load8 r2 $r7
cmp r2 32
jne c14_match_50_advance
store8 8270000000000000023 1
jmp c14_next_50
label c14_match_50_advance
add r0 1
jmp c14_match_50_seek
label c14_next_50
cmp r9 12
jlt c14_next_51
set r0 0
label c14_match_51_seek
mov r8 r9
sub r8 12
cmp r0 r8
jgt c14_next_51
mov r7 r0
add r7 9190000000000001024
load8 r2 $r7
cmp r2 32
jne c14_match_51_advance
mov r7 r0
add r7 9190000000000001025
load8 r2 $r7
cmp r2 101
jne c14_match_51_advance
mov r7 r0
add r7 9190000000000001026
load8 r2 $r7
cmp r2 106
jne c14_match_51_advance
mov r7 r0
add r7 9190000000000001027
load8 r2 $r7
cmp r2 101
jne c14_match_51_advance
mov r7 r0
add r7 9190000000000001028
load8 r2 $r7
cmp r2 99
jne c14_match_51_advance
mov r7 r0
add r7 9190000000000001029
load8 r2 $r7
cmp r2 117
jne c14_match_51_advance
mov r7 r0
add r7 9190000000000001030
load8 r2 $r7
cmp r2 116
jne c14_match_51_advance
mov r7 r0
add r7 9190000000000001031
load8 r2 $r7
cmp r2 97
jne c14_match_51_advance
mov r7 r0
add r7 9190000000000001032
load8 r2 $r7
cmp r2 98
jne c14_match_51_advance
mov r7 r0
add r7 9190000000000001033
load8 r2 $r7
cmp r2 108
jne c14_match_51_advance
mov r7 r0
add r7 9190000000000001034
load8 r2 $r7
cmp r2 101
jne c14_match_51_advance
mov r7 r0
add r7 9190000000000001035
load8 r2 $r7
cmp r2 32
jne c14_match_51_advance
store8 8270000000000000023 1
jmp c14_next_51
label c14_match_51_advance
add r0 1
jmp c14_match_51_seek
label c14_next_51
set r12 0
load8 r4 8270000000000000020
cmp r4 0
je c14_no_memory
add r12 1
label c14_no_memory
load8 r4 8270000000000000021
cmp r4 0
je c14_no_logic
add r12 2
label c14_no_logic
load8 r4 8270000000000000022
cmp r4 0
je c14_no_creative
add r12 4
label c14_no_creative
load8 r4 8270000000000000023
cmp r4 0
je c14_no_execute
add r12 8
label c14_no_execute
set r11 0
cmp r12 0
je c14_generic
cmp r12 1
je c14_memory
cmp r12 2
je c14_reasoning
cmp r12 4
je c14_creation
cmp r12 8
je c14_execution
set r11 4
jmp c14_guard
label c14_memory
set r11 1
jmp c14_guard
label c14_reasoning
set r11 2
jmp c14_guard
label c14_creation
set r11 3
jmp c14_guard
label c14_execution
set r11 5
jmp c14_guard
label c14_generic
load8 r3 9190000000000000128
cmp r3 3
jne c14_guard
set r11 6
label c14_guard
load8 r3 9190000000000000128
cmp r3 5
je c14_guarded
cmp r3 6
je c14_guarded
load8 r3 9190000000000000133
cmp r3 0
je c14_finish
cmp r12 0
je c14_finish
label c14_guarded
set r11 7
label c14_finish
store8 8270000000000000016 r11
load8 r3 9190000000000000128
cmp r3 8
jgt c14_bad
mul r3 8
add r3 r11
mul r3 2
add r3 r14
store8 8270000000000000018 r3
load8 r5 9190000000000000128
print r5
print r11
print r3
halt
label c14_bad
div r0 0
