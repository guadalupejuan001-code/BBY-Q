#!reverse-pc-machine-v1
# Learned, query-only byte frames. No example spelling is in executable code.
# Persistent records are separate from sealed prior grammars and E027/28/29.
load8 r0 9200000000000000000
cmp r0 1
jne lf_delegate
load8 r9 7400000000000000017
load8 r14 7400000000000000003
store8 9200000000000000600 0
set r10 0
label lf_rule
cmp r10 8
jge lf_chosen
set r15 9200000000000001024
mov r0 r10
mul r0 256
add r15 r0
load8 r0 $r15
cmp r0 2
jne lf_next
mov r7 r15
add r7 1
load8 r0 $r7
cmp r0 r14
jne lf_next
add r7 1
load8 r11 $r7
add r7 1
load8 r12 $r7
mov r13 r9
sub r13 r11
sub r13 r12
cmp r13 1
jlt lf_next
cmp r13 31
jgt lf_next
set r0 0
label lf_match_prefix
cmp r0 r11
jge lf_match_suffix_start
mov r7 r15
add r7 48
add r7 r0
load8 r3 $r7
set r7 7400000000000000128
add r7 r0
load8 r4 $r7
cmp r3 r4
jne lf_next
add r0 1
jmp lf_match_prefix
label lf_match_suffix_start
set r0 0
label lf_match_suffix
cmp r0 r12
jge lf_match_subject_start
mov r7 r15
add r7 128
add r7 r0
load8 r3 $r7
set r7 7400000000000000128
add r7 r11
add r7 r13
add r7 r0
load8 r4 $r7
cmp r3 r4
jne lf_next
add r0 1
jmp lf_match_suffix
label lf_match_subject_start
set r0 0
label lf_match_subject
cmp r0 r13
jge lf_save_start
set r7 7400000000000000128
add r7 r11
add r7 r0
load8 r3 $r7
cmp r3 48
jlt lf_next
cmp r3 57
jle lf_match_subject_next
cmp r3 97
jlt lf_next
cmp r3 122
jgt lf_next
label lf_match_subject_next
add r0 1
jmp lf_match_subject
label lf_save_start
load8 r0 9200000000000000600
cmp r0 0
je lf_save_first
cmp r0 r13
jne lf_reject
set r0 0
label lf_same_capture
cmp r0 r13
jge lf_next
set r7 7400000000000000128
add r7 r11
add r7 r0
load8 r3 $r7
set r7 9200000000000000512
add r7 r0
load8 r4 $r7
cmp r3 r4
jne lf_reject
add r0 1
jmp lf_same_capture
label lf_save_first
store8 9200000000000000600 r13
set r0 0
label lf_save_subject
cmp r0 r13
jge lf_next
set r7 7400000000000000128
add r7 r11
add r7 r0
load8 r3 $r7
set r7 9200000000000000512
add r7 r0
store8 $r7 r3
add r0 1
jmp lf_save_subject
label lf_next
add r10 1
jmp lf_rule
label lf_chosen
load8 r13 9200000000000000600
cmp r13 0
je lf_reject
# Clear the entire ORIGINAL raw request before constructing the canonical query.
set r0 0
label lf_clear_original
cmp r0 r9
jge lf_canonical
set r7 7400000000000000128
add r7 r0
store8 $r7 0
add r0 1
jmp lf_clear_original
label lf_canonical
load8 r14 7400000000000000003
cmp r14 2
je lf_canonical_en
store8 7400000000000000128 113
store8 7400000000000000129 117
store8 7400000000000000130 101
store8 7400000000000000131 32
store8 7400000000000000132 101
store8 7400000000000000133 115
store8 7400000000000000134 32
set r0 0
label lf_canonical_subject_es
cmp r0 r13
jge lf_canonical_suffix_es
set r7 9200000000000000512
add r7 r0
load8 r3 $r7
set r7 7400000000000000135
add r7 r0
store8 $r7 r3
add r0 1
jmp lf_canonical_subject_es
label lf_canonical_suffix_es
set r7 7400000000000000135
add r7 r13
store8 $r7 32
add r7 1
store8 $r7 121
add r7 1
store8 $r7 32
add r7 1
store8 $r7 113
add r7 1
store8 $r7 117
add r7 1
store8 $r7 101
add r7 1
store8 $r7 32
add r7 1
store8 $r7 114
add r7 1
store8 $r7 101
add r7 1
store8 $r7 113
add r7 1
store8 $r7 117
add r7 1
store8 $r7 105
add r7 1
store8 $r7 101
add r7 1
store8 $r7 114
add r7 1
store8 $r7 101
add r7 1
mov r0 r13
add r0 22
store8 7400000000000000017 r0
store8 7400000000000000016 1
jmp lf_reject
label lf_canonical_en
store8 7400000000000000128 119
store8 7400000000000000129 104
store8 7400000000000000130 97
store8 7400000000000000131 116
store8 7400000000000000132 32
store8 7400000000000000133 105
store8 7400000000000000134 115
store8 7400000000000000135 32
set r0 0
label lf_canonical_subject_en
cmp r0 r13
jge lf_canonical_suffix_en
set r7 9200000000000000512
add r7 r0
load8 r3 $r7
set r7 7400000000000000136
add r7 r0
store8 $r7 r3
add r0 1
jmp lf_canonical_subject_en
label lf_canonical_suffix_en
set r7 7400000000000000136
add r7 r13
store8 $r7 32
add r7 1
store8 $r7 97
add r7 1
store8 $r7 110
add r7 1
store8 $r7 100
add r7 1
store8 $r7 32
add r7 1
store8 $r7 119
add r7 1
store8 $r7 104
add r7 1
store8 $r7 97
add r7 1
store8 $r7 116
add r7 1
store8 $r7 32
add r7 1
store8 $r7 100
add r7 1
store8 $r7 111
add r7 1
store8 $r7 101
add r7 1
store8 $r7 115
add r7 1
store8 $r7 32
add r7 1
store8 $r7 105
add r7 1
store8 $r7 116
add r7 1
store8 $r7 32
add r7 1
store8 $r7 110
add r7 1
store8 $r7 101
add r7 1
store8 $r7 101
add r7 1
store8 $r7 100
add r7 1
mov r0 r13
add r0 30
store8 7400000000000000017 r0
store8 7400000000000000016 1
jmp lf_reject
label lf_reject
set r0 512
label lf_clean_scratch
set r7 9200000000000000000
add r7 r0
store8 $r7 0
add r0 1
cmp r0 1024
jlt lf_clean_scratch
label lf_delegate
jmp lf_parent_entry
