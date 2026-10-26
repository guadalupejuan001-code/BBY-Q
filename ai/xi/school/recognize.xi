#!reverse-pc-machine-v1
# E010 XI classifier: domain-scoped nearest grounded exemplar.
# Input +100=2, +101=domain, +102..104=observable features.
# The model sees NO test label and does NOT inspect +300 grading feedback.
load8 r12 7200000000000000000
cmp r12 83
je schema_ok
div r12 0
label schema_ok
load8 r12 7200000000000000100
cmp r12 2
je query_ready
div r12 0
label query_ready
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
load8 r11 7200000000000000010
set r7 99999
set r10 99999
set r8 0
set r0 0
label compare_exemplar
cmp r0 r11
jge select_predicted_concept
set r5 7200000000000001000
mov r12 r0
mul r12 32
add r5 r12
load8 r13 $r5
cmp r13 r6
jne next_exemplar
mov r12 r5
add r12 4
load8 r13 $r12
cmp r13 2
jlt next_exemplar
set r9 0
mov r12 r5
add r12 1
load8 r13 $r12
mov r14 r2
sub r14 r13
cmp r14 0
jge dx_positive
mul r14 -1
label dx_positive
add r9 r14
mov r12 r5
add r12 2
load8 r13 $r12
mov r14 r3
sub r14 r13
cmp r14 0
jge dy_positive
mul r14 -1
label dy_positive
add r9 r14
mov r12 r5
add r12 3
load8 r13 $r12
mov r14 r4
sub r14 r13
cmp r14 0
jge dz_positive
mul r14 -1
label dz_positive
add r9 r14
cmp r9 r7
jge not_better_exemplar
mov r10 r7
mov r7 r9
mov r8 r0
add r8 1
jmp next_exemplar
label not_better_exemplar
cmp r9 r10
jge next_exemplar
mov r10 r9
label next_exemplar
add r0 1
jmp compare_exemplar
label select_predicted_concept
set r14 0
cmp r8 0
je undecidable
cmp r7 r10
je undecidable
cmp r6 1
je color_tolerance
cmp r7 0
jne undecidable
jmp sufficient_evidence
label color_tolerance
cmp r7 85
jgt undecidable
# Margin protects nearest class under ambiguous RGB values.
mov r12 r10
sub r12 r7
cmp r12 30
jlt undecidable
label sufficient_evidence
set r14 1
jmp persist_prediction
label undecidable
set r8 0
label persist_prediction
store8 7200000000000000200 r8
store8 7200000000000000201 r14
store8 7200000000000000203 r6
cmp r7 255
jle distance_in_byte
set r7 255
label distance_in_byte
store8 7200000000000000202 r7
# Erase temporary observation, not trained prototypes.
set r0 0
label erase_query
set r12 7200000000000000100
add r12 r0
store8 $r12 0
add r0 1
cmp r0 5
jlt erase_query
print r14
print r8
print r7
mem_stats
stats
