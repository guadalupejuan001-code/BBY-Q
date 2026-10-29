#!reverse-pc-machine-v1
# Supervised one-subject question frames. Roles are raw query + subject, language
# and intent=1 (definition AND requirement). XI finds the span and infers literals.
# T+16 language, +17 query bytes, +18 subject bytes, +19 construction ID 1..8,
# +20 intent. +128 query, +400 subject. Only an explicit native teaching session.
# Records T+1024+i*256: witnesses/lang/prefixlen/suffixlen/firstlen/intent,
# +16 first subject, +48 prefix(80), +128 suffix(80), +208 second subject.
load8 r14 9200000000000000016
cmp r14 1
jlt lf_invalid
cmp r14 2
jgt lf_invalid
load8 r9 9200000000000000017
load8 r13 9200000000000000018
cmp r9 3
jlt lf_invalid
cmp r13 1
jlt lf_invalid
cmp r13 31
jgt lf_invalid
load8 r0 9200000000000000019
cmp r0 1
jlt lf_invalid
cmp r0 8
jgt lf_invalid
sub r0 1
mul r0 256
set r15 9200000000000001024
add r15 r0
load8 r0 9200000000000000020
cmp r0 1
jne lf_invalid
# Validate raw text, so only one ASCII subject slot can be generalized.
set r0 0
label lf_query_ascii
cmp r0 r9
jge lf_subject_ascii_start
set r7 9200000000000000128
add r7 r0
load8 r3 $r7
cmp r3 32
je lf_query_ascii_next
cmp r3 48
jlt lf_invalid
cmp r3 57
jle lf_query_ascii_next
cmp r3 97
jlt lf_invalid
cmp r3 122
jgt lf_invalid
label lf_query_ascii_next
add r0 1
jmp lf_query_ascii
label lf_subject_ascii_start
set r0 0
label lf_subject_ascii
cmp r0 r13
jge lf_search_start
set r7 9200000000000000400
add r7 r0
load8 r3 $r7
cmp r3 48
jlt lf_invalid
cmp r3 57
jle lf_subject_ascii_next
cmp r3 97
jlt lf_invalid
cmp r3 122
jgt lf_invalid
label lf_subject_ascii_next
add r0 1
jmp lf_subject_ascii
label lf_search_start
set r0 0
set r10 0
label lf_search
mov r1 r0
add r1 r13
cmp r1 r9
jgt lf_found
set r2 0
label lf_search_char
cmp r2 r13
jge lf_boundary
set r7 9200000000000000128
add r7 r0
add r7 r2
load8 r3 $r7
set r7 9200000000000000400
add r7 r2
load8 r4 $r7
cmp r3 r4
jne lf_search_next
add r2 1
jmp lf_search_char
label lf_boundary
cmp r0 0
je lf_search_next
set r7 9200000000000000127
add r7 r0
load8 r3 $r7
cmp r3 32
jne lf_search_next
mov r7 r0
add r7 r13
cmp r7 r9
jge lf_search_next
add r7 9200000000000000128
load8 r3 $r7
cmp r3 32
jne lf_search_next
add r10 1
mov r11 r0
label lf_search_next
add r0 1
jmp lf_search
label lf_found
cmp r10 1
jne lf_invalid
cmp r11 1
jlt lf_invalid
cmp r11 80
jgt lf_invalid
mov r12 r9
sub r12 r11
sub r12 r13
cmp r12 1
jlt lf_invalid
cmp r12 80
jgt lf_invalid
load8 r0 $r15
cmp r0 0
je lf_allocate
cmp r0 1
jne lf_invalid
mov r7 r15
add r7 1
load8 r0 $r7
cmp r0 r14
jne lf_invalid
add r7 1
load8 r0 $r7
cmp r0 r11
jne lf_invalid
add r7 1
load8 r0 $r7
cmp r0 r12
jne lf_invalid
# Validate BOTH literal sides completely before mutating the pending record.
set r0 0
label lf_compare_prefix
cmp r0 r11
jge lf_compare_suffix_start
mov r7 r15
add r7 48
add r7 r0
load8 r3 $r7
set r7 9200000000000000128
add r7 r0
load8 r4 $r7
cmp r3 r4
jne lf_invalid
add r0 1
jmp lf_compare_prefix
label lf_compare_suffix_start
set r0 0
label lf_compare_suffix
cmp r0 r12
jge lf_distinct
mov r7 r15
add r7 128
add r7 r0
load8 r3 $r7
set r7 9200000000000000128
add r7 r11
add r7 r13
add r7 r0
load8 r4 $r7
cmp r3 r4
jne lf_invalid
add r0 1
jmp lf_compare_suffix
label lf_distinct
mov r7 r15
add r7 4
load8 r0 $r7
cmp r0 r13
jne lf_promote
set r0 0
label lf_compare_subject
cmp r0 r13
jge lf_clean
mov r7 r15
add r7 16
add r7 r0
load8 r3 $r7
set r7 9200000000000000400
add r7 r0
load8 r4 $r7
cmp r3 r4
jne lf_promote
add r0 1
jmp lf_compare_subject
label lf_allocate
store8 9200000000000000000 1
store8 $r15 1
mov r7 r15
add r7 1
store8 $r7 r14
add r7 1
store8 $r7 r11
add r7 1
store8 $r7 r12
add r7 1
store8 $r7 r13
add r7 1
store8 $r7 1
set r0 0
label lf_copy_first
cmp r0 r13
jge lf_copy_prefix_start
set r7 9200000000000000400
add r7 r0
load8 r3 $r7
mov r7 r15
add r7 16
add r7 r0
store8 $r7 r3
add r0 1
jmp lf_copy_first
label lf_copy_prefix_start
set r0 0
label lf_copy_prefix
cmp r0 r11
jge lf_copy_suffix_start
set r7 9200000000000000128
add r7 r0
load8 r3 $r7
mov r7 r15
add r7 48
add r7 r0
store8 $r7 r3
add r0 1
jmp lf_copy_prefix
label lf_copy_suffix_start
set r0 0
label lf_copy_suffix
cmp r0 r12
jge lf_clean
set r7 9200000000000000128
add r7 r11
add r7 r13
add r7 r0
load8 r3 $r7
mov r7 r15
add r7 128
add r7 r0
store8 $r7 r3
add r0 1
jmp lf_copy_suffix
label lf_promote
# Distinct witness, same intent and literal context: enable the subject slot.
store8 $r15 2
set r0 0
label lf_copy_second
cmp r0 r13
jge lf_clean
set r7 9200000000000000400
add r7 r0
load8 r3 $r7
mov r7 r15
add r7 208
add r7 r0
store8 $r7 r3
add r0 1
jmp lf_copy_second
label lf_clean
set r0 16
label lf_clean_mailbox
set r7 9200000000000000000
add r7 r0
store8 $r7 0
add r0 1
cmp r0 1024
jlt lf_clean_mailbox
halt
label lf_invalid
div r0 0
