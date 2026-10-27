#!reverse-pc-machine-v1
# Designed compositional generalization, enabled only by the trained model.
# An exact learned construction always wins. A learned literal question cue
# can license an unfamiliar preamble, followed by a completely known clause
# with exactly one entity and one predicate. No unknown content in that clause,
# no multiple roles, no negation/teaching/retraction/alias veto concepts.
# This parser can only ask; it has no fact/word mutation route.
load8 r0 8000000000000000003
cmp r0 1
jne done
load8 r0 7800000000000000064
cmp r0 0
jne done
load8 r0 7400000000000000040
cmp r0 0
jne done
load8 r12 7400000000000000032
load8 r11 8000000000000000005
cmp r11 16
jgt done
set r0 0
label token
cmp r0 r12
jge cue_ready
set r8 7400000000000000512
mov r1 r0
mul r1 34
add r8 r1
load8 r10 $r8
set r7 7800000000000001024
mov r1 r0
mul r1 4
add r7 r1
load8 r9 $r7
add r7 1
load8 r14 $r7
mul r14 256
add r9 r14
set r1 0
label cue
cmp r1 r11
jge next_token
set r7 8000000000000001000
mov r2 r1
mul r2 40
add r7 r2
load8 r2 $r7
cmp r2 1
je spelling
cmp r2 3
je next_cue
add r7 2
load8 r2 $r7
add r7 1
load8 r14 $r7
mul r14 256
add r2 r14
cmp r2 r9
je done
jmp next_cue
label spelling
add r7 1
load8 r2 $r7
cmp r2 r10
jne next_cue
add r7 3
set r2 0
label letters
cmp r2 r10
jge found_cue
mov r3 r7
add r3 r2
load8 r3 $r3
mov r4 r8
add r4 1
add r4 r2
load8 r4 $r4
cmp r3 r4
jne next_cue
add r2 1
jmp letters
label found_cue
load8 r2 8000000000000000026
cmp r2 0
jne done
mov r2 r0
add r2 1
store8 8000000000000000026 r2
label next_cue
add r1 1
jmp cue
label next_token
add r0 1
jmp token
label cue_ready
load8 r10 8000000000000000026
cmp r10 0
je done
# A conditional veto immediately before the question cue marks a different
# question (e.g. purpose/why). Earlier occurrences in a preamble are harmless.
mov r0 r10
sub r0 2
cmp r0 0
jlt no_previous
mul r0 4
set r7 7800000000000001024
add r7 r0
load8 r8 $r7
add r7 1
load8 r14 $r7
mul r14 256
add r8 r14
set r1 0
label preceding_veto
cmp r1 r11
jge no_previous
set r7 8000000000000001000
mov r0 r1
mul r0 40
add r7 r0
load8 r0 $r7
cmp r0 3
jne next_preceding
add r7 2
load8 r0 $r7
add r7 1
load8 r14 $r7
mul r14 256
add r0 r14
cmp r0 r8
je done
label next_preceding
add r1 1
jmp preceding_veto
label no_previous
set r0 0
label role
cmp r0 r12
jge roles_ready
set r7 7800000000000001024
mov r1 r0
mul r1 4
add r7 r1
load8 r8 $r7
add r7 1
load8 r14 $r7
mul r14 256
add r8 r14
add r7 1
load8 r9 $r7
mov r1 r0
add r1 1
cmp r1 r10
je next_role
jlt preamble
cmp r8 0
je done
cmp r9 3
je next_role
cmp r9 1
je subject
cmp r9 2
jne done
load8 r2 7800000000000000069
cmp r2 0
jne done
store8 7800000000000000069 r1
jmp next_role
label subject
cmp r8 13
jlt valid_subject
cmp r8 22
jle done
label valid_subject
load8 r2 7800000000000000068
cmp r2 0
jne done
store8 7800000000000000068 r1
jmp next_role
label preamble
# Recognized content before the question cue would leave its scope unclear.
cmp r9 2
je done
cmp r9 1
jne next_role
# Numeric question numbering is allowed only before the cue, never as S.
cmp r8 13
jlt done
cmp r8 22
jgt done
label next_role
add r0 1
jmp role
label roles_ready
load8 r0 7800000000000000068
cmp r0 0
je done
load8 r0 7800000000000000069
cmp r0 0
je done
store8 7800000000000000064 1
label done
halt
