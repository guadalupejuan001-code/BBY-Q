#!reverse-pc-machine-v1
# E028: XI-native question parsing, entity matching, provenance and composition.
# This module only interprets constrained supported forms; E027 and E025 remain fallback.
load8 r9 7400000000000000017
cmp r9 2
jlt e28_delegate
load8 r3 7400000000000000128
cmp r3 64
je e28_ctx_delegate
load8 r13 7400000000000000003
set r8 0
mov r10 r9
load8 r3 7400000000000000128
cmp r3 194
jne e28_trim
load8 r3 7400000000000000129
cmp r3 191
jne e28_trim
set r8 2
label e28_trim
cmp r10 r8
jle e28_delegate
mov r7 r10
sub r7 1
add r7 7400000000000000128
load8 r3 $r7
cmp r3 63
je e28_trim_drop
cmp r3 46
jne e28_form_0
label e28_trim_drop
sub r10 1
label e28_form_0
label e28_follow_0
mov r0 r8
add r0 14
cmp r0 r10
jgt e28_follow_1
mov r7 r8
add r7 7400000000000000128
load8 r3 $r7
cmp r3 65
jlt e28_follow_0_lc_0
cmp r3 90
jgt e28_follow_0_lc_0
add r3 32
label e28_follow_0_lc_0
cmp r3 121
jne e28_follow_1
mov r7 r8
add r7 1
add r7 7400000000000000128
load8 r3 $r7
cmp r3 65
jlt e28_follow_0_lc_1
cmp r3 90
jgt e28_follow_0_lc_1
add r3 32
label e28_follow_0_lc_1
cmp r3 32
jne e28_follow_1
mov r7 r8
add r7 2
add r7 7400000000000000128
load8 r3 $r7
cmp r3 65
jlt e28_follow_0_lc_2
cmp r3 90
jgt e28_follow_0_lc_2
add r3 32
label e28_follow_0_lc_2
cmp r3 113
jne e28_follow_1
mov r7 r8
add r7 3
add r7 7400000000000000128
load8 r3 $r7
cmp r3 65
jlt e28_follow_0_lc_3
cmp r3 90
jgt e28_follow_0_lc_3
add r3 32
label e28_follow_0_lc_3
cmp r3 117
jne e28_follow_1
mov r7 r8
add r7 4
add r7 7400000000000000128
load8 r3 $r7
cmp r3 65
jlt e28_follow_0_lc_4
cmp r3 90
jgt e28_follow_0_lc_4
add r3 32
label e28_follow_0_lc_4
cmp r3 101
jne e28_follow_1
mov r7 r8
add r7 5
add r7 7400000000000000128
load8 r3 $r7
cmp r3 65
jlt e28_follow_0_lc_5
cmp r3 90
jgt e28_follow_0_lc_5
add r3 32
label e28_follow_0_lc_5
cmp r3 32
jne e28_follow_1
mov r7 r8
add r7 6
add r7 7400000000000000128
load8 r3 $r7
cmp r3 65
jlt e28_follow_0_lc_6
cmp r3 90
jgt e28_follow_0_lc_6
add r3 32
label e28_follow_0_lc_6
cmp r3 114
jne e28_follow_1
mov r7 r8
add r7 7
add r7 7400000000000000128
load8 r3 $r7
cmp r3 65
jlt e28_follow_0_lc_7
cmp r3 90
jgt e28_follow_0_lc_7
add r3 32
label e28_follow_0_lc_7
cmp r3 101
jne e28_follow_1
mov r7 r8
add r7 8
add r7 7400000000000000128
load8 r3 $r7
cmp r3 65
jlt e28_follow_0_lc_8
cmp r3 90
jgt e28_follow_0_lc_8
add r3 32
label e28_follow_0_lc_8
cmp r3 113
jne e28_follow_1
mov r7 r8
add r7 9
add r7 7400000000000000128
load8 r3 $r7
cmp r3 65
jlt e28_follow_0_lc_9
cmp r3 90
jgt e28_follow_0_lc_9
add r3 32
label e28_follow_0_lc_9
cmp r3 117
jne e28_follow_1
mov r7 r8
add r7 10
add r7 7400000000000000128
load8 r3 $r7
cmp r3 65
jlt e28_follow_0_lc_10
cmp r3 90
jgt e28_follow_0_lc_10
add r3 32
label e28_follow_0_lc_10
cmp r3 105
jne e28_follow_1
mov r7 r8
add r7 11
add r7 7400000000000000128
load8 r3 $r7
cmp r3 65
jlt e28_follow_0_lc_11
cmp r3 90
jgt e28_follow_0_lc_11
add r3 32
label e28_follow_0_lc_11
cmp r3 101
jne e28_follow_1
mov r7 r8
add r7 12
add r7 7400000000000000128
load8 r3 $r7
cmp r3 65
jlt e28_follow_0_lc_12
cmp r3 90
jgt e28_follow_0_lc_12
add r3 32
label e28_follow_0_lc_12
cmp r3 114
jne e28_follow_1
mov r7 r8
add r7 13
add r7 7400000000000000128
load8 r3 $r7
cmp r3 65
jlt e28_follow_0_lc_13
cmp r3 90
jgt e28_follow_0_lc_13
add r3 32
label e28_follow_0_lc_13
cmp r3 101
jne e28_follow_1
mov r0 r8
add r0 14
cmp r0 r10
jne e28_follow_1
set r11 2
set r12 0
jmp e28_context_follow
label e28_follow_1
mov r0 r8
add r0 15
cmp r0 r10
jgt e28_follow_2
mov r7 r8
add r7 7400000000000000128
load8 r3 $r7
cmp r3 65
jlt e28_follow_1_lc_0
cmp r3 90
jgt e28_follow_1_lc_0
add r3 32
label e28_follow_1_lc_0
cmp r3 121
jne e28_follow_2
mov r7 r8
add r7 1
add r7 7400000000000000128
load8 r3 $r7
cmp r3 65
jlt e28_follow_1_lc_1
cmp r3 90
jgt e28_follow_1_lc_1
add r3 32
label e28_follow_1_lc_1
cmp r3 32
jne e28_follow_2
mov r7 r8
add r7 2
add r7 7400000000000000128
load8 r3 $r7
cmp r3 65
jlt e28_follow_1_lc_2
cmp r3 90
jgt e28_follow_1_lc_2
add r3 32
label e28_follow_1_lc_2
cmp r3 113
jne e28_follow_2
mov r7 r8
add r7 3
add r7 7400000000000000128
load8 r3 $r7
cmp r3 65
jlt e28_follow_1_lc_3
cmp r3 90
jgt e28_follow_1_lc_3
add r3 32
label e28_follow_1_lc_3
cmp r3 117
jne e28_follow_2
mov r7 r8
add r7 4
add r7 7400000000000000128
load8 r3 $r7
cmp r3 65
jlt e28_follow_1_lc_4
cmp r3 90
jgt e28_follow_1_lc_4
add r3 32
label e28_follow_1_lc_4
cmp r3 195
jne e28_follow_2
mov r7 r8
add r7 5
add r7 7400000000000000128
load8 r3 $r7
cmp r3 65
jlt e28_follow_1_lc_5
cmp r3 90
jgt e28_follow_1_lc_5
add r3 32
label e28_follow_1_lc_5
cmp r3 169
jne e28_follow_2
mov r7 r8
add r7 6
add r7 7400000000000000128
load8 r3 $r7
cmp r3 65
jlt e28_follow_1_lc_6
cmp r3 90
jgt e28_follow_1_lc_6
add r3 32
label e28_follow_1_lc_6
cmp r3 32
jne e28_follow_2
mov r7 r8
add r7 7
add r7 7400000000000000128
load8 r3 $r7
cmp r3 65
jlt e28_follow_1_lc_7
cmp r3 90
jgt e28_follow_1_lc_7
add r3 32
label e28_follow_1_lc_7
cmp r3 114
jne e28_follow_2
mov r7 r8
add r7 8
add r7 7400000000000000128
load8 r3 $r7
cmp r3 65
jlt e28_follow_1_lc_8
cmp r3 90
jgt e28_follow_1_lc_8
add r3 32
label e28_follow_1_lc_8
cmp r3 101
jne e28_follow_2
mov r7 r8
add r7 9
add r7 7400000000000000128
load8 r3 $r7
cmp r3 65
jlt e28_follow_1_lc_9
cmp r3 90
jgt e28_follow_1_lc_9
add r3 32
label e28_follow_1_lc_9
cmp r3 113
jne e28_follow_2
mov r7 r8
add r7 10
add r7 7400000000000000128
load8 r3 $r7
cmp r3 65
jlt e28_follow_1_lc_10
cmp r3 90
jgt e28_follow_1_lc_10
add r3 32
label e28_follow_1_lc_10
cmp r3 117
jne e28_follow_2
mov r7 r8
add r7 11
add r7 7400000000000000128
load8 r3 $r7
cmp r3 65
jlt e28_follow_1_lc_11
cmp r3 90
jgt e28_follow_1_lc_11
add r3 32
label e28_follow_1_lc_11
cmp r3 105
jne e28_follow_2
mov r7 r8
add r7 12
add r7 7400000000000000128
load8 r3 $r7
cmp r3 65
jlt e28_follow_1_lc_12
cmp r3 90
jgt e28_follow_1_lc_12
add r3 32
label e28_follow_1_lc_12
cmp r3 101
jne e28_follow_2
mov r7 r8
add r7 13
add r7 7400000000000000128
load8 r3 $r7
cmp r3 65
jlt e28_follow_1_lc_13
cmp r3 90
jgt e28_follow_1_lc_13
add r3 32
label e28_follow_1_lc_13
cmp r3 114
jne e28_follow_2
mov r7 r8
add r7 14
add r7 7400000000000000128
load8 r3 $r7
cmp r3 65
jlt e28_follow_1_lc_14
cmp r3 90
jgt e28_follow_1_lc_14
add r3 32
label e28_follow_1_lc_14
cmp r3 101
jne e28_follow_2
mov r0 r8
add r0 15
cmp r0 r10
jne e28_follow_2
set r11 2
set r12 0
jmp e28_context_follow
label e28_follow_2
mov r0 r8
add r0 14
cmp r0 r10
jgt e28_follow_3
mov r7 r8
add r7 7400000000000000128
load8 r3 $r7
cmp r3 65
jlt e28_follow_2_lc_0
cmp r3 90
jgt e28_follow_2_lc_0
add r3 32
label e28_follow_2_lc_0
cmp r3 121
jne e28_follow_3
mov r7 r8
add r7 1
add r7 7400000000000000128
load8 r3 $r7
cmp r3 65
jlt e28_follow_2_lc_1
cmp r3 90
jgt e28_follow_2_lc_1
add r3 32
label e28_follow_2_lc_1
cmp r3 32
jne e28_follow_3
mov r7 r8
add r7 2
add r7 7400000000000000128
load8 r3 $r7
cmp r3 65
jlt e28_follow_2_lc_2
cmp r3 90
jgt e28_follow_2_lc_2
add r3 32
label e28_follow_2_lc_2
cmp r3 113
jne e28_follow_3
mov r7 r8
add r7 3
add r7 7400000000000000128
load8 r3 $r7
cmp r3 65
jlt e28_follow_2_lc_3
cmp r3 90
jgt e28_follow_2_lc_3
add r3 32
label e28_follow_2_lc_3
cmp r3 117
jne e28_follow_3
mov r7 r8
add r7 4
add r7 7400000000000000128
load8 r3 $r7
cmp r3 65
jlt e28_follow_2_lc_4
cmp r3 90
jgt e28_follow_2_lc_4
add r3 32
label e28_follow_2_lc_4
cmp r3 101
jne e28_follow_3
mov r7 r8
add r7 5
add r7 7400000000000000128
load8 r3 $r7
cmp r3 65
jlt e28_follow_2_lc_5
cmp r3 90
jgt e28_follow_2_lc_5
add r3 32
label e28_follow_2_lc_5
cmp r3 32
jne e28_follow_3
mov r7 r8
add r7 6
add r7 7400000000000000128
load8 r3 $r7
cmp r3 65
jlt e28_follow_2_lc_6
cmp r3 90
jgt e28_follow_2_lc_6
add r3 32
label e28_follow_2_lc_6
cmp r3 110
jne e28_follow_3
mov r7 r8
add r7 7
add r7 7400000000000000128
load8 r3 $r7
cmp r3 65
jlt e28_follow_2_lc_7
cmp r3 90
jgt e28_follow_2_lc_7
add r3 32
label e28_follow_2_lc_7
cmp r3 101
jne e28_follow_3
mov r7 r8
add r7 8
add r7 7400000000000000128
load8 r3 $r7
cmp r3 65
jlt e28_follow_2_lc_8
cmp r3 90
jgt e28_follow_2_lc_8
add r3 32
label e28_follow_2_lc_8
cmp r3 99
jne e28_follow_3
mov r7 r8
add r7 9
add r7 7400000000000000128
load8 r3 $r7
cmp r3 65
jlt e28_follow_2_lc_9
cmp r3 90
jgt e28_follow_2_lc_9
add r3 32
label e28_follow_2_lc_9
cmp r3 101
jne e28_follow_3
mov r7 r8
add r7 10
add r7 7400000000000000128
load8 r3 $r7
cmp r3 65
jlt e28_follow_2_lc_10
cmp r3 90
jgt e28_follow_2_lc_10
add r3 32
label e28_follow_2_lc_10
cmp r3 115
jne e28_follow_3
mov r7 r8
add r7 11
add r7 7400000000000000128
load8 r3 $r7
cmp r3 65
jlt e28_follow_2_lc_11
cmp r3 90
jgt e28_follow_2_lc_11
add r3 32
label e28_follow_2_lc_11
cmp r3 105
jne e28_follow_3
mov r7 r8
add r7 12
add r7 7400000000000000128
load8 r3 $r7
cmp r3 65
jlt e28_follow_2_lc_12
cmp r3 90
jgt e28_follow_2_lc_12
add r3 32
label e28_follow_2_lc_12
cmp r3 116
jne e28_follow_3
mov r7 r8
add r7 13
add r7 7400000000000000128
load8 r3 $r7
cmp r3 65
jlt e28_follow_2_lc_13
cmp r3 90
jgt e28_follow_2_lc_13
add r3 32
label e28_follow_2_lc_13
cmp r3 97
jne e28_follow_3
mov r0 r8
add r0 14
cmp r0 r10
jne e28_follow_3
set r11 2
set r12 0
jmp e28_context_follow
label e28_follow_3
mov r0 r8
add r0 15
cmp r0 r10
jgt e28_follow_4
mov r7 r8
add r7 7400000000000000128
load8 r3 $r7
cmp r3 65
jlt e28_follow_3_lc_0
cmp r3 90
jgt e28_follow_3_lc_0
add r3 32
label e28_follow_3_lc_0
cmp r3 121
jne e28_follow_4
mov r7 r8
add r7 1
add r7 7400000000000000128
load8 r3 $r7
cmp r3 65
jlt e28_follow_3_lc_1
cmp r3 90
jgt e28_follow_3_lc_1
add r3 32
label e28_follow_3_lc_1
cmp r3 32
jne e28_follow_4
mov r7 r8
add r7 2
add r7 7400000000000000128
load8 r3 $r7
cmp r3 65
jlt e28_follow_3_lc_2
cmp r3 90
jgt e28_follow_3_lc_2
add r3 32
label e28_follow_3_lc_2
cmp r3 113
jne e28_follow_4
mov r7 r8
add r7 3
add r7 7400000000000000128
load8 r3 $r7
cmp r3 65
jlt e28_follow_3_lc_3
cmp r3 90
jgt e28_follow_3_lc_3
add r3 32
label e28_follow_3_lc_3
cmp r3 117
jne e28_follow_4
mov r7 r8
add r7 4
add r7 7400000000000000128
load8 r3 $r7
cmp r3 65
jlt e28_follow_3_lc_4
cmp r3 90
jgt e28_follow_3_lc_4
add r3 32
label e28_follow_3_lc_4
cmp r3 195
jne e28_follow_4
mov r7 r8
add r7 5
add r7 7400000000000000128
load8 r3 $r7
cmp r3 65
jlt e28_follow_3_lc_5
cmp r3 90
jgt e28_follow_3_lc_5
add r3 32
label e28_follow_3_lc_5
cmp r3 169
jne e28_follow_4
mov r7 r8
add r7 6
add r7 7400000000000000128
load8 r3 $r7
cmp r3 65
jlt e28_follow_3_lc_6
cmp r3 90
jgt e28_follow_3_lc_6
add r3 32
label e28_follow_3_lc_6
cmp r3 32
jne e28_follow_4
mov r7 r8
add r7 7
add r7 7400000000000000128
load8 r3 $r7
cmp r3 65
jlt e28_follow_3_lc_7
cmp r3 90
jgt e28_follow_3_lc_7
add r3 32
label e28_follow_3_lc_7
cmp r3 110
jne e28_follow_4
mov r7 r8
add r7 8
add r7 7400000000000000128
load8 r3 $r7
cmp r3 65
jlt e28_follow_3_lc_8
cmp r3 90
jgt e28_follow_3_lc_8
add r3 32
label e28_follow_3_lc_8
cmp r3 101
jne e28_follow_4
mov r7 r8
add r7 9
add r7 7400000000000000128
load8 r3 $r7
cmp r3 65
jlt e28_follow_3_lc_9
cmp r3 90
jgt e28_follow_3_lc_9
add r3 32
label e28_follow_3_lc_9
cmp r3 99
jne e28_follow_4
mov r7 r8
add r7 10
add r7 7400000000000000128
load8 r3 $r7
cmp r3 65
jlt e28_follow_3_lc_10
cmp r3 90
jgt e28_follow_3_lc_10
add r3 32
label e28_follow_3_lc_10
cmp r3 101
jne e28_follow_4
mov r7 r8
add r7 11
add r7 7400000000000000128
load8 r3 $r7
cmp r3 65
jlt e28_follow_3_lc_11
cmp r3 90
jgt e28_follow_3_lc_11
add r3 32
label e28_follow_3_lc_11
cmp r3 115
jne e28_follow_4
mov r7 r8
add r7 12
add r7 7400000000000000128
load8 r3 $r7
cmp r3 65
jlt e28_follow_3_lc_12
cmp r3 90
jgt e28_follow_3_lc_12
add r3 32
label e28_follow_3_lc_12
cmp r3 105
jne e28_follow_4
mov r7 r8
add r7 13
add r7 7400000000000000128
load8 r3 $r7
cmp r3 65
jlt e28_follow_3_lc_13
cmp r3 90
jgt e28_follow_3_lc_13
add r3 32
label e28_follow_3_lc_13
cmp r3 116
jne e28_follow_4
mov r7 r8
add r7 14
add r7 7400000000000000128
load8 r3 $r7
cmp r3 65
jlt e28_follow_3_lc_14
cmp r3 90
jgt e28_follow_3_lc_14
add r3 32
label e28_follow_3_lc_14
cmp r3 97
jne e28_follow_4
mov r0 r8
add r0 15
cmp r0 r10
jne e28_follow_4
set r11 2
set r12 0
jmp e28_context_follow
label e28_follow_4
mov r0 r8
add r0 21
cmp r0 r10
jgt e28_follow_5
mov r7 r8
add r7 7400000000000000128
load8 r3 $r7
cmp r3 65
jlt e28_follow_4_lc_0
cmp r3 90
jgt e28_follow_4_lc_0
add r3 32
label e28_follow_4_lc_0
cmp r3 97
jne e28_follow_5
mov r7 r8
add r7 1
add r7 7400000000000000128
load8 r3 $r7
cmp r3 65
jlt e28_follow_4_lc_1
cmp r3 90
jgt e28_follow_4_lc_1
add r3 32
label e28_follow_4_lc_1
cmp r3 110
jne e28_follow_5
mov r7 r8
add r7 2
add r7 7400000000000000128
load8 r3 $r7
cmp r3 65
jlt e28_follow_4_lc_2
cmp r3 90
jgt e28_follow_4_lc_2
add r3 32
label e28_follow_4_lc_2
cmp r3 100
jne e28_follow_5
mov r7 r8
add r7 3
add r7 7400000000000000128
load8 r3 $r7
cmp r3 65
jlt e28_follow_4_lc_3
cmp r3 90
jgt e28_follow_4_lc_3
add r3 32
label e28_follow_4_lc_3
cmp r3 32
jne e28_follow_5
mov r7 r8
add r7 4
add r7 7400000000000000128
load8 r3 $r7
cmp r3 65
jlt e28_follow_4_lc_4
cmp r3 90
jgt e28_follow_4_lc_4
add r3 32
label e28_follow_4_lc_4
cmp r3 119
jne e28_follow_5
mov r7 r8
add r7 5
add r7 7400000000000000128
load8 r3 $r7
cmp r3 65
jlt e28_follow_4_lc_5
cmp r3 90
jgt e28_follow_4_lc_5
add r3 32
label e28_follow_4_lc_5
cmp r3 104
jne e28_follow_5
mov r7 r8
add r7 6
add r7 7400000000000000128
load8 r3 $r7
cmp r3 65
jlt e28_follow_4_lc_6
cmp r3 90
jgt e28_follow_4_lc_6
add r3 32
label e28_follow_4_lc_6
cmp r3 97
jne e28_follow_5
mov r7 r8
add r7 7
add r7 7400000000000000128
load8 r3 $r7
cmp r3 65
jlt e28_follow_4_lc_7
cmp r3 90
jgt e28_follow_4_lc_7
add r3 32
label e28_follow_4_lc_7
cmp r3 116
jne e28_follow_5
mov r7 r8
add r7 8
add r7 7400000000000000128
load8 r3 $r7
cmp r3 65
jlt e28_follow_4_lc_8
cmp r3 90
jgt e28_follow_4_lc_8
add r3 32
label e28_follow_4_lc_8
cmp r3 32
jne e28_follow_5
mov r7 r8
add r7 9
add r7 7400000000000000128
load8 r3 $r7
cmp r3 65
jlt e28_follow_4_lc_9
cmp r3 90
jgt e28_follow_4_lc_9
add r3 32
label e28_follow_4_lc_9
cmp r3 100
jne e28_follow_5
mov r7 r8
add r7 10
add r7 7400000000000000128
load8 r3 $r7
cmp r3 65
jlt e28_follow_4_lc_10
cmp r3 90
jgt e28_follow_4_lc_10
add r3 32
label e28_follow_4_lc_10
cmp r3 111
jne e28_follow_5
mov r7 r8
add r7 11
add r7 7400000000000000128
load8 r3 $r7
cmp r3 65
jlt e28_follow_4_lc_11
cmp r3 90
jgt e28_follow_4_lc_11
add r3 32
label e28_follow_4_lc_11
cmp r3 101
jne e28_follow_5
mov r7 r8
add r7 12
add r7 7400000000000000128
load8 r3 $r7
cmp r3 65
jlt e28_follow_4_lc_12
cmp r3 90
jgt e28_follow_4_lc_12
add r3 32
label e28_follow_4_lc_12
cmp r3 115
jne e28_follow_5
mov r7 r8
add r7 13
add r7 7400000000000000128
load8 r3 $r7
cmp r3 65
jlt e28_follow_4_lc_13
cmp r3 90
jgt e28_follow_4_lc_13
add r3 32
label e28_follow_4_lc_13
cmp r3 32
jne e28_follow_5
mov r7 r8
add r7 14
add r7 7400000000000000128
load8 r3 $r7
cmp r3 65
jlt e28_follow_4_lc_14
cmp r3 90
jgt e28_follow_4_lc_14
add r3 32
label e28_follow_4_lc_14
cmp r3 105
jne e28_follow_5
mov r7 r8
add r7 15
add r7 7400000000000000128
load8 r3 $r7
cmp r3 65
jlt e28_follow_4_lc_15
cmp r3 90
jgt e28_follow_4_lc_15
add r3 32
label e28_follow_4_lc_15
cmp r3 116
jne e28_follow_5
mov r7 r8
add r7 16
add r7 7400000000000000128
load8 r3 $r7
cmp r3 65
jlt e28_follow_4_lc_16
cmp r3 90
jgt e28_follow_4_lc_16
add r3 32
label e28_follow_4_lc_16
cmp r3 32
jne e28_follow_5
mov r7 r8
add r7 17
add r7 7400000000000000128
load8 r3 $r7
cmp r3 65
jlt e28_follow_4_lc_17
cmp r3 90
jgt e28_follow_4_lc_17
add r3 32
label e28_follow_4_lc_17
cmp r3 110
jne e28_follow_5
mov r7 r8
add r7 18
add r7 7400000000000000128
load8 r3 $r7
cmp r3 65
jlt e28_follow_4_lc_18
cmp r3 90
jgt e28_follow_4_lc_18
add r3 32
label e28_follow_4_lc_18
cmp r3 101
jne e28_follow_5
mov r7 r8
add r7 19
add r7 7400000000000000128
load8 r3 $r7
cmp r3 65
jlt e28_follow_4_lc_19
cmp r3 90
jgt e28_follow_4_lc_19
add r3 32
label e28_follow_4_lc_19
cmp r3 101
jne e28_follow_5
mov r7 r8
add r7 20
add r7 7400000000000000128
load8 r3 $r7
cmp r3 65
jlt e28_follow_4_lc_20
cmp r3 90
jgt e28_follow_4_lc_20
add r3 32
label e28_follow_4_lc_20
cmp r3 100
jne e28_follow_5
mov r0 r8
add r0 21
cmp r0 r10
jne e28_follow_5
set r11 2
set r12 0
jmp e28_context_follow
label e28_follow_5
mov r0 r8
add r0 24
cmp r0 r10
jgt e28_follow_6
mov r7 r8
add r7 7400000000000000128
load8 r3 $r7
cmp r3 65
jlt e28_follow_5_lc_0
cmp r3 90
jgt e28_follow_5_lc_0
add r3 32
label e28_follow_5_lc_0
cmp r3 97
jne e28_follow_6
mov r7 r8
add r7 1
add r7 7400000000000000128
load8 r3 $r7
cmp r3 65
jlt e28_follow_5_lc_1
cmp r3 90
jgt e28_follow_5_lc_1
add r3 32
label e28_follow_5_lc_1
cmp r3 110
jne e28_follow_6
mov r7 r8
add r7 2
add r7 7400000000000000128
load8 r3 $r7
cmp r3 65
jlt e28_follow_5_lc_2
cmp r3 90
jgt e28_follow_5_lc_2
add r3 32
label e28_follow_5_lc_2
cmp r3 100
jne e28_follow_6
mov r7 r8
add r7 3
add r7 7400000000000000128
load8 r3 $r7
cmp r3 65
jlt e28_follow_5_lc_3
cmp r3 90
jgt e28_follow_5_lc_3
add r3 32
label e28_follow_5_lc_3
cmp r3 32
jne e28_follow_6
mov r7 r8
add r7 4
add r7 7400000000000000128
load8 r3 $r7
cmp r3 65
jlt e28_follow_5_lc_4
cmp r3 90
jgt e28_follow_5_lc_4
add r3 32
label e28_follow_5_lc_4
cmp r3 119
jne e28_follow_6
mov r7 r8
add r7 5
add r7 7400000000000000128
load8 r3 $r7
cmp r3 65
jlt e28_follow_5_lc_5
cmp r3 90
jgt e28_follow_5_lc_5
add r3 32
label e28_follow_5_lc_5
cmp r3 104
jne e28_follow_6
mov r7 r8
add r7 6
add r7 7400000000000000128
load8 r3 $r7
cmp r3 65
jlt e28_follow_5_lc_6
cmp r3 90
jgt e28_follow_5_lc_6
add r3 32
label e28_follow_5_lc_6
cmp r3 97
jne e28_follow_6
mov r7 r8
add r7 7
add r7 7400000000000000128
load8 r3 $r7
cmp r3 65
jlt e28_follow_5_lc_7
cmp r3 90
jgt e28_follow_5_lc_7
add r3 32
label e28_follow_5_lc_7
cmp r3 116
jne e28_follow_6
mov r7 r8
add r7 8
add r7 7400000000000000128
load8 r3 $r7
cmp r3 65
jlt e28_follow_5_lc_8
cmp r3 90
jgt e28_follow_5_lc_8
add r3 32
label e28_follow_5_lc_8
cmp r3 32
jne e28_follow_6
mov r7 r8
add r7 9
add r7 7400000000000000128
load8 r3 $r7
cmp r3 65
jlt e28_follow_5_lc_9
cmp r3 90
jgt e28_follow_5_lc_9
add r3 32
label e28_follow_5_lc_9
cmp r3 100
jne e28_follow_6
mov r7 r8
add r7 10
add r7 7400000000000000128
load8 r3 $r7
cmp r3 65
jlt e28_follow_5_lc_10
cmp r3 90
jgt e28_follow_5_lc_10
add r3 32
label e28_follow_5_lc_10
cmp r3 111
jne e28_follow_6
mov r7 r8
add r7 11
add r7 7400000000000000128
load8 r3 $r7
cmp r3 65
jlt e28_follow_5_lc_11
cmp r3 90
jgt e28_follow_5_lc_11
add r3 32
label e28_follow_5_lc_11
cmp r3 101
jne e28_follow_6
mov r7 r8
add r7 12
add r7 7400000000000000128
load8 r3 $r7
cmp r3 65
jlt e28_follow_5_lc_12
cmp r3 90
jgt e28_follow_5_lc_12
add r3 32
label e28_follow_5_lc_12
cmp r3 115
jne e28_follow_6
mov r7 r8
add r7 13
add r7 7400000000000000128
load8 r3 $r7
cmp r3 65
jlt e28_follow_5_lc_13
cmp r3 90
jgt e28_follow_5_lc_13
add r3 32
label e28_follow_5_lc_13
cmp r3 32
jne e28_follow_6
mov r7 r8
add r7 14
add r7 7400000000000000128
load8 r3 $r7
cmp r3 65
jlt e28_follow_5_lc_14
cmp r3 90
jgt e28_follow_5_lc_14
add r3 32
label e28_follow_5_lc_14
cmp r3 105
jne e28_follow_6
mov r7 r8
add r7 15
add r7 7400000000000000128
load8 r3 $r7
cmp r3 65
jlt e28_follow_5_lc_15
cmp r3 90
jgt e28_follow_5_lc_15
add r3 32
label e28_follow_5_lc_15
cmp r3 116
jne e28_follow_6
mov r7 r8
add r7 16
add r7 7400000000000000128
load8 r3 $r7
cmp r3 65
jlt e28_follow_5_lc_16
cmp r3 90
jgt e28_follow_5_lc_16
add r3 32
label e28_follow_5_lc_16
cmp r3 32
jne e28_follow_6
mov r7 r8
add r7 17
add r7 7400000000000000128
load8 r3 $r7
cmp r3 65
jlt e28_follow_5_lc_17
cmp r3 90
jgt e28_follow_5_lc_17
add r3 32
label e28_follow_5_lc_17
cmp r3 114
jne e28_follow_6
mov r7 r8
add r7 18
add r7 7400000000000000128
load8 r3 $r7
cmp r3 65
jlt e28_follow_5_lc_18
cmp r3 90
jgt e28_follow_5_lc_18
add r3 32
label e28_follow_5_lc_18
cmp r3 101
jne e28_follow_6
mov r7 r8
add r7 19
add r7 7400000000000000128
load8 r3 $r7
cmp r3 65
jlt e28_follow_5_lc_19
cmp r3 90
jgt e28_follow_5_lc_19
add r3 32
label e28_follow_5_lc_19
cmp r3 113
jne e28_follow_6
mov r7 r8
add r7 20
add r7 7400000000000000128
load8 r3 $r7
cmp r3 65
jlt e28_follow_5_lc_20
cmp r3 90
jgt e28_follow_5_lc_20
add r3 32
label e28_follow_5_lc_20
cmp r3 117
jne e28_follow_6
mov r7 r8
add r7 21
add r7 7400000000000000128
load8 r3 $r7
cmp r3 65
jlt e28_follow_5_lc_21
cmp r3 90
jgt e28_follow_5_lc_21
add r3 32
label e28_follow_5_lc_21
cmp r3 105
jne e28_follow_6
mov r7 r8
add r7 22
add r7 7400000000000000128
load8 r3 $r7
cmp r3 65
jlt e28_follow_5_lc_22
cmp r3 90
jgt e28_follow_5_lc_22
add r3 32
label e28_follow_5_lc_22
cmp r3 114
jne e28_follow_6
mov r7 r8
add r7 23
add r7 7400000000000000128
load8 r3 $r7
cmp r3 65
jlt e28_follow_5_lc_23
cmp r3 90
jgt e28_follow_5_lc_23
add r3 32
label e28_follow_5_lc_23
cmp r3 101
jne e28_follow_6
mov r0 r8
add r0 24
cmp r0 r10
jne e28_follow_6
set r11 2
set r12 0
jmp e28_context_follow
label e28_follow_6
label e28_q_0
mov r0 r8
add r0 7
cmp r0 r10
jgt e28_q_1
mov r7 r8
add r7 7400000000000000128
load8 r3 $r7
cmp r3 65
jlt e28_q_0_lc_0
cmp r3 90
jgt e28_q_0_lc_0
add r3 32
label e28_q_0_lc_0
cmp r3 113
jne e28_q_1
mov r7 r8
add r7 1
add r7 7400000000000000128
load8 r3 $r7
cmp r3 65
jlt e28_q_0_lc_1
cmp r3 90
jgt e28_q_0_lc_1
add r3 32
label e28_q_0_lc_1
cmp r3 117
jne e28_q_1
mov r7 r8
add r7 2
add r7 7400000000000000128
load8 r3 $r7
cmp r3 65
jlt e28_q_0_lc_2
cmp r3 90
jgt e28_q_0_lc_2
add r3 32
label e28_q_0_lc_2
cmp r3 101
jne e28_q_1
mov r7 r8
add r7 3
add r7 7400000000000000128
load8 r3 $r7
cmp r3 65
jlt e28_q_0_lc_3
cmp r3 90
jgt e28_q_0_lc_3
add r3 32
label e28_q_0_lc_3
cmp r3 32
jne e28_q_1
mov r7 r8
add r7 4
add r7 7400000000000000128
load8 r3 $r7
cmp r3 65
jlt e28_q_0_lc_4
cmp r3 90
jgt e28_q_0_lc_4
add r3 32
label e28_q_0_lc_4
cmp r3 101
jne e28_q_1
mov r7 r8
add r7 5
add r7 7400000000000000128
load8 r3 $r7
cmp r3 65
jlt e28_q_0_lc_5
cmp r3 90
jgt e28_q_0_lc_5
add r3 32
label e28_q_0_lc_5
cmp r3 115
jne e28_q_1
mov r7 r8
add r7 6
add r7 7400000000000000128
load8 r3 $r7
cmp r3 65
jlt e28_q_0_lc_6
cmp r3 90
jgt e28_q_0_lc_6
add r3 32
label e28_q_0_lc_6
cmp r3 32
jne e28_q_1
mov r4 r8
add r4 7
set r11 1
set r12 0
jmp e28_tail_parse
label e28_q_1
mov r0 r8
add r0 8
cmp r0 r10
jgt e28_q_2
mov r7 r8
add r7 7400000000000000128
load8 r3 $r7
cmp r3 65
jlt e28_q_1_lc_0
cmp r3 90
jgt e28_q_1_lc_0
add r3 32
label e28_q_1_lc_0
cmp r3 113
jne e28_q_2
mov r7 r8
add r7 1
add r7 7400000000000000128
load8 r3 $r7
cmp r3 65
jlt e28_q_1_lc_1
cmp r3 90
jgt e28_q_1_lc_1
add r3 32
label e28_q_1_lc_1
cmp r3 117
jne e28_q_2
mov r7 r8
add r7 2
add r7 7400000000000000128
load8 r3 $r7
cmp r3 65
jlt e28_q_1_lc_2
cmp r3 90
jgt e28_q_1_lc_2
add r3 32
label e28_q_1_lc_2
cmp r3 195
jne e28_q_2
mov r7 r8
add r7 3
add r7 7400000000000000128
load8 r3 $r7
cmp r3 65
jlt e28_q_1_lc_3
cmp r3 90
jgt e28_q_1_lc_3
add r3 32
label e28_q_1_lc_3
cmp r3 169
jne e28_q_2
mov r7 r8
add r7 4
add r7 7400000000000000128
load8 r3 $r7
cmp r3 65
jlt e28_q_1_lc_4
cmp r3 90
jgt e28_q_1_lc_4
add r3 32
label e28_q_1_lc_4
cmp r3 32
jne e28_q_2
mov r7 r8
add r7 5
add r7 7400000000000000128
load8 r3 $r7
cmp r3 65
jlt e28_q_1_lc_5
cmp r3 90
jgt e28_q_1_lc_5
add r3 32
label e28_q_1_lc_5
cmp r3 101
jne e28_q_2
mov r7 r8
add r7 6
add r7 7400000000000000128
load8 r3 $r7
cmp r3 65
jlt e28_q_1_lc_6
cmp r3 90
jgt e28_q_1_lc_6
add r3 32
label e28_q_1_lc_6
cmp r3 115
jne e28_q_2
mov r7 r8
add r7 7
add r7 7400000000000000128
load8 r3 $r7
cmp r3 65
jlt e28_q_1_lc_7
cmp r3 90
jgt e28_q_1_lc_7
add r3 32
label e28_q_1_lc_7
cmp r3 32
jne e28_q_2
mov r4 r8
add r4 8
set r11 1
set r12 0
jmp e28_tail_parse
label e28_q_2
mov r0 r8
add r0 13
cmp r0 r10
jgt e28_q_3
mov r7 r8
add r7 7400000000000000128
load8 r3 $r7
cmp r3 65
jlt e28_q_2_lc_0
cmp r3 90
jgt e28_q_2_lc_0
add r3 32
label e28_q_2_lc_0
cmp r3 113
jne e28_q_3
mov r7 r8
add r7 1
add r7 7400000000000000128
load8 r3 $r7
cmp r3 65
jlt e28_q_2_lc_1
cmp r3 90
jgt e28_q_2_lc_1
add r3 32
label e28_q_2_lc_1
cmp r3 117
jne e28_q_3
mov r7 r8
add r7 2
add r7 7400000000000000128
load8 r3 $r7
cmp r3 65
jlt e28_q_2_lc_2
cmp r3 90
jgt e28_q_2_lc_2
add r3 32
label e28_q_2_lc_2
cmp r3 101
jne e28_q_3
mov r7 r8
add r7 3
add r7 7400000000000000128
load8 r3 $r7
cmp r3 65
jlt e28_q_2_lc_3
cmp r3 90
jgt e28_q_2_lc_3
add r3 32
label e28_q_2_lc_3
cmp r3 32
jne e28_q_3
mov r7 r8
add r7 4
add r7 7400000000000000128
load8 r3 $r7
cmp r3 65
jlt e28_q_2_lc_4
cmp r3 90
jgt e28_q_2_lc_4
add r3 32
label e28_q_2_lc_4
cmp r3 114
jne e28_q_3
mov r7 r8
add r7 5
add r7 7400000000000000128
load8 r3 $r7
cmp r3 65
jlt e28_q_2_lc_5
cmp r3 90
jgt e28_q_2_lc_5
add r3 32
label e28_q_2_lc_5
cmp r3 101
jne e28_q_3
mov r7 r8
add r7 6
add r7 7400000000000000128
load8 r3 $r7
cmp r3 65
jlt e28_q_2_lc_6
cmp r3 90
jgt e28_q_2_lc_6
add r3 32
label e28_q_2_lc_6
cmp r3 113
jne e28_q_3
mov r7 r8
add r7 7
add r7 7400000000000000128
load8 r3 $r7
cmp r3 65
jlt e28_q_2_lc_7
cmp r3 90
jgt e28_q_2_lc_7
add r3 32
label e28_q_2_lc_7
cmp r3 117
jne e28_q_3
mov r7 r8
add r7 8
add r7 7400000000000000128
load8 r3 $r7
cmp r3 65
jlt e28_q_2_lc_8
cmp r3 90
jgt e28_q_2_lc_8
add r3 32
label e28_q_2_lc_8
cmp r3 105
jne e28_q_3
mov r7 r8
add r7 9
add r7 7400000000000000128
load8 r3 $r7
cmp r3 65
jlt e28_q_2_lc_9
cmp r3 90
jgt e28_q_2_lc_9
add r3 32
label e28_q_2_lc_9
cmp r3 101
jne e28_q_3
mov r7 r8
add r7 10
add r7 7400000000000000128
load8 r3 $r7
cmp r3 65
jlt e28_q_2_lc_10
cmp r3 90
jgt e28_q_2_lc_10
add r3 32
label e28_q_2_lc_10
cmp r3 114
jne e28_q_3
mov r7 r8
add r7 11
add r7 7400000000000000128
load8 r3 $r7
cmp r3 65
jlt e28_q_2_lc_11
cmp r3 90
jgt e28_q_2_lc_11
add r3 32
label e28_q_2_lc_11
cmp r3 101
jne e28_q_3
mov r7 r8
add r7 12
add r7 7400000000000000128
load8 r3 $r7
cmp r3 65
jlt e28_q_2_lc_12
cmp r3 90
jgt e28_q_2_lc_12
add r3 32
label e28_q_2_lc_12
cmp r3 32
jne e28_q_3
mov r4 r8
add r4 13
set r11 2
set r12 0
jmp e28_tail_parse
label e28_q_3
mov r0 r8
add r0 14
cmp r0 r10
jgt e28_q_4
mov r7 r8
add r7 7400000000000000128
load8 r3 $r7
cmp r3 65
jlt e28_q_3_lc_0
cmp r3 90
jgt e28_q_3_lc_0
add r3 32
label e28_q_3_lc_0
cmp r3 113
jne e28_q_4
mov r7 r8
add r7 1
add r7 7400000000000000128
load8 r3 $r7
cmp r3 65
jlt e28_q_3_lc_1
cmp r3 90
jgt e28_q_3_lc_1
add r3 32
label e28_q_3_lc_1
cmp r3 117
jne e28_q_4
mov r7 r8
add r7 2
add r7 7400000000000000128
load8 r3 $r7
cmp r3 65
jlt e28_q_3_lc_2
cmp r3 90
jgt e28_q_3_lc_2
add r3 32
label e28_q_3_lc_2
cmp r3 195
jne e28_q_4
mov r7 r8
add r7 3
add r7 7400000000000000128
load8 r3 $r7
cmp r3 65
jlt e28_q_3_lc_3
cmp r3 90
jgt e28_q_3_lc_3
add r3 32
label e28_q_3_lc_3
cmp r3 169
jne e28_q_4
mov r7 r8
add r7 4
add r7 7400000000000000128
load8 r3 $r7
cmp r3 65
jlt e28_q_3_lc_4
cmp r3 90
jgt e28_q_3_lc_4
add r3 32
label e28_q_3_lc_4
cmp r3 32
jne e28_q_4
mov r7 r8
add r7 5
add r7 7400000000000000128
load8 r3 $r7
cmp r3 65
jlt e28_q_3_lc_5
cmp r3 90
jgt e28_q_3_lc_5
add r3 32
label e28_q_3_lc_5
cmp r3 114
jne e28_q_4
mov r7 r8
add r7 6
add r7 7400000000000000128
load8 r3 $r7
cmp r3 65
jlt e28_q_3_lc_6
cmp r3 90
jgt e28_q_3_lc_6
add r3 32
label e28_q_3_lc_6
cmp r3 101
jne e28_q_4
mov r7 r8
add r7 7
add r7 7400000000000000128
load8 r3 $r7
cmp r3 65
jlt e28_q_3_lc_7
cmp r3 90
jgt e28_q_3_lc_7
add r3 32
label e28_q_3_lc_7
cmp r3 113
jne e28_q_4
mov r7 r8
add r7 8
add r7 7400000000000000128
load8 r3 $r7
cmp r3 65
jlt e28_q_3_lc_8
cmp r3 90
jgt e28_q_3_lc_8
add r3 32
label e28_q_3_lc_8
cmp r3 117
jne e28_q_4
mov r7 r8
add r7 9
add r7 7400000000000000128
load8 r3 $r7
cmp r3 65
jlt e28_q_3_lc_9
cmp r3 90
jgt e28_q_3_lc_9
add r3 32
label e28_q_3_lc_9
cmp r3 105
jne e28_q_4
mov r7 r8
add r7 10
add r7 7400000000000000128
load8 r3 $r7
cmp r3 65
jlt e28_q_3_lc_10
cmp r3 90
jgt e28_q_3_lc_10
add r3 32
label e28_q_3_lc_10
cmp r3 101
jne e28_q_4
mov r7 r8
add r7 11
add r7 7400000000000000128
load8 r3 $r7
cmp r3 65
jlt e28_q_3_lc_11
cmp r3 90
jgt e28_q_3_lc_11
add r3 32
label e28_q_3_lc_11
cmp r3 114
jne e28_q_4
mov r7 r8
add r7 12
add r7 7400000000000000128
load8 r3 $r7
cmp r3 65
jlt e28_q_3_lc_12
cmp r3 90
jgt e28_q_3_lc_12
add r3 32
label e28_q_3_lc_12
cmp r3 101
jne e28_q_4
mov r7 r8
add r7 13
add r7 7400000000000000128
load8 r3 $r7
cmp r3 65
jlt e28_q_3_lc_13
cmp r3 90
jgt e28_q_3_lc_13
add r3 32
label e28_q_3_lc_13
cmp r3 32
jne e28_q_4
mov r4 r8
add r4 14
set r11 2
set r12 0
jmp e28_tail_parse
label e28_q_4
mov r0 r8
add r0 13
cmp r0 r10
jgt e28_q_5
mov r7 r8
add r7 7400000000000000128
load8 r3 $r7
cmp r3 65
jlt e28_q_4_lc_0
cmp r3 90
jgt e28_q_4_lc_0
add r3 32
label e28_q_4_lc_0
cmp r3 113
jne e28_q_5
mov r7 r8
add r7 1
add r7 7400000000000000128
load8 r3 $r7
cmp r3 65
jlt e28_q_4_lc_1
cmp r3 90
jgt e28_q_4_lc_1
add r3 32
label e28_q_4_lc_1
cmp r3 117
jne e28_q_5
mov r7 r8
add r7 2
add r7 7400000000000000128
load8 r3 $r7
cmp r3 65
jlt e28_q_4_lc_2
cmp r3 90
jgt e28_q_4_lc_2
add r3 32
label e28_q_4_lc_2
cmp r3 101
jne e28_q_5
mov r7 r8
add r7 3
add r7 7400000000000000128
load8 r3 $r7
cmp r3 65
jlt e28_q_4_lc_3
cmp r3 90
jgt e28_q_4_lc_3
add r3 32
label e28_q_4_lc_3
cmp r3 32
jne e28_q_5
mov r7 r8
add r7 4
add r7 7400000000000000128
load8 r3 $r7
cmp r3 65
jlt e28_q_4_lc_4
cmp r3 90
jgt e28_q_4_lc_4
add r3 32
label e28_q_4_lc_4
cmp r3 110
jne e28_q_5
mov r7 r8
add r7 5
add r7 7400000000000000128
load8 r3 $r7
cmp r3 65
jlt e28_q_4_lc_5
cmp r3 90
jgt e28_q_4_lc_5
add r3 32
label e28_q_4_lc_5
cmp r3 101
jne e28_q_5
mov r7 r8
add r7 6
add r7 7400000000000000128
load8 r3 $r7
cmp r3 65
jlt e28_q_4_lc_6
cmp r3 90
jgt e28_q_4_lc_6
add r3 32
label e28_q_4_lc_6
cmp r3 99
jne e28_q_5
mov r7 r8
add r7 7
add r7 7400000000000000128
load8 r3 $r7
cmp r3 65
jlt e28_q_4_lc_7
cmp r3 90
jgt e28_q_4_lc_7
add r3 32
label e28_q_4_lc_7
cmp r3 101
jne e28_q_5
mov r7 r8
add r7 8
add r7 7400000000000000128
load8 r3 $r7
cmp r3 65
jlt e28_q_4_lc_8
cmp r3 90
jgt e28_q_4_lc_8
add r3 32
label e28_q_4_lc_8
cmp r3 115
jne e28_q_5
mov r7 r8
add r7 9
add r7 7400000000000000128
load8 r3 $r7
cmp r3 65
jlt e28_q_4_lc_9
cmp r3 90
jgt e28_q_4_lc_9
add r3 32
label e28_q_4_lc_9
cmp r3 105
jne e28_q_5
mov r7 r8
add r7 10
add r7 7400000000000000128
load8 r3 $r7
cmp r3 65
jlt e28_q_4_lc_10
cmp r3 90
jgt e28_q_4_lc_10
add r3 32
label e28_q_4_lc_10
cmp r3 116
jne e28_q_5
mov r7 r8
add r7 11
add r7 7400000000000000128
load8 r3 $r7
cmp r3 65
jlt e28_q_4_lc_11
cmp r3 90
jgt e28_q_4_lc_11
add r3 32
label e28_q_4_lc_11
cmp r3 97
jne e28_q_5
mov r7 r8
add r7 12
add r7 7400000000000000128
load8 r3 $r7
cmp r3 65
jlt e28_q_4_lc_12
cmp r3 90
jgt e28_q_4_lc_12
add r3 32
label e28_q_4_lc_12
cmp r3 32
jne e28_q_5
mov r4 r8
add r4 13
set r11 2
set r12 0
jmp e28_tail_parse
label e28_q_5
mov r0 r8
add r0 14
cmp r0 r10
jgt e28_q_6
mov r7 r8
add r7 7400000000000000128
load8 r3 $r7
cmp r3 65
jlt e28_q_5_lc_0
cmp r3 90
jgt e28_q_5_lc_0
add r3 32
label e28_q_5_lc_0
cmp r3 113
jne e28_q_6
mov r7 r8
add r7 1
add r7 7400000000000000128
load8 r3 $r7
cmp r3 65
jlt e28_q_5_lc_1
cmp r3 90
jgt e28_q_5_lc_1
add r3 32
label e28_q_5_lc_1
cmp r3 117
jne e28_q_6
mov r7 r8
add r7 2
add r7 7400000000000000128
load8 r3 $r7
cmp r3 65
jlt e28_q_5_lc_2
cmp r3 90
jgt e28_q_5_lc_2
add r3 32
label e28_q_5_lc_2
cmp r3 195
jne e28_q_6
mov r7 r8
add r7 3
add r7 7400000000000000128
load8 r3 $r7
cmp r3 65
jlt e28_q_5_lc_3
cmp r3 90
jgt e28_q_5_lc_3
add r3 32
label e28_q_5_lc_3
cmp r3 169
jne e28_q_6
mov r7 r8
add r7 4
add r7 7400000000000000128
load8 r3 $r7
cmp r3 65
jlt e28_q_5_lc_4
cmp r3 90
jgt e28_q_5_lc_4
add r3 32
label e28_q_5_lc_4
cmp r3 32
jne e28_q_6
mov r7 r8
add r7 5
add r7 7400000000000000128
load8 r3 $r7
cmp r3 65
jlt e28_q_5_lc_5
cmp r3 90
jgt e28_q_5_lc_5
add r3 32
label e28_q_5_lc_5
cmp r3 110
jne e28_q_6
mov r7 r8
add r7 6
add r7 7400000000000000128
load8 r3 $r7
cmp r3 65
jlt e28_q_5_lc_6
cmp r3 90
jgt e28_q_5_lc_6
add r3 32
label e28_q_5_lc_6
cmp r3 101
jne e28_q_6
mov r7 r8
add r7 7
add r7 7400000000000000128
load8 r3 $r7
cmp r3 65
jlt e28_q_5_lc_7
cmp r3 90
jgt e28_q_5_lc_7
add r3 32
label e28_q_5_lc_7
cmp r3 99
jne e28_q_6
mov r7 r8
add r7 8
add r7 7400000000000000128
load8 r3 $r7
cmp r3 65
jlt e28_q_5_lc_8
cmp r3 90
jgt e28_q_5_lc_8
add r3 32
label e28_q_5_lc_8
cmp r3 101
jne e28_q_6
mov r7 r8
add r7 9
add r7 7400000000000000128
load8 r3 $r7
cmp r3 65
jlt e28_q_5_lc_9
cmp r3 90
jgt e28_q_5_lc_9
add r3 32
label e28_q_5_lc_9
cmp r3 115
jne e28_q_6
mov r7 r8
add r7 10
add r7 7400000000000000128
load8 r3 $r7
cmp r3 65
jlt e28_q_5_lc_10
cmp r3 90
jgt e28_q_5_lc_10
add r3 32
label e28_q_5_lc_10
cmp r3 105
jne e28_q_6
mov r7 r8
add r7 11
add r7 7400000000000000128
load8 r3 $r7
cmp r3 65
jlt e28_q_5_lc_11
cmp r3 90
jgt e28_q_5_lc_11
add r3 32
label e28_q_5_lc_11
cmp r3 116
jne e28_q_6
mov r7 r8
add r7 12
add r7 7400000000000000128
load8 r3 $r7
cmp r3 65
jlt e28_q_5_lc_12
cmp r3 90
jgt e28_q_5_lc_12
add r3 32
label e28_q_5_lc_12
cmp r3 97
jne e28_q_6
mov r7 r8
add r7 13
add r7 7400000000000000128
load8 r3 $r7
cmp r3 65
jlt e28_q_5_lc_13
cmp r3 90
jgt e28_q_5_lc_13
add r3 32
label e28_q_5_lc_13
cmp r3 32
jne e28_q_6
mov r4 r8
add r4 14
set r11 2
set r12 0
jmp e28_tail_parse
label e28_q_6
mov r0 r8
add r0 8
cmp r0 r10
jgt e28_q_7
mov r7 r8
add r7 7400000000000000128
load8 r3 $r7
cmp r3 65
jlt e28_q_6_lc_0
cmp r3 90
jgt e28_q_6_lc_0
add r3 32
label e28_q_6_lc_0
cmp r3 119
jne e28_q_7
mov r7 r8
add r7 1
add r7 7400000000000000128
load8 r3 $r7
cmp r3 65
jlt e28_q_6_lc_1
cmp r3 90
jgt e28_q_6_lc_1
add r3 32
label e28_q_6_lc_1
cmp r3 104
jne e28_q_7
mov r7 r8
add r7 2
add r7 7400000000000000128
load8 r3 $r7
cmp r3 65
jlt e28_q_6_lc_2
cmp r3 90
jgt e28_q_6_lc_2
add r3 32
label e28_q_6_lc_2
cmp r3 97
jne e28_q_7
mov r7 r8
add r7 3
add r7 7400000000000000128
load8 r3 $r7
cmp r3 65
jlt e28_q_6_lc_3
cmp r3 90
jgt e28_q_6_lc_3
add r3 32
label e28_q_6_lc_3
cmp r3 116
jne e28_q_7
mov r7 r8
add r7 4
add r7 7400000000000000128
load8 r3 $r7
cmp r3 65
jlt e28_q_6_lc_4
cmp r3 90
jgt e28_q_6_lc_4
add r3 32
label e28_q_6_lc_4
cmp r3 32
jne e28_q_7
mov r7 r8
add r7 5
add r7 7400000000000000128
load8 r3 $r7
cmp r3 65
jlt e28_q_6_lc_5
cmp r3 90
jgt e28_q_6_lc_5
add r3 32
label e28_q_6_lc_5
cmp r3 105
jne e28_q_7
mov r7 r8
add r7 6
add r7 7400000000000000128
load8 r3 $r7
cmp r3 65
jlt e28_q_6_lc_6
cmp r3 90
jgt e28_q_6_lc_6
add r3 32
label e28_q_6_lc_6
cmp r3 115
jne e28_q_7
mov r7 r8
add r7 7
add r7 7400000000000000128
load8 r3 $r7
cmp r3 65
jlt e28_q_6_lc_7
cmp r3 90
jgt e28_q_6_lc_7
add r3 32
label e28_q_6_lc_7
cmp r3 32
jne e28_q_7
mov r4 r8
add r4 8
set r11 1
set r12 0
jmp e28_tail_parse
label e28_q_7
mov r0 r8
add r0 10
cmp r0 r10
jgt e28_q_8
mov r7 r8
add r7 7400000000000000128
load8 r3 $r7
cmp r3 65
jlt e28_q_7_lc_0
cmp r3 90
jgt e28_q_7_lc_0
add r3 32
label e28_q_7_lc_0
cmp r3 119
jne e28_q_8
mov r7 r8
add r7 1
add r7 7400000000000000128
load8 r3 $r7
cmp r3 65
jlt e28_q_7_lc_1
cmp r3 90
jgt e28_q_7_lc_1
add r3 32
label e28_q_7_lc_1
cmp r3 104
jne e28_q_8
mov r7 r8
add r7 2
add r7 7400000000000000128
load8 r3 $r7
cmp r3 65
jlt e28_q_7_lc_2
cmp r3 90
jgt e28_q_7_lc_2
add r3 32
label e28_q_7_lc_2
cmp r3 97
jne e28_q_8
mov r7 r8
add r7 3
add r7 7400000000000000128
load8 r3 $r7
cmp r3 65
jlt e28_q_7_lc_3
cmp r3 90
jgt e28_q_7_lc_3
add r3 32
label e28_q_7_lc_3
cmp r3 116
jne e28_q_8
mov r7 r8
add r7 4
add r7 7400000000000000128
load8 r3 $r7
cmp r3 65
jlt e28_q_7_lc_4
cmp r3 90
jgt e28_q_7_lc_4
add r3 32
label e28_q_7_lc_4
cmp r3 32
jne e28_q_8
mov r7 r8
add r7 5
add r7 7400000000000000128
load8 r3 $r7
cmp r3 65
jlt e28_q_7_lc_5
cmp r3 90
jgt e28_q_7_lc_5
add r3 32
label e28_q_7_lc_5
cmp r3 100
jne e28_q_8
mov r7 r8
add r7 6
add r7 7400000000000000128
load8 r3 $r7
cmp r3 65
jlt e28_q_7_lc_6
cmp r3 90
jgt e28_q_7_lc_6
add r3 32
label e28_q_7_lc_6
cmp r3 111
jne e28_q_8
mov r7 r8
add r7 7
add r7 7400000000000000128
load8 r3 $r7
cmp r3 65
jlt e28_q_7_lc_7
cmp r3 90
jgt e28_q_7_lc_7
add r3 32
label e28_q_7_lc_7
cmp r3 101
jne e28_q_8
mov r7 r8
add r7 8
add r7 7400000000000000128
load8 r3 $r7
cmp r3 65
jlt e28_q_7_lc_8
cmp r3 90
jgt e28_q_7_lc_8
add r3 32
label e28_q_7_lc_8
cmp r3 115
jne e28_q_8
mov r7 r8
add r7 9
add r7 7400000000000000128
load8 r3 $r7
cmp r3 65
jlt e28_q_7_lc_9
cmp r3 90
jgt e28_q_7_lc_9
add r3 32
label e28_q_7_lc_9
cmp r3 32
jne e28_q_8
mov r4 r8
add r4 10
set r11 3
set r12 0
jmp e28_tail_parse
label e28_q_8
jmp e28_delegate
label e28_tail_parse
cmp r11 3
jne e28_tail_general
label e28_need_tail_0
mov r0 r10
sub r0 5
cmp r0 r4
jlt e28_need_tail_1
mov r7 r0
add r7 7400000000000000128
load8 r3 $r7
cmp r3 65
jlt e28_need_tail_0_lc_0
cmp r3 90
jgt e28_need_tail_0_lc_0
add r3 32
label e28_need_tail_0_lc_0
cmp r3 32
jne e28_need_tail_1
mov r7 r0
add r7 1
add r7 7400000000000000128
load8 r3 $r7
cmp r3 65
jlt e28_need_tail_0_lc_1
cmp r3 90
jgt e28_need_tail_0_lc_1
add r3 32
label e28_need_tail_0_lc_1
cmp r3 110
jne e28_need_tail_1
mov r7 r0
add r7 2
add r7 7400000000000000128
load8 r3 $r7
cmp r3 65
jlt e28_need_tail_0_lc_2
cmp r3 90
jgt e28_need_tail_0_lc_2
add r3 32
label e28_need_tail_0_lc_2
cmp r3 101
jne e28_need_tail_1
mov r7 r0
add r7 3
add r7 7400000000000000128
load8 r3 $r7
cmp r3 65
jlt e28_need_tail_0_lc_3
cmp r3 90
jgt e28_need_tail_0_lc_3
add r3 32
label e28_need_tail_0_lc_3
cmp r3 101
jne e28_need_tail_1
mov r7 r0
add r7 4
add r7 7400000000000000128
load8 r3 $r7
cmp r3 65
jlt e28_need_tail_0_lc_4
cmp r3 90
jgt e28_need_tail_0_lc_4
add r3 32
label e28_need_tail_0_lc_4
cmp r3 100
jne e28_need_tail_1
sub r10 5
set r11 2
jmp e28_subject
label e28_need_tail_1
mov r0 r10
sub r0 8
cmp r0 r4
jlt e28_need_tail_2
mov r7 r0
add r7 7400000000000000128
load8 r3 $r7
cmp r3 65
jlt e28_need_tail_1_lc_0
cmp r3 90
jgt e28_need_tail_1_lc_0
add r3 32
label e28_need_tail_1_lc_0
cmp r3 32
jne e28_need_tail_2
mov r7 r0
add r7 1
add r7 7400000000000000128
load8 r3 $r7
cmp r3 65
jlt e28_need_tail_1_lc_1
cmp r3 90
jgt e28_need_tail_1_lc_1
add r3 32
label e28_need_tail_1_lc_1
cmp r3 114
jne e28_need_tail_2
mov r7 r0
add r7 2
add r7 7400000000000000128
load8 r3 $r7
cmp r3 65
jlt e28_need_tail_1_lc_2
cmp r3 90
jgt e28_need_tail_1_lc_2
add r3 32
label e28_need_tail_1_lc_2
cmp r3 101
jne e28_need_tail_2
mov r7 r0
add r7 3
add r7 7400000000000000128
load8 r3 $r7
cmp r3 65
jlt e28_need_tail_1_lc_3
cmp r3 90
jgt e28_need_tail_1_lc_3
add r3 32
label e28_need_tail_1_lc_3
cmp r3 113
jne e28_need_tail_2
mov r7 r0
add r7 4
add r7 7400000000000000128
load8 r3 $r7
cmp r3 65
jlt e28_need_tail_1_lc_4
cmp r3 90
jgt e28_need_tail_1_lc_4
add r3 32
label e28_need_tail_1_lc_4
cmp r3 117
jne e28_need_tail_2
mov r7 r0
add r7 5
add r7 7400000000000000128
load8 r3 $r7
cmp r3 65
jlt e28_need_tail_1_lc_5
cmp r3 90
jgt e28_need_tail_1_lc_5
add r3 32
label e28_need_tail_1_lc_5
cmp r3 105
jne e28_need_tail_2
mov r7 r0
add r7 6
add r7 7400000000000000128
load8 r3 $r7
cmp r3 65
jlt e28_need_tail_1_lc_6
cmp r3 90
jgt e28_need_tail_1_lc_6
add r3 32
label e28_need_tail_1_lc_6
cmp r3 114
jne e28_need_tail_2
mov r7 r0
add r7 7
add r7 7400000000000000128
load8 r3 $r7
cmp r3 65
jlt e28_need_tail_1_lc_7
cmp r3 90
jgt e28_need_tail_1_lc_7
add r3 32
label e28_need_tail_1_lc_7
cmp r3 101
jne e28_need_tail_2
sub r10 8
set r11 2
jmp e28_subject
label e28_need_tail_2
jmp e28_ambiguous
label e28_tail_general
cmp r11 1
jne e28_subject
label e28_dual_tail_0
mov r0 r10
sub r0 15
cmp r0 r4
jlt e28_dual_tail_1
mov r7 r0
add r7 7400000000000000128
load8 r3 $r7
cmp r3 65
jlt e28_dual_tail_0_lc_0
cmp r3 90
jgt e28_dual_tail_0_lc_0
add r3 32
label e28_dual_tail_0_lc_0
cmp r3 32
jne e28_dual_tail_1
mov r7 r0
add r7 1
add r7 7400000000000000128
load8 r3 $r7
cmp r3 65
jlt e28_dual_tail_0_lc_1
cmp r3 90
jgt e28_dual_tail_0_lc_1
add r3 32
label e28_dual_tail_0_lc_1
cmp r3 121
jne e28_dual_tail_1
mov r7 r0
add r7 2
add r7 7400000000000000128
load8 r3 $r7
cmp r3 65
jlt e28_dual_tail_0_lc_2
cmp r3 90
jgt e28_dual_tail_0_lc_2
add r3 32
label e28_dual_tail_0_lc_2
cmp r3 32
jne e28_dual_tail_1
mov r7 r0
add r7 3
add r7 7400000000000000128
load8 r3 $r7
cmp r3 65
jlt e28_dual_tail_0_lc_3
cmp r3 90
jgt e28_dual_tail_0_lc_3
add r3 32
label e28_dual_tail_0_lc_3
cmp r3 113
jne e28_dual_tail_1
mov r7 r0
add r7 4
add r7 7400000000000000128
load8 r3 $r7
cmp r3 65
jlt e28_dual_tail_0_lc_4
cmp r3 90
jgt e28_dual_tail_0_lc_4
add r3 32
label e28_dual_tail_0_lc_4
cmp r3 117
jne e28_dual_tail_1
mov r7 r0
add r7 5
add r7 7400000000000000128
load8 r3 $r7
cmp r3 65
jlt e28_dual_tail_0_lc_5
cmp r3 90
jgt e28_dual_tail_0_lc_5
add r3 32
label e28_dual_tail_0_lc_5
cmp r3 101
jne e28_dual_tail_1
mov r7 r0
add r7 6
add r7 7400000000000000128
load8 r3 $r7
cmp r3 65
jlt e28_dual_tail_0_lc_6
cmp r3 90
jgt e28_dual_tail_0_lc_6
add r3 32
label e28_dual_tail_0_lc_6
cmp r3 32
jne e28_dual_tail_1
mov r7 r0
add r7 7
add r7 7400000000000000128
load8 r3 $r7
cmp r3 65
jlt e28_dual_tail_0_lc_7
cmp r3 90
jgt e28_dual_tail_0_lc_7
add r3 32
label e28_dual_tail_0_lc_7
cmp r3 114
jne e28_dual_tail_1
mov r7 r0
add r7 8
add r7 7400000000000000128
load8 r3 $r7
cmp r3 65
jlt e28_dual_tail_0_lc_8
cmp r3 90
jgt e28_dual_tail_0_lc_8
add r3 32
label e28_dual_tail_0_lc_8
cmp r3 101
jne e28_dual_tail_1
mov r7 r0
add r7 9
add r7 7400000000000000128
load8 r3 $r7
cmp r3 65
jlt e28_dual_tail_0_lc_9
cmp r3 90
jgt e28_dual_tail_0_lc_9
add r3 32
label e28_dual_tail_0_lc_9
cmp r3 113
jne e28_dual_tail_1
mov r7 r0
add r7 10
add r7 7400000000000000128
load8 r3 $r7
cmp r3 65
jlt e28_dual_tail_0_lc_10
cmp r3 90
jgt e28_dual_tail_0_lc_10
add r3 32
label e28_dual_tail_0_lc_10
cmp r3 117
jne e28_dual_tail_1
mov r7 r0
add r7 11
add r7 7400000000000000128
load8 r3 $r7
cmp r3 65
jlt e28_dual_tail_0_lc_11
cmp r3 90
jgt e28_dual_tail_0_lc_11
add r3 32
label e28_dual_tail_0_lc_11
cmp r3 105
jne e28_dual_tail_1
mov r7 r0
add r7 12
add r7 7400000000000000128
load8 r3 $r7
cmp r3 65
jlt e28_dual_tail_0_lc_12
cmp r3 90
jgt e28_dual_tail_0_lc_12
add r3 32
label e28_dual_tail_0_lc_12
cmp r3 101
jne e28_dual_tail_1
mov r7 r0
add r7 13
add r7 7400000000000000128
load8 r3 $r7
cmp r3 65
jlt e28_dual_tail_0_lc_13
cmp r3 90
jgt e28_dual_tail_0_lc_13
add r3 32
label e28_dual_tail_0_lc_13
cmp r3 114
jne e28_dual_tail_1
mov r7 r0
add r7 14
add r7 7400000000000000128
load8 r3 $r7
cmp r3 65
jlt e28_dual_tail_0_lc_14
cmp r3 90
jgt e28_dual_tail_0_lc_14
add r3 32
label e28_dual_tail_0_lc_14
cmp r3 101
jne e28_dual_tail_1
sub r10 15
set r12 1
jmp e28_subject
label e28_dual_tail_1
mov r0 r10
sub r0 16
cmp r0 r4
jlt e28_dual_tail_2
mov r7 r0
add r7 7400000000000000128
load8 r3 $r7
cmp r3 65
jlt e28_dual_tail_1_lc_0
cmp r3 90
jgt e28_dual_tail_1_lc_0
add r3 32
label e28_dual_tail_1_lc_0
cmp r3 32
jne e28_dual_tail_2
mov r7 r0
add r7 1
add r7 7400000000000000128
load8 r3 $r7
cmp r3 65
jlt e28_dual_tail_1_lc_1
cmp r3 90
jgt e28_dual_tail_1_lc_1
add r3 32
label e28_dual_tail_1_lc_1
cmp r3 121
jne e28_dual_tail_2
mov r7 r0
add r7 2
add r7 7400000000000000128
load8 r3 $r7
cmp r3 65
jlt e28_dual_tail_1_lc_2
cmp r3 90
jgt e28_dual_tail_1_lc_2
add r3 32
label e28_dual_tail_1_lc_2
cmp r3 32
jne e28_dual_tail_2
mov r7 r0
add r7 3
add r7 7400000000000000128
load8 r3 $r7
cmp r3 65
jlt e28_dual_tail_1_lc_3
cmp r3 90
jgt e28_dual_tail_1_lc_3
add r3 32
label e28_dual_tail_1_lc_3
cmp r3 113
jne e28_dual_tail_2
mov r7 r0
add r7 4
add r7 7400000000000000128
load8 r3 $r7
cmp r3 65
jlt e28_dual_tail_1_lc_4
cmp r3 90
jgt e28_dual_tail_1_lc_4
add r3 32
label e28_dual_tail_1_lc_4
cmp r3 117
jne e28_dual_tail_2
mov r7 r0
add r7 5
add r7 7400000000000000128
load8 r3 $r7
cmp r3 65
jlt e28_dual_tail_1_lc_5
cmp r3 90
jgt e28_dual_tail_1_lc_5
add r3 32
label e28_dual_tail_1_lc_5
cmp r3 195
jne e28_dual_tail_2
mov r7 r0
add r7 6
add r7 7400000000000000128
load8 r3 $r7
cmp r3 65
jlt e28_dual_tail_1_lc_6
cmp r3 90
jgt e28_dual_tail_1_lc_6
add r3 32
label e28_dual_tail_1_lc_6
cmp r3 169
jne e28_dual_tail_2
mov r7 r0
add r7 7
add r7 7400000000000000128
load8 r3 $r7
cmp r3 65
jlt e28_dual_tail_1_lc_7
cmp r3 90
jgt e28_dual_tail_1_lc_7
add r3 32
label e28_dual_tail_1_lc_7
cmp r3 32
jne e28_dual_tail_2
mov r7 r0
add r7 8
add r7 7400000000000000128
load8 r3 $r7
cmp r3 65
jlt e28_dual_tail_1_lc_8
cmp r3 90
jgt e28_dual_tail_1_lc_8
add r3 32
label e28_dual_tail_1_lc_8
cmp r3 114
jne e28_dual_tail_2
mov r7 r0
add r7 9
add r7 7400000000000000128
load8 r3 $r7
cmp r3 65
jlt e28_dual_tail_1_lc_9
cmp r3 90
jgt e28_dual_tail_1_lc_9
add r3 32
label e28_dual_tail_1_lc_9
cmp r3 101
jne e28_dual_tail_2
mov r7 r0
add r7 10
add r7 7400000000000000128
load8 r3 $r7
cmp r3 65
jlt e28_dual_tail_1_lc_10
cmp r3 90
jgt e28_dual_tail_1_lc_10
add r3 32
label e28_dual_tail_1_lc_10
cmp r3 113
jne e28_dual_tail_2
mov r7 r0
add r7 11
add r7 7400000000000000128
load8 r3 $r7
cmp r3 65
jlt e28_dual_tail_1_lc_11
cmp r3 90
jgt e28_dual_tail_1_lc_11
add r3 32
label e28_dual_tail_1_lc_11
cmp r3 117
jne e28_dual_tail_2
mov r7 r0
add r7 12
add r7 7400000000000000128
load8 r3 $r7
cmp r3 65
jlt e28_dual_tail_1_lc_12
cmp r3 90
jgt e28_dual_tail_1_lc_12
add r3 32
label e28_dual_tail_1_lc_12
cmp r3 105
jne e28_dual_tail_2
mov r7 r0
add r7 13
add r7 7400000000000000128
load8 r3 $r7
cmp r3 65
jlt e28_dual_tail_1_lc_13
cmp r3 90
jgt e28_dual_tail_1_lc_13
add r3 32
label e28_dual_tail_1_lc_13
cmp r3 101
jne e28_dual_tail_2
mov r7 r0
add r7 14
add r7 7400000000000000128
load8 r3 $r7
cmp r3 65
jlt e28_dual_tail_1_lc_14
cmp r3 90
jgt e28_dual_tail_1_lc_14
add r3 32
label e28_dual_tail_1_lc_14
cmp r3 114
jne e28_dual_tail_2
mov r7 r0
add r7 15
add r7 7400000000000000128
load8 r3 $r7
cmp r3 65
jlt e28_dual_tail_1_lc_15
cmp r3 90
jgt e28_dual_tail_1_lc_15
add r3 32
label e28_dual_tail_1_lc_15
cmp r3 101
jne e28_dual_tail_2
sub r10 16
set r12 1
jmp e28_subject
label e28_dual_tail_2
mov r0 r10
sub r0 15
cmp r0 r4
jlt e28_dual_tail_3
mov r7 r0
add r7 7400000000000000128
load8 r3 $r7
cmp r3 65
jlt e28_dual_tail_2_lc_0
cmp r3 90
jgt e28_dual_tail_2_lc_0
add r3 32
label e28_dual_tail_2_lc_0
cmp r3 32
jne e28_dual_tail_3
mov r7 r0
add r7 1
add r7 7400000000000000128
load8 r3 $r7
cmp r3 65
jlt e28_dual_tail_2_lc_1
cmp r3 90
jgt e28_dual_tail_2_lc_1
add r3 32
label e28_dual_tail_2_lc_1
cmp r3 121
jne e28_dual_tail_3
mov r7 r0
add r7 2
add r7 7400000000000000128
load8 r3 $r7
cmp r3 65
jlt e28_dual_tail_2_lc_2
cmp r3 90
jgt e28_dual_tail_2_lc_2
add r3 32
label e28_dual_tail_2_lc_2
cmp r3 32
jne e28_dual_tail_3
mov r7 r0
add r7 3
add r7 7400000000000000128
load8 r3 $r7
cmp r3 65
jlt e28_dual_tail_2_lc_3
cmp r3 90
jgt e28_dual_tail_2_lc_3
add r3 32
label e28_dual_tail_2_lc_3
cmp r3 113
jne e28_dual_tail_3
mov r7 r0
add r7 4
add r7 7400000000000000128
load8 r3 $r7
cmp r3 65
jlt e28_dual_tail_2_lc_4
cmp r3 90
jgt e28_dual_tail_2_lc_4
add r3 32
label e28_dual_tail_2_lc_4
cmp r3 117
jne e28_dual_tail_3
mov r7 r0
add r7 5
add r7 7400000000000000128
load8 r3 $r7
cmp r3 65
jlt e28_dual_tail_2_lc_5
cmp r3 90
jgt e28_dual_tail_2_lc_5
add r3 32
label e28_dual_tail_2_lc_5
cmp r3 101
jne e28_dual_tail_3
mov r7 r0
add r7 6
add r7 7400000000000000128
load8 r3 $r7
cmp r3 65
jlt e28_dual_tail_2_lc_6
cmp r3 90
jgt e28_dual_tail_2_lc_6
add r3 32
label e28_dual_tail_2_lc_6
cmp r3 32
jne e28_dual_tail_3
mov r7 r0
add r7 7
add r7 7400000000000000128
load8 r3 $r7
cmp r3 65
jlt e28_dual_tail_2_lc_7
cmp r3 90
jgt e28_dual_tail_2_lc_7
add r3 32
label e28_dual_tail_2_lc_7
cmp r3 110
jne e28_dual_tail_3
mov r7 r0
add r7 8
add r7 7400000000000000128
load8 r3 $r7
cmp r3 65
jlt e28_dual_tail_2_lc_8
cmp r3 90
jgt e28_dual_tail_2_lc_8
add r3 32
label e28_dual_tail_2_lc_8
cmp r3 101
jne e28_dual_tail_3
mov r7 r0
add r7 9
add r7 7400000000000000128
load8 r3 $r7
cmp r3 65
jlt e28_dual_tail_2_lc_9
cmp r3 90
jgt e28_dual_tail_2_lc_9
add r3 32
label e28_dual_tail_2_lc_9
cmp r3 99
jne e28_dual_tail_3
mov r7 r0
add r7 10
add r7 7400000000000000128
load8 r3 $r7
cmp r3 65
jlt e28_dual_tail_2_lc_10
cmp r3 90
jgt e28_dual_tail_2_lc_10
add r3 32
label e28_dual_tail_2_lc_10
cmp r3 101
jne e28_dual_tail_3
mov r7 r0
add r7 11
add r7 7400000000000000128
load8 r3 $r7
cmp r3 65
jlt e28_dual_tail_2_lc_11
cmp r3 90
jgt e28_dual_tail_2_lc_11
add r3 32
label e28_dual_tail_2_lc_11
cmp r3 115
jne e28_dual_tail_3
mov r7 r0
add r7 12
add r7 7400000000000000128
load8 r3 $r7
cmp r3 65
jlt e28_dual_tail_2_lc_12
cmp r3 90
jgt e28_dual_tail_2_lc_12
add r3 32
label e28_dual_tail_2_lc_12
cmp r3 105
jne e28_dual_tail_3
mov r7 r0
add r7 13
add r7 7400000000000000128
load8 r3 $r7
cmp r3 65
jlt e28_dual_tail_2_lc_13
cmp r3 90
jgt e28_dual_tail_2_lc_13
add r3 32
label e28_dual_tail_2_lc_13
cmp r3 116
jne e28_dual_tail_3
mov r7 r0
add r7 14
add r7 7400000000000000128
load8 r3 $r7
cmp r3 65
jlt e28_dual_tail_2_lc_14
cmp r3 90
jgt e28_dual_tail_2_lc_14
add r3 32
label e28_dual_tail_2_lc_14
cmp r3 97
jne e28_dual_tail_3
sub r10 15
set r12 1
jmp e28_subject
label e28_dual_tail_3
mov r0 r10
sub r0 16
cmp r0 r4
jlt e28_dual_tail_4
mov r7 r0
add r7 7400000000000000128
load8 r3 $r7
cmp r3 65
jlt e28_dual_tail_3_lc_0
cmp r3 90
jgt e28_dual_tail_3_lc_0
add r3 32
label e28_dual_tail_3_lc_0
cmp r3 32
jne e28_dual_tail_4
mov r7 r0
add r7 1
add r7 7400000000000000128
load8 r3 $r7
cmp r3 65
jlt e28_dual_tail_3_lc_1
cmp r3 90
jgt e28_dual_tail_3_lc_1
add r3 32
label e28_dual_tail_3_lc_1
cmp r3 121
jne e28_dual_tail_4
mov r7 r0
add r7 2
add r7 7400000000000000128
load8 r3 $r7
cmp r3 65
jlt e28_dual_tail_3_lc_2
cmp r3 90
jgt e28_dual_tail_3_lc_2
add r3 32
label e28_dual_tail_3_lc_2
cmp r3 32
jne e28_dual_tail_4
mov r7 r0
add r7 3
add r7 7400000000000000128
load8 r3 $r7
cmp r3 65
jlt e28_dual_tail_3_lc_3
cmp r3 90
jgt e28_dual_tail_3_lc_3
add r3 32
label e28_dual_tail_3_lc_3
cmp r3 113
jne e28_dual_tail_4
mov r7 r0
add r7 4
add r7 7400000000000000128
load8 r3 $r7
cmp r3 65
jlt e28_dual_tail_3_lc_4
cmp r3 90
jgt e28_dual_tail_3_lc_4
add r3 32
label e28_dual_tail_3_lc_4
cmp r3 117
jne e28_dual_tail_4
mov r7 r0
add r7 5
add r7 7400000000000000128
load8 r3 $r7
cmp r3 65
jlt e28_dual_tail_3_lc_5
cmp r3 90
jgt e28_dual_tail_3_lc_5
add r3 32
label e28_dual_tail_3_lc_5
cmp r3 195
jne e28_dual_tail_4
mov r7 r0
add r7 6
add r7 7400000000000000128
load8 r3 $r7
cmp r3 65
jlt e28_dual_tail_3_lc_6
cmp r3 90
jgt e28_dual_tail_3_lc_6
add r3 32
label e28_dual_tail_3_lc_6
cmp r3 169
jne e28_dual_tail_4
mov r7 r0
add r7 7
add r7 7400000000000000128
load8 r3 $r7
cmp r3 65
jlt e28_dual_tail_3_lc_7
cmp r3 90
jgt e28_dual_tail_3_lc_7
add r3 32
label e28_dual_tail_3_lc_7
cmp r3 32
jne e28_dual_tail_4
mov r7 r0
add r7 8
add r7 7400000000000000128
load8 r3 $r7
cmp r3 65
jlt e28_dual_tail_3_lc_8
cmp r3 90
jgt e28_dual_tail_3_lc_8
add r3 32
label e28_dual_tail_3_lc_8
cmp r3 110
jne e28_dual_tail_4
mov r7 r0
add r7 9
add r7 7400000000000000128
load8 r3 $r7
cmp r3 65
jlt e28_dual_tail_3_lc_9
cmp r3 90
jgt e28_dual_tail_3_lc_9
add r3 32
label e28_dual_tail_3_lc_9
cmp r3 101
jne e28_dual_tail_4
mov r7 r0
add r7 10
add r7 7400000000000000128
load8 r3 $r7
cmp r3 65
jlt e28_dual_tail_3_lc_10
cmp r3 90
jgt e28_dual_tail_3_lc_10
add r3 32
label e28_dual_tail_3_lc_10
cmp r3 99
jne e28_dual_tail_4
mov r7 r0
add r7 11
add r7 7400000000000000128
load8 r3 $r7
cmp r3 65
jlt e28_dual_tail_3_lc_11
cmp r3 90
jgt e28_dual_tail_3_lc_11
add r3 32
label e28_dual_tail_3_lc_11
cmp r3 101
jne e28_dual_tail_4
mov r7 r0
add r7 12
add r7 7400000000000000128
load8 r3 $r7
cmp r3 65
jlt e28_dual_tail_3_lc_12
cmp r3 90
jgt e28_dual_tail_3_lc_12
add r3 32
label e28_dual_tail_3_lc_12
cmp r3 115
jne e28_dual_tail_4
mov r7 r0
add r7 13
add r7 7400000000000000128
load8 r3 $r7
cmp r3 65
jlt e28_dual_tail_3_lc_13
cmp r3 90
jgt e28_dual_tail_3_lc_13
add r3 32
label e28_dual_tail_3_lc_13
cmp r3 105
jne e28_dual_tail_4
mov r7 r0
add r7 14
add r7 7400000000000000128
load8 r3 $r7
cmp r3 65
jlt e28_dual_tail_3_lc_14
cmp r3 90
jgt e28_dual_tail_3_lc_14
add r3 32
label e28_dual_tail_3_lc_14
cmp r3 116
jne e28_dual_tail_4
mov r7 r0
add r7 15
add r7 7400000000000000128
load8 r3 $r7
cmp r3 65
jlt e28_dual_tail_3_lc_15
cmp r3 90
jgt e28_dual_tail_3_lc_15
add r3 32
label e28_dual_tail_3_lc_15
cmp r3 97
jne e28_dual_tail_4
sub r10 16
set r12 1
jmp e28_subject
label e28_dual_tail_4
mov r0 r10
sub r0 22
cmp r0 r4
jlt e28_dual_tail_5
mov r7 r0
add r7 7400000000000000128
load8 r3 $r7
cmp r3 65
jlt e28_dual_tail_4_lc_0
cmp r3 90
jgt e28_dual_tail_4_lc_0
add r3 32
label e28_dual_tail_4_lc_0
cmp r3 32
jne e28_dual_tail_5
mov r7 r0
add r7 1
add r7 7400000000000000128
load8 r3 $r7
cmp r3 65
jlt e28_dual_tail_4_lc_1
cmp r3 90
jgt e28_dual_tail_4_lc_1
add r3 32
label e28_dual_tail_4_lc_1
cmp r3 97
jne e28_dual_tail_5
mov r7 r0
add r7 2
add r7 7400000000000000128
load8 r3 $r7
cmp r3 65
jlt e28_dual_tail_4_lc_2
cmp r3 90
jgt e28_dual_tail_4_lc_2
add r3 32
label e28_dual_tail_4_lc_2
cmp r3 110
jne e28_dual_tail_5
mov r7 r0
add r7 3
add r7 7400000000000000128
load8 r3 $r7
cmp r3 65
jlt e28_dual_tail_4_lc_3
cmp r3 90
jgt e28_dual_tail_4_lc_3
add r3 32
label e28_dual_tail_4_lc_3
cmp r3 100
jne e28_dual_tail_5
mov r7 r0
add r7 4
add r7 7400000000000000128
load8 r3 $r7
cmp r3 65
jlt e28_dual_tail_4_lc_4
cmp r3 90
jgt e28_dual_tail_4_lc_4
add r3 32
label e28_dual_tail_4_lc_4
cmp r3 32
jne e28_dual_tail_5
mov r7 r0
add r7 5
add r7 7400000000000000128
load8 r3 $r7
cmp r3 65
jlt e28_dual_tail_4_lc_5
cmp r3 90
jgt e28_dual_tail_4_lc_5
add r3 32
label e28_dual_tail_4_lc_5
cmp r3 119
jne e28_dual_tail_5
mov r7 r0
add r7 6
add r7 7400000000000000128
load8 r3 $r7
cmp r3 65
jlt e28_dual_tail_4_lc_6
cmp r3 90
jgt e28_dual_tail_4_lc_6
add r3 32
label e28_dual_tail_4_lc_6
cmp r3 104
jne e28_dual_tail_5
mov r7 r0
add r7 7
add r7 7400000000000000128
load8 r3 $r7
cmp r3 65
jlt e28_dual_tail_4_lc_7
cmp r3 90
jgt e28_dual_tail_4_lc_7
add r3 32
label e28_dual_tail_4_lc_7
cmp r3 97
jne e28_dual_tail_5
mov r7 r0
add r7 8
add r7 7400000000000000128
load8 r3 $r7
cmp r3 65
jlt e28_dual_tail_4_lc_8
cmp r3 90
jgt e28_dual_tail_4_lc_8
add r3 32
label e28_dual_tail_4_lc_8
cmp r3 116
jne e28_dual_tail_5
mov r7 r0
add r7 9
add r7 7400000000000000128
load8 r3 $r7
cmp r3 65
jlt e28_dual_tail_4_lc_9
cmp r3 90
jgt e28_dual_tail_4_lc_9
add r3 32
label e28_dual_tail_4_lc_9
cmp r3 32
jne e28_dual_tail_5
mov r7 r0
add r7 10
add r7 7400000000000000128
load8 r3 $r7
cmp r3 65
jlt e28_dual_tail_4_lc_10
cmp r3 90
jgt e28_dual_tail_4_lc_10
add r3 32
label e28_dual_tail_4_lc_10
cmp r3 100
jne e28_dual_tail_5
mov r7 r0
add r7 11
add r7 7400000000000000128
load8 r3 $r7
cmp r3 65
jlt e28_dual_tail_4_lc_11
cmp r3 90
jgt e28_dual_tail_4_lc_11
add r3 32
label e28_dual_tail_4_lc_11
cmp r3 111
jne e28_dual_tail_5
mov r7 r0
add r7 12
add r7 7400000000000000128
load8 r3 $r7
cmp r3 65
jlt e28_dual_tail_4_lc_12
cmp r3 90
jgt e28_dual_tail_4_lc_12
add r3 32
label e28_dual_tail_4_lc_12
cmp r3 101
jne e28_dual_tail_5
mov r7 r0
add r7 13
add r7 7400000000000000128
load8 r3 $r7
cmp r3 65
jlt e28_dual_tail_4_lc_13
cmp r3 90
jgt e28_dual_tail_4_lc_13
add r3 32
label e28_dual_tail_4_lc_13
cmp r3 115
jne e28_dual_tail_5
mov r7 r0
add r7 14
add r7 7400000000000000128
load8 r3 $r7
cmp r3 65
jlt e28_dual_tail_4_lc_14
cmp r3 90
jgt e28_dual_tail_4_lc_14
add r3 32
label e28_dual_tail_4_lc_14
cmp r3 32
jne e28_dual_tail_5
mov r7 r0
add r7 15
add r7 7400000000000000128
load8 r3 $r7
cmp r3 65
jlt e28_dual_tail_4_lc_15
cmp r3 90
jgt e28_dual_tail_4_lc_15
add r3 32
label e28_dual_tail_4_lc_15
cmp r3 105
jne e28_dual_tail_5
mov r7 r0
add r7 16
add r7 7400000000000000128
load8 r3 $r7
cmp r3 65
jlt e28_dual_tail_4_lc_16
cmp r3 90
jgt e28_dual_tail_4_lc_16
add r3 32
label e28_dual_tail_4_lc_16
cmp r3 116
jne e28_dual_tail_5
mov r7 r0
add r7 17
add r7 7400000000000000128
load8 r3 $r7
cmp r3 65
jlt e28_dual_tail_4_lc_17
cmp r3 90
jgt e28_dual_tail_4_lc_17
add r3 32
label e28_dual_tail_4_lc_17
cmp r3 32
jne e28_dual_tail_5
mov r7 r0
add r7 18
add r7 7400000000000000128
load8 r3 $r7
cmp r3 65
jlt e28_dual_tail_4_lc_18
cmp r3 90
jgt e28_dual_tail_4_lc_18
add r3 32
label e28_dual_tail_4_lc_18
cmp r3 110
jne e28_dual_tail_5
mov r7 r0
add r7 19
add r7 7400000000000000128
load8 r3 $r7
cmp r3 65
jlt e28_dual_tail_4_lc_19
cmp r3 90
jgt e28_dual_tail_4_lc_19
add r3 32
label e28_dual_tail_4_lc_19
cmp r3 101
jne e28_dual_tail_5
mov r7 r0
add r7 20
add r7 7400000000000000128
load8 r3 $r7
cmp r3 65
jlt e28_dual_tail_4_lc_20
cmp r3 90
jgt e28_dual_tail_4_lc_20
add r3 32
label e28_dual_tail_4_lc_20
cmp r3 101
jne e28_dual_tail_5
mov r7 r0
add r7 21
add r7 7400000000000000128
load8 r3 $r7
cmp r3 65
jlt e28_dual_tail_4_lc_21
cmp r3 90
jgt e28_dual_tail_4_lc_21
add r3 32
label e28_dual_tail_4_lc_21
cmp r3 100
jne e28_dual_tail_5
sub r10 22
set r12 1
jmp e28_subject
label e28_dual_tail_5
mov r0 r10
sub r0 25
cmp r0 r4
jlt e28_dual_tail_6
mov r7 r0
add r7 7400000000000000128
load8 r3 $r7
cmp r3 65
jlt e28_dual_tail_5_lc_0
cmp r3 90
jgt e28_dual_tail_5_lc_0
add r3 32
label e28_dual_tail_5_lc_0
cmp r3 32
jne e28_dual_tail_6
mov r7 r0
add r7 1
add r7 7400000000000000128
load8 r3 $r7
cmp r3 65
jlt e28_dual_tail_5_lc_1
cmp r3 90
jgt e28_dual_tail_5_lc_1
add r3 32
label e28_dual_tail_5_lc_1
cmp r3 97
jne e28_dual_tail_6
mov r7 r0
add r7 2
add r7 7400000000000000128
load8 r3 $r7
cmp r3 65
jlt e28_dual_tail_5_lc_2
cmp r3 90
jgt e28_dual_tail_5_lc_2
add r3 32
label e28_dual_tail_5_lc_2
cmp r3 110
jne e28_dual_tail_6
mov r7 r0
add r7 3
add r7 7400000000000000128
load8 r3 $r7
cmp r3 65
jlt e28_dual_tail_5_lc_3
cmp r3 90
jgt e28_dual_tail_5_lc_3
add r3 32
label e28_dual_tail_5_lc_3
cmp r3 100
jne e28_dual_tail_6
mov r7 r0
add r7 4
add r7 7400000000000000128
load8 r3 $r7
cmp r3 65
jlt e28_dual_tail_5_lc_4
cmp r3 90
jgt e28_dual_tail_5_lc_4
add r3 32
label e28_dual_tail_5_lc_4
cmp r3 32
jne e28_dual_tail_6
mov r7 r0
add r7 5
add r7 7400000000000000128
load8 r3 $r7
cmp r3 65
jlt e28_dual_tail_5_lc_5
cmp r3 90
jgt e28_dual_tail_5_lc_5
add r3 32
label e28_dual_tail_5_lc_5
cmp r3 119
jne e28_dual_tail_6
mov r7 r0
add r7 6
add r7 7400000000000000128
load8 r3 $r7
cmp r3 65
jlt e28_dual_tail_5_lc_6
cmp r3 90
jgt e28_dual_tail_5_lc_6
add r3 32
label e28_dual_tail_5_lc_6
cmp r3 104
jne e28_dual_tail_6
mov r7 r0
add r7 7
add r7 7400000000000000128
load8 r3 $r7
cmp r3 65
jlt e28_dual_tail_5_lc_7
cmp r3 90
jgt e28_dual_tail_5_lc_7
add r3 32
label e28_dual_tail_5_lc_7
cmp r3 97
jne e28_dual_tail_6
mov r7 r0
add r7 8
add r7 7400000000000000128
load8 r3 $r7
cmp r3 65
jlt e28_dual_tail_5_lc_8
cmp r3 90
jgt e28_dual_tail_5_lc_8
add r3 32
label e28_dual_tail_5_lc_8
cmp r3 116
jne e28_dual_tail_6
mov r7 r0
add r7 9
add r7 7400000000000000128
load8 r3 $r7
cmp r3 65
jlt e28_dual_tail_5_lc_9
cmp r3 90
jgt e28_dual_tail_5_lc_9
add r3 32
label e28_dual_tail_5_lc_9
cmp r3 32
jne e28_dual_tail_6
mov r7 r0
add r7 10
add r7 7400000000000000128
load8 r3 $r7
cmp r3 65
jlt e28_dual_tail_5_lc_10
cmp r3 90
jgt e28_dual_tail_5_lc_10
add r3 32
label e28_dual_tail_5_lc_10
cmp r3 100
jne e28_dual_tail_6
mov r7 r0
add r7 11
add r7 7400000000000000128
load8 r3 $r7
cmp r3 65
jlt e28_dual_tail_5_lc_11
cmp r3 90
jgt e28_dual_tail_5_lc_11
add r3 32
label e28_dual_tail_5_lc_11
cmp r3 111
jne e28_dual_tail_6
mov r7 r0
add r7 12
add r7 7400000000000000128
load8 r3 $r7
cmp r3 65
jlt e28_dual_tail_5_lc_12
cmp r3 90
jgt e28_dual_tail_5_lc_12
add r3 32
label e28_dual_tail_5_lc_12
cmp r3 101
jne e28_dual_tail_6
mov r7 r0
add r7 13
add r7 7400000000000000128
load8 r3 $r7
cmp r3 65
jlt e28_dual_tail_5_lc_13
cmp r3 90
jgt e28_dual_tail_5_lc_13
add r3 32
label e28_dual_tail_5_lc_13
cmp r3 115
jne e28_dual_tail_6
mov r7 r0
add r7 14
add r7 7400000000000000128
load8 r3 $r7
cmp r3 65
jlt e28_dual_tail_5_lc_14
cmp r3 90
jgt e28_dual_tail_5_lc_14
add r3 32
label e28_dual_tail_5_lc_14
cmp r3 32
jne e28_dual_tail_6
mov r7 r0
add r7 15
add r7 7400000000000000128
load8 r3 $r7
cmp r3 65
jlt e28_dual_tail_5_lc_15
cmp r3 90
jgt e28_dual_tail_5_lc_15
add r3 32
label e28_dual_tail_5_lc_15
cmp r3 105
jne e28_dual_tail_6
mov r7 r0
add r7 16
add r7 7400000000000000128
load8 r3 $r7
cmp r3 65
jlt e28_dual_tail_5_lc_16
cmp r3 90
jgt e28_dual_tail_5_lc_16
add r3 32
label e28_dual_tail_5_lc_16
cmp r3 116
jne e28_dual_tail_6
mov r7 r0
add r7 17
add r7 7400000000000000128
load8 r3 $r7
cmp r3 65
jlt e28_dual_tail_5_lc_17
cmp r3 90
jgt e28_dual_tail_5_lc_17
add r3 32
label e28_dual_tail_5_lc_17
cmp r3 32
jne e28_dual_tail_6
mov r7 r0
add r7 18
add r7 7400000000000000128
load8 r3 $r7
cmp r3 65
jlt e28_dual_tail_5_lc_18
cmp r3 90
jgt e28_dual_tail_5_lc_18
add r3 32
label e28_dual_tail_5_lc_18
cmp r3 114
jne e28_dual_tail_6
mov r7 r0
add r7 19
add r7 7400000000000000128
load8 r3 $r7
cmp r3 65
jlt e28_dual_tail_5_lc_19
cmp r3 90
jgt e28_dual_tail_5_lc_19
add r3 32
label e28_dual_tail_5_lc_19
cmp r3 101
jne e28_dual_tail_6
mov r7 r0
add r7 20
add r7 7400000000000000128
load8 r3 $r7
cmp r3 65
jlt e28_dual_tail_5_lc_20
cmp r3 90
jgt e28_dual_tail_5_lc_20
add r3 32
label e28_dual_tail_5_lc_20
cmp r3 113
jne e28_dual_tail_6
mov r7 r0
add r7 21
add r7 7400000000000000128
load8 r3 $r7
cmp r3 65
jlt e28_dual_tail_5_lc_21
cmp r3 90
jgt e28_dual_tail_5_lc_21
add r3 32
label e28_dual_tail_5_lc_21
cmp r3 117
jne e28_dual_tail_6
mov r7 r0
add r7 22
add r7 7400000000000000128
load8 r3 $r7
cmp r3 65
jlt e28_dual_tail_5_lc_22
cmp r3 90
jgt e28_dual_tail_5_lc_22
add r3 32
label e28_dual_tail_5_lc_22
cmp r3 105
jne e28_dual_tail_6
mov r7 r0
add r7 23
add r7 7400000000000000128
load8 r3 $r7
cmp r3 65
jlt e28_dual_tail_5_lc_23
cmp r3 90
jgt e28_dual_tail_5_lc_23
add r3 32
label e28_dual_tail_5_lc_23
cmp r3 114
jne e28_dual_tail_6
mov r7 r0
add r7 24
add r7 7400000000000000128
load8 r3 $r7
cmp r3 65
jlt e28_dual_tail_5_lc_24
cmp r3 90
jgt e28_dual_tail_5_lc_24
add r3 32
label e28_dual_tail_5_lc_24
cmp r3 101
jne e28_dual_tail_6
sub r10 25
set r12 1
jmp e28_subject
label e28_dual_tail_6
jmp e28_subject
label e28_context_follow
load8 r5 9000000000000000032
cmp r5 1
jlt e28_need_subject
cmp r5 48
jgt e28_need_subject
store8 9000000000000000128 r5
set r0 0
label e28_follow_copy
cmp r0 r5
jge e28_subject_ready
set r7 9000000000000000064
add r7 r0
load8 r3 $r7
set r7 9000000000000000256
add r7 r0
store8 $r7 r3
add r0 1
jmp e28_follow_copy
label e28_subject
mov r5 r10
sub r5 r4
cmp r5 1
jlt e28_need_subject
cmp r5 48
jgt e28_ambiguous
store8 9000000000000000128 r5
set r0 0
label e28_subject_copy
cmp r0 r5
jge e28_subject_normalize
set r7 7400000000000000128
add r7 r4
add r7 r0
load8 r3 $r7
cmp r3 32
je e28_subject_char_accepted
cmp r3 45
je e28_subject_char_accepted
cmp r3 95
je e28_subject_char_accepted
cmp r3 48
jlt e28_subject_non_ascii
cmp r3 57
jle e28_subject_char_accepted
cmp r3 65
jlt e28_subject_non_ascii
cmp r3 90
jle e28_subject_char_accepted
cmp r3 97
jlt e28_subject_non_ascii
cmp r3 122
jle e28_subject_char_accepted
label e28_subject_non_ascii
cmp r3 128
jlt e28_ambiguous
label e28_subject_char_accepted
cmp r3 65
jlt e28_subject_lower_done
cmp r3 90
jgt e28_subject_lower_done
add r3 32
label e28_subject_lower_done
set r7 9000000000000000256
add r7 r0
store8 $r7 r3
add r0 1
jmp e28_subject_copy
label e28_subject_normalize
load8 r5 9000000000000000128
cmp r5 4
jlt e28_subject_pronoun
label e28_article_0
cmp r5 4
jlt e28_article_1
load8 r3 9000000000000000256
cmp r3 101
jne e28_article_1
load8 r3 9000000000000000257
cmp r3 108
jne e28_article_1
load8 r3 9000000000000000258
cmp r3 32
jne e28_article_1
set r6 3
jmp e28_article_remove
label e28_article_1
cmp r5 4
jlt e28_article_2
load8 r3 9000000000000000256
cmp r3 108
jne e28_article_2
load8 r3 9000000000000000257
cmp r3 97
jne e28_article_2
load8 r3 9000000000000000258
cmp r3 32
jne e28_article_2
set r6 3
jmp e28_article_remove
label e28_article_2
cmp r5 5
jlt e28_article_3
load8 r3 9000000000000000256
cmp r3 116
jne e28_article_3
load8 r3 9000000000000000257
cmp r3 104
jne e28_article_3
load8 r3 9000000000000000258
cmp r3 101
jne e28_article_3
load8 r3 9000000000000000259
cmp r3 32
jne e28_article_3
set r6 4
jmp e28_article_remove
label e28_article_3
jmp e28_subject_pronoun
label e28_article_remove
set r0 0
label e28_article_shift
mov r7 r5
sub r7 r6
cmp r0 r7
jge e28_article_done
set r7 9000000000000000256
add r7 r0
mov r8 r7
add r8 r6
load8 r3 $r8
store8 $r7 r3
add r0 1
jmp e28_article_shift
label e28_article_done
sub r5 r6
store8 9000000000000000128 r5
label e28_subject_pronoun
load8 r5 9000000000000000128
cmp r5 2
je e28_maybe_it
cmp r5 3
jne e28_subject_ready
load8 r3 9000000000000000256
cmp r3 101
jne e28_subject_ready
load8 r3 9000000000000000257
cmp r3 115
jne e28_subject_ready
load8 r3 9000000000000000258
cmp r3 111
jne e28_subject_ready
jmp e28_pronoun_copy
label e28_maybe_it
load8 r3 9000000000000000256
cmp r3 105
jne e28_subject_ready
load8 r3 9000000000000000257
cmp r3 116
jne e28_subject_ready
jmp e28_pronoun_copy
label e28_pronoun_copy
load8 r5 9000000000000000032
cmp r5 1
jlt e28_need_subject
cmp r5 48
jgt e28_need_subject
store8 9000000000000000128 r5
set r0 0
label e28_pronoun_loop
cmp r0 r5
jge e28_subject_ready
set r7 9000000000000000064
add r7 r0
load8 r3 $r7
set r7 9000000000000000256
add r7 r0
store8 $r7 r3
add r0 1
jmp e28_pronoun_loop
label e28_subject_ready
load8 r0 9000000000000000128
cmp r0 0
je e28_need_subject
store8 9000000000000000129 r11
store8 9000000000000000130 r12
store8 9000000000000000131 r13
jmp e28_scan_init
label e28_ctx_delegate
jmp e28_e027_entry
label e28_delegate
store8 9000000000000000032 0
jmp e28_e027_entry
