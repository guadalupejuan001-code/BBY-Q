#!reverse-pc-machine-v1
# Resolve words to SHARED concept IDs. No subject matter or dictionary in code.
# 1..22 use original E010 words directly; only new aliases occupy E012 memory.
# Token +512+i*34; resolved +1600+i*2 = ID, kind (entity/predicate/question).
load8 r0 7400000000000000002
cmp r0 1
jne invalid
load8 r0 7400000000000000016
cmp r0 1
jne invalid
load8 r0 7400000000000000040
cmp r0 0
jne done
load8 r15 7400000000000000032
cmp r15 15
jgt invalid
set r0 0
label token
cmp r0 r15
jge done
set r1 7400000000000000512
mov r2 r0
mul r2 34
add r1 r2
load8 r2 $r1
set r3 0
label old_concept
cmp r3 22
jge new_lexicon
set r4 7200000000000001000
mov r5 r3
mul r5 32
add r4 r5
mov r5 r4
add r5 4
load8 r6 $r5
cmp r6 2
jlt next_old
set r7 5
label old_language
mov r5 r4
add r5 r7
load8 r6 $r5
cmp r6 r2
jne next_old_language
set r8 0
label old_letters
cmp r8 r2
jge old_match
mov r5 r1
add r5 1
add r5 r8
load8 r6 $r5
mov r5 r4
add r5 r7
add r5 1
add r5 r8
load8 r9 $r5
cmp r6 r9
jne next_old_language
add r8 1
jmp old_letters
label old_match
mov r12 r3
add r12 1
set r13 1
jmp save
label next_old_language
cmp r7 5
jne next_old
set r7 14
jmp old_language
label next_old
add r3 1
jmp old_concept
label new_lexicon
load8 r10 7400000000000000004
load8 r5 7400000000000000005
mul r5 256
add r10 r5
cmp r10 512
jgt invalid
set r3 0
label new_word
cmp r3 r10
jge unknown
set r4 7400000000000010000
mov r5 r3
mul r5 40
add r4 r5
mov r5 r4
add r5 3
load8 r6 $r5
cmp r6 r2
jne next_word
set r8 0
label new_letters
cmp r8 r2
jge new_match
mov r5 r1
add r5 1
add r5 r8
load8 r6 $r5
mov r5 r4
add r5 4
add r5 r8
load8 r9 $r5
cmp r6 r9
jne next_word
add r8 1
jmp new_letters
label new_match
load8 r12 $r4
add r4 1
load8 r13 $r4
jmp save
label next_word
add r3 1
jmp new_word
label unknown
set r12 0
set r13 0
label save
set r5 7400000000000001600
mov r6 r0
mul r6 2
add r5 r6
store8 $r5 r12
add r5 1
store8 $r5 r13
add r0 1
jmp token
label done
halt
label invalid
div r0 0
