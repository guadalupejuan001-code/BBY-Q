#!reverse-pc-machine-v1
# E009: infer whether ANY learned relation is transitive from observed
# two-link paths plus positive/negative DIRECT counterexamples.
# No predicate names, English rules or Spanish outputs are hardcoded.
load8 r14 7100000000000000002
cmp r14 1
je schema_ok
div r14 0
label schema_ok
load8 r3 7100000000000000018
cmp r3 25
jlt work_bounded
div r3 0
label work_bounded
set r0 1
label reset_predicate_evidence
set r13 7100000000000002000
add r13 r0
store8 $r13 0
set r13 7100000000000002100
add r13 r0
store8 $r13 0
set r13 7100000000000002150
add r13 r0
store8 $r13 0
add r0 1
load8 r14 7100000000000000017
cmp r0 r14
jle reset_predicate_evidence
set r0 0
label scan_first_edge
cmp r0 r3
jge infer_predicates
set r13 7100000000000003000
mov r14 r0
mul r14 8
add r13 r14
load8 r4 $r13
add r13 1
load8 r5 $r13
add r13 1
load8 r6 $r13
add r13 1
load8 r14 $r13
cmp r14 2
jlt next_first
add r13 1
load8 r15 $r13
cmp r15 r14
jge next_first
set r1 0
label scan_second_edge
cmp r1 r3
jge next_first
set r13 7100000000000003000
mov r14 r1
mul r14 8
add r13 r14
load8 r7 $r13
cmp r7 r6
jne next_second
add r13 1
load8 r8 $r13
cmp r8 r5
jne next_second
add r13 1
load8 r9 $r13
cmp r9 r4
je next_second
add r13 1
load8 r14 $r13
cmp r14 2
jlt next_second
add r13 1
load8 r15 $r13
cmp r15 r14
jge next_second
set r2 0
label scan_observed_conclusion
cmp r2 r3
jge next_second
set r13 7100000000000003000
mov r14 r2
mul r14 8
add r13 r14
load8 r10 $r13
cmp r10 r4
jne next_conclusion
add r13 1
load8 r11 $r13
cmp r11 r5
jne next_conclusion
add r13 1
load8 r12 $r13
cmp r12 r9
jne next_conclusion
add r13 1
load8 r14 $r13
add r13 1
load8 r15 $r13
# Contradiction in ANY fully grounded path vetoes transitivity.
cmp r15 2
jlt evaluate_supported
cmp r15 r14
jlt evaluate_supported
set r13 7100000000000002150
add r13 r5
load8 r14 $r13
cmp r14 200
jge example_evaluated
add r14 1
store8 $r13 r14
jmp example_evaluated
label evaluate_supported
cmp r14 2
jlt example_evaluated
cmp r14 r15
jle example_evaluated
set r13 7100000000000002100
add r13 r5
load8 r14 $r13
cmp r14 200
jge example_evaluated
add r14 1
store8 $r13 r14
label example_evaluated
jmp next_second
label next_conclusion
add r2 1
jmp scan_observed_conclusion
label next_second
add r1 1
jmp scan_second_edge
label next_first
add r0 1
jmp scan_first_edge
label infer_predicates
set r0 1
set r11 0
label evaluate_each_relation
load8 r14 7100000000000000017
cmp r0 r14
jgt consolidation_done
set r13 7100000000000002100
add r13 r0
load8 r12 $r13
cmp r12 2
jlt no_transitivity
set r13 7100000000000002150
add r13 r0
load8 r12 $r13
cmp r12 0
jne no_transitivity
set r13 7100000000000002000
add r13 r0
store8 $r13 1
add r11 1
jmp next_predicate
label no_transitivity
set r13 7100000000000002000
add r13 r0
store8 $r13 0
label next_predicate
add r0 1
jmp evaluate_each_relation
label consolidation_done
print r11
mem_stats
stats
