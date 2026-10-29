#!reverse-pc-machine-v1
# Generic temporal interpreter: all word order and verb spellings come from
# native learned frames. Facts are keyed by entity, object AND temporal bucket.
store8 8650000000000000608 0
load8 r0 8650000000000000000
cmp r0 1
jne te_delegate
load8 r9 7400000000000000017
set r10 0
label te_frame
cmp r10 64
jge te_selected
set r15 8650000000000004096
mov r0 r10
mul r0 256
add r15 r0
load8 r0 $r15
cmp r0 2
jne te_next
mov r7 r15
add r7 5
load8 r11 $r7
add r7 1
load8 r12 $r7
add r7 1
load8 r13 $r7
set r0 0
label te_prefix
cmp r0 r11
jge te_s_start
mov r7 r15
add r7 80
add r7 r0
load8 r3 $r7
set r7 7400000000000000128
add r7 r0
load8 r4 $r7
cmp r3 r4
jne te_next
add r0 1
jmp te_prefix
label te_s_start
mov r4 r11
set r5 0
label te_subject
cmp r4 r9
jge te_next
set r7 7400000000000000128
add r7 r4
load8 r3 $r7
cmp r3 48
jlt te_mid_start
cmp r3 57
jle te_s_char
cmp r3 97
jlt te_mid_start
cmp r3 122
jgt te_mid_start
label te_s_char
add r5 1
cmp r5 31
jgt te_next
add r4 1
jmp te_subject
label te_mid_start
cmp r5 0
je te_next
store8 8650000000000000600 r11
store8 8650000000000000601 r5
set r0 0
label te_middle
cmp r0 r12
jge te_o_start
mov r1 r4
add r1 r0
cmp r1 r9
jge te_next
mov r7 r15
add r7 112
add r7 r0
load8 r3 $r7
set r7 7400000000000000128
add r7 r4
add r7 r0
load8 r8 $r7
cmp r3 r8
jne te_next
add r0 1
jmp te_middle
label te_o_start
add r4 r12
store8 8650000000000000602 r4
set r6 0
label te_object
cmp r4 r9
jge te_suffix_start
set r7 7400000000000000128
add r7 r4
load8 r3 $r7
cmp r3 48
jlt te_suffix_start
cmp r3 57
jle te_o_char
cmp r3 97
jlt te_suffix_start
cmp r3 122
jgt te_suffix_start
label te_o_char
add r6 1
cmp r6 31
jgt te_next
add r4 1
jmp te_object
label te_suffix_start
cmp r6 0
je te_next
mov r0 r4
add r0 r13
cmp r0 r9
jne te_next
set r0 0
label te_suffix
cmp r0 r13
jge te_match
mov r7 r15
add r7 160
add r7 r0
load8 r3 $r7
set r7 7400000000000000128
add r7 r4
add r7 r0
load8 r8 $r7
cmp r3 r8
jne te_next
add r0 1
jmp te_suffix
label te_match
load8 r0 8650000000000000608
cmp r0 0
je te_remember
# Equal candidates must agree on both captures and all semantic labels.
load8 r0 8650000000000000609
cmp r0 r5
jne te_ambiguous
load8 r0 8650000000000000610
cmp r0 r6
jne te_ambiguous
set r0 0
label te_compare_labels
cmp r0 3
jge te_same_s_start
mov r7 r15
add r7 1
add r7 r0
load8 r3 $r7
set r7 8650000000000000604
add r7 r0
load8 r8 $r7
cmp r3 r8
jne te_ambiguous
add r0 1
jmp te_compare_labels
label te_same_s_start
set r0 0
label te_same_s
cmp r0 r5
jge te_same_o_start
set r7 7400000000000000128
add r7 r11
add r7 r0
load8 r3 $r7
set r7 8650000000000000768
add r7 r0
load8 r8 $r7
cmp r3 r8
jne te_ambiguous
add r0 1
jmp te_same_s
label te_same_o_start
set r0 0
label te_same_o
cmp r0 r6
jge te_next
load8 r7 8650000000000000602
add r7 7400000000000000128
add r7 r0
load8 r3 $r7
set r7 8650000000000000800
add r7 r0
load8 r8 $r7
cmp r3 r8
jne te_ambiguous
add r0 1
jmp te_same_o
label te_remember
store8 8650000000000000608 1
store8 8650000000000000609 r5
store8 8650000000000000610 r6
set r0 0
label te_remember_labels
cmp r0 3
jge te_copy_s_start
mov r7 r15
add r7 1
add r7 r0
load8 r3 $r7
set r7 8650000000000000604
add r7 r0
store8 $r7 r3
add r0 1
jmp te_remember_labels
label te_copy_s_start
set r0 0
label te_copy_s
cmp r0 r5
jge te_copy_o_start
set r7 7400000000000000128
add r7 r11
add r7 r0
load8 r3 $r7
set r7 8650000000000000768
add r7 r0
store8 $r7 r3
add r0 1
jmp te_copy_s
label te_copy_o_start
set r0 0
label te_copy_o
cmp r0 r6
jge te_next
load8 r7 8650000000000000602
add r7 7400000000000000128
add r7 r0
load8 r3 $r7
set r7 8650000000000000800
add r7 r0
store8 $r7 r3
add r0 1
jmp te_copy_o
label te_next
add r10 1
jmp te_frame
label te_selected
load8 r0 8650000000000000608
cmp r0 1
jne te_delegate
load8 r11 8650000000000000605
load8 r12 8650000000000000609
load8 r13 8650000000000000610
set r10 0
label te_fact
cmp r10 256
jge te_capacity
set r15 8650000000000065536
mov r0 r10
mul r0 80
add r15 r0
load8 r0 $r15
cmp r0 0
je te_not_found
mov r7 r15
add r7 1
load8 r0 $r7
cmp r0 r11
jne te_next_fact
add r7 2
load8 r0 $r7
cmp r0 r12
jne te_next_fact
add r7 1
load8 r0 $r7
cmp r0 r13
jne te_next_fact
set r0 0
label te_fact_s
cmp r0 r12
jge te_fact_o_start
mov r7 r15
add r7 8
add r7 r0
load8 r3 $r7
set r7 8650000000000000768
add r7 r0
load8 r4 $r7
cmp r3 r4
jne te_next_fact
add r0 1
jmp te_fact_s
label te_fact_o_start
set r0 0
label te_fact_o
cmp r0 r13
jge te_fact_found
mov r7 r15
add r7 40
add r7 r0
load8 r3 $r7
set r7 8650000000000000800
add r7 r0
load8 r4 $r7
cmp r3 r4
jne te_next_fact
add r0 1
jmp te_fact_o
label te_next_fact
add r10 1
jmp te_fact
label te_fact_found
load8 r0 8650000000000000604
cmp r0 2
je te_answer
mov r7 r15
add r7 2
load8 r3 $r7
load8 r4 8650000000000000606
cmp r3 3
je te_ack
cmp r3 r4
je te_ack
add r3 r4
store8 $r7 r3
jmp te_ack
label te_not_found
load8 r0 8650000000000000604
cmp r0 2
je te_unknown
store8 $r15 1
mov r7 r15
add r7 1
store8 $r7 r11
add r7 1
load8 r0 8650000000000000606
store8 $r7 r0
add r7 1
store8 $r7 r12
add r7 1
store8 $r7 r13
set r0 0
label te_save_fact_s
cmp r0 r12
jge te_save_fact_o_start
set r7 8650000000000000768
add r7 r0
load8 r3 $r7
mov r7 r15
add r7 8
add r7 r0
store8 $r7 r3
add r0 1
jmp te_save_fact_s
label te_save_fact_o_start
set r0 0
label te_save_fact_o
cmp r0 r13
jge te_ack
set r7 8650000000000000800
add r7 r0
load8 r3 $r7
mov r7 r15
add r7 40
add r7 r0
store8 $r7 r3
add r0 1
jmp te_save_fact_o
label te_capacity
load8 r0 8650000000000000604
cmp r0 2
je te_unknown
jmp te_emit_capacity
label te_answer
mov r7 r15
add r7 2
load8 r3 $r7
cmp r3 3
je te_conflict
cmp r11 3
je te_future_answer
cmp r3 2
je te_negative
jmp te_positive
label te_future_answer
cmp r3 2
je te_future_negative
jmp te_future_positive
label te_ack
cmp r11 1
je te_ack_past
cmp r11 2
je te_ack_present
jmp te_ack_future
label te_ambiguous
load8 r0 7400000000000000003
cmp r0 2
je te_ambiguous_en
set r14 73
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
set r14 99
print r14
set r14 105
print r14
set r14 195
print r14
set r14 179
print r14
set r14 110
print r14
set r14 32
print r14
set r14 116
print r14
set r14 101
print r14
set r14 109
print r14
set r14 112
print r14
set r14 111
print r14
set r14 114
print r14
set r14 97
print r14
set r14 108
print r14
set r14 32
print r14
set r14 97
print r14
set r14 109
print r14
set r14 98
print r14
set r14 105
print r14
set r14 103
print r14
set r14 117
print r14
set r14 97
print r14
set r14 46
print r14
jmp te_finish
label te_ambiguous_en
set r14 65
print r14
set r14 109
print r14
set r14 98
print r14
set r14 105
print r14
set r14 103
print r14
set r14 117
print r14
set r14 111
print r14
set r14 117
print r14
set r14 115
print r14
set r14 32
print r14
set r14 116
print r14
set r14 101
print r14
set r14 109
print r14
set r14 112
print r14
set r14 111
print r14
set r14 114
print r14
set r14 97
print r14
set r14 108
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
set r14 116
print r14
set r14 105
print r14
set r14 111
print r14
set r14 110
print r14
set r14 46
print r14
jmp te_finish
label te_unknown
load8 r0 7400000000000000003
cmp r0 2
je te_unknown_en
set r14 78
print r14
set r14 111
print r14
set r14 32
print r14
set r14 116
print r14
set r14 101
print r14
set r14 110
print r14
set r14 103
print r14
set r14 111
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
set r14 101
print r14
set r14 115
print r14
set r14 101
print r14
set r14 32
print r14
set r14 109
print r14
set r14 111
print r14
set r14 109
print r14
set r14 101
print r14
set r14 110
print r14
set r14 116
print r14
set r14 111
print r14
set r14 46
print r14
jmp te_finish
label te_unknown_en
set r14 73
print r14
set r14 32
print r14
set r14 104
print r14
set r14 97
print r14
set r14 118
print r14
set r14 101
print r14
set r14 32
print r14
set r14 110
print r14
set r14 111
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
set r14 101
print r14
set r14 32
print r14
set r14 102
print r14
set r14 111
print r14
set r14 114
print r14
set r14 32
print r14
set r14 116
print r14
set r14 104
print r14
set r14 97
print r14
set r14 116
print r14
set r14 32
print r14
set r14 116
print r14
set r14 105
print r14
set r14 109
print r14
set r14 101
print r14
set r14 46
print r14
jmp te_finish
label te_conflict
load8 r0 7400000000000000003
cmp r0 2
je te_conflict_en
set r14 72
print r14
set r14 97
print r14
set r14 121
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
set r14 99
print r14
set r14 105
print r14
set r14 111
print r14
set r14 110
print r14
set r14 101
print r14
set r14 115
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
set r14 115
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
set r14 101
print r14
set r14 115
print r14
set r14 101
print r14
set r14 32
print r14
set r14 109
print r14
set r14 111
print r14
set r14 109
print r14
set r14 101
print r14
set r14 110
print r14
set r14 116
print r14
set r14 111
print r14
set r14 46
print r14
jmp te_finish
label te_conflict_en
set r14 84
print r14
set r14 104
print r14
set r14 101
print r14
set r14 114
print r14
set r14 101
print r14
set r14 32
print r14
set r14 97
print r14
set r14 114
print r14
set r14 101
print r14
set r14 32
print r14
set r14 99
print r14
set r14 111
print r14
set r14 110
print r14
set r14 102
print r14
set r14 108
print r14
set r14 105
print r14
set r14 99
print r14
set r14 116
print r14
set r14 105
print r14
set r14 110
print r14
set r14 103
print r14
set r14 32
print r14
set r14 115
print r14
set r14 116
print r14
set r14 97
print r14
set r14 116
print r14
set r14 101
print r14
set r14 109
print r14
set r14 101
print r14
set r14 110
print r14
set r14 116
print r14
set r14 115
print r14
set r14 32
print r14
set r14 102
print r14
set r14 111
print r14
set r14 114
print r14
set r14 32
print r14
set r14 116
print r14
set r14 104
print r14
set r14 97
print r14
set r14 116
print r14
set r14 32
print r14
set r14 116
print r14
set r14 105
print r14
set r14 109
print r14
set r14 101
print r14
set r14 46
print r14
jmp te_finish
label te_emit_capacity
load8 r0 7400000000000000003
cmp r0 2
je te_emit_capacity_en
set r14 77
print r14
set r14 101
print r14
set r14 109
print r14
set r14 111
print r14
set r14 114
print r14
set r14 105
print r14
set r14 97
print r14
set r14 32
print r14
set r14 116
print r14
set r14 101
print r14
set r14 109
print r14
set r14 112
print r14
set r14 111
print r14
set r14 114
print r14
set r14 97
print r14
set r14 108
print r14
set r14 32
print r14
set r14 108
print r14
set r14 108
print r14
set r14 101
print r14
set r14 110
print r14
set r14 97
print r14
set r14 46
print r14
jmp te_finish
label te_emit_capacity_en
set r14 84
print r14
set r14 101
print r14
set r14 109
print r14
set r14 112
print r14
set r14 111
print r14
set r14 114
print r14
set r14 97
print r14
set r14 108
print r14
set r14 32
print r14
set r14 109
print r14
set r14 101
print r14
set r14 109
print r14
set r14 111
print r14
set r14 114
print r14
set r14 121
print r14
set r14 32
print r14
set r14 105
print r14
set r14 115
print r14
set r14 32
print r14
set r14 102
print r14
set r14 117
print r14
set r14 108
print r14
set r14 108
print r14
set r14 46
print r14
jmp te_finish
label te_ack_past
load8 r0 7400000000000000003
cmp r0 2
je te_ack_past_en
set r14 82
print r14
set r14 101
print r14
set r14 103
print r14
set r14 105
print r14
set r14 115
print r14
set r14 116
print r14
set r14 114
print r14
set r14 97
print r14
set r14 100
print r14
set r14 111
print r14
set r14 32
print r14
set r14 101
print r14
set r14 110
print r14
set r14 32
print r14
set r14 112
print r14
set r14 97
print r14
set r14 115
print r14
set r14 97
print r14
set r14 100
print r14
set r14 111
print r14
set r14 46
print r14
jmp te_finish
label te_ack_past_en
set r14 82
print r14
set r14 101
print r14
set r14 99
print r14
set r14 111
print r14
set r14 114
print r14
set r14 100
print r14
set r14 101
print r14
set r14 100
print r14
set r14 32
print r14
set r14 105
print r14
set r14 110
print r14
set r14 32
print r14
set r14 116
print r14
set r14 104
print r14
set r14 101
print r14
set r14 32
print r14
set r14 112
print r14
set r14 97
print r14
set r14 115
print r14
set r14 116
print r14
set r14 46
print r14
jmp te_finish
label te_ack_present
load8 r0 7400000000000000003
cmp r0 2
je te_ack_present_en
set r14 82
print r14
set r14 101
print r14
set r14 103
print r14
set r14 105
print r14
set r14 115
print r14
set r14 116
print r14
set r14 114
print r14
set r14 97
print r14
set r14 100
print r14
set r14 111
print r14
set r14 32
print r14
set r14 101
print r14
set r14 110
print r14
set r14 32
print r14
set r14 112
print r14
set r14 114
print r14
set r14 101
print r14
set r14 115
print r14
set r14 101
print r14
set r14 110
print r14
set r14 116
print r14
set r14 101
print r14
set r14 46
print r14
jmp te_finish
label te_ack_present_en
set r14 82
print r14
set r14 101
print r14
set r14 99
print r14
set r14 111
print r14
set r14 114
print r14
set r14 100
print r14
set r14 101
print r14
set r14 100
print r14
set r14 32
print r14
set r14 105
print r14
set r14 110
print r14
set r14 32
print r14
set r14 116
print r14
set r14 104
print r14
set r14 101
print r14
set r14 32
print r14
set r14 112
print r14
set r14 114
print r14
set r14 101
print r14
set r14 115
print r14
set r14 101
print r14
set r14 110
print r14
set r14 116
print r14
set r14 46
print r14
jmp te_finish
label te_ack_future
load8 r0 7400000000000000003
cmp r0 2
je te_ack_future_en
set r14 82
print r14
set r14 101
print r14
set r14 103
print r14
set r14 105
print r14
set r14 115
print r14
set r14 116
print r14
set r14 114
print r14
set r14 97
print r14
set r14 100
print r14
set r14 111
print r14
set r14 32
print r14
set r14 99
print r14
set r14 111
print r14
set r14 109
print r14
set r14 111
print r14
set r14 32
print r14
set r14 112
print r14
set r14 114
print r14
set r14 101
print r14
set r14 118
print r14
set r14 105
print r14
set r14 115
print r14
set r14 105
print r14
set r14 195
print r14
set r14 179
print r14
set r14 110
print r14
set r14 32
print r14
set r14 102
print r14
set r14 117
print r14
set r14 116
print r14
set r14 117
print r14
set r14 114
print r14
set r14 97
print r14
set r14 46
print r14
jmp te_finish
label te_ack_future_en
set r14 82
print r14
set r14 101
print r14
set r14 99
print r14
set r14 111
print r14
set r14 114
print r14
set r14 100
print r14
set r14 101
print r14
set r14 100
print r14
set r14 32
print r14
set r14 97
print r14
set r14 115
print r14
set r14 32
print r14
set r14 97
print r14
set r14 32
print r14
set r14 102
print r14
set r14 117
print r14
set r14 116
print r14
set r14 117
print r14
set r14 114
print r14
set r14 101
print r14
set r14 32
print r14
set r14 112
print r14
set r14 114
print r14
set r14 111
print r14
set r14 106
print r14
set r14 101
print r14
set r14 99
print r14
set r14 116
print r14
set r14 105
print r14
set r14 111
print r14
set r14 110
print r14
set r14 46
print r14
jmp te_finish
label te_future_positive
load8 r0 7400000000000000003
cmp r0 2
je te_future_positive_en
set r14 80
print r14
set r14 114
print r14
set r14 101
print r14
set r14 118
print r14
set r14 105
print r14
set r14 115
print r14
set r14 116
print r14
set r14 111
print r14
set r14 32
print r14
set r14 113
print r14
set r14 117
print r14
set r14 101
print r14
set r14 32
print r14
set r14 115
print r14
set r14 195
print r14
set r14 173
print r14
set r14 59
print r14
set r14 32
print r14
set r14 116
print r14
set r14 111
print r14
set r14 100
print r14
set r14 97
print r14
set r14 118
print r14
set r14 195
print r14
set r14 173
print r14
set r14 97
print r14
set r14 32
print r14
set r14 110
print r14
set r14 111
print r14
set r14 32
print r14
set r14 101
print r14
set r14 115
print r14
set r14 116
print r14
set r14 195
print r14
set r14 161
print r14
set r14 32
print r14
set r14 99
print r14
set r14 111
print r14
set r14 110
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
set r14 100
print r14
set r14 111
print r14
set r14 46
print r14
jmp te_finish
label te_future_positive_en
set r14 80
print r14
set r14 114
print r14
set r14 111
print r14
set r14 106
print r14
set r14 101
print r14
set r14 99
print r14
set r14 116
print r14
set r14 101
print r14
set r14 100
print r14
set r14 32
print r14
set r14 121
print r14
set r14 101
print r14
set r14 115
print r14
set r14 59
print r14
set r14 32
print r14
set r14 105
print r14
set r14 116
print r14
set r14 32
print r14
set r14 105
print r14
set r14 115
print r14
set r14 32
print r14
set r14 110
print r14
set r14 111
print r14
set r14 116
print r14
set r14 32
print r14
set r14 121
print r14
set r14 101
print r14
set r14 116
print r14
set r14 32
print r14
set r14 99
print r14
set r14 111
print r14
set r14 110
print r14
set r14 102
print r14
set r14 105
print r14
set r14 114
print r14
set r14 109
print r14
set r14 101
print r14
set r14 100
print r14
set r14 46
print r14
jmp te_finish
label te_future_negative
load8 r0 7400000000000000003
cmp r0 2
je te_future_negative_en
set r14 80
print r14
set r14 114
print r14
set r14 101
print r14
set r14 118
print r14
set r14 105
print r14
set r14 115
print r14
set r14 116
print r14
set r14 111
print r14
set r14 32
print r14
set r14 113
print r14
set r14 117
print r14
set r14 101
print r14
set r14 32
print r14
set r14 110
print r14
set r14 111
print r14
set r14 59
print r14
set r14 32
print r14
set r14 116
print r14
set r14 111
print r14
set r14 100
print r14
set r14 97
print r14
set r14 118
print r14
set r14 195
print r14
set r14 173
print r14
set r14 97
print r14
set r14 32
print r14
set r14 110
print r14
set r14 111
print r14
set r14 32
print r14
set r14 101
print r14
set r14 115
print r14
set r14 116
print r14
set r14 195
print r14
set r14 161
print r14
set r14 32
print r14
set r14 99
print r14
set r14 111
print r14
set r14 110
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
set r14 100
print r14
set r14 111
print r14
set r14 46
print r14
jmp te_finish
label te_future_negative_en
set r14 80
print r14
set r14 114
print r14
set r14 111
print r14
set r14 106
print r14
set r14 101
print r14
set r14 99
print r14
set r14 116
print r14
set r14 101
print r14
set r14 100
print r14
set r14 32
print r14
set r14 110
print r14
set r14 111
print r14
set r14 59
print r14
set r14 32
print r14
set r14 105
print r14
set r14 116
print r14
set r14 32
print r14
set r14 105
print r14
set r14 115
print r14
set r14 32
print r14
set r14 110
print r14
set r14 111
print r14
set r14 116
print r14
set r14 32
print r14
set r14 121
print r14
set r14 101
print r14
set r14 116
print r14
set r14 32
print r14
set r14 99
print r14
set r14 111
print r14
set r14 110
print r14
set r14 102
print r14
set r14 105
print r14
set r14 114
print r14
set r14 109
print r14
set r14 101
print r14
set r14 100
print r14
set r14 46
print r14
jmp te_finish
label te_positive
load8 r0 7400000000000000003
cmp r0 2
je te_positive_en
cmp r11 1
je te_positive_es_past
set r14 83
print r14
set r14 101
print r14
set r14 103
print r14
set r14 195
print r14
set r14 186
print r14
set r14 110
print r14
set r14 32
print r14
set r14 108
print r14
set r14 111
print r14
set r14 32
print r14
set r14 114
print r14
set r14 101
print r14
set r14 103
print r14
set r14 105
print r14
set r14 115
print r14
set r14 116
print r14
set r14 114
print r14
set r14 97
print r14
set r14 100
print r14
set r14 111
print r14
set r14 58
print r14
set r14 32
print r14
set r14 115
print r14
set r14 195
print r14
set r14 173
print r14
set r14 32
print r14
set r14 40
print r14
set r14 112
print r14
set r14 114
print r14
set r14 101
print r14
set r14 115
print r14
set r14 101
print r14
set r14 110
print r14
set r14 116
print r14
set r14 101
print r14
set r14 41
print r14
set r14 46
print r14
jmp te_finish
label te_positive_es_past
set r14 83
print r14
set r14 101
print r14
set r14 103
print r14
set r14 195
print r14
set r14 186
print r14
set r14 110
print r14
set r14 32
print r14
set r14 108
print r14
set r14 111
print r14
set r14 32
print r14
set r14 114
print r14
set r14 101
print r14
set r14 103
print r14
set r14 105
print r14
set r14 115
print r14
set r14 116
print r14
set r14 114
print r14
set r14 97
print r14
set r14 100
print r14
set r14 111
print r14
set r14 58
print r14
set r14 32
print r14
set r14 115
print r14
set r14 195
print r14
set r14 173
print r14
set r14 32
print r14
set r14 40
print r14
set r14 112
print r14
set r14 97
print r14
set r14 115
print r14
set r14 97
print r14
set r14 100
print r14
set r14 111
print r14
set r14 41
print r14
set r14 46
print r14
jmp te_finish
label te_positive_en
cmp r11 1
je te_positive_en_past
set r14 65
print r14
set r14 99
print r14
set r14 99
print r14
set r14 111
print r14
set r14 114
print r14
set r14 100
print r14
set r14 105
print r14
set r14 110
print r14
set r14 103
print r14
set r14 32
print r14
set r14 116
print r14
set r14 111
print r14
set r14 32
print r14
set r14 116
print r14
set r14 104
print r14
set r14 101
print r14
set r14 32
print r14
set r14 114
print r14
set r14 101
print r14
set r14 99
print r14
set r14 111
print r14
set r14 114
print r14
set r14 100
print r14
set r14 58
print r14
set r14 32
print r14
set r14 121
print r14
set r14 101
print r14
set r14 115
print r14
set r14 32
print r14
set r14 40
print r14
set r14 112
print r14
set r14 114
print r14
set r14 101
print r14
set r14 115
print r14
set r14 101
print r14
set r14 110
print r14
set r14 116
print r14
set r14 41
print r14
set r14 46
print r14
jmp te_finish
label te_positive_en_past
set r14 65
print r14
set r14 99
print r14
set r14 99
print r14
set r14 111
print r14
set r14 114
print r14
set r14 100
print r14
set r14 105
print r14
set r14 110
print r14
set r14 103
print r14
set r14 32
print r14
set r14 116
print r14
set r14 111
print r14
set r14 32
print r14
set r14 116
print r14
set r14 104
print r14
set r14 101
print r14
set r14 32
print r14
set r14 114
print r14
set r14 101
print r14
set r14 99
print r14
set r14 111
print r14
set r14 114
print r14
set r14 100
print r14
set r14 58
print r14
set r14 32
print r14
set r14 121
print r14
set r14 101
print r14
set r14 115
print r14
set r14 32
print r14
set r14 40
print r14
set r14 112
print r14
set r14 97
print r14
set r14 115
print r14
set r14 116
print r14
set r14 41
print r14
set r14 46
print r14
jmp te_finish
label te_negative
load8 r0 7400000000000000003
cmp r0 2
je te_negative_en
cmp r11 1
je te_negative_es_past
set r14 83
print r14
set r14 101
print r14
set r14 103
print r14
set r14 195
print r14
set r14 186
print r14
set r14 110
print r14
set r14 32
print r14
set r14 108
print r14
set r14 111
print r14
set r14 32
print r14
set r14 114
print r14
set r14 101
print r14
set r14 103
print r14
set r14 105
print r14
set r14 115
print r14
set r14 116
print r14
set r14 114
print r14
set r14 97
print r14
set r14 100
print r14
set r14 111
print r14
set r14 58
print r14
set r14 32
print r14
set r14 110
print r14
set r14 111
print r14
set r14 32
print r14
set r14 40
print r14
set r14 112
print r14
set r14 114
print r14
set r14 101
print r14
set r14 115
print r14
set r14 101
print r14
set r14 110
print r14
set r14 116
print r14
set r14 101
print r14
set r14 41
print r14
set r14 46
print r14
jmp te_finish
label te_negative_es_past
set r14 83
print r14
set r14 101
print r14
set r14 103
print r14
set r14 195
print r14
set r14 186
print r14
set r14 110
print r14
set r14 32
print r14
set r14 108
print r14
set r14 111
print r14
set r14 32
print r14
set r14 114
print r14
set r14 101
print r14
set r14 103
print r14
set r14 105
print r14
set r14 115
print r14
set r14 116
print r14
set r14 114
print r14
set r14 97
print r14
set r14 100
print r14
set r14 111
print r14
set r14 58
print r14
set r14 32
print r14
set r14 110
print r14
set r14 111
print r14
set r14 32
print r14
set r14 40
print r14
set r14 112
print r14
set r14 97
print r14
set r14 115
print r14
set r14 97
print r14
set r14 100
print r14
set r14 111
print r14
set r14 41
print r14
set r14 46
print r14
jmp te_finish
label te_negative_en
cmp r11 1
je te_negative_en_past
set r14 65
print r14
set r14 99
print r14
set r14 99
print r14
set r14 111
print r14
set r14 114
print r14
set r14 100
print r14
set r14 105
print r14
set r14 110
print r14
set r14 103
print r14
set r14 32
print r14
set r14 116
print r14
set r14 111
print r14
set r14 32
print r14
set r14 116
print r14
set r14 104
print r14
set r14 101
print r14
set r14 32
print r14
set r14 114
print r14
set r14 101
print r14
set r14 99
print r14
set r14 111
print r14
set r14 114
print r14
set r14 100
print r14
set r14 58
print r14
set r14 32
print r14
set r14 110
print r14
set r14 111
print r14
set r14 32
print r14
set r14 40
print r14
set r14 112
print r14
set r14 114
print r14
set r14 101
print r14
set r14 115
print r14
set r14 101
print r14
set r14 110
print r14
set r14 116
print r14
set r14 41
print r14
set r14 46
print r14
jmp te_finish
label te_negative_en_past
set r14 65
print r14
set r14 99
print r14
set r14 99
print r14
set r14 111
print r14
set r14 114
print r14
set r14 100
print r14
set r14 105
print r14
set r14 110
print r14
set r14 103
print r14
set r14 32
print r14
set r14 116
print r14
set r14 111
print r14
set r14 32
print r14
set r14 116
print r14
set r14 104
print r14
set r14 101
print r14
set r14 32
print r14
set r14 114
print r14
set r14 101
print r14
set r14 99
print r14
set r14 111
print r14
set r14 114
print r14
set r14 100
print r14
set r14 58
print r14
set r14 32
print r14
set r14 110
print r14
set r14 111
print r14
set r14 32
print r14
set r14 40
print r14
set r14 112
print r14
set r14 97
print r14
set r14 115
print r14
set r14 116
print r14
set r14 41
print r14
set r14 46
print r14
jmp te_finish
label te_finish
set r0 0
label te_clear_input
set r7 7400000000000000128
add r7 r0
store8 $r7 0
add r0 1
cmp r0 255
jlt te_clear_input
store8 7400000000000000016 0
store8 7400000000000000017 0
set r8 1
jmp te_clear_scratch_start
label te_delegate
set r8 0
label te_clear_scratch_start
set r0 16
label te_clear_scratch
set r7 8650000000000000000
add r7 r0
store8 $r7 0
add r0 1
cmp r0 4096
jlt te_clear_scratch
cmp r8 1
je te_halt
jmp te_parent_entry
label te_halt
halt
