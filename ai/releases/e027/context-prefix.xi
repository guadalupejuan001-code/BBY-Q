#!reverse-pc-machine-v1
# E027 long-context storage/retrieval; all decisions and byte handling execute in XI.
# The ordinary E025 path remains byte-for-byte instruction-equivalent.
load8 r9 7400000000000000017
cmp r9 5
jlt lctx_original
load8 r3 7400000000000000128
cmp r3 64
jne lctx_original
load8 r3 7400000000000000129
cmp r3 99
jne lctx_original
load8 r3 7400000000000000130
cmp r3 116
jne lctx_original
load8 r3 7400000000000000131
cmp r3 120
jne lctx_original
load8 r3 7400000000000000132
cmp r3 32
jne lctx_original
load8 r3 8900000000000000000
cmp r3 76
je lctx_ready
store8 8900000000000000000 76
store8 8900000000000000001 1
store8 8900000000000000002 0
store8 8900000000000000003 0
store8 8900000000000000004 0
store8 8900000000000000005 0
store8 8900000000000000006 0
label lctx_ready
label lctx_check_0
cmp r9 11
jne lctx_check_1
load8 r3 7400000000000000128
cmp r3 64
jne lctx_check_1
load8 r3 7400000000000000129
cmp r3 99
jne lctx_check_1
load8 r3 7400000000000000130
cmp r3 116
jne lctx_check_1
load8 r3 7400000000000000131
cmp r3 120
jne lctx_check_1
load8 r3 7400000000000000132
cmp r3 32
jne lctx_check_1
load8 r3 7400000000000000133
cmp r3 115
jne lctx_check_1
load8 r3 7400000000000000134
cmp r3 116
jne lctx_check_1
load8 r3 7400000000000000135
cmp r3 97
jne lctx_check_1
load8 r3 7400000000000000136
cmp r3 116
jne lctx_check_1
load8 r3 7400000000000000137
cmp r3 117
jne lctx_check_1
load8 r3 7400000000000000138
cmp r3 115
jne lctx_check_1
jmp lctx_status
label lctx_check_1
cmp r9 10
jne lctx_check_2
load8 r3 7400000000000000128
cmp r3 64
jne lctx_check_2
load8 r3 7400000000000000129
cmp r3 99
jne lctx_check_2
load8 r3 7400000000000000130
cmp r3 116
jne lctx_check_2
load8 r3 7400000000000000131
cmp r3 120
jne lctx_check_2
load8 r3 7400000000000000132
cmp r3 32
jne lctx_check_2
load8 r3 7400000000000000133
cmp r3 99
jne lctx_check_2
load8 r3 7400000000000000134
cmp r3 108
jne lctx_check_2
load8 r3 7400000000000000135
cmp r3 101
jne lctx_check_2
load8 r3 7400000000000000136
cmp r3 97
jne lctx_check_2
load8 r3 7400000000000000137
cmp r3 114
jne lctx_check_2
jmp lctx_clear
label lctx_check_2
cmp r9 9
jle lctx_check_3
load8 r3 7400000000000000128
cmp r3 64
jne lctx_check_3
load8 r3 7400000000000000129
cmp r3 99
jne lctx_check_3
load8 r3 7400000000000000130
cmp r3 116
jne lctx_check_3
load8 r3 7400000000000000131
cmp r3 120
jne lctx_check_3
load8 r3 7400000000000000132
cmp r3 32
jne lctx_check_3
load8 r3 7400000000000000133
cmp r3 97
jne lctx_check_3
load8 r3 7400000000000000134
cmp r3 100
jne lctx_check_3
load8 r3 7400000000000000135
cmp r3 100
jne lctx_check_3
load8 r3 7400000000000000136
cmp r3 32
jne lctx_check_3
jmp lctx_add
label lctx_check_3
cmp r9 9
jle lctx_check_4
load8 r3 7400000000000000128
cmp r3 64
jne lctx_check_4
load8 r3 7400000000000000129
cmp r3 99
jne lctx_check_4
load8 r3 7400000000000000130
cmp r3 116
jne lctx_check_4
load8 r3 7400000000000000131
cmp r3 120
jne lctx_check_4
load8 r3 7400000000000000132
cmp r3 32
jne lctx_check_4
load8 r3 7400000000000000133
cmp r3 103
jne lctx_check_4
load8 r3 7400000000000000134
cmp r3 101
jne lctx_check_4
load8 r3 7400000000000000135
cmp r3 116
jne lctx_check_4
load8 r3 7400000000000000136
cmp r3 32
jne lctx_check_4
jmp lctx_get
label lctx_check_4
cmp r9 10
jle lctx_check_5
load8 r3 7400000000000000128
cmp r3 64
jne lctx_check_5
load8 r3 7400000000000000129
cmp r3 99
jne lctx_check_5
load8 r3 7400000000000000130
cmp r3 116
jne lctx_check_5
load8 r3 7400000000000000131
cmp r3 120
jne lctx_check_5
load8 r3 7400000000000000132
cmp r3 32
jne lctx_check_5
load8 r3 7400000000000000133
cmp r3 102
jne lctx_check_5
load8 r3 7400000000000000134
cmp r3 105
jne lctx_check_5
load8 r3 7400000000000000135
cmp r3 110
jne lctx_check_5
load8 r3 7400000000000000136
cmp r3 100
jne lctx_check_5
load8 r3 7400000000000000137
cmp r3 32
jne lctx_check_5
jmp lctx_find
label lctx_check_5
set r14 67
print r14
set r14 84
print r14
set r14 88
print r14
set r14 32
print r14
set r14 99
print r14
set r14 111
print r14
set r14 109
print r14
set r14 97
print r14
set r14 110
print r14
set r14 100
print r14
set r14 111
print r14
set r14 32
print r14
set r14 100
print r14
set r14 101
print r14
set r14 115
print r14
set r14 99
print r14
set r14 111
print r14
set r14 110
print r14
set r14 111
print r14
set r14 99
print r14
set r14 105
print r14
set r14 100
print r14
set r14 111
print r14
set r14 46
print r14
halt
label lctx_status
load8 r4 8900000000000000002
load8 r8 8900000000000000003
mul r8 256
add r4 r8
load8 r6 8900000000000000004
load8 r8 8900000000000000005
mul r8 256
add r6 r8
load8 r8 8900000000000000006
mul r8 65536
add r6 r8
set r14 67
print r14
set r14 84
print r14
set r14 88
print r14
set r14 32
print r14
set r14 110
print r14
set r14 61
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
div r8 1
add r8 48
mov r14 r8
print r14
mod r0 1
set r14 32
print r14
set r14 98
print r14
set r14 121
print r14
set r14 116
print r14
set r14 101
print r14
set r14 115
print r14
set r14 61
print r14
mov r0 r6
mov r8 r0
div r8 100000
add r8 48
mov r14 r8
print r14
mod r0 100000
mov r8 r0
div r8 10000
add r8 48
mov r14 r8
print r14
mod r0 10000
mov r8 r0
div r8 1000
add r8 48
mov r14 r8
print r14
mod r0 1000
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
div r8 1
add r8 48
mov r14 r8
print r14
mod r0 1
set r14 32
print r14
set r14 108
print r14
set r14 105
print r14
set r14 109
print r14
set r14 105
print r14
set r14 116
print r14
set r14 101
print r14
set r14 61
print r14
set r14 49
print r14
set r14 49
print r14
set r14 52
print r14
set r14 54
print r14
set r14 56
print r14
set r14 56
print r14
halt
label lctx_clear
load8 r4 8900000000000000002
load8 r8 8900000000000000003
mul r8 256
add r4 r8
load8 r6 8900000000000000004
load8 r8 8900000000000000005
mul r8 256
add r6 r8
load8 r8 8900000000000000006
mul r8 65536
add r6 r8
set r0 0
label lctx_clear_data
cmp r0 r6
jge lctx_clear_metadata_start
set r7 8900000000000100000
add r7 r0
store8 $r7 0
add r0 1
jmp lctx_clear_data
label lctx_clear_metadata_start
mul r4 4
set r0 0
label lctx_clear_metadata
cmp r0 r4
jge lctx_clear_done
set r7 8900000000000001024
add r7 r0
store8 $r7 0
add r0 1
jmp lctx_clear_metadata
label lctx_clear_done
store8 8900000000000000002 0
store8 8900000000000000003 0
store8 8900000000000000004 0
store8 8900000000000000005 0
store8 8900000000000000006 0
set r14 67
print r14
set r14 84
print r14
set r14 88
print r14
set r14 32
print r14
set r14 118
print r14
set r14 97
print r14
set r14 99
print r14
set r14 105
print r14
set r14 97
print r14
set r14 100
print r14
set r14 111
print r14
set r14 46
print r14
halt
label lctx_add
load8 r4 8900000000000000002
load8 r8 8900000000000000003
mul r8 256
add r4 r8
load8 r6 8900000000000000004
load8 r8 8900000000000000005
mul r8 256
add r6 r8
load8 r8 8900000000000000006
mul r8 65536
add r6 r8
mov r5 r9
sub r5 9
cmp r5 224
jgt lctx_full
cmp r4 512
jge lctx_full
mov r10 r6
add r10 r5
cmp r10 114688
jgt lctx_full
mov r7 r4
mul r7 4
add r7 8900000000000001024
mov r8 r6
mod r8 256
store8 $r7 r8
add r7 1
mov r8 r6
div r8 256
mod r8 256
store8 $r7 r8
add r7 1
mov r8 r6
div r8 65536
store8 $r7 r8
add r7 1
store8 $r7 r5
set r0 0
label lctx_add_copy
cmp r0 r5
jge lctx_add_complete
set r7 7400000000000000137
add r7 r0
load8 r3 $r7
set r7 8900000000000100000
add r7 r6
add r7 r0
store8 $r7 r3
add r0 1
jmp lctx_add_copy
label lctx_add_complete
set r14 67
print r14
set r14 84
print r14
set r14 88
print r14
set r14 32
print r14
set r14 103
print r14
set r14 117
print r14
set r14 97
print r14
set r14 114
print r14
set r14 100
print r14
set r14 97
print r14
set r14 100
print r14
set r14 111
print r14
set r14 32
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
div r8 1
add r8 48
mov r14 r8
print r14
mod r0 1
add r4 1
mov r8 r4
mod r8 256
store8 8900000000000000002 r8
mov r8 r4
div r8 256
store8 8900000000000000003 r8
mov r8 r10
mod r8 256
store8 8900000000000000004 r8
mov r8 r10
div r8 256
mod r8 256
store8 8900000000000000005 r8
mov r8 r10
div r8 65536
store8 8900000000000000006 r8
halt
label lctx_full
set r14 67
print r14
set r14 84
print r14
set r14 88
print r14
set r14 32
print r14
set r14 108
print r14
set r14 105
print r14
set r14 109
print r14
set r14 105
print r14
set r14 116
print r14
set r14 101
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
set r14 103
print r14
set r14 117
print r14
set r14 97
print r14
set r14 114
print r14
set r14 100
print r14
set r14 97
print r14
set r14 100
print r14
set r14 111
print r14
set r14 46
print r14
halt
label lctx_get
set r4 0
set r0 9
cmp r9 12
jgt lctx_invalid
label lctx_get_parse
cmp r0 r9
jge lctx_get_parsed
set r7 7400000000000000128
add r7 r0
load8 r3 $r7
cmp r3 48
jlt lctx_invalid
cmp r3 57
jgt lctx_invalid
sub r3 48
mul r4 10
add r4 r3
add r0 1
jmp lctx_get_parse
label lctx_get_parsed
load8 r10 8900000000000000002
load8 r8 8900000000000000003
mul r8 256
add r10 r8
cmp r4 r10
jge lctx_absent
jmp lctx_emit_segment
label lctx_find
mov r4 r9
sub r4 10
cmp r4 3
jlt lctx_invalid
cmp r4 80
jgt lctx_invalid
load8 r12 8900000000000000004
load8 r8 8900000000000000005
mul r8 256
add r12 r8
load8 r8 8900000000000000006
mul r8 65536
add r12 r8
cmp r12 r4
jlt lctx_no_match
# Boyer-Moore-Horspool skip table for casefolded ASCII; no external language code.
set r0 0
label lctx_find_skip_init
cmp r0 256
jge lctx_find_skip_build_start
set r7 8900000000000005000
add r7 r0
store8 $r7 r4
add r0 1
jmp lctx_find_skip_init
label lctx_find_skip_build_start
set r0 0
label lctx_find_skip_build
mov r15 r4
sub r15 1
cmp r0 r15
jge lctx_find_search_start
set r7 7400000000000000138
add r7 r0
load8 r3 $r7
cmp r3 65
jlt lctx_find_skip_set
cmp r3 90
jgt lctx_find_skip_set
add r3 32
label lctx_find_skip_set
mov r8 r4
sub r8 1
sub r8 r0
set r7 8900000000000005000
add r7 r3
store8 $r7 r8
cmp r3 97
jlt lctx_find_skip_next
cmp r3 122
jgt lctx_find_skip_next
sub r7 32
store8 $r7 r8
label lctx_find_skip_next
add r0 1
jmp lctx_find_skip_build
label lctx_find_search_start
set r6 0
set r5 -1
mov r12 r12
sub r12 r4
label lctx_find_position
cmp r6 r12
jgt lctx_find_finish_search
mov r15 r6
add r15 r4
sub r15 1
set r7 8900000000000100000
add r7 r15
load8 r3 $r7
cmp r3 65
jlt lctx_find_last_ready
cmp r3 90
jgt lctx_find_last_ready
add r3 32
label lctx_find_last_ready
mov r13 r3
set r7 7400000000000000138
mov r15 r4
sub r15 1
add r7 r15
load8 r11 $r7
cmp r11 65
jlt lctx_find_last_compare
cmp r11 90
jgt lctx_find_last_compare
add r11 32
label lctx_find_last_compare
cmp r13 r11
jne lctx_find_skip_position
set r0 0
label lctx_find_compare
cmp r0 r4
jge lctx_find_record_match
set r7 8900000000000100000
add r7 r6
add r7 r0
load8 r3 $r7
set r7 7400000000000000138
add r7 r0
load8 r11 $r7
cmp r3 65
jlt lctx_find_needle_case
cmp r3 90
jgt lctx_find_needle_case
add r3 32
label lctx_find_needle_case
cmp r11 65
jlt lctx_find_byte_compare
cmp r11 90
jgt lctx_find_byte_compare
add r11 32
label lctx_find_byte_compare
cmp r3 r11
jne lctx_find_skip_position
add r0 1
jmp lctx_find_compare
label lctx_find_record_match
mov r5 r6
add r6 1
jmp lctx_find_position
label lctx_find_skip_position
set r7 8900000000000005000
add r7 r13
load8 r8 $r7
cmp r8 1
jlt lctx_invalid
add r6 r8
jmp lctx_find_position
label lctx_find_finish_search
set r0 0
label lctx_find_skip_clear
cmp r0 256
jge lctx_find_search_done
set r7 8900000000000005000
add r7 r0
store8 $r7 0
add r0 1
jmp lctx_find_skip_clear
label lctx_find_search_done
cmp r5 0
jlt lctx_no_match
jmp lctx_find_matched
label lctx_find_matched
load8 r13 8900000000000000002
load8 r8 8900000000000000003
mul r8 256
add r13 r8
set r11 0
set r12 0
label lctx_find_segment
cmp r11 r13
jge lctx_no_match
mov r7 r11
mul r7 4
add r7 8900000000000001027
load8 r3 $r7
mov r15 r12
add r15 r3
cmp r5 r15
jlt lctx_find_selected
mov r12 r15
add r11 1
jmp lctx_find_segment
label lctx_find_selected
mov r4 r11
jmp lctx_emit_segment
label lctx_emit_segment
mov r7 r4
mul r7 4
add r7 8900000000000001024
load8 r6 $r7
add r7 1
load8 r8 $r7
mul r8 256
add r6 r8
add r7 1
load8 r8 $r7
mul r8 65536
add r6 r8
add r7 1
load8 r5 $r7
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
div r8 1
add r8 48
mov r14 r8
print r14
mod r0 1
set r14 32
print r14
set r0 0
label lctx_emit_byte
cmp r0 r5
jge lctx_emit_done
set r7 8900000000000100000
add r7 r6
add r7 r0
load8 r3 $r7
mov r14 r3
print r14
add r0 1
jmp lctx_emit_byte
label lctx_emit_done
halt
label lctx_absent
set r14 67
print r14
set r14 84
print r14
set r14 88
print r14
set r14 32
print r14
set r14 115
print r14
set r14 101
print r14
set r14 103
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
set r14 32
print r14
set r14 105
print r14
set r14 110
print r14
set r14 101
print r14
set r14 120
print r14
set r14 105
print r14
set r14 115
print r14
set r14 116
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
halt
label lctx_no_match
set r14 67
print r14
set r14 84
print r14
set r14 88
print r14
set r14 32
print r14
set r14 115
print r14
set r14 105
print r14
set r14 110
print r14
set r14 32
print r14
set r14 99
print r14
set r14 111
print r14
set r14 105
print r14
set r14 110
print r14
set r14 99
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
set r14 46
print r14
halt
label lctx_invalid
set r14 67
print r14
set r14 84
print r14
set r14 88
print r14
set r14 32
print r14
set r14 115
print r14
set r14 111
print r14
set r14 108
print r14
set r14 105
print r14
set r14 99
print r14
set r14 105
print r14
set r14 116
print r14
set r14 117
print r14
set r14 100
print r14
set r14 32
print r14
set r14 105
print r14
set r14 110
print r14
set r14 118
print r14
set r14 97
print r14
set r14 108
print r14
set r14 105
print r14
set r14 100
print r14
set r14 97
print r14
set r14 46
print r14
halt
