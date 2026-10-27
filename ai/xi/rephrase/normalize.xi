#!reverse-pc-machine-v1
# Learned query-only rewrites. Exact literal/typed-variable patterns and their
# canonical sides live in the state. No spelling or response is encoded here.
load8 r0 8100000000000000003
cmp r0 1
jne inactive
load8 r0 7400000000000000040
cmp r0 0
jne inactive
load8 r12 7400000000000000032
cmp r12 1
jlt inactive
# Any learned global veto leaves the original interpretation untouched.
set r0 0
label veto_token
cmp r0 r12
jge snapshot_start
set r7 7800000000000001024
mov r1 r0
mul r1 4
add r7 r1
load8 r8 $r7
add r7 1
load8 r14 $r7
mul r14 256
add r8 r14
set r1 0
label veto_cue
load8 r2 8000000000000000005
cmp r1 r2
jge next_veto_token
set r7 8000000000000001000
mov r2 r1
mul r2 40
add r7 r2
load8 r2 $r7
cmp r2 2
jne next_veto_cue
add r7 2
load8 r2 $r7
add r7 1
load8 r14 $r7
mul r14 256
add r2 r14
cmp r2 r8
je inactive
label next_veto_cue
add r1 1
jmp veto_cue
label next_veto_token
add r0 1
jmp veto_token
label snapshot_start
store8 8100000000000001600 r12
set r0 0
label snapshot_raw
set r7 7400000000000000512
add r7 r0
load8 r1 $r7
set r7 8100000000000001000
add r7 r0
store8 $r7 r1
add r0 1
cmp r0 510
jlt snapshot_raw
set r0 0
label snapshot_legacy
set r7 7400000000000001600
add r7 r0
load8 r1 $r7
set r7 8100000000000001510
add r7 r0
store8 $r7 r1
add r0 1
cmp r0 30
jlt snapshot_legacy
set r0 0
label snapshot_open
set r7 7800000000000001024
add r7 r0
load8 r1 $r7
set r7 8100000000000001540
add r7 r0
store8 $r7 r1
add r0 1
cmp r0 60
jlt snapshot_open
# A literal learned question cue licenses suffixes even before a whole-rule
# reorder. This reuses the parent's exact spelling table, not a word constant.
set r0 0
label question_token
cmp r0 r12
jge choose
set r8 7400000000000000512
mov r1 r0
mul r1 34
add r8 r1
load8 r10 $r8
set r1 0
label question_cue
load8 r2 8000000000000000005
cmp r1 r2
jge next_question_token
set r7 8000000000000001000
mov r2 r1
mul r2 40
add r7 r2
load8 r2 $r7
cmp r2 1
jne next_question_cue
add r7 1
load8 r2 $r7
cmp r2 r10
jne next_question_cue
add r7 3
set r2 0
label question_letters
cmp r2 r10
jge question_found
mov r3 r7
add r3 r2
load8 r3 $r3
mov r4 r8
add r4 1
add r4 r2
load8 r4 $r4
cmp r3 r4
jne next_question_cue
add r2 1
jmp question_letters
label question_found
store8 8100000000000000027 2
jmp choose
label next_question_cue
add r1 1
jmp question_cue
label next_question_token
add r0 1
jmp question_token
label choose
load8 r12 7400000000000000032
store8 8100000000000000080 0
store8 8100000000000000096 0
store8 8100000000000000104 0
store8 8100000000000000105 0
set r0 0
label rule
load8 r1 8100000000000000004
cmp r0 r1
jge chosen
set r7 8100000000000030000
mov r1 r0
mul r1 8
add r7 r1
load8 r10 $r7
add r7 1
load8 r11 $r7
cmp r10 4
je whole_scope
cmp r10 1
je prefix_scope
load8 r1 8100000000000000027
cmp r1 0
je next_rule
cmp r11 0
je prepare_rule
cmp r1 r11
jne next_rule
jmp prepare_rule
label whole_scope
load8 r1 8100000000000000029
cmp r1 1
je next_rule
jmp prepare_rule
label prefix_scope
load8 r1 8100000000000000028
cmp r1 1
je next_rule
label prepare_rule
set r9 8100000000000010000
mov r1 r0
mul r1 96
add r9 r1
load8 r8 $r9
cmp r8 r12
jgt next_rule
cmp r10 4
jne length_ready
cmp r8 r12
jne next_rule
label length_ready
set r1 0
cmp r10 2
jne position
mov r1 r12
sub r1 r8
label position
store8 8100000000000000090 0
store8 8100000000000000091 0
store8 8100000000000000092 0
set r2 0
set r6 0
label slot
cmp r2 r8
jge matched
mov r7 r9
add r7 16
mov r3 r2
mul r3 4
add r7 r3
load8 r3 $r7
add r7 1
load8 r4 $r7
add r7 1
load8 r14 $r7
mul r14 256
add r4 r14
add r7 1
load8 r5 $r7
mov r7 r1
add r7 r2
mul r7 4
add r7 7800000000000001024
load8 r14 $r7
add r7 1
load8 r15 $r7
mul r15 256
add r14 r15
add r7 1
load8 r15 $r7
cmp r3 16
jne variable
cmp r14 r4
jne next_position
cmp r15 r5
jne next_position
add r6 1
jmp next_slot
label variable
cmp r3 2
je predicate
cmp r3 1
je subject
cmp r3 4
jne fail
set r7 8100000000000000092
jmp entity
label subject
set r7 8100000000000000090
label entity
cmp r14 0
je bind
cmp r15 1
jne next_position
cmp r14 13
jlt bind
cmp r14 22
jle next_position
jmp bind
label predicate
set r7 8100000000000000091
cmp r14 0
je bind
cmp r15 2
jne next_position
label bind
mov r3 r1
add r3 r2
add r3 1
store8 $r7 r3
label next_slot
add r2 1
jmp slot
label matched
# Shared lexical aliases already have the same semantic IDs. Do not keep
# replacing an inner alias with itself; prefix identities may activate scope.
cmp r10 1
je semantic_progress
cmp r10 4
je semantic_progress
set r5 8100000000000020000
mov r4 r0
mul r4 96
add r5 r4
load8 r4 $r5
cmp r4 r8
jne semantic_progress
mul r4 4
mov r7 r9
add r7 16
add r5 16
set r2 0
label identical_span
cmp r2 r4
jge next_rule
mov r14 r7
add r14 r2
load8 r14 $r14
mov r15 r5
add r15 r2
load8 r15 $r15
cmp r14 r15
jne semantic_progress
add r2 1
jmp identical_span
label semantic_progress
# Whole patterns precede prefix heads; then longer literal spans win.
mov r3 r8
set r4 256
cmp r10 4
jne not_whole_score
set r4 768
mov r3 r6
label not_whole_score
cmp r10 1
jne score_ready
set r4 512
label score_ready
add r3 r4
load8 r4 8100000000000000104
load8 r14 8100000000000000105
mul r14 256
add r4 r14
cmp r3 r4
jlt next_position
jgt remember
# Disjoint functional spans compose left to right. Overlapping equally
# specific candidates must agree; otherwise preserve the original request.
load8 r4 8100000000000000081
cmp r1 r4
je same_span
jlt earlier_span
load8 r5 8100000000000000082
add r4 r5
cmp r1 r4
jlt conflict
jmp next_position
label earlier_span
mov r5 r1
add r5 r8
cmp r5 r4
jgt conflict
jmp remember
label same_span
# Ties must bind the same roles and produce the same semantic token sequence.
set r2 0
label compare_bindings
set r7 8100000000000000090
add r7 r2
load8 r4 $r7
add r7 3
load8 r5 $r7
cmp r4 r5
jne conflict
add r2 1
cmp r2 3
jlt compare_bindings
load8 r4 8100000000000000080
sub r4 1
mul r4 96
set r7 8100000000000020000
add r7 r4
set r5 8100000000000020000
mov r4 r0
mul r4 96
add r5 r4
load8 r4 $r7
load8 r14 $r5
cmp r4 r14
jne conflict
mul r4 4
add r7 16
add r5 16
set r2 0
label compare_output
cmp r2 r4
jge next_position
mov r14 r7
add r14 r2
load8 r14 $r14
mov r15 r5
add r15 r2
load8 r15 $r15
cmp r14 r15
jne conflict
add r2 1
jmp compare_output
label conflict
store8 8100000000000000096 1
jmp next_position
label remember
store8 8100000000000000096 0
mov r4 r3
mod r4 256
store8 8100000000000000104 r4
div r3 256
store8 8100000000000000105 r3
mov r4 r0
add r4 1
store8 8100000000000000080 r4
store8 8100000000000000081 r1
store8 8100000000000000082 r8
store8 8100000000000000085 r10
store8 8100000000000000086 r11
set r2 0
label remember_bindings
set r7 8100000000000000090
add r7 r2
load8 r4 $r7
add r7 3
store8 $r7 r4
add r2 1
cmp r2 3
jlt remember_bindings
label next_position
cmp r10 3
jne next_rule
add r1 1
mov r2 r1
add r2 r8
cmp r2 r12
jle position
label next_rule
add r0 1
jmp rule
label chosen
load8 r0 8100000000000000080
cmp r0 0
je done
load8 r0 8100000000000000096
cmp r0 1
je fail
load8 r0 8100000000000000030
cmp r0 8
jge fail
add r0 1
store8 8100000000000000030 r0
store8 8100000000000000024 1
# apply.xi is linked next, and returns to choose after committing one rewrite.
halt
label fail
store8 8100000000000000026 1
label done
# No winner: skip apply, while leaving the snapshot for accept/cleanup.
store8 8100000000000000080 0
halt

label inactive
halt
