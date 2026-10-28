#!reverse-pc-machine-v1
store8 8800000000000000000 0
label c26_form_0
set r7 7400000000000000128
load8 r3 $r7
cmp r3 113
jne c26_form_1
set r7 7400000000000000129
load8 r3 $r7
cmp r3 117
jne c26_form_1
set r7 7400000000000000130
load8 r3 $r7
cmp r3 101
jne c26_form_1
set r7 7400000000000000131
load8 r3 $r7
cmp r3 32
jne c26_form_1
set r7 7400000000000000132
load8 r3 $r7
cmp r3 101
jne c26_form_1
set r7 7400000000000000133
load8 r3 $r7
cmp r3 115
jne c26_form_1
set r7 7400000000000000134
load8 r3 $r7
cmp r3 32
jne c26_form_1
set r4 7
set r5 0
label c26_0_subject
mov r7 r4
add r7 r5
add r7 7400000000000000128
load8 r3 $r7
cmp r3 32
je c26_0_tail
cmp r3 97
jlt c26_form_1
cmp r3 122
jgt c26_form_1
add r5 1
cmp r5 32
jge c26_form_1
jmp c26_0_subject
label c26_0_tail
cmp r5 0
je c26_form_1
mov r7 r4
add r7 r5
add r7 128
add r7 7400000000000000000
load8 r3 $r7
cmp r3 32
jne c26_form_1
mov r7 r4
add r7 r5
add r7 129
add r7 7400000000000000000
load8 r3 $r7
cmp r3 121
jne c26_form_1
mov r7 r4
add r7 r5
add r7 130
add r7 7400000000000000000
load8 r3 $r7
cmp r3 32
jne c26_form_1
mov r7 r4
add r7 r5
add r7 131
add r7 7400000000000000000
load8 r3 $r7
cmp r3 113
jne c26_form_1
mov r7 r4
add r7 r5
add r7 132
add r7 7400000000000000000
load8 r3 $r7
cmp r3 117
jne c26_form_1
mov r7 r4
add r7 r5
add r7 133
add r7 7400000000000000000
load8 r3 $r7
cmp r3 101
jne c26_form_1
mov r7 r4
add r7 r5
add r7 134
add r7 7400000000000000000
load8 r3 $r7
cmp r3 32
jne c26_form_1
mov r7 r4
add r7 r5
add r7 135
add r7 7400000000000000000
load8 r3 $r7
cmp r3 114
jne c26_form_1
mov r7 r4
add r7 r5
add r7 136
add r7 7400000000000000000
load8 r3 $r7
cmp r3 101
jne c26_form_1
mov r7 r4
add r7 r5
add r7 137
add r7 7400000000000000000
load8 r3 $r7
cmp r3 113
jne c26_form_1
mov r7 r4
add r7 r5
add r7 138
add r7 7400000000000000000
load8 r3 $r7
cmp r3 117
jne c26_form_1
mov r7 r4
add r7 r5
add r7 139
add r7 7400000000000000000
load8 r3 $r7
cmp r3 105
jne c26_form_1
mov r7 r4
add r7 r5
add r7 140
add r7 7400000000000000000
load8 r3 $r7
cmp r3 101
jne c26_form_1
mov r7 r4
add r7 r5
add r7 141
add r7 7400000000000000000
load8 r3 $r7
cmp r3 114
jne c26_form_1
mov r7 r4
add r7 r5
add r7 142
add r7 7400000000000000000
load8 r3 $r7
cmp r3 101
jne c26_form_1
load8 r6 7400000000000000017
mov r7 r4
add r7 r5
add r7 15
cmp r6 r7
je c26_0_valid
add r7 1
cmp r6 r7
jne c26_form_1
sub r7 1
add r7 7400000000000000128
load8 r3 $r7
cmp r3 63
jne c26_form_1
label c26_0_valid
set r0 0
label c26_0_save
cmp r0 r5
jge c26_0_prepare
set r7 7400000000000000128
add r7 r4
add r7 r0
load8 r3 $r7
set r7 8800000000000000032
add r7 r0
store8 $r7 r3
add r0 1
jmp c26_0_save
label c26_0_prepare
load8 r6 7400000000000000017
set r0 0
label c26_0_clear_raw
cmp r0 r6
jge c26_0_raw_ready
set r7 7400000000000000128
add r7 r0
store8 $r7 0
add r0 1
jmp c26_0_clear_raw
label c26_0_raw_ready
store8 7400000000000000128 113
store8 7400000000000000129 117
store8 7400000000000000130 101
store8 7400000000000000131 32
store8 7400000000000000132 101
store8 7400000000000000133 115
store8 7400000000000000134 32
store8 8800000000000000128 113
store8 8800000000000000129 117
store8 8800000000000000130 101
store8 8800000000000000131 32
store8 8800000000000000132 114
store8 8800000000000000133 101
store8 8800000000000000134 113
store8 8800000000000000135 117
store8 8800000000000000136 105
store8 8800000000000000137 101
store8 8800000000000000138 114
store8 8800000000000000139 101
store8 8800000000000000140 32
set r0 0
label c26_0_copy
cmp r0 r5
jge c26_0_suffix
set r7 8800000000000000032
add r7 r0
load8 r3 $r7
set r7 7400000000000000135
add r7 r0
store8 $r7 r3
set r7 8800000000000000141
add r7 r0
store8 $r7 r3
add r0 1
jmp c26_0_copy
label c26_0_suffix
mov r6 r5
add r6 7
store8 7400000000000000017 r6
mov r6 r5
add r6 13
store8 8800000000000000002 r6
store8 8800000000000000000 1
jmp c26_base_entry
label c26_form_1
set r7 7400000000000000128
load8 r3 $r7
cmp r3 119
jne c26_form_2
set r7 7400000000000000129
load8 r3 $r7
cmp r3 104
jne c26_form_2
set r7 7400000000000000130
load8 r3 $r7
cmp r3 97
jne c26_form_2
set r7 7400000000000000131
load8 r3 $r7
cmp r3 116
jne c26_form_2
set r7 7400000000000000132
load8 r3 $r7
cmp r3 32
jne c26_form_2
set r7 7400000000000000133
load8 r3 $r7
cmp r3 105
jne c26_form_2
set r7 7400000000000000134
load8 r3 $r7
cmp r3 115
jne c26_form_2
set r7 7400000000000000135
load8 r3 $r7
cmp r3 32
jne c26_form_2
set r4 8
set r5 0
label c26_1_subject
mov r7 r4
add r7 r5
add r7 7400000000000000128
load8 r3 $r7
cmp r3 32
je c26_1_tail
cmp r3 97
jlt c26_form_2
cmp r3 122
jgt c26_form_2
add r5 1
cmp r5 32
jge c26_form_2
jmp c26_1_subject
label c26_1_tail
cmp r5 0
je c26_form_2
mov r7 r4
add r7 r5
add r7 128
add r7 7400000000000000000
load8 r3 $r7
cmp r3 32
jne c26_form_2
mov r7 r4
add r7 r5
add r7 129
add r7 7400000000000000000
load8 r3 $r7
cmp r3 97
jne c26_form_2
mov r7 r4
add r7 r5
add r7 130
add r7 7400000000000000000
load8 r3 $r7
cmp r3 110
jne c26_form_2
mov r7 r4
add r7 r5
add r7 131
add r7 7400000000000000000
load8 r3 $r7
cmp r3 100
jne c26_form_2
mov r7 r4
add r7 r5
add r7 132
add r7 7400000000000000000
load8 r3 $r7
cmp r3 32
jne c26_form_2
mov r7 r4
add r7 r5
add r7 133
add r7 7400000000000000000
load8 r3 $r7
cmp r3 119
jne c26_form_2
mov r7 r4
add r7 r5
add r7 134
add r7 7400000000000000000
load8 r3 $r7
cmp r3 104
jne c26_form_2
mov r7 r4
add r7 r5
add r7 135
add r7 7400000000000000000
load8 r3 $r7
cmp r3 97
jne c26_form_2
mov r7 r4
add r7 r5
add r7 136
add r7 7400000000000000000
load8 r3 $r7
cmp r3 116
jne c26_form_2
mov r7 r4
add r7 r5
add r7 137
add r7 7400000000000000000
load8 r3 $r7
cmp r3 32
jne c26_form_2
mov r7 r4
add r7 r5
add r7 138
add r7 7400000000000000000
load8 r3 $r7
cmp r3 100
jne c26_form_2
mov r7 r4
add r7 r5
add r7 139
add r7 7400000000000000000
load8 r3 $r7
cmp r3 111
jne c26_form_2
mov r7 r4
add r7 r5
add r7 140
add r7 7400000000000000000
load8 r3 $r7
cmp r3 101
jne c26_form_2
mov r7 r4
add r7 r5
add r7 141
add r7 7400000000000000000
load8 r3 $r7
cmp r3 115
jne c26_form_2
mov r7 r4
add r7 r5
add r7 142
add r7 7400000000000000000
load8 r3 $r7
cmp r3 32
jne c26_form_2
mov r7 r4
add r7 r5
add r7 143
add r7 7400000000000000000
load8 r3 $r7
cmp r3 105
jne c26_form_2
mov r7 r4
add r7 r5
add r7 144
add r7 7400000000000000000
load8 r3 $r7
cmp r3 116
jne c26_form_2
mov r7 r4
add r7 r5
add r7 145
add r7 7400000000000000000
load8 r3 $r7
cmp r3 32
jne c26_form_2
mov r7 r4
add r7 r5
add r7 146
add r7 7400000000000000000
load8 r3 $r7
cmp r3 114
jne c26_form_2
mov r7 r4
add r7 r5
add r7 147
add r7 7400000000000000000
load8 r3 $r7
cmp r3 101
jne c26_form_2
mov r7 r4
add r7 r5
add r7 148
add r7 7400000000000000000
load8 r3 $r7
cmp r3 113
jne c26_form_2
mov r7 r4
add r7 r5
add r7 149
add r7 7400000000000000000
load8 r3 $r7
cmp r3 117
jne c26_form_2
mov r7 r4
add r7 r5
add r7 150
add r7 7400000000000000000
load8 r3 $r7
cmp r3 105
jne c26_form_2
mov r7 r4
add r7 r5
add r7 151
add r7 7400000000000000000
load8 r3 $r7
cmp r3 114
jne c26_form_2
mov r7 r4
add r7 r5
add r7 152
add r7 7400000000000000000
load8 r3 $r7
cmp r3 101
jne c26_form_2
load8 r6 7400000000000000017
mov r7 r4
add r7 r5
add r7 25
cmp r6 r7
je c26_1_valid
add r7 1
cmp r6 r7
jne c26_form_2
sub r7 1
add r7 7400000000000000128
load8 r3 $r7
cmp r3 63
jne c26_form_2
label c26_1_valid
set r0 0
label c26_1_save
cmp r0 r5
jge c26_1_prepare
set r7 7400000000000000128
add r7 r4
add r7 r0
load8 r3 $r7
set r7 8800000000000000032
add r7 r0
store8 $r7 r3
add r0 1
jmp c26_1_save
label c26_1_prepare
load8 r6 7400000000000000017
set r0 0
label c26_1_clear_raw
cmp r0 r6
jge c26_1_raw_ready
set r7 7400000000000000128
add r7 r0
store8 $r7 0
add r0 1
jmp c26_1_clear_raw
label c26_1_raw_ready
store8 7400000000000000128 119
store8 7400000000000000129 104
store8 7400000000000000130 97
store8 7400000000000000131 116
store8 7400000000000000132 32
store8 7400000000000000133 105
store8 7400000000000000134 115
store8 7400000000000000135 32
store8 8800000000000000128 119
store8 8800000000000000129 104
store8 8800000000000000130 97
store8 8800000000000000131 116
store8 8800000000000000132 32
store8 8800000000000000133 100
store8 8800000000000000134 111
store8 8800000000000000135 101
store8 8800000000000000136 115
store8 8800000000000000137 32
set r0 0
label c26_1_copy
cmp r0 r5
jge c26_1_suffix
set r7 8800000000000000032
add r7 r0
load8 r3 $r7
set r7 7400000000000000136
add r7 r0
store8 $r7 r3
set r7 8800000000000000138
add r7 r0
store8 $r7 r3
add r0 1
jmp c26_1_copy
label c26_1_suffix
set r7 8800000000000000138
add r7 r5
store8 $r7 32
set r7 8800000000000000139
add r7 r5
store8 $r7 114
set r7 8800000000000000140
add r7 r5
store8 $r7 101
set r7 8800000000000000141
add r7 r5
store8 $r7 113
set r7 8800000000000000142
add r7 r5
store8 $r7 117
set r7 8800000000000000143
add r7 r5
store8 $r7 105
set r7 8800000000000000144
add r7 r5
store8 $r7 114
set r7 8800000000000000145
add r7 r5
store8 $r7 101
mov r6 r5
add r6 8
store8 7400000000000000017 r6
mov r6 r5
add r6 18
store8 8800000000000000002 r6
store8 8800000000000000000 1
jmp c26_base_entry
label c26_form_2
set r7 7400000000000000128
load8 r3 $r7
cmp r3 113
jne c26_form_3
set r7 7400000000000000129
load8 r3 $r7
cmp r3 117
jne c26_form_3
set r7 7400000000000000130
load8 r3 $r7
cmp r3 101
jne c26_form_3
set r7 7400000000000000131
load8 r3 $r7
cmp r3 32
jne c26_form_3
set r7 7400000000000000132
load8 r3 $r7
cmp r3 101
jne c26_form_3
set r7 7400000000000000133
load8 r3 $r7
cmp r3 115
jne c26_form_3
set r7 7400000000000000134
load8 r3 $r7
cmp r3 32
jne c26_form_3
set r4 7
set r5 0
label c26_2_subject
mov r7 r4
add r7 r5
add r7 7400000000000000128
load8 r3 $r7
cmp r3 32
je c26_2_tail
cmp r3 97
jlt c26_form_3
cmp r3 122
jgt c26_form_3
add r5 1
cmp r5 32
jge c26_form_3
jmp c26_2_subject
label c26_2_tail
cmp r5 0
je c26_form_3
mov r7 r4
add r7 r5
add r7 128
add r7 7400000000000000000
load8 r3 $r7
cmp r3 32
jne c26_form_3
mov r7 r4
add r7 r5
add r7 129
add r7 7400000000000000000
load8 r3 $r7
cmp r3 121
jne c26_form_3
mov r7 r4
add r7 r5
add r7 130
add r7 7400000000000000000
load8 r3 $r7
cmp r3 32
jne c26_form_3
mov r7 r4
add r7 r5
add r7 131
add r7 7400000000000000000
load8 r3 $r7
cmp r3 113
jne c26_form_3
mov r7 r4
add r7 r5
add r7 132
add r7 7400000000000000000
load8 r3 $r7
cmp r3 117
jne c26_form_3
mov r7 r4
add r7 r5
add r7 133
add r7 7400000000000000000
load8 r3 $r7
cmp r3 101
jne c26_form_3
mov r7 r4
add r7 r5
add r7 134
add r7 7400000000000000000
load8 r3 $r7
cmp r3 32
jne c26_form_3
mov r7 r4
add r7 r5
add r7 135
add r7 7400000000000000000
load8 r3 $r7
cmp r3 110
jne c26_form_3
mov r7 r4
add r7 r5
add r7 136
add r7 7400000000000000000
load8 r3 $r7
cmp r3 101
jne c26_form_3
mov r7 r4
add r7 r5
add r7 137
add r7 7400000000000000000
load8 r3 $r7
cmp r3 99
jne c26_form_3
mov r7 r4
add r7 r5
add r7 138
add r7 7400000000000000000
load8 r3 $r7
cmp r3 101
jne c26_form_3
mov r7 r4
add r7 r5
add r7 139
add r7 7400000000000000000
load8 r3 $r7
cmp r3 115
jne c26_form_3
mov r7 r4
add r7 r5
add r7 140
add r7 7400000000000000000
load8 r3 $r7
cmp r3 105
jne c26_form_3
mov r7 r4
add r7 r5
add r7 141
add r7 7400000000000000000
load8 r3 $r7
cmp r3 116
jne c26_form_3
mov r7 r4
add r7 r5
add r7 142
add r7 7400000000000000000
load8 r3 $r7
cmp r3 97
jne c26_form_3
load8 r6 7400000000000000017
mov r7 r4
add r7 r5
add r7 15
cmp r6 r7
je c26_2_valid
add r7 1
cmp r6 r7
jne c26_form_3
sub r7 1
add r7 7400000000000000128
load8 r3 $r7
cmp r3 63
jne c26_form_3
label c26_2_valid
set r0 0
label c26_2_save
cmp r0 r5
jge c26_2_prepare
set r7 7400000000000000128
add r7 r4
add r7 r0
load8 r3 $r7
set r7 8800000000000000032
add r7 r0
store8 $r7 r3
add r0 1
jmp c26_2_save
label c26_2_prepare
load8 r6 7400000000000000017
set r0 0
label c26_2_clear_raw
cmp r0 r6
jge c26_2_raw_ready
set r7 7400000000000000128
add r7 r0
store8 $r7 0
add r0 1
jmp c26_2_clear_raw
label c26_2_raw_ready
store8 7400000000000000128 113
store8 7400000000000000129 117
store8 7400000000000000130 101
store8 7400000000000000131 32
store8 7400000000000000132 101
store8 7400000000000000133 115
store8 7400000000000000134 32
store8 8800000000000000128 113
store8 8800000000000000129 117
store8 8800000000000000130 101
store8 8800000000000000131 32
store8 8800000000000000132 114
store8 8800000000000000133 101
store8 8800000000000000134 113
store8 8800000000000000135 117
store8 8800000000000000136 105
store8 8800000000000000137 101
store8 8800000000000000138 114
store8 8800000000000000139 101
store8 8800000000000000140 32
set r0 0
label c26_2_copy
cmp r0 r5
jge c26_2_suffix
set r7 8800000000000000032
add r7 r0
load8 r3 $r7
set r7 7400000000000000135
add r7 r0
store8 $r7 r3
set r7 8800000000000000141
add r7 r0
store8 $r7 r3
add r0 1
jmp c26_2_copy
label c26_2_suffix
mov r6 r5
add r6 7
store8 7400000000000000017 r6
mov r6 r5
add r6 13
store8 8800000000000000002 r6
store8 8800000000000000000 1
jmp c26_base_entry
label c26_form_3
set r7 7400000000000000128
load8 r3 $r7
cmp r3 119
jne c26_form_4
set r7 7400000000000000129
load8 r3 $r7
cmp r3 104
jne c26_form_4
set r7 7400000000000000130
load8 r3 $r7
cmp r3 97
jne c26_form_4
set r7 7400000000000000131
load8 r3 $r7
cmp r3 116
jne c26_form_4
set r7 7400000000000000132
load8 r3 $r7
cmp r3 32
jne c26_form_4
set r7 7400000000000000133
load8 r3 $r7
cmp r3 105
jne c26_form_4
set r7 7400000000000000134
load8 r3 $r7
cmp r3 115
jne c26_form_4
set r7 7400000000000000135
load8 r3 $r7
cmp r3 32
jne c26_form_4
set r4 8
set r5 0
label c26_3_subject
mov r7 r4
add r7 r5
add r7 7400000000000000128
load8 r3 $r7
cmp r3 32
je c26_3_tail
cmp r3 97
jlt c26_form_4
cmp r3 122
jgt c26_form_4
add r5 1
cmp r5 32
jge c26_form_4
jmp c26_3_subject
label c26_3_tail
cmp r5 0
je c26_form_4
mov r7 r4
add r7 r5
add r7 128
add r7 7400000000000000000
load8 r3 $r7
cmp r3 32
jne c26_form_4
mov r7 r4
add r7 r5
add r7 129
add r7 7400000000000000000
load8 r3 $r7
cmp r3 97
jne c26_form_4
mov r7 r4
add r7 r5
add r7 130
add r7 7400000000000000000
load8 r3 $r7
cmp r3 110
jne c26_form_4
mov r7 r4
add r7 r5
add r7 131
add r7 7400000000000000000
load8 r3 $r7
cmp r3 100
jne c26_form_4
mov r7 r4
add r7 r5
add r7 132
add r7 7400000000000000000
load8 r3 $r7
cmp r3 32
jne c26_form_4
mov r7 r4
add r7 r5
add r7 133
add r7 7400000000000000000
load8 r3 $r7
cmp r3 119
jne c26_form_4
mov r7 r4
add r7 r5
add r7 134
add r7 7400000000000000000
load8 r3 $r7
cmp r3 104
jne c26_form_4
mov r7 r4
add r7 r5
add r7 135
add r7 7400000000000000000
load8 r3 $r7
cmp r3 97
jne c26_form_4
mov r7 r4
add r7 r5
add r7 136
add r7 7400000000000000000
load8 r3 $r7
cmp r3 116
jne c26_form_4
mov r7 r4
add r7 r5
add r7 137
add r7 7400000000000000000
load8 r3 $r7
cmp r3 32
jne c26_form_4
mov r7 r4
add r7 r5
add r7 138
add r7 7400000000000000000
load8 r3 $r7
cmp r3 100
jne c26_form_4
mov r7 r4
add r7 r5
add r7 139
add r7 7400000000000000000
load8 r3 $r7
cmp r3 111
jne c26_form_4
mov r7 r4
add r7 r5
add r7 140
add r7 7400000000000000000
load8 r3 $r7
cmp r3 101
jne c26_form_4
mov r7 r4
add r7 r5
add r7 141
add r7 7400000000000000000
load8 r3 $r7
cmp r3 115
jne c26_form_4
mov r7 r4
add r7 r5
add r7 142
add r7 7400000000000000000
load8 r3 $r7
cmp r3 32
jne c26_form_4
mov r7 r4
add r7 r5
add r7 143
add r7 7400000000000000000
load8 r3 $r7
cmp r3 105
jne c26_form_4
mov r7 r4
add r7 r5
add r7 144
add r7 7400000000000000000
load8 r3 $r7
cmp r3 116
jne c26_form_4
mov r7 r4
add r7 r5
add r7 145
add r7 7400000000000000000
load8 r3 $r7
cmp r3 32
jne c26_form_4
mov r7 r4
add r7 r5
add r7 146
add r7 7400000000000000000
load8 r3 $r7
cmp r3 110
jne c26_form_4
mov r7 r4
add r7 r5
add r7 147
add r7 7400000000000000000
load8 r3 $r7
cmp r3 101
jne c26_form_4
mov r7 r4
add r7 r5
add r7 148
add r7 7400000000000000000
load8 r3 $r7
cmp r3 101
jne c26_form_4
mov r7 r4
add r7 r5
add r7 149
add r7 7400000000000000000
load8 r3 $r7
cmp r3 100
jne c26_form_4
load8 r6 7400000000000000017
mov r7 r4
add r7 r5
add r7 22
cmp r6 r7
je c26_3_valid
add r7 1
cmp r6 r7
jne c26_form_4
sub r7 1
add r7 7400000000000000128
load8 r3 $r7
cmp r3 63
jne c26_form_4
label c26_3_valid
set r0 0
label c26_3_save
cmp r0 r5
jge c26_3_prepare
set r7 7400000000000000128
add r7 r4
add r7 r0
load8 r3 $r7
set r7 8800000000000000032
add r7 r0
store8 $r7 r3
add r0 1
jmp c26_3_save
label c26_3_prepare
load8 r6 7400000000000000017
set r0 0
label c26_3_clear_raw
cmp r0 r6
jge c26_3_raw_ready
set r7 7400000000000000128
add r7 r0
store8 $r7 0
add r0 1
jmp c26_3_clear_raw
label c26_3_raw_ready
store8 7400000000000000128 119
store8 7400000000000000129 104
store8 7400000000000000130 97
store8 7400000000000000131 116
store8 7400000000000000132 32
store8 7400000000000000133 105
store8 7400000000000000134 115
store8 7400000000000000135 32
store8 8800000000000000128 119
store8 8800000000000000129 104
store8 8800000000000000130 97
store8 8800000000000000131 116
store8 8800000000000000132 32
store8 8800000000000000133 100
store8 8800000000000000134 111
store8 8800000000000000135 101
store8 8800000000000000136 115
store8 8800000000000000137 32
set r0 0
label c26_3_copy
cmp r0 r5
jge c26_3_suffix
set r7 8800000000000000032
add r7 r0
load8 r3 $r7
set r7 7400000000000000136
add r7 r0
store8 $r7 r3
set r7 8800000000000000138
add r7 r0
store8 $r7 r3
add r0 1
jmp c26_3_copy
label c26_3_suffix
set r7 8800000000000000138
add r7 r5
store8 $r7 32
set r7 8800000000000000139
add r7 r5
store8 $r7 114
set r7 8800000000000000140
add r7 r5
store8 $r7 101
set r7 8800000000000000141
add r7 r5
store8 $r7 113
set r7 8800000000000000142
add r7 r5
store8 $r7 117
set r7 8800000000000000143
add r7 r5
store8 $r7 105
set r7 8800000000000000144
add r7 r5
store8 $r7 114
set r7 8800000000000000145
add r7 r5
store8 $r7 101
mov r6 r5
add r6 8
store8 7400000000000000017 r6
mov r6 r5
add r6 18
store8 8800000000000000002 r6
store8 8800000000000000000 1
jmp c26_base_entry
label c26_form_4
jmp c26_base_entry
