#!reverse-pc-machine-v1
# E010 owner's XI: learn paired ES/EN names from observed feature vectors.
# One model, no preloaded categories or color tables, one RVPC2 authority.
load8 r15 7200000000000000000
cmp r15 83
je right_schema
div r15 0
label right_schema
load8 r15 7200000000000000100
cmp r15 1
je lesson_present
div r15 0
label lesson_present
load8 r6 7200000000000000101
cmp r6 1
jge domain_low
div r6 0
label domain_low
cmp r6 4
jle domain_high
div r6 0
label domain_high
load8 r2 7200000000000000102
load8 r3 7200000000000000103
load8 r4 7200000000000000104
load8 r9 7200000000000000105
load8 r10 7200000000000000115
cmp r9 1
jge eslen_low
div r9 0
label eslen_low
cmp r9 8
jle eslen_high
div r9 0
label eslen_high
cmp r10 1
jge enlen_low
div r10 0
label enlen_low
cmp r10 8
jle enlen_high
div r10 0
label enlen_high
# Validate both names as ASCII alphabetic observations.
set r11 0
label validate_es
cmp r11 r9
jge validate_en_start
set r12 7200000000000000106
add r12 r11
load8 r13 $r12
cmp r13 97
jge lowercase_es_low
div r13 0
label lowercase_es_low
cmp r13 122
jle lowercase_es_high
div r13 0
label lowercase_es_high
add r11 1
jmp validate_es
label validate_en_start
set r11 0
label validate_en
cmp r11 r10
jge find_matching_observation
set r12 7200000000000000116
add r12 r11
load8 r13 $r12
cmp r13 97
jge lowercase_en_low
div r13 0
label lowercase_en_low
cmp r13 122
jle lowercase_en_high
div r13 0
label lowercase_en_high
add r11 1
jmp validate_en
label find_matching_observation
load8 r7 7200000000000000010
set r0 0
label scan_prototypes
cmp r0 r7
jge allocate_prototype
set r8 7200000000000001000
mov r12 r0
mul r12 32
add r8 r12
load8 r13 $r8
cmp r13 r6
jne next_prototype
mov r12 r8
add r12 1
load8 r13 $r12
cmp r13 r2
jne next_prototype
mov r12 r8
add r12 2
load8 r13 $r12
cmp r13 r3
jne next_prototype
mov r12 r8
add r12 3
load8 r13 $r12
cmp r13 r4
jne next_prototype
# Same physical exemplar must never be silently renamed.
mov r12 r8
add r12 5
load8 r13 $r12
cmp r13 r9
jne conflicting_grounding
mov r12 r8
add r12 14
load8 r13 $r12
cmp r13 r10
jne conflicting_grounding
set r11 0
label check_es_spelling
cmp r11 r9
jge check_en_start
set r12 7200000000000000106
add r12 r11
load8 r13 $r12
mov r14 r8
add r14 r11
add r14 6
load8 r15 $r14
cmp r13 r15
jne conflicting_grounding
add r11 1
jmp check_es_spelling
label check_en_start
set r11 0
label check_en_spelling
cmp r11 r10
jge reinforce_prototype
set r12 7200000000000000116
add r12 r11
load8 r13 $r12
mov r14 r8
add r14 r11
add r14 15
load8 r15 $r14
cmp r13 r15
jne conflicting_grounding
add r11 1
jmp check_en_spelling
label conflicting_grounding
div r0 0
label reinforce_prototype
mov r12 r8
add r12 4
load8 r13 $r12
cmp r13 200
jge clear_lesson
add r13 1
store8 $r12 r13
jmp clear_lesson
label next_prototype
add r0 1
jmp scan_prototypes
label allocate_prototype
cmp r7 32
jlt space_available
div r7 0
label space_available
set r8 7200000000000001000
mov r12 r7
mul r12 32
add r8 r12
store8 $r8 r6
mov r12 r8
add r12 1
store8 $r12 r2
mov r12 r8
add r12 2
store8 $r12 r3
mov r12 r8
add r12 3
store8 $r12 r4
mov r12 r8
add r12 4
store8 $r12 1
mov r12 r8
add r12 5
store8 $r12 r9
mov r12 r8
add r12 14
store8 $r12 r10
set r11 0
label copy_es_spelling
cmp r11 r9
jge start_copy_en
set r12 7200000000000000106
add r12 r11
load8 r13 $r12
mov r14 r8
add r14 r11
add r14 6
store8 $r14 r13
add r11 1
jmp copy_es_spelling
label start_copy_en
set r11 0
label copy_en_spelling
cmp r11 r10
jge new_observation_recorded
set r12 7200000000000000116
add r12 r11
load8 r13 $r12
mov r14 r8
add r14 r11
add r14 15
store8 $r14 r13
add r11 1
jmp copy_en_spelling
label new_observation_recorded
add r7 1
store8 7200000000000000010 r7
label clear_lesson
load8 r13 7200000000000000011
cmp r13 250
jge total_limit
add r13 1
store8 7200000000000000011 r13
label total_limit
set r0 0
label erase_training_input
set r12 7200000000000000100
add r12 r0
store8 $r12 0
add r0 1
cmp r0 24
jlt erase_training_input
load8 r14 7200000000000000010
print r14
load8 r14 7200000000000000011
print r14
mem_stats
stats
