#!reverse-pc-machine-v1
# Construct clauses and labeled proof paths from actual semantic results.
# +300 stage,+301 answer index,+302 dispatch (1 name,2 bytes,3 act,0 done).
load8 r0 7800000000000000309
cmp r0 1
je proof
load8 r0 7800000000000000300
cmp r0 0
je subject_article
cmp r0 1
je subject
cmp r0 2
je spanish_negative
cmp r0 3
je predicate
cmp r0 4
je english_negative
cmp r0 5
je object_article
cmp r0 6
je object
jmp triple_done
label subject_article
store8 7800000000000000300 1
load8 r2 7800000000000000072
load8 r14 7800000000000000073
mul r14 256
add r2 r14
jmp article
label subject
store8 7800000000000000300 2
load8 r2 7800000000000000072
load8 r14 7800000000000000073
mul r14 256
add r2 r14
jmp name
label spanish_negative
store8 7800000000000000300 3
load8 r0 7800000000000000138
cmp r0 2
je predicate
load8 r0 7800000000000000080
cmp r0 2
jne predicate
load8 r0 7400000000000000003
cmp r0 1
je negative_word
load8 r0 7800000000000000139
cmp r0 1
jne predicate
store8 7800000000000000304 13
store8 7800000000000000302 3
halt
jmp predicate
label predicate
store8 7800000000000000300 4
load8 r2 7800000000000000074
load8 r14 7800000000000000075
mul r14 256
add r2 r14
load8 r0 7800000000000000139
cmp r0 1
jne name
set r7 7800000000009000000
mov r0 r2
mul r0 34
add r7 r0
load8 r6 $r7
add r7 1
load8 r13 7700000000000000038
store8 7800000000000000302 2
halt
jmp name
label english_negative
store8 7800000000000000300 5
load8 r0 7800000000000000080
cmp r0 2
jne object_article
load8 r0 7400000000000000003
cmp r0 2
jne object_article
load8 r0 7800000000000000074
load8 r14 7800000000000000075
mul r14 256
add r0 r14
load8 r1 7800000000000000032
load8 r14 7800000000000000033
mul r14 256
add r1 r14
cmp r0 r1
je negative_word
jmp object_article
label negative_word
store8 7800000000000000304 10
store8 7800000000000000302 3
halt
label object_article
store8 7800000000000000300 6
load8 r0 7800000000000000301
set r7 7800000000008300000
mul r0 2
add r7 r0
mov r15 r7
load8 r2 $r15
add r15 1
load8 r14 $r15
mul r14 256
add r2 r14
jmp article
label object
store8 7800000000000000300 7
load8 r0 7800000000000000301
set r7 7800000000008300000
mul r0 2
add r7 r0
mov r15 r7
load8 r2 $r15
add r15 1
load8 r14 $r15
mul r14 256
add r2 r14
jmp name
label article
load8 r0 7800000000000000063
cmp r0 1
jne no_article
load8 r0 7800000000000000074
load8 r14 7800000000000000075
mul r14 256
add r0 r14
load8 r1 7800000000000000032
load8 r14 7800000000000000033
mul r14 256
add r1 r14
cmp r0 r1
jne no_article
cmp r2 255
jgt no_article
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
store8 7800000000000000302 2
halt
label no_article
load8 r0 7800000000000000300
cmp r0 1
je subject
jmp object
label name
mov r14 r2
mod r14 256
store8 7800000000000000306 r14
mov r14 r2
div r14 256
store8 7800000000000000307 r14
store8 7800000000000000302 1
halt
label triple_done
load8 r0 7800000000000000301
add r0 1
load8 r1 7800000000000000082
cmp r0 r1
jge response_done
store8 7800000000000000301 r0
store8 7800000000000000300 0
store8 7700000000000000038 0
store8 7700000000000000039 0
set r14 59
print r14
set r14 32
print r14
jmp subject_article
label response_done
set r14 46
print r14
load8 r0 7800000000000000121
cmp r0 2
jlt done
sub r0 1
store8 7800000000000000311 r0
store8 7800000000000000309 1
store8 7700000000000000038 0
store8 7700000000000000039 0
set r14 32
print r14
set r14 91
print r14
label proof
load8 r0 7800000000000000310
cmp r0 0
je proof_node
cmp r0 2
je after_predicate
load8 r0 7800000000000000311
cmp r0 0
je proof_done
sub r0 1
store8 7800000000000000311 r0
set r7 7800000000008200002
mul r0 4
add r7 r0
mov r15 r7
load8 r2 $r15
add r15 1
load8 r14 $r15
mul r14 256
add r2 r14
store8 7800000000000000310 2
store8 7700000000000000039 0
set r14 32
print r14
set r14 45
print r14
print r14
jmp name
label after_predicate
store8 7700000000000000039 0
set r14 45
print r14
print r14
set r14 62
print r14
set r14 32
print r14
label proof_node
load8 r0 7800000000000000311
set r7 7800000000008200000
mul r0 4
add r7 r0
mov r15 r7
load8 r2 $r15
add r15 1
load8 r14 $r15
mul r14 256
add r2 r14
store8 7800000000000000310 1
jmp name
label proof_done
set r14 93
print r14
label done
store8 7800000000000000302 0
halt
