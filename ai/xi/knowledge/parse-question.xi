#!reverse-pc-machine-v1
# Microgrammar uses learned roles, not literal Spanish/English question words:
# SUBJECT PREDICATE OBJECT? or QUESTION PREDICATE SUBJECT?
store8 7400000000000000008 0
store8 7400000000000000009 0
store8 7400000000000000010 0
store8 7400000000000000011 0
store8 7400000000000000012 0
store8 7400000000000000013 0
store8 7400000000000000014 0
store8 7400000000000000015 0
set r0 0
label clear_answers
set r7 7400000000000002100
add r7 r0
store8 $r7 0
add r0 1
cmp r0 8
jlt clear_answers
set r0 0
label clear_proof
set r7 7400000000000002200
add r7 r0
store8 $r7 0
add r0 1
cmp r0 32
jlt clear_proof
load8 r0 7400000000000000040
cmp r0 0
jne grammar_error
load8 r0 7400000000000000032
cmp r0 3
jne grammar_error
load8 r0 7400000000000001603
cmp r0 2
jne grammar_error
load8 r3 7400000000000001602
store8 7400000000000000011 r3
load8 r0 7400000000000001601
cmp r0 3
je object_question
store8 7400000000000000013 1
load8 r2 7400000000000001600
load8 r4 7400000000000001604
store8 7400000000000000010 r2
store8 7400000000000000012 r4
cmp r2 0
je unknown
cmp r4 0
je unknown
load8 r0 7400000000000001605
cmp r0 3
je grammar_error
halt
label object_question
store8 7400000000000000013 2
load8 r2 7400000000000001604
store8 7400000000000000010 r2
cmp r2 0
je unknown
load8 r0 7400000000000001605
cmp r0 3
je grammar_error
halt
label unknown
store8 7400000000000000009 1
halt
label grammar_error
store8 7400000000000000009 2
halt
