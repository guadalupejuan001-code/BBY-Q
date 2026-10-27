#!reverse-pc-machine-v1
# Compose factual clauses from actual semantic results and taught articles.
# Retain the exact inference path; do not replace evidence with fluent prose.
# 7700000000000000032 answer index or proof cursor,+33 stage,+34 proof flag,+35 dispatch.
load8 r0 7700000000000000034
cmp r0 1
je proof
load8 r0 7700000000000000033
cmp r0 0
je subject_article
cmp r0 1
je subject
cmp r0 2
je predicate
cmp r0 3
je object_article
cmp r0 4
je object
jmp triple_done
label subject_article
store8 7700000000000000033 1
load8 r0 7400000000000000011
load8 r1 7700000000000000528
cmp r0 r1
jne subject
load8 r2 7400000000000000010
jmp article
label subject
store8 7700000000000000033 2
load8 r2 7400000000000000010
jmp name
label predicate
store8 7700000000000000033 3
load8 r2 7400000000000000011
jmp name
label object_article
store8 7700000000000000033 4
load8 r0 7400000000000000011
load8 r1 7700000000000000528
cmp r0 r1
jne object
load8 r0 7700000000000000032
set r7 7400000000000002100
add r7 r0
load8 r2 $r7
jmp article
label object
store8 7700000000000000033 5
load8 r0 7700000000000000032
set r7 7400000000000002100
add r7 r0
load8 r2 $r7
jmp name
label article
set r7 7700000000000100102
mov r0 r2
mul r0 224
add r7 r0
load8 r0 7400000000000000003
sub r0 1
mul r0 112
add r7 r0
load8 r6 $r7
cmp r6 0
je no_article
add r7 1
load8 r13 7700000000000000038
store8 7700000000000000035 2
halt
label no_article
load8 r0 7700000000000000033
cmp r0 1
je subject
jmp object
label name
store8 7700000000000000040 r2
store8 7700000000000000035 1
halt
label triple_done
load8 r0 7700000000000000032
add r0 1
load8 r1 7400000000000000014
cmp r0 r1
jge response_done
store8 7700000000000000032 r0
store8 7700000000000000033 0
load8 r2 7800000000000000003
cmp r2 1
jne full_clause
store8 7700000000000000033 3
store8 7700000000000000038 0
sub r1 1
cmp r0 r1
je conjunction
store8 7700000000000000039 0
set r14 44
print r14
set r14 32
print r14
jmp object_article
label conjunction
# Select the independently taught E018 conjunction, keeping every result.
set r7 7800000000000507168
load8 r0 7400000000000000003
sub r0 1
mul r0 256
add r7 r0
load8 r6 $r7
add r7 1
set r13 0
store8 7700000000000000035 2
halt
label full_clause
set r14 59
print r14
set r14 32
print r14
store8 7700000000000000039 0
store8 7700000000000000038 0
jmp subject_article
label response_done
set r14 46
print r14
# Only a checkpoint with the explicit E018 preference hides routine proofs.
load8 r0 7800000000000000003
cmp r0 1
jne show_proof
load8 r0 7800000000000000085
cmp r0 1
jne done
label show_proof
load8 r0 7400000000000000015
cmp r0 2
jlt done
store8 7700000000000000032 r0
store8 7700000000000000033 0
store8 7700000000000000034 1
store8 7700000000000000038 0
store8 7700000000000000039 0
set r14 32
print r14
set r14 91
print r14
label proof
load8 r0 7700000000000000033
cmp r0 0
je proof_name
load8 r0 7700000000000000032
cmp r0 0
je proof_done
sub r0 1
store8 7700000000000000032 r0
store8 7700000000000000039 0
set r14 32
print r14
set r14 45
print r14
set r14 62
print r14
set r14 32
print r14
label proof_name
load8 r0 7700000000000000032
set r7 7400000000000002200
add r7 r0
load8 r2 $r7
store8 7700000000000000033 1
jmp name
label proof_done
set r14 93
print r14
label done
store8 7700000000000000035 4
halt
