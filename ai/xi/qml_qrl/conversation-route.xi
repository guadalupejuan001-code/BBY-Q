#!reverse-pc-machine-v1
# C08: parser XI, sin aprendizaje implicito.
# Acciones: 1 estado, 2 entrenar XOR, 3 XNOR, 4 evaluar, 5 clasificar, 6 entrenar QRL, 7 planificar, 8 ayuda, 254 entrada invalida.
store8 8180000000000000000 0
store8 8180000000000000001 255
store8 8180000000000000002 255
store8 8180000000000000003 0
load8 r0 9190000000000000008
set r4 0
set r5 0
set r10 0
cmp r0 14
jlt prefix_next_0
mov r7 r4
add r7 0
add r7 9190000000000004096
load8 r2 $r7
cmp r2 98
je prefix_match_0_0
cmp r2 66
jne prefix_next_0
label prefix_match_0_0
mov r7 r4
add r7 1
add r7 9190000000000004096
load8 r2 $r7
cmp r2 98
je prefix_match_0_1
cmp r2 66
jne prefix_next_0
label prefix_match_0_1
mov r7 r4
add r7 2
add r7 9190000000000004096
load8 r2 $r7
cmp r2 121
je prefix_match_0_2
cmp r2 89
jne prefix_next_0
label prefix_match_0_2
mov r7 r4
add r7 3
add r7 9190000000000004096
load8 r2 $r7
cmp r2 32
jne prefix_next_0
mov r7 r4
add r7 4
add r7 9190000000000004096
load8 r2 $r7
cmp r2 113
je prefix_match_0_4
cmp r2 81
jne prefix_next_0
label prefix_match_0_4
mov r7 r4
add r7 5
add r7 9190000000000004096
load8 r2 $r7
cmp r2 32
jne prefix_next_0
mov r7 r4
add r7 6
add r7 9190000000000004096
load8 r2 $r7
cmp r2 113
je prefix_match_0_6
cmp r2 81
jne prefix_next_0
label prefix_match_0_6
mov r7 r4
add r7 7
add r7 9190000000000004096
load8 r2 $r7
cmp r2 117
je prefix_match_0_7
cmp r2 85
jne prefix_next_0
label prefix_match_0_7
mov r7 r4
add r7 8
add r7 9190000000000004096
load8 r2 $r7
cmp r2 97
je prefix_match_0_8
cmp r2 65
jne prefix_next_0
label prefix_match_0_8
mov r7 r4
add r7 9
add r7 9190000000000004096
load8 r2 $r7
cmp r2 110
je prefix_match_0_9
cmp r2 78
jne prefix_next_0
label prefix_match_0_9
mov r7 r4
add r7 10
add r7 9190000000000004096
load8 r2 $r7
cmp r2 116
je prefix_match_0_10
cmp r2 84
jne prefix_next_0
label prefix_match_0_10
mov r7 r4
add r7 11
add r7 9190000000000004096
load8 r2 $r7
cmp r2 117
je prefix_match_0_11
cmp r2 85
jne prefix_next_0
label prefix_match_0_11
mov r7 r4
add r7 12
add r7 9190000000000004096
load8 r2 $r7
cmp r2 109
je prefix_match_0_12
cmp r2 77
jne prefix_next_0
label prefix_match_0_12
mov r7 r4
add r7 13
add r7 9190000000000004096
load8 r2 $r7
cmp r2 32
jne prefix_next_0
set r4 14
set r5 1
jmp prefixed_done
label prefix_next_0
cmp r0 8
jlt prefix_next_1
mov r7 r4
add r7 0
add r7 9190000000000004096
load8 r2 $r7
cmp r2 113
je prefix_match_1_0
cmp r2 81
jne prefix_next_1
label prefix_match_1_0
mov r7 r4
add r7 1
add r7 9190000000000004096
load8 r2 $r7
cmp r2 117
je prefix_match_1_1
cmp r2 85
jne prefix_next_1
label prefix_match_1_1
mov r7 r4
add r7 2
add r7 9190000000000004096
load8 r2 $r7
cmp r2 97
je prefix_match_1_2
cmp r2 65
jne prefix_next_1
label prefix_match_1_2
mov r7 r4
add r7 3
add r7 9190000000000004096
load8 r2 $r7
cmp r2 110
je prefix_match_1_3
cmp r2 78
jne prefix_next_1
label prefix_match_1_3
mov r7 r4
add r7 4
add r7 9190000000000004096
load8 r2 $r7
cmp r2 116
je prefix_match_1_4
cmp r2 84
jne prefix_next_1
label prefix_match_1_4
mov r7 r4
add r7 5
add r7 9190000000000004096
load8 r2 $r7
cmp r2 117
je prefix_match_1_5
cmp r2 85
jne prefix_next_1
label prefix_match_1_5
mov r7 r4
add r7 6
add r7 9190000000000004096
load8 r2 $r7
cmp r2 109
je prefix_match_1_6
cmp r2 77
jne prefix_next_1
label prefix_match_1_6
mov r7 r4
add r7 7
add r7 9190000000000004096
load8 r2 $r7
cmp r2 32
jne prefix_next_1
set r4 8
set r5 1
jmp prefixed_done
label prefix_next_1
cmp r0 9
jlt prefix_next_2
mov r7 r4
add r7 0
add r7 9190000000000004096
load8 r2 $r7
cmp r2 99
je prefix_match_2_0
cmp r2 67
jne prefix_next_2
label prefix_match_2_0
mov r7 r4
add r7 1
add r7 9190000000000004096
load8 r2 $r7
cmp r2 117
je prefix_match_2_1
cmp r2 85
jne prefix_next_2
label prefix_match_2_1
mov r7 r4
add r7 2
add r7 9190000000000004096
load8 r2 $r7
cmp r2 97
je prefix_match_2_2
cmp r2 65
jne prefix_next_2
label prefix_match_2_2
mov r7 r4
add r7 3
add r7 9190000000000004096
load8 r2 $r7
cmp r2 110
je prefix_match_2_3
cmp r2 78
jne prefix_next_2
label prefix_match_2_3
mov r7 r4
add r7 4
add r7 9190000000000004096
load8 r2 $r7
cmp r2 116
je prefix_match_2_4
cmp r2 84
jne prefix_next_2
label prefix_match_2_4
mov r7 r4
add r7 5
add r7 9190000000000004096
load8 r2 $r7
cmp r2 105
je prefix_match_2_5
cmp r2 73
jne prefix_next_2
label prefix_match_2_5
mov r7 r4
add r7 6
add r7 9190000000000004096
load8 r2 $r7
cmp r2 99
je prefix_match_2_6
cmp r2 67
jne prefix_next_2
label prefix_match_2_6
mov r7 r4
add r7 7
add r7 9190000000000004096
load8 r2 $r7
cmp r2 111
je prefix_match_2_7
cmp r2 79
jne prefix_next_2
label prefix_match_2_7
mov r7 r4
add r7 8
add r7 9190000000000004096
load8 r2 $r7
cmp r2 32
jne prefix_next_2
set r4 9
set r5 1
jmp prefixed_done
label prefix_next_2
cmp r0 10
jlt prefix_next_3
mov r7 r4
add r7 0
add r7 9190000000000004096
load8 r2 $r7
cmp r2 99
je prefix_match_3_0
cmp r2 67
jne prefix_next_3
label prefix_match_3_0
mov r7 r4
add r7 1
add r7 9190000000000004096
load8 r2 $r7
cmp r2 117
je prefix_match_3_1
cmp r2 85
jne prefix_next_3
label prefix_match_3_1
mov r7 r4
add r7 2
add r7 9190000000000004096
load8 r2 $r7
cmp r2 195
jne prefix_next_3
mov r7 r4
add r7 3
add r7 9190000000000004096
load8 r2 $r7
cmp r2 161
jne prefix_next_3
mov r7 r4
add r7 4
add r7 9190000000000004096
load8 r2 $r7
cmp r2 110
je prefix_match_3_4
cmp r2 78
jne prefix_next_3
label prefix_match_3_4
mov r7 r4
add r7 5
add r7 9190000000000004096
load8 r2 $r7
cmp r2 116
je prefix_match_3_5
cmp r2 84
jne prefix_next_3
label prefix_match_3_5
mov r7 r4
add r7 6
add r7 9190000000000004096
load8 r2 $r7
cmp r2 105
je prefix_match_3_6
cmp r2 73
jne prefix_next_3
label prefix_match_3_6
mov r7 r4
add r7 7
add r7 9190000000000004096
load8 r2 $r7
cmp r2 99
je prefix_match_3_7
cmp r2 67
jne prefix_next_3
label prefix_match_3_7
mov r7 r4
add r7 8
add r7 9190000000000004096
load8 r2 $r7
cmp r2 111
je prefix_match_3_8
cmp r2 79
jne prefix_next_3
label prefix_match_3_8
mov r7 r4
add r7 9
add r7 9190000000000004096
load8 r2 $r7
cmp r2 32
jne prefix_next_3
set r4 10
set r5 1
jmp prefixed_done
label prefix_next_3
label prefixed_done
load8 r1 9190000000000000009
cmp r1 0
jne unsupported
load8 r1 9190000000000000010
cmp r1 0
jne unsupported
load8 r1 9190000000000000011
cmp r1 0
jne unsupported
load8 r1 9190000000000000012
cmp r1 r0
jne unsupported
load8 r1 9190000000000000013
cmp r1 0
jne unsupported
load8 r1 9190000000000000014
cmp r1 0
jne unsupported
load8 r1 9190000000000000015
cmp r1 0
jne unsupported
mov r6 r0
sub r6 r4
cmp r6 6
jne pattern_next_0
mov r7 r4
add r7 0
add r7 9190000000000004096
load8 r2 $r7
cmp r2 101
je exact_0_0
cmp r2 69
jne pattern_next_0
label exact_0_0
mov r7 r4
add r7 1
add r7 9190000000000004096
load8 r2 $r7
cmp r2 115
je exact_0_1
cmp r2 83
jne pattern_next_0
label exact_0_1
mov r7 r4
add r7 2
add r7 9190000000000004096
load8 r2 $r7
cmp r2 116
je exact_0_2
cmp r2 84
jne pattern_next_0
label exact_0_2
mov r7 r4
add r7 3
add r7 9190000000000004096
load8 r2 $r7
cmp r2 97
je exact_0_3
cmp r2 65
jne pattern_next_0
label exact_0_3
mov r7 r4
add r7 4
add r7 9190000000000004096
load8 r2 $r7
cmp r2 100
je exact_0_4
cmp r2 68
jne pattern_next_0
label exact_0_4
mov r7 r4
add r7 5
add r7 9190000000000004096
load8 r2 $r7
cmp r2 111
je exact_0_5
cmp r2 79
jne pattern_next_0
label exact_0_5
set r10 1
jmp result
label pattern_next_0
cmp r6 6
jne pattern_next_1
mov r7 r4
add r7 0
add r7 9190000000000004096
load8 r2 $r7
cmp r2 115
je exact_1_0
cmp r2 83
jne pattern_next_1
label exact_1_0
mov r7 r4
add r7 1
add r7 9190000000000004096
load8 r2 $r7
cmp r2 116
je exact_1_1
cmp r2 84
jne pattern_next_1
label exact_1_1
mov r7 r4
add r7 2
add r7 9190000000000004096
load8 r2 $r7
cmp r2 97
je exact_1_2
cmp r2 65
jne pattern_next_1
label exact_1_2
mov r7 r4
add r7 3
add r7 9190000000000004096
load8 r2 $r7
cmp r2 116
je exact_1_3
cmp r2 84
jne pattern_next_1
label exact_1_3
mov r7 r4
add r7 4
add r7 9190000000000004096
load8 r2 $r7
cmp r2 117
je exact_1_4
cmp r2 85
jne pattern_next_1
label exact_1_4
mov r7 r4
add r7 5
add r7 9190000000000004096
load8 r2 $r7
cmp r2 115
je exact_1_5
cmp r2 83
jne pattern_next_1
label exact_1_5
set r10 1
jmp result
label pattern_next_1
cmp r6 5
jne pattern_next_2
mov r7 r4
add r7 0
add r7 9190000000000004096
load8 r2 $r7
cmp r2 97
je exact_2_0
cmp r2 65
jne pattern_next_2
label exact_2_0
mov r7 r4
add r7 1
add r7 9190000000000004096
load8 r2 $r7
cmp r2 121
je exact_2_1
cmp r2 89
jne pattern_next_2
label exact_2_1
mov r7 r4
add r7 2
add r7 9190000000000004096
load8 r2 $r7
cmp r2 117
je exact_2_2
cmp r2 85
jne pattern_next_2
label exact_2_2
mov r7 r4
add r7 3
add r7 9190000000000004096
load8 r2 $r7
cmp r2 100
je exact_2_3
cmp r2 68
jne pattern_next_2
label exact_2_3
mov r7 r4
add r7 4
add r7 9190000000000004096
load8 r2 $r7
cmp r2 97
je exact_2_4
cmp r2 65
jne pattern_next_2
label exact_2_4
set r10 8
jmp result
label pattern_next_2
cmp r6 4
jne pattern_next_3
mov r7 r4
add r7 0
add r7 9190000000000004096
load8 r2 $r7
cmp r2 104
je exact_3_0
cmp r2 72
jne pattern_next_3
label exact_3_0
mov r7 r4
add r7 1
add r7 9190000000000004096
load8 r2 $r7
cmp r2 101
je exact_3_1
cmp r2 69
jne pattern_next_3
label exact_3_1
mov r7 r4
add r7 2
add r7 9190000000000004096
load8 r2 $r7
cmp r2 108
je exact_3_2
cmp r2 76
jne pattern_next_3
label exact_3_2
mov r7 r4
add r7 3
add r7 9190000000000004096
load8 r2 $r7
cmp r2 112
je exact_3_3
cmp r2 80
jne pattern_next_3
label exact_3_3
set r10 8
jmp result
label pattern_next_3
cmp r6 11
jne pattern_next_4
mov r7 r4
add r7 0
add r7 9190000000000004096
load8 r2 $r7
cmp r2 101
je exact_4_0
cmp r2 69
jne pattern_next_4
label exact_4_0
mov r7 r4
add r7 1
add r7 9190000000000004096
load8 r2 $r7
cmp r2 110
je exact_4_1
cmp r2 78
jne pattern_next_4
label exact_4_1
mov r7 r4
add r7 2
add r7 9190000000000004096
load8 r2 $r7
cmp r2 116
je exact_4_2
cmp r2 84
jne pattern_next_4
label exact_4_2
mov r7 r4
add r7 3
add r7 9190000000000004096
load8 r2 $r7
cmp r2 114
je exact_4_3
cmp r2 82
jne pattern_next_4
label exact_4_3
mov r7 r4
add r7 4
add r7 9190000000000004096
load8 r2 $r7
cmp r2 101
je exact_4_4
cmp r2 69
jne pattern_next_4
label exact_4_4
mov r7 r4
add r7 5
add r7 9190000000000004096
load8 r2 $r7
cmp r2 110
je exact_4_5
cmp r2 78
jne pattern_next_4
label exact_4_5
mov r7 r4
add r7 6
add r7 9190000000000004096
load8 r2 $r7
cmp r2 97
je exact_4_6
cmp r2 65
jne pattern_next_4
label exact_4_6
mov r7 r4
add r7 7
add r7 9190000000000004096
load8 r2 $r7
cmp r2 32
jne pattern_next_4
mov r7 r4
add r7 8
add r7 9190000000000004096
load8 r2 $r7
cmp r2 120
je exact_4_8
cmp r2 88
jne pattern_next_4
label exact_4_8
mov r7 r4
add r7 9
add r7 9190000000000004096
load8 r2 $r7
cmp r2 111
je exact_4_9
cmp r2 79
jne pattern_next_4
label exact_4_9
mov r7 r4
add r7 10
add r7 9190000000000004096
load8 r2 $r7
cmp r2 114
je exact_4_10
cmp r2 82
jne pattern_next_4
label exact_4_10
set r10 2
jmp result
label pattern_next_4
cmp r6 9
jne pattern_next_5
mov r7 r4
add r7 0
add r7 9190000000000004096
load8 r2 $r7
cmp r2 116
je exact_5_0
cmp r2 84
jne pattern_next_5
label exact_5_0
mov r7 r4
add r7 1
add r7 9190000000000004096
load8 r2 $r7
cmp r2 114
je exact_5_1
cmp r2 82
jne pattern_next_5
label exact_5_1
mov r7 r4
add r7 2
add r7 9190000000000004096
load8 r2 $r7
cmp r2 97
je exact_5_2
cmp r2 65
jne pattern_next_5
label exact_5_2
mov r7 r4
add r7 3
add r7 9190000000000004096
load8 r2 $r7
cmp r2 105
je exact_5_3
cmp r2 73
jne pattern_next_5
label exact_5_3
mov r7 r4
add r7 4
add r7 9190000000000004096
load8 r2 $r7
cmp r2 110
je exact_5_4
cmp r2 78
jne pattern_next_5
label exact_5_4
mov r7 r4
add r7 5
add r7 9190000000000004096
load8 r2 $r7
cmp r2 32
jne pattern_next_5
mov r7 r4
add r7 6
add r7 9190000000000004096
load8 r2 $r7
cmp r2 120
je exact_5_6
cmp r2 88
jne pattern_next_5
label exact_5_6
mov r7 r4
add r7 7
add r7 9190000000000004096
load8 r2 $r7
cmp r2 111
je exact_5_7
cmp r2 79
jne pattern_next_5
label exact_5_7
mov r7 r4
add r7 8
add r7 9190000000000004096
load8 r2 $r7
cmp r2 114
je exact_5_8
cmp r2 82
jne pattern_next_5
label exact_5_8
set r10 2
jmp result
label pattern_next_5
cmp r6 12
jne pattern_next_6
mov r7 r4
add r7 0
add r7 9190000000000004096
load8 r2 $r7
cmp r2 101
je exact_6_0
cmp r2 69
jne pattern_next_6
label exact_6_0
mov r7 r4
add r7 1
add r7 9190000000000004096
load8 r2 $r7
cmp r2 110
je exact_6_1
cmp r2 78
jne pattern_next_6
label exact_6_1
mov r7 r4
add r7 2
add r7 9190000000000004096
load8 r2 $r7
cmp r2 116
je exact_6_2
cmp r2 84
jne pattern_next_6
label exact_6_2
mov r7 r4
add r7 3
add r7 9190000000000004096
load8 r2 $r7
cmp r2 114
je exact_6_3
cmp r2 82
jne pattern_next_6
label exact_6_3
mov r7 r4
add r7 4
add r7 9190000000000004096
load8 r2 $r7
cmp r2 101
je exact_6_4
cmp r2 69
jne pattern_next_6
label exact_6_4
mov r7 r4
add r7 5
add r7 9190000000000004096
load8 r2 $r7
cmp r2 110
je exact_6_5
cmp r2 78
jne pattern_next_6
label exact_6_5
mov r7 r4
add r7 6
add r7 9190000000000004096
load8 r2 $r7
cmp r2 97
je exact_6_6
cmp r2 65
jne pattern_next_6
label exact_6_6
mov r7 r4
add r7 7
add r7 9190000000000004096
load8 r2 $r7
cmp r2 32
jne pattern_next_6
mov r7 r4
add r7 8
add r7 9190000000000004096
load8 r2 $r7
cmp r2 120
je exact_6_8
cmp r2 88
jne pattern_next_6
label exact_6_8
mov r7 r4
add r7 9
add r7 9190000000000004096
load8 r2 $r7
cmp r2 110
je exact_6_9
cmp r2 78
jne pattern_next_6
label exact_6_9
mov r7 r4
add r7 10
add r7 9190000000000004096
load8 r2 $r7
cmp r2 111
je exact_6_10
cmp r2 79
jne pattern_next_6
label exact_6_10
mov r7 r4
add r7 11
add r7 9190000000000004096
load8 r2 $r7
cmp r2 114
je exact_6_11
cmp r2 82
jne pattern_next_6
label exact_6_11
set r10 3
jmp result
label pattern_next_6
cmp r6 10
jne pattern_next_7
mov r7 r4
add r7 0
add r7 9190000000000004096
load8 r2 $r7
cmp r2 116
je exact_7_0
cmp r2 84
jne pattern_next_7
label exact_7_0
mov r7 r4
add r7 1
add r7 9190000000000004096
load8 r2 $r7
cmp r2 114
je exact_7_1
cmp r2 82
jne pattern_next_7
label exact_7_1
mov r7 r4
add r7 2
add r7 9190000000000004096
load8 r2 $r7
cmp r2 97
je exact_7_2
cmp r2 65
jne pattern_next_7
label exact_7_2
mov r7 r4
add r7 3
add r7 9190000000000004096
load8 r2 $r7
cmp r2 105
je exact_7_3
cmp r2 73
jne pattern_next_7
label exact_7_3
mov r7 r4
add r7 4
add r7 9190000000000004096
load8 r2 $r7
cmp r2 110
je exact_7_4
cmp r2 78
jne pattern_next_7
label exact_7_4
mov r7 r4
add r7 5
add r7 9190000000000004096
load8 r2 $r7
cmp r2 32
jne pattern_next_7
mov r7 r4
add r7 6
add r7 9190000000000004096
load8 r2 $r7
cmp r2 120
je exact_7_6
cmp r2 88
jne pattern_next_7
label exact_7_6
mov r7 r4
add r7 7
add r7 9190000000000004096
load8 r2 $r7
cmp r2 110
je exact_7_7
cmp r2 78
jne pattern_next_7
label exact_7_7
mov r7 r4
add r7 8
add r7 9190000000000004096
load8 r2 $r7
cmp r2 111
je exact_7_8
cmp r2 79
jne pattern_next_7
label exact_7_8
mov r7 r4
add r7 9
add r7 9190000000000004096
load8 r2 $r7
cmp r2 114
je exact_7_9
cmp r2 82
jne pattern_next_7
label exact_7_9
set r10 3
jmp result
label pattern_next_7
cmp r6 6
jne pattern_next_8
mov r7 r4
add r7 0
add r7 9190000000000004096
load8 r2 $r7
cmp r2 101
je exact_8_0
cmp r2 69
jne pattern_next_8
label exact_8_0
mov r7 r4
add r7 1
add r7 9190000000000004096
load8 r2 $r7
cmp r2 118
je exact_8_1
cmp r2 86
jne pattern_next_8
label exact_8_1
mov r7 r4
add r7 2
add r7 9190000000000004096
load8 r2 $r7
cmp r2 97
je exact_8_2
cmp r2 65
jne pattern_next_8
label exact_8_2
mov r7 r4
add r7 3
add r7 9190000000000004096
load8 r2 $r7
cmp r2 108
je exact_8_3
cmp r2 76
jne pattern_next_8
label exact_8_3
mov r7 r4
add r7 4
add r7 9190000000000004096
load8 r2 $r7
cmp r2 117
je exact_8_4
cmp r2 85
jne pattern_next_8
label exact_8_4
mov r7 r4
add r7 5
add r7 9190000000000004096
load8 r2 $r7
cmp r2 97
je exact_8_5
cmp r2 65
jne pattern_next_8
label exact_8_5
set r10 4
jmp result
label pattern_next_8
cmp r6 7
jne pattern_next_9
mov r7 r4
add r7 0
add r7 9190000000000004096
load8 r2 $r7
cmp r2 101
je exact_9_0
cmp r2 69
jne pattern_next_9
label exact_9_0
mov r7 r4
add r7 1
add r7 9190000000000004096
load8 r2 $r7
cmp r2 118
je exact_9_1
cmp r2 86
jne pattern_next_9
label exact_9_1
mov r7 r4
add r7 2
add r7 9190000000000004096
load8 r2 $r7
cmp r2 97
je exact_9_2
cmp r2 65
jne pattern_next_9
label exact_9_2
mov r7 r4
add r7 3
add r7 9190000000000004096
load8 r2 $r7
cmp r2 108
je exact_9_3
cmp r2 76
jne pattern_next_9
label exact_9_3
mov r7 r4
add r7 4
add r7 9190000000000004096
load8 r2 $r7
cmp r2 195
jne pattern_next_9
mov r7 r4
add r7 5
add r7 9190000000000004096
load8 r2 $r7
cmp r2 186
jne pattern_next_9
mov r7 r4
add r7 6
add r7 9190000000000004096
load8 r2 $r7
cmp r2 97
je exact_9_6
cmp r2 65
jne pattern_next_9
label exact_9_6
set r10 4
jmp result
label pattern_next_9
cmp r6 4
jne pattern_next_10
mov r7 r4
add r7 0
add r7 9190000000000004096
load8 r2 $r7
cmp r2 101
je exact_10_0
cmp r2 69
jne pattern_next_10
label exact_10_0
mov r7 r4
add r7 1
add r7 9190000000000004096
load8 r2 $r7
cmp r2 118
je exact_10_1
cmp r2 86
jne pattern_next_10
label exact_10_1
mov r7 r4
add r7 2
add r7 9190000000000004096
load8 r2 $r7
cmp r2 97
je exact_10_2
cmp r2 65
jne pattern_next_10
label exact_10_2
mov r7 r4
add r7 3
add r7 9190000000000004096
load8 r2 $r7
cmp r2 108
je exact_10_3
cmp r2 76
jne pattern_next_10
label exact_10_3
set r10 4
jmp result
label pattern_next_10
cmp r6 8
jne pattern_next_11
mov r7 r4
add r7 0
add r7 9190000000000004096
load8 r2 $r7
cmp r2 101
je exact_11_0
cmp r2 69
jne pattern_next_11
label exact_11_0
mov r7 r4
add r7 1
add r7 9190000000000004096
load8 r2 $r7
cmp r2 118
je exact_11_1
cmp r2 86
jne pattern_next_11
label exact_11_1
mov r7 r4
add r7 2
add r7 9190000000000004096
load8 r2 $r7
cmp r2 97
je exact_11_2
cmp r2 65
jne pattern_next_11
label exact_11_2
mov r7 r4
add r7 3
add r7 9190000000000004096
load8 r2 $r7
cmp r2 108
je exact_11_3
cmp r2 76
jne pattern_next_11
label exact_11_3
mov r7 r4
add r7 4
add r7 9190000000000004096
load8 r2 $r7
cmp r2 117
je exact_11_4
cmp r2 85
jne pattern_next_11
label exact_11_4
mov r7 r4
add r7 5
add r7 9190000000000004096
load8 r2 $r7
cmp r2 97
je exact_11_5
cmp r2 65
jne pattern_next_11
label exact_11_5
mov r7 r4
add r7 6
add r7 9190000000000004096
load8 r2 $r7
cmp r2 116
je exact_11_6
cmp r2 84
jne pattern_next_11
label exact_11_6
mov r7 r4
add r7 7
add r7 9190000000000004096
load8 r2 $r7
cmp r2 101
je exact_11_7
cmp r2 69
jne pattern_next_11
label exact_11_7
set r10 4
jmp result
label pattern_next_11
cmp r6 14
jne pattern_next_12
mov r7 r4
add r7 0
add r7 9190000000000004096
load8 r2 $r7
cmp r2 101
je exact_12_0
cmp r2 69
jne pattern_next_12
label exact_12_0
mov r7 r4
add r7 1
add r7 9190000000000004096
load8 r2 $r7
cmp r2 110
je exact_12_1
cmp r2 78
jne pattern_next_12
label exact_12_1
mov r7 r4
add r7 2
add r7 9190000000000004096
load8 r2 $r7
cmp r2 116
je exact_12_2
cmp r2 84
jne pattern_next_12
label exact_12_2
mov r7 r4
add r7 3
add r7 9190000000000004096
load8 r2 $r7
cmp r2 114
je exact_12_3
cmp r2 82
jne pattern_next_12
label exact_12_3
mov r7 r4
add r7 4
add r7 9190000000000004096
load8 r2 $r7
cmp r2 101
je exact_12_4
cmp r2 69
jne pattern_next_12
label exact_12_4
mov r7 r4
add r7 5
add r7 9190000000000004096
load8 r2 $r7
cmp r2 110
je exact_12_5
cmp r2 78
jne pattern_next_12
label exact_12_5
mov r7 r4
add r7 6
add r7 9190000000000004096
load8 r2 $r7
cmp r2 97
je exact_12_6
cmp r2 65
jne pattern_next_12
label exact_12_6
mov r7 r4
add r7 7
add r7 9190000000000004096
load8 r2 $r7
cmp r2 32
jne pattern_next_12
mov r7 r4
add r7 8
add r7 9190000000000004096
load8 r2 $r7
cmp r2 97
je exact_12_8
cmp r2 65
jne pattern_next_12
label exact_12_8
mov r7 r4
add r7 9
add r7 9190000000000004096
load8 r2 $r7
cmp r2 103
je exact_12_9
cmp r2 71
jne pattern_next_12
label exact_12_9
mov r7 r4
add r7 10
add r7 9190000000000004096
load8 r2 $r7
cmp r2 101
je exact_12_10
cmp r2 69
jne pattern_next_12
label exact_12_10
mov r7 r4
add r7 11
add r7 9190000000000004096
load8 r2 $r7
cmp r2 110
je exact_12_11
cmp r2 78
jne pattern_next_12
label exact_12_11
mov r7 r4
add r7 12
add r7 9190000000000004096
load8 r2 $r7
cmp r2 116
je exact_12_12
cmp r2 84
jne pattern_next_12
label exact_12_12
mov r7 r4
add r7 13
add r7 9190000000000004096
load8 r2 $r7
cmp r2 101
je exact_12_13
cmp r2 69
jne pattern_next_12
label exact_12_13
set r10 6
jmp result
label pattern_next_12
cmp r6 11
jne pattern_next_13
mov r7 r4
add r7 0
add r7 9190000000000004096
load8 r2 $r7
cmp r2 101
je exact_13_0
cmp r2 69
jne pattern_next_13
label exact_13_0
mov r7 r4
add r7 1
add r7 9190000000000004096
load8 r2 $r7
cmp r2 110
je exact_13_1
cmp r2 78
jne pattern_next_13
label exact_13_1
mov r7 r4
add r7 2
add r7 9190000000000004096
load8 r2 $r7
cmp r2 116
je exact_13_2
cmp r2 84
jne pattern_next_13
label exact_13_2
mov r7 r4
add r7 3
add r7 9190000000000004096
load8 r2 $r7
cmp r2 114
je exact_13_3
cmp r2 82
jne pattern_next_13
label exact_13_3
mov r7 r4
add r7 4
add r7 9190000000000004096
load8 r2 $r7
cmp r2 101
je exact_13_4
cmp r2 69
jne pattern_next_13
label exact_13_4
mov r7 r4
add r7 5
add r7 9190000000000004096
load8 r2 $r7
cmp r2 110
je exact_13_5
cmp r2 78
jne pattern_next_13
label exact_13_5
mov r7 r4
add r7 6
add r7 9190000000000004096
load8 r2 $r7
cmp r2 97
je exact_13_6
cmp r2 65
jne pattern_next_13
label exact_13_6
mov r7 r4
add r7 7
add r7 9190000000000004096
load8 r2 $r7
cmp r2 32
jne pattern_next_13
mov r7 r4
add r7 8
add r7 9190000000000004096
load8 r2 $r7
cmp r2 113
je exact_13_8
cmp r2 81
jne pattern_next_13
label exact_13_8
mov r7 r4
add r7 9
add r7 9190000000000004096
load8 r2 $r7
cmp r2 114
je exact_13_9
cmp r2 82
jne pattern_next_13
label exact_13_9
mov r7 r4
add r7 10
add r7 9190000000000004096
load8 r2 $r7
cmp r2 108
je exact_13_10
cmp r2 76
jne pattern_next_13
label exact_13_10
set r10 6
jmp result
label pattern_next_13
cmp r6 11
jne pattern_next_14
mov r7 r4
add r7 0
add r7 9190000000000004096
load8 r2 $r7
cmp r2 116
je exact_14_0
cmp r2 84
jne pattern_next_14
label exact_14_0
mov r7 r4
add r7 1
add r7 9190000000000004096
load8 r2 $r7
cmp r2 114
je exact_14_1
cmp r2 82
jne pattern_next_14
label exact_14_1
mov r7 r4
add r7 2
add r7 9190000000000004096
load8 r2 $r7
cmp r2 97
je exact_14_2
cmp r2 65
jne pattern_next_14
label exact_14_2
mov r7 r4
add r7 3
add r7 9190000000000004096
load8 r2 $r7
cmp r2 105
je exact_14_3
cmp r2 73
jne pattern_next_14
label exact_14_3
mov r7 r4
add r7 4
add r7 9190000000000004096
load8 r2 $r7
cmp r2 110
je exact_14_4
cmp r2 78
jne pattern_next_14
label exact_14_4
mov r7 r4
add r7 5
add r7 9190000000000004096
load8 r2 $r7
cmp r2 32
jne pattern_next_14
mov r7 r4
add r7 6
add r7 9190000000000004096
load8 r2 $r7
cmp r2 97
je exact_14_6
cmp r2 65
jne pattern_next_14
label exact_14_6
mov r7 r4
add r7 7
add r7 9190000000000004096
load8 r2 $r7
cmp r2 103
je exact_14_7
cmp r2 71
jne pattern_next_14
label exact_14_7
mov r7 r4
add r7 8
add r7 9190000000000004096
load8 r2 $r7
cmp r2 101
je exact_14_8
cmp r2 69
jne pattern_next_14
label exact_14_8
mov r7 r4
add r7 9
add r7 9190000000000004096
load8 r2 $r7
cmp r2 110
je exact_14_9
cmp r2 78
jne pattern_next_14
label exact_14_9
mov r7 r4
add r7 10
add r7 9190000000000004096
load8 r2 $r7
cmp r2 116
je exact_14_10
cmp r2 84
jne pattern_next_14
label exact_14_10
set r10 6
jmp result
label pattern_next_14
cmp r6 13
jne pattern_next_15
mov r7 r4
add r7 0
add r7 9190000000000004096
load8 r2 $r7
cmp r2 99
je parameter_15_0
cmp r2 67
jne pattern_next_15
label parameter_15_0
mov r7 r4
add r7 1
add r7 9190000000000004096
load8 r2 $r7
cmp r2 108
je parameter_15_1
cmp r2 76
jne pattern_next_15
label parameter_15_1
mov r7 r4
add r7 2
add r7 9190000000000004096
load8 r2 $r7
cmp r2 97
je parameter_15_2
cmp r2 65
jne pattern_next_15
label parameter_15_2
mov r7 r4
add r7 3
add r7 9190000000000004096
load8 r2 $r7
cmp r2 115
je parameter_15_3
cmp r2 83
jne pattern_next_15
label parameter_15_3
mov r7 r4
add r7 4
add r7 9190000000000004096
load8 r2 $r7
cmp r2 105
je parameter_15_4
cmp r2 73
jne pattern_next_15
label parameter_15_4
mov r7 r4
add r7 5
add r7 9190000000000004096
load8 r2 $r7
cmp r2 102
je parameter_15_5
cmp r2 70
jne pattern_next_15
label parameter_15_5
mov r7 r4
add r7 6
add r7 9190000000000004096
load8 r2 $r7
cmp r2 105
je parameter_15_6
cmp r2 73
jne pattern_next_15
label parameter_15_6
mov r7 r4
add r7 7
add r7 9190000000000004096
load8 r2 $r7
cmp r2 99
je parameter_15_7
cmp r2 67
jne pattern_next_15
label parameter_15_7
mov r7 r4
add r7 8
add r7 9190000000000004096
load8 r2 $r7
cmp r2 97
je parameter_15_8
cmp r2 65
jne pattern_next_15
label parameter_15_8
mov r7 r4
add r7 9
add r7 9190000000000004096
load8 r2 $r7
cmp r2 32
jne pattern_next_15
mov r7 r4
add r7 10
add r7 9190000000000004096
load8 r8 $r7
cmp r8 48
jlt invalid_args
cmp r8 49
jgt invalid_args
sub r8 48
add r7 1
load8 r2 $r7
cmp r2 32
jne invalid_args
add r7 1
load8 r9 $r7
cmp r9 48
jlt invalid_args
cmp r9 49
jgt invalid_args
sub r9 48
set r10 5
jmp result
label pattern_next_15
cmp r6 12
jne pattern_next_16
mov r7 r4
add r7 0
add r7 9190000000000004096
load8 r2 $r7
cmp r2 99
je parameter_16_0
cmp r2 67
jne pattern_next_16
label parameter_16_0
mov r7 r4
add r7 1
add r7 9190000000000004096
load8 r2 $r7
cmp r2 108
je parameter_16_1
cmp r2 76
jne pattern_next_16
label parameter_16_1
mov r7 r4
add r7 2
add r7 9190000000000004096
load8 r2 $r7
cmp r2 97
je parameter_16_2
cmp r2 65
jne pattern_next_16
label parameter_16_2
mov r7 r4
add r7 3
add r7 9190000000000004096
load8 r2 $r7
cmp r2 115
je parameter_16_3
cmp r2 83
jne pattern_next_16
label parameter_16_3
mov r7 r4
add r7 4
add r7 9190000000000004096
load8 r2 $r7
cmp r2 115
je parameter_16_4
cmp r2 83
jne pattern_next_16
label parameter_16_4
mov r7 r4
add r7 5
add r7 9190000000000004096
load8 r2 $r7
cmp r2 105
je parameter_16_5
cmp r2 73
jne pattern_next_16
label parameter_16_5
mov r7 r4
add r7 6
add r7 9190000000000004096
load8 r2 $r7
cmp r2 102
je parameter_16_6
cmp r2 70
jne pattern_next_16
label parameter_16_6
mov r7 r4
add r7 7
add r7 9190000000000004096
load8 r2 $r7
cmp r2 121
je parameter_16_7
cmp r2 89
jne pattern_next_16
label parameter_16_7
mov r7 r4
add r7 8
add r7 9190000000000004096
load8 r2 $r7
cmp r2 32
jne pattern_next_16
mov r7 r4
add r7 9
add r7 9190000000000004096
load8 r8 $r7
cmp r8 48
jlt invalid_args
cmp r8 49
jgt invalid_args
sub r8 48
add r7 1
load8 r2 $r7
cmp r2 32
jne invalid_args
add r7 1
load8 r9 $r7
cmp r9 48
jlt invalid_args
cmp r9 49
jgt invalid_args
sub r9 48
set r10 5
jmp result
label pattern_next_16
cmp r6 10
jne pattern_next_17
mov r7 r4
add r7 0
add r7 9190000000000004096
load8 r2 $r7
cmp r2 112
je parameter_17_0
cmp r2 80
jne pattern_next_17
label parameter_17_0
mov r7 r4
add r7 1
add r7 9190000000000004096
load8 r2 $r7
cmp r2 108
je parameter_17_1
cmp r2 76
jne pattern_next_17
label parameter_17_1
mov r7 r4
add r7 2
add r7 9190000000000004096
load8 r2 $r7
cmp r2 97
je parameter_17_2
cmp r2 65
jne pattern_next_17
label parameter_17_2
mov r7 r4
add r7 3
add r7 9190000000000004096
load8 r2 $r7
cmp r2 110
je parameter_17_3
cmp r2 78
jne pattern_next_17
label parameter_17_3
mov r7 r4
add r7 4
add r7 9190000000000004096
load8 r2 $r7
cmp r2 101
je parameter_17_4
cmp r2 69
jne pattern_next_17
label parameter_17_4
mov r7 r4
add r7 5
add r7 9190000000000004096
load8 r2 $r7
cmp r2 97
je parameter_17_5
cmp r2 65
jne pattern_next_17
label parameter_17_5
mov r7 r4
add r7 6
add r7 9190000000000004096
load8 r2 $r7
cmp r2 32
jne pattern_next_17
mov r7 r4
add r7 7
add r7 9190000000000004096
load8 r8 $r7
cmp r8 48
jlt invalid_args
cmp r8 49
jgt invalid_args
sub r8 48
add r7 1
load8 r2 $r7
cmp r2 32
jne invalid_args
add r7 1
load8 r9 $r7
cmp r9 48
jlt invalid_args
cmp r9 49
jgt invalid_args
sub r9 48
set r10 7
jmp result
label pattern_next_17
cmp r6 8
jne pattern_next_18
mov r7 r4
add r7 0
add r7 9190000000000004096
load8 r2 $r7
cmp r2 112
je parameter_18_0
cmp r2 80
jne pattern_next_18
label parameter_18_0
mov r7 r4
add r7 1
add r7 9190000000000004096
load8 r2 $r7
cmp r2 108
je parameter_18_1
cmp r2 76
jne pattern_next_18
label parameter_18_1
mov r7 r4
add r7 2
add r7 9190000000000004096
load8 r2 $r7
cmp r2 97
je parameter_18_2
cmp r2 65
jne pattern_next_18
label parameter_18_2
mov r7 r4
add r7 3
add r7 9190000000000004096
load8 r2 $r7
cmp r2 110
je parameter_18_3
cmp r2 78
jne pattern_next_18
label parameter_18_3
mov r7 r4
add r7 4
add r7 9190000000000004096
load8 r2 $r7
cmp r2 32
jne pattern_next_18
mov r7 r4
add r7 5
add r7 9190000000000004096
load8 r8 $r7
cmp r8 48
jlt invalid_args
cmp r8 49
jgt invalid_args
sub r8 48
add r7 1
load8 r2 $r7
cmp r2 32
jne invalid_args
add r7 1
load8 r9 $r7
cmp r9 48
jlt invalid_args
cmp r9 49
jgt invalid_args
sub r9 48
set r10 7
jmp result
label pattern_next_18
label unsupported
cmp r5 1
jne result
set r10 254
jmp result
label invalid_args
set r10 254
label result
store8 8180000000000000000 r10
store8 8180000000000000003 r5
cmp r10 5
je write_bits
cmp r10 7
jne end
label write_bits
store8 8180000000000000001 r8
store8 8180000000000000002 r9
label end
halt
