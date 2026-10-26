#!reverse-pc-machine-v1
# E009 semantic question in XI. Three grounded ASCII words in the intake.
# Answer statuses: 0=unknown, 1=supported, 2=counterevidence.
# For supported inference return an evidence witness (intermediate concept).
load8 r14 7100000000000000002
cmp r14 1
je schema_ok
div r14 0
label schema_ok
load8 r14 7100000000000000175
cmp r14 3
je question_ready
div r14 0
label question_ready
set r15 0
label resolve_next_query_word
set r7 7100000000000000140
mov r8 r15
mul r8 10
add r7 r8
load8 r2 $r7
cmp r2 1
jlt unknown_word
cmp r2 8
jgt unknown_word
load8 r5 7100000000000000016
set r0 0
label scan_word_memory
cmp r0 r5
jge unknown_word
set r4 7100000000000001000
mov r8 r0
mul r8 16
add r4 r8
load8 r9 $r4
cmp r9 r2
jne next_word
set r1 0
label compare_letters
cmp r1 r2
jge lexeme_resolved
mov r8 r7
add r8 r1
add r8 1
load8 r9 $r8
mov r10 r4
add r10 r1
add r10 2
load8 r11 $r10
cmp r9 r11
jne next_word
add r1 1
jmp compare_letters
label lexeme_resolved
mov r8 r4
add r8 1
load8 r3 $r8
set r8 7100000000000000180
add r8 r15
store8 $r8 r3
add r15 1
cmp r15 3
jlt resolve_next_query_word
jmp all_words_found
label next_word
add r0 1
jmp scan_word_memory
label unknown_word
set r2 0
set r3 0
set r4 0
set r6 0
set r10 0
set r11 0
jmp commit_result
label all_words_found
load8 r2 7100000000000000180
load8 r3 7100000000000000181
load8 r4 7100000000000000182
set r10 0
set r11 0
set r6 0
load8 r5 7100000000000000018
set r0 0
label direct_fact_lookup
cmp r0 r5
jge try_composition
set r7 7100000000000003000
mov r8 r0
mul r8 8
add r7 r8
load8 r9 $r7
cmp r9 r2
jne next_direct
add r7 1
load8 r9 $r7
cmp r9 r3
jne next_direct
add r7 1
load8 r9 $r7
cmp r9 r4
jne next_direct
# An explicitly observed negative fact beats a hypothetical composition.
add r7 1
load8 r12 $r7
add r7 1
load8 r13 $r7
cmp r13 2
jlt positive_evidence
cmp r13 r12
jlt positive_evidence
set r10 2
set r11 1
jmp commit_result
label positive_evidence
cmp r12 2
jlt commit_result
cmp r12 r13
jle commit_result
set r10 1
set r11 1
jmp commit_result
label next_direct
add r0 1
jmp direct_fact_lookup
label try_composition
set r7 7100000000000002000
add r7 r3
load8 r9 $r7
cmp r9 1
jne commit_result
# Transitive two-hop proof: (S,R,W) and (W,R,O), with grounded edges.
set r0 0
label first_proven_edge
cmp r0 r5
jge commit_result
set r7 7100000000000003000
mov r8 r0
mul r8 8
add r7 r8
load8 r9 $r7
cmp r9 r2
jne next_first_edge
add r7 1
load8 r9 $r7
cmp r9 r3
jne next_first_edge
add r7 1
load8 r6 $r7
add r7 1
load8 r12 $r7
cmp r12 2
jlt next_first_edge
add r7 1
load8 r13 $r7
cmp r12 r13
jle next_first_edge
set r1 0
label second_proven_edge
cmp r1 r5
jge next_first_edge
set r7 7100000000000003000
mov r8 r1
mul r8 8
add r7 r8
load8 r9 $r7
cmp r9 r6
jne next_second_edge
add r7 1
load8 r9 $r7
cmp r9 r3
jne next_second_edge
add r7 1
load8 r9 $r7
cmp r9 r4
jne next_second_edge
add r7 1
load8 r12 $r7
cmp r12 2
jlt next_second_edge
add r7 1
load8 r13 $r7
cmp r12 r13
jle next_second_edge
set r10 1
set r11 2
jmp commit_result
label next_second_edge
add r1 1
jmp second_proven_edge
label next_first_edge
add r0 1
jmp first_proven_edge
label commit_result
# The utterance is assembled LATER from these concept IDs, not a reply table.
store8 7100000000000000190 r10
store8 7100000000000000191 r2
store8 7100000000000000192 r3
store8 7100000000000000193 r4
store8 7100000000000000194 r6
store8 7100000000000000195 r11
set r0 0
label erase_query_intake
set r7 7100000000000000140
add r7 r0
store8 $r7 0
add r0 1
cmp r0 29
jlt erase_query_intake
store8 7100000000000000170 0
store8 7100000000000000175 0
set r0 0
label erase_resolution_scratch
set r7 7100000000000000180
add r7 r0
store8 $r7 0
add r0 1
cmp r0 3
jlt erase_resolution_scratch
load8 r12 7100000000000000196
cmp r12 250
jge count_queries_done
add r12 1
store8 7100000000000000196 r12
label count_queries_done
print r10
print r11
print r6
mem_stats
stats
