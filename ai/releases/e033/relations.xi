#!reverse-pc-machine-v1
# Native learned functional relations: shared strings, indexed facts, provenance.
load8 r0 8500000000000000000
cmp r0 1
jne mr_delegate
store8 8500000000000000010 0
store8 8500000000000000011 0
store8 8500000000000000017 0
load8 r9 7400000000000000017
store8 8500000000000000016 r9
set r0 0
label mr_fold
cmp r0 r9
jge mr_commands
set r7 7400000000000000128
add r7 r0
load8 r3 $r7
cmp r3 65
jlt mr_fold_save
cmp r3 90
jgt mr_fold_save
add r3 32
label mr_fold_save
set r7 8500000000000000128
add r7 r0
store8 $r7 r3
add r0 1
jmp mr_fold
label mr_frames_start
set r10 0
label mr_frame
cmp r10 32
jge mr_selected
set r15 8500000000000004096
mov r0 r10
mul r0 256
add r15 r0
load8 r0 $r15
cmp r0 2
jne mr_next
mov r7 r15
add r7 5
load8 r11 $r7
add r7 1
load8 r12 $r7
add r7 1
load8 r13 $r7
mov r8 r9
sub r8 r13
cmp r8 r11
jle mr_next
set r0 0
label mr_prefix
cmp r0 r11
jge mr_suffix_start
mov r7 r15
add r7 144
add r7 r0
load8 r3 $r7
set r7 8500000000000000128
add r7 r0
load8 r4 $r7
cmp r3 r4
jne mr_next
add r0 1
jmp mr_prefix
label mr_suffix_start
set r0 0
label mr_suffix
cmp r0 r13
jge mr_capture_start
mov r7 r15
add r7 240
add r7 r0
load8 r3 $r7
set r7 8500000000000000128
add r7 r8
add r7 r0
load8 r4 $r7
cmp r3 r4
jne mr_next
add r0 1
jmp mr_suffix
label mr_capture_start
store8 8500000000000000040 r11
mov r7 r15
add r7 1
load8 r0 $r7
cmp r0 2
je mr_query_capture
store8 8500000000000000044 0
set r4 1
label mr_middle_position
cmp r4 48
jgt mr_middle_done
mov r1 r11
add r1 r4
mov r2 r1
add r2 r12
cmp r2 r8
jge mr_middle_done
mov r6 r8
sub r6 r2
cmp r6 80
jgt mr_middle_next
set r0 0
label mr_middle
cmp r0 r12
jge mr_middle_hit
mov r7 r15
add r7 192
add r7 r0
load8 r3 $r7
set r7 8500000000000000128
add r7 r1
add r7 r0
load8 r5 $r7
cmp r3 r5
jne mr_middle_next
add r0 1
jmp mr_middle
label mr_middle_hit
load8 r0 8500000000000000044
add r0 1
store8 8500000000000000044 r0
store8 8500000000000000041 r4
store8 8500000000000000042 r2
store8 8500000000000000043 r6
label mr_middle_next
add r4 1
jmp mr_middle_position
label mr_middle_done
load8 r0 8500000000000000044
cmp r0 1
jne mr_next
jmp mr_validate_roles
label mr_query_capture
sub r8 r11
cmp r8 1
jlt mr_next
cmp r8 48
jgt mr_next
store8 8500000000000000041 r8
store8 8500000000000000042 0
store8 8500000000000000043 0
label mr_validate_roles
load8 r5 8500000000000000041
load8 r6 8500000000000000040
cmp r5 0
je mr_subject_done
set r0 0
label mr_subject_copy
cmp r0 r5
jge mr_subject_done
set r7 8500000000000000128
add r7 r6
add r7 r0
load8 r3 $r7
cmp r3 32
jlt mr_next
cmp r3 32
jne mr_subject_character
cmp r0 0
je mr_next
mov r1 r5
sub r1 1
cmp r0 r1
je mr_next
label mr_subject_character
cmp r3 33
je mr_next
cmp r3 46
je mr_next
cmp r3 59
je mr_next
cmp r3 63
je mr_next
cmp r3 58
je mr_next
set r7 8500000000000000512
add r7 r0
store8 $r7 r3
add r0 1
jmp mr_subject_copy
label mr_subject_done
load8 r5 8500000000000000043
load8 r6 8500000000000000042
cmp r5 0
je mr_value_done
set r0 0
label mr_value_copy
cmp r0 r5
jge mr_value_done
set r7 8500000000000000128
add r7 r6
add r7 r0
load8 r3 $r7
cmp r3 32
jlt mr_next
cmp r3 32
jne mr_value_character
cmp r0 0
je mr_next
mov r1 r5
sub r1 1
cmp r0 r1
je mr_next
label mr_value_character
cmp r3 33
je mr_next
cmp r3 46
je mr_next
cmp r3 59
je mr_next
cmp r3 63
je mr_next
cmp r3 58
je mr_next
set r7 8500000000000000576
add r7 r0
store8 $r7 r3
add r0 1
jmp mr_value_copy
label mr_value_done
load8 r0 8500000000000000017
cmp r0 0
je mr_remember
mov r7 r15
add r7 1
load8 r3 $r7
load8 r4 8500000000000000018
cmp r3 r4
jne mr_ambiguous
add r7 1
load8 r3 $r7
load8 r4 8500000000000000019
cmp r3 r4
jne mr_ambiguous
load8 r3 8500000000000000041
load8 r4 8500000000000000020
cmp r3 r4
jne mr_ambiguous
load8 r3 8500000000000000043
load8 r4 8500000000000000021
cmp r3 r4
jne mr_ambiguous
set r0 0
load8 r8 8500000000000000020
label mr_same_subject
cmp r0 r8
jge mr_same_subject_done
set r7 8500000000000000512
add r7 r0
load8 r3 $r7
set r7 8500000000000000768
add r7 r0
load8 r4 $r7
cmp r3 r4
jne mr_ambiguous
add r0 1
jmp mr_same_subject
label mr_same_subject_done
set r0 0
load8 r8 8500000000000000021
label mr_same_value
cmp r0 r8
jge mr_same_value_done
set r7 8500000000000000576
add r7 r0
load8 r3 $r7
set r7 8500000000000000832
add r7 r0
load8 r4 $r7
cmp r3 r4
jne mr_ambiguous
add r0 1
jmp mr_same_value
label mr_same_value_done
jmp mr_next
label mr_remember
store8 8500000000000000017 1
mov r0 r10
add r0 1
store8 8500000000000000022 r0
mov r7 r15
add r7 1
load8 r3 $r7
store8 8500000000000000018 r3
add r7 1
load8 r3 $r7
store8 8500000000000000019 r3
load8 r3 8500000000000000041
store8 8500000000000000020 r3
load8 r3 8500000000000000043
store8 8500000000000000021 r3
set r0 0
load8 r8 8500000000000000020
label mr_remember_subject
cmp r0 r8
jge mr_remember_subject_done
set r7 8500000000000000512
add r7 r0
load8 r3 $r7
set r7 8500000000000000768
add r7 r0
store8 $r7 r3
add r0 1
jmp mr_remember_subject
label mr_remember_subject_done
set r0 0
load8 r8 8500000000000000021
label mr_remember_value
cmp r0 r8
jge mr_remember_value_done
set r7 8500000000000000576
add r7 r0
load8 r3 $r7
set r7 8500000000000000832
add r7 r0
store8 $r7 r3
add r0 1
jmp mr_remember_value
label mr_remember_value_done
label mr_next
add r10 1
jmp mr_frame
label mr_selected
load8 r0 8500000000000000017
cmp r0 1
jne mr_delegate
set r0 0
set r8 0
load8 r5 8500000000000000020
label mr_entity_hash
cmp r0 r5
jge mr_entity_probe_start
set r7 8500000000000000768
add r7 r0
load8 r3 $r7
mul r8 131
add r8 r3
mod r8 127
add r0 1
jmp mr_entity_hash
label mr_entity_probe_start
set r10 0
label mr_entity_probe
cmp r10 127
jge mr_capacity
set r15 8500000000000032768
mov r0 r8
mul r0 64
add r15 r0
load8 r1 $r15
cmp r1 0
je mr_entity_new
cmp r1 r5
jne mr_entity_collision
set r0 0
label mr_entity_compare
cmp r0 r5
jge mr_entity_found
mov r7 r15
add r7 1
add r7 r0
load8 r3 $r7
set r7 8500000000000000768
add r7 r0
load8 r4 $r7
cmp r3 r4
jne mr_entity_collision
add r0 1
jmp mr_entity_compare
label mr_entity_collision
add r8 1
mod r8 127
add r10 1
jmp mr_entity_probe
label mr_entity_new
load8 r0 8500000000000000018
cmp r0 2
je mr_unknown
load8 r0 8500000000000000001
cmp r0 96
jge mr_capacity
store8 8500000000000000033 1
jmp mr_entity_save_id
label mr_entity_found
store8 8500000000000000033 0
label mr_entity_save_id
add r8 1
store8 8500000000000000032 r8
load8 r0 8500000000000000018
cmp r0 2
je mr_fact_start
set r0 0
set r8 0
load8 r5 8500000000000000021
label mr_value_hash
cmp r0 r5
jge mr_value_probe_start
set r7 8500000000000000832
add r7 r0
load8 r3 $r7
mul r8 131
add r8 r3
mod r8 127
add r0 1
jmp mr_value_hash
label mr_value_probe_start
set r10 0
label mr_value_probe
cmp r10 127
jge mr_capacity
set r15 8500000000000049152
mov r0 r8
mul r0 96
add r15 r0
load8 r1 $r15
cmp r1 0
je mr_value_new
cmp r1 r5
jne mr_value_collision
set r0 0
label mr_value_compare
cmp r0 r5
jge mr_value_found
mov r7 r15
add r7 1
add r7 r0
load8 r3 $r7
set r7 8500000000000000832
add r7 r0
load8 r4 $r7
cmp r3 r4
jne mr_value_collision
add r0 1
jmp mr_value_compare
label mr_value_collision
add r8 1
mod r8 127
add r10 1
jmp mr_value_probe
label mr_value_new
load8 r0 8500000000000000002
cmp r0 96
jge mr_capacity
store8 8500000000000000035 1
jmp mr_value_save_id
label mr_value_found
store8 8500000000000000035 0
label mr_value_save_id
add r8 1
store8 8500000000000000034 r8
label mr_fact_start
load8 r0 8500000000000000018
cmp r0 2
jne mr_hash_fact
load8 r0 8500000000000000005
cmp r0 1
jne mr_hash_fact
load8 r0 8500000000000000006
load8 r1 8500000000000000032
cmp r0 r1
jne mr_hash_fact
load8 r0 8500000000000000007
load8 r1 8500000000000000019
cmp r0 r1
jne mr_hash_fact
load8 r0 8500000000000000009
load8 r1 8500000000000000003
cmp r0 r1
jne mr_hash_fact
load8 r8 8500000000000000008
store8 8500000000000000036 r8
store8 8500000000000000010 1
jmp mr_answer
label mr_hash_fact
load8 r8 8500000000000000032
mul r8 31
load8 r0 8500000000000000019
add r8 r0
mod r8 256
set r10 0
label mr_fact_probe
cmp r10 256
jge mr_capacity
set r15 8500000000000065536
mov r0 r8
mul r0 8
add r15 r0
load8 r3 $r15
cmp r3 0
je mr_empty_fact
load8 r4 8500000000000000032
cmp r3 r4
jne mr_fact_collision
mov r7 r15
add r7 1
load8 r3 $r7
load8 r4 8500000000000000019
cmp r3 r4
jne mr_fact_collision
store8 8500000000000000037 0
jmp mr_fact_slot
label mr_fact_collision
add r8 1
mod r8 256
add r10 1
jmp mr_fact_probe
label mr_empty_fact
load8 r0 8500000000000000018
cmp r0 2
je mr_unknown
store8 8500000000000000037 1
label mr_fact_slot
store8 8500000000000000036 r8
mov r0 r10
add r0 1
cmp r0 255
jle mr_save_probe_count
set r0 255
label mr_save_probe_count
store8 8500000000000000011 r0
load8 r0 8500000000000000018
cmp r0 2
je mr_save_cache
load8 r0 8500000000000000037
cmp r0 1
je mr_new_event
mov r7 r15
add r7 2
load8 r1 $r7
cmp r1 1
jne mr_duplicate_conflict
add r7 1
load8 r3 $r7
load8 r4 8500000000000000034
cmp r3 r4
je mr_ack
jmp mr_new_event
label mr_duplicate_conflict
load8 r0 8500000000000000018
cmp r0 3
je mr_new_event
mov r7 r15
add r7 5
load8 r1 $r7
sub r1 1
mul r1 8
set r7 8500000000000070002
add r7 r1
load8 r3 $r7
load8 r4 8500000000000000034
cmp r3 r4
je mr_ack
label mr_new_event
load8 r0 8500000000000000003
cmp r0 255
jge mr_capacity
load8 r0 8500000000000000033
cmp r0 1
jne mr_store_entity_done
load8 r0 8500000000000000032
sub r0 1
mul r0 64
set r15 8500000000000032768
add r15 r0
load8 r8 8500000000000000020
store8 $r15 r8
set r0 0
label mr_store_entity
cmp r0 r8
jge mr_store_entity_count
set r7 8500000000000000768
add r7 r0
load8 r3 $r7
mov r7 r15
add r7 1
add r7 r0
store8 $r7 r3
add r0 1
jmp mr_store_entity
label mr_store_entity_count
load8 r0 8500000000000000001
add r0 1
store8 8500000000000000001 r0
label mr_store_entity_done
load8 r0 8500000000000000035
cmp r0 1
jne mr_store_value_done
load8 r0 8500000000000000034
sub r0 1
mul r0 96
set r15 8500000000000049152
add r15 r0
load8 r8 8500000000000000021
store8 $r15 r8
set r0 0
label mr_store_value
cmp r0 r8
jge mr_store_value_count
set r7 8500000000000000832
add r7 r0
load8 r3 $r7
mov r7 r15
add r7 1
add r7 r0
store8 $r7 r3
add r0 1
jmp mr_store_value
label mr_store_value_count
load8 r0 8500000000000000002
add r0 1
store8 8500000000000000002 r0
label mr_store_value_done
load8 r0 8500000000000000036
mul r0 8
set r15 8500000000000065536
add r15 r0
set r13 0
load8 r0 8500000000000000037
cmp r0 1
je mr_previous_ready
mov r7 r15
add r7 2
load8 r0 $r7
cmp r0 2
je mr_previous_conflict
add r7 2
load8 r13 $r7
jmp mr_previous_ready
label mr_previous_conflict
mov r7 r15
add r7 5
load8 r13 $r7
label mr_previous_ready
load8 r12 8500000000000000003
mov r0 r12
mul r0 8
set r11 8500000000000070000
add r11 r0
load8 r3 8500000000000000032
store8 $r11 r3
add r11 1
load8 r3 8500000000000000019
store8 $r11 r3
add r11 1
load8 r3 8500000000000000034
store8 $r11 r3
add r11 1
load8 r3 8500000000000000022
store8 $r11 r3
add r11 1
store8 $r11 r13
add r12 1
store8 8500000000000000003 r12
store8 8500000000000000005 0
load8 r3 8500000000000000032
store8 $r15 r3
mov r7 r15
add r7 1
load8 r3 8500000000000000019
store8 $r7 r3
load8 r0 8500000000000000037
cmp r0 1
je mr_publish_value
load8 r0 8500000000000000018
cmp r0 3
je mr_publish_value
mov r7 r15
add r7 2
store8 $r7 2
mov r7 r15
add r7 5
store8 $r7 r12
jmp mr_ack
label mr_publish_value
mov r7 r15
add r7 2
store8 $r7 1
add r7 1
load8 r3 8500000000000000034
store8 $r7 r3
add r7 1
store8 $r7 r12
add r7 1
store8 $r7 0
jmp mr_ack
label mr_save_cache
store8 8500000000000000005 1
load8 r0 8500000000000000032
store8 8500000000000000006 r0
load8 r0 8500000000000000019
store8 8500000000000000007 r0
load8 r0 8500000000000000036
store8 8500000000000000008 r0
load8 r0 8500000000000000003
store8 8500000000000000009 r0
label mr_answer
load8 r0 8500000000000000036
mul r0 8
set r15 8500000000000065536
add r15 r0
mov r7 r15
add r7 2
load8 r0 $r7
cmp r0 2
je mr_conflict
add r7 1
load8 r3 $r7
add r7 1
load8 r12 $r7
sub r3 1
mul r3 96
set r15 8500000000000049152
add r15 r3
load8 r8 $r15
set r0 0
label mr_value_output
cmp r0 r8
jge mr_citation
mov r7 r15
add r7 1
add r7 r0
load8 r14 $r7
print r14
add r0 1
jmp mr_value_output
label mr_citation
set r14 32
print r14
set r14 91
print r14
set r14 35
print r14
set r14 114
print r14

mov r14 r12
div r14 100
add r14 48
print r14
mov r14 r12
div r14 10
mod r14 10
add r14 48
print r14
mov r14 r12
mod r14 10
add r14 48
print r14
set r14 93
print r14
set r14 46
print r14

jmp mr_finish
label mr_ack
load8 r0 7400000000000000003
cmp r0 2
je mr_ack_en
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
set r14 195
print r14
set r14 169
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
set r14 114
print r14
set r14 101
print r14
set r14 108
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
set r14 46
print r14
jmp mr_finish
label mr_ack_en
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
set r14 114
print r14
set r14 101
print r14
set r14 108
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
jmp mr_finish
label mr_unknown
load8 r0 7400000000000000003
cmp r0 2
je mr_unknown_en
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
set r14 97
print r14
set r14 32
print r14
set r14 114
print r14
set r14 101
print r14
set r14 108
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
set r14 46
print r14
jmp mr_finish
label mr_unknown_en
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
set r14 114
print r14
set r14 101
print r14
set r14 108
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
jmp mr_finish
label mr_conflict
load8 r0 7400000000000000003
cmp r0 2
je mr_conflict_en
set r14 72
print r14
set r14 97
print r14
set r14 121
print r14
set r14 32
print r14
set r14 100
print r14
set r14 97
print r14
set r14 116
print r14
set r14 111
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
set r14 111
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
set r14 97
print r14
set r14 32
print r14
set r14 114
print r14
set r14 101
print r14
set r14 108
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
set r14 46
print r14
jmp mr_finish
label mr_conflict_en
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
set r14 105
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
set r14 114
print r14
set r14 101
print r14
set r14 108
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
jmp mr_finish
label mr_ambiguous
load8 r0 7400000000000000003
cmp r0 2
je mr_ambiguous_en
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
set r14 100
print r14
set r14 101
print r14
set r14 32
print r14
set r14 114
print r14
set r14 101
print r14
set r14 108
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
jmp mr_finish
label mr_ambiguous_en
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
set r14 114
print r14
set r14 101
print r14
set r14 108
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
jmp mr_finish
label mr_capacity
load8 r0 7400000000000000003
cmp r0 2
je mr_capacity_en
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
set r14 100
print r14
set r14 101
print r14
set r14 32
print r14
set r14 114
print r14
set r14 101
print r14
set r14 108
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
set r14 195
print r14
set r14 169
print r14
set r14 32
print r14
set r14 99
print r14
set r14 97
print r14
set r14 109
print r14
set r14 98
print r14
set r14 105
print r14
set r14 111
print r14
set r14 115
print r14
set r14 46
print r14
jmp mr_finish
label mr_capacity_en
set r14 82
print r14
set r14 101
print r14
set r14 108
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
set r14 102
print r14
set r14 117
print r14
set r14 108
print r14
set r14 108
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
set r14 99
print r14
set r14 104
print r14
set r14 97
print r14
set r14 110
print r14
set r14 103
print r14
set r14 101
print r14
set r14 115
print r14
set r14 32
print r14
set r14 119
print r14
set r14 101
print r14
set r14 114
print r14
set r14 101
print r14
set r14 32
print r14
set r14 115
print r14
set r14 97
print r14
set r14 118
print r14
set r14 101
print r14
set r14 100
print r14
set r14 46
print r14
jmp mr_finish
label mr_finish
set r0 16
label mr_clean
set r7 8500000000000000000
add r7 r0
store8 $r7 0
add r0 1
cmp r0 1024
jlt mr_clean
halt
label mr_delegate
set r0 16
label mr_clean_delegate
set r7 8500000000000000000
add r7 r0
store8 $r7 0
add r0 1
cmp r0 1024
jlt mr_clean_delegate
jmp mr_parent_entry
label mr_commands
cmp r9 12
jlt mr_frames_start
load8 r0 8500000000000000128
cmp r0 64
jne mr_frames_start
load8 r0 8500000000000000129
cmp r0 114
jne mr_frames_start
load8 r0 8500000000000000130
cmp r0 101
jne mr_frames_start
load8 r0 8500000000000000131
cmp r0 108
jne mr_frames_start
load8 r0 8500000000000000132
cmp r0 32
jne mr_frames_start
load8 r0 8500000000000000133
cmp r0 115
jne mr_frames_start
load8 r0 8500000000000000134
cmp r0 111
jne mr_frames_start
load8 r0 8500000000000000135
cmp r0 117
jne mr_frames_start
load8 r0 8500000000000000136
cmp r0 114
jne mr_frames_start
load8 r0 8500000000000000137
cmp r0 99
jne mr_frames_start
load8 r0 8500000000000000138
cmp r0 101
jne mr_frames_start
load8 r0 8500000000000000139
cmp r0 32
jne mr_frames_start
cmp r9 12
jle mr_unknown
cmp r9 15
jgt mr_unknown
set r0 12
set r12 0
label mr_source_digits
cmp r0 r9
jge mr_source_index
set r7 8500000000000000128
add r7 r0
load8 r3 $r7
cmp r3 48
jlt mr_unknown
cmp r3 57
jgt mr_unknown
sub r3 48
mul r12 10
add r12 r3
add r0 1
jmp mr_source_digits
label mr_source_index
cmp r12 1
jlt mr_unknown
load8 r0 8500000000000000003
cmp r12 r0
jgt mr_unknown
mov r0 r12
sub r0 1
mul r0 8
set r15 8500000000000070000
add r15 r0
load8 r3 $r15
store8 8500000000000000050 r3
mov r7 r15
add r7 2
load8 r3 $r7
store8 8500000000000000051 r3
add r7 1
load8 r3 $r7
store8 8500000000000000052 r3
add r7 1
load8 r13 $r7
set r14 35
print r14
set r14 114
print r14
mov r14 r12
div r14 100
add r14 48
print r14
mov r14 r12
div r14 10
mod r14 10
add r14 48
print r14
mov r14 r12
mod r14 10
add r14 48
print r14
set r14 32
print r14
set r14 60
print r14
set r14 45
print r14
set r14 114
print r14
mov r14 r13
div r14 100
add r14 48
print r14
mov r14 r13
div r14 10
mod r14 10
add r14 48
print r14
mov r14 r13
mod r14 10
add r14 48
print r14
set r14 32
print r14

load8 r0 8500000000000000052
sub r0 1
mul r0 256
set r15 8500000000000004096
add r15 r0
mov r7 r15
add r7 5
load8 r8 $r7
add r15 144

set r0 0
label mr_source_prefix
cmp r0 r8
jge mr_source_prefix_done
mov r7 r15
add r7 r0
load8 r14 $r7
print r14
add r0 1
jmp mr_source_prefix
label mr_source_prefix_done
load8 r0 8500000000000000050
sub r0 1
mul r0 64
set r15 8500000000000032768
add r15 r0
load8 r8 $r15
add r15 1
set r0 0
label mr_source_subject
cmp r0 r8
jge mr_source_subject_done
mov r7 r15
add r7 r0
load8 r14 $r7
print r14
add r0 1
jmp mr_source_subject
label mr_source_subject_done
load8 r0 8500000000000000052
sub r0 1
mul r0 256
set r15 8500000000000004096
add r15 r0
mov r7 r15
add r7 6
load8 r8 $r7
add r15 192

set r0 0
label mr_source_middle
cmp r0 r8
jge mr_source_middle_done
mov r7 r15
add r7 r0
load8 r14 $r7
print r14
add r0 1
jmp mr_source_middle
label mr_source_middle_done
load8 r0 8500000000000000051
sub r0 1
mul r0 96
set r15 8500000000000049152
add r15 r0
load8 r8 $r15
add r15 1
set r0 0
label mr_source_value
cmp r0 r8
jge mr_source_value_done
mov r7 r15
add r7 r0
load8 r14 $r7
print r14
add r0 1
jmp mr_source_value
label mr_source_value_done
load8 r0 8500000000000000052
sub r0 1
mul r0 256
set r15 8500000000000004096
add r15 r0
mov r7 r15
add r7 7
load8 r8 $r7
add r15 240

set r0 0
label mr_source_suffix
cmp r0 r8
jge mr_source_suffix_done
mov r7 r15
add r7 r0
load8 r14 $r7
print r14
add r0 1
jmp mr_source_suffix
label mr_source_suffix_done
jmp mr_finish
