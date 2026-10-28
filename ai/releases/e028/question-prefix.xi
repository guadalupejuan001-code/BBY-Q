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
label e28_scan_init
store8 9000000000000000400 0
store8 9000000000000000401 2
store8 9000000000000000402 0
store8 9000000000000000403 2
store8 9000000000000000404 0
store8 9000000000000000405 0
store8 9000000000000000408 0
store8 9000000000000000409 0
store8 9000000000000000422 0
store8 9000000000000000423 0
store8 9000000000000000426 0
store8 9000000000000000427 0
jmp e28_scan_loop
label e28_scan_loop
load8 r4 9000000000000000408
load8 r8 9000000000000000409
mul r8 256
add r4 r8
load8 r0 8900000000000000002
load8 r8 8900000000000000003
mul r8 256
add r0 r8
cmp r4 r0
jge e28_scan_done
cmp r4 512
jge e28_scan_done
mov r7 r4
mul r7 4
add r7 8900000000000001024
load8 r5 $r7
add r7 1
load8 r8 $r7
mul r8 256
add r5 r8
add r7 1
load8 r8 $r7
mul r8 65536
add r5 r8
add r7 1
load8 r6 $r7
load8 r11 9000000000000000128
mov r0 r11
add r0 4
cmp r6 r0
jlt e28_scan_next
set r0 0
label e28_compare_entity
cmp r0 r11
jge e28_entity_boundary
set r7 8900000000000100000
add r7 r5
add r7 r0
load8 r3 $r7
cmp r3 65
jlt e28_fact_entity_lc
cmp r3 90
jgt e28_fact_entity_lc
add r3 32
label e28_fact_entity_lc
set r7 9000000000000000256
add r7 r0
load8 r8 $r7
cmp r3 r8
jne e28_scan_next
add r0 1
jmp e28_compare_entity
label e28_entity_boundary
set r7 8900000000000100000
add r7 r5
add r7 r11
load8 r3 $r7
cmp r3 32
jne e28_scan_next
add r11 1
label e28_pred_0
mov r0 r11
add r0 12
cmp r0 r6
jge e28_pred_1
mov r7 r11
add r7 8900000000000100000
add r7 r5
load8 r3 $r7
cmp r3 65
jlt e28_pred_0_fold_0
cmp r3 90
jgt e28_pred_0_fold_0
add r3 32
label e28_pred_0_fold_0
cmp r3 110
jne e28_pred_1
mov r7 r11
add r7 1
add r7 8900000000000100000
add r7 r5
load8 r3 $r7
cmp r3 65
jlt e28_pred_0_fold_1
cmp r3 90
jgt e28_pred_0_fold_1
add r3 32
label e28_pred_0_fold_1
cmp r3 111
jne e28_pred_1
mov r7 r11
add r7 2
add r7 8900000000000100000
add r7 r5
load8 r3 $r7
cmp r3 65
jlt e28_pred_0_fold_2
cmp r3 90
jgt e28_pred_0_fold_2
add r3 32
label e28_pred_0_fold_2
cmp r3 32
jne e28_pred_1
mov r7 r11
add r7 3
add r7 8900000000000100000
add r7 r5
load8 r3 $r7
cmp r3 65
jlt e28_pred_0_fold_3
cmp r3 90
jgt e28_pred_0_fold_3
add r3 32
label e28_pred_0_fold_3
cmp r3 114
jne e28_pred_1
mov r7 r11
add r7 4
add r7 8900000000000100000
add r7 r5
load8 r3 $r7
cmp r3 65
jlt e28_pred_0_fold_4
cmp r3 90
jgt e28_pred_0_fold_4
add r3 32
label e28_pred_0_fold_4
cmp r3 101
jne e28_pred_1
mov r7 r11
add r7 5
add r7 8900000000000100000
add r7 r5
load8 r3 $r7
cmp r3 65
jlt e28_pred_0_fold_5
cmp r3 90
jgt e28_pred_0_fold_5
add r3 32
label e28_pred_0_fold_5
cmp r3 113
jne e28_pred_1
mov r7 r11
add r7 6
add r7 8900000000000100000
add r7 r5
load8 r3 $r7
cmp r3 65
jlt e28_pred_0_fold_6
cmp r3 90
jgt e28_pred_0_fold_6
add r3 32
label e28_pred_0_fold_6
cmp r3 117
jne e28_pred_1
mov r7 r11
add r7 7
add r7 8900000000000100000
add r7 r5
load8 r3 $r7
cmp r3 65
jlt e28_pred_0_fold_7
cmp r3 90
jgt e28_pred_0_fold_7
add r3 32
label e28_pred_0_fold_7
cmp r3 105
jne e28_pred_1
mov r7 r11
add r7 8
add r7 8900000000000100000
add r7 r5
load8 r3 $r7
cmp r3 65
jlt e28_pred_0_fold_8
cmp r3 90
jgt e28_pred_0_fold_8
add r3 32
label e28_pred_0_fold_8
cmp r3 101
jne e28_pred_1
mov r7 r11
add r7 9
add r7 8900000000000100000
add r7 r5
load8 r3 $r7
cmp r3 65
jlt e28_pred_0_fold_9
cmp r3 90
jgt e28_pred_0_fold_9
add r3 32
label e28_pred_0_fold_9
cmp r3 114
jne e28_pred_1
mov r7 r11
add r7 10
add r7 8900000000000100000
add r7 r5
load8 r3 $r7
cmp r3 65
jlt e28_pred_0_fold_10
cmp r3 90
jgt e28_pred_0_fold_10
add r3 32
label e28_pred_0_fold_10
cmp r3 101
jne e28_pred_1
mov r7 r11
add r7 11
add r7 8900000000000100000
add r7 r5
load8 r3 $r7
cmp r3 65
jlt e28_pred_0_fold_11
cmp r3 90
jgt e28_pred_0_fold_11
add r3 32
label e28_pred_0_fold_11
cmp r3 32
jne e28_pred_1
set r12 2
set r13 1
mov r14 r11
add r14 12
jmp e28_fact_value
label e28_pred_1
mov r0 r11
add r0 12
cmp r0 r6
jge e28_pred_2
mov r7 r11
add r7 8900000000000100000
add r7 r5
load8 r3 $r7
cmp r3 65
jlt e28_pred_1_fold_0
cmp r3 90
jgt e28_pred_1_fold_0
add r3 32
label e28_pred_1_fold_0
cmp r3 110
jne e28_pred_2
mov r7 r11
add r7 1
add r7 8900000000000100000
add r7 r5
load8 r3 $r7
cmp r3 65
jlt e28_pred_1_fold_1
cmp r3 90
jgt e28_pred_1_fold_1
add r3 32
label e28_pred_1_fold_1
cmp r3 111
jne e28_pred_2
mov r7 r11
add r7 2
add r7 8900000000000100000
add r7 r5
load8 r3 $r7
cmp r3 65
jlt e28_pred_1_fold_2
cmp r3 90
jgt e28_pred_1_fold_2
add r3 32
label e28_pred_1_fold_2
cmp r3 32
jne e28_pred_2
mov r7 r11
add r7 3
add r7 8900000000000100000
add r7 r5
load8 r3 $r7
cmp r3 65
jlt e28_pred_1_fold_3
cmp r3 90
jgt e28_pred_1_fold_3
add r3 32
label e28_pred_1_fold_3
cmp r3 110
jne e28_pred_2
mov r7 r11
add r7 4
add r7 8900000000000100000
add r7 r5
load8 r3 $r7
cmp r3 65
jlt e28_pred_1_fold_4
cmp r3 90
jgt e28_pred_1_fold_4
add r3 32
label e28_pred_1_fold_4
cmp r3 101
jne e28_pred_2
mov r7 r11
add r7 5
add r7 8900000000000100000
add r7 r5
load8 r3 $r7
cmp r3 65
jlt e28_pred_1_fold_5
cmp r3 90
jgt e28_pred_1_fold_5
add r3 32
label e28_pred_1_fold_5
cmp r3 99
jne e28_pred_2
mov r7 r11
add r7 6
add r7 8900000000000100000
add r7 r5
load8 r3 $r7
cmp r3 65
jlt e28_pred_1_fold_6
cmp r3 90
jgt e28_pred_1_fold_6
add r3 32
label e28_pred_1_fold_6
cmp r3 101
jne e28_pred_2
mov r7 r11
add r7 7
add r7 8900000000000100000
add r7 r5
load8 r3 $r7
cmp r3 65
jlt e28_pred_1_fold_7
cmp r3 90
jgt e28_pred_1_fold_7
add r3 32
label e28_pred_1_fold_7
cmp r3 115
jne e28_pred_2
mov r7 r11
add r7 8
add r7 8900000000000100000
add r7 r5
load8 r3 $r7
cmp r3 65
jlt e28_pred_1_fold_8
cmp r3 90
jgt e28_pred_1_fold_8
add r3 32
label e28_pred_1_fold_8
cmp r3 105
jne e28_pred_2
mov r7 r11
add r7 9
add r7 8900000000000100000
add r7 r5
load8 r3 $r7
cmp r3 65
jlt e28_pred_1_fold_9
cmp r3 90
jgt e28_pred_1_fold_9
add r3 32
label e28_pred_1_fold_9
cmp r3 116
jne e28_pred_2
mov r7 r11
add r7 10
add r7 8900000000000100000
add r7 r5
load8 r3 $r7
cmp r3 65
jlt e28_pred_1_fold_10
cmp r3 90
jgt e28_pred_1_fold_10
add r3 32
label e28_pred_1_fold_10
cmp r3 97
jne e28_pred_2
mov r7 r11
add r7 11
add r7 8900000000000100000
add r7 r5
load8 r3 $r7
cmp r3 65
jlt e28_pred_1_fold_11
cmp r3 90
jgt e28_pred_1_fold_11
add r3 32
label e28_pred_1_fold_11
cmp r3 32
jne e28_pred_2
set r12 2
set r13 1
mov r14 r11
add r14 12
jmp e28_fact_value
label e28_pred_2
mov r0 r11
add r0 6
cmp r0 r6
jge e28_pred_3
mov r7 r11
add r7 8900000000000100000
add r7 r5
load8 r3 $r7
cmp r3 65
jlt e28_pred_2_fold_0
cmp r3 90
jgt e28_pred_2_fold_0
add r3 32
label e28_pred_2_fold_0
cmp r3 110
jne e28_pred_3
mov r7 r11
add r7 1
add r7 8900000000000100000
add r7 r5
load8 r3 $r7
cmp r3 65
jlt e28_pred_2_fold_1
cmp r3 90
jgt e28_pred_2_fold_1
add r3 32
label e28_pred_2_fold_1
cmp r3 111
jne e28_pred_3
mov r7 r11
add r7 2
add r7 8900000000000100000
add r7 r5
load8 r3 $r7
cmp r3 65
jlt e28_pred_2_fold_2
cmp r3 90
jgt e28_pred_2_fold_2
add r3 32
label e28_pred_2_fold_2
cmp r3 32
jne e28_pred_3
mov r7 r11
add r7 3
add r7 8900000000000100000
add r7 r5
load8 r3 $r7
cmp r3 65
jlt e28_pred_2_fold_3
cmp r3 90
jgt e28_pred_2_fold_3
add r3 32
label e28_pred_2_fold_3
cmp r3 101
jne e28_pred_3
mov r7 r11
add r7 4
add r7 8900000000000100000
add r7 r5
load8 r3 $r7
cmp r3 65
jlt e28_pred_2_fold_4
cmp r3 90
jgt e28_pred_2_fold_4
add r3 32
label e28_pred_2_fold_4
cmp r3 115
jne e28_pred_3
mov r7 r11
add r7 5
add r7 8900000000000100000
add r7 r5
load8 r3 $r7
cmp r3 65
jlt e28_pred_2_fold_5
cmp r3 90
jgt e28_pred_2_fold_5
add r3 32
label e28_pred_2_fold_5
cmp r3 32
jne e28_pred_3
set r12 1
set r13 1
mov r14 r11
add r14 6
jmp e28_fact_value
label e28_pred_3
mov r0 r11
add r0 7
cmp r0 r6
jge e28_pred_4
mov r7 r11
add r7 8900000000000100000
add r7 r5
load8 r3 $r7
cmp r3 65
jlt e28_pred_3_fold_0
cmp r3 90
jgt e28_pred_3_fold_0
add r3 32
label e28_pred_3_fold_0
cmp r3 105
jne e28_pred_4
mov r7 r11
add r7 1
add r7 8900000000000100000
add r7 r5
load8 r3 $r7
cmp r3 65
jlt e28_pred_3_fold_1
cmp r3 90
jgt e28_pred_3_fold_1
add r3 32
label e28_pred_3_fold_1
cmp r3 115
jne e28_pred_4
mov r7 r11
add r7 2
add r7 8900000000000100000
add r7 r5
load8 r3 $r7
cmp r3 65
jlt e28_pred_3_fold_2
cmp r3 90
jgt e28_pred_3_fold_2
add r3 32
label e28_pred_3_fold_2
cmp r3 32
jne e28_pred_4
mov r7 r11
add r7 3
add r7 8900000000000100000
add r7 r5
load8 r3 $r7
cmp r3 65
jlt e28_pred_3_fold_3
cmp r3 90
jgt e28_pred_3_fold_3
add r3 32
label e28_pred_3_fold_3
cmp r3 110
jne e28_pred_4
mov r7 r11
add r7 4
add r7 8900000000000100000
add r7 r5
load8 r3 $r7
cmp r3 65
jlt e28_pred_3_fold_4
cmp r3 90
jgt e28_pred_3_fold_4
add r3 32
label e28_pred_3_fold_4
cmp r3 111
jne e28_pred_4
mov r7 r11
add r7 5
add r7 8900000000000100000
add r7 r5
load8 r3 $r7
cmp r3 65
jlt e28_pred_3_fold_5
cmp r3 90
jgt e28_pred_3_fold_5
add r3 32
label e28_pred_3_fold_5
cmp r3 116
jne e28_pred_4
mov r7 r11
add r7 6
add r7 8900000000000100000
add r7 r5
load8 r3 $r7
cmp r3 65
jlt e28_pred_3_fold_6
cmp r3 90
jgt e28_pred_3_fold_6
add r3 32
label e28_pred_3_fold_6
cmp r3 32
jne e28_pred_4
set r12 1
set r13 1
mov r14 r11
add r14 7
jmp e28_fact_value
label e28_pred_4
mov r0 r11
add r0 14
cmp r0 r6
jge e28_pred_5
mov r7 r11
add r7 8900000000000100000
add r7 r5
load8 r3 $r7
cmp r3 65
jlt e28_pred_4_fold_0
cmp r3 90
jgt e28_pred_4_fold_0
add r3 32
label e28_pred_4_fold_0
cmp r3 100
jne e28_pred_5
mov r7 r11
add r7 1
add r7 8900000000000100000
add r7 r5
load8 r3 $r7
cmp r3 65
jlt e28_pred_4_fold_1
cmp r3 90
jgt e28_pred_4_fold_1
add r3 32
label e28_pred_4_fold_1
cmp r3 111
jne e28_pred_5
mov r7 r11
add r7 2
add r7 8900000000000100000
add r7 r5
load8 r3 $r7
cmp r3 65
jlt e28_pred_4_fold_2
cmp r3 90
jgt e28_pred_4_fold_2
add r3 32
label e28_pred_4_fold_2
cmp r3 101
jne e28_pred_5
mov r7 r11
add r7 3
add r7 8900000000000100000
add r7 r5
load8 r3 $r7
cmp r3 65
jlt e28_pred_4_fold_3
cmp r3 90
jgt e28_pred_4_fold_3
add r3 32
label e28_pred_4_fold_3
cmp r3 115
jne e28_pred_5
mov r7 r11
add r7 4
add r7 8900000000000100000
add r7 r5
load8 r3 $r7
cmp r3 65
jlt e28_pred_4_fold_4
cmp r3 90
jgt e28_pred_4_fold_4
add r3 32
label e28_pred_4_fold_4
cmp r3 32
jne e28_pred_5
mov r7 r11
add r7 5
add r7 8900000000000100000
add r7 r5
load8 r3 $r7
cmp r3 65
jlt e28_pred_4_fold_5
cmp r3 90
jgt e28_pred_4_fold_5
add r3 32
label e28_pred_4_fold_5
cmp r3 110
jne e28_pred_5
mov r7 r11
add r7 6
add r7 8900000000000100000
add r7 r5
load8 r3 $r7
cmp r3 65
jlt e28_pred_4_fold_6
cmp r3 90
jgt e28_pred_4_fold_6
add r3 32
label e28_pred_4_fold_6
cmp r3 111
jne e28_pred_5
mov r7 r11
add r7 7
add r7 8900000000000100000
add r7 r5
load8 r3 $r7
cmp r3 65
jlt e28_pred_4_fold_7
cmp r3 90
jgt e28_pred_4_fold_7
add r3 32
label e28_pred_4_fold_7
cmp r3 116
jne e28_pred_5
mov r7 r11
add r7 8
add r7 8900000000000100000
add r7 r5
load8 r3 $r7
cmp r3 65
jlt e28_pred_4_fold_8
cmp r3 90
jgt e28_pred_4_fold_8
add r3 32
label e28_pred_4_fold_8
cmp r3 32
jne e28_pred_5
mov r7 r11
add r7 9
add r7 8900000000000100000
add r7 r5
load8 r3 $r7
cmp r3 65
jlt e28_pred_4_fold_9
cmp r3 90
jgt e28_pred_4_fold_9
add r3 32
label e28_pred_4_fold_9
cmp r3 110
jne e28_pred_5
mov r7 r11
add r7 10
add r7 8900000000000100000
add r7 r5
load8 r3 $r7
cmp r3 65
jlt e28_pred_4_fold_10
cmp r3 90
jgt e28_pred_4_fold_10
add r3 32
label e28_pred_4_fold_10
cmp r3 101
jne e28_pred_5
mov r7 r11
add r7 11
add r7 8900000000000100000
add r7 r5
load8 r3 $r7
cmp r3 65
jlt e28_pred_4_fold_11
cmp r3 90
jgt e28_pred_4_fold_11
add r3 32
label e28_pred_4_fold_11
cmp r3 101
jne e28_pred_5
mov r7 r11
add r7 12
add r7 8900000000000100000
add r7 r5
load8 r3 $r7
cmp r3 65
jlt e28_pred_4_fold_12
cmp r3 90
jgt e28_pred_4_fold_12
add r3 32
label e28_pred_4_fold_12
cmp r3 100
jne e28_pred_5
mov r7 r11
add r7 13
add r7 8900000000000100000
add r7 r5
load8 r3 $r7
cmp r3 65
jlt e28_pred_4_fold_13
cmp r3 90
jgt e28_pred_4_fold_13
add r3 32
label e28_pred_4_fold_13
cmp r3 32
jne e28_pred_5
set r12 2
set r13 1
mov r14 r11
add r14 14
jmp e28_fact_value
label e28_pred_5
mov r0 r11
add r0 17
cmp r0 r6
jge e28_pred_6
mov r7 r11
add r7 8900000000000100000
add r7 r5
load8 r3 $r7
cmp r3 65
jlt e28_pred_5_fold_0
cmp r3 90
jgt e28_pred_5_fold_0
add r3 32
label e28_pred_5_fold_0
cmp r3 100
jne e28_pred_6
mov r7 r11
add r7 1
add r7 8900000000000100000
add r7 r5
load8 r3 $r7
cmp r3 65
jlt e28_pred_5_fold_1
cmp r3 90
jgt e28_pred_5_fold_1
add r3 32
label e28_pred_5_fold_1
cmp r3 111
jne e28_pred_6
mov r7 r11
add r7 2
add r7 8900000000000100000
add r7 r5
load8 r3 $r7
cmp r3 65
jlt e28_pred_5_fold_2
cmp r3 90
jgt e28_pred_5_fold_2
add r3 32
label e28_pred_5_fold_2
cmp r3 101
jne e28_pred_6
mov r7 r11
add r7 3
add r7 8900000000000100000
add r7 r5
load8 r3 $r7
cmp r3 65
jlt e28_pred_5_fold_3
cmp r3 90
jgt e28_pred_5_fold_3
add r3 32
label e28_pred_5_fold_3
cmp r3 115
jne e28_pred_6
mov r7 r11
add r7 4
add r7 8900000000000100000
add r7 r5
load8 r3 $r7
cmp r3 65
jlt e28_pred_5_fold_4
cmp r3 90
jgt e28_pred_5_fold_4
add r3 32
label e28_pred_5_fold_4
cmp r3 32
jne e28_pred_6
mov r7 r11
add r7 5
add r7 8900000000000100000
add r7 r5
load8 r3 $r7
cmp r3 65
jlt e28_pred_5_fold_5
cmp r3 90
jgt e28_pred_5_fold_5
add r3 32
label e28_pred_5_fold_5
cmp r3 110
jne e28_pred_6
mov r7 r11
add r7 6
add r7 8900000000000100000
add r7 r5
load8 r3 $r7
cmp r3 65
jlt e28_pred_5_fold_6
cmp r3 90
jgt e28_pred_5_fold_6
add r3 32
label e28_pred_5_fold_6
cmp r3 111
jne e28_pred_6
mov r7 r11
add r7 7
add r7 8900000000000100000
add r7 r5
load8 r3 $r7
cmp r3 65
jlt e28_pred_5_fold_7
cmp r3 90
jgt e28_pred_5_fold_7
add r3 32
label e28_pred_5_fold_7
cmp r3 116
jne e28_pred_6
mov r7 r11
add r7 8
add r7 8900000000000100000
add r7 r5
load8 r3 $r7
cmp r3 65
jlt e28_pred_5_fold_8
cmp r3 90
jgt e28_pred_5_fold_8
add r3 32
label e28_pred_5_fold_8
cmp r3 32
jne e28_pred_6
mov r7 r11
add r7 9
add r7 8900000000000100000
add r7 r5
load8 r3 $r7
cmp r3 65
jlt e28_pred_5_fold_9
cmp r3 90
jgt e28_pred_5_fold_9
add r3 32
label e28_pred_5_fold_9
cmp r3 114
jne e28_pred_6
mov r7 r11
add r7 10
add r7 8900000000000100000
add r7 r5
load8 r3 $r7
cmp r3 65
jlt e28_pred_5_fold_10
cmp r3 90
jgt e28_pred_5_fold_10
add r3 32
label e28_pred_5_fold_10
cmp r3 101
jne e28_pred_6
mov r7 r11
add r7 11
add r7 8900000000000100000
add r7 r5
load8 r3 $r7
cmp r3 65
jlt e28_pred_5_fold_11
cmp r3 90
jgt e28_pred_5_fold_11
add r3 32
label e28_pred_5_fold_11
cmp r3 113
jne e28_pred_6
mov r7 r11
add r7 12
add r7 8900000000000100000
add r7 r5
load8 r3 $r7
cmp r3 65
jlt e28_pred_5_fold_12
cmp r3 90
jgt e28_pred_5_fold_12
add r3 32
label e28_pred_5_fold_12
cmp r3 117
jne e28_pred_6
mov r7 r11
add r7 13
add r7 8900000000000100000
add r7 r5
load8 r3 $r7
cmp r3 65
jlt e28_pred_5_fold_13
cmp r3 90
jgt e28_pred_5_fold_13
add r3 32
label e28_pred_5_fold_13
cmp r3 105
jne e28_pred_6
mov r7 r11
add r7 14
add r7 8900000000000100000
add r7 r5
load8 r3 $r7
cmp r3 65
jlt e28_pred_5_fold_14
cmp r3 90
jgt e28_pred_5_fold_14
add r3 32
label e28_pred_5_fold_14
cmp r3 114
jne e28_pred_6
mov r7 r11
add r7 15
add r7 8900000000000100000
add r7 r5
load8 r3 $r7
cmp r3 65
jlt e28_pred_5_fold_15
cmp r3 90
jgt e28_pred_5_fold_15
add r3 32
label e28_pred_5_fold_15
cmp r3 101
jne e28_pred_6
mov r7 r11
add r7 16
add r7 8900000000000100000
add r7 r5
load8 r3 $r7
cmp r3 65
jlt e28_pred_5_fold_16
cmp r3 90
jgt e28_pred_5_fold_16
add r3 32
label e28_pred_5_fold_16
cmp r3 32
jne e28_pred_6
set r12 2
set r13 1
mov r14 r11
add r14 17
jmp e28_fact_value
label e28_pred_6
mov r0 r11
add r0 9
cmp r0 r6
jge e28_pred_7
mov r7 r11
add r7 8900000000000100000
add r7 r5
load8 r3 $r7
cmp r3 65
jlt e28_pred_6_fold_0
cmp r3 90
jgt e28_pred_6_fold_0
add r3 32
label e28_pred_6_fold_0
cmp r3 114
jne e28_pred_7
mov r7 r11
add r7 1
add r7 8900000000000100000
add r7 r5
load8 r3 $r7
cmp r3 65
jlt e28_pred_6_fold_1
cmp r3 90
jgt e28_pred_6_fold_1
add r3 32
label e28_pred_6_fold_1
cmp r3 101
jne e28_pred_7
mov r7 r11
add r7 2
add r7 8900000000000100000
add r7 r5
load8 r3 $r7
cmp r3 65
jlt e28_pred_6_fold_2
cmp r3 90
jgt e28_pred_6_fold_2
add r3 32
label e28_pred_6_fold_2
cmp r3 113
jne e28_pred_7
mov r7 r11
add r7 3
add r7 8900000000000100000
add r7 r5
load8 r3 $r7
cmp r3 65
jlt e28_pred_6_fold_3
cmp r3 90
jgt e28_pred_6_fold_3
add r3 32
label e28_pred_6_fold_3
cmp r3 117
jne e28_pred_7
mov r7 r11
add r7 4
add r7 8900000000000100000
add r7 r5
load8 r3 $r7
cmp r3 65
jlt e28_pred_6_fold_4
cmp r3 90
jgt e28_pred_6_fold_4
add r3 32
label e28_pred_6_fold_4
cmp r3 105
jne e28_pred_7
mov r7 r11
add r7 5
add r7 8900000000000100000
add r7 r5
load8 r3 $r7
cmp r3 65
jlt e28_pred_6_fold_5
cmp r3 90
jgt e28_pred_6_fold_5
add r3 32
label e28_pred_6_fold_5
cmp r3 101
jne e28_pred_7
mov r7 r11
add r7 6
add r7 8900000000000100000
add r7 r5
load8 r3 $r7
cmp r3 65
jlt e28_pred_6_fold_6
cmp r3 90
jgt e28_pred_6_fold_6
add r3 32
label e28_pred_6_fold_6
cmp r3 114
jne e28_pred_7
mov r7 r11
add r7 7
add r7 8900000000000100000
add r7 r5
load8 r3 $r7
cmp r3 65
jlt e28_pred_6_fold_7
cmp r3 90
jgt e28_pred_6_fold_7
add r3 32
label e28_pred_6_fold_7
cmp r3 101
jne e28_pred_7
mov r7 r11
add r7 8
add r7 8900000000000100000
add r7 r5
load8 r3 $r7
cmp r3 65
jlt e28_pred_6_fold_8
cmp r3 90
jgt e28_pred_6_fold_8
add r3 32
label e28_pred_6_fold_8
cmp r3 32
jne e28_pred_7
set r12 2
set r13 0
mov r14 r11
add r14 9
jmp e28_fact_value
label e28_pred_7
mov r0 r11
add r0 9
cmp r0 r6
jge e28_pred_8
mov r7 r11
add r7 8900000000000100000
add r7 r5
load8 r3 $r7
cmp r3 65
jlt e28_pred_7_fold_0
cmp r3 90
jgt e28_pred_7_fold_0
add r3 32
label e28_pred_7_fold_0
cmp r3 110
jne e28_pred_8
mov r7 r11
add r7 1
add r7 8900000000000100000
add r7 r5
load8 r3 $r7
cmp r3 65
jlt e28_pred_7_fold_1
cmp r3 90
jgt e28_pred_7_fold_1
add r3 32
label e28_pred_7_fold_1
cmp r3 101
jne e28_pred_8
mov r7 r11
add r7 2
add r7 8900000000000100000
add r7 r5
load8 r3 $r7
cmp r3 65
jlt e28_pred_7_fold_2
cmp r3 90
jgt e28_pred_7_fold_2
add r3 32
label e28_pred_7_fold_2
cmp r3 99
jne e28_pred_8
mov r7 r11
add r7 3
add r7 8900000000000100000
add r7 r5
load8 r3 $r7
cmp r3 65
jlt e28_pred_7_fold_3
cmp r3 90
jgt e28_pred_7_fold_3
add r3 32
label e28_pred_7_fold_3
cmp r3 101
jne e28_pred_8
mov r7 r11
add r7 4
add r7 8900000000000100000
add r7 r5
load8 r3 $r7
cmp r3 65
jlt e28_pred_7_fold_4
cmp r3 90
jgt e28_pred_7_fold_4
add r3 32
label e28_pred_7_fold_4
cmp r3 115
jne e28_pred_8
mov r7 r11
add r7 5
add r7 8900000000000100000
add r7 r5
load8 r3 $r7
cmp r3 65
jlt e28_pred_7_fold_5
cmp r3 90
jgt e28_pred_7_fold_5
add r3 32
label e28_pred_7_fold_5
cmp r3 105
jne e28_pred_8
mov r7 r11
add r7 6
add r7 8900000000000100000
add r7 r5
load8 r3 $r7
cmp r3 65
jlt e28_pred_7_fold_6
cmp r3 90
jgt e28_pred_7_fold_6
add r3 32
label e28_pred_7_fold_6
cmp r3 116
jne e28_pred_8
mov r7 r11
add r7 7
add r7 8900000000000100000
add r7 r5
load8 r3 $r7
cmp r3 65
jlt e28_pred_7_fold_7
cmp r3 90
jgt e28_pred_7_fold_7
add r3 32
label e28_pred_7_fold_7
cmp r3 97
jne e28_pred_8
mov r7 r11
add r7 8
add r7 8900000000000100000
add r7 r5
load8 r3 $r7
cmp r3 65
jlt e28_pred_7_fold_8
cmp r3 90
jgt e28_pred_7_fold_8
add r3 32
label e28_pred_7_fold_8
cmp r3 32
jne e28_pred_8
set r12 2
set r13 0
mov r14 r11
add r14 9
jmp e28_fact_value
label e28_pred_8
mov r0 r11
add r0 3
cmp r0 r6
jge e28_pred_9
mov r7 r11
add r7 8900000000000100000
add r7 r5
load8 r3 $r7
cmp r3 65
jlt e28_pred_8_fold_0
cmp r3 90
jgt e28_pred_8_fold_0
add r3 32
label e28_pred_8_fold_0
cmp r3 101
jne e28_pred_9
mov r7 r11
add r7 1
add r7 8900000000000100000
add r7 r5
load8 r3 $r7
cmp r3 65
jlt e28_pred_8_fold_1
cmp r3 90
jgt e28_pred_8_fold_1
add r3 32
label e28_pred_8_fold_1
cmp r3 115
jne e28_pred_9
mov r7 r11
add r7 2
add r7 8900000000000100000
add r7 r5
load8 r3 $r7
cmp r3 65
jlt e28_pred_8_fold_2
cmp r3 90
jgt e28_pred_8_fold_2
add r3 32
label e28_pred_8_fold_2
cmp r3 32
jne e28_pred_9
set r12 1
set r13 0
mov r14 r11
add r14 3
jmp e28_fact_value
label e28_pred_9
mov r0 r11
add r0 6
cmp r0 r6
jge e28_pred_10
mov r7 r11
add r7 8900000000000100000
add r7 r5
load8 r3 $r7
cmp r3 65
jlt e28_pred_9_fold_0
cmp r3 90
jgt e28_pred_9_fold_0
add r3 32
label e28_pred_9_fold_0
cmp r3 110
jne e28_pred_10
mov r7 r11
add r7 1
add r7 8900000000000100000
add r7 r5
load8 r3 $r7
cmp r3 65
jlt e28_pred_9_fold_1
cmp r3 90
jgt e28_pred_9_fold_1
add r3 32
label e28_pred_9_fold_1
cmp r3 101
jne e28_pred_10
mov r7 r11
add r7 2
add r7 8900000000000100000
add r7 r5
load8 r3 $r7
cmp r3 65
jlt e28_pred_9_fold_2
cmp r3 90
jgt e28_pred_9_fold_2
add r3 32
label e28_pred_9_fold_2
cmp r3 101
jne e28_pred_10
mov r7 r11
add r7 3
add r7 8900000000000100000
add r7 r5
load8 r3 $r7
cmp r3 65
jlt e28_pred_9_fold_3
cmp r3 90
jgt e28_pred_9_fold_3
add r3 32
label e28_pred_9_fold_3
cmp r3 100
jne e28_pred_10
mov r7 r11
add r7 4
add r7 8900000000000100000
add r7 r5
load8 r3 $r7
cmp r3 65
jlt e28_pred_9_fold_4
cmp r3 90
jgt e28_pred_9_fold_4
add r3 32
label e28_pred_9_fold_4
cmp r3 115
jne e28_pred_10
mov r7 r11
add r7 5
add r7 8900000000000100000
add r7 r5
load8 r3 $r7
cmp r3 65
jlt e28_pred_9_fold_5
cmp r3 90
jgt e28_pred_9_fold_5
add r3 32
label e28_pred_9_fold_5
cmp r3 32
jne e28_pred_10
set r12 2
set r13 0
mov r14 r11
add r14 6
jmp e28_fact_value
label e28_pred_10
mov r0 r11
add r0 9
cmp r0 r6
jge e28_pred_11
mov r7 r11
add r7 8900000000000100000
add r7 r5
load8 r3 $r7
cmp r3 65
jlt e28_pred_10_fold_0
cmp r3 90
jgt e28_pred_10_fold_0
add r3 32
label e28_pred_10_fold_0
cmp r3 114
jne e28_pred_11
mov r7 r11
add r7 1
add r7 8900000000000100000
add r7 r5
load8 r3 $r7
cmp r3 65
jlt e28_pred_10_fold_1
cmp r3 90
jgt e28_pred_10_fold_1
add r3 32
label e28_pred_10_fold_1
cmp r3 101
jne e28_pred_11
mov r7 r11
add r7 2
add r7 8900000000000100000
add r7 r5
load8 r3 $r7
cmp r3 65
jlt e28_pred_10_fold_2
cmp r3 90
jgt e28_pred_10_fold_2
add r3 32
label e28_pred_10_fold_2
cmp r3 113
jne e28_pred_11
mov r7 r11
add r7 3
add r7 8900000000000100000
add r7 r5
load8 r3 $r7
cmp r3 65
jlt e28_pred_10_fold_3
cmp r3 90
jgt e28_pred_10_fold_3
add r3 32
label e28_pred_10_fold_3
cmp r3 117
jne e28_pred_11
mov r7 r11
add r7 4
add r7 8900000000000100000
add r7 r5
load8 r3 $r7
cmp r3 65
jlt e28_pred_10_fold_4
cmp r3 90
jgt e28_pred_10_fold_4
add r3 32
label e28_pred_10_fold_4
cmp r3 105
jne e28_pred_11
mov r7 r11
add r7 5
add r7 8900000000000100000
add r7 r5
load8 r3 $r7
cmp r3 65
jlt e28_pred_10_fold_5
cmp r3 90
jgt e28_pred_10_fold_5
add r3 32
label e28_pred_10_fold_5
cmp r3 114
jne e28_pred_11
mov r7 r11
add r7 6
add r7 8900000000000100000
add r7 r5
load8 r3 $r7
cmp r3 65
jlt e28_pred_10_fold_6
cmp r3 90
jgt e28_pred_10_fold_6
add r3 32
label e28_pred_10_fold_6
cmp r3 101
jne e28_pred_11
mov r7 r11
add r7 7
add r7 8900000000000100000
add r7 r5
load8 r3 $r7
cmp r3 65
jlt e28_pred_10_fold_7
cmp r3 90
jgt e28_pred_10_fold_7
add r3 32
label e28_pred_10_fold_7
cmp r3 115
jne e28_pred_11
mov r7 r11
add r7 8
add r7 8900000000000100000
add r7 r5
load8 r3 $r7
cmp r3 65
jlt e28_pred_10_fold_8
cmp r3 90
jgt e28_pred_10_fold_8
add r3 32
label e28_pred_10_fold_8
cmp r3 32
jne e28_pred_11
set r12 2
set r13 0
mov r14 r11
add r14 9
jmp e28_fact_value
label e28_pred_11
mov r0 r11
add r0 3
cmp r0 r6
jge e28_pred_12
mov r7 r11
add r7 8900000000000100000
add r7 r5
load8 r3 $r7
cmp r3 65
jlt e28_pred_11_fold_0
cmp r3 90
jgt e28_pred_11_fold_0
add r3 32
label e28_pred_11_fold_0
cmp r3 105
jne e28_pred_12
mov r7 r11
add r7 1
add r7 8900000000000100000
add r7 r5
load8 r3 $r7
cmp r3 65
jlt e28_pred_11_fold_1
cmp r3 90
jgt e28_pred_11_fold_1
add r3 32
label e28_pred_11_fold_1
cmp r3 115
jne e28_pred_12
mov r7 r11
add r7 2
add r7 8900000000000100000
add r7 r5
load8 r3 $r7
cmp r3 65
jlt e28_pred_11_fold_2
cmp r3 90
jgt e28_pred_11_fold_2
add r3 32
label e28_pred_11_fold_2
cmp r3 32
jne e28_pred_12
set r12 1
set r13 0
mov r14 r11
add r14 3
jmp e28_fact_value
label e28_pred_12
jmp e28_scan_next
label e28_fact_value
mov r10 r6
sub r10 r14
cmp r10 1
jlt e28_scan_next
cmp r10 81
jgt e28_scan_next
mov r0 r6
sub r0 1
set r7 8900000000000100000
add r7 r5
add r7 r0
load8 r3 $r7
cmp r3 46
jne e28_fact_no_dot
sub r10 1
label e28_fact_no_dot
cmp r10 1
jlt e28_scan_next
cmp r10 80
jgt e28_scan_next
set r0 0
set r9 0
label e28_value_validate
cmp r0 r10
jge e28_fact_valid
set r7 8900000000000100000
add r7 r5
add r7 r14
add r7 r0
load8 r3 $r7
cmp r3 10
je e28_scan_next
cmp r3 13
je e28_scan_next
cmp r3 33
je e28_scan_next
cmp r3 34
je e28_scan_next
cmp r3 39
je e28_scan_next
cmp r3 44
je e28_scan_next
cmp r3 46
je e28_scan_next
cmp r3 58
je e28_scan_next
cmp r3 59
je e28_scan_next
cmp r3 63
je e28_scan_next
cmp r3 91
je e28_scan_next
cmp r3 93
je e28_scan_next
cmp r3 32
jne e28_value_not_space
cmp r0 0
je e28_scan_next
cmp r9 32
je e28_scan_next
mov r8 r10
sub r8 1
cmp r0 r8
je e28_scan_next
label e28_value_not_space
mov r9 r3
add r0 1
jmp e28_value_validate
label e28_fact_valid
load8 r3 9000000000000000130
cmp r3 1
je e28_fact_requested
load8 r3 9000000000000000129
cmp r3 r12
jne e28_scan_next
label e28_fact_requested
cmp r13 1
je e28_fact_conflict_kind
cmp r12 1
je e28_kind1
jmp e28_kind2
label e28_kind1
load8 r8 9000000000000000400
load8 r0 9000000000000000401
mul r0 256
add r8 r0
cmp r8 512
jne e28_duplicate_compare
mov r0 r4
mod r0 256
store8 9000000000000000400 r0
mov r0 r4
div r0 256
store8 9000000000000000401 r0
store8 9000000000000000422 r14
store8 9000000000000000423 r10
jmp e28_scan_next
label e28_kind2
load8 r8 9000000000000000402
load8 r0 9000000000000000403
mul r0 256
add r8 r0
cmp r8 512
jne e28_duplicate_compare
mov r0 r4
mod r0 256
store8 9000000000000000402 r0
mov r0 r4
div r0 256
store8 9000000000000000403 r0
store8 9000000000000000426 r14
store8 9000000000000000427 r10
jmp e28_scan_next
label e28_duplicate_compare
cmp r12 1
je e28_duplicate_kind1
load8 r9 9000000000000000426
load8 r6 9000000000000000427
jmp e28_duplicate_kind_selected
label e28_duplicate_kind1
load8 r9 9000000000000000422
load8 r6 9000000000000000423
label e28_duplicate_kind_selected
cmp r6 r10
jne e28_fact_conflict_kind
mov r7 r8
mul r7 4
add r7 8900000000000001024
load8 r0 $r7
add r7 1
load8 r3 $r7
mul r3 256
add r0 r3
add r7 1
load8 r3 $r7
mul r3 65536
add r0 r3
add r0 r9
add r5 r14
set r11 0
label e28_duplicate_value_loop
cmp r11 r10
jge e28_scan_next
set r7 8900000000000100000
add r7 r0
add r7 r11
load8 r3 $r7
cmp r3 65
jlt e28_duplicate_prev_fold
cmp r3 90
jgt e28_duplicate_prev_fold
add r3 32
label e28_duplicate_prev_fold
set r7 8900000000000100000
add r7 r5
add r7 r11
load8 r9 $r7
cmp r9 65
jlt e28_duplicate_cur_fold
cmp r9 90
jgt e28_duplicate_cur_fold
add r9 32
label e28_duplicate_cur_fold
cmp r3 r9
jne e28_fact_conflict_kind
add r11 1
jmp e28_duplicate_value_loop
label e28_fact_conflict_kind
cmp r12 1
jne e28_fact_conflict2
store8 9000000000000000404 1
jmp e28_scan_next
label e28_fact_conflict2
store8 9000000000000000405 1
jmp e28_scan_next
label e28_scan_next
load8 r4 9000000000000000408
load8 r3 9000000000000000409
mul r3 256
add r4 r3
add r4 1
mov r3 r4
mod r3 256
store8 9000000000000000408 r3
div r4 256
store8 9000000000000000409 r4
jmp e28_scan_loop
label e28_scan_done
load8 r12 9000000000000000129
load8 r13 9000000000000000130
cmp r13 1
je e28_check_double
cmp r12 1
je e28_check_kind1
jmp e28_check_kind2
label e28_check_double
load8 r3 9000000000000000404
cmp r3 1
je e28_conflict
load8 r3 9000000000000000405
cmp r3 1
je e28_conflict
load8 r3 9000000000000000401
cmp r3 2
je e28_missing
load8 r3 9000000000000000403
cmp r3 2
je e28_missing
jmp e28_save_focus
label e28_check_kind1
load8 r3 9000000000000000404
cmp r3 1
je e28_conflict
load8 r3 9000000000000000401
cmp r3 2
je e28_missing_atomic
jmp e28_save_focus
label e28_check_kind2
load8 r3 9000000000000000405
cmp r3 1
je e28_conflict
load8 r3 9000000000000000403
cmp r3 2
je e28_missing_atomic
jmp e28_save_focus
label e28_save_focus
load8 r5 9000000000000000128
store8 9000000000000000032 r5
set r0 0
label e28_focus_copy
cmp r0 r5
jge e28_emit_init
set r7 9000000000000000256
add r7 r0
load8 r3 $r7
set r7 9000000000000000064
add r7 r0
store8 $r7 r3
add r0 1
jmp e28_focus_copy
label e28_emit_init
load8 r11 9000000000000000129
load8 r12 9000000000000000130
cmp r12 1
jne e28_emit_atomic
set r11 1
store8 9000000000000000132 1
jmp e28_emit_fact
label e28_emit_atomic
store8 9000000000000000132 3
label e28_emit_fact
store8 9000000000000000133 r11
load8 r5 9000000000000000128
set r0 0
label e28_emit_entity
cmp r0 r5
jge e28_emit_predicate
set r7 9000000000000000256
add r7 r0
load8 r14 $r7
print r14
add r0 1
jmp e28_emit_entity
label e28_emit_predicate
load8 r11 9000000000000000133
load8 r13 9000000000000000131
cmp r13 2
je e28_emit_pred_en
cmp r11 1
je e28_emit_es_is
set r14 32
print r14
set r14 114
print r14
set r14 101
print r14
set r14 113
print r14
set r14 117
print r14
set r14 105
print r14
set r14 101
print r14
set r14 114
print r14
set r14 101
print r14
set r14 32
print r14
jmp e28_emit_value_init
label e28_emit_es_is
set r14 32
print r14
set r14 101
print r14
set r14 115
print r14
set r14 32
print r14
jmp e28_emit_value_init
label e28_emit_pred_en
cmp r11 1
je e28_emit_en_is
set r14 32
print r14
set r14 110
print r14
set r14 101
print r14
set r14 101
print r14
set r14 100
print r14
set r14 115
print r14
set r14 32
print r14
jmp e28_emit_value_init
label e28_emit_en_is
set r14 32
print r14
set r14 105
print r14
set r14 115
print r14
set r14 32
print r14
label e28_emit_value_init
load8 r11 9000000000000000133
cmp r11 1
jne e28_emit_value_kind2
load8 r4 9000000000000000400
load8 r0 9000000000000000401
mul r0 256
add r4 r0
load8 r6 9000000000000000422
load8 r5 9000000000000000423
jmp e28_emit_value_pointer
label e28_emit_value_kind2
load8 r4 9000000000000000402
load8 r0 9000000000000000403
mul r0 256
add r4 r0
load8 r6 9000000000000000426
load8 r5 9000000000000000427
label e28_emit_value_pointer
mov r7 r4
mul r7 4
add r7 8900000000000001024
load8 r9 $r7
add r7 1
load8 r0 $r7
mul r0 256
add r9 r0
add r7 1
load8 r0 $r7
mul r0 65536
add r9 r0
add r9 r6
set r0 0
label e28_emit_value_bytes
cmp r0 r5
jge e28_emit_citation
set r7 8900000000000100000
add r7 r9
add r7 r0
load8 r14 $r7
print r14
add r0 1
jmp e28_emit_value_bytes
label e28_emit_citation
set r14 32
print r14
set r14 91
print r14
set r14 35
print r14
mov r0 r4
mov r8 r0
div r8 100
add r8 48
mov r14 r8
print r14
mod r0 100
mov r8 r0
div r8 10
add r8 48
mov r14 r8
print r14
mod r0 10
mov r8 r0
add r8 48
mov r14 r8
print r14
set r14 93
print r14
set r14 46
print r14
load8 r0 9000000000000000132
cmp r0 1
jne e28_end
store8 9000000000000000132 2
set r14 32
print r14
set r11 2
jmp e28_emit_fact
label e28_missing
set r14 70
print r14
set r14 97
print r14
set r14 108
print r14
set r14 116
print r14
set r14 97
print r14
set r14 32
print r14
set r14 101
print r14
set r14 118
print r14
set r14 105
print r14
set r14 100
print r14
set r14 101
print r14
set r14 110
print r14
set r14 99
print r14
set r14 105
print r14
set r14 97
print r14
set r14 32
print r14
set r14 112
print r14
set r14 97
print r14
set r14 114
print r14
set r14 97
print r14
set r14 32
print r14
set r14 99
print r14
set r14 111
print r14
set r14 109
print r14
set r14 98
print r14
set r14 105
print r14
set r14 110
print r14
set r14 97
print r14
set r14 114
print r14
set r14 32
print r14
set r14 97
print r14
set r14 109
print r14
set r14 98
print r14
set r14 97
print r14
set r14 115
print r14
set r14 32
print r14
set r14 112
print r14
set r14 114
print r14
set r14 111
print r14
set r14 112
print r14
set r14 105
print r14
set r14 101
print r14
set r14 100
print r14
set r14 97
print r14
set r14 100
print r14
set r14 101
print r14
set r14 115
print r14
set r14 46
print r14
store8 9000000000000000032 0
jmp e28_end
label e28_conflict
set r14 69
print r14
set r14 118
print r14
set r14 105
print r14
set r14 100
print r14
set r14 101
print r14
set r14 110
print r14
set r14 99
print r14
set r14 105
print r14
set r14 97
print r14
set r14 32
print r14
set r14 110
print r14
set r14 101
print r14
set r14 103
print r14
set r14 97
print r14
set r14 116
print r14
set r14 105
print r14
set r14 118
print r14
set r14 97
print r14
set r14 32
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
set r14 116
print r14
set r14 114
print r14
set r14 97
print r14
set r14 100
print r14
set r14 105
print r14
set r14 99
print r14
set r14 116
print r14
set r14 111
print r14
set r14 114
print r14
set r14 105
print r14
set r14 97
print r14
set r14 59
print r14
set r14 32
print r14
set r14 110
print r14
set r14 111
print r14
set r14 32
print r14
set r14 112
print r14
set r14 117
print r14
set r14 101
print r14
set r14 100
print r14
set r14 111
print r14
set r14 32
print r14
set r14 97
print r14
set r14 102
print r14
set r14 105
print r14
set r14 114
print r14
set r14 109
print r14
set r14 97
print r14
set r14 114
print r14
set r14 32
print r14
set r14 101
print r14
set r14 115
print r14
set r14 97
print r14
set r14 32
print r14
set r14 112
print r14
set r14 114
print r14
set r14 111
print r14
set r14 112
print r14
set r14 105
print r14
set r14 101
print r14
set r14 100
print r14
set r14 97
print r14
set r14 100
print r14
set r14 46
print r14
store8 9000000000000000032 0
jmp e28_end
label e28_ambiguous
set r14 78
print r14
set r14 111
print r14
set r14 32
print r14
set r14 112
print r14
set r14 117
print r14
set r14 101
print r14
set r14 100
print r14
set r14 111
print r14
set r14 32
print r14
set r14 105
print r14
set r14 110
print r14
set r14 116
print r14
set r14 101
print r14
set r14 114
print r14
set r14 112
print r14
set r14 114
print r14
set r14 101
print r14
set r14 116
print r14
set r14 97
print r14
set r14 114
print r14
set r14 32
print r14
set r14 101
print r14
set r14 115
print r14
set r14 97
print r14
set r14 32
print r14
set r14 112
print r14
set r14 114
print r14
set r14 101
print r14
set r14 103
print r14
set r14 117
print r14
set r14 110
print r14
set r14 116
print r14
set r14 97
print r14
set r14 32
print r14
set r14 99
print r14
set r14 111
print r14
set r14 110
print r14
set r14 32
print r14
set r14 115
print r14
set r14 101
print r14
set r14 103
print r14
set r14 117
print r14
set r14 114
print r14
set r14 105
print r14
set r14 100
print r14
set r14 97
print r14
set r14 100
print r14
set r14 46
print r14
store8 9000000000000000032 0
jmp e28_end
label e28_need_subject
set r14 78
print r14
set r14 101
print r14
set r14 99
print r14
set r14 101
print r14
set r14 115
print r14
set r14 105
print r14
set r14 116
print r14
set r14 111
print r14
set r14 32
print r14
set r14 117
print r14
set r14 110
print r14
set r14 97
print r14
set r14 32
print r14
set r14 101
print r14
set r14 110
print r14
set r14 116
print r14
set r14 105
print r14
set r14 100
print r14
set r14 97
print r14
set r14 100
print r14
set r14 32
print r14
set r14 111
print r14
set r14 32
print r14
set r14 114
print r14
set r14 101
print r14
set r14 102
print r14
set r14 101
print r14
set r14 114
print r14
set r14 101
print r14
set r14 110
print r14
set r14 99
print r14
set r14 105
print r14
set r14 97
print r14
set r14 32
print r14
set r14 97
print r14
set r14 110
print r14
set r14 116
print r14
set r14 101
print r14
set r14 114
print r14
set r14 105
print r14
set r14 111
print r14
set r14 114
print r14
set r14 46
print r14
store8 9000000000000000032 0
jmp e28_end
label e28_missing_atomic
store8 9000000000000000032 0
jmp e28_delegate
label e28_end
load8 r9 7400000000000000017
set r0 0
label e28_cleanup_input
cmp r0 r9
jge e28_cleanup_query
set r7 7400000000000000128
add r7 r0
store8 $r7 0
add r0 1
jmp e28_cleanup_input
label e28_cleanup_query
set r0 0
label e28_cleanup_query_loop
cmp r0 48
jge e28_cleanup_controls
set r7 9000000000000000256
add r7 r0
store8 $r7 0
add r0 1
jmp e28_cleanup_query_loop
label e28_cleanup_controls
set r0 128
label e28_cleanup_flags
cmp r0 136
jge e28_cleanup_results
set r7 9000000000000000000
add r7 r0
store8 $r7 0
add r0 1
jmp e28_cleanup_flags
label e28_cleanup_results
set r0 400
label e28_cleanup_results_loop
cmp r0 428
jge e28_cleanup_done
set r7 9000000000000000000
add r7 r0
store8 $r7 0
add r0 1
jmp e28_cleanup_results_loop
label e28_cleanup_done
store8 7400000000000000017 0
store8 7400000000000000016 0
halt
