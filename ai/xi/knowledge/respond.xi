#!reverse-pc-machine-v1
# All content words come from the learned bilingual lexicon. No ready answers.
# Render factual triples and, for inference, the actual parent chain from BFS.
load8 r0 7400000000000000008
cmp r0 0
jne supported
set r14 63
print r14
halt
label supported
cmp r0 2
jne begin_response
set r14 110
print r14
set r14 111
print r14
set r14 58
print r14
set r14 32
print r14
label begin_response
set r0 0
set r1 0
set r12 0
label choose_word
cmp r12 1
je proof_word
cmp r1 0
je subject_word
cmp r1 1
je predicate_word
set r7 7400000000000002100
add r7 r0
load8 r2 $r7
jmp emit_word
label subject_word
load8 r2 7400000000000000010
jmp emit_word
label predicate_word
load8 r2 7400000000000000011
jmp emit_word
label proof_word
set r7 7400000000000002200
add r7 r1
load8 r2 $r7
label emit_word
load8 r15 7400000000000000003
cmp r2 22
jgt new_name
set r7 7200000000000001000
mov r3 r2
sub r3 1
mul r3 32
add r7 r3
set r3 5
cmp r15 1
je old_name
set r3 14
label old_name
add r7 r3
load8 r6 $r7
add r7 1
jmp letters_start
label new_name
load8 r10 7400000000000000004
load8 r3 7400000000000000005
mul r3 256
add r10 r3
set r3 0
label lexeme
cmp r3 r10
jge invalid
set r7 7400000000000010000
mov r4 r3
mul r4 40
add r7 r4
load8 r4 $r7
cmp r4 r2
jne next_lexeme
mov r4 r7
add r4 2
load8 r5 $r4
cmp r5 r15
jne next_lexeme
add r7 3
load8 r6 $r7
add r7 1
jmp letters_start
label next_lexeme
add r3 1
jmp lexeme
label letters_start
cmp r6 1
jlt invalid
cmp r6 32
jgt invalid
set r3 0
label letter
cmp r3 r6
jge word_done
mov r4 r7
add r4 r3
load8 r14 $r4
print r14
add r3 1
jmp letter
label word_done
cmp r12 1
je after_proof_word
add r1 1
cmp r1 3
jge triple_done
set r14 32
print r14
jmp choose_word
label triple_done
add r0 1
load8 r4 7400000000000000014
cmp r0 r4
jge response_done
set r14 59
print r14
set r14 32
print r14
set r1 0
jmp choose_word
label response_done
set r14 46
print r14
load8 r1 7400000000000000015
cmp r1 2
jlt done
set r14 32
print r14
set r14 91
print r14
set r12 1
jmp choose_word
label after_proof_word
cmp r1 0
je proof_done
set r14 32
print r14
set r14 45
print r14
set r14 62
print r14
set r14 32
print r14
sub r1 1
jmp choose_word
label proof_done
set r14 93
print r14
label done
halt
label invalid
div r0 0
